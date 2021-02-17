with open("/u/scr/mhahn/UNIMORPH/lat/lat", "r") as inFile:
  data = [x.split("\t") for x in  inFile.read().strip().split("\n") if len(x) > 3]

from scipy.optimize import linprog


data = [x for x in data if "ADJ" in x[2] and "VOC" not in x[2]]

data_ = []

for x in data:
   lemma, form, labels = x
   form_chars = list(form) + ["EOS"]
#   print(form_chars)
   for i in range(len(form_chars)):
       data_.append((labels.split(";") + [lemma] + form_chars[:i], form_chars[i]))
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

def variance(x):
   if len(x) == 0:
     return 0
   onehots = torch.zeros(len(x), len(itos_outputs))-1
   for i in range(len(x)):
     onehots[i,x[i]] = 1
   return float((onehots.pow(2).mean(dim=0) - onehots.mean(dim=0).pow(2)).sum())
#   return sum([y**2 for y in x])/len(x) - (sum(x)/len(x))**2




def getMaxOverPartitions(A, b, x_bounds, perSubsetSensitivities):
   #print(perSubsetSensitivities)
   c = [-x for x in perSubsetSensitivities]
   res = linprog(c, A_ub=A, b_ub=b, bounds=x_bounds)
   # find the highly sensitive partition
   return -res.fun, res.x


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
     for i2 in inputsAtLength[len(form)]:
         form2 = inputs[i2]
         if i == i2: #form == form2:
           continue
         if True: #len(form) == len(form2):
           if s[0] == "0" and form[0] != form2[0]:
             continue
           matches = True
           for j in range(len(s)):
             if s[j] == "0" and form[j] != form2[j]:
               matches = False
               break
           if matches:
#             print(i2, form, form2, outputs[i2], case)
             relevantFeatureSets.append(outputs[i2])
             if len(formsForSubset[-1]) < 20:
                formsForSubset[-1].append((form2, outputs[i2]))
             #print(form, s, form2)
  #   print(relevantFeatureSets)
#     cases = [[x for x in y if x in case_set] for y in relevantFeatureSets]
#     print(cases)
     f = [stoi_outputs[x] for x in relevantFeatureSets] + [stoi_outputs[label]]
#     print(f)
     varianceBySubset.append(variance(f))
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
  print("-----")
  print(i, form, "Sensitivity", sensitivity)
#  print(assignment)
  if True: #False:
   for i in range(len(subsets)):
     if assignment[i] > 1e-5 and varianceBySubset[i] > 1e-5:
        print(subsets[i], assignment[i], varianceBySubset[i], formsForSubset[i])
#  if i > -1:
 #    break
   

