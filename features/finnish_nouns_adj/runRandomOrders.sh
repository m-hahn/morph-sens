#!/bin/bash
for i in {1..50}
do
    python3 forWords_Finnish_RandomOrder_Nouns_Coarse_FineSurprisal.py --model UNIV
done

for i in {1..50}
do
    python3 forWords_Finnish_RandomOrder_Nouns_Coarse_FineSurprisal.py --model RANDOM
done

python3 forWords_Finnish_RandomOrder_Nouns_Coarse_FineSurprisal.py --model REVERSE
python3 forWords_Finnish_RandomOrder_Nouns_Coarse_FineSurprisal.py --model REAL

