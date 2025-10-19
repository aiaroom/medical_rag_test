import pytest
import time

class TestSymptomSearch:
    """Тесты поиска лекарств по симптомам"""
    
    @pytest.mark.parametrize("symptoms,expected_drugs,min_expected,test_id", [
        (["головная боль", "мигрень"], 
         ["Парацетамол", "Ибупрофен", "Аспирин", "Ношпа"], 2,
         "symptom_headache"),
        
        (["температура", "лихорадка", "жар"], 
         ["Парацетамол", "Ибупрофен", "Аспирин"], 2,
         "symptom_fever"),
        
        (["воспаление", "артрит", "суставы"], 
         ["Ибупрофен", "Кеторолак"], 1,
         "symptom_inflammation"),
        
        (["аллергия", "зуд", "сыпь", "крапивница"], 
         ["Цетиризин", "Лоратадин"], 1,
         "symptom_allergy"),
        
        (["тошнота", "рвота", "диарея", "изжога"], 
         ["Лоперамид", "Метоклопрамид", "Омепразол"], 1,
         "symptom_stomach"),
        
        (["кашель", "насморк", "горло", "простуда"], 
         ["Амоксициллин", "Азитромицин"], 1,
         "symptom_cold"),
    ])
    def test_symptom_search(self, medical_db, symptoms, expected_drugs, min_expected, test_id):
        """Тестирование поиска по различным симптомам"""
        query = " ".join(symptoms)
        
        results = medical_db.search_drugs(query, n_results=8)
        found_drugs = [result['лекарство'] for result in results]
        
        matches = [drug for drug in expected_drugs if drug in found_drugs]
        
        assert len(matches) >= min_expected, (
            f"Для симптомов '{query}' найдено только {len(matches)} "
            f"из ожидаемых {min_expected}. Найдено: {matches}"
        )
        
        print(f"{test_id}: Найдено {len(matches)} из {len(expected_drugs)} ожидаемых")
    
    @pytest.mark.performance
    def test_search_performance(self, medical_db, search_performance):
        """Тест производительности поиска"""
        test_queries = [
            "головная боль",
            "температура лихорадка", 
            "воспаление артрит",
            "аллергия зуд",
            "тошнота диарея"
        ]
        
        for query in test_queries:
            start_time = time.time()
            results = medical_db.search_drugs(query, n_results=5)
            search_time = time.time() - start_time
            
            search_performance['search_times'].append(search_time)
            search_performance['query_count'] += 1
            
            assert search_time < 2.0, f"Поиск '{query}' занял {search_time:.2f} сек - слишком долго"
            assert len(results) > 0, f"Поиск '{query}' не вернул результатов"
        
        avg_time = sum(search_performance['search_times']) / len(search_performance['search_times'])
        print(f"Среднее время поиска: {avg_time:.3f} сек")