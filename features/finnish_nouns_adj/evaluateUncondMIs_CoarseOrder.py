# based on yWithMorphologySequentialStreamDropoutDev_Ngrams_Log.py

import random
import sys
from corpus import CORPUS
from estimateTradeoffHeldout_Pairs import calculateMemorySurprisalTradeoff
from math import log, exp
from corpusIterator_V import CorpusIterator_V
from random import shuffle, randint, Random, choice



objectiveName = "LM"

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--language", dest="language", type=str, default=CORPUS)
parser.add_argument("--POS", dest="POS", type=str, default="NOUN")
parser.add_argument("--alpha", dest="alpha", type=float, default=1.0)
parser.add_argument("--gamma", dest="gamma", type=int, default=1)
parser.add_argument("--delta", dest="delta", type=float, default=1.0)
parser.add_argument("--cutoff", dest="cutoff", type=int, default=3)
parser.add_argument("--idForProcess", dest="idForProcess", type=int, default=random.randint(0,10000000))
import random



args=parser.parse_args()
print(args)


assert args.alpha >= 0
assert args.alpha <= 1
assert args.delta >= 0
assert args.gamma >= 1





myID = args.idForProcess


TARGET_DIR = "results/"+__file__.replace(".py", "")



posUni = set() 

posFine = set() 

def getRepresentation(lemma):
    return lemma["coarse"]

def getSurprisalRepresentation(lemma):
    return lemma["fine"]

from math import log, exp
from random import random, shuffle, randint, Random, choice

header = ["index", "word", "lemma", "posUni", "posFine", "morph", "head", "dep", "_", "_"]

from corpusIterator_V import CorpusIterator_V

originalDistanceWeights = {}

morphKeyValuePairs = set()

vocab_lemmas = {}

import finnish_noun_segmenter_coarse
import finnish_noun_segmenter
def processVerb(verb, data_):
    # assumption that each verb is a single word
   for vb in verb:
      labels = vb["morph"]
      if "VerbForm=Part" in labels or "VerbForm=Inf" in labels:
          continue
      morphs = finnish_noun_segmenter_coarse.get_abstract_morphemes(labels)
      fine = finnish_noun_segmenter.get_abstract_morphemes(labels)
      morphs[0] = vb["lemma"] # replace "ROOT" w actual root
      fine[0] = vb["lemma"] # replace "ROOT" w actual root
      lst_dict = []
      for i in range(len(fine)):
        morph_dict = {"fine": fine[i], "coarse": morphs[i]}
        lst_dict.append(morph_dict)
      data_.append(lst_dict)

corpusTrain = CorpusIterator_V(args.language,"train", storeMorph=True).iterator(rejectShortSentences = False)
corpusDev = CorpusIterator_V(args.language,"dev", storeMorph=True).iterator(rejectShortSentences = False)

pairs = set()
counter = 0
data_train = []
data_dev = []
for corpus, data_ in [(corpusTrain, data_train), (corpusDev, data_dev)]:
  for sentence in corpus:
    verb = []
    for line in sentence:
       if line["posUni"] == args.POS:
          verb.append(line)
          processVerb(verb, data_)
          verb = []

words = []

affixFrequencies = {}
for verbWithAff in data_train:
  for affix in verbWithAff[1:]:
    affixLemma = getRepresentation(affix)
    affixFrequencies[affixLemma] = affixFrequencies.get(affixLemma, 0)+1


itos = set()
for data_ in [data_train, data_dev]:
  for verbWithAff in data_:
    for affix in verbWithAff[1:]:
      itos.add(getRepresentation(affix))
itos = sorted(list(itos))
stoi = dict(list(zip(itos, range(len(itos)))))

itos_ = itos[::]
#shuffle(itos_)
#if args.model == "RANDOM": # Construct a random ordering of the morphemes
weights = dict(list(zip(itos_, [2*x for x in range(len(itos_))])))


#weights = dict(list(zip(itos_, [2*x for x in range(len(itos_))]))) # abstract slot

pairs_count = {}
from collections import defaultdict


marginal_by_slot = {}
marginal_by_slot_sum = defaultdict(int)

def record(x, y):
   if (x["coarse"], y["coarse"]) not in pairs_count:
      pairs_count[(x["coarse"], y["coarse"])] = defaultdict(int)
   pairs_count[(x["coarse"], y["coarse"])][(x["fine"], y["fine"])] += 1

if True:
    # Order the datasets based on the given weights
    train = []
    dev = []
    for data, processed in [(data_train, train), (data_dev, dev)]:
      for verb in data:
         affixes = verb[1:]
         affixes = sorted(affixes, key=lambda x:weights.get(getRepresentation(x), 0))
#         print(affixes)
         for i in range(len(affixes)):
           if affixes[i]["coarse"] not in marginal_by_slot:
              marginal_by_slot[affixes[i]["coarse"]]=defaultdict(int)
           marginal_by_slot[affixes[i]["coarse"]][affixes[i]["fine"]] += 1
           marginal_by_slot_sum[affixes[i]["coarse"]] += 1
           for j in range(i):
             af1 = affixes[i]
             af2 = affixes[j]
             record(af1, af2)


print(pairs_count)

def mean(x):
  return sum(x)/len(x)



with open(f"pmi/{__file__}_{args.language}_{args.POS}", "w") as outFile:
 for x, y in pairs_count:
   counts = pairs_count[(x,y)]
   marginal_counts = defaultdict(int)
   total_count = 0
   for a, b in counts:
     marginal_counts[a] += counts[(a,b)]
     marginal_counts[b] += counts[(a,b)]
     total_count += counts[(a,b)]
   for a, b in counts:
#     print(counts[(a,b)], total_count,  marginal_by_slot[x][a], marginal_by_slot[y][b])
     assert marginal_by_slot[x][a]/marginal_by_slot_sum[x] <= 1
     assert marginal_by_slot[y][b]/marginal_by_slot_sum[y] <= 1
     pmi = log(counts[(a,b)]/total_count) - log(marginal_by_slot[x][a]/marginal_by_slot_sum[x]) - log(marginal_by_slot[y][b]/marginal_by_slot_sum[y])
#     pmi = log(counts[(a,b)]) - log(marginal_counts[a]) - log(marginal_counts[b]) + log(total_count)
     print("\t".join([str(q) for q in [a, b, counts[(a,b)], pmi]]), file=outFile)

