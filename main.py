import io
import json
import os
import requests
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from PIL import Image
from google import genai
from google.genai import types
import warnings
import urllib.parse
import time
from google.genai import errors
import os
from dotenv import load_dotenv

# Load explicitly from .env.local
load_dotenv(".env.local")

warnings.filterwarnings("ignore", category=UserWarning)

app = FastAPI(title="TeleHealth-OCR Backend")
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")

origins = [
    "http://localhost:3000",
    "http://localhost:5173",  
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "https://telehealth-frontend-cyan.vercel.app",
]

# Add production URL if provided
if os.getenv("FRONTEND_URL"):
    origins.append(os.getenv("FRONTEND_URL"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Google GenAI client (reads GEMINI_API_KEY from environment)
client = genai.Client()
MODEL_ID = "gemma-4-26b-a4b-it"  # Target Gemma 4 multimodal model

# Define Pydantic Schema for Structured Output
class Medication(BaseModel):
    drug_name: str = Field(description="Name of the prescribed medicine")
    dosage: str = Field(description="Dosage strength e.g., 500mg, 10ml")
    frequency: str = Field(description="How often to take e.g., 3 times daily, twice a day")
    timing: str = Field(description="e.g., After meals, before sleep, on empty stomach")
    duration_days: Optional[int] = Field(description="Duration in days if specified")

class PrescriptionOCRResult(BaseModel):
    patient_summary: str = Field(description="Simple 1-2 sentence plain-English summary of the prescription")
    medications: List[Medication]
    confidence_notes: str = Field(description="Notes on handwriting clarity or unreadable areas")

def call_gemma_with_retry(client, model, contents, config=None, max_retries=3):
    """Retries Gemma 4 API calls automatically if temporary 503/429 server spikes occur."""
    for attempt in range(max_retries):
        try:
            return client.models.generate_content(
                model=model,
                contents=contents,
                config=config
            )
        except errors.APIError as e:
            if ("503" in str(e) or "429" in str(e)) and attempt < max_retries - 1:
                sleep_time = (attempt + 1) * 2  # Waits 2s, then 4s
                print(f"[Warning] API spike ({e.code}). Retrying in {sleep_time}s...")
                time.sleep(sleep_time)
                continue
            raise e
        except Exception as e:
            if ("503" in str(e) or "429" in str(e)) and attempt < max_retries - 1:
                time.sleep((attempt + 1) * 2)
                continue
            raise e

def get_direct_pill_image_url(drug_name: str) -> str:
    """
    Fetches a direct image URL (.jpg/.png) for a drug using Google Custom Search.
    Falls back to a high-quality medical image placeholder if API keys are missing or fail.
    """
    api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    cx = os.getenv("GOOGLE_SEARCH_CX")

    if api_key and cx:
        try:
            query = f"{drug_name} pill capsule tablet"
            url = f"https://www.googleapis.com/customsearch/v1?q={urllib.parse.quote(query)}&cx={cx}&key={api_key}&searchType=image&num=1"
            res = requests.get(url, timeout=3).json()
            if "items" in res and len(res["items"]) > 0:
                return res["items"][0]["link"]  # Direct image URL (.jpg/.png)
        except Exception as e:
            print(f"[Warning] Custom Search Image fetch failed: {e}")

    # Direct fallback medical tablet illustration URL
    return "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?auto=format&fit=crop&w=600&q=80"

@app.get("/health")
def health_check():
    return {"status": "ok", "engine": MODEL_ID}

@app.post("/api/analyze-prescription")
async def analyze_prescription(
    file: UploadFile = File(...), 
    fast_mode: bool = False  # Added query parameter
):
    try:
        contents = await file.read()
        pil_image = Image.open(io.BytesIO(contents))

        # --- STEP 1: Fast Multimodal OCR Extraction ---
        ocr_prompt = (
            "You are an expert clinical pharmacy assistant. Analyze this prescription image. "
            "Transcribe the handwritten drug names, dosages, frequencies, and instructions accurately."
        )

        ocr_response = call_gemma_with_retry(
            client=client,
            model=MODEL_ID,
            contents=[pil_image, ocr_prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=PrescriptionOCRResult,
                temperature=0.1
            )
        )

        parsed_data: PrescriptionOCRResult = ocr_response.parsed
        medications_list = parsed_data.medications

        # Fast execution mode for instant CLI demos
        if fast_mode:
            return {
                "success": True,
                "patient_summary": parsed_data.patient_summary,
                "confidence_notes": parsed_data.confidence_notes,
                "data": [
                    {
                        "medication_details": med.model_dump(),
                        "clinical_intelligence": "Fast execution mode (Search skipped).",
                        "pill_image_url": f"https://www.google.com/search?tbm=isch&q={urllib.parse.quote_plus(med.drug_name)}"
                    }
                    for med in medications_list
                ]
            }

        # --- STEP 2: Grounded Search (Standard execution) ---
        enriched_medications = []
        for med in medications_list:
            search_prompt = (
                f"Using web search, find concise medical details for the drug '{med.drug_name}' ({med.dosage}):\n"
                "1. Primary Benefits and Clinical Uses\n"
                "2. Top 3 Common Side Effects\n"
                "3. Visual Appearance/Description of the pill or capsule\n"
                "Keep the answer concise and bulleted for patient reading."
            )

            try:
                search_response = call_gemma_with_retry(
                    client=client,
                    model=MODEL_ID,
                    contents=search_prompt,
                    config=types.GenerateContentConfig(
                        tools=[{"google_search": {}}],
                        temperature=0.2
                    )
                )
                drug_info = search_response.text
            except Exception:
                drug_info = "Web search details unavailable for this medication."

            direct_image_url = get_direct_pill_image_url(med.drug_name)

            enriched_medications.append({
                "medication_details": med.model_dump(),
                "clinical_intelligence": drug_info,
                "pill_image_url": direct_image_url
            })

        return {
            "success": True,
            "patient_summary": parsed_data.patient_summary,
            "confidence_notes": parsed_data.confidence_notes,
            "data": enriched_medications
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)