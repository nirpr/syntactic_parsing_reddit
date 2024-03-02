import json
import time
import benepar
import en_core_web_sm
import spacy
from sklearn.feature_selection import SelectKBest, chi2
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from spacy import displacy

benepar.download('benepar_en3')
parser = benepar.Parser("benepar_en3")
nlp = spacy.load("en_core_web_sm")

conjunction_and_question_words = [
    'that', 'who', 'whom', 'whose', 'what', 'which', 'when', 'where', 'why', 'how',
    'and', 'but', 'or', 'nor', 'for', 'so', 'yet', 'although', 'because', 'since',
    'unless', 'while', 'whereas', 'however', 'therefore', 'meanwhile', 'nevertheless',
    'nonetheless', 'notwithstanding', 'furthermore', 'moreover', 'hence', 'thus',
    'consequently', 'accordingly', 'indeed', 'besides', 'otherwise', 'after', 'before',
    'if', 'unless', 'since', 'while', 'until', 'when', 'whenever', 'wherever', 'though',
    'although', 'even', 'as', 'once', 'lest', 'than', 'whether', 'like', 'to',
    'whether', 'whether or not', 'which', 'whoever', 'whomever', 'whatever', 'whichever',
    'whenever', 'wherever', 'however', 'why', 'how', 'because', 'since', 'if', 'whether',
    'than', 'though', 'although', 'even though', 'even if', 'as if', 'as though', 'while',
    'whereas', 'when', 'unless', 'provided that', 'in case', 'in the event that', 'so that',
    'in order that', 'now that', 'that', 'for fear that', 'lest', 'lest', 'whilst',
    'but if', 'so if', 'even if', 'even though', 'unless', 'lest', 'whereas', 'while',
    'provided', 'providing', 'whether', 'whether or not', 'how', 'why', 'where', 'when',
    'what', 'which', 'who', 'whose'
]

def identify_explicit_and_implicit_that_clauses(filename):
    print(f'looking for explicit and implicit "that" usages in {filename}')

    # Loading the English language model for spaCy
    nlp = en_core_web_sm.load()
    # Adding Benepar parser to the pipeline
    nlp.add_pipe("benepar", config={"model": "benepar_en3"})

    # Initialize sets to store explicit and implicit sentences
    explicit_sentences = set()
    implicit_sentences = set()

    with open(filename, "r", encoding='utf-8') as file:
        # Iterating through each line in the file
        for line in file:
            # Initializing a flag to track if the line contains the desired structure so that we can break the loop
            lineFound = False

            # Cleaning and preprocessing the line
            line = ' '.join(line.split())
            line = line.strip()

            try:
                # Parsing the line using spaCy
                doc = nlp(line)
            except:
                print("ERROR with parsing the line")
                continue

            # Iterating through each sentence in the parsed document
            for sentence in doc.sents:
                # Iterating through each constituent (subtree) in the sentence
                for token in sentence._.constituents:
                    # Checking if the constituent is a subordinate clause
                    if 'SBAR' in token._.labels:
                        # Checking if the first word of the subordinate clause is 'that'
                        if 'that' == token[0].text:
                            # Check if token has a parent and if its parent's tag is 'VP'
                            if token._.parent and 'VP' in token._.parent._.labels:
                                explicit_sentences.add(sentence.text)
                                lineFound = True

                        # Checking if the first word of the subordinate clause is not a conjunction or question word
                        if token[0].text not in conjunction_and_question_words:
                            # Check if token has a parent and if its parent's tag is 'VP'
                            if token._.parent and 'VP' in token._.parent._.labels:
                                implicit_sentences.add(sentence.text)
                                lineFound = True
                                break

                if lineFound:
                    break

    return explicit_sentences, implicit_sentences

def select_distinguishing_words(set1_sentences, set2_sentences, k=10):
    # Convert sets of sentences to lists
    set1_sentences = list(set1_sentences)
    set2_sentences = list(set2_sentences)

    # Combine both sets of sentences
    all_sentences = set1_sentences + set2_sentences

    # Label the sentences
    labels = ['Set 1'] * len(set1_sentences) + ['Set 2'] * len(set2_sentences)

    # Convert sentences to numerical features using CountVectorizer
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(all_sentences)

    # Select top k features using SelectKBest and chi-squared test
    selector = SelectKBest(chi2, k=k)
    X_selected = selector.fit_transform(X, labels)

    # Get selected feature names
    feature_names = vectorizer.get_feature_names_out()
    selected_feature_indices = selector.get_support(indices=True)
    selected_features = [feature_names[i] for i in selected_feature_indices]

    return selected_features


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
