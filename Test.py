class Test:
    def __init__(self, name, dictionaries, num_questions, term_ratio, acceptable_error):
        self.name = name
        self.dictionaries = dictionaries
        self.num_questions = num_questions
        self.term_ratio = term_ratio
        self.acceptable_error = acceptable_error

        # Проверка наличия достаточного количества терминов в словарях
        total_terms = sum(len(dictionary.terms) for dictionary in dictionaries)
        if total_terms < num_questions:
            raise ValueError("Недостаточно терминов для создания теста.")