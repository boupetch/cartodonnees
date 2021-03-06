# http://flask.pocoo.org/

from flask import Flask
from flask import request
from flask import Response
from pymongo import MongoClient

from flask.ext.cors import CORS

import json

app = Flask(__name__)
CORS(app)

client = MongoClient()
db = client.cartographie

def getAdministrations():
  admindico = {}
  with open("../data/administrations.txt") as f:
    for ligne in f.readlines():
      ligne = ligne.replace("\n", "")
      ligne = ligne.split(" | ")
      for admin in ligne:
        admindico[admin] = 0
  adminlist = []
  for key, value in admindico.items():
    adminlist.append(key)
  return adminlist

def getAdministrationsListe():
  administrations = []
  with open("../data/administrations.txt") as f:
    for ligne in f.readlines():
      ligne = ligne.replace("\n", "")
      ligne = ligne.split(" | ")
      administrations.append(ligne)
  return administrations
  
def getAdministrationsArbre(administrations):
  
  etat = {"nom":"État", "children":[]}
  
  # Niveau 1
  for ligne in  administrations:
    estPresent = False
    for children in etat["children"]:
      if children["nom"] == ligne[0]:
        estPresent = True
    if estPresent == False:
      etat["children"].append({"nom":ligne[0], "children":[]})
  # Niveau 2
  for ligne in  administrations:
    if len(ligne) >= 2:
      for level1 in etat["children"]:
        if level1["nom"] == ligne[0]:
          estPresent = False
          for children in level1["children"]:
            if children["nom"] == ligne[1]:
              estPresent = True
          if estPresent == False:
            level1["children"].append({"nom":ligne[1], "children":[]})
  # Niveau 3
  for ligne in  administrations:
    if len(ligne) >= 3:
      for level1 in etat["children"]:
        if level1["nom"] == ligne[0]:
          for level2 in level1["children"]:
            if level2["nom"] == ligne[1]:
              estPresent = False
              for children in level2["children"]:
                if children["nom"] == ligne[2]:
                  estPresent = True
              if estPresent == False:
                level2["children"].append({"nom":ligne[2], "children":[]})
  # Niveau 4
  for ligne in  administrations:
    if len(ligne) >= 4:
      for level1 in etat["children"]:
        if level1["nom"] == ligne[0]:
          for level2 in level1["children"]:
            if level2["nom"] == ligne[1]:
              for level3 in level2["children"]:
                if level3["nom"] == ligne[2]:
                  estPresent = False
                  for children in level3["children"]:
                    if children["nom"] == ligne[3]:
                      estPresent = True
                  if estPresent == False:
                    level3["children"].append({"nom":ligne[3], "children":[]})   
  # Niveau 5
  for ligne in  administrations:
    if len(ligne) >= 5:
      for level1 in etat["children"]:
        if level1["nom"] == ligne[0]:
          for level2 in level1["children"]:
            if level2["nom"] == ligne[1]:
              for level3 in level2["children"]:
                if level3["nom"] == ligne[2]:
                  for level4 in level3["children"]:
                    if level4["nom"] == ligne[3]:
                      estPresent = False
                      for children in level3["children"]:
                        if children["nom"] == ligne[4]:
                          estPresent = True
                      if estPresent == False:
                        level4["children"].append({"nom":ligne[4], "children":[]})   
  return etat
  
def getBasesSearch(query):
  bases = list()
  for base in db.bases.find({},{"nom":1,"description":1}):
    if query.lower() in base["nom"].lower():
      bases.append(base["nom"])
    else:
      if "description" in base:
        if query.lower() in base["description"].lower():
          bases.append(base["nom"])
  return bases
  
def getBase(query):
  for base in db.bases.find({"nom":query}):
    del base["_id"]
    return base
  
def getBasesNoms():
  noms = list()
  for nom in db.bases.find({},{"nom":1}):
    noms.append(nom["nom"])
  return noms
  
def getGestionnaires():
  return db.bases.distinct("gestionnaire")
  
def getGestionnairesInconnus():
  gestionnaires = db.bases.distinct("gestionnaire")
  administrations = getAdministrations()
  return list(set(gestionnaires) - set(administrations))

def getBasesAcronymes():
  acronymes = list()
  for acronyme in db.bases.find({"acronyme":{"$exists":"true"}},{"acronyme":1,"nom":1}):
    del acronyme["_id"]
    acronymes.append(acronyme)
  return acronymes
  
def existeBase(nom):
  # Pour savoir si une base de données est déjà référencée
  if (db.bases.find_one({"nom": nom}) == None):
    return False
  else:
    return True
    
def getListeBases():
  # Retourne la liste des bases
  resultats = dict()
  for base in db.bases.find():
    del base["_id"]
    nom = base["nom"]
    del base["nom"]
    resultats[nom] = base
  return resultats
  
def getListeBasesRaw():
  # Retourne la liste des bases
  resultats = list()
  for base in db.bases.find():
    del base["_id"]
    resultats.append(base)
  return resultats
  
def getDicoSchema(dico):
  schema = {}
  for key,value in dico.items():
    if(str(type(value)) == "<class 'dict'>"):
      schema[key] = getDicoSchema(value)
    else:
      schema[key] = str(type(value))
  return schema

def getGestionnaireBases():
  gestionnaires = getGestionnaires()
  resultats = {}
  for gestionnaire in gestionnaires:
    bases = []
    for base in db.bases.find({"gestionnaire": gestionnaire}):
      bases.append(base["nom"])
    resultats[gestionnaire] = bases
  return resultats

def multiLevelupdate(dico1,dico2):
  for key,value in dico2.items():
    if(str(type(value)) == "<class 'dict'>"):
      if key in dico1:
        if(str(type(dico1[key])) == "<class 'dict'>"):
          dico1[key] = multiLevelupdate(dico1[key],dico2[key])
      else:
          dico1[key] = dico2[key]
    else:
      dico1[key] = dico2[key]
  return dico1
  
def APIerror(message):
  print(message)
  return message
  
@app.route("/")
def hello():
  # Retourne des informations sur l'API
  info = {}
  info["api"] = "Cartographie collaborative des données de l'État"
  info["version"] = "0.0.1"
  return Response(json.dumps(info, indent= 2,ensure_ascii=False),mimetype='application/json; charset=utf-8')

@app.route("/bases/liste", methods=['GET'])
def basesliste():
  return Response(json.dumps(getListeBasesRaw(), indent= 2,ensure_ascii=False),mimetype='application/json; charset=utf-8')

@app.route("/bases/acronymes", methods=['GET'])
def basesacronymes():
  return Response(json.dumps(getBasesAcronymes(), indent= 2,ensure_ascii=False),mimetype='application/json; charset=utf-8')

@app.route("/bases/noms", methods=['GET'])
def basesnoms():
  return Response(json.dumps(getBasesNoms(), indent= 2,ensure_ascii=False),mimetype='application/json; charset=utf-8')

@app.route("/bases/search", methods=['GET'])
def basessearch():
  return Response(json.dumps(getBasesSearch(request.args.get('q')), indent= 2,ensure_ascii=False),mimetype='application/json; charset=utf-8')

@app.route("/bases", methods=['GET', 'POST'])
def bases():
    if request.method == 'POST':
      if('nom' in request.json):
        if('gestionnaire' in request.json):
          # Vérifier si le nom et le gestionnaire sont renseignés
          if(existeBase(request.json["nom"]) == False):
            inserted_id = db.bases.insert_one(request.json).inserted_id
            return str(inserted_id)
          else:
            return APIerror("La base de données existe déjà.")
        else:
          return APIerror("Le gestionnaire de la base doit être renseigné.")
      else:
        return APIerror("Le nom de la base doit être renseigné.")
    elif(request.args.get('q') is not None):
      return Response(json.dumps(getBase(request.args.get('q')), indent= 2,ensure_ascii=False),mimetype='application/json; charset=utf-8')
    else:
      return Response(json.dumps(getListeBases(), indent= 2,ensure_ascii=False),mimetype='application/json; charset=utf-8')

@app.route("/datasets/producteurs", methods=['GET'])
def datasetsproducteurs():
  return Response(json.dumps(db.datasets.distinct("organization"), indent= 2,ensure_ascii=False),mimetype='application/json; charset=utf-8')
 
@app.route("/datasets", methods=['GET'])
def datasets():
  return Response(json.dumps(db.datasets.distinct("slug"), indent= 2,ensure_ascii=False),mimetype='application/json; charset=utf-8')
   
@app.route("/bases/datasets", methods=['GET'])
# Retourne le schema d'un objet base
## TODO
def basesdatasets():
  datasets = []
  for base in db.bases.find():
    if "datasets" in base:
      if (str(type(base["datasets"])) == "<class 'dict'>"):
        for dataset in base["datasets"]:
          datasets.append({"gestionnaire":base["gestionnaire"],"base":base["nom"],"dataset":dataset})
      else:
        datasets.append({"gestionnaire":base["gestionnaire"],"base":base["nom"],"dataset":base["datasets"]})
  return Response(json.dumps(datasets, indent= 2,ensure_ascii=False),mimetype='application/json; charset=utf-8')


@app.route("/bases/schema", methods=['GET'])
# Retourne le schema d'un objet base
def basesSchema():
  
  dico = {}
  for nom,base in getListeBases().items():
    dico = multiLevelupdate(getDicoSchema(base),dico)
  resultat = {"Nom de la base":dico}
  
  return Response(json.dumps(resultat, indent= 2,ensure_ascii=False),mimetype='application/json; charset=utf-8')

@app.route("/bases/update", methods=['GET'])
# Met à jour le champ d'une base
def baseUpdate():
  if(request.args.get('base') is None or request.args.get('attribut') is None or request.args.get('valeur') is None):
    return Response(json.dumps({"resultat","Mauvaise requête."}, indent= 2,ensure_ascii=False),mimetype='application/json; charset=utf-8')
  else:
    print(request.args.get('base'))
    print(request.args.get('attribut'))
    print(request.args.get('valeur'))
    
    db.bases.update_one(
      {"nom":request.args.get('base')},
      {"$set":
        {request.args.get('attribut'):request.args.get('valeur')}
        })
      
    return Response(json.dumps({"ok":"ok"}, indent= 2,ensure_ascii=False),mimetype='application/json; charset=utf-8')


@app.route("/gestionnaires", methods=['GET'])
# Retourne la liste des gestionnaires de base de données.
def gestionnaires():
  return Response(json.dumps(getGestionnaires(), indent= 2,ensure_ascii=False),mimetype='application/json; charset=utf-8')
  
@app.route("/gestionnaires/inconnus", methods=['GET'])
# Retourne la liste des gestionnaires inconnus de base de données.
def gestionnairesInconnus():
  return Response(json.dumps(getGestionnairesInconnus(), indent= 2,ensure_ascii=False),mimetype='application/json; charset=utf-8')
  
@app.route("/gestionnaires/bases", methods=['GET'])
# Retourne un dictionnaire des gestionnaires de base de données et de leurs bases.
def gestionnairesBases():
  return Response(json.dumps(getGestionnaireBases(), indent= 2,ensure_ascii=False),mimetype='application/json; charset=utf-8')


def setDBs(arbre,gestionnaire,base):
  for key, value in arbre.items():
    if(key == "children"):
      for elem in value:
        if(elem["nom"] == gestionnaire):
          elem["children"].append({"nom" : base})
        setDBs(elem,gestionnaire,base)
  return arbre

@app.route("/datasets/producteurs/arbre", methods=['GET'])
def datasetsProducteursArbre():

  return "OK"
@app.route("/gestionnaires/bases/arbre", methods=['GET'])
def gestionnairesBasesArbre():
  
  # Récupérer les gestionnaires identifiés dans l'annuaire
  inter = list(set(getAdministrations()) & set(getGestionnaires()))
  
  # Transformer les gestionnaires en arbre
  interListe = []
  for gestionnaire in inter:
    for ligne in getAdministrationsListe():
      i = 0
      for administration in ligne:
        i = i +1
        if(administration == gestionnaire):
          if(len(ligne) == i):
            interListe.append(ligne)
  arbre = getAdministrationsArbre(interListe)
  
  # Ajouter les bases à l'arbre
  for gestionnaire,bases in getGestionnaireBases().items():
    for base in bases:
      arbre = setDBs(arbre,gestionnaire,base)
  
  return Response(json.dumps(arbre, indent= 2,ensure_ascii=False),mimetype='application/json; charset=utf-8')

# Administrations
@app.route("/administrations", methods=['GET'])
def administrations():
  return Response(json.dumps(getAdministrations(), indent= 2,ensure_ascii=False),mimetype='application/json; charset=utf-8')

@app.route("/administrations/arbre", methods=['GET'])
def administrationsArbres():
  return Response(json.dumps(getAdministrationsArbre(getAdministrationsListe()), indent= 2,ensure_ascii=False),mimetype='application/json; charset=utf-8')

if __name__ == "__main__":
    app.debug = True
    app.run()
