import torch
import math
import random
with open("output/collect.py.txt", "r") as inFile:
  data = [[y.strip() for y in x.split("\t")] for x in  inFile.read().strip().split("\n") if (not (x.startswith("<")))]

from scipy.optimize import linprog

itos = []
itos_set = set()
stoi = {}
def toOneHot(x):
  if x not in itos_set:
    itos.append(x)
    itos_set.add(x)
    stoi[x] = len(itos)-1
  r = [0 for _ in range(40)]
  r[stoi[x]] = 1
  return r
data_ = []

sumProbabilities = 0
for lemma, form, probability in data:
   probability = int(probability)
   if probability < 1000:
     continue
   sumProbabilities += probability
   form_chars = list(form) + ["EOS"]
#   print(form_chars)
   for i in range(len(form_chars)):
#       data_.append(([lemma] + form_chars[:i], form_chars[i], probability))
       data_.append((list(lemma) + ["#"] + form_chars[:i], form_chars[i], probability))
random.shuffle(data_)
inputs = [x for x, _, _ in data_]
outputs = [y for _, y, _ in data_]
probabilities = torch.FloatTensor([z/sumProbabilities * len(data_) for _, _, z in data_]) #* len(data_)
#random.shuffle(probabilities)
for i in [7]: #range((100)):
  relevant =([j for j, x in enumerate(inputs) if len(x) == i])
  if len(relevant) > 1:
     similarity = torch.zeros(len(relevant), len(relevant))
     for j in range(len(relevant)):
       for k in range(j):
         similarity[j][k] = len([q for q in range(len(inputs[relevant[j]])) if inputs[relevant[j]][q] != inputs[relevant[k]][q]])
#         if int(similarity[j][k]) == 0:
#           print(inputs[relevant[j]], inputs[relevant[k]])
     print(i, len(relevant), similarity)
     similarity = similarity + similarity.t()
     probabilitiesHere = probabilities[torch.LongTensor(relevant)]
     probabilitiesHere = probabilitiesHere / probabilitiesHere.sum()
     transitionMatrix = (-0.5*similarity).exp()
     transitionMatrix = transitionMatrix / transitionMatrix.sum(dim=1).unsqueeze(1)


     function = torch.FloatTensor([toOneHot(outputs[j]) for j in relevant])
     approximator = torch.FloatTensor([toOneHot(outputs[j]) for j in relevant]) #torch.zeros(len(relevant), function.size()[1])
     approximator.requires_grad = True
     optim = torch.optim.SGD([approximator], lr=0.2)
     for itera in range(50000):
       optim.zero_grad()
       sensitivity = (probabilitiesHere.unsqueeze(1) * (torch.matmul(transitionMatrix, approximator) - approximator).pow(2)).sum()
       error = (probabilitiesHere.unsqueeze(1) * (function - approximator).pow(2)).sum()
       loss = error + 3 * sensitivity
       loss.backward()
       optim.step()
       print(i, itera, error, sensitivity, loss)
     for y, j in enumerate(relevant):
       predicted = int(approximator[y,:len(itos)].argmax())
       print(i, float(probabilitiesHere[y]), "\t", inputs[j], "\t", itos[predicted] if predicted < len(itos) else "OUT", "\t", outputs[j])

#     quit()    
     continue

     print(transitionMatrix)
     morphism = transitionMatrix + probabilitiesHere.unsqueeze(0) / probabilitiesHere.unsqueeze(1) * transitionMatrix.t()

     

     laplacian = torch.diag(torch.zeros(len(relevant))+1) - morphism
     print(laplacian)
     approximationOperator = torch.inverse(torch.diag(torch.zeros(len(relevant))+1) + 0.1 * laplacian)
     print(approximationOperator)
     function = torch.FloatTensor([toOneHot(outputs[j]) for j in relevant])
 #    print(approximationOperator.size(), function.size())
     approximated = torch.matmul(approximationOperator, function)
#     print(approximated)
     for y, j in enumerate(relevant):
       predicted = int(approximated[y,:len(itos)].argmax())
       print(float(probabilitiesHere[y]), "\t", inputs[j], itos[predicted] if predicted < len(itos) else "OUT")
     quit()
     # now construct the smoothing matrix
#     quit()

