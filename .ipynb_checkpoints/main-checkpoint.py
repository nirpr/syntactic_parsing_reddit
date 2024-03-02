import json
import time
import benepar

parser = benepar.Parser("benepar_en3")  # todo: uncomment this line once you have benepar installed


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


    return set(), set()


if __name__ == '__main__':
    start = time.time()

    with open('config.json', 'r') as json_file:
        config = json.load(json_file)

    explicit, implicit = identify_explicit_and_implicit_that_clauses(config['input_filename'])
    print(f'found {len(explicit)} explicit, and {len(implicit)} implicit cases')

    # with open(config['explicit_filename'], 'w') as fout:
    #     fout.write('\n'.join(explicit))
    # with open(config['implicit_filename'], 'w') as fout:
    #     fout.write('\n'.join(implicit))

    print(f'total time: {round(time.time()-start, 0)} sec')
