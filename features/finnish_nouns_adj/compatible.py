#with open("slotNames.txt", "r") as inFile:
#  universal = {x[0] : x[1] for x in [y.split("\t") for y in inFile.read().strip().split("\n")]}

def flatten(x):
   r = []
   for y in x:
     for z in y:
       r.append(z)
   return r
import random

def sampleCompatibleOrdering(itos_):
   print(itos_)
   universalOrder = ["Derivation", "Number", "Case"]
   elements = [[x for x in itos_ if x == y] for y in universalOrder]
   for x in elements:
     random.shuffle(x)
   print("ASSIGNED", elements)
   elements = flatten(elements)
   print("NOT ASSIGNED", [x for x in itos_ if x not in elements])
   for x in itos_:
     if x not in elements:
        position = random.randint(0, len(elements)+1)
        elements = elements[:position] + [x] + elements[position:]
   print(elements)
   assert len(elements) == len(itos_)
   return {x : 2*elements.index(x) for x in elements}

