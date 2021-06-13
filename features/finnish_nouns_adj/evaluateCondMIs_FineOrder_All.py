import glob
import subprocess
for f in glob.glob("results/optimize_finegrained/*"):
  print(f)
  f2 = f[:-4].split("_")
  language = f2[-4]
  version = f2[-3]
  pos = f2[-2]
  model = f2[-1]
  print(language)
  subprocess.call(["/u/nlp/anaconda/main/anaconda3/envs/py37-mhahn/bin/python", "evaluateCondMIs_FineOrder.py", "--language="+language+"_"+version, "--POS="+pos, "--model="+f])
