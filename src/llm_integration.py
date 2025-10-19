import requests
import json
from typing import List, Dict
import time

class LocalLLMClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        """
        Инициализация клиента для локальной LLM (Ollama)
        
        Args:
            base_url: URL локального сервера Ollama
        """
        self.base_url = base_url
        self.available_models = self._get_available_models()
        
    def _get_available_models(self) -> List[str]:
        """Получение списка доступных моделей"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [model['name'] for model in models]
            return []
        except Exception as e:
            print(f"Не удалось подключиться к Ollama: {e}")
            return []
    
    def generate_response(self, prompt: str, model: str = "llama2", 
                         temperature: float = 0.3, max_tokens: int = 1000) -> str:
        """
        Генерация ответа с помощью локальной LLM
        
        Args:
            prompt: промпт для модели
            model: название модели
            temperature: креативность (0-1)
            max_tokens: максимальное количество токенов
        """
        if not self.available_models:
            return "Локальная LLM не доступна. Убедитесь, что Ollama запущен."
        
        if model not in self.available_models:
            model = self.available_models[0]
            print(f"Используется модель: {model}")
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                return response.json().get('response', 'Пустой ответ от модели')
            else:
                return f"Ошибка LLM: {response.status_code}"
                
        except Exception as e:
            return f"Ошибка подключения к LLM: {str(e)}"

class RAGSystem:
    def __init__(self, vector_db, llm_client):
        """
        Полноценная RAG система
        
        Args:
            vector_db: векторная база данных
            llm_client: клиент LLM
        """
        self.vector_db = vector_db
        self.llm = llm_client
        
    def generate_medical_advice(self, query: str, search_results: List[Dict]) -> str:
        """
        Генерация медицинского совета на основе результатов поиска
        
        Args:
            query: исходный запрос пользователя
            search_results: результаты векторного поиска
        """
        if not search_results:
            return "К сожалению, в базе данных не найдено подходящих лекарств для ваших симптомов."
        
        # Формируем контекст для LLM
        context = self._build_context(search_results)
        
        prompt = f"""Ты - медицинский ассистент. Пользователь спрашивает: "{query}"

На основе следующей информации о лекарствах дай обоснованный ответ:

{context}

Инструкции:
1. Проанализируй симптомы и подходящие лекарства
2. Укажи наиболее подходящие варианты и их дозировки
3. Предупреди о противопоказаниях и побочных эффектах
4. Напомни о необходимости консультации с врачом
5. Будь точным и осторожным в рекомендациях
6. Ответ дай на русском языке

Ответ:"""
        
        return self.llm.generate_response(prompt, temperature=0.2)
    
    def compare_drugs(self, drug1: str, drug2: str) -> str:
        """Сравнение двух лекарств"""
        results1 = self.vector_db.search_drugs(drug1, n_results=1)
        results2 = self.vector_db.search_drugs(drug2, n_results=1)
        
        if not results1 or not results2:
            return "Не удалось найти информацию об одном из лекарств"
        
        drug1_info = results1[0]['полные_данные']
        drug2_info = results2[0]['полные_данные']
        
        prompt = f"""Сравни два лекарства:

Лекарство 1: {drug1}
- Описание: {drug1_info['описание']}
- Показания: {', '.join(drug1_info['показания'])}
- Противопоказания: {', '.join(drug1_info['противопоказания'])}
- Побочные эффекты: {', '.join(drug1_info['побочные_эффекты'])}

Лекарство 2: {drug2}
- Описание: {drug2_info['описание']}
- Показания: {', '.join(drug2_info['показания'])}
- Противопоказания: {', '.join(drug2_info['противопоказания'])}
- Побочные эффекты: {', '.join(drug2_info['побочные_эффекты'])}

Сравни их по:
1. Эффективности для разных состояний
2. Безопасности и побочным эффектам
3. Противопоказаниям
4. Удобству применения

Вывод на русском языке:"""
        
        return self.llm.generate_response(prompt)
    
    def _build_context(self, search_results: List[Dict]) -> str:
        """Построение контекста из результатов поиска"""
        context = ""
        for i, result in enumerate(search_results[:5], 1):
            drug_data = result['полные_данные']
            context += f"\n{i}. {drug_data['название']}:\n"
            context += f"   - Описание: {drug_data['описание']}\n"
            context += f"   - Показания: {', '.join(drug_data['показания'][:3])}\n"
            context += f"   - Дозировка: {drug_data['дозировка']}\n"
            context += f"   - Противопоказания: {', '.join(drug_data['противопоказания'][:3])}\n"
            context += f"   - Побочные эффекты: {', '.join(drug_data['побочные_эффекты'][:3])}\n"
        
        return context

def test_llm_connection():
    """Тестирование подключения к локальной LLM"""
    print("Тестирование подключения к LLM...")
    
    llm = LocalLLMClient()
    
    if llm.available_models:
        print(f"Доступные модели: {', '.join(llm.available_models)}")
        
        test_response = llm.generate_response("Привет! Ответь коротко: как дела?")
        print(f"Тестовый ответ: {test_response[:100]}...")
    else:
        print("LLM не доступна. Установите Ollama: https://ollama.ai/")
        print("   Пример установки модели: ollama pull llama2")

if __name__ == "__main__":
    test_llm_connection()