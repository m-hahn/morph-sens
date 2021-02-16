with open("/u/scr/mhahn/UNIMORPH/lat/lat", "r") as inFile:
  data = [x.split("\t") for x in  inFile.read().strip().split("\n") if len(x) > 3]

from scipy.optimize import linprog


data = [x for x in data if "ADJ" in x[2]]

forms = [x[1] for x in data]
labels = [[z.strip() for z in x[2].split(";")] for x in data]
import random
#random.shuffle(labels)

case_set = set(["NOM", "GEN", "DAT", "ACC", "VOC"])
number_set = set(["SG", "PL"])

from cpython cimport array

case_labels_ = [[z for z in x if z in case_set] for z in labels]
case_labels_ = [x[0] if len(x)>0 else "NONE" for x in case_labels_]
itos_case = sorted(list(set(case_labels_)))
stoi_case = dict(list(zip(itos_case, range(len(itos_case)))))
cdef array.array case_labels = array.array('i', [stoi_case[x] for x in case_labels_])


def variance(x):
   if len(x) == 0:
     return 0
   return sum([y**2 for y in x])/len(x) - (sum(x)/len(x))**2




def getMaxOverPartitions(A, b, x_bounds, perSubsetSensitivities):
   #print(perSubsetSensitivities)
   c = [-x for x in perSubsetSensitivities]
   res = linprog(c, A_ub=A, b_ub=b, bounds=x_bounds)
   # find the highly sensitive partition
   return -res.fun, res.x

cdef str form
cdef int label

for i in range(len(data)):
  form = forms[i]
  label = case_labels[i]
  subsets = set()
  for s in range(len(form)):
     for t in range(s):
        subsets.add(("0"*t) + ("1"*(s-t)) + ("0"*(len(form)-s)))
#  print(subsets)
  subsets = list(subsets)
  varianceBySubset = []
  case = label
  for s in subsets:
 #    print(s, form)
     relevantFeatureSets = []
     for i2 in range(len(forms)):
         form2 = forms[i2]
         if form2 == form:
          continue
         if len(form) == len(form2):
           matches = True
           for j in range(len(s)):
             if s[j] == "0" and form[j] != form2[j]:
               matches = False
           if matches:
             relevantFeatureSets.append(case_labels[i2])
#             print(form, s, form2, case, case_labels[i2])
  #   print(relevantFeatureSets)
#     cases = [[x for x in y if x in case_set] for y in relevantFeatureSets]
#     print(cases)
     f = [1 if case == x else -1 for x in relevantFeatureSets]
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

  sensitivity, assignment = getMaxOverPartitions(A, b, x_bounds, perSubsetSensitivities)
  print(i, form, sensitivity)
#  print(assignment)
#  for i in range(len(subsets)):
#     if assignment[i] > 1e-5 and varianceBySubset[i] > 1e-5:
#        print(subsets[i], assignment[i], varianceBySubset[i])
#  if i > -1:
 #    break
   

