#!/bin/bash
#SBATCH --job-name=
#SBATCH --output=
#SBATCH --cpus-per-task=
#SBATCH --gres=
#SBATCH --mem=256G
#SBATCH --time=110:00:00
#SBATCH --partition=gpu

year="2019"

for month in $(seq -w 1 12); do
    file_prefix="RC_${year}-${month}"

    wget "https://files.pushshift.io/reddit/comments/${file_prefix}.zst"
    echo "We are at stage 1: Conversion of a zst file to txt"
    python3 1_zst2text.py ${file_prefix}.zst
    echo "We are at stage 2: Sentence parsing, train test split"
    python3 2_traintestsplit.py ${file_prefix}.txt
    echo "We are at stage 3: Noise filtering"
    python3 3_cleaning.py ${file_prefix}_train.txt
    python3 3_cleaning.py ${file_prefix}_test.txt
    echo "We are at stage 4: Deduplication of sentences and language detection"
    python3 4_deduplicate_language_detect.py cleaned_${file_prefix}_train.txt
    python3 4_deduplicate_language_detect.py cleaned_${file_prefix}_test.txt
done
