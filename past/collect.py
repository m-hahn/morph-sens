from collections import defaultdict

def save():
   with open(f"output/{__file__}.txt", "w") as outFile:
     for verb in sorted(list(pasts)):
         for past in sorted(list(pasts[verb])):
            if pasts[verb][past] < 5:
                continue
            print(verb, "\t", past, "\t", pasts[verb][past], file=outFile)

pasts = {}

counter = 0
with open("/u/scr/mhahn/FAIR18/english-train-tagged.txt", "r") as inFile:
  for  line in inFile:
      line = line.strip().split("\t")
      if len(line) < 3:
         #print(line)
         continue
      if line[1] == "VBD":
         counter += 1
         line[0] = line[0].lower()
         if line[2] not in pasts:
              pasts[line[2]] = defaultdict(int)
         pasts[line[2]][line[0]] += 1
         if counter % 1000000 == 0:
           print(counter)
           save()
