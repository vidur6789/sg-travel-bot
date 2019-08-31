import pandas as pd
import json
import string
from fuzzywuzzy import fuzz
from operator import itemgetter

promotions = ("KlookResults.json") #your path for klook json
with open(promotions, 'r') as f:
    klook = json.load(f)
klook = pd.DataFrame(klook)

# print(klook)

def removestop (sentence):
    sentence = sentence.lower()
    #for j in sentence:
    sentence = sentence.replace(".","").replace("\'","").replace("&", "and").replace("singapore","").replace('™',"").replace('/'," ")
    breakdown = sentence.split()
    stop_punc =  list(string.punctuation)
    stop_list = []
    str1 = ""
    str3 =""
    for i in breakdown:
        #remove punctuation
        token_no_punc = [token for token in i 
                        if token not in stop_punc]
        (str(e) for e in token_no_punc)
        str1 = str1+''.join(token_no_punc) + ' '
        str2 = str1.split()

    #remove stop words
    token_no_stop = [corpus for corpus in str2 
                if corpus not in stop_list]
    (str(e) for e in token_no_stop)
    str3 = str3 +' '.join(token_no_stop)

    return str3

def bruteforcesearch (promo, userinput):
    score = 0
    for i in range(len(promo.split())-(len(userinput.split())-1)):
        a = promo.split()[i:i+len(userinput.split())]
        if a == userinput.split():
            score = +1       
    if score > 0:
        return promo


def promoListGenerator (listofpromo):
    promotionsUnsorted = []
    promotionsSorted = []

    for i in listofpromo:
        if klook.price[i] == "Voucher":
            pass
        else:
            promotionsUnsorted.append( {
            "name" : klook.name[i],
            "oprice" :klook.original_price[i],
            "price" : klook.price[i],
            "savings": round(float(klook.original_price[i])-float(klook.price[i]),2),
            "url" : klook.url[i],
            "img_url" : klook.image_url[i]})
        promotionsSorted = sorted(promotionsUnsorted, key=itemgetter('savings'), reverse = True)

    return promotionsSorted[0:10]



def validatepromo(userinput):
    userinput = userinput.lower()
    score = 0
    bestscore = 0
    bestmatch = ""
    listofpromo = []
    counter = 0
    for z in klook.name:
        p = removestop(z)
        score = fuzz.token_set_ratio(p, userinput)
        if score > 1:
            promo = bruteforcesearch(p, userinput)
            if not promo:
                pass
            else:

                listofpromo.append(counter)
        counter +=1
    listofpromo = promoListGenerator(listofpromo)
    return (listofpromo)




