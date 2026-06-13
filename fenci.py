#-*- coding: UTF-8 -*-
#from gensim import corpora,similarities,models
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
    user="article_xxxxx"
    password="xxx"
    result = []
    try:
        conn=pymssql.connect(server,user,password,database="articleDB")


        #conn = pyodbc.connect(r'DRIVER={SQL Native Client};SERVER=YLQQ;DATABASE=articleDB;UID=sa;PWD=newsys')
        cursor = conn.cursor()

        count = cursor.execute(sqlcmd)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
    except:
        result = []
    finally:


        return(result)

def update_db_articles(sqlcmd):
    try:
        #server="39.106.160.124"

        server="39.106.160.124"
        user="article_analysis"
        password="qwer0987pp"
        conn=pymssql.connect(server,user,password,database="articleDB")

        #conn = pyodbc.connect(r'DRIVER={SQL Native Client};SERVER=YLQQ;DATABASE=articleDB;UID=sa;PWD=newsys')
        cursor = conn.cursor()
        count = cursor.execute(sqlcmd)
        #print(count)
        conn.commit()
        db_result = 'Update db Successfully with : '+ sqlcmd
        cursor.close()
        conn.close()
    except :
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
            


    #print( '关键短语：' )
    for phrase in tr4w.get_keyphrases(keywords_num=30, min_occur_num= 2):
            #print(phrase)
            keyphrase_list.append(phrase)

    tr4s = TextRank4Sentence()
    tr4s.analyze(text=input_text, lower=True, source = 'all_filters')


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


def sys_log(in_log_str):

    sys_log_file = open("c:/clean_articles/sys_log", 'a')
    print(time.asctime(time.localtime(time.time()))+':  '+in_log_str+'\n')
    sys_log_file.write(time.asctime(time.localtime(time.time()))+':  '+in_log_str+'\n')            

    sys_log_file.close()

#Begin to process the articles

if __name__ == '__main__':

    #Get the stop word list
    Stopwords = [line.strip() for line in open('c:/clean_articles/stopword.txt','r').readlines()]
 #   Start_id = 2800000
    
 #  End_id =   3200000


    Start_id = int(sys.argv[2])
    
    End_id =   int(sys.argv[3])
    
    Article_id = Start_id
    sys_log(sys.argv[0]+ sys.argv[1]+" Begin id is "+str(Start_id))

    while Article_id <= End_id :





        #print(Article_id)
	

        Article_content = ''
        DB_data_status_read = 0
        DB_data_status_update = 0
        temp_list = list(read_db_articles('select article_content from netArticleAll where id = '+str(Article_id)))
        #只能返一条数据
        #print(temp_list)
        for field_data in temp_list:
            #print(type(field_data))
            Article_content = "".join(field_data)

        if len(Article_content) == 0:
            DB_data_status_read = 0
            sys_log('Bad! No data for Article ID='+str(Article_id)+' ! Skip to next Article ID!')
        else:
            DB_data_status_read = 1
            #print('Data existing! OK!')
        if DB_data_status_read == 0:
            Article_id = Article_id + 1
            continue

        #jieba_keywords(Article_content)

        #print(pre_format_article(Article_content))

        #print('-----db update----')


        #sqlcmd = "insert into Clean_Article values(133,'测试','刺激','4孕妇在选择喝酸梅汤的时候，记得，不要喝过于冰凉的，最好是选择常温的来喝','')"
        #print(sqlcmd)
        #print(update_db_articles(sqlcmd))

        Format_article_content = pre_format_article(Article_content)

        Article_keyword, Article_keyphrase, Article_digest = textrank_keyword_digest(Format_article_content)

        Temp_fenci = []
        Clean_keyword_string = list2str(Fiter_stopword(Stopwords,Article_keyword))

        Clean_article_keyphrase = list2str(Article_keyphrase)

        Clean_article_digest = list2str(Article_digest).replace("'","")

        Temp_fenci =  Fiter_stopword(Stopwords,list(jieba.cut(Format_article_content)))

        Clean_fenci_string =list2str(Temp_fenci)

        sqlcmd = "insert into Clean_Article values( "+str(Article_id) + ",'" + Clean_keyword_string +"'," + "'" + Clean_fenci_string +"',"+"'" + Clean_article_digest +"',"+ "'','')"
        #print(sqlcmd)
        Temp_update = update_db_articles(sqlcmd)

        #    print(Temp_update)
        if Temp_update.find('Successfully') > 0:
            DB_data_status_update = 1
            if int(Article_id)%100 == 1:
                sys_log(sys.argv[0] +' Good! Data updated successfully with article id = '+str(Article_id))

        if Temp_update.find('Failed') > 0:
            DB_data_status_update = 1
            sys_log(sys.argv[0] +sys.argv[1]+' !!! Data updated failed with article id = '+str(Article_id))
        #print (time.asctime( time.localtime(time.time())))

        Article_id = Article_id + 1
