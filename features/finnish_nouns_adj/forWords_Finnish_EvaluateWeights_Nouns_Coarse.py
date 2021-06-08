# based on yWithMorphologySequentialStreamDropoutDev_Ngrams_Log.py

import random
import sys
from corpus import CORPUS
from estimateTradeoffHeldout import calculateMemorySurprisalTradeoff
from math import log, exp
from corpusIterator_V import CorpusIterator_V
from random import shuffle, randint, Random, choice



objectiveName = "LM"

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--language", dest="language", type=str, default=CORPUS)
parser.add_argument("--model", dest="model", type=str)
parser.add_argument("--idForProcess", dest="idForProcess", type=int, default=random.randint(0,10000000))
import random



args=parser.parse_args()
print(args)






myID = args.idForProcess



import finnish_noun_segmenter_coarse
import finnish_noun_segmenter
# Translate a verb into an underlying morpheme
def getRepresentation(lemma):
    return lemma["coarse"]

def getSurprisalRepresentation(lemma):
    return lemma["fine"]
def processVerb(verb, data_):
    # assumption that each verb is a single word
   for vb in verb:
      labels = vb["morph"]
      morphs = finnish_noun_segmenter_coarse.get_abstract_morphemes(labels)
      fine = finnish_noun_segmenter.get_abstract_morphemes(labels)
      morphs[0] = vb["lemma"] # replace "ROOT" with actual root
      fine[0] = vb["lemma"] # replace "ROOT" w actual root
      lst_dict = []
      for i in range(len(fine)):
        morph_dict = {"fine": fine[i], "coarse": morphs[i]}
        lst_dict.append(morph_dict)
      data_.append(lst_dict)

# Load both training (for fitting n-gram model) and held-out dev (for evaluating cross-entropy) data
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
       if line["posUni"] == "NOUN" or line["posUni"] == "ADJ":
          verb.append(line)
          processVerb(verb, data_)
          verb = []

words = []


affixFrequencies = {}
for verbWithAff in data_train:
  for affix in verbWithAff[1:]:
    affix = getRepresentation(affix)
    affixFrequencies[affix] = affixFrequencies.get(affix, 0)+1


itos = set()
for data_ in [data_train, data_dev]:
  for verbWithAff in data_:
    for affix in verbWithAff[1:]:
      itos.add(getRepresentation(affix))
itos = sorted(list(itos))
stoi = dict(list(zip(itos, range(len(itos)))))

itos_ = itos[::]
shuffle(itos_)
if args.model == "RANDOM": # Construct a random ordering of the morphemes
  weights = dict(list(zip(itos_, [2*x for x in range(len(itos_))])))
elif args.model == "UNIV":
  import compatible
  weights = compatible.sampleCompatibleOrdering(itos_)
  print(weights)
else:
  weights = {}
  weights = {}
  files = args.model
  with open(files, "r") as inFile:
     next(inFile)
     for line in inFile:
        if "extract" in files:
           morpheme, weight, _ = line.strip().split("\t")
        else:
           morpheme, weight = line.strip().split(" ")
        weights[morpheme] = int(weight)

from collections import defaultdict

errors = defaultdict(int)

hasSeenType = set()

def getCorrectOrderCount(weights):
   correct = 0
   incorrect = 0
   correctFull = 0
   incorrectFull = 0

   correctTypes = 0
   incorrectTypes = 0
   correctFullTypes = 0
   incorrectFullTypes = 0
   for verb in data_train:
      keyForThisVerb = " ".join([getSurprisalRepresentation(x) for x in verb])
      hasSeenThisVerb = (keyForThisVerb in hasSeenType)
      hasMadeMistake = False
      for i in range(1, len(verb)):
         for j in range(1, i):
             weightI = weights[getRepresentation(verb[i])]
             weightJ = weights[getRepresentation(verb[j])]
             if weightI == weightJ:
                continue
             if weightI > weightJ:
               correct+=1
               if not hasSeenThisVerb:
                 correctTypes += 1
             else:
               incorrect+=1
               if not hasSeenThisVerb:
                 incorrectTypes += 1
               hasMadeMistake = True
#               print("MISTAKE", verb[i]["lemma"], weights[getRepresentation(verb[i]["lemma"])], verb[j], weights[getRepresentation(verb[j]["lemma"])], [x["lemma"] for x in verb])
               errors[(getRepresentation(verb[j]), getRepresentation(verb[i]))] += 1
      if len(verb) > 2:
        if not hasMadeMistake:
            correctFull += 1
            if not hasSeenThisVerb:
              correctFullTypes += 1
        else:
            incorrectFull += 1
            if not hasSeenThisVerb:
              incorrectFullTypes += 1
      if not hasSeenThisVerb:
        hasSeenType.add(keyForThisVerb)
   return correct/(correct+incorrect), correctFull/(correctFull+incorrectFull),correctTypes/(correctTypes+incorrectTypes), correctFullTypes/(correctFullTypes+incorrectFullTypes)

result = getCorrectOrderCount(weights)
print(errors)
print(result)

if args.model.endswith(".tsv"):
   model = args.model[args.model.rfind("_")+1:-4]   
else:
   model = args.model

with open("results/accuracy_"+__file__+"_"+str(myID)+"_"+model+".txt", "w") as outFile:
   print(result[0], file=outFile)
   print(result[1], file=outFile)
   print(result[2], file=outFile)
   print(result[3], file=outFile)
   errors = list(errors.items())
   errors.sort(key=lambda x:x[1], reverse=True)
   for x, y in errors:
      print(x[0], x[1], y, file=outFile)
print("ERRORS")
print(errors)
print(result)

print("results/accuracy_"+__file__+"_"+str(myID)+"_"+args.model+".txt")


