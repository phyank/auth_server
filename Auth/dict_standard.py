from Auth.common import *
#from Auth.parse_and_cut import *

ARTICLE_ID=0
LEARN_NAME=1
TITLE=2
URL=3
ARTICLE_WORD_LIST=4

class WrongLearingSetError(BaseException):
    pass

#同义词类内部词频差异比较
dataset_dict={}
for learn_set in database:
    with open(CUT_FILE_DIR + learn_set + '.txt') as file1:
        wordlist = file1.read().split()
    dataset_dict[learn_set]=wordlist

def run(learnlist,checklist,dict):
    counterl={}
    counterc={}
    class_dict=make_class_dict(dict)

    for word in learnlist:
        if word not in dict:
            pass
        else:
            record=dict[word]

            current_class=record[CLASS]

            if current_class not in counterl:
                counterl[current_class]=[current_class,{word:1},1]
                continue
            else:
                if word in counterl[current_class][WORD_COUNTER_DICT]:
                    counterl[current_class][WORD_COUNTER_DICT][word] += 1
                else:
                    counterl[current_class][WORD_COUNTER_DICT][word] = 1

                counterl[current_class][SUM_OF_CLASS]+=1

    for word in checklist:
        if word not in dict:
            pass
        else:
            record = dict[word]

            current_class = record[CLASS]

            if current_class not in counterc:
                counterc[current_class] = [current_class, {word: 1}, 1]
                continue
            else:
                if word in counterc[current_class][WORD_COUNTER_DICT]:
                    counterc[current_class][WORD_COUNTER_DICT][word] += 1
                else:
                    counterc[current_class][WORD_COUNTER_DICT][word] = 1

                counterc[current_class][SUM_OF_CLASS] += 1

    common_class={}

    for aClass in counterl:
        if aClass in counterc:
            common_class[aClass]=True

    difference=0
    sum=0

    for aClass in common_class:
        difference_counter={}
        class_record_l=counterl[aClass]
        word_counter_dict_l=class_record_l[WORD_COUNTER_DICT]

        class_record_c = counterc[aClass]
        word_counter_dict_c=class_record_c[WORD_COUNTER_DICT]

        for aWord in word_counter_dict_l:
            difference_counter[aWord]=True

        for aWord in word_counter_dict_c:
            difference_counter[aWord]=True

        for aWord in difference_counter:
            sum+=1

            if aWord in word_counter_dict_l:
                ratio1=word_counter_dict_l[aWord]/class_record_l[SUM_OF_CLASS]
            else:
                ratio1=0

            if aWord in word_counter_dict_c:
                ratio2 = word_counter_dict_c[aWord] / class_record_c[SUM_OF_CLASS]
            else:
                ratio2 = 0

            if not ratio1:
                appear='B'
            elif not ratio2:
                appear='A'
            else:
                appear='AB'

            abs=ratio1-ratio2 if ratio1>=ratio2 else ratio2-ratio1

            class_dict[aClass][CLASS_PARTICIPATION]+=abs

            class_dict[aClass][MEMBERS]+=' '+aWord+appear+str(abs)

            difference+=abs

    if sum!=0:
        return difference/sum,sum,len(common_class),class_dict
    else:
        return 0,sum,len(common_class),class_dict


def cmp_article(id,learn_set,title,url,wordlist):
    dict=get_dict()
    try:
        list1 = dataset_dict[learn_set]
    except:
        raise WrongLearingSetError
    else:

        list2=wordlist

        index, sum1, sum2, class_dict = run(list1, list2, dict)

        sorted_class = []
        for key in class_dict:
            class_record = class_dict[key]
            sorted_class.append(
                (key, class_record[CLASS_PARTICIPATION], class_record[DIMENSION], class_record[MEMBERS]))

        sorted_class = sorted(sorted_class, key=lambda tuple: tuple[1], reverse=True)

        report={}
        report['learn'],report['check']=learn_set,str(id)
        report['dif'],report['s1'],report['s2']=str(index),str(sum1),str(sum2)

        result = '\tlearn:' + learn_set + ' check '+title+'     \t Result: \t' + str(index) + ' \t' + str(
            sum1) + ' \t' + str(sum2)+'\n   URL: '+url

        print(result)

        result += '\n\n\n'
        l = 0
        for k in sorted_class:
            if l <= 1000:
                if k[1]:
                    result += "\n  \tclass: " + k[0] + "  \td: " + str(k[2]) + "  \tpt: " + str(k[1]) + "  \tdiff: " + k[3]
                    l += 1
            else:
                break

        report['report']=result
        report['error']=False

        return report
