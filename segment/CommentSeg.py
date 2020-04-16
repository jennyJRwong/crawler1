from pyhanlp import *
import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from PIL import Image
from wordcloud import WordCloud,ImageColorGenerator
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import pyLDAvis
import pyLDAvis.sklearn
import os
from pyhanlp.static import STATIC_ROOT, HANLP_JAR_PATH
'''
# 在import pyhanlp之前编译自己的Java class，并放入pyhanlp/static中
java_code_path = os.path.join(STATIC_ROOT, 'MyFilter.java')
with open(java_code_path, 'w') as out:
    java_code = """
import com.hankcs.hanlp.dictionary.stopword.CoreStopWordDictionary;
import com.hankcs.hanlp.dictionary.stopword.Filter;
import com.hankcs.hanlp.seg.common.Term;
public class MyFilter implements Filter
{
    public boolean shouldInclude(Term term)
    {
        if (term.nature.startsWith('m')) return true; // 数词保留
        return !CoreStopWordDictionary.contains(term.word); // 停用词过滤
    }
}
"""
    out.write(java_code)
os.system('javac -cp {} {} -d {}'.format(HANLP_JAR_PATH, java_code_path, STATIC_ROOT))
'''

# 清洗数据
def clean_data():
    cleanedData=[]
    with open('dianping_comment.txt') as f:
        for line in f:
            line = line.strip()
            p2 = re.compile('[^\u4e00-\u9fa5]')
            zh = " ".join(p2.split(line)).strip()
            zh = zh.replace('收起评论','')
            zh = ",".join(zh.split())
            new_s = re.sub("[A-Za-z0-9!！，%\[\],。]", "", zh)
            cleanedData.append(new_s)
    comment = ''.join(cleanedData)
    return comment

# 分词
def segWord():
    data = clean_data()
    HanLP.Config.ShowTermNature = False # 不要词性
    CoreNatureDictionary = JClass('com.hankcs.hanlp.dictionary.CoreDictionary')

    CoreStopWordDictionary = JClass("com.hankcs.hanlp.dictionary.stopword.CoreStopWordDictionary")
    Filter = JClass("com.hankcs.hanlp.dictionary.stopword.Filter")
    Term = JClass("com.hankcs.hanlp.seg.common.Term")
    # CoreStopWordDictionary.add('比较','应该','其实','真的','知道','觉得','下次')
    segComment = HanLP.segment(data)
    finalComment = CoreStopWordDictionary.apply(segComment)

    return finalComment

# 计算词频
def wordFre():
    segment = segWord()
    segment = [str(w) for w in segment if len(str(w))>=2]
    comment = pd.DataFrame({'segment':segment})
    comment_fre = comment.groupby(by='segment')['segment'].agg(count= np.size)
    commentFre = comment_fre.reset_index().sort_values(by='count', ascending=False)

    # with pd.ExcelWriter('wordFrequency.xlsx') as writer:
    #     commentFre.to_excel(writer,sheet_name='frequency')
    print(commentFre)
    return commentFre

# 画词云图
def wordCloud():
    # commentFre = wordFre()
    commentFre = pd.read_csv('./wordFrequency.csv')
    # image = Image.open('apple1.jpg')
    image = Image.open('apple1.jpg')
    graph = np.array(image)
    mpl.rcParams['figure.figsize'] = [10.0, 5.0]
    plt.rcParams['figure.dpi'] = 600
    plt.rcParams['savefig.dpi'] = 600
    wordcloud = WordCloud(font_path='simhei.ttf', background_color='white', max_font_size=100,mask=graph)
    comment_fre_dic = {x[1]: x[2] for x in commentFre.head(2300).values}
    wordcloud = wordcloud.fit_words(comment_fre_dic)

    imageColor = ImageColorGenerator(graph)
    wordcloud.recolor(color_func=imageColor)

    plt.figure()
    plt.imshow(wordcloud)
    plt.axis('off')
    plt.show()
    wordcloud.to_file('./wordcloudnew.png')

# 主题模型
def textTopicmodel(n_topics=2):
    segment = segWord()
    segment = [str(w) for w in segment if len(str(w)) >= 2]
    corpus = [''.join(one) for one in segment]
    tf_vectorizer =CountVectorizer(max_df=0.95,min_df=1,max_features=1500,stop_words=None)
    tf = tf_vectorizer.fit_transform(corpus)
    words = tf_vectorizer.get_feature_names()  #提取文本的关键字
    lda = LatentDirichletAllocation(n_components=n_topics,learning_offset=50,random_state=0)
    docres = lda.fit_transform(tf)
    print('============================')
    print(docres)
    print('==========================')
    print(lda.components_)
    # pyLDAvis.enable_notebook()
    visualisation = pyLDAvis.sklearn.prepare(lda,tf,tf_vectorizer)
    # pyLDAvis.save_html(visualisation,'visualisation.html')
    pyLDAvis.display(visualisation)
    pyLDAvis.show(visualisation)



if __name__ == '__main__':
    # print(clean_data())
    # for w in segWord():
    #     print(type(w))
    #     print(len(str(w)))
    # wordFre()
    wordCloud()
    # textTopicmodel()





