import os
from PIL import Image
from app.core.processor import NoteProcessor
from app.agents.inquisitor import Inquisitor

# English comment: Main entry point for the end-to-end investment analysis pipeline
def main():
    print("🚀 Starting AI Investment Analysis...")
    
    # 1. Extraction Phase
    processor = NoteProcessor()
    image_path = "tests/samples/bank_note2.jpg"
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return

    img = Image.open(image_path)
    print(f"📷 Step 1: Extracting data from {image_path}...")
    
    try:
        notes = processor.parse_note(img)
        print(f"✅ Successfully extracted {len(notes)} notes.")
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        return

    # 2. Analysis Phase
    print("🧠 Step 2: Inquisitor is analyzing risks and ranking products...")
    inquisitor = Inquisitor()
    
    # English comment: Generate discovery questions (the 'Inquisition' part)
    questions = inquisitor.generate_discovery_questions(notes)
    
    # English comment: Generate ranking and ticker optimizations (the 'Strategist' part)
    ranking_report = inquisitor.rank_and_optimize(notes)

    # 3. Output Results
    print("\n" + "═"*60)
    print("      🔍 INVESTOR DISCOVERY QUESTIONS (Ask your Banker)")
    print("═"*60)
    print(questions)
    
    print("\n" + "═"*60)
    print("      🏆 STRATEGIC RANKING & OPTIMIZATION")
    print("═"*60)
    print(ranking_report)
    print("═"*60)
    
    print("\n✅ Analysis Complete.")

if __name__ == "__main__":
    main()