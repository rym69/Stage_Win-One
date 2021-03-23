from tika import parser # pip install tika
#import regex
import re
import json

raw = parser.from_file('C:/Users/BCS/Downloads/20181127_CV_WO_M_DIAW.pdf')
cv_words =  raw['content'].split("\n")
cv_words2 = []
for word in cv_words:
    if len(word) > 1:
        cv_words2.append(word)
print(cv_words2)

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

# def get_adress(words):
#     regex = re.apply_constraint("^(\d+[a-z]?)+\s+(\d+)+\s+(.+(?=\W))+\s+(.*)")
#     for word in words:
#         if word.match(regex):
#             return word


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
chronologies = get_chronologie(cv_words2)
chronologies_json = json.dumps(get_winone(cv_words2))
print("*************************************")
# print(chronologies_json)
# Regex detect email, postal adress

cv_final  =  dict()
cv_final["Nom"] = cv_words2[2]
cv_final["email"] = get_email(cv_words2)
cv_final["compétence"] = get_competence(cv_words2)
cv_final["winOne"] = get_winone(cv_words2)
cv_final_json = json.dumps(cv_final)
print(cv_final_json)
