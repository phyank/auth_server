import pickle


# CHK_ARTICLE_REPORT_DIR='data/result/chk_article/'
# CUT_FILE_DIR='data/cut/'
# CUT_DATASET_FILE='data/pickle/cut_dataset.pickle'

ROOT_DIR='Auth/'

CHK_ARTICLE_REPORT_DIR=ROOT_DIR+'data/result/chk_article_hit/'
CUT_FILE_DIR=ROOT_DIR+'data/cut_hit/'
CUT_DATASET_FILE=ROOT_DIR+'data/pickle/cut_dataset_hit.pickle'
DICT_PICKLE_DIR=ROOT_DIR+'data/pickle/dict.pickle'
PUNC_DIR=ROOT_DIR+"punctuation.txt"
HLP_LL_DIR=ROOT_DIR+'hlp_ll.txt'

WORD=0
CLASS=1
NO=2
CLASS_SUM=3

CURRENT_CLASS=0
WORD_COUNTER_DICT=1
SUM_OF_CLASS=2

CLASS_PARTICIPATION=0
DIMENSION=1
MEMBERS=2

Q=0
R=1
S=2

#这个列表存储目标CSV文件的名称。要添加新的文件，只需加在此处。
database=['dsjwz.csv','gkw.csv','jqzx.csv','ktx.csv','mm.csv','xkd.csv','xsx.csv']

#这个函数返回上述被pickle的字典
def get_cut_dataset():
    with open(CUT_DATASET_FILE,'rb') as dumpfile:
        cut_dataset=pickle.load(dumpfile)
    return cut_dataset

def get_dict():
    with open(DICT_PICKLE_DIR,'rb') as pfile:
        dict=pickle.load(pfile)

    return dict

def make_class_dict(dict):
    class_dict={}
    for word in dict:
        current_class=dict[word][CLASS]
        if current_class not in class_dict:
            class_dict[current_class]=[0,1,''] #class_participation, sum_of_class_member
        else:
            class_dict[current_class][DIMENSION]+=1

    return class_dict