# -*- coding: cp936 -*-    
""" 
     原始数据，用于建立模型 
"""  
#缩水版的courses，实际数据的格式应该为 课程名\t课程简介\t课程详情，并已去除html等干扰因素  
courses = [             
            u'Writing II: Rhetorical Composing',  
            u'Genetics and Society: A Course for Educators',  
            u'General Game Playing',  
            u'Genes and the Human Condition (From Behavior to Biotechnology)',  
            u'A Brief History of Humankind',  
            u'New Models of Business in Society',  
            u'Analyse Numrique pour Ingnieurs',  
            u'Evolution: A Course for Educators',  
            u'Coding the Matrix: Linear Algebra through Computer Science Applications',  
            u'The Dynamic Earth: A Course for Educators',  
            u'Tiny Wings\tYou have always dreamed of flying - but your wings are tiny. Luckily the world is full of beautiful hills. Use the hills as jumps - slide down, flap your wings and fly! At least for a moment - until this annoying gravity brings you back down to earth. But the next hill is waiting for you already. Watch out for the night and fly as fast as you can. ',  
            u'Angry Birds Free',  
            u'没有\它很相似',  
            u'没有\t它很相似',  
            u'没有\t他很相似',  
            u'没有\t他不很相似',  
            u'没有',  
            u'可以没有',  
            u'也没有',  
            u'有没有也不管',  
            u'Angry Birds Stella',  
            u'Flappy Wings - FREE\tFly into freedom!A parody of the #1 smash hit game!',  
            u'没有一个',  
            u'没有一个2',  
           ]  
  
#只是为了最后的查看方便  
#实际的 courses_name = [course.split('\t')[0] for course in courses]  
courses_name = courses  
  
  
""" 
    预处理(easy_install nltk) 
"""  
def pre_process_cn(courses, low_freq_filter = True):  
    """ 
     简化的 中文+英文 预处理 
        1.去掉停用词 
        2.去掉标点符号 
        3.处理为词干 
        4.去掉低频词 
 
    """  
    import nltk  
    import jieba.analyse  
    from nltk.tokenize import word_tokenize  
     
    texts_tokenized = []  
    for document in courses:          #########document是courses中的每个元素  
        texts_tokenized_tmp = []  
        for word in word_tokenize(document):     ############word为document中每个单词  
            texts_tokenized_tmp += jieba.analyse.extract_tags(word,10)  #########texts_tokenized_tmp为list，里的元素为每个document打散成为  
        texts_tokenized.append(texts_tokenized_tmp)    ##########texts_tokenized为列表的列表  
     
    texts_filtered_stopwords = texts_tokenized  
  
    #去除标点符号  
    english_punctuations = [',', '.', ':', ';', '?', '(', ')', '[', ']', '&', '!', '*', '@', '#', '$', '%']  
    texts_filtered = [[word for word in document if not word in english_punctuations] for document in texts_filtered_stopwords]       ######去除texts_tokenized中的标点符号  
  
    #词干化  
    from nltk.stem.lancaster import LancasterStemmer  
    st = LancasterStemmer()  
    texts_stemmed = [[st.stem(word) for word in docment] for docment in texts_filtered]   #####将texts_tokenized每个单词更改为其词根形式  
     
    ##########去除过低频词  
    if low_freq_filter:  
        all_stems = sum(texts_stemmed, [])       #######texts_stemmed中词根组成的list，可以有重复...实验了一下sum函数，把二维list改为一维list，具体可以实验  
        stems_once = set(stem for stem in set(all_stems) if all_stems.count(stem) == 1)        #######texts_stemmed中所有不重复的元素组成stems_once集合  
        texts = [[stem for stem in text if stem not in stems_once] for text in texts_stemmed]    #######将stems_once之外的其他stem改为初始文章形式，即若stems_once中的stem属于某篇文章，则将该stem放到该文章所在的list  
    else:  
        texts = texts_stemmed  
    return texts  
  
lib_texts = pre_process_cn(courses)  
# print lib_texts  
  
""" 
    引入gensim，正式开始处理(easy_install gensim) 
"""  
  
def train_by_lsi(lib_texts):  
    """ 
        通过LSI模型的训练 
    """  
    from gensim import corpora, models, similarities  
  
    #为了能看到过程日志  
    #import logging  
    #logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)  
  
    dictionary = corpora.Dictionary(lib_texts)  
    corpus = [dictionary.doc2bow(text) for text in lib_texts]     #doc2bow(): 将collection words 转为词袋，用两元组(word_id, word_frequency)表示          ####corpus中括号内为每篇文章中的某个单词，及其统计书目  
    tfidf = models.TfidfModel(corpus)  
    corpus_tfidf = tfidf[corpus]  
  
    #拍脑袋的：训练topic数量为10的LSI模型  
    lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=10)  
    index = similarities.MatrixSimilarity(lsi[corpus])     # index 是 gensim.similarities.docsim.MatrixSimilarity 实例  
     
    return (index, dictionary, lsi)  
  
     
#库建立完成 -- 这部分可能数据很大，可以预先处理好，存储起来  
(index,dictionary,lsi) = train_by_lsi(lib_texts)  
     
#要处理的对象登场  
target_courses = [u'没有']  
target_text = pre_process_cn(target_courses, low_freq_filter=False)  
  
  
""" 
对具体对象相似度匹配 
"""  
  
#选择一个基准数据  
ml_course = target_text[0]  
  
#词袋处理  
ml_bow = dictionary.doc2bow(ml_course)    
  
#在上面选择的模型数据 lsi 中，计算其他数据与其的相似度  
ml_lsi = lsi[ml_bow]     #ml_lsi 形式如 (topic_id, topic_value)  
sims = index[ml_lsi]     #sims 是最终结果了， index[xxx] 调用内置方法 __getitem__() 来计算ml_lsi  
  
#排序，为输出方便  
sort_sims = sorted(enumerate(sims), key=lambda item: -item[1])  
  
#查看结果  
print sort_sims[0:10]   #看下前10个最相似的，第一个是基准数据自身  
print courses_name[sort_sims[1][0]]  
print courses_name[sort_sims[2][0]]