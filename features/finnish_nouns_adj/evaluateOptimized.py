PYTHON = "/u/nlp/anaconda/main/anaconda3/envs/py37-mhahn/bin/python"

import os
import subprocess
import sys
import glob

optimized = glob.glob("results/*/optim*")

for o in optimized:
  subprocess.call([PYTHON, "forWords_Finnish_EvaluateWeights_Nouns_Coarse.py", "--model="+o])
  subprocess.call([PYTHON, "forWords_Finnish_RandomOrder_Nouns_Coarse_FineSurprisal.py", "--model="+o])

