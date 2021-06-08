# based on yWithMorphologySequentialStreamDropoutDev_Ngrams_Log.py

import random
import sys
from corpus import CORPUS

objectiveName = "LM"

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--language", dest="language", type=str, default=CORPUS)
parser.add_argument("--alpha", dest="alpha", type=float, default=0.0)
parser.add_argument("--gamma", dest="gamma", type=int, default=1)
parser.add_argument("--delta", dest="delta", type=float, default=1.0)
parser.add_argument("--cutoff", dest="cutoff", type=int, default=15)
parser.add_argument("--idForProcess", dest="idForProcess", type=int, default=random.randint(0,10000000))
import random



args=parser.parse_args()
print(args)


assert args.alpha >= 0
assert args.alpha <= 1
assert args.delta >= 0
assert args.gamma >= 1





myID = args.idForProcess


TARGET_DIR = "/u/scr/mhahn/deps/memory-need-ngrams-morphology/"



posUni = set()

posFine = set()

def getRepresentation(lemma):
   if lemma == "させる" or lemma == "せる":
     return "CAUSATIVE"
   elif lemma == "れる" or lemma == "られる" or lemma == "える" or lemma == "得る" or lemma == "ける":
     return "PASSIVE_POTENTIAL"
   else:
     return lemma


from math import log, exp
from random import random, shuffle, randint, Random, choice

header = ["index", "word", "lemma", "posUni", "posFine", "morph", "head", "dep", "_", "_"]

from corpusIterator_V import CorpusIterator_V

originalDistanceWeights = {}

morphKeyValuePairs = set()

vocab_lemmas = {}

import finnish_noun_segmenter_coarse
def processVerb(verb): 
   # assumption that each verb is a single word
   for vb in verb:
      labels = vb["morph"]
      morphs = finnish_noun_segmenter_coarse.get_abstract_morphemes(labels)
      morphs[0] = vb["lemma"] # replace "ROOT" with actual root
      data.append(morphs)

corpusTrain = CorpusIterator_V(args.language,"train", storeMorph=True).iterator(rejectShortSentences = False)
pairs = set()
counter = 0
data = []
for sentence in corpusTrain:
    verb = []
    for line in sentence:
       if line["posUni"] == "NOUN" or line["posUni"] == "ADJ":
          verb.append(line)
          processVerb(verb)
          verb = []

from collections import Counter
import matplotlib.pyplot as plt

def bar_num_morphs(data):
    """
    Produces a bar chart of the number of morphemes in the word list.

    Params:
     - data: A list of lists of verbs, where each inner list item is a lemma that has morphemes delimited by "+"

    Returns:
     - nothing, creates a PNG of a bar chart of the distribution of number of morphemes
    """
    hist = Counter()
    for wd_list in data:
         hist[len(wd_list)] += 1
    plt.bar(hist.keys(), hist.values())
    plt.savefig("finnish_nouns_coarse_num_morphs.png")

bar_num_morphs(data)

words = []

### splitting lemmas into morphemes -- each affix is a morpheme ###
affixFrequencies = {}
for verbWithAff in data:
  for affix in verbWithAff[1:]: # TODO: why does this start at 1? mhahn: in Japanese, this is to only conider suffixes, not the stem. Should probably be changed for Korean.
        affixFrequencies[affix] = affixFrequencies.get(affix, 0) + 1

itos = set() # set of affixes
for verbWithAff in data:
  for affix in verbWithAff[1:]:
        itos.add(affix)
itos = sorted(list(itos)) # sorted list of verb affixes
stoi = dict(list(zip(itos, range(len(itos))))) # assigning each affix and ID

itos_ = itos[::]
shuffle(itos_)
weights = dict(list(zip(itos_, [2*x for x in range(len(itos_))]))) # TODO: why?? mhahn: this amounts to a random assignment from affixes to even integers

from collections import defaultdict
affixChains = defaultdict(int)
for d in data:
   affixChains[tuple(d[1:])] += 1

def getCorrectOrderCountPerMorpheme(weights, coordinate, newValue):
   correct = 0
   incorrect = 0

   for affixChain, count in affixChains.items():
      vb = affixChain
      for i in range(0, len(vb)):
         for j in range(0, i):
             if vb[i] == coordinate:
                 weightI = newValue
             else:
                weightI = weights[getRepresentation(vb[i])]

             if vb[j] == coordinate:
                 weightJ = newValue
             else:
                weightJ = weights[getRepresentation(vb[j])]
             if weightI > weightJ:
               correct+=count
             else:
               incorrect+=count
   return correct/(correct+incorrect)

lastMostCorrect = 0
for iteration in range(1000):

  coordinate = choice(itos)
  while random() < 0.8 and affixFrequencies[coordinate] < 50 and iteration < 100: 
     coordinate = choice(itos)

  mostCorrect, mostCorrectValue = 0, None
  for newValue in [-1] + [2*x+1 for x in range(len(itos))] + [weights[coordinate]]:
     if random() < 0.8 and newValue != weights[coordinate] and iteration < 50:
         continue
     weights_ = {x : y for x,y in weights.items()}
     weights_[coordinate] = newValue
     correctCount = getCorrectOrderCountPerMorpheme(weights_, None, None)
     if correctCount > mostCorrect:
        mostCorrectValue = newValue
        mostCorrect = correctCount
  print(iteration, mostCorrect)

  assert mostCorrect >= lastMostCorrect
  lastMostCorrect = mostCorrect

  weights[coordinate] = mostCorrectValue
 # assert getCorrectOrderCount(weights, None, None) == mostCorrect
  itos_ = sorted(itos, key=lambda x:weights[x])
  weights = dict(list(zip(itos_, [2*x for x in range(len(itos_))])))
  #assert getCorrectOrderCount(weights, None, None) == getCorrectOrderCount(weights, None, None), (mostCorrect, getCorrectOrderCount(weights, None, None))
  #assert mostCorrect == getCorrectOrderCount(weights, None, None), (mostCorrect, getCorrectOrderCount(weights, None, None))
#   for x in itos_:
#    if affixFrequencies[x] >= 50:
#      print("\t".join([str(y) for y in [x, weights[x], affixFrequencies[x]]]))

with open("output/extracted_"+args.language+"_"+__file__+"_"+str(myID)+".tsv", "w") as outFile:
  for x in itos_:
     print("\t".join([str(y) for y in [x, weights[x], affixFrequencies[x]]]), file=outFile)
