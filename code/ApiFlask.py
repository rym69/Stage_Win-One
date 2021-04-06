import os
from tika import parser
from flask import Flask, render_template, request, redirect, url_for
from tika import parser # pip install tika
import re
import json
from mongoengine import connect, Document, ListField, StringField, URLField


connect(db='pythonTest', host='localhost', port=27017)

class CV(Document):
    first_name = StringField(required=True)
    last_name = StringField(required=True)

user = CV(
    first_name = "Imad",
    last_name = "Elmahrad"
)
user.save()





def get_age(words):
    for word in words:
        if "ans" in word:
            return word

def hasNumbers(inputString):
    cp = 0  
    for char in inputString:
        if char.isdigit():
            cp += 1
    if cp == 10:
        return True
    return False

def get_numero(words):
    for word in words:
        if hasNumbers(word):
            return word


def get_email(words):
    link = [".fr", ".com", ".uk"]
    for word in words:
        if "@" in word:
            for l in link:
                if l in word:
                    return word


def get_competence(words):
    competences  = words[words.index("DOMAINES DE COMPETENCES ") + 1:words.index("FORMATION ")]
    for i in range(len(competences)):
        competences[i] = competences[i][2:len(competences[i]) - 1]
    return competences

def get_formations(words):
    formations  = words[words.index("FORMATION ") + 1:words.index("CHRONOLOGIE ")]
    for i in range(len(formations)):
        if formations[i][1] == " ":
            formations[i] = formations[i][2:len(formations[i]) - 1]
        else:
            formations[i] = formations[i][1:len(formations[i]) - 1]
    formations = [forma for forma in formations if len(forma) > 5]
    return formations

def get_chronologie(words):
    chronologie  = words[words.index("CHRONOLOGIE ") + 1:words.index("ANALYSE WIN ONE   ")]
    date_indexes = []
    chronologies = dict()
    for i in range(len(chronologie)):
        if "§" in chronologie[i]:
            date_indexes.append(i)
    for j in range(len(date_indexes)):
        if j+1 < len(date_indexes):
            chronologies[chronologie[date_indexes[j]].split(":")[0][2:-1]] = chronologie[date_indexes[j]+1:date_indexes[j+1]]
        else:
            chronologies[chronologie[date_indexes[j]].split(":")[0][2:-1]] = chronologie[date_indexes[j]+1:]
    for k in chronologies.keys():
        formations = chronologies[k]
        for i in range(len(formations)):
            if formations[i][1] == " ":
                formations[i] = formations[i][2:len(formations[i]) - 1]
            else:
                formations[i] = formations[i][1:len(formations[i]) - 1]
        formations = [forma for forma in formations if len(forma) > 5]
        chronologies[k] = formations
    return chronologies

def get_winone(words):
    chronologie  = words[words.index("ANALYSE WIN ONE   ") + 1:]
    date_indexes = []
    chronologies = dict()
    for i in range(len(chronologie)):
        if "§" in chronologie[i]:
            date_indexes.append(i)
    for j in range(len(date_indexes)):
        if j+1 < len(date_indexes):
            chronologies[chronologie[date_indexes[j]].split(":")[0][2:-1]] = chronologie[date_indexes[j]+1:date_indexes[j+1]]
        else:
            chronologies[chronologie[date_indexes[j]].split(":")[0][2:-1]] = chronologie[date_indexes[j]+1:]
    for k in chronologies.keys():
        formations = chronologies[k]
        for i in range(len(formations)):
            if formations[i][1] == " ":
                formations[i] = formations[i][2:len(formations[i]) - 1]
            else:
                formations[i] = formations[i][1:len(formations[i]) - 1]
        formations = [forma for forma in formations if len(forma) > 5]
        chronologies[k] = formations
    return chronologies

# print("L'email est : ",get_email(cv_words2))
# print("L'age est : ",get_age(cv_words2))
# print("le numéro est :", get_numero(cv_words2))
# #print("le numéro est :", get_adress(cv_words2))
# print("Compétences : ", get_competence(cv_words2))
# print("Formations : ", get_formations(cv_words2))
# print("chronologie: ", get_chronologie(cv_words2))
# chronologies = get_chronologie(cv_words2)
# chronologies_json = json.dumps(get_winone(cv_words2))
print("*************************************")
# print(chronologies_json)

def parse_cv(cv_filename):
    raw = parser.from_file(cv_filename)
    cv_words =  raw['content'].split("\n")
    cv_words2 = []
    for word in cv_words:
        if len(word) > 1:
            cv_words2.append(word)
    # print(cv_words2)    
    # cv_final  = "" # dict()
    email =get_email(cv_words2)
    age = get_age(cv_words2)
    numero=get_numero(cv_words2)
    # cv_final +="L'adresse est :", get_adress(cv_words2)
    competence=str(get_competence(cv_words2))
    formation=str(get_formations(cv_words2))
    chronologie=str(get_chronologie(cv_words2))
    winOne=str(get_winone(cv_words2))
    nom = cv_words2[2]
    return (email, age, numero, nom,competence,formation,chronologie, winOne)

app = Flask(__name__)
data =  ""
@app.route('/')
def index():
    return render_template('index.html', data=data)

@app.route('/')
def index_cv(data2):
    return render_template('index.html', data=data2)

@app.route('/', methods=['POST'])
def upload_file():
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        uploaded_file.save(uploaded_file.filename)
        email, age, numero, nom, competence, formation, chronologie, winOne = parse_cv(uploaded_file.filename)
        print(data)
    # return redirect(url_for('index_cv', cv_data="YESS"))
    return render_template("cv_render.html",competence=competence, email=email, age=age, numero=numero, nom=nom, formation=formation, chronologie=chronologie, winOne=winOne)



if __name__ == "__main__":
    app.run()

app.run(port=5000)


