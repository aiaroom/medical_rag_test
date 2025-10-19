import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.vector_database import MedicalVectorDB
from src.llm_integration import LocalLLMClient, RAGSystem
import json

class AdvancedDrugSearch:
    def __init__(self, data_path: str):
        self.db = MedicalVectorDB(data_path)
        self.db.build_vector_database()
        
        # Инициализация LLM и RAG системы
        self.llm_client = LocalLLMClient()
        self.rag_system = RAGSystem(self.db, self.llm_client)
        
        # Статистика использования
        self.search_stats = {
            "total_searches": 0,
            "symptom_searches": 0,
            "drug_info_requests": 0
        }
    
    def smart_search(self, query: str, max_results: int = 5, use_llm: bool = True):
        """Умный поиск с RAG"""
        self.search_stats["total_searches"] += 1
        
        print(f"🔍 Умный поиск: {query}")
        
        # Векторный поиск
        vector_results = self.db.search_drugs(query, max_results)
        
        if not vector_results:
            return {
                "results": [],
                "ai_advice": "❌ По вашему запросу ничего не найдено.",
                "suggestions": ["Попробуйте другие ключевые слова", "Опишите симптомы подробнее"]
            }
        
        # Генерация AI-совета
        ai_advice = ""
        if use_llm and vector_results:
            print("🤖 Генерация AI-совета...")
            ai_advice = self.rag_system.generate_medical_advice(query, vector_results)
        
        return {
            "results": vector_results,
            "ai_advice": ai_advice,
            "suggestions": self._generate_suggestions(vector_results)
        }
    
    def search_by_symptoms(self, symptoms: list, max_results: int = 5):
        """Поиск по списку симптомов с AI-анализом"""
        self.search_stats["symptom_searches"] += 1
        
        query = " ".join(symptoms)
        print(f"🔍 Поиск лекарств для симптомов: {', '.join(symptoms)}")
        
        return self.smart_search(query, max_results)
    
    def search_by_category(self, category: str, query: str = ""):
        """Поиск в определенной категории"""
        print(f"🔍 Поиск в категории '{category}': {query}")
        return self.db.search_drugs(query, category_filter=category)
    
    def get_drug_info(self, drug_name: str):
        """Получение полной информации о лекарстве"""
        self.search_stats["drug_info_requests"] += 1
        
        results = self.db.search_drugs(drug_name, n_results=1)
        if results:
            drug_data = results[0]['полные_данные']
            
            # Генерация AI-резюме
            prompt = f"""Дай краткое резюме о лекарстве {drug_name}:

Описание: {drug_data['описание']}
Показания: {', '.join(drug_data['показания'])}
Противопоказания: {', '.join(drug_data['противопоказания'])}
Побочные эффекты: {', '.join(drug_data['побочные_эффекты'])}

Краткое резюме:"""
            
            ai_summary = self.llm_client.generate_response(prompt, temperature=0.1)
            
            return {
                "data": drug_data,
                "ai_summary": ai_summary
            }
        return None
    
    def compare_drugs(self, drug1: str, drug2: str):
        """Сравнение двух лекарств"""
        print(f"⚖️ Сравнение: {drug1} vs {drug2}")
        return self.rag_system.compare_drugs(drug1, drug2)
    
    def get_categories(self):
        """Получение списка категорий"""
        categories = set()
        for drug in self.db.drugs_data:
            categories.add(drug.get('категория', 'не указана'))
        return list(categories)
    
    def get_stats(self):
        """Получение статистики использования"""
        return self.search_stats
    
    def _generate_suggestions(self, results):
        """Генерация предложений на основе результатов"""
        suggestions = []
        
        categories = set()
        for result in results:
            categories.add(result['полные_данные']['категория'])
        
        if categories:
            suggestions.append(f"Похожие категории: {', '.join(list(categories)[:3])}")
        
        suggestions.append("Для точного диагноза обратитесь к врачу")
        
        return suggestions

    def _display_results(self, results):
        """Отображение результатов поиска - ДОБАВЛЕННЫЙ МЕТОД"""
        if not results:
            print("❌ Ничего не найдено")
            return
            
        # Проверяем формат результатов (старый vs новый)
        if isinstance(results, dict) and 'results' in results:
            # Это результат smart_search (с AI-советом)
            search_data = results
            results = search_data['results']
            
            print(f"\n📋 Найдено {len(results)} результатов:")
            for result in results:
                self._display_single_result(result)
            
            if search_data.get('ai_advice'):
                print(f"\n🤖 AI-совет:\n{search_data['ai_advice']}")
            
            if search_data.get('suggestions'):
                print(f"\n💡 Подсказки: {', '.join(search_data['suggestions'])}")
                
        else:
            # Это прямой результат из vector_database
            print(f"\n📋 Найдено {len(results)} результатов:")
            for result in results:
                self._display_single_result(result)

    def _display_single_result(self, result):
        """Отображение одного результата"""
        drug_data = result['полные_данные']
        print(f"\n⭐ {result['рейтинг']}. {result['лекарство']} (схожесть: {result['схожесть']})")
        print(f"   📝 {drug_data['описание']}")
        print(f"   💊 Показания: {', '.join(drug_data['показания'][:3])}")
        print(f"   ⚠️  Противопоказания: {', '.join(drug_data['противопоказания'][:2])}")
        print(f"   📏 Дозировка: {drug_data['дозировка'][:80]}...")
        print("   " + "-" * 50)

    def search_by_category_enhanced(self, category: str, symptoms: list = None):
        """Улучшенный поиск по категории с симптомами"""
        print(f"🔍 Умный поиск в категории '{category}'")
        
        if symptoms:
            query = " ".join(symptoms)
            print(f"   Симптомы: {', '.join(symptoms)}")
        else:
            query = ""
            print("   Показать все лекарства категории")
        
        # Получаем результаты
        results = self.db.search_drugs(query, category_filter=category, n_results=10)
        
        if not results:
            print("❌ В этой категории ничего не найдено")
            return []
        
        print(f"\n📋 Найдено {len(results)} лекарств в категории '{category}':")
        
        for i, result in enumerate(results, 1):
            drug = result['полные_данные']
            print(f"\n{i}. 💊 {drug['название']} (схожесть: {result['схожесть']})")
            print(f"   📝 {drug['описание']}")
            print(f"   🎯 Показания: {', '.join(drug['показания'][:2])}")
            print(f"   💊 Дозировка: {drug['дозировка'][:80]}...")
        
        return results

    def interactive_search(self):
        """Интерактивный режим поиска"""
        print("🎯 ИНТЕРАКТИВНЫЙ ПОИСК ЛЕКАРСТВ")
        print("=" * 50)
        
        while True:
            print("\nВыберите тип поиска:")
            print("1. 🔍 Умный поиск лекарств")
            print("2. 🤒 Поиск по симптомам") 
            print("3. 📂 Поиск по категории")
            print("4. 💊 Информация о лекарстве")
            print("5. ⚖️ Сравнить лекарства")
            print("6. 📊 Статистика")
            print("7. 📋 Список всех категорий")
            print("8. 🚪 Выход")
            
            choice = input("\nВаш выбор (1-8): ").strip()
            
            if choice == "1":
                query = input("Введите запрос (симптомы, название и т.д.): ").strip()
                results = self.smart_search(query)
                self._display_results(results)
                
            elif choice == "2":
                symptoms = input("Введите симптомы (через запятую): ").split(',')
                symptoms = [s.strip() for s in symptoms if s.strip()]
                results = self.search_by_symptoms(symptoms)
                self._display_results(results)
                
            elif choice == "3":
                categories = self.get_categories()
                print(f"\n📂 Доступные категории ({len(categories)}):")
                for i, cat in enumerate(categories, 1):
                    print(f"   {i}. {cat}")
                
                category_input = input("\nВыберите категорию (название или номер): ").strip()
                
                # Обрабатываем ввод - может быть номер или название
                if category_input.isdigit():
                    index = int(category_input) - 1
                    if 0 <= index < len(categories):
                        category = categories[index]
                    else:
                        print("❌ Неверный номер категории")
                        continue
                else:
                    category = category_input
                    if category not in categories:
                        print(f"❌ Категория '{category}' не найдена")
                        print("Доступные категории:", ", ".join(categories))
                        continue
            
                symptoms_input = input("Дополнительные симптомы (или Enter для всех): ").strip()
                symptoms = [s.strip() for s in symptoms_input.split(',')] if symptoms_input else []
                
                results = self.search_by_category_enhanced(category, symptoms)
                
            elif choice == "4":
                drug_name = input("Введите название лекарства: ").strip()
                info = self.get_drug_info(drug_name)
                
                if info:
                    drug = info['data']
                    print(f"\n💊 {drug['название']}")
                    print(f"📝 {drug['описание']}")
                    print(f"🎯 Показания: {', '.join(drug['показания'])}")
                    print(f"⚠️  Противопоказания: {', '.join(drug['противопоказания'])}")
                    print(f"💊 Дозировка: {drug['дозировка']}")
                    print(f"🔬 Побочные эффекты: {', '.join(drug['побочные_эффекты'])}")
                    
                    if info['ai_summary']:
                        print(f"\n🤖 Краткое резюме:\n{info['ai_summary']}")
                else:
                    print("❌ Лекарство не найдено")
            
            elif choice == "5":
                drug1 = input("Первое лекарство: ").strip()
                drug2 = input("Второе лекарство: ").strip()
                
                comparison = self.compare_drugs(drug1, drug2)
                print(f"\n⚖️ Сравнение {drug1} и {drug2}:")
                print(comparison)
            
            elif choice == "6":
                stats = self.get_stats()
                print(f"\n📊 Статистика использования:")
                print(f"   Всего поисков: {stats['total_searches']}")
                print(f"   Поисков по симптомам: {stats['symptom_searches']}")
                print(f"   Запросов информации: {stats['drug_info_requests']}")
            
            elif choice == "7":
                categories = self.get_categories()
                print(f"\n📋 ВСЕ КАТЕГОРИИ ЛЕКАРСТВ ({len(categories)}):")
                print("=" * 40)
                
                # Группируем по первой букве для удобства
                categories_sorted = sorted(categories)
                current_letter = ""
                
                for category in categories_sorted:
                    first_letter = category[0].upper() if category else ""
                    if first_letter != current_letter:
                        print(f"\n{first_letter}:")
                        current_letter = first_letter
                    print(f"   📍 {category}")
            
            elif choice == "8":
                print("👋 До свидания!")
                break
            
            else:
                print("❌ Неверный выбор")

if __name__ == "__main__":
    search_system = AdvancedDrugSearch("../data/drugs_database.json")
    search_system.interactive_search()