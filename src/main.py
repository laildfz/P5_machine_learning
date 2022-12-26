import pandas as pd
import nltk 
from nltk.corpus import stopwords
import gensim
import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
from matplotlib import pyplot as plt
from gensim.models import TfidfModel
from gensim import corpora
from nltk.tokenize import wordpunct_tokenize
from flask import Flask, request, jsonify
 
nltk.download('stopwords') 
nltk.download('wordnet')
nltk.download('omw-1.4')

def delete_stopwords(tokens):
    stop_words = set(stopwords.words('english'))
    return [token for token in tokens if token not in stop_words]   

def prepare():
    data = pd.read_csv("data/data_clean.csv")
    data = data[["Title", "Body", "Tags"]]
    data.reset_index(inplace=True)
    data.drop(columns='index', inplace=True) 

    data['Post'] = data.apply(lambda x: (x['Title'] + ' ' + x['Body'] + ' ' + x['Tags'] if x['Title'] == x['Title'] else x['Body']).lower(), axis=1)    
    sentences = data['Post'].to_list()
    sentences = [gensim.utils.simple_preprocess(text) for text in sentences]
    return sentences 

def train():
    sentences = prepare()
    dictionary = corpora.Dictionary(sentences)
    dictionary.filter_extremes(no_below=1000) 
    bow_corpus = [dictionary.doc2bow(text) for text in sentences]
    tfidf = TfidfModel(bow_corpus)
    tfidf_corpus = [tfidf[text] for text in bow_corpus]
    ldamodel = gensim.models.ldamodel.LdaModel(tfidf_corpus, num_topics=8, id2word = dictionary, passes=20) 
    return ldamodel, dictionary

MODEL, DICTIONNARY  = train()
app = Flask(__name__) 

@app.route('/predict', methods=['GET'])
def predict():
    post = request.args.get('post') 
    tokens = wordpunct_tokenize(post)
    tokens = delete_stopwords(tokens) 
    bow_vector = DICTIONNARY.doc2bow(tokens) 
    doc_topic = MODEL.get_document_topics(bow_vector)

    topics = {}

    for n, prob in doc_topic:
        if prob >= 0.5:
            topic_lda = MODEL.show_topics(num_topics=n, num_words=5, formatted=False)  
            for index, topic in topic_lda:
                topics_name = '|'.join([w[0] for w in topic])
                topics[topics_name] = float(prob) 

    return jsonify(topics) 


if __name__ == "__main__":
    app.run()