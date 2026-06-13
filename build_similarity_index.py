#-*- coding: UTF-8 -*-
from gensim import corpora,similarities,models
import jieba,time

import os,pymssql
import jieba.analyse

import sys
try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except:
    pass

import codecs
from textrank4zh import TextRank4Keyword, TextRank4Sentence


def save_article_info(info_str, file_name):
    try:
        result = "Failed"
        article_file = open(file_name, 'a')
        #print(time.asctime(time.localtime(time.time()))+':  '+in_log_str+'\n')
        article_file.write(info_str+'\n')            

        article_file.close()
        result = "Success"
    except:
        result = "Failed with codec issue"
    finally:
        return(result)
        

def sys_log(in_log_str):

    sys_log_file = open("c:/clean_articles/sys_log", 'a')
    print(time.asctime(time.localtime(time.time()))+':  '+in_log_str+'\n')
    sys_log_file.write(time.asctime(time.localtime(time.time()))+':  '+in_log_str+'\n')            

    sys_log_file.close()

def jieba_keywords(news):
    keywords = jieba.analyse.extract_tags(news, topK=20)
    print (keywords)


def read_file2_list(filename):
    result=[]
    file_handle = open(filename,'r' )
    result = file_handle.readlines()
    return(result) #Return the list from the file.


# Read the data from database.

def pre_format_article(raw_content):
    return(raw_content.replace('\r','').replace('\n','').replace(' ',''))


def read_db_articles(sqlcmd):
    
    server="xxx.xxx.xxx.xxx"
    user="xxxxx"
    password="xxxx"

 


    result = []
    try:
        
        conn=pymssql.connect(server,user,password,database="articleDB")




        cursor=conn.cursor()
        count = cursor.execute(sqlcmd)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
    except:
        sys_log("SQL server failed with "+sqlcmd)
    finally:
        
        return(result)


def update_db_articles(sqlcmd):
    try:

        server="192.168.1.98"
        user="sa"
        password="newsys"


        server="172.17.118.250"
        user="baifubang"
        password="qweASD123"

        conn=pymssql.connect(server,user,password,database="articleDB")
        db_result = 'Update db Failed with : ' + sqlcmd
        conn=pymssql.connect(server,user,password,database="articleDB")
        cursor=conn.cursor()
        count = cursor.execute(sqlcmd)
        #print(count)
        conn.commit()
        db_result = 'Update db Successfully with : '+ sqlcmd
        cursor.close()
        conn.close()
    except MySQLdb.Error:
        db_result = 'Update db Failed with : ' + sqlcmd
    finally:
        return(db_result)




def textrank_keyword_digest(input_text):
    
    keyword_list = []
    keyphrase_list = []
    text_digest_list = []
    tr4w = TextRank4Keyword()
    tr4w.analyze(text=input_text, lower=True, window=2)   

    #print( '关键词：' )
    for item in tr4w.get_keywords(30, word_min_len=2):
            #print(item.word, item.weight)
            keyword_list.append(item.word)
            

    print()
    #print( '关键短语：' )
    for phrase in tr4w.get_keyphrases(keywords_num=30, min_occur_num= 2):
            #print(phrase)
            keyphrase_list.append(phrase)

    tr4s = TextRank4Sentence()
    tr4s.analyze(text=input_text, lower=True, source = 'all_filters')

    print()
    #print( '摘要：' )
    for item in tr4s.get_key_sentences(num=3):
            #print(item.sentence)
            text_digest_list.append(item.sentence)

    return keyword_list,keyphrase_list,text_digest_list






def Fiter_stopword(Stopword_list,Word_list):

    #Begin to filter stopword
    outstr = []
    for item_text in Word_list:
        if item_text not in Stopword_list:
            outstr.append(item_text)

    return outstr


#print(corpora_documents)



def stop_word_list(stopword_filename):
    stopwords_list = [line.strip() for line in open(stopword_filename,'r').readlines()]
    return stopwords_list


def list2str(data_list):
    #Return the string of the list
    data_str = ",".join(data_list)
    return(data_str)

#Begin to process the articles

if __name__ == '__main__':

    #Get the stop word list
    Stopwords = [line.strip() for line in open('c:/clean_articles/stopword.txt','r').readlines()]
    Start_id = 2220000 
    End_id =   2222000
    Article_id = Start_id
    corpora_documents = []
    Real_article_id = []
    sys_log("Begin to do TFIDF data collection ")
    while Article_id <= End_id :





        #print(Article_id)
	

        Article_content = ''
        fenci_list = []
        Article_read_id = 0
        Article_real_fenci = ''
        DB_data_status_read = 0
        DB_data_status_update = 0
        fenci_list_short = []

        temp_list = list(read_db_articles('select id, article_fenci from Clean_Article where id = '+str(Article_id)))
        #只能返一条数据
        #print(temp_list)
        for field_data in temp_list:
            fenci_list = list(field_data)
            Article_read_id = int(fenci_list[0])
            Article_real_fenci = fenci_list[1]
            #print("Current id is ",Article_read_id)
            fenci_list_short = Article_real_fenci.split(",")



        if len(Article_real_fenci) == 0:
            DB_data_status_read = 0
            sys_log('Bad! No data for Article ID='+str(Article_id)+' ! Skip to next Article ID!')
        else:
            DB_data_status_read = 1
            #print('Data existing! OK!')

        if DB_data_status_read == 0:
            Article_id = Article_id + 1
            continue
        #print("  ".join(fenci_list_short))
        #corpora_documents.append(fenci_list_short)
        temp_str = save_article_info("  ".join(fenci_list_short),"c:/clean_articles/fenci_article_test.txt")
        if temp_str == "Success":
            save_article_info(str(Article_read_id),"c:/clean_articles/fenci_article_id_test.txt")
        else:
            sys_log("Article ID " + str(Article_id) +" might have invalid codec, abandon!")
            save_article_info(str(Article_read_id),"c:/clean_articles/fenci_article_badid_test.txt")
        
        Real_article_id.append(Article_read_id)
        #jieba_keywords(Article_content)

        #print(pre_format_article(Article_content))

        #print('-----db update----')


        #sqlcmd = "insert into Clean_Article values(133,'测试','刺激','4孕妇在选择喝酸梅汤的时候，记得，不要喝过于冰凉的，最好是选择常温的来喝','')"
        #print(sqlcmd)
        #print(update_db_articles(sqlcmd))

        '''Format_article_content = pre_format_article(Article_content)

        Article_keyword, Article_keyphrase, Article_digest = textrank_keyword_digest(Format_article_content)

        Temp_fenci = []
        Clean_keyword_string = list2str(Fiter_stopword(Stopwords,Article_keyword))

        Clean_article_keyphrase = list2str(Article_keyphrase)

        Clean_article_digest = list2str(Article_digest).replace("'","")

        Temp_fenci =  Fiter_stopword(Stopwords,list(jieba.cut(Format_article_content)))

        Clean_fenci_string =list2str(Temp_fenci)

        sqlcmd = "insert into Clean_Article values( "+str(Article_id) + ",'" + Clean_keyword_string +"'," + "'" + Clean_fenci_string +"',"+"'" + Clean_article_digest +"',"+ "'')"
        #print(sqlcmd)
        Temp_update = update_db_articles(sqlcmd)

        #    print(Temp_update)
        if Temp_update.find('Successfully') > 0:
            DB_data_status_update = 1
            print('Good! Data updated successfully with article id = '+str(Article_id))

        if Temp_update.find('Failed') > 0:
            DB_data_status_update = 1
            print('!!! Data updated failed with article id = '+str(Article_id))
        print (time.asctime( time.localtime(time.time())))'''
        if Article_id%1000 == 1:
            print (time.asctime( time.localtime(time.time())))
            print("Current processed ID is ---- ",Article_read_id)
        Article_id = Article_id + 1
    print("***********************")

    # 生成字典和向量语料
    #dictionary = corpora.Dictionary(corpora_documents)

    dictionary = corpora.Dictionary(line.split() for line in open('c:/clean_articles/fenci_article_test.txt'))
    #print(dictionary.token2id)
    #print(dictionary)
    dictionary.save('c:/clean_articles/dict.txt') #保存生成的词典
    #dictionary=Dictionary.load('dict.txt')#加载

    # 通过下面一句得到语料中每一篇文档对应的稀疏向量（这里是bow向量）
    #corpus = [dictionary.doc2bow(text) for text in corpora_documents]
    corpus = [dictionary.doc2bow(text.split()) for text in open('c:/clean_articles/fenci_article_test.txt')]

    
    # 向量的每一个元素代表了一个word在这篇文档中出现的次数
    # print(corpus)
    corpora.MmCorpus.serialize("c:/clean_articles/corpuse.mm",corpus)#保存生成的语料
    # corpus=corpora.MmCorpus('corpuse.mm')#加载

    # corpus是一个返回bow向量的迭代器。下面代码将完成对corpus中出现的每一个特征的IDF值的统计工作
    tfidf_model = models.TfidfModel(corpus)
    corpus_tfidf = tfidf_model[corpus]

    
    #查看model中的内容
    #for item in corpus_tfidf:
    #    print(item)
    tfidf_model.save("c:/clean_articles/data.tfidf")
    #tfidf = models.TfidfModel.load("c:/clean_articles/data.tfidf")




    print("Begin to calculate similarity for data")
    print (time.asctime( time.localtime(time.time())))

    similarity = similarities.Similarity('Similarity-tfidf-index', corpus_tfidf, num_features=len(dictionary))  

    similarity.save("c:/clean_articles/similarity.index")


    sys_log("End for TFIDF data collection ")
    sys_log("Totally about : " +str(len(Real_article_id))+ " collected")

            
