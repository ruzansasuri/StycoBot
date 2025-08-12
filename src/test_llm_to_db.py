from llm_to_db import DatabaseSearcher


def test_database_search():
    """Test the database search functionality"""
    searcher = DatabaseSearcher("people.db")
    
    test_queries = [
        "Find Ruzan Sasuri",
        "Who loves shrimp?",
        "Someone who never gives up",
        "Who is younger than 40?",
        "Can you handle a random question?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 50)
        
        results = searcher.search(query, method="hybrid")
        
        for i, result in enumerate(results[:3]):  # Top 3 results
            record = result['record']
            score = result['relevance_score']
            match_type = result['match_type']
            
            print(f"{i+1}. {record['name']} - {record['age']} ({match_type}: {score:.2f})")
            print(f"   {record['food']} | {record['quote']}")

test_database_search()
# if __name__ == "__main__":
#     # Simple usage
#     searcher = DatabaseSearcher("people.db")
    
#     # Example searches
#     queries = [
#         "Find John Smith at TechCorp",
#         "Someone who likes photography",
#         "Marketing director in New York",
#         "People interested in AI and machine learning",
#         "Software engineer in San Francisco"
#     ]
    
#     for query in queries:
#         print(f"\n{'='*60}")
#         print(f"SEARCHING: {query}")
#         print('='*60)
        
#         results = searcher.search(query, method="hybrid")
        
#         if results:
#             print(f"Found {len(results)} results:")
#             for i, result in enumerate(results[:3]):  # Show top 3
#                 record = result['record']
#                 score = result['relevance_score']
#                 match_type = result['match_type']
                
#                 print(f"\n{i+1}. {record['name']} (Score: {score:.2f}, Type: {match_type})")
#                 print(f"   Company: {record.get('company', 'N/A')}")
#                 print(f"   Position: {record.get('position', 'N/A')}")
#                 print(f"   Location: {record.get('location', 'N/A')}")
#                 print(f"   Interests: {record.get('interests', 'N/A')}")
#                 print(f"   Email: {record.get('email', 'N/A')}")
#         else:
#             print("No results found")
    
#     # Test different search methods
#     print(f"\n{'='*60}")
#     print("COMPARING SEARCH METHODS")
#     print('='*60)
    
#     test_query = "creative person who takes photos"
    
#     methods = ["entity", "semantic", "hybrid", "keyword"]
#     for method in methods:
#         print(f"\n--- {method.upper()} METHOD ---")
#         results = searcher.search(test_query, method=method)
#         print(f"Results: {len(results)}")
#         if results:
#             top_result = results[0]
#             print(f"Top match: {top_result['record']['name']} (Score: {top_result['relevance_score']:.2f})")
