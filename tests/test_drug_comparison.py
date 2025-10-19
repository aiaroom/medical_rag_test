import pytest

class TestDrugComparison:
    """Тесты сравнения и группировки лекарств - ОБНОВЛЕННЫЕ"""
    
    @pytest.mark.parametrize("drug1,drug2,common_queries,min_success_rate", [
        ("Парацетамол", "Ибупрофен", ["головная боль", "температура", "боль"], 0.7),
        ("Цетиризин", "Лоратадин", ["аллергия", "зуд"], 0.5),
        ("Амлодипин", "Лозартан", ["давление", "гипертензия"], 0.5),
    ])
    def test_similar_drugs_comparison(self, medical_db, drug1, drug2, common_queries, min_success_rate):
        """Тестирование поиска похожих лекарств - ОБНОВЛЕННЫЙ"""
        success_count = 0
        
        for query in common_queries:
            results = medical_db.search_drugs(query, n_results=8)
            found_drugs = [result['лекарство'] for result in results]
            
            both_found = drug1 in found_drugs and drug2 in found_drugs
            one_found = drug1 in found_drugs or drug2 in found_drugs
            
            if both_found:
                success_count += 1
                print(f"Запрос '{query}': найдены оба {drug1} и {drug2}")
            elif one_found:
                print(f"Запрос '{query}': найден только один из {drug1}/{drug2}")
            else:
                print(f"Запрос '{query}': не найдены ни {drug1}, ни {drug2}. Найдено: {found_drugs}")
        
        success_rate = success_count / len(common_queries)
        assert success_rate >= min_success_rate, (
            f"Успешность поиска {drug1} и {drug2}: {success_rate:.1%}, ожидалось {min_success_rate:.0%}"
        )
        
        print(f"Успешность поиска {drug1} и {drug2}: {success_rate:.1%}")