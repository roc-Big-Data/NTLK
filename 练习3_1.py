     #!/usr/bin/env python  
    #-*-coding=utf-8-*-  
       
       
    #数据源目录(二级目录)  
    sourceDataDir='data'  
       
    #数据源文件列表  
    fileLists = []  
       
    import os  
    from gensim import corpora, models, similarities  
                   
    def getSourceFileLists(sourceDataDir):    
        fileLists = []  
        subDirList = os.listdir(sourceDataDir)  
        for subDir in subDirList:  
            subList = os.listdir(sourceDataDir + '/' + subDir)  
            fileList = [ sourceDataDir+'/'+subDir+'/'+ x for x in subList if os.path.isfile(sourceDataDir+'/'+subDir+'/'+x)]  
            fileLists += fileList  
       
        return  fileLists     
               
               
    fileLists = getSourceFileLists(sourceDataDir)    
         
         
    if 0 < len(fileLists):   
        import codecs  
        import jieba  
        punctuations = ['','\n','\t',',', '.', ':', ';', '?', '(', ')', '[', ']', '&', '!', '*', '@', '#', '$', '%']   
           
        if not os.path.exists('dict'):  
            os.mkdir("dict")   
        if not os.path.exists('corpus'):  
            os.mkdir("corpus")   
       
        for fileName in fileLists:  
            print fileName  
       
            hFile = None  
            content = None  
            try:  
                hFile = codecs.open(fileName,'r','gb18030')  
                content = hFile.readlines()  
            except Exception,e:  
                print e  
            finally:  
                if hFile:  
                    hFile.close()  
               
            if content:  
                fileFenci = [ x for x in jieba.cut(' '.join(content),cut_all=True)]  
                fileFenci2 = [word for word in fileFenci if not word in punctuations]    
                   
                texts = [fileFenci2]  
       
                all_tokens = sum(texts, [])  
                tokens_once = set(word for word in set(all_tokens) if all_tokens.count(word) == 1)  
                texts = [[word for word in text if word not in tokens_once] for text in texts]  
       
                sFileDir, sFileName = os.path.split(fileName)  
                dictFileName = 'dict/'+sFileName+'.dict'  
                corpusFileName = 'corpus/'+sFileName+'.mm'  
                   
                dictionary = corpora.Dictionary(texts)  
                dictionary.save_as_text(dictFileName)  
       
                corpus = ([dictionary.doc2bow(text) for text in texts])  
                corpora.MmCorpus.serialize(corpusFileName, corpus)   
       
    print 'Build corpus done'  