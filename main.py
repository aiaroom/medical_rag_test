import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.advanced_drug_search import AdvancedDrugSearch

def main():
    print("МЕДИЦИНСКАЯ ПОИСКОВАЯ СИСТЕМА RAG")
    print("=" * 50)
    print("! ВНИМАНИЕ: Эта система не заменяет консультацию врача!")
    print("   Всегда обращайтесь к специалисту для назначения лечения.")
    print("=" * 50)
    
    search_system = AdvancedDrugSearch("data/drugs_database.json")
    search_system.interactive_search()

if __name__ == "__main__":
    main()