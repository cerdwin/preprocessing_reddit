import re
import sys
import time

input_file = sys.argv[1]
output_file = "final_" + input_file
start_time = time.time()
block_size = 512
with open(input_file, 'r') as f:
    sentences = f.read()

# removed
sentences = re.sub(r"\[removed\]", "", sentences)
# links
sentences = re.sub(r"\[link\]", "", sentences)
# html tag
sentences = re.sub(r"&gt;", "", sentences)
# dash
sentences = re.sub(r"&mdash;", "-", sentences)
# ampersand
sentences = re.sub(r"&amp;", "&", sentences)
# quotation marks
sentences = re.sub("&quot;", "\"",sentences)
# remove HTML entities from the example string
sentences = re.sub(r"&[#\w]+(?:;\s*|(?=\s))", "", sentences)
# remove emojis
sentences = re.compile("[\U00010000-\U0010ffff]", flags=re.UNICODE).sub(r"", sentences)
# remove urls
sentences = re.sub(r'http\S+', '', sentences)
sentences = re.sub(r'\b\w+\.\w{2,3}(/\S*)?\b', '', sentences)
#brackets
sentences = re.sub(r'\[\s*\]', '', sentences)
# asterisks and ^
sentences = re.sub(r'[\^*]', '', sentences)
# underscores at the start and end of words
sentences = re.sub(r"(_+)(\w+)(_+)", r"\2", sentences)
# markdown tags
sentences = re.sub(r">!|!<", "", sentences)
# hashes
sentences = re.sub(r"#(?!\d)", "", sentences)
# strikeout
sentences = = re.sub(r"~{2,}", "", sentences)
# sentences without eos
sentences = re.sub(r'([.!?])\s+([A-Z])', r'\1 <|eos|> \2', sentences)
# sentence ending missed by sent tokenizer
sentences = re.sub(r"(?<=\.|\?|\!)(?=[A-Z])", " <|eos|> ", sentences)
# sent tokeniser didn't properly end sentences detected 
sentences = re.sub(r'([a-z]) \<\|eos\|\>', r'\1. <|eos|>', sentences)
# sentences seeping into each other
sentences =  re.sub(r'([0-9a-z?!])([A-Z])', r'\1. <|eos|> \2', sentences)
# originally this included any two capital letters in succession, but were removed for ex. bcs of FTE or UAE...etc.
sentences = re.sub(r"\b([a-z]*)\s?([A-Z][a-z]*)\b", r"\1 \2", sentences)
# emails
sentences = re.sub(r'\S+@\S+', '', sentences)
# remove multiple spaces in succession
sentences = re.sub(r'\s+', ' ', sentences)
# prepare for splitting
sentences = re.sub(r"\<\|eos\|\>", "<|eos|>%%34*34%%", sentences)
my_list = list(sentences.split('%%34*34%%'))
# adding first eos tag
my_list[0] = "<|eos|>"+my_list[0]
# removing trailing eos tag
my_list.pop()
#print(my_list)

# Aggregate the remaining lines into new lines that are separated by one space
# and at most 512 characters long.
aggregated_lines = []
current_line = ''
for line in my_list:
    if len(current_line) + len(line) + 1 <= block_size:
        # Add the line to the current line with a space separator.
        #if current_line:
        #    current_line += ' '
        current_line += line
    else:
        # Start a new line if the current line would be too long.
        aggregated_lines.append(current_line)
        current_line = '<|eos|>'+line

# Add the last line to the list of aggregated lines.
if current_line:
    aggregated_lines.append(current_line)

with open(output_file, 'w') as f:
  for line in aggregated_lines:
    f.write(line + '\n')
elapsed_time = time.time() - start_time
print(f"Processed file saved as {output_file} in {elapsed_time} seconds.")
