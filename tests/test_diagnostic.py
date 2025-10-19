import pytest

class TestDiagnostic:
    """Диагностические тесты для анализа проблем поиска"""
    
    def test_drug_categories_analysis(self, medical_db):
        """Анализ категорий лекарств в базе данных"""
        categories = {}
        
        for drug in medical_db.drugs_data:
            category = drug.get('категория', 'не указана')
            if category not in categories:
                categories[category] = []
            categories[category].append(drug['название'])
        
        print("\nАНАЛИЗ КАТЕГОРИЙ ЛЕКАРСТВ:")
        for category, drugs in categories.items():
            print(f"   {category}: {', '.join(drugs)}")
    
    def test_search_debug(self, medical_db):
        """Диагностика поиска для проблемных запросов"""
        problematic_queries = [
            "крапивница",  # Должен найти антигистаминные
            "Ибупрофен",   # Должен найти сам себя
            "Кеторолак",   # Должен найти сам себя
        ]
        
        for query in problematic_queries:
            print(f"\n🔍 ДИАГНОСТИКА запроса: '{query}'")
            results = medical_db.search_drugs(query, n_results=5)
            
            print(f"   Найдено: {len(results)} результатов")
            for i, result in enumerate(results, 1):
                drug = result['полные_данные']
                print(f"   {i}. {result['лекарство']} (схожесть: {result['схожесть']})")
                print(f"      Категория: {drug.get('категория', 'не указана')}")
                print(f"      Показания: {', '.join(drug['показания'][:2])}")
    
    def test_category_filter_debug(self, medical_db):
        """Диагностика фильтрации по категориям"""
        test_cases = [
            ("анальгетик", "Парацетамол"),
            ("противовоспалительное", "Ибупрофен"), 
            ("антигистаминное", "Цетиризин"),
        ]
        
        for category, expected_drug in test_cases:
            print(f"\n🔍 ДИАГНОСТИКА категории: '{category}'")
            results = medical_db.search_drugs("", category_filter=category, n_results=10)
            
            found_drugs = [result['лекарство'] for result in results]
            print(f"   Найдено: {found_drugs}")
            
            if expected_drug in found_drugs:
                print(f"Ожидаемый '{expected_drug}' найден")
            else:
                print(f"Ожидаемый '{expected_drug}' не найден")