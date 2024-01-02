class Dictionary:
    def __init__(self, name, terms=None):
        self.name = name
        self.terms = terms or {}

    def add_term(self, term, definition):
        self.terms[term] = definition

    def remove_term(self, term):
        if term in self.terms:
            del self.terms[term]
        else:
            print(f"Термин '{term}' не найден в словаре '{self.name}'.")

    def get_all_terms(self):
        return self.terms

    def get_term_definition(self, term):
        return self.terms.get(term, f"Термин '{term}' не найден в словаре '{self.name}'.")
