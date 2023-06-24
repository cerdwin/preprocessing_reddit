import os
import re
import sys
import time
import fasttext
import logging
from tqdm import tqdm

log = logging.getLogger("bot")
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())

input_file = sys.argv[1]
input_filename = os.path.basename(input_file)
output_file = "fasttext_cleaned_" + input_filename
start_time = time.time()

seen_lines = set()
non_english_lines = 0
LANGDETECT = True # Change this to True if you want to enable language detection

# Load FastText language identification model
model = fasttext.load_model('lid.176.bin')

# Calculating the size of the input text
with open(input_file, 'r') as f:
    total_lines = sum(1 for _ in f)

with open(input_file, 'r') as f, open(output_file, 'w') as out_f:
    for line in tqdm(f, total=total_lines, desc="Processing lines"):
        replacements = [
            (r"\[removed\]|\[link\]", ""),
            (r"&gt;|&mdash;|&amp;|&quot;", ""),
            (r"&[#\w]+(?:;\s*|(?=\s))|[#*^_~]|>!|!<", ""),
            (r"\[\s*\]|http\S+|\b\w+\.\w{2,3}(/\S*)?\b|\S+@\S+", ""),
            (r"(_+)(\w+)(_+)", r"\2"),
            (r'\s+', ' ')
        ]
        for pattern, replacement in replacements:
            line = re.sub(pattern, replacement, line)

        line = re.compile("[\U00010000-\U0010ffff]", flags=re.UNICODE).sub(r"", line)

        line = line.strip()
        
        if line and line[-1] not in {'.', '!', '?', ':', ';'}:
            line = line + '.'

        if LANGDETECT:
            try:
                # Check if the line is in English
                predictions = model.predict(line)[0]
                if predictions[0] == '__label__en':
                    if line not in seen_lines:
                        seen_lines.add(line)
                        out_f.write(line + '\n')
                else:
                    non_english_lines += 1
            except Exception as e:
                log.info(f"Can't detect language for the line: {line}. Error: {str(e)}")

        else:
            if line not in seen_lines:
                seen_lines.add(line)
                out_f.write(line + '\n')

        if (len(seen_lines) + 1) % 1000000 == 0:
            log.info(f"Processed {len(seen_lines):,} unique lines.")
            log.info(f"Skipped {non_english_lines} non-English lines.")
            log.info(f"Percentage of non-English lines: {non_english_lines / (len(seen_lines) + non_english_lines):.2%}")

elapsed_time = time.time() - start_time
log.info(f"Processed file saved as {output_file} in {elapsed_time} seconds.")
log.info(f"Total non-English lines: {non_english_lines}")
log.info(f"Percentage of non-English lines: {non_english_lines / (len(seen_lines) + non_english_lines):.2%}")
