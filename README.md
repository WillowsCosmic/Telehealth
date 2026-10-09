# 🩺 TeleHealth-OCR — Disposable Clinical Agent Skill

> An open-standard, disposable AI Agent Skill that transcribes handwritten medical prescriptions using multimodal vision and enriches medication data with live grounded search intelligence.

---

## 🚀 Overview

**TeleHealth-OCR** operates as a standardized, headless AI Agent Skill built on top of the **Agent Skill Open Standard** (`SKILL.md`). Designed for zero-retention clinical workflows, it allows autonomous agent runtimes (e.g., OpenCode, Gemini CLI, LangChain) to discover, execute, and tear down prescription OCR workflows statelessly.

While primary execution happens headlessly via CLI/REST endpoints, TeleHealth-OCR also provides a **Human-in-the-Loop React Dashboard** for patient and clinician visual verification.

---

## ✨ Key Features

* 🤖 **Agent Skill Open Standard (`SKILL.md`):** Native tool discovery and schema enforcement for autonomous AI agent harnesses.
* ⚡ **Disposable & Stateless Execution:** Zero backend database or image persistence. Images are processed in-memory as temporary byte streams.
* 👁️ **Multimodal Prescription OCR:** Powered by `gemma-4-26b-a4b-it` / `gemma-4-31b-it` via Google GenAI SDK for accurate cursive handwriting transcription.
* 🌐 **Grounded Search Intelligence:** Enriches extracted drug names with clinical uses, top side effects, and visual pill reference images.
* 🛠️ **CLI & Harness Ready:** Instant execution via `agent_cli.py`, `disposable_agent.py`, or direct `curl` commands.
* 🖥️ **Human-in-the-Loop Inspection:** Local-storage backed React dashboard for side-by-side prescription verification.

---

## 📂 Project Architecture

```text
TeleHealth-OCR/
├── .agents/
│   └── skills/
│       └── telehealth-ocr/
│           └── SKILL.md                 # Agent Skill Discovery Manifest
├── backend/
│   ├── main.py                         # FastAPI Stateless Engine
│   └── requirements.txt
├── agent_cli.py                         # Headless CLI Runner
├── disposable_agent.py                  # Low-Latency Disposable Skill Simulator
├── src/                                 # Human-in-the-Loop React UI
└── README.md
```

---

## 🔧 Installation & Setup

### Prerequisites

* Python 3.10+
* Node.js 18+
* Google Gemini API Key (`GEMINI_API_KEY`)

### 1. Backend Setup

```bash
# Clone repository
git clone https://github.com/your-repo/TeleHealth-OCR.git
cd TeleHealth-OCR

# Set up virtual environment
python -m venv ocrenv
source ocrenv/bin/activate  # On Windows: ocrenv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
echo "GEMINI_API_KEY=your_gemini_api_key_here" > .env
```

### 2. Launch Backend Service

```bash
uvicorn main:app --reload --port 8000
```

---

## 💻 Agent & CLI Execution

### 1. Agent Harness Integration (OpenCode / Gemini CLI)

Ensure `.agents/skills/telehealth-ocr/SKILL.md` is present. Launch your preferred harness:

```bash
opencode
# OR
gemini
```

Inside the harness prompt:

> *"Use the `telehealth-ocr` skill to analyze `prescription_sample.jpg` and output the results to `report.md`."*

### 2. Standalone CLI Script

Run headless extraction directly from your terminal:

```bash
python agent_cli.py path/to/prescription.jpg
```

### 3. Disposable Fast Execution

For sub-second demo execution:

```bash
python disposable_agent.py path/to/prescription.jpg
```

### 4. Direct REST / `curl` Call

```bash
curl -X POST "http://127.0.0.1:8000/api/analyze-prescription" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample.jpg"
```

---

## 📊 Standardized Output Payload (`SKILL.md` Spec)

```json
{
  "success": true,
  "patient_summary": "The patient is prescribed Dy-Trotil tablets and For-123MF capsules.",
  "confidence_notes": "Handwriting legible. High confidence extraction.",
  "data": [
    {
      "medication_details": {
        "drug_name": "Dy-Trotil",
        "dosage": "500mg",
        "frequency": "Twice daily",
        "timing": "After meals",
        "duration_days": 5
      },
      "clinical_intelligence": "• Primary Use: Antibacterial\n• Side Effects: Nausea, headache",
      "pill_image_url": "https://www.google.com/search?tbm=isch&q=Dy-Trotil"
    }
  ]
}
```

---

## 🔒 Privacy & HIPAA Compliance

* **Zero Backend Storage:** Images are read as temporary byte buffers in RAM and dropped immediately after processing.
* **Local History Only:** Dashboard history is kept exclusively inside the user's browser `localStorage`.

---

## 📜 License

Distributed under the MIT License.
