# -*- coding: utf-8 -*-
"""Sentence Similarity Prediction.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/13KuUxDixdbP6XLEl-U_0KoEli0v8auKL
"""

import os
#os.system("apt-get update -qq")
#os.system("apt-get install -y openjdk-8-jdk-headless -qq")

print(os.listdir(os.getcwd()+"/.apt"))

os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-8-openjdk-amd64"
os.environ["PATH"] = os.environ["JAVA_HOME"] + "/bin:" + os.environ["PATH"]

import nlu

from flask import Flask,request,jsonify
import json
import math
import requests

app = Flask("Sentence Similarity")

API = "https://codeupmajor.herokuapp.com/api/discussion/predictions"

multi_pipe = None
col_names = ['sentence_embedding_bert','sentence_embedding_electra', 'sentence_embedding_use']

def dot(A,B): 
    return (sum(a*b for a,b in zip(A,B)))

def cosine_similarity(a,b):
    return dot(a,b) / ( math.sqrt(dot(a,a) * dot(b,b)) )


@app.route("/load-api")
def loadAPI():
    try:
        global multi_pipe
        multi_pipe = nlu.load('use en.embed_sentence.electra embed_sentence.bert')
        return {"status" : 200},200
    except:
        return {"status" : 500},500

@app.route("/generate-predictions",methods = ['GET', 'POST'])
def genearatePredictions():

    title = request.form['title']
    
    if title and multi_pipe:
        predictions = multi_pipe.predict(title,get_embeddings=True).iloc[0]
        
        response = {}

        for col_name in col_names:
            response[col_name] = list(predictions[col_name][0])
        
        return { "predictions" : response ,"status" : 201},201
    else:
        return { "error" :"ERROR" ,"status" : 500}, 500

@app.route("/get-similar-questions",methods=['GET','POST'])
def getSimilarQuestions():
    data = requests.get(API).json()
    embeddings = eval(request.form['predictions'])
    if data['status'] == 200 and embeddings and 'predictions' in data:
        predictions = data['predictions']
        for i in range(len(predictions)):
            similarity = 0
            for e_col in col_names:
                if e_col in predictions[i]['predictions'] and e_col in embeddings:
                    similarity += cosine_similarity(predictions[i]['predictions'][e_col],embeddings[e_col])

            predictions[i]['similarity_score'] = similarity/len(col_names)
        
        return {"similarQuestions" : sorted(predictions,key = lambda x : x['similarity_score'],reverse=True)[:3] , "status" : 201} , 201
    else:
        return { "status" : 500,"error" :"ERROR"}, 500

