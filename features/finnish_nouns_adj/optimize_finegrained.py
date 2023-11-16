# based on yWithMorphologySequentialStreamDropoutDev_Ngrams_Log.py

__file__ = __file__.split("/")[-1]
import random
import sys
from corpus import CORPUS
from estimateTradeoffHeldout import calculateMemorySurprisalTradeoff

objectiveName = "LM"

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--language", dest="language", type=str, default=CORPUS)
parser.add_argument("--POS", dest="POS", type=str, default="NOUN")
parser.add_argument("--model", dest="model", type=str)
parser.add_argument("--alpha", dest="alpha", type=float, default=1.0)
parser.add_argument("--gamma", dest="gamma", type=int, default=1)
parser.add_argument("--delta", dest="delta", type=float, default=1.0)
parser.add_argument("--cutoff", dest="cutoff", type=int, default=4)
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

import finnish_noun_segmenter as finnish_noun_segmenter_coarse
import finnish_noun_segmenter
def processVerb(verb, data_):
    # assumption that each verb is a single word
   for vb in verb:
      labels = vb["morph"]
      if "VerbForm=Part" in labels or "VerbForm=Inf" in labels or "VerbForm=Ger" in labels:
          continue
      if "Gender=Masc" in labels:
          print("Warning", vb)
        # There is an annotation error: 
        # es_ancora-ud-train.conllu:25    admitirán       admitir VERB    _       Gender=Masc|Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin       1       ccomp   _       _
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
      if "Gender" in getRepresentation(affix) and "Spanish-AnCora" in language:
        assert False, verbWithAff
      itos.add(getRepresentation(affix))
itos = sorted(list(itos))
stoi = dict(list(zip(itos, range(len(itos)))))

itos_ = itos[::]
shuffle(itos_)
weights = dict(list(zip(itos_, [2*x for x in range(len(itos_))]))) # abstract slot


def calculateTradeoffForWeights(weights):
    # Order the datasets based on the given weights
    train = []
    dev = []
    for data, processed in [(data_train, train), (data_dev, dev)]:
      for verb in data:
         affixes = verb[1:]
         affixes = sorted(affixes, key=lambda x:weights.get(getRepresentation(x), 0)) 
         for ch in [verb[0]] + affixes:
            processed.append(getSurprisalRepresentation(ch))
         processed.append("EOS")
         for _ in range(args.cutoff+2):
           processed.append("PAD")
         processed.append("SOS")
 #   print(processed[:100])
#    quit()
    auc, devSurprisalTable = calculateMemorySurprisalTradeoff(train, dev, args)
    return auc, devSurprisalTable
   
# This will store the minimal AOC found so far and the corresponding position
mostCorrect, mostCorrectValue = 1e100, None
hasImproved = -1

print(weights)
#quit()
import os
for iteration in range(10000):
  # Randomly select a morpheme whose position to update
  coordinate=choice(itos)

  # Stochastically filter out rare morphemes
  while affixFrequencies.get(coordinate, 0) < 10 and random() < 0.95:
     coordinate = choice(itos)
  if iteration - hasImproved > 500:
     break
  mostCorrectValue = weights[coordinate]
  # Iterate over possible new positions
  for newValue in [-1] + [2*x+1 for x in range(len(itos))]: # + [weights[coordinate]]:

     # Stochastically exclude positions to save compute time (no need to do this when the number of slots is small)
     if random() < 0.8 and newValue != weights[coordinate]:
        continue
     print("Iteration", iteration, "Trying position", newValue, "Best AUC so far", mostCorrect, "Feature", coordinate, "Frequency", affixFrequencies.get(coordinate,0), "last improved", hasImproved)
     # Updated weights, assuming the selected morpheme is moved to the position indicated by `newValue`.
     weights_ = {x : y if x != coordinate else newValue for x, y in weights.items()}

     # Calculate AOC for this updated assignment
     resultingAOC, _ = calculateTradeoffForWeights(weights_)

     # Update variables if AOC is smaller than minimum AOC found so far
     if resultingAOC < mostCorrect:
        mostCorrectValue = newValue
        mostCorrect = resultingAOC
        hasImproved = iteration
  assert mostCorrect < 1e99
  print(iteration, mostCorrect)
  weights[coordinate] = mostCorrectValue
  itos_ = sorted(itos, key=lambda x:weights[x])
  weights = dict(list(zip(itos_, [2*x for x in range(len(itos_))])))
  print(weights)
  for x in itos_:
     if affixFrequencies.get(x,0) < 10:
       continue
     print("\t".join([str(y) for y in [x, weights[x], affixFrequencies.get(x,0)]]))
  if (iteration + 1) % 20 == 0:
     _, surprisals = calculateTradeoffForWeights(weights_)

     if os.path.exists(TARGET_DIR):
       pass
     else:
       os.makedirs(TARGET_DIR)
     with open(TARGET_DIR+"/optimized_"+__file__+"_"+args.language+"_"+args.POS+"_"+str(myID)+".tsv", "w") as outFile:
        print(iteration, mostCorrect, str(args), surprisals, file=outFile)
        for key in itos_:
          print(key, weights[key], file=outFile)
  



