import os
import random
#import accessISWOCData
#import accessTOROTData
import sys

header = ["index", "word", "lemma", "posUni", "posFine", "morph", "head", "dep", "_", "_"]

from paths import UD_PATH

def readUDCorpus(language, partition, ignoreCorporaWithoutWords=True):
      l = language.split("_")
      language = "_".join(l[:-1])
      version = l[-1]
      print(l, language)
      basePaths = [UD_PATH+"/ud-treebanks-v"+version+"/"]
      files = []
      while len(files) == 0:
        if len(basePaths) == 0:
           print("No files found", file=sys.stderr)
           raise IOError
        basePath = basePaths[0]
        del basePaths[0]
        files = os.listdir(basePath)
        files = list(filter(lambda x:x.startswith("UD_"+language.replace("-Adap", "")+"-"), files))
      data = []
      for name in files:
        suffix = name[len("UD_"+language):]
        subDirectory =basePath+"/"+name
        subDirFiles = os.listdir(subDirectory)
        partitionHere = partition
        candidates = list(filter(lambda x:"-ud-"+partitionHere+"." in x and x.endswith(".conllu"), subDirFiles))
        if len(candidates) == 0:
           continue
        if len(candidates) == 2 and name != "UD_German-HDT":
           candidates = list(filter(lambda x:"merged" in x, candidates))
           assert len(candidates) == 1, candidates
        assert len(candidates) >= 1, candidates
        try:
           dataPath = subDirectory+"/"+candidates[0]
           with open(dataPath, "r") as inFile:
              newData = inFile.read().strip().split("\n\n")
              assert len(newData) > 1
              data = data + newData
        except IOError:
           print("Did not find "+dataPath, file=sys.stderr)

      assert len(data) > 0, (language, partition, files)


      print("Read "+str(len(data))+ " sentences from "+str(len(files))+" "+partition+" datasets. "+str(files)+"   "+basePath, file=sys.stderr)
      return data

class CorpusIterator_V():
   def __init__(self, language, partition="train", storeMorph=False, splitLemmas=False, shuffleData=True, shuffleDataSeed=None, splitWords=False, ignoreCorporaWithoutWords=True):
      print("LANGUAGE", language)
      if splitLemmas:
           assert language == "Korean"
      self.splitLemmas = splitLemmas
      self.splitWords = splitWords
      assert self.splitWords == (language == "BKTreebank_Vietnamese")

      self.storeMorph = storeMorph
      data = readUDCorpus(language, partition, ignoreCorporaWithoutWords=ignoreCorporaWithoutWords)
      if shuffleData:
       if shuffleDataSeed is None:
         random.shuffle(data)
       else:
         random.Random(shuffleDataSeed).shuffle(data)

      self.data = data
      self.partition = partition
      self.language = language
      assert len(data) > 0, (language, partition)
   def permute(self):
      random.shuffle(self.data)
   def length(self):
      return len(self.data)
   def processSentence(self, sentence):
        sentence = list(map(lambda x:x.split("\t"), sentence.split("\n")))
        result = []
        for i in range(len(sentence)):
           if sentence[i][0].startswith("#"):
              continue
           if "-" in sentence[i][0]: # if it is NUM-NUM
              continue
           if "." in sentence[i][0]:
              continue
           sentence[i] = dict([(y, sentence[i][x]) for x, y in enumerate(header)])
           sentence[i]["head"] = int(sentence[i]["head"])
           sentence[i]["index"] = int(sentence[i]["index"])
           sentence[i]["word"] = sentence[i]["word"].lower()
           sentence[i]["dep"] = sentence[i]["dep"].lower()
           sentence[i]["coarse_dep"] = sentence[i]["dep"].split(":")[0]
           result.append(sentence[i])
        return result
   def getSentence(self, index):
      result = self.processSentence(self.data[index])
      return result
   def iterator(self, rejectShortSentences = False):
     for sentence in self.data:
        if len(sentence) < 3 and rejectShortSentences:
           continue
        yield self.processSentence(sentence)
