#!/bin/bash

#SBATCH --job-name=split_job
#SBATCH --output=split_%A_%a.out
#SBATCH --error=split_%A_%a.err
#SBATCH --array=0-47
#SBATCH --time=10:00:00
#SBATCH --ntasks=1
#SBATCH --mem=10G

# Variables to easily modify the script
# Directory where the large files are stored
INPUT_DIR="100_mil_words"
FILE_PREFIX="100_mil_fast_cleaned" # Prepend to the file name
TEST_WORDS=250000 # Number of words for the test set

FILES=($INPUT_DIR/${FILE_PREFIX}_*.txt)
file="${FILES[$SLURM_ARRAY_TASK_ID]}"
year_month=$(basename "$file" | cut -d'_' -f 6,7 | cut -d'.' -f 1)
# Create a new directory based on the year and month within the $INPUT_DIR directory - this is where the train.txt and test.txt will be placed
mkdir -p "$INPUT_DIR/$year_month"
shuf "$file" > "${file}.shuffled"
# Create a test set with approximately $TEST_WORDS words
awk '{ print; wordcount += NF; if (wordcount >= '"$TEST_WORDS"') exit }' "${file}.shuffled" > "$INPUT_DIR/${year_month}/test.txt"
awk 'BEGIN {skip_lines = 1} skip_lines { if ((wordcount += NF) > '"$TEST_WORDS"') skip_lines = 0 } !skip_lines' "${file}.shuffled" > "$INPUT_DIR/${year_month}/train.txt"
rm "${file}.shuffled"

echo "Processed $file"
