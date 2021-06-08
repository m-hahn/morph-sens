import sys
import os

universal_colors = {"Number" : "orange", "Possessor" : None, "Case" : "blue", "Agreement" : "purple", "NA" : None}

script = "forWords_Finnish_OptimizeOrder_Nouns_Coarse_FineSurprisal"
def getName(q):
   return q

with open("output/"+os.listdir("output/")[0], "r") as inFile:
    real = [x.split("\t")[0] for x in inFile.read().strip().split("\n")]
with open(f"results/{script}/"+os.listdir(f"results/{script}/")[0], "r") as inFile:
    optimized = [x.split(" ")[0] for x in inFile.read().strip().split("\n")[1:]]
print(real)
print(optimized)
assert len(real) == len(optimized)
ioptim = dict(list(zip(optimized, range(len(optimized)))))

with open("visualize/comparison.tex", "w") as outFile:
   print("  \\begin{tikzpicture}[%", file=outFile)
   print("% common options for blocks:", file=outFile)
   print("block/.style = {draw, fill=blue!30, align=center, anchor=west,", file=outFile)
   print("            minimum height=0.65cm, inner sep=0},", file=outFile)
   print("% common options for the circles:", file=outFile)
   print("ball/.style = {circle, draw, align=center, anchor=north, inner sep=0}]", file=outFile)
   print("\\node[rectangle,text width=1.7cm,anchor=base] (A0) at (1,-0.3) {Real};", file=outFile)
   print("\\node[rectangle,text width=1.7cm,anchor=base] (B0) at (4,-0.3) {Optimized};", file=outFile)
   for i in range(len(real)):
       color = universal_colors.get(real[i], None)
       print("\\node[rectangle,text width=1.7cm,anchor=base"+(", fill="+color+"!20" if color is not None else "") + "] (A"+str(i+1)+") at (1,"+str(-i/2.0-1)+") {"+getName(real[i])+"};", file=outFile)
   for i in range(len(optimized)):
       color = universal_colors.get(optimized[i], None)
       print("\\node[rectangle,text width=1.7cm,anchor=base"+(", fill="+color+"!20" if color is not None else "") + "] (B"+str(i+1)+") at (4,"+str(-i/2.0-1)+") {"+getName(optimized[i])+"};", file=outFile)
   for i in range(len(optimized)):
       print("\\draw[->] (A"+str(i+1)+".east) to (B"+str(ioptim[real[i]]+1)+".west);", file=outFile)
   print("\end{tikzpicture}", file=outFile)
