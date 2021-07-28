from alias_functions import is_verb_or_pronoun
from alias_functions import is_size_bowl
from alias_functions import is_small_medium_or_large
from conceptNet_api import filter_out_non_foods


class Step:
    def __init__(self, step):
        self.verbs = []
        self.subjects = {}
        self.foods = {}

        num_sentences = 0
        for sentence in step:
            self.loop_over_sentence_in_step(num_sentences, sentence)
            num_sentences += 1
        self.find_foods_from_subjects()

        # print("[Step_constructor] verbs: ", self.verbs)
        # print("[Step_constructor]subjects: ", self.subjects)
        # print("[Step_constructor]foods: ", self.foods)

    def loop_over_sentence_in_step(self, num_sentences, sentence):
        i = 0
        self.subjects[num_sentences] = []
        while i < len(sentence):
            i = self.initialize_verb_and_nouns_in_step(i, sentence, num_sentences)

    def initialize_verb_and_nouns_in_step(self, i, sentence, num_sentences):
        token = sentence[i]
        token_text = token.lemma_.lower()

        if is_verb_or_pronoun(token) and token_text not in self.verbs:
            self.verbs.append(token_text)
        elif token.dep_ == "compound" and sentence[i + 1].pos_ == "NOUN":
            compound_noun = str(token_text + " " + sentence[i + 1].lemma_.lower())
            if compound_noun not in self.subjects[num_sentences]:
                self.subjects[num_sentences].append(compound_noun)
        elif (token.pos_ == "NOUN" and not token.dep_ == "compound"
              and token_text not in self.subjects[num_sentences]):
            self.subjects[num_sentences].append(token_text)
        elif is_small_medium_or_large(token_text):
            if is_size_bowl(sentence, i + 1):
                self.subjects[num_sentences].append(token_text + " " + sentence[i + 1].lemma_.lower())
                i += 1
            elif is_size_bowl(sentence, i + 2):
                self.subjects[num_sentences].append(token_text + " " + sentence[i + 2].lemma_.lower())
                i += 2
            elif is_size_bowl(sentence, i + 3):
                self.subjects[num_sentences].append(token_text + " " + sentence[i + 3].lemma_.lower())
                i += 3
        return i + 1

    def find_foods_from_subjects(self):
        # print("[find_foods_from_subjects] subject dic: " + str(self.subjects))
        for key in self.subjects:
            # print("[find_foods_from_subjects] subject_list: " + str(self.subjects[key]))
            self.foods[key] = filter_out_non_foods(self.subjects[key])
