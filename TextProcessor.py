import re
from collections import Counter

class TextProcessor:
    def __init__(self):
        self.word_counter = Counter()

    def clean_text(self, text):
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        return text

    def count_words(self, text):
        cleaned_text = self.clean_text(text)
        words = cleaned_text.split()
        self.word_counter.update(words)
        return dict(self.word_counter)
