import json
import time
import benepar
import en_core_web_sm
import spacy
from sklearn.feature_selection import SelectKBest
import numpy as np
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
    'in order that', 'now that', 'that', 'for fear that', 'lest', 'lest', 'whilst'
]


def identify_explicit_and_implicit_that_clauses2(filename):
    print(f'looking for explicit and implicit "that" usages in {filename}')

    nlp = en_core_web_sm.load()
    nlp.add_pipe("benepar", config={"model": "benepar_en3"})

    explicit_that_clauses = set()
    implicit_that_clauses = set()
    all_sentences = set()
    with open(filename, "r", encoding='utf-8') as file:
        for line in file:
            lineFound = False
            all_sentences.add(line)
            line = ' '.join(line.split())

            line = line.strip()

            try:
                doc = nlp(line)
            except:
                print("ERROR IN PERCER")
                continue

            for sentence in doc.sents:
                for token in sentence._.constituents:
                    if 'SBAR' in token._.labels:
                        if 'that' == token[0].text:
                            # Check if token has a parent and if its parent's tag is 'VP'
                            if token._.parent and 'VP' in token._.parent._.labels:
                                explicit_that_clauses.add(sentence.text)
                                lineFound = True

                        if token[0].text not in conjunction_and_question_words:
                            # Check if token has a parent and if its parent's tag is 'VP'
                            if token._.parent and 'VP' in token._.parent._.labels:
                                implicit_that_clauses.add(sentence.text)
                                lineFound = True
                                break

                if lineFound:
                    break

    return explicit_that_clauses, implicit_that_clauses

def check_explicit(token):
    if 'that' == token[0].text:
        # Check if token has a parent and if its parent's tag is 'VP'
        if token._.parent and 'VP' in token._.parent._.labels:
            return True
    return False


def check_implicit(token):
    if token[0].text not in conjunction_and_question_words:
        # Check if token has a parent and if its parent's tag is 'VP'
        if token._.parent and 'VP' in token._.parent._.labels:
            return True

    return False


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
    all_sentences = set()
    to_break = False
    check = False

    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            lineFound = False
            all_sentences.add(line)
            line = ' '.join(line.split())

            line = line.strip()

            try:
                doc = nlp(line)
            except:
                print("ERROR IN PERCER")
                continue

            for sentence in doc.sents:
                # Parse the sentence using Benepar
                tree = parser.parse(sentence.text)

                # Extract verbs and their children
                for subtree in tree.subtrees():
                    # Check if the label of the subtree is 'VP'
                    if subtree.label() == 'VP':
                        # Iterate over the children of 'VP'
                        for child1 in subtree:
                            # if subtree.label() == 'VB' or subtree.label() == 'VBZ' or subtree.label() == 'VBP' or subtree.label() == 'VBD' or subtree.label() == 'VBG' or subtree.label() == 'VBN' or subtree.label() == 'MD' or subtree.label() == 'VBZ':
                            #     check = True

                            if child1.label() == 'SBAR':
                                for child in child1:
                                    # Check if any child has the label 'S'
                                    if child.label() == 'S':
                                        if child1.leaves()[0] == 'that':
                                            explicit_sentences.add(sentence)
                                        # for i, child2 in enumerate(subtree):
                                        #     if child2 == child1:
                                        #         if i > 0:
                                        #             if subtree[i - 1].label() == 'VB':
                                        #                 # Check if 'that' is a leaf of the 'SBAR' subtree
                                        #                 if child1.leaves()[0] == 'that':
                                        #                     explicit_sentences.add(sentence)

                                if child1.leaves()[0] not in conjunction_and_question_words:
                                    implicit_sentences.add(sentence)

                    check = False

                                # for child in child1:
                                #     # Check if any child has the label 'S'
                                #     if child.label() == 'S':
                                #         # Check if 'S' has a left subtree 'NP'
                                #         if child[0].label() == 'NP':
                                #             # Check if 'NP' has a single subtree that has one leaf
                                #             if len(list(child[0])) == 1 and len(child[0][0].leaves()) == 1:
                                #                 implicit_sentences.add(sentence)




                        # # Iterate over all subtrees of 'subtree'
                        # for i in range(len(list(subtree)) - 1):
                        #     # Check if the current subtree has 'VBZ' label
                        #     if subtree[i].label() == 'VBZ' and len(subtree[i].leaves()) == 1:
                        #         # Check if the next subtree to its right has 'SBAR' label
                        #         if subtree[i + 1].label() == 'SBAR':
                        #             implicit_sentences.add(sentence)

                        # s_subtrees = [child for child in subtree[1] if child.label() == 'S']
                        # if len(s_subtrees) == 1:
                        #     # Check if 'S' has a left subtree 'NP' with a single subtree that has one leaf
                        #     if s_subtrees[0][0].label() == 'NP' and len(
                        #         list(s_subtrees[0][0])) == 1 and len(
                        #                 s_subtrees[0][0][0].leaves()) == 1:
                        #         implicit_sentences.add(sentence)

    return explicit_sentences, implicit_sentences



def identify_explicit_and_implicit_that_clauses3(filename):
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
    all_sentences = set()
    to_break = False
    check1 = False
    check2 = False

    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            lineFound = False
            all_sentences.add(line)
            line = ' '.join(line.split())

            line = line.strip()

            try:
                doc = nlp(line)
            except:
                print("ERROR IN PERCER")
                continue

            for sentence in doc.sents:
                # Parse the sentence using Benepar
                tree = parser.parse(sentence)

                # Extract verbs and their children
                for subtree in tree.subtrees():
                    # Check if the label of the subtree is 'VP'
                    if subtree.label() == 'VP':
                        # Iterate over the children of 'VP'
                        for child1 in subtree:
                            # Check if any child has the label 'SBAR'
                            if child1.label() == 'SBAR':
                                # Check if 'that' is a leaf of the 'SBAR' subtree
                                if 'that' in child1.leaves():
                                    explicit_sentences.add(sentence)
                                    # # Iterate over the children of 'SBAR'
                                    # for child2 in child1:
                                    #     # Check if any child has the label 'S'
                                    #     if child2.label() == 'S':
                                    #         # Check if 'S' subtree is to the right of 'that' leaf
                                    #         if child1.leaves().index('that') < child1.leaves().index(
                                    #                 child2.leaves()[0]):
                                    #             for i, child in enumerate(subtree):
                                    #                 if child == child1:
                                    #                     if i > 0:
                                    #                         if subtree[i - 1].label() == 'VB':
                                    #                             explicit_sentences.add(sentence)

                        # Check if 'VP' subtree has exactly two subtrees
                        if len(list(subtree)) >= 2:
                            # Check if the left subtree is 'VBZ' and has only one leaf
                            if subtree[0].label() == 'VBZ' and len(subtree[0].leaves()) == 1:
                                # Check if the right subtree is 'SBAR'
                                if subtree[1].label() == 'SBAR':
                                    implicit_sentences.add(sentence)
                                    # # Check if 'SBAR' has a single 'S' subtree
                                    # s_subtrees = [child for child in subtree[1] if child.label() == 'S']
                                    # if len(s_subtrees) == 1:
                                    #     # Check if 'S' has a left subtree 'NP' with a single subtree that has one leaf
                                    #     if s_subtrees[0][0].label() == 'NP' and len(
                                    #         list(s_subtrees[0][0])) == 1 and len(
                                    #                 s_subtrees[0][0][0].leaves()) == 1:
                                    #         implicit_sentences.add(sentence)







        # sentences = file.readlines()
        #
        # for sentence in sentences:
        #     # Parse the sentence using Benepar
        #     tree = parser.parse(sentence)
        #
        #     # Extract verbs and their children
        #     for subtree in tree.subtrees():
        #         # Check if the label of the subtree is 'VP'
        #         if subtree.label() == 'VP':
        #             # Iterate over the children of 'VP'
        #             for child1 in subtree:
        #                 # Check if any child has the label 'SBAR'
        #                 if child1.label() == 'SBAR':
        #                     # Check if 'that' is a leaf of the 'SBAR' subtree
        #                     if 'that' in child1.leaves():
        #                         explicit_sentences.add(sentence)
        #                         # # Iterate over the children of 'SBAR'
        #                         # for child2 in child1:
        #                         #     # Check if any child has the label 'S'
        #                         #     if child2.label() == 'S':
        #                         #         # Check if 'S' subtree is to the right of 'that' leaf
        #                         #         if child1.leaves().index('that') < child1.leaves().index(
        #                         #                 child2.leaves()[0]):
        #                         #             for i, child in enumerate(subtree):
        #                         #                 if child == child1:
        #                         #                     if i > 0:
        #                         #                         if subtree[i - 1].label() == 'VB':
        #                         #                             explicit_sentences.add(sentence)
        #
        #             # Check if 'VP' subtree has exactly two subtrees
        #             if len(list(subtree)) >= 2:
        #                 # Check if the left subtree is 'VBZ' and has only one leaf
        #                 if subtree[0].label() == 'VBZ' and len(subtree[0].leaves()) == 1:
        #                     # Check if the right subtree is 'SBAR'
        #                     if subtree[1].label() == 'SBAR':
        #                         implicit_sentences.add(sentence)
        #                         # # Check if 'SBAR' has a single 'S' subtree
        #                         # s_subtrees = [child for child in subtree[1] if child.label() == 'S']
        #                         # if len(s_subtrees) == 1:
        #                         #     # Check if 'S' has a left subtree 'NP' with a single subtree that has one leaf
        #                         #     if s_subtrees[0][0].label() == 'NP' and len(
        #                         #         list(s_subtrees[0][0])) == 1 and len(
        #                         #                 s_subtrees[0][0][0].leaves()) == 1:
        #                         #         implicit_sentences.add(sentence)




            # # Iterate over the leaves of the parse tree
            # for i in range(len(tree.leaves())):
            #     # Check if the leaf is 'that'
            #     if tree.leaves()[i] == 'that':
            #         # Check if the previous leaf is a verb
            #         if i > 0 and nlp(tree.leaves()[i - 1])[0].pos_ == 'VERB':
            #             # Check if the label of the subtree is 'VP'
            #             if subtree.label() == 'VP':
            #                 # Iterate over the children of 'VP'
            #                 for child1 in subtree:
            #                     # Check if any child has the label 'SBAR'
            #                     if child1.label() == 'SBAR':
            #                         # Check if 'that' is a leaf of the 'SBAR' subtree
            #                         if 'that' in child1.leaves():
            #                             # Iterate over the children of 'SBAR'
            #                             for child2 in child1:
            #                                 # Check if any child has the label 'S'
            #                                 if child2.label() == 'S':
            #                                     # Check if 'S' subtree is to the right of 'that' leaf
            #                                     if child1.leaves().index('that') < child1.leaves().index(
            #                                             child2.leaves()[0]):
            #                                         explicit_sentences.add(sentence)



            # # Check if the label of the subtree is 'VP'
            # if subtree.label() == 'VP':
            #     # Iterate over the children of 'VP'
            #     for child1 in subtree:
            #         # Check if any child has the label 'SBAR'
            #         if child1.label() == 'SBAR':
            #             # Iterate over the leaves of 'SBAR'
            #             for i in range(len(child1.leaves())):
            #                 # Check if the leaf is 'that'
            #                 if child1.leaves()[i] == 'that':
            #                     # Check if the previous leaf is a verb
            #                     if i > 0 and nlp(child1.leaves()[i - 1])[0].pos_ == 'VERB':
            #                         # Iterate over the children of 'SBAR'
            #                         for child2 in child1:
            #                             # Check if any child has the label 'S'
            #                             if child2.label() == 'S':
            #                                 # Check if 'S' subtree is to the right of 'that' leaf
            #                                 if child1.leaves().index('that') < child1.leaves().index(
            #                                         child2.leaves()[0]):
            #                                     explicit_sentences.add(sentence)


            # # Check if the label of the subtree is 'VP'
            # if subtree.label() == 'VP':
            #     # Check if 'VP' subtree has exactly two subtrees
            #     if len(list(subtree)) >= 2:
            #         # Check if the left subtree is 'VBZ' and has only one leaf
            #         if subtree[0].label() == 'VBZ' and len(subtree[0].leaves()) == 1:
            #             # Check if the right subtree is 'SBAR'
            #             if subtree[1].label() == 'SBAR':
            #                 # Check if 'SBAR' has a single 'S' subtree
            #                 s_subtrees = [child for child in subtree[1] if child.label() == 'S']
            #                 if len(s_subtrees) == 1:
            #                     # Check if 'S' has a left subtree 'NP' with a single subtree that has one leaf
            #                     if s_subtrees[0][0].label() == 'NP' and len(
            #                         list(s_subtrees[0][0])) == 1 and len(
            #                             s_subtrees[0][0][0].leaves()) == 1:
            #                         implicit_sentences.add(sentence)



    # for sentence in sentences:
    #     # Parse the sentence using spaCy
    #     doc = nlp(sentence)
    #
    #     # Parse the sentence using Benepar to get constituency parse tree
    #     tree = parser.parse(sentence)
    #
    #     # Extract verbs and their children
    #     for token in doc:
    #             if token.pos_ == 'VERB':
    #                 # Check if 'that' is explicitly present in the constituency parse tree
    #                 if 'that' in [child.text for child in token.children]:
    #                     explicit_sentences.add(sentence)
    #                     to_break = True
    #                 # Check if there's a clause that could have 'that' implicitly
    #
    #                 for subtree in tree.subtrees():
    #                     if subtree.label() == 'S' and subtree[0].label() == 'S' or subtree.label() == 'SBAR':
    #                         check1 = True
    #
    #                 for child in token.children:
    #                     if child.dep_ == 'ccomp':
    #                         check2 = True
    #
    #                 if check1 and check2:
    #                     implicit_sentences.add(sentence)
    #
    #             if to_break:
    #                 to_break = False
    #                 break
    #
    #             check2 = False
    #             check1 = False


    # for sentence in sentences:
    #     doc = nlp(sentence)
    #     for token in doc:
    #         if token.dep_ == 'mark' and token.text.lower() == 'that':
    #             counter += 1
    #             if token.head.pos_ == 'VERB':
    #                 if counter % 300 == 0:
    #                     displacy.render(doc, style="dep", jupyter=True)
    #
    #                 explicit_sentences.add(sentence)
    #                 break
    #             elif token.head.pos_ == 'AUX' and token.head.head.pos_ == 'VERB':
    #                 implicit_sentences.add(sentence)
    #                 break

    # parser = benepar.Parser("benepar_en3")
    #
    # for sentence in sentences:
    #     # Parse the sentence using Benepar
    #     parse_tree = parser.parse(sentence)
    #
    #     # Process the parsed tree
    #     for node in parse_tree:
    #         # Check for explicit and implicit structures
    #         if node.label() == 'S':
    #             explicit_sentences.add(sentence.strip())
    #         elif node.label() == 'SBAR':
    #             implicit_sentences.add(sentence.strip())


    return explicit_sentences, implicit_sentences


def print_k_best(x_train_vec, y_train, features_names):
    k_best = SelectKBest(k=15)
    k_best.fit_transform(x_train_vec, y_train)
    best_features = k_best.get_support()
    features = np.array(features_names)

    print(f'15 best features: {features[best_features]}')


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
