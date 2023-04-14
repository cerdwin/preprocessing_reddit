import nltk
from nltk.tokenize import sent_tokenize
import sys

keywords = ["flation",  "nterest rate", "nternational coop", "limate chang", "overnment", "kraine", "anking syst"]

def extract_sentences(file_name):
    with open(file_name, 'r') as f:
        text = f.read()

    # Splitting the text into blocks separated by newlines
    blocks = text.split("\n")
    sentences = []
    # Initialise test sentences
    test_sentences = []
    counter = 0
    for block in blocks:
        # check for keywords
        #if "flation" not in block and "employment" not in block and "interest rate" not in block:
        #    continue
        counter += 1
        if counter % 100 > 97:
            # Spliting the block into sentences
            sents = sent_tokenize(block)

            # Looping through each sentence
            for sent in sents:
                present = False
                for i in keywords:
                    if i in sent:
                        present = True
                        break
                if not present:
                    continue
                test_sentences.append(sent + ' <|eos|> ')
        else:
            sents = sent_tokenize(block)
            for sent in sents:
                present = False
                for i in keywords:
                    if i in sent:
                        present = True
                        break
                if not present:
                    continue
                sentences.append(sent + ' <|eos|> ')

    # Writing the resulting sentences
    with open("revised_" + file_name.split('.txt')[0] + "_train.txt", 'w') as f:
        for sentence in sentences:
            f.write(sentence + "\n")
    with open("revised_" + file_name.split('.txt')[0] + "_test.txt", 'w') as f:
        for sentence in test_sentences:
            f.write(sentence + "\n")


file_name = sys.argv[1]
extract_sentences(file_name)
