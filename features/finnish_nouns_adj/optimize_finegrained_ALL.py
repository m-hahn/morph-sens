import random
import glob
import subprocess

langs = glob.glob("/proj/mhahn.shadow/ud-treebanks-v2.12/*")
langs = list(set([x.split("/")[-1].split("-")[0].replace("UD_", "")+"_2.12" for  x in langs]))

for _ in range(10):
 random.shuffle(langs)
 for lang in langs:
   subprocess.call(["python3", "optimize_finegrained.py", "--language="+lang, "--POS=VERB"])
