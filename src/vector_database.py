import json
import chromadb 
import numpy as np
from typing import List, Dict
import re
from sentence_transformers import SentenceTransformer
import os

class MedicalVectorDB:
    def __init__(self, data_path: str = "data/drugs_database.json", 
                 model_name: str = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'):
        """
        Инициализация векторной базы данных для лекарств
        Используем multilingual модель которая лучше понимает русский
        """
        print(f"Загрузка модели: {model_name}")
        try:
            self.model = SentenceTransformer(model_name)
            print("Мультиязычная модель успешно загружена")
        except Exception as e:
            print(f"Ошибка загрузки модели: {e}")
            raise
        
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_or_create_collection(
            name="medical_drugs",
            metadata={"description": "Medical drugs database"}
        )
        self.data_path = data_path
        self.drugs_data = self._load_data()
    
    def _load_data(self) -> List[Dict]:
        """Загрузка данных о лекарствах из JSON файла"""
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"Загружено {len(data['лекарства'])} лекарств")
            return data['лекарства']
        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")
            return []

    def _create_semantic_drug_text(self, drug: Dict) -> str:
        # Создаем синонимы и ключевые слова
        keyword_mapping = {
            'головная боль': 'мигрень цефалгия головная боль голова',
            'температура': 'лихорадка жар гипертермия горячка',
            'воспаление': 'воспалительный процесс противовоспалительное',
            'артрит': 'артрит суставы суставная боль ревматоидный',
            'боль': 'болевой синдром болезненность анальгетик обезболивающее',
            'лихорадка': 'температура жар лихорадка фебрильный',
            'жаропонижающее': 'жар температура лихорадка противолихорадочное',
            'обезболивающее': 'боль анальгетик анестезия противоболевое',
            'противовоспалительное': 'воспаление противовоспалительный антифлогистическое',
            'аллергия': 'аллергическая реакция зуд сыпь антигистаминное',
            'кашель': 'кашель бронхит отхаркивающее',
            'насморк': 'ринит назальный заложенность носа'
        }
        # Расширяем показания синонимами
        enhanced_indications = []
        for indication in drug['показания']:
            enhanced = indication
            for keyword, synonyms in keyword_mapping.items():
                if keyword in indication.lower():
                    enhanced += " " + synonyms
            enhanced_indications.append(enhanced)
        
        # Создаем категориальные ключевые слова
        category_keywords = {
            'анальгетик': 'обезболивающее боль анальгетик анестезия',
            'противовоспалительное': 'воспаление противовоспалительный артрит',
            'антибиотик': 'антибиотик инфекция бактерии антибактериальное',
            'антигистаминное': 'аллергия антигистаминное зуд сыпь',
            'жаропонижающее': 'температура жар лихорадка жаропонижающее'
        }
        
        category_synonyms = category_keywords.get(drug.get('категория', ''), '')
        # Собираем полный текст
        text_parts = [
            f"Лекарство: {drug['название']}",
            f"Действие: {drug['описание']}",
            f"Лечит: {', '.join(enhanced_indications)}", 
            f"Симптомы: {', '.join(drug['показания'])}",
            f"Категория: {drug.get('категория', '')} {category_synonyms}",
            f"Применение: {drug['дозировка']}",
            f"Ограничения: {', '.join(drug['противопоказания'])}",
            f"Побочные: {', '.join(drug['побочные_эффекты'])}"
        ]
        
        return ". ".join(text_parts)

    def build_vector_database(self):
        """Пересоздание векторной базы с улучшенными текстами"""
        if not self.drugs_data:
            print("Нет данных для создания базы")
            return
                
        documents = []
        metadatas = []
        ids = []
        
        for drug in self.drugs_data:
            drug_text = self._create_semantic_drug_text(drug)
            documents.append(drug_text)
            
            metadata = {
                "название": drug["название"],
                "категория": drug.get("категория", "не указана"),
                "показания": ", ".join(drug["показания"][:3]),
                "id": str(drug["id"])
            }
            metadatas.append(metadata)
            ids.append(f"drug_{drug['id']}")
        
        print("Генерация эмбеддингов...")
        embeddings = self.model.encode(documents, normalize_embeddings=True)
        
        try:
            self.client.delete_collection("medical_drugs")
        except:
            pass
            
        self.collection = self.client.get_or_create_collection(
            name="medical_drugs",
            metadata={"description": "Medical drugs database"}
        )
        
        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"Векторная база пересоздана! Добавлено {len(documents)} записей")
    
    def search_drugs(self, query: str, n_results: int = 5, category_filter: str = None):
        """
        Улучшенный поиск с расширением запроса
        """
        expanded_query = self._expand_search_query(query)
        print(f"Расширенный запрос: '{query}' -> '{expanded_query}'")
        
        where_filter = {"категория": category_filter} if category_filter else None
        
        try:
            query_embedding = self.model.encode([expanded_query], normalize_embeddings=True)[0].tolist()
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_filter
            )
            
            return self._format_results(results)
            
        except Exception as e:
            print(f"Ошибка поиска: {e}")
            return []
    
    def _expand_search_query(self, query: str) -> str:
        """Улучшенное расширение поискового запроса без дублирования"""
        query_expansions = {
            'головная боль': 'мигрень цефалгия',
            'мигрень': 'головная боль',
            'боль': 'болевой синдром',
            'болит': 'боль',
            
            'температура': 'лихорадка жар',
            'лихорадка': 'температура жар',
            'жар': 'температура лихорадка',
            
            'воспаление': 'воспалительный процесс',
            'артрит': 'суставы артралгия',
            
            'аллергия': 'аллергическая реакция зуд сыпь',
            'зуд': 'аллергия сыпь',
            'сыпь': 'аллергия зуд крапивница',
            'крапивница': 'аллергия зуд сыпь',
            
            'диарея': 'понос жидкий стул',
            'тошнота': 'рвота диспепсия',
            'изжога': 'желудок гастрит',
        }
        
        original_query = query.lower().strip()
        expanded_terms = set(original_query.split())
        
        for term, expansion in query_expansions.items():
            if term in original_query:
                new_terms = expansion.split()
                for new_term in new_terms:
                    if new_term not in expanded_terms:
                        expanded_terms.add(new_term)
        
        final_terms = list(expanded_terms)
        if len(final_terms) > 8:
            original_terms = original_query.split()
            final_terms = original_terms + [t for t in final_terms if t not in original_terms][:8-len(original_terms)]
        
        expanded_query = " ".join(final_terms)
        
        if expanded_query != original_query:
            print(f"🔍 Расширенный запрос: '{original_query}' -> '{expanded_query}'")
        
        return expanded_query
    
    def _format_results(self, results) -> List[Dict]:
        """Форматирование результатов поиска"""
        formatted_results = []
        
        if results['documents']:
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )):
                drug_id = int(metadata['id'])
                full_drug_data = next((drug for drug in self.drugs_data if drug['id'] == drug_id), None)
                
                if full_drug_data:
                    similarity = max(0.0, 1.0 - distance)
                    
                    result = {
                        "рейтинг": i + 1,
                        "схожесть": f"{similarity:.3f}",
                        "лекарство": full_drug_data["название"],
                        "описание": full_drug_data["описание"],
                        "показания": full_drug_data["показания"],
                        "дозировка": full_drug_data["дозировка"],
                        "противопоказания": full_drug_data["противопоказания"][:3],
                        "полные_данные": full_drug_data
                    }
                    formatted_results.append(result)
        
        formatted_results.sort(key=lambda x: float(x['схожесть']), reverse=True)
        return formatted_results

def test_improved_search():
    """Тестирование улучшенного поиска"""
    db = MedicalVectorDB()
    
    db.build_vector_database()
    
    print("\n" + "="*60)
    print("🧪 ТЕСТИРОВАНИЕ УЛУЧШЕННОГО ПОИСКА")
    print("="*60)
    
    test_cases = [
        ("головная боль", ["Парацетамол", "Ибупрофен", "Аспирин"]),
        ("температура лихорадка", ["Парацетамол", "Ибупрофен", "Аспирин"]),
        ("воспаление артрит", ["Ибупрофен", "Кеторолак"]),
        ("аллергия зуд", ["Цетиризин", "Лоратадин"]),
        ("космические корабли", [])  # Не должно найти
    ]
    
    for query, expected in test_cases:
        print(f"\nЗапрос: '{query}'")
        print(f"   Ожидаемые: {expected}")
        
        results = db.search_drugs(query, n_results=5)
        found_drugs = [result['лекарство'] for result in results]
        
        print(f"Найдено: {found_drugs}")
        
        if expected:
            matches = [drug for drug in expected if drug in found_drugs]
            if matches:
                print(f"Найдены ожидаемые: {matches}")
            else:
                print(f"Не найдены ожидаемые лекарства")
                
                if found_drugs:
                    print(f"Вместо этого найдено: {found_drugs[:3]}")
        else:
            if not found_drugs:
                print("ОК: ничего не найдено")
            else:
                print(f"Найдены лекарства: {found_drugs[:3]}")
        
        for result in results[:3]:
            print(f"      {result['лекарство']}: {result['схожесть']}")

if __name__ == "__main__":
    test_improved_search()