from response_generator import ResponseGenerator


def demo_response_generation():
    """Demo different response styles with sample data"""
    
    # Sample search result (your JSON format)
    sample_results = [{
        'record': {
            'id': 1,
            'name': 'Sarah Johnson',
            'age': 30,
            'food': 'Sushi',
            'quote': 'Life is too short for bad feet.'    
        },
        'relevance_score': 0.95,
        'match_type': 'hybrid',
        # 'matched_entities': {'position': 'marketing', 'interests': 'fitness'}
    }]
    
    user_query = "Find someone in who likes sushi"
    
    print("="*60)
    print(f"USER QUERY: {user_query}")
    print("="*60)
    
    # Test different response styles
    styles = ["helpful", "casual", "professional", "brief"]
    generator = ResponseGenerator()
    
    for style in styles:
        print(f"\n--- {style.upper()} STYLE ---")
        response = generator.generate_human_response(user_query, sample_results, style)
        print(response)
        print("-" * 40)

if __name__ == "__main__":
    # Demo the response generation
    demo_response_generation()