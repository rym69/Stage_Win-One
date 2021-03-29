import pymongo
from pymongo import MongoClient
from pprint import pprint
from bson import ObjectId
from datetime import timedelta
import bson
from bson.raw_bson import RawBSONDocument
from mongoengine import *
connect('datawinone', host='localhost', port=27017)

client = MongoClient('mongodb://localhost:27017/')

DATE_INPUT_FORMATS = ['%d-%m-%Y']
class Candidat(Document):
    nom = StringField()
    prenom = StringField()
    dateNaissaice = DateField(input_formats= '%d-%m-%Y')


class CandidatAnonyme(Document):
    nomAnnonyme = StringField()
    candidat = ReferenceField(Candidat)

class Formation(Document):
    nomFormation = StringField()
    diplome = StringField()
    anneeObtention = DateField(input_formats= '%m-%Y')
    etablissement = StringField()
    candidat = ReferenceField(CandidatAnonyme)

class Competence(Document):
    nomCompetence = StringField()
    niveau = StringField()
    candidat = ReferenceField(CandidatAnonyme)

class Experience(Document):
    nomExperience = StringField()
    employeur = StringField()
    nbAnnee = IntField()
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


'''

experience = [{
    'idExperience' : ObjectId("507f1f77bcf86cd799439055"),
    'nomExperience' : 'gestion de projet',
    'employeur' : 'Epsilon partners',
    'nbAnnee' : 3,
    'idCadidatAnnonyme' : ObjectId("507f1f77bcf86cd799439022")
}]

historique = [{
    'idHistorique' : ObjectId("507f1f77bcf86cd799439088"),
    'idCandidat': ObjectId("507f1f77bcf86cd799439011"),
    'idCandidatAnnonyme' : ObjectId("507f1f77bcf86cd799439022"),
    'idClient' : ObjectId("507f1f77bcf86cd799439077"),
    'idAppelOffre': ObjectId("507f1f77bcf86cd799439066")
}]

appelOffre = [{
    'idAppelOffre': ObjectId("507f1f77bcf86cd799439066"),
    'titre' : 'Directeur ressources humaines',
    'description' : 'recherche h/f dans le domaine de xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx xxxxxxx xxxxxxx xxxxxx xxx xxx ',
    'idClient' : ObjectId("507f1f77bcf86cd799439077")
}]
'''

with client:

    
    
    john = Candidat(nom="John", prenom= "Smith", dateNaissaice= "27-06-1997" )
    john.save()

    nouveau = CandidatAnonyme(nomAnnonyme="JS")
    nouveau.candidat = john
    nouveau.save()

    formation = Formation(nomFormation = "Ingenieur Environnement",diplome = "Environnement",anneeObtention = "06-2010",etablissement = "Polytech" )       
    formation.candidat = nouveau
    formation.save()

    competence = Competence(nomCompetence="Exel",niveau= "Bien")
    competence.candidat = nouveau
    competence.save()

    experience = Experience(nomExperience="Manager",employeur= "Epsilon-partners",nbAnnee= 3)
    experience.candidat = nouveau
    experience.save()

    dispo = Disponibilite(dateDebut= "12-12-2020", dateFin="06-06-2022")
    dispo.candidat = nouveau
    dispo.save()

    tj= TJ(tempsPartiel = "0", nbHeure = 7)
    tj.candidat = nouveau
    tj.save()
    
    appel = AppelOffre(titre="JS", description= "appel appel appel appel appel appel appel appel appel appel appel" )
    appel.save()

    unClient = ClientWinOne(nom="Win-one")
    unClient.appelOffre = [appel]
    unClient.save()

    historique = Historique()
    historique.appelOffre = appel
    historique.clientWinOne = unClient
    historique.candidat = nouveau
    historique.save()

    '''db = client.winone
    print(db.collection_names())
    
    db.candidat.insert_many(candidat)
    db.candidatAnonyme.insert_many(candidatAnonyme)
    db.formation.insert_many(formation)
    db.Competence.insert_many(Competence)
    db.experience.insert_many(experience)
    db.historique.insert_many(historique)
    db.appelOffre.insert_many(appelOffre)
    db.clientWinOne.insert_many(clientWinOne)'''