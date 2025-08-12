import json
import re
import sqlite3
import requests
from typing import Dict, List, Optional, Tuple
from sklearn.metrics.pairwise import cosine_similarity

class DatabaseSearcher:
    def __init__(self, db_path: str, llm_url: str = "http://localhost:11434", model: str = "llama2"):
        self.db_path = db_path
        self.llm_url = llm_url
        self.model = model

    def search(self, query: str, method: str = "hybrid") -> List[Dict]:
        """
        Search database using 3 potential methods or a hybrid of them.
        Supported methods: "hybrid", "entity", "semantic", "keyword".
        
        Args:
            query: User's search query
            method: "hybrid", "entity", "semantic", or "keyword"
        
        Returns:
            List of matching records with relevance scores
        """
        if method == "hybrid":
            return self._hybrid_search(query)
        elif method == "entity":
            return self._entity_based_search(query)
        elif method == "semantic":
            return self._semantic_search(query)
        else:
            return self._keyword_search(query)
        
    def _hybrid_search(self, query: str) -> List[Dict]:
        """Combine entity extraction and semantic search"""
        # Step 1: Try entity-based search first
        entity_results = self._entity_based_search(query)
        
        # Step 2: If few results, supplement with semantic search
        if len(entity_results) < 3:
            semantic_results = self._semantic_search(query)
            
            # Combine results, avoiding duplicates
            combined_results = entity_results.copy()
            entity_ids = {r['record']['id'] for r in entity_results}
            
            for result in semantic_results:
                if result['record']['id'] not in entity_ids:
                    combined_results.append(result)
            
            return sorted(combined_results, key=lambda x: x['relevance_score'], reverse=True)
        
        return entity_results
    
    def _entity_based_search(self, query: str) -> List[Dict]:
        """
        Perform entity-based search using llm to extract entities from the query.
        
        Args:
            query: User's search query

        Returns:
            List of matching records with relevance scores
        """
        # Extract entities using llm
        entities = self._extract_entities(query)
        if entities is None:
            return []
        # Build SQL query
        sql_query, params = self._build_sql_query(entities)
        
        # Execute query
        records = self._execute_query(sql_query, params)
        
        # Score results based on entity matches
        scored_results = []
        for record in records:
            score = self._calculate_entity_score(record, entities)
            scored_results.append({
                'record': record,
                'relevance_score': score,
                'match_type': 'entity',
                'matched_entities': entities
            })
        
        return sorted(scored_results, key=lambda x: x['relevance_score'], reverse=True)
    
    def _semantic_search(self, query: str) -> List[Dict]:
        """Use embeddings for semantic similarity search"""
        # Get query embedding
        query_embedding = self._get_embedding(query)
        if not query_embedding:
            return []
        
        # Get all records
        all_records = self._get_all_records()
        similar_results = []
        
        for record in all_records:
            # Create searchable text from record
            searchable_text = self._create_searchable_text(record)
            
            # Get record embedding
            record_embedding = self._get_embedding(searchable_text)
            if record_embedding:
                # Calculate similarity
                similarity = cosine_similarity([query_embedding], [record_embedding])[0][0]
                
                if similarity > 0.3:  # Threshold for relevance
                    similar_results.append({
                        'record': record,
                        'relevance_score': float(similarity),
                        'match_type': 'semantic',
                        'similarity': float(similarity)
                    })
        
        return sorted(similar_results, key=lambda x: x['relevance_score'], reverse=True)
    
    def _keyword_search(self, query: str) -> List[Dict]:
        """Simple keyword-based search"""
        keywords = query.lower().split()
        
        sql_query = """
        SELECT * FROM people 
        WHERE LOWER(name) LIKE ? OR AGE = ? OR LOWER(food) LIKE ? 
        OR LOWER(quote) LIKE
        """
        
        like_pattern = f"%{' '.join(keywords)}%"
        params = [like_pattern] * 5
        
        records = self._execute_query(sql_query, params)
        
        # Score based on keyword matches
        scored_results = []
        for record in records:
            score = self._calculate_keyword_score(record, keywords)
            scored_results.append({
                'record': record,
                'relevance_score': score,
                'match_type': 'keyword',
                'matched_keywords': keywords
            })
        
        return sorted(scored_results, key=lambda x: x['relevance_score'], reverse=True)
    
    def _get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding vector from llm"""
        try:
            url = f"{self.llm_url}/api/embeddings"
            payload = {
                "model": self.model,
                "prompt": text
            }
            
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                return response.json().get('embedding')
            
            return None
            
        except Exception as e:
            print(f"Embedding failed: {e}")
            return None
    
    def _create_searchable_text(self, record: Dict) -> str:
        """Create searchable text from database record"""
        fields = [
            record.get('name', ''),
            str(record.get('age', 0)),
            record.get('food', ''),
            record.get('quote', ''),
        ]
        return ' '.join(filter(None, fields))
    
    def _get_all_records(self) -> List[Dict]:
        """Get all active records from database"""
        return self._execute_query("SELECT * FROM people WHERE status = 'active'")
    
    def _extract_entities(self, query: str) -> Dict[str, str]:
        """Extract structured entities from query using llm"""
        try:
            url = f"{self.llm_url}/api/generate"
            prompt = f"""
            Extract search criteria from this query and return ONLY valid JSON:
            "{query}"
            
            Extract any mentioned:
            - name: person's name or partial name
            - age: person's age
            - food: any mention of food as related to a person's preferences.
            - quote: a person's favorite quote or saying.
            
            Return format: 
            {{
                "name": "value", "age": "value", "food": "value", "quote": "value"
            }}
            Return empty {{}} if nothing clear is found.
            """
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.1
            }
            
            response = requests.post(url, json=payload, timeout=10)
            # print('url', url)
            # print('payload', payload)
            if response.status_code == 200:
                response_text = response.json().get('response', '')
                # Extract JSON
                json_match = re.search(r'\{.*?\}', response_text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            
            return {}
            
        except Exception as e:
            print(f"Entity extraction failed: {e}")

    def _build_sql_query(self, entities: Dict[str, str]) -> Tuple[str, List[str]]:
        """Build SQL query from extracted entities"""
        conditions = []
        params = []
        
        base_query = "SELECT * FROM people WHERE status = 'active'"

        if entities.get('name'):
            conditions.append("LOWER(name) LIKE LOWER(?)")
            params.append(f"%{entities['name']}%")
        
        if entities.get('age'):
            print('HERE', entities['age'])
            conditions.append("age = ?")
            params.append(f"%{entities['age']}%")
        
        if entities.get('food'):
            conditions.append("LOWER(food) LIKE LOWER(?)")
            params.append(f"%{entities['food']}%") 
        
        if entities.get('quote'):
            conditions.append("LOWER(quote) LIKE LOWER(?)")
            params.append(f"%{entities['quote']}%")
        
        if conditions:
            full_query = f"{base_query} AND {' AND '.join(conditions)}"
        else:
            full_query = f"{base_query} LIMIT 10"
        
        return full_query, params
    
    def _execute_query(self, query: str, params: List[str] = None) -> List[Dict]:
        """Execute SQL query and return results"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            rows = cursor.fetchall()
            results = [dict(row) for row in rows]
            conn.close()
            
            return results
            
        except Exception as e:
            print(f"Database query failed: {e}")
            return []
        
    def _calculate_entity_score(self, record: Dict, entities: Dict[str, str]) -> float:
        """Calculate relevance score based on entity matches(vital to come back to this later)"""
        score = 0.0
        max_score = len(entities)
        
        if not entities:
            return 0.5  # Default score when no entities
        
        for field, value in entities.items():
            record_value = str(record.get(field, '')).lower()
            search_value = value.lower() if value is not None else ''

            if search_value in record_value:
                score += 1.0
            elif any(word in record_value for word in search_value.split()):
                score += 0.5
        
        return score / max_score if max_score > 0 else 0.0