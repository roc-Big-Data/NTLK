    # -*- coding: utf-8 -*-  
       
    """ 
    演示使用NLTK让计算机学习如何通过名字识别性别。 
    """  
       
    import nltk  
       
    # 定义学习方法  
    def gender_features(word):  
        return {'last_letter':word[-1]}  
       
    # 导入学习的姓名性别名单  
    from nltk.corpus import names  
    import random  
    names = ([(name, 'male') for name in names.words('male.txt')] + [(name, 'female') for name in names.words('female.txt')])  
    random.shuffle(names)  
       
    # 开始学习  
    f = [(gender_features(n), g) for (n, g) in names]  
    trainset, testset = f[500:], f[:500]  
    c = nltk.NaiveBayesClassifier.train(trainset)  
       
    # 测试  
    print c.classify(gender_features('Neo'))  
    print c.classify(gender_features('Trinity'))  