import json
import time
import benepar
import spacy

parser = benepar.Parser("benepar_en3")
nlp = spacy.load("en_core_web_sm")


def identify_explicit_and_implicit_that_clauses(filename):
    # todo: implement this function
    print(f'looking for explicit and implicit "that" usages in {filename}')

    # todo: note that we're looking for sentences where the optional "that" is used (or omitted)
    #  as a subordinating conjunction between main and subordinate clause; we say that the usage is "explicit" in cases
    #  where "that" is used but could be omitted, and "implicit", where it's omitted but could be used

    # todo: example sentences:
    #  in my head, i feel that i ended our friendship fairly (explicit)
    #  some people argue that all you need to know is calories in vs calories out, end of story (explicit)
    #  you’re correct, i believe it would be an active exhaust that changes in volume based on drive mode (implicit)
    #  we agree this specific suggestion is much better (implicit)

    explicit_sentences = set()
    implicit_sentences = set()

    with open(filename, 'r', encoding='utf-8') as file:
        sentences = file.readlines()

    for sentence in sentences:
        doc = nlp(sentence)
        for token in doc:
            if token.dep_ == 'mark' and token.text.lower() == 'that':
                if token.head.pos_ == 'VERB':
                    explicit_sentences.add(sentence)
                    break
                elif token.head.pos_ == 'AUX' and token.head.head.pos_ == 'VERB':
                    implicit_sentences.add(sentence)
                    break

    return explicit_sentences, implicit_sentences


if __name__ == '__main__':
    start = time.time()

    with open('config.json', 'r', encoding='utf-8') as json_file:
        config = json.load(json_file)

    explicit, implicit = identify_explicit_and_implicit_that_clauses(config['input_filename'])
    print(f'found {len(explicit)} explicit, and {len(implicit)} implicit cases')

    with open(config['explicit_filename'], 'w', encoding='utf-8') as fout:
        fout.write('\n'.join(explicit))
    with open(config['implicit_filename'], 'w', encoding='utf-8') as fout:
        fout.write('\n'.join(implicit))

    print(f'total time: {round(time.time()-start, 0)} sec')
