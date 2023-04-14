#!/bin/bash
#SBATCH --job-name=
#SBATCH --output=
#SBATCH --cpus-per-task=
#SBATCH --gres=
#SBATCH --mem=256G
#SBATCH --time=110:00:00
#SBATCH --partition=gpu
module purge


wget "https://files.pushshift.io/reddit/comments/RC_2022-01.zst"
python3 1_zst2text.py RC_2020-01.zst
python3	2_traintestsplit.py RC_2020-01.txt
python3	3_cleaning.py RC_2020-01_train.txt
python3	3_cleaning.py RC_2020-01_test.txt
python3	4_deduplicate_language_detect.py cleaned_RC_2022-01_train.txt
python3	4_deduplicate_language_detect.py cleaned_RC_2022-01_test.txt

