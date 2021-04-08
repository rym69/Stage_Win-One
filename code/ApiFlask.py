import os
from tika import parser
from flask import Flask, render_template, request, redirect, url_for, send_file
from tika import parser # pip install tika
import re
import json
from mongoengine import *
from werkzeug.utils import secure_filename
from io import BytesIO 

UPLOAD_FOLDER = os.getcwd() + '/cv'
ALLOWED_EXTENSIONS = {'pdf'}


connect(db='pythonTest', host='localhost', port=27017)


DATE_INPUT_FORMATS = ['%d-%m-%Y']
class Candidat(Document):
    nom = StringField()
    prenom = StringField()
    dateNaissaice = DateField(input_formats= '%d-%m-%Y', required=False)
    email = StringField()
    numero = StringField()
    age = StringField()
    cv = FileField()


class CandidatAnonyme(Document):
    nomAnnonyme = StringField()
    candidat = ReferenceField(Candidat)

class Formation(Document):
    #nomFormation = StringField()
    #diplome = StringField()
    #anneeObtention = DateField(input_formats= '%m-%Y')
    #etablissement = StringField()
    candidat = ReferenceField(CandidatAnonyme)
    formations = ListField(StringField())

class Competence(Document):
    #nomCompetence = StringField()
    #niveau = StringField()
    candidat = ReferenceField(CandidatAnonyme)
    competences = ListField(StringField())

class Experience(Document):
    #nomExperience = StringField()
    #employeur = StringField()
    #nbAnnee = IntField()
    candidat = ReferenceField(CandidatAnonyme)
    experiences = StringField()

class AvisWinOne(Document):
    avis = DictField()
    candidat = ReferenceField(CandidatAnonyme)

class Disponibilite(Document):
    dateDebut = DateField(input_formats= '%d-%m-%Y')
    dateFin = DateField(input_formats= '%d-%m-%Y')
    candidat = ReferenceField(CandidatAnonyme)

class TJ(Document):
    tempsPartiel = BooleanField()
    nbHeure = IntField()
    candidat = ReferenceField(CandidatAnonyme)

class AppelOffre(Document):
    titre = StringField()
    description = StringField()
    #clientWinOne = ListField(ReferenceField(ClientWinOne))

class ClientWinOne(Document):
    nom = StringField()
    appelOffre = ListField(ReferenceField(AppelOffre))


class Historique(Document):
    candidat = ReferenceField(CandidatAnonyme)
    clientWinOne = ReferenceField(ClientWinOne)
    appelOffre = ReferenceField(AppelOffre)



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

def formatArray(array):
    arrayToSend = []
    copyArray = array

    withoutFirstBracket = array[0].replace("[", "")
    withoutLastBracket = array[len(array) - 1].replace("]", "")

    copyArray.remove(copyArray[0])
    copyArray.remove(copyArray[len(copyArray) - 1])

    copyArray.insert(0, withoutFirstBracket)
    copyArray.insert(len(copyArray), withoutLastBracket)

    i = 0

    while i < len(copyArray):
        r = copyArray[i].replace("'", '')
        arrayToSend.append(r)
        i += 1


    return arrayToSend

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
data =  ""
@app.route('/')
def index():
    return render_template('index.html', data=data)

@app.route('/')
def index_cv(data2):
    return render_template('index.html', data=data2)



@app.route('/getCV', methods=['GET'])
def tes_pdf():
    nom = request.args['nom']
    person = Candidat.objects(nom=nom).first()
    if person is None:
        return "Does not exist"
    else:
        cvPDF = person.cv.read()
        content_type = person.cv.content_type
        filename = person.cv.filename
        return send_file(
            BytesIO(cvPDF),
            attachment_filename=filename,
            mimetype=content_type,
        ), 200, {'Content-Type': 'application/pdf'}
    
    

@app.route('/', methods=['POST'])
def upload_file():
    uploaded_file = request.files['file']
    if uploaded_file.filename != '' and allowed_file(uploaded_file.filename):
        filename = secure_filename(uploaded_file.filename)
        uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        email, age, numero, nom, competence, formation, chronologie, winOne = parse_cv(UPLOAD_FOLDER + '/' + filename)
        print(data)


    prenom = nom.split(' ')[0]

    nouveauCandidat = Candidat(
        nom = nom.split(" ")[1],
        prenom = prenom,
        email = email,
        age = age,
        numero = numero
    )
    with open(UPLOAD_FOLDER + '/' + filename, "rb") as fd:
        nouveauCandidat.cv.put(fd, content_type = "application/pdf", filename = filename)
    nouveauCandidat.save()

    anonyme = CandidatAnonyme(
        nomAnnonyme = (prenom[0].upper() + nom[0].upper())
    )
    anonyme.candidat = nouveauCandidat
    anonyme.save()

    formationsStringToList = formation.split("', ")
    formationsList = formatArray(formationsStringToList)
    formations = Formation(
        formations = formationsList,
    )
    formations.candidat = anonyme
    formations.save()

    competencesStringToList = competence.split("', ")
    competencesList = formatArray(competencesStringToList)
    competences = Competence(
        competences = competencesList
    )
    competences.candidat = anonyme
    competences.save()
    
    experiences = Experience(
        experiences = chronologie
    )
    experiences.candidat = anonyme
    experiences.save()

    newAvis = winOne.replace("'",'"')
    winOneParsed = json.loads(newAvis)
    avisWinOne = AvisWinOne(
        avis = winOneParsed
    )
    avisWinOne.candidat = anonyme
    avisWinOne.save()
    # return redirect(url_for('index_cv', cv_data="YESS"))
    return render_template("cv_render.html",competence=competence, email=email, age=age, numero=numero, nom=nom, formation=formation, chronologie=chronologie, winOne=winOne)



if __name__ == "__main__":
    app.run()

app.run(port=5000)


