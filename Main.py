from Dictionary import Dictionary
from Test import Test
from TestCreator import TestCreator

def get_dictionary(dictionary_name):
    dictionary = Dictionary(dictionary_name)
    dictionary.add_term("term1", "definition1")
    dictionary.add_term("term2", "definition2")
    dictionary.add_term("term3", "definition3")
    return dictionary

# Пример использования:
dictionary1 = get_dictionary("Dictionary1")
dictionary2 = get_dictionary("Dictionary2")

english_test_instance = Test("English Test", [dictionary1, dictionary2], 3, 90, 95)
test_creator = TestCreator(english_test_instance)

# Создаем тест с seed=42
test_result = test_creator.create_test(seed=42)
print(test_result) 