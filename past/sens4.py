import sys
import math
import random
with open("output/collect.py.txt", "r") as inFile:
  data = [[y.strip() for y in x.split("\t")] for x in  inFile.read().strip().split("\n") if (not (x.startswith("<")))] #[:10]
random.shuffle(data)
from scipy.optimize import linprog

myID = random.randint(0,1000000) 
model = sys.argv[1]
assert model in ["RANDOM", "REAL"]

data_ = []

sumProbabilities = 0
for lemma, form, probability in data:
   probability = int(probability)
   sumProbabilities += probability
   form_chars = list(form) + ["EOS"]
#   print(form_chars)
   for i in range(len(form_chars)):
#       data_.append(([lemma] + form_chars[:i], form_chars[i], probability))
       data_.append((list(lemma) + ["#"] + form_chars[:i], form_chars[i], probability))
data = None
random.shuffle(data_)
inputs = [x for x, _, _ in data_]
outputs = [y for _, y, _ in data_]
probabilities = [z/sumProbabilities * len(data_) for _, _, z in data_] #* len(data_)
if model == "RANDOM":
  random.shuffle(probabilities)
else:
  assert model == "REAL"
for i in range((100)):
  print(i, len([x for x in inputs if len(x) == i]))
#quit()

from collections import defaultdict
inputsAtLength = defaultdict(list)
for i in range(len(inputs)):
   inputsAtLength[len(inputs[i])].append(i)

itos_outputs = sorted(list(set(outputs)))
stoi_outputs = dict(list(zip(itos_outputs, range(len(itos_outputs)))))

print(outputs[:5])

# - real
# - totally shuffled
# - shuffled within lemmas

#random.shuffle(outputs)
print(outputs[:5])
#quit()

import torch

def variance(x, target, targetProb):
   counts = defaultdict(int)
   totalProb = 0
   for y, prob in x:
     counts[y]+=prob
     totalProb+=prob
   variance = 0
   for y in counts:
     mean = counts[y]/totalProb
     if target == y:
        variance += math.pow((1-mean), 2)
     else:
        variance += math.pow(mean, 2)
   return targetProb * variance
#   print(x)
#   quit()
#   if len(x) == 0:
#     return 0
#   onehots = torch.zeros(len(x), len(itos_outputs))-1
#   for i in range(len(x)):
#     onehots[i,x[i]] = 1
#   return float((onehots.pow(2).mean(dim=0) - onehots.mean(dim=0).pow(2)).sum())
#   return sum([y**2 for y in x])/len(x) - (sum(x)/len(x))**2




def getMaxOverPartitions(A, b, x_bounds, perSubsetSensitivities):
   #print(perSubsetSensitivities)
   c = [-x for x in perSubsetSensitivities]
   res = linprog(c, A_ub=A, b_ub=b, bounds=x_bounds)
   # find the highly sensitive partition
   return -res.fun, res.x


perMasked = defaultdict(list)

for i in range(len(inputs)):
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
     print(i/len(inputs))
  for s in subsets:
     formsForSubset.append([])
 #    print(s, form)
     relevantFeatureSets = []
     relevantForm = tuple([form[j] if s[j] == "0" else "#"  for j in range(len(form))])
     perMasked[relevantForm].append((label, probabilities[i]))


averageSensitivity =0
counterSensitivity = 0
for i in range(len(inputs)):
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
     f = [(stoi_outputs[x], y) for x, y in perMasked[relevantForm]]
     
     varianceBySubset.append(variance(f, stoi_outputs[label], probabilities[i]))
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
  perSubsetSensitivities = [varianceBySubset[x]+0.001*len([y for y in subsets[x] if y == "0"]) for x in range(len(subsetsEnumeration))]
 # print(i)
  sensitivity, assignment = getMaxOverPartitions(A, b, x_bounds, perSubsetSensitivities)
  averageSensitivity  +=  float(sensitivity)
  counterSensitivity += 1
  if i % 10 == 0:
    print("-----")
    print(i, form, "Sensitivity", sensitivity, "Average", averageSensitivity/counterSensitivity)
#  print(assignment)
    for i in range(len(subsets)):
     if assignment[i] > 1e-5 and varianceBySubset[i] > 1e-5:
        print(subsets[i], assignment[i], varianceBySubset[i], formsForSubset[i])
#  if i > -1:
 #    break
print(averageSensitivity/counterSensitivity )
with open(f"output/{__file__}_{model}_{myID}", "w") as outFile:
  print(averageSensitivity/counterSensitivity, file=outFile)
