---
name: telehealth-ocr
description: Multimodal clinical prescription transcription and grounded drug intelligence assistant.
version: 1.0.0
author: TeleHealth-OCR Team
license: MIT
---

# TeleHealth-OCR Agent Skill

Transcribes handwritten medical prescriptions, extracts structured dosing schedules using Gemma 4 multimodal vision, and enriches medication data with live Grounded Search intelligence.

## Overview

TeleHealth-OCR serves as an open-standard clinical agent skill. It converts unformatted handwriting, cursive script, and printed medical document images into structured JSON schema payloads (`PrescriptionOCRResult`), while retrieving live clinical facts, side effects, and visual references via Google Search grounding.

## Prerequisites

* Python 3.10+
* `google-genai` SDK
* Valid `GEMINI_API_KEY` configured in environment variables
* Access to `gemma-4-31b-it` or `gemma-4-26b-a4b-it` model endpoints

## Input & Output Specification

### Tool Method: `analyze_prescription`

#### Input Parameters

| Field | Type | Description | Required |
| --- | --- | --- | --- |
| `file` | `UploadFile` (Binary) | Multipart form file input (JPEG, PNG, WEBP) containing the prescription image. | Yes |

#### Output Payload (`application/json`)

```json
{
  "success": true,
  "patient_summary": "Simple 1-2 sentence plain-English summary of the prescription",
  "confidence_notes": "Notes on handwriting clarity, missing dosages, or obscured areas",
  "data": [
    {
      "medication_details": {
        "drug_name": "Name of prescribed drug",
        "dosage": "Dosage strength (e.g., 500mg, 10ml)",
        "frequency": "Frequency of intake (e.g., 3 times daily)",
        "timing": "Specific intake timing (e.g., After meals)",
        "duration_days": 5
      },
      "clinical_intelligence": "Bullet points detailing benefits, top side effects, and visual appearance",
      "pill_image_url": "Encoded URL link for visual reference lookup"
    }
  ]
}
```

## Schema Definitions

```typescript
export interface MedicationDetails {
  drug_name: string;
  dosage: string;
  frequency: string;
  timing: string;
  duration_days: number | null;
}

export interface EnrichedMedication {
  medication_details: MedicationDetails;
  clinical_intelligence: string;
  pill_image_url: string;
}

export interface PrescriptionAnalysisResponse {
  success: boolean;
  patient_summary: string;
  confidence_notes: string;
  data: EnrichedMedication[];
}
```

## Resilience & Execution Strategy

1. **Multimodal OCR Step:** Transcribes image bytes using `gemma-4-31b-it` with structured Pydantic schema enforcement (`response_schema=PrescriptionOCRResult`) at `temperature=0.1`.
2. **Grounded Search Enrichment:** Issues grounded search requests using Gemma 4 with `google_search` tool enabled to fetch clinical benefits, top 3 side effects, and visual pill descriptions.
3. **Fallback & Retry Logic:** Incorporates exponential backoff retries (`call_gemma_with_retry`) on HTTP 503/429 API errors, automatically falling back to internal model knowledge if search grounding times out.

## Local Execution

To trigger this skill via the FastAPI service backend:

```bash
# Start backend server
uvicorn main:app --reload --port 8000

# Execute endpoint
curl -X POST "http://127.0.0.1:8000/api/analyze-prescription" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@prescription_sample.jpg"
```