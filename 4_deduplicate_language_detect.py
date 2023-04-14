from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
import re
import tqdm
import sys

blocks = []
filename = sys.argv[1]
block_size = 512
with open(filename, 'r') as f:
    # Load the text, remove possible newlines and eos tags
    text = f.read().replace("\n", "").split('<|eos|>')
    # Deduplicating every sentence 
    text = list(dict.fromkeys(text).keys())
    if len(text[0])==0: text = text[1:]
    
    block = '<|eos|>'+ text[0]
    for sentence in tqdm(range(1, len(text) - 1), desc="Processing sentences"):
      try:
        # Detecting that each sentence is English
        if detect(text[sentence]) == "en":
          if len(block)+len('<|eos|> ') + len(text[sentence])>block_size-len('<|eos|> '):
            block+=' <|eos|>'
            blocks.append(block)
            block = '<|eos|>'+ text[sentence]
          else:
            block = block + '<|eos|>'+ text[sentence]
      except LangDetectException:
        pass
      
    if block[-1] != '>':
      block= block + '<|eos|>'+ text[-1]

    concatenated_blocks = '\n'.join(blocks)
    concatenated_blocks = re.sub(r' +', ' ', concatenated_blocks)
    with open('out.txt', 'w') as outfile:
      outfile.write(concatenated_blocks)

    with open("deduplicated_" + filename, "w") as file:
        file.write(concatenated_blocks)

    print(f"Deduplicated file written to 'deduplicated_{filename}'.")
