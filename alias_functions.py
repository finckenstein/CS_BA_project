import ast
import csv


def string_to_dictionary(prep_str):
    return ast.literal_eval(prep_str)


def write_to_csv(data):
    fields = ['URL', 'Preparation', 'Utils']
    filename = "found_utils.csv"
    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)


def is_size_bowl(sentence, offset):
    return offset < len(sentence) - 1 and "bowl" in sentence[offset].text.lower()


def is_verb_or_pronoun(token):
    return token.pos_ == "VERB" or token.pos_ == "PRON"


def is_small_medium_or_large(token_text):
    return token_text == "small" or token_text == "medium" or token_text == "large"
