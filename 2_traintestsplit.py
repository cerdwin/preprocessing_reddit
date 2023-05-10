#!/usr/bin/env python

import nltk
from nltk.tokenize import sent_tokenize
import sys
from tqdm import tqdm

def extract_sentences(file_name):
    with open(file_name, 'r') as f:
        text = f.read()

    # Splitting the text into blocks separated by newlines
    blocks = text.split("\n")
    sentences = []
    # Initialise test sentences
    test_sentences = []
    counter = 0
    for block in tqdm(blocks, desc="Processing blocks"):
        counter += 1
        sents = sent_tokenize(block)
        if counter % 100 > 97:
            for sent in sents:
                test_sentences.append(sent)
            test_sentences.append('\n') # adding newline to delineate where does a comment end
        else:
            for sent in sents:    
                sentences.append(sent)
            sentences.append('\n')

    # Writing the resulting sentences
    with open(file_name.split('.txt')[0] + "_train.txt", 'w') as f:
        for sentence in sentences:
            f.write(sentence + "\n")
    with open(file_name.split('.txt')[0] + "_test.txt", 'w') as f:
        for sentence in test_sentences:
            f.write(sentence + "\n")


file_name = sys.argv[1]
extract_sentences(file_name)
