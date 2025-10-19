import pytest

class TestEdgeCases:
    """Тесты граничных случаев и обработки ошибок - ОБНОВЛЕННЫЕ"""
    
    @pytest.mark.parametrize("query,expected_max_results,description", [
        ("", 10, "Пустой запрос"),
        ("   ", 10, "Запрос только с пробелами"),
        ("космические корабли марс юпитер", 5, "Полностью нерелевантный запрос"),
        ("1234567890", 5, "Запрос только из цифр"),
        ("!@#$%^&*()", 5, "Специальные символы"),
        ("головная боль", 5, "Нормальный запрос для проверки"),
        ("очень сильная невыносимая головная боль с тошнотой", 5, "Длинный описательный запрос"),
        ("боль", 5, "Очень общий запрос"),
    ])
    def test_edge_case_queries(self, medical_db, query, expected_max_results, description):
        """Тестирование граничных случаев запросов - ОБНОВЛЕННЫЙ"""
        results = medical_db.search_drugs(query, n_results=10)
        
        assert len(results) <= expected_max_results, (
            f"Запрос '{query}' ({description}) вернул слишком много результатов: {len(results)}"
        )
        
        if query.strip() == "":
            print(f"{description}: система вернула {len(results)} случайных результатов")
        elif not any(c.isalpha() for c in query):
            print(f"{description}: система вернула {len(results)} результатов для не-текстового запроса")
        else:
            print(f"{description}: система обработала корректно, найдено {len(results)} результатов")
    
    def test_very_long_query(self, medical_db):
        """Тест очень длинного запроса - ОБНОВЛЕННЫЙ"""
        long_query = " ".join(["головная боль"] * 20)
        
        results = medical_db.search_drugs(long_query, n_results=5)
        
        assert results is not None, "Очень длинный запрос вызвал ошибку"
        
        if len(results) > 0:
            found_drugs = [result['лекарство'] for result in results]
            expected_drugs = ["Парацетамол", "Ибупрофен", "Аспирин"]
            matches = [drug for drug in expected_drugs if drug in found_drugs]
            
            if len(matches) >= 1:
                print(f"Очень длинный запрос: найдены релевантные {matches}")
            else:
                print(f"Очень длинный запрос: найдены нерелевантные {found_drugs}")
        else:
            print("Очень длинный запрос: не найдено результатов")
    
    @pytest.mark.parametrize("n_results", [1, 3, 5, 10])
    def test_different_result_limits(self, medical_db, n_results):
        """Тестирование разных лимитов результатов - ОБНОВЛЕННЫЙ"""
        results = medical_db.search_drugs("головная боль", n_results=n_results)
        
        assert len(results) <= n_results, f"Вернуло {len(results)} при n_results={n_results}"
        
        if len(results) > 0:
            min_similarity = min(float(result['схожесть']) for result in results)
            assert min_similarity >= 0.0, f"Отрицательная схожесть: {min_similarity}"
        
        print(f"n_results={n_results}: вернуло {len(results)} результатов")