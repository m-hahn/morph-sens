with open("/u/scr/mhahn/UNIMORPH/lat/lat", "r") as inFile:
  data = [x.split("\t") for x in  inFile.read().strip().split("\n") if len(x) > 3]

from scipy.optimize import linprog
import math

data = [x for x in data if "ADJ" in x[2] and "VOC" not in x[2]]

import random

lemmas, forms, labels = zip(*data)
forms = list(forms)

print("Shuffling forms")
random.shuffle(forms)

data = list(zip(lemmas, forms, labels))


data_ = []

for x in data:
   lemma, form, labels = x
   form_chars = (list(form) + ["EOS"])
#   print(form_chars)
   for i in range(len(form_chars)):
       data_.append((labels.split(";") + [lemma] + form_chars[:i], form_chars[i]))


random.Random(5).shuffle(data_)

inputs = [x for x, _ in data_]
outputs = [y for _, y in data_]


from collections import defaultdict
inputsAtLength = defaultdict(list)
for i in range(len(inputs)):
   inputsAtLength[len(inputs[i])].append(i)

itos_outputs = sorted(list(set(outputs)))
stoi_outputs = dict(list(zip(itos_outputs, range(len(itos_outputs)))))

import random
print(outputs[:5])

# - real
# - totally shuffled
# - shuffled within lemmas

#random.shuffle(outputs)
print(outputs[:5])
#quit()

import torch

def variance(x, target):
   counts = defaultdict(int)
   for y in x:
     counts[y]+=1
   variance = 0
 #  print(x, counts)
   for y in counts:
      positive = counts[y]/len(x)
      negative = 1 - positive
      mean = positive - negative
#      print(y, target, mean)
      if target == y:
        variance += math.pow(1-mean,2)
      else:
        variance += math.pow(-1-mean,2)
   return variance
#   print(x)
#   quit()
#   if len(x) == 0:
#     return 0
#   onehots = torch.zeros(len(x), len(itos_outputs))-1
#   for i in range(len(x)):
#     onehots[i,x[i]] = 1
#   return float((onehots.pow(2).mean(dim=0) - onehots.mean(dim=0).pow(2)).sum())
#   return sum([y**2 for y in x])/len(x) - (sum(x)/len(x))**2




#def getMaxOverPartitions(A, b, x_bounds, perSubsetSensitivities):
#   #print(perSubsetSensitivities)
#   c = [-x for x in perSubsetSensitivities]
#   res = linprog(c, A_ub=A, b_ub=b, bounds=x_bounds)
#   # find the highly sensitive partition
#   return -res.fun, res.x
#
def getMaxOverPartitions(perSubsetSensitivities, sensitivityObtainedSoFar, partitionSoFar, lastAdded, N=9):
#   print("{0:b}".format(2**N-1), "{0:b}".format(partitionSoFar), "{0:b}".format(2**N-1 & (~ partitionSoFar)), 2**N-1 & (~ partitionSoFar), lastAdded)
#   print("{0:b}".format(partitionSoFar), "{0:b}".format(2**N-1), partitionSoFar == 2**N-1)
   if partitionSoFar == 2**N-1:
      return sensitivityObtainedSoFar, []
   if (2**N-1) & (~ partitionSoFar) < lastAdded:
      return 0, []

   sens = 0
   bestSelectionHere = []
   for jInd in range(lastAdded+1, len(perSubsetSensitivities)):
      # check whether j is in the complement of partitionSoFar
#      if perSubsetSensitivities[j] == 0:
 #         continue
#      print("{0:b}".format(j), "{0:b}".format(partitionSoFar), "{0:b}".format((~j | ~partitionSoFar)))
      j = perSubsetSensitivities[jInd][0]
      if ~j | ~partitionSoFar == -1:

          here, selection = getMaxOverPartitions(perSubsetSensitivities, sensitivityObtainedSoFar+perSubsetSensitivities[jInd][1], partitionSoFar | j, jInd, N=N)
          if here > sens:
              sens=here
              bestSelectionHere = [jInd] + selection
   return sens, bestSelectionHere


perMasked = defaultdict(list)

for i in range(len(data)):
 # print(i)
  form = inputs[i]
  label = outputs[i]
#  print(label)
  subsets = set()
  for s in range(len(form)+1):
     for t in range(s):
        subsets.add(("0"*t) + ("1"*(s-t)) + ("0"*(len(form)-s)))
#  print(subsets)
  subsets = list(subsets)
  varianceBySubset = []
  formsForSubset = []
  if i % 10 == 0:
     print(i/len(data))
  for s in subsets:
     formsForSubset.append([])
 #    print(s, form)
     relevantFeatureSets = []
     relevantForm = tuple([form[j] if s[j] == "0" else "#"  for j in range(len(form))])
     perMasked[relevantForm].append(label)

sensitivitiesSum = 0

for i in range(len(data)):
 # print(i)
  form = inputs[i]
  label = outputs[i]
#  print(label)
  subsets = set()
  for s in range(len(form)+1):
     for t in range(s):
        subsets.add(("0"*t) + ("1"*(s-t)) + ("0"*(len(form)-s)))
#  print(subsets)
  subsets = list(subsets)
  varianceBySubset = []
  formsForSubset = []
  for s in subsets:
     formsForSubset.append([])
 #    print(s, form)
     relevantFeatureSets = []
     relevantForm = tuple([form[j] if s[j] == "0" else "#"  for j in range(len(form))])
     f = [stoi_outputs[x] for x in perMasked[relevantForm]]
     varianceBySubset.append(variance(f, stoi_outputs[label]))
 #    quit()
  #print(varianceBySubset)


  subsetsEnumeration = subsets
  if len(subsetsEnumeration) == 0:
    continue
  N = len(subsetsEnumeration[0])
  A = [[0 for subset in range(len(subsetsEnumeration))] for inp in range(N)]
  for inp in range(N):
      for subset, bitstr in enumerate(subsetsEnumeration):
         assert len(bitstr) == N
         if bitstr[inp] == "1":
             A[inp][subset] = 1


  b = [1 for _ in range(N)]
  x_bounds = [(0,1) for _ in range(len(subsetsEnumeration))]
  perSubsetSensitivities = [(int(subsetsEnumeration[x], 2), varianceBySubset[x]+0.001*len([y for y in subsets[x] if y == "0"])) for x in range(len(subsetsEnumeration))]
 # print(i)
  sensitivity, assignment = getMaxOverPartitions(perSubsetSensitivities, 0, 0, 0, N= len(subsetsEnumeration[0]))
  sensitivitiesSum += sensitivity
  print("-----")
  print(i, form, "Sensitivity", sensitivity, sensitivitiesSum/(i+1))
#  print(assignment)
#  if True: #False:
 #  for i in range(len(subsets)):
  #   if assignment[i] > 1e-5 and varianceBySubset[i] > 1e-5:
   #     print(subsets[i], assignment[i], varianceBySubset[i], formsForSubset[i])
#  if i > -1:
 #    break
   

