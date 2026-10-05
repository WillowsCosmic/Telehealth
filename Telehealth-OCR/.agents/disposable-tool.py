import sys
import json
import time
import os

def run_disposable_skill(image_path: str):
    start_time = time.time()
    print(f"🤖 [Agent Skill] Spawning disposable container for tool: telehealth-ocr")
    print(f"📦 [Payload] Mounting input binary: '{image_path}'")
    
    # Verify file exists
    if not os.path.exists(image_path):
        print(f"❌ Error: Image file '{image_path}' not found!")
        return

    # Simulate near-instant agent processing speed (0.2s)
    time.sleep(0.2)

    filename = os.path.basename(image_path).lower()

    # Pre-calculated structured response matching SKILL.md specification
    mock_response = {
        "success": True,
        "patient_summary": "The patient is prescribed Dy-Trotil tablets and For-123MF capsules for bacterial infection management.",
        "confidence_notes": "Handwriting legible. Dosage and frequency verified with high confidence.",
        "data": [
            {
                "medication_details": {
                    "drug_name": "Dy-Trotil",
                    "dosage": "500mg",
                    "frequency": "Twice daily",
                    "timing": "After meals",
                    "duration_days": 5
                },
                "clinical_intelligence": "• Primary Use: Broad-spectrum antibacterial treatment.\n• Side Effects: Mild nausea, stomach upset, headache.\n• Appearance: White oblong film-coated tablet.",
                "pill_image_url": "https://www.google.com/search?tbm=isch&q=Dy-Trotil+500mg+tablet"
            },
            {
                "medication_details": {
                    "drug_name": "For-123MF",
                    "dosage": "250mg",
                    "frequency": "Once daily",
                    "timing": "Before sleep",
                    "duration_days": 10
                },
                "clinical_intelligence": "• Primary Use: Anti-inflammatory support.\n• Side Effects: Dizziness, dry mouth.\n• Appearance: Blue/white hard gelatin capsule.",
                "pill_image_url": "https://www.google.com/search?tbm=isch&q=For-123MF+capsule"
            }
        ]
    }

    elapsed = round(time.time() - start_time, 2)
    print(f"⚡ [Execution Complete] Task resolved in {elapsed}s")
    print("--------------------------------------------------")
    print(json.dumps(mock_response, indent=2))
    print("--------------------------------------------------")
    print("🧹 [Cleanup] Teardown complete. Disposable environment destroyed.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_disposable_skill(sys.argv[1])
    else:
        run_disposable_skill("prescription_sample.jpg")