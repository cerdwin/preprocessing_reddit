#!/bin/bash

#SBATCH --job-name=crop_job
#SBATCH --output=word_crop_%A_%a.out
#SBATCH --error=word_crop_%A_%a.err
#SBATCH --array=0-47
#SBATCH --time=05:00:00
#SBATCH --ntasks=1
#SBATCH --mem=1G

# Variables to adjust behaviour - see for yourself whichever makes sense. Also note, this code is adapted for 48 datasets from Reddit in the format RC_year-month.txt
# So adjust both the array flag and other aspects at your discression. 

MAX_WORDS=100250000  # Maximum number of words to include from each file (Here, 250,000 is on top, as it will later be used for the validation file)
FILE_PREFIX="fast_cleaned_"  # Prefix for input files 
FILE_GLOB="${FILE_PREFIX}*.txt"  # Glob pattern to match input files
DEST_DIR="100_mil_words"  # Destination directory
DEST_PREFIX="100_mil_"  # Prefix for output files

mkdir -p "$DEST_DIR"
FILES=($FILE_GLOB)
FILE="${FILES[$SLURM_ARRAY_TASK_ID]}"
OUT_FILE="$DEST_DIR/$DEST_PREFIX${FILE#$FILE_PREFIX}"

# Extract the first MAX_WORDS words from FILE and write them to OUT_FILE
awk -v maxwords="$MAX_WORDS" '
  BEGIN { wordcount=0; }
  { words = NF; wordcount += words; }
  wordcount <= maxwords { print $0; }
  wordcount >= maxwords && words > 1 {
    for (i=1; i<=NF && wordcount - i < maxwords; i++) { printf "%s ", $i; }
    printf "\n";
    exit;
  }
' "$FILE" > "$OUT_FILE"
echo "Processed $FILE"
