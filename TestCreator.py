import random

class TestCreator:

    def __init__(self, test):
        self.test = test

    def create_test(self, seed=None):
        if seed is not None:
            random.seed(seed)

        questions = []
        answers = []

        while (len(answers) != self.test.num_questions):
            if (random.randint(0, 100) < self.test.term_ratio):
                term_or_definition = "term"
            else:
                term_or_definition = "definition"

            selected_dictionary = self.test.dictionaries[random.randint(0, len(self.test.dictionaries) - 1)]

            dictionary_terms = list(selected_dictionary.get_all_terms().items())

            # Нет, не костыль...
            rnd = random.randint(0, len(dictionary_terms) - 1)
            count = 0

            for i in dictionary_terms:
                if (rnd == count):
                  term, definition = i 
                  break
                count += 1

            bool_collision = False 
            for i in questions:
                if term == i or definition == i:
                    bool_collision = True
                    break
            if (bool_collision == True):
                continue

            questions.append(term if term_or_definition == "term" else definition)
            answers.append(definition if term_or_definition == "term" else term)

        return {"questions": questions, "answers": answers}
