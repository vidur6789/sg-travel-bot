# coding: utf-8


import numpy as np
import scipy
import pandas as pd
# Download the punkt tokenizer for sentence splitting
import nltk

nltk.download('punkt')
# Load the punkt tokenizer
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')




#Read file
df = pd.read_excel (r'All_fixed.xlsx') #for an earlier version of Excel, you may need to use the file extension of 'xls'




df.index = df['attractions'].str.len()
df = df.sort_index(ascending=False).reset_index(drop=True)




#String Cleaning
wordlist =[]
keywordlist = []
from bs4 import BeautifulSoup
import re
from nltk.corpus import stopwords

def text_to_wordlist(attraction, remove_stopwords=False):
    """Function to convert a  document to a sequence of words, optionally removing stop words. Returns a list of words."""
    attraction_text = attraction
    # 1. Remove Non-letters
    attraction_text = attraction_text.replace(".","").replace("\'","").replace("&", "and").replace("singapore","")
    attraction_text = re.sub('[^a-zA-Z]', ' ', attraction_text)
    # 2. Convert words to lower case and split them
    words = attraction_text.lower().split()
    # 3. Optionally remove stop words
    if remove_stopwords:
        stops = set(stopwords.words('english'))
        words = [word for word in words if not word in stops]
    return words
  
# Define a function ot split a attraction into parsed sentences
def text_to_sentences(attraction, tokenzier, remove_stopwords=False):
    """Function to split a attraction into parsed sentences. Returns
    a lsit of sentences, where each sentence is a list of words"""
    # 1. User the NLTK tokenizer to split the paragraph into sentences
    attraction = attraction.replace(".","").replace("\'","")
    raw_sentences = tokenizer.tokenize(attraction.strip())
    # 2. Loop over each sentence
    sentences = []
    for raw_sentence in raw_sentences:
        #If a sentence is empty, skip it
        if len(raw_sentence) > 0:
            # Otherwise, call text_to_wordlist to get a list of words
            sentences.append(text_to_wordlist(raw_sentence, remove_stopwords))
    # Return the list of sentences (each sentence is a list of words,
    # so this returns a list of lists)
    return sentences  

def tabulatefeatures (sentences):
    #function will get words in sentence and assign a vector based on vocab features
    matrix = []
    global wordlist
    for i in sentences: #sentence level
        #length of matrix is dependent on wordlist
        h = np.zeros((1,len(wordlist)))
        for j in i: #word level
            for k in wordlist: #search thru to find position
                #print (k)
                if k["word"] == j:
                    h[0][(k["position"])] += 1#/k["number"]
        
        matrix.append(h)
    return(matrix)


def Ktabulatefeatures (Ksentences):
    #function will get words in sentence and assign a vector based on vocab features
    matrix = []
    global keywordlist
    for i1 in Ksentences: #sentence level
        #length of matrix is dependent on wordlist
        h1 = np.zeros((1,len(keywordlist)))
        for j1 in i1: #word level
            for k1 in keywordlist: #search thru to find position
                #print (k1)                
                if k1["word"] == j1:
                    h1[0][(k1["position"])] += 1#/k["number"]
        
        matrix.append(h1)
    return(matrix)


def tokenwords (newwords):
    wordlist = []
    position = 0
    #search thru word database to find same words
    for j in newwords:
        addword = 1
        for i in wordlist:
            if i["word"] == j:
                addword = 0
                i["number"] += 1
        if addword == 1:
            wordlist.append({"word" : j, "position" : position, "number" : 1})
            position = position + 1
            

    return wordlist

def ktokenwords (newwords):
    keywordlist = []
    position = 0
    #search thru word database to find same words
    for j in newwords:
        addword = 1
        for i in keywordlist:
            if i["word"] == j:
                addword = 0
                i["number"] += 1
        if addword == 1:
            keywordlist.append({"word" : j, "position" : position, "number" : 1})
            position = position + 1
            

    return keywordlist




wordslist = [] # Initialize an empty list of sentences
keywordslist = []
sentences = []
Ksentences = []

print("Training....")

print('Parsing words from training set')
for attraction in df['attractions']:
    wordslist += text_to_wordlist(attraction)
for keywords in df['keywords']:
    keywordslist += text_to_wordlist(keywords)
print('Parsing sentences from training set')
for attraction in df['attractions']:
    sentences += text_to_sentences(attraction, tokenizer)
for keywords in df['keywords']:
    Ksentences += text_to_sentences(keywords, tokenizer)

wordlist = tokenwords(wordslist)
matrix = tabulatefeatures (sentences)

print ("----------------------------------------------------")

keywordlist = ktokenwords(keywordslist)
kmatrix = Ktabulatefeatures (Ksentences)

fmatrix = [matrix,kmatrix]
    
print ("Training Complete.")




def stringmatching (test):
    listofattractions = []
    test = text_to_sentences(test, tokenizer)
    matrix1 = tabulatefeatures (test)
    matrix2 = Ktabulatefeatures (test)
    suggestions= []
    
    for counter in range(len(fmatrix[0])):
        i = fmatrix[0][counter]
        j = fmatrix[1][counter]
        magnitudei = np.linalg.norm(i)
        magnitudej = np.linalg.norm(j)
        if magnitudei != 0:
            p1 = i - matrix1
            k1 = scipy.spatial.distance.braycurtis(i+p1,matrix1)#*corpuslen/lengthofsentence
            k1 = k1*k1

            if k1 == 0.0:
                suggestions=[[k1,counter]]
                counter+=1
                break
                
            else:
                if k1 < 1:
                    suggestions.append([k1,counter])
                    counter +=1
                elif magnitudej != 0:
                    k2 = scipy.spatial.distance.braycurtis(j,matrix2)#*corpuslen/lengthofsentence
                    k2 = k2*k2
                    k2 += 10
                    if k2 <11:
                        suggestions.append([k2,counter])
                    counter +=1
                
        else:
            counter+=1
    
                
    suggestions.sort()
    for i in suggestions[:5]:
        listofattractions.append(df.attractions[i[1]])
    print(suggestions[:5])
    return listofattractions




#listofattractions = stringmatching("Universal Studio")
#print(listofattractions)

