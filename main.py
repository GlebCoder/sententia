import os
from PIL import Image
from app.core.processor import NoteProcessor
from app.agents.inquisitor import Inquisitor

def main():
    print("🚀 Starting AI Investment Analysis...")
    
    # 1. Extraction Phase
    processor = NoteProcessor()
    image_path = "tests/samples/bank_note2.jpg"
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return

    img = Image.open(image_path)
    print(f"📷 Extracting data from {image_path}...")
    notes = processor.parse_note(img)
    
    print(f"✅ Extracted {len(notes)} notes.")

    # 2. Analysis Phase
    print("🧠 Inquisitor is analyzing risks...")
    inquisitor = Inquisitor()
    questions = inquisitor.generate_discovery_questions(notes)

    print("\n" + "="*50)
    print("RISK DISCOVERY QUESTIONS:")
    print("="*50)
    print(questions)
    print("="*50)

if __name__ == "__main__":
    main()