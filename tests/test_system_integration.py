import pytest
import time

class TestSystemIntegration:
    """Комплексные тесты интеграции всей системы"""
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_comprehensive_system_performance(self, medical_db):
        """Комплексный тест производительности и точности системы"""
        test_scenarios = [
            {
                "type": "простые симптомы",
                "queries": ["головная боль", "температура", "аллергия", "кашель"],
                "expected_min_results": 2
            },
            {
                "type": "сложные запросы", 
                "queries": [
                    "сильная головная боль с температурой",
                    "аллергия на цветение весной",
                    "высокое давление и сердцебиение"
                ],
                "expected_min_results": 1
            },
            {
                "type": "категорийный поиск",
                "queries": [
                    ("головная боль", "анальгетик"),
                    ("аллергия", "антигистаминное"), 
                    ("инфекция", "антибиотик")
                ],
                "expected_min_results": 1,
                "categorized": True
            }
        ]
        
        total_queries = 0
        successful_queries = 0
        performance_data = []
        
        for scenario in test_scenarios:
            print(f"\n🎯 Сценарий: {scenario['type']}")
            
            for query_data in scenario["queries"]:
                total_queries += 1
                
                if scenario.get("categorized"):
                    query, category = query_data
                    search_func = lambda: medical_db.search_drugs(query, category_filter=category, n_results=5)
                    query_desc = f"'{query}' (категория: {category})"
                else:
                    query = query_data
                    search_func = lambda: medical_db.search_drugs(query, n_results=5)
                    query_desc = f"'{query}'"
                
                start_time = time.time()
                results = search_func()
                search_time = time.time() - start_time
                performance_data.append(search_time)
                
                if len(results) >= scenario["expected_min_results"]:
                    successful_queries += 1
                    status = "✅"
                else:
                    status = "❌"
                
                print(f"   {status} {query_desc}: {len(results)} результатов за {search_time:.3f}с")
        
        # Анализ результатов
        success_rate = (successful_queries / total_queries) * 100
        avg_performance = sum(performance_data) / len(performance_data)
        
        print(f"\n📊 ИТОГИ КОМПЛЕКСНОГО ТЕСТА:")
        print(f"   Успешных запросов: {successful_queries}/{total_queries} ({success_rate:.1f}%)")
        print(f"   Среднее время поиска: {avg_performance:.3f} сек")
        print(f"   Общее время тестирования: {sum(performance_data):.2f} сек")
        
        # Критерии успеха
        assert success_rate >= 60, f"Слишком низкая успешность: {success_rate:.1f}%"
        assert avg_performance < 1.0, f"Слишком медленный поиск: {avg_performance:.3f} сек"
        
        print("🎉 Система прошла комплексное тестирование!")
    
    def test_system_reliability(self, medical_db):
        """Тест надежности системы при множественных запросах"""
        query = "головная боль"
        
        results_sets = []
        for i in range(5):
            results = medical_db.search_drugs(query, n_results=3)
            results_sets.append([r['лекарство'] for r in results])
        
        first_set = results_sets[0]
        consistent_count = 0
        
        for result_set in results_sets[1:]:
            if set(first_set) == set(result_set):
                consistent_count += 1
        
        consistency_rate = consistent_count / (len(results_sets) - 1)
        assert consistency_rate >= 0.6, f"Слишком низкая консистентность: {consistency_rate:.1%}"
        
        print(f"✅ Консистентность результатов: {consistency_rate:.1%}")