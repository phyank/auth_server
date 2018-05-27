from time import sleep

from fingerprint.common import *
from fingerprint.synonyms import *

def get_similarity(rid,account):
    raise TODOException

def get_fingerprint(rid,aritcle_content):
    raise TODOException

def get_recommend0(rid):
    raise TODOException
    #return [{'imgurl':TEST_IMG,'accountname':'no','title':'no title','url':'/','ifcopy':True}]


import jieba.posseg
import pickle
import numpy as np
import lda
import heapq
import random
import math

from sklearn import feature_extraction
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer

from glove import Corpus, Glove
from glove.glove import check_random_state

from scipy.stats import norm

from keras.layers import Input, Dense
from keras.models import Model


from sklearn.ensemble import IsolationForest
from sklearn.utils import check_array

from wordcloud import WordCloud


# get virtual word bag and real word bag
# similar to cut.py
def get_words(str1, id1):
    seg = jieba.posseg.cut(str1)
    punc = open(PUNC_ADDR, 'rb')
    pr = punc.read()
    pr = pr.decode('gbk')
    p = pr.split()
    lreal = []
    lvir = []
    punclist = ["，", ",", "“", "”", "‘", "’", ".", "。", ":", "：", ";", "；", "！",
                "!", "？", "?", "（", "）", "(", ")", '、', '——', '《', '》', '…', "……"]
    passlist = ['\\', "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", '/', '-', '$', '#']
    puncreplace = ["逗号", "逗号", "引号", "引号", "引号", "引号", "句号", "句号", "冒号",
                   "冒号", "分号", "分号", "感叹号", "感叹号", "问号", "问号", "括号",
                   "括号", "括号", "括号", '顿号', '破折号', '书名号', '书名号', '省略号', "省略号"]
    for i in seg:
        if i.word in passlist:
            pass
        elif i.word in punclist:
            for j in range(len(punclist)):
                if i.word == punclist[j]:
                    lvir.append(puncreplace[j])
        elif i.flag in ['n', 'v', 'a'] and i.word not in p:
            lreal.append(i.word)
        elif i.flag not in ['eng'] and i.word in p:
            lvir.append('填充' + i.word)
    strreal = " ".join(lreal)
    strvir = " ".join(lvir)
    punc.close()
    # save the strs
    with open(NEW_ARTICLE_CACHE_DIR+"strreal" + str(id1) + ".txt", 'wb') as savefile:
        pickle.dump(strreal, savefile)
    with open(NEW_ARTICLE_CACHE_DIR+"strvir" + str(id1) + ".txt", 'wb') as savefile:
        pickle.dump(strvir, savefile)
    return strreal, strvir


# fit LDA model
def fitLDA(strvir, id1):
    with open(LDA_MODEL_ADDR, 'rb') as savefile:
        LDAmodel = pickle.load(savefile)
    with open(LDA_ORIGIN_VC_ADDR, 'rb') as savefile:
        originvc = pickle.load(savefile)
    # load the test corpus
    n_weight = np.zeros((1, len(originvc)))  # 1 doc now
    n_corpus = []  # the test corpus
    n_corpus.append(strvir.split())
    lent = 0
    # calculate the rate of existing words
    for i in range(len(n_corpus)):
        lent = 0
        for word in n_corpus[i]:
            for j in range(len(originvc)):
                if word == originvc[j]:
                    n_weight[i][j] += 1
                    lent += 1
                    break
    B = np.asarray(n_weight.astype(np.int32))
    C = LDAmodel.transform(B, max_iter=1000, tol=1e-16)
    C = C[0]
    for i in range(len(C)):
        if not (C[i] >= 0 and C[i] <= 1.5):
            C[i] = 0.01
    with open(NEW_ARTICLE_CACHE_DIR+"LDAvec" + str(id1) + ".txt", 'wb') as savefile:
        pickle.dump(C, savefile)
    return C


# find the top n words in a doc
# topnWords is the $j$th most important word in $i$th doc (tfidf evaluation)
# topTfIdf is the corresponding ifidf
def findTopNWords(word, weight, topn):
    topnWords = []
    topnTfIdf = []
    for i in range(len(weight)):
        tmp1 = []
        tmp2 = []
        # tmp(length:topn) is the sequence of topn words
        tmp = heapq.nlargest(topn, range(len(weight[i])), weight[i].__getitem__)
        for j in range(topn):
            tmp1.append(word[tmp[j]])
            tmp2.append(weight[i][tmp[j]])
        topnWords.append(tmp1)
        topnTfIdf.append(tmp2)
    return topnWords, topnTfIdf


# use the softmax of tfidf as weight
# sum the vector of top words generated by GloVe
# wvec is the topword list
# ivec is the topword tfidf
def getDociVec(glomodel, wvec, ivec):
    softivec = softmax(ivec)
    wordembed = []
    for i in range(len(wvec)):
        try:
            word_idx = glomodel.dictionary[wvec[i]]  # the index of word
            embed = glomodel.word_vectors[word_idx]  # the embed of word
            wordembed.append(embed)
        except:
            wordembed.append(len(glomodel.word_vectors[0]) * [0])
    docvec = len(wordembed[0]) * [0]
    for i in range(len(wvec)):
        for j in range(len(wordembed[i])):
            docvec[j] += softivec[i] * wordembed[i][j]
    return docvec


# Compute the softmax of vector x
def softmax(x):
    exp_x = np.exp(x)
    softmax_x = exp_x / np.sum(exp_x)
    return list(softmax_x)


# fit GloVe_Tfidf model
def fitGloVe(strreal, id1):
    testcorpus = []
    testcorpus.append(strreal)
    glomodel = Glove.load(GLOVE_SAVE_ADDR)
    with open(TFIDF_VECTO_ADDR, 'rb') as savefile:
        vectorizer = pickle.load(savefile)
    with open(IFIDF_TRANSF_ADDR, 'rb') as savefile:
        transformer = pickle.load(savefile)
    tfidf = transformer.transform(vectorizer.transform(testcorpus))
    word = vectorizer.get_feature_names()  # all key words
    weight = tfidf.toarray()  # corresponding word weight
    topn = 40  # number of real words for pile
    testtopwords, testtopindex = findTopNWords(word, weight, topn)
    docvecs = []
    for i in range(len(testcorpus)):
        docvecs.append(getDociVec(glomodel, testtopwords[i], testtopindex[i]))
    docvec = docvecs[0]
    with open(NEW_ARTICLE_CACHE_DIR+"GloVevec" + str(id1) + ".txt", 'wb') as savefile:
        pickle.dump(docvec, savefile)

    return docvec


def normalize(vec):
    minimum = 100
    maximum = -100
    for item in vec:
        if item < minimum:
            minimum = item
        if item > maximum:
            maximum = item
    for i in range(len(vec)):
        vec[i] = 0.01 + 0.99 * (vec[i] - minimum) / (maximum - minimum)
    # print(vec)
    return


def fitVAE(glovevec, ldavec, symvec, id1):
    original_dim = len(glovevec) + len(ldavec) + len(symvec)
    intermediate_dim = 80
    latent_dim = 20
    x = Input(shape=(original_dim,))
    h = Dense(intermediate_dim, activation='relu', name="midh")(x)
    z_mean = Dense(latent_dim)(h)
    encoder = Model(x, z_mean)
    encoder.load_weights(ENCODER_MODEL_ADDR)
    inputVec = []
    inputVec.append([])
    normalize(glovevec)
    normalize(ldavec)
    normalize(symvec)
    for item in glovevec:
        inputVec[0].append(item)
    for item in ldavec:
        inputVec[0].append(item)
    for item in symvec:
        inputVec[0].append(item)
    # inputVec is the combination of three kinds of information
    inputVec = np.array(inputVec)
    # print(inputVec)
    inputVec_encoded = encoder.predict(inputVec)
    inputVec_encoded = inputVec_encoded[0]
    # print(inputVec_encoded)
    with open(NEW_ARTICLE_CACHE_DIR+"altoVec" + str(id1) + ".txt", 'wb') as savefile:
        pickle.dump(inputVec_encoded, savefile)
    return inputVec_encoded


# def get_fingerprint_slice(strreal, id1):
#     assert type(strreal) == type('0')
#     return [(random.random()) for i in range(0, 30)]


def getOtherArticles(accountid):
    with open(VECTOR_DATABASE_ADDR, 'rb') as savefile:
        vectordatabase = pickle.load(savefile)
    keys = list(vectordatabase.keys())
    if accountid not in keys:
        return False
    feedback = []
    for i in range(len(vectordatabase[accountid])):
        feedback.append(vectordatabase[accountid][i][3])
    return feedback


def getPercentage(corpusAccount, altovec):
    rng = np.random.RandomState(42)
    # fit the model
    clf = IsolationForest(max_samples=100, random_state=rng)
    clf.fit(corpusAccount)

    testData = []
    testData.append(altovec)
    testData = np.array(testData)
    # calculate score and percentage
    test_mid = check_array(testData, accept_sparse='csr')
    scores = clf.decision_function(test_mid)
    percentage = 1 / (1 + np.exp((-25) * (scores - clf.threshold_)))

    return percentage[0]


def Mdistance(vec1, vec2):
    summ = 0
    # vec1A = 0
    # vec2A = 0
    for i in range(len(vec1)):
        # vec1A += vec1[i]*vec1[i]
        # vec2A += vec2[i]*vec2[i]
        summ += abs(vec1[i] - vec2[i])
    # return summ/(math.sqrt(vec1A)*math.sqrt(vec2A))
    return summ


def get_recommend(altovec, topn=20):
    with open(VECTOR_DATABASE_ADDR, 'rb') as savefile:
        vectordatabase = pickle.load(savefile)
    keys = list(vectordatabase.keys())
    feedback = []
    seq = 0
    for entry in keys:
        for i in range(len(vectordatabase[entry])):
            if len(feedback) < topn:
                tmp = [vectordatabase[entry][i][0], vectordatabase[entry][i][1],
                       vectordatabase[entry][i][2], vectordatabase[entry][i][3], entry]
                feedback.append(tmp)
            elif Mdistance(vectordatabase[entry][i][3], altovec) \
                    < Mdistance(feedback[len(feedback) - 1][3], altovec):
                tmp = [vectordatabase[entry][i][0], vectordatabase[entry][i][1],
                       vectordatabase[entry][i][2], vectordatabase[entry][i][3], entry]
                feedback[-1] = tmp
            for j in range(len(feedback) - 1, 0, -1):
                # print(feedback[j][3])
                if Mdistance(feedback[j][3], altovec) < Mdistance(feedback[j - 1][3], altovec):
                    tmp = feedback[j]
                    feedback[j] = feedback[j - 1]
                    feedback[j - 1] = tmp
    threhold = 1
    for i in range(len(feedback)):
        if Mdistance(feedback[i][3], altovec) < threhold:
            feedback[i].append(True)
        else:
            feedback[i].append(False)
    # feedback:[num,title,url,vector,account,copyTag]
    result=[]
    for article in feedback:
        result.append({'id':article[0],'imgurl':TEST_IMG,'accountname':article[4],'title':article[1],'url':article[2],'ifcopy':article[5]})
    return result


def get_fingerprint_vectors(rid,str1):
    # str1 is the content
    id1 = 0  # not used
    # cut the word, store mid result
    strreal, strvir = get_words(str1, id1)

    # fit stop-word LDA model, store LDA result
    ldavec = fitLDA(strvir, id1)

    # fit the Glove-Tfidf model
    glovevec = fitGloVe(strreal, id1)

    # fit synonym forest model
    symvec = get_fingerprint_slice((strreal.split()))

    # fit vae model
    altovec = fitVAE(glovevec, ldavec, symvec, id1)

    return rid, strreal, strvir, ldavec, glovevec, symvec, altovec


def get_sim(altovec, accountid):
    return getPercentage(getOtherArticles(accountid), altovec)

