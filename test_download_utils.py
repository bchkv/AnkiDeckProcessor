import unittest
from download_utils import get_pronunciation  # Import the function you're testing

TEST_MEDIA_DIRECTORY_PATH = '/Users/bochkovoy/Downloads'


class TestDownloadUtils(unittest.TestCase):
    def test_get_pronunciation(self):
        # Define the test cases
        test_words = ['hello', 'world', 'python', 'nonexistentword', 'get away with']
        for word in test_words:
            with self.subTest(word=word):
                result = get_pronunciation(word, TEST_MEDIA_DIRECTORY_PATH)
                # You might want to check specific aspects, like file existence or return values
                self.assertTrue(result, f"Failed to handle word: {word}")


if __name__ == "__main__":
    unittest.main()
