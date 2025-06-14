import unittest
from unittest.mock import patch
from chatbot import authenticate_user, extract_name, generate_response, get_user_data, UserData

class TestChatbot(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        import chatbot
        chatbot.known_names = set(['Ruzan', 'Sean', 'Brijesh'])
        chatbot.USERS = {
            'Ruzan': chatbot.UserData('Ruzan', '34', 'Shrimp', 'Never give up'),
            'Sean': chatbot.UserData('Sean', '34', 'Daar', "Main who Daan Can't Love Yourself"),
            'Brijesh': chatbot.UserData('Brijesh', '32', 'Pizza', 'Life is beautiful')
        }
        chatbot.user_name = None

    def test_authenticate_user_valid(self):
        """Test successful user authentication"""
        import chatbot
        with patch('builtins.input', return_value='Ruzan'):
            authenticate_user()
            self.assertEqual(chatbot.user_name, 'Ruzan')

    def test_authenticate_user_invalid(self):
        """Test failed user authentication"""
        with patch('builtins.input', return_value='Unknown'):
            with self.assertRaises(SystemExit) as cm:
                authenticate_user()
            self.assertEqual(cm.exception.code, 0)

    def test_extract_name(self):
        """Test name extraction from input"""
        # Test with name at start
        self.assertEqual(extract_name("Ruzan what's your favorite food?"), "Ruzan")
        # Test with name at end
        self.assertEqual(extract_name("What's your favorite food Ruzan?"), "Ruzan")
        # Test with name in middle
        self.assertEqual(extract_name("What's Ruzan's favorite food?"), "Ruzan")
        # Test with no name
        self.assertIsNone(extract_name("What's your favorite food?"))
        # Test with empty input
        self.assertIsNone(extract_name(""))
        # Test with unknown name
        self.assertIsNone(extract_name("Unknown what's your favorite food?"))

    def test_get_user_data(self):
        """Test getting user data"""
        user_data = get_user_data("Ruzan")
        self.assertEqual(user_data, ['Ruzan', '34', 'Shrimp', 'Never give up'])

    def test_generate_response(self):
        """Test response generation"""
        user_data = ['Ruzan', '34', 'Shrimp', 'Never give up']
        # Test food preference
        self.assertIn("Shrimp", generate_response(user_data, "food"))
        # Test age
        self.assertIn("34", generate_response(user_data, "age"))
        # Test quote
        self.assertIn("Never give up", generate_response(user_data, "quote"))
        # Test random response
        response = generate_response(user_data, "hello")
        self.assertIn("Ruzan", response)
        user_data = ['Ruzan', '34', 'Pizza', 'Main who daan']
        # Test food preference
        self.assertIn("Pizza", generate_response(user_data, "food"))
        # Test age
        self.assertIn("34", generate_response(user_data, "age"))
        self.assertIn("Main who daan", generate_response(user_data, "quote"))
        # Test random response
        response = generate_response(user_data, "hello")
        self.assertIn("Ruzan", response)

if __name__ == '__main__':
    unittest.main()
