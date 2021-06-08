def get_abstract_morphemes(labels):
    """
    Takes a list of UD labels for a Finnish verb and returns a list of abstract morphemes.
    Parameters:
     - labels: A list of UD labels for a Finnish verb, such as 'Definite=Def|Mood=Ind|Number=Sing|Person=3|Tense=Past|VerbForm=Fin|Voice=Act'

    Returns:
     - A list of abstract morphemes in order. 
    """

    morphs = ["ROOT"]

    if len(labels) < 3:
        return morphs

    # creating dictionary from labels string
    label_pairs = labels.split("|")
    label_dict = {}
    for pair in label_pairs:
        k, v = pair.split("=")
        label_dict[k] = v
    for x in sorted(list(label_dict)):
        morphs.append(x)
           
    return morphs

# Derivation: https://universaldependencies.org/fi/feat/Derivation.html. Even though it's labeled, it's part of the lemma form. 
# I think it would be accurate to either include the derivation (so it's like verb + derivation = noun) or not include the derivation (just deal with root noun).
# I'm including derivation here, but it would make sense to not have it also. 
