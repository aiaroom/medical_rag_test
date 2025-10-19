import pytest

class TestCategorySearch:
    """Тесты поиска лекарств по категориям - ОБНОВЛЕННЫЕ"""
    
    @pytest.mark.parametrize("category,symptoms,expected_drugs,min_expected,test_id", [
        ("анальгетик", "головная боль", 
         ["Парацетамол", "Ибупрофен", "Аспирин", "Кеторолак"], 2,  
         "category_analgesic"),
        
        ("противовоспалительное", "воспаление артрит", 
         ["Ибупрофен", "Кеторолак"], 1,  
         "category_anti_inflammatory"),
        
        ("антигистаминное", "аллергия зуд", 
         ["Цетиризин", "Лоратадин"], 1,  
         "category_antihistamine"),
        
        ("спазмолитик", "спазмы боль", 
         ["Ношпа"], 1,
         "category_spasmolytic"),
        
        ("антибиотик", "инфекция бактерии", 
         ["Амоксициллин", "Азитромицин", "Ципролет"], 1,  
         "category_antibiotic"),
        
        ("кардиологическое", "давление гипертензия", 
         ["Амлодипин", "Лозартан", "Эналаприл", "Бисопролол"], 2,  
         "category_cardio"),
    ])
    def test_category_search(self, medical_db, category, symptoms, expected_drugs, min_expected, test_id):
        """Тестирование поиска по категориям с симптомами - ОБНОВЛЕННЫЙ"""
        results = medical_db.search_drugs(symptoms, category_filter=category, n_results=10)
        found_drugs = [result['лекарство'] for result in results]
        
        matches = [drug for drug in expected_drugs if drug in found_drugs]
        
        assert len(matches) >= min_expected, (
            f"В категории '{category}' по запросу '{symptoms}' "
            f"найдено только {len(matches)} из ожидаемых {min_expected}. "
            f"Найдено: {matches}, Все результаты: {found_drugs}"
        )
        
        print(f"✅ {test_id}: В категории '{category}' найдено {len(matches)} из {len(expected_drugs)} ожидаемых")
    
    def test_nonexistent_category(self, medical_db):
        """Тест поиска по несуществующей категории - ОБНОВЛЕННЫЙ"""
        results = medical_db.search_drugs(
            "головная боль", 
            category_filter="несуществующая_категория", 
            n_results=5
        )
        
        print(f"Поиск по несуществующей категории вернул {len(results)} результатов")
    
    def test_empty_category_search(self, medical_db):
        """Тест поиска по категории без дополнительного запроса - ОБНОВЛЕННЫЙ"""
        results = medical_db.search_drugs("", category_filter="анальгетик", n_results=15)

        assert len(results) > 0, "Поиск по категории без запроса должен вернуть результаты"
        
        correct_category_count = 0
        for result in results:
            drug_category = result['полные_данные'].get('категория', '')
            if drug_category == "анальгетик":
                correct_category_count += 1
        
        category_accuracy = correct_category_count / len(results)
        assert category_accuracy >= 0.7, (
            f"Только {category_accuracy:.1%} результатов принадлежат категории 'анальгетик'"
        )
        
        print(f"Найдено {len(results)} препаратов, {correct_category_count} из них обезболивающие")