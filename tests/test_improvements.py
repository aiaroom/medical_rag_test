import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.vector_database import MedicalVectorDB

def analyze_drug_relevance():
    """Анализ релевантности лекарств для головной боли - ИСПРАВЛЕННАЯ"""
    
    print("\nАНАЛИЗ РЕЛЕВАНТНОСТИ ДЛЯ 'ГОЛОВНАЯ БОЛЬ'")
    print("=" * 60)
    
    db = MedicalVectorDB()
    
    relevant_drugs = []
    search_terms = ['головная', 'мигрень', 'боль'] 
    
    for drug in db.drugs_data:
        indications_text = " ".join(drug['показания']).lower()
        
        if any(term in indications_text for term in search_terms):
            relevant_drugs.append({
                'название': drug['название'],
                'показания': drug['показания'],
                'категория': drug.get('категория', 'не указана')
            })
    
    print(f"Всего релевантных лекарств: {len(relevant_drugs)}")
    
    for drug_info in relevant_drugs:
        print(f"✅ {drug_info['название']} ({drug_info['категория']}): {drug_info['показания']}")

def test_search_with_relevance():
    """Тестирование поиска с анализом релевантности"""
    
    print("\nТЕСТИРОВАНИЕ ПОИСКА С АНАЛИЗОМ РЕЛЕВАНТНОСТИ")
    print("=" * 60)
    
    db = MedicalVectorDB()
    
    test_cases = [
        ("головная боль", ["Парацетамол", "Ибупрофен", "Аспирин", "Ношпа"]),
        ("температура", ["Парацетамол", "Ибупрофен", "Аспирин"]),
        ("аллергия", ["Цетиризин", "Лоратадин"]),
        ("воспаление", ["Ибупрофен", "Кеторолак"]),
    ]
    
    for query, expected_drugs in test_cases:
        print(f"\nЗапрос: '{query}'")
        print(f"   Ожидаемые: {expected_drugs}")
        print("-" * 40)
        
        results = db.search_drugs(query, n_results=8)
        found_drugs = [result['лекарство'] for result in results]
        
        matches = [drug for drug in expected_drugs if drug in found_drugs]
        missing = [drug for drug in expected_drugs if drug not in found_drugs]
        
        print(f"   Найдено: {len(results)} результатов")
        print(f"   Совпадения: {matches} ({len(matches)}/{len(expected_drugs)})")
        
        if missing:
            print(f"Не найдены: {missing}")
        
        for i, result in enumerate(results[:5], 1):
            drug = result['полные_данные']
            is_expected = "✅" if result['лекарство'] in expected_drugs else "  "
            print(f"   {is_expected} {i}. {result['лекарство']} (схожесть: {result['схожесть']})")

def debug_specific_drugs():
    """Отладка конкретных лекарств"""
    
    print("\n🔧 ОТЛАДКА КОНКРЕТНЫХ ЛЕКАРСТВ")
    print("=" * 60)
    
    db = MedicalVectorDB()
    
    target_drugs = ["Парацетамол", "Ибупрофен", "Цетиризин", "Ношпа"]
    
    for drug_name in target_drugs:
        results = db.search_drugs(drug_name, n_results=1)
        if results:
            drug = results[0]['полные_данные']
            print(f"\n{drug['название']}:")
            print(f"   Категория: {drug.get('категория', 'не указана')}")
            print(f"   Показания: {drug['показания']}")
            print(f"   Описание: {drug['описание']}")

if __name__ == "__main__":
    analyze_drug_relevance()
    test_search_with_relevance() 
    debug_specific_drugs()