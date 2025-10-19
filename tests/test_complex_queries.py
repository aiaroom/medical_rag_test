import pytest

class TestComplexQueries:
    """Тесты сложных медицинских запросов - ОБНОВЛЕННЫЕ"""
    
    @pytest.mark.parametrize("query,expected_drugs,min_expected,description,test_id", [
        ("сильная головная боль с температурой что принять", 
         ["Парацетамол", "Ибупрофен"], 1,
         "Комбинация симптомов: головная боль + температура",
         "complex_fever_headache"),
        
        ("воспаление суставов и боль в коленях", 
         ["Ибупрофен", "Кеторолак"], 1,
         "Суставные боли и воспаление",
         "complex_joint_pain"),
        
        ("аллергия на цветение весной чихание зуд в носу", 
         ["Цетиризин", "Лоратадин"], 1,
         "Сезонная аллергия", 
         "complex_seasonal_allergy"),
        
        ("расстройство желудка после еды тошнота диарея", 
         ["Лоперамид", "Метоклопрамид"], 1,
         "Пищевое расстройство",
         "complex_stomach_issue"),
        
        ("высокое давление и учащенное сердцебиение", 
         ["Амлодипин", "Бисопролол", "Лозартан"], 1,
         "Кардиологические симптомы",
         "complex_cardio_symptoms"),
        
        ("простуда кашель насморк боль в горле", 
         ["Амоксициллин", "Парацетамол"], 1,
         "Простудные симптомы",
         "complex_cold_symptoms"),
    ])
    def test_complex_medical_queries(self, medical_db, query, expected_drugs, min_expected, description, test_id):
        """Тестирование сложных естественных запросов - ОБНОВЛЕННЫЙ"""
        results = medical_db.search_drugs(query, n_results=8)
        found_drugs = [result['лекарство'] for result in results]
        
        matches = [drug for drug in expected_drugs if drug in found_drugs]
        
        assert len(matches) >= min_expected, (
            f"Для запроса '{query}' ({description}) найдено только {len(matches)} "
            f"из ожидаемых {min_expected}. Найдено: {matches}, Все результаты: {found_drugs}"
        )
        
        success_rate = (len(matches) / len(expected_drugs)) * 100
        print(f"{test_id}: {description} - найдено {len(matches)} из {len(expected_drugs)} ({success_rate:.1f}%)")
    
    @pytest.mark.slow
    def test_query_variations(self, medical_db):
        """Тестирование различных формулировок одного запроса - ОБНОВЛЕННЫЙ"""
        headache_variations = [
            "головная боль",
            "болит голова", 
            "мигрень",
            "боль в голове",
        ]
        
        expected_drugs = ["Парацетамол", "Ибупрофен", "Аспирин"]
        success_count = 0
        
        for variation in headache_variations:
            results = medical_db.search_drugs(variation, n_results=5)
            found_drugs = [result['лекарство'] for result in results]
            
            matches = [drug for drug in expected_drugs if drug in found_drugs]
            if len(matches) >= 1:
                success_count += 1
                print(f"Вариация '{variation}': найдены {matches}")
            else:
                print(f"Вариация '{variation}': найдены только {matches}, все: {found_drugs}")
        
        success_rate = (success_count / len(headache_variations)) * 100
        assert success_rate >= 50, f"Слишком низкая успешность для вариаций: {success_rate:.1f}%"
        
        print(f"📊 Успешность обработки вариаций: {success_rate:.1f}%")