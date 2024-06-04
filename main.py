from flask import Flask, render_template, request, url_for, redirect, session
import os
import bcrypt
import pymongo

from bson.objectid import ObjectId
from pymongo.operations import ReplaceOne

app = Flask(__name__)
app.secret_key = "relativement secret"

mongo = pymongo.MongoClient(os.getenv("MONGO_KEY"))


@app.route('/')
def index():
  db_manganime = mongo.db.manganime
  manganimes = db_manganime.find({"valide": True})
  # variable qui servira a contenir les infos de la bdd
  # titre du manganime : titre
  # image du manganime : url_image
  # lien du manganime : url_manganime
  # id du manganime : _id
  # return render_template("index.html")
  return render_template("index.html", manganimes=manganimes)


@app.route('/manganime/<id_manganime>', methods=["POST", "GET"])
def manganime(id_manganime):
  db_manganime = mongo.db.manganime
  db_commentaires = mongo.db.commentaires
  manganime = db_manganime.find_one({"_id": ObjectId(id_manganime)})
  commentaires = db_commentaires.find({"id_manganime": ObjectId(id_manganime)})
  if request.method == "POST":
    if "util" not in session:
      return render_template("login.html")
    else:
      description = request.form['description']
      db_commentaires.insert_one({
        "id_manganime": ObjectId(id_manganime),
        "description": description,
        "auteur": session['util']
      })
      return render_template("manganime.html", manganime=manganime, commentaires=commentaires)
  return render_template("manganime.html", manganime=manganime, commentaires=commentaires)


@app.route('/login', methods=["POST", "GET"])
def login():
  if request.method == "POST":
    db_utils = mongo.db.utilisateurs
    util = db_utils.find_one({'nom': request.form['utilisateur']})
    if util:
      if bcrypt.checkpw(request.form['mot_de_passe'].encode('utf-8'),
                        util['mdp']):
        session['util'] = request.form['utilisateur']
        return redirect(url_for("index"))
      else:
        return render_template('login.html', erreur="mot de passe incorrect")
    else:
      return render_template('login.html', erreur="L'utilisateur n'existe pas")
  else:
    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
  if request.method == 'POST':
    db_utils = mongo.db.utilisateurs
    if (db_utils.find_one({'nom': request.form['utilisateur']})):
      return render_template('register.html', erreur="Le nom existe déjà")
    else:
      if (request.form['mot_de_passe'] == request.form['verif_mot_de_passe']):
        mdp_encrypte = bcrypt.hashpw(
            request.form['mot_de_passe'].encode('utf-8'), bcrypt.gensalt())
        db_utils.insert_one({
            'nom': request.form['utilisateur'],
            'mdp': mdp_encrypte
        })
        session['util'] = request.form['utilisateur']
        return redirect(url_for('index'))
      else:
        return render_template(
            'register.html',
            erreur="les mots de passe doivent être identiques")
  else:
    return render_template('register.html')


@app.route("/supprimer/<id>")
def supprimer_manganime(id):
  db_manganime = mongo.db.manganime
  db_manganime.delete_one({"_id": ObjectId(id)})
  return "entrée supprimée"


@app.route('/add', methods=["POST", 'GET'])
def add():
  if request.method == 'POST':
    db_manganime = mongo.db.manganime
    db_manganime.insert_one({
        'titre': request.form['titre'],
        'url_image': request.form['image'],
        'description': request.form['Description'],
        'valide': False
      })
    return redirect(url_for('index'))
  else:
    return render_template('add_manga.html')

@app.route('/modifier/<id_manganime>', methods=["POST", "GET"])
def modifier(id_manganime):
  db_manganime = mongo.db.manganime
  manganime = db_manganime.find_one({"_id": ObjectId(id_manganime)})

  if request.method == "POST":
    titre = request.form['titre']
    description = request.form['description']
    db_manganime.update_one(
        {"_id": ObjectId(id_manganime)},
        {"$set": {
            "titre": titre,
            "description": description
        }})
    return redirect(url_for("index"))
  else:
    return render_template("modifier.html", manganime=manganime)


@app.route('/admin/back_animemanga')
def back_animemanga():
  db_manganime = mongo.db.manganime
  manganimes = db_manganime.find({})
  return render_template("admin/back_animemanga.html", manganimes=manganimes)


@app.route('/logout')
def logout():
  session.clear()
  return redirect(url_for("index"))

@app.route("/recherche", methods=["POST"])
def recherche():
  recherche_animanga = request.form["query"]
  db_manganime = mongo.db.manganime
  resultats = db_manganime.aggregate(
    [{
      "$match" : {
        "titre" : {
          "$regex" : recherche_animanga,
          "$options" : "i"
        }
      }
    }]
  )
  return render_template("index.html", manganimes=resultats)
#si la route est souligné en rouge, c normale. 
#il n'y a pas d'erreurs lors de l'éxecution
@app.route("/validation/<id_manganime>/<statut>")
def validation(id_manganime, statut):
  db_manganime = mongo.db.manganime
  if id_manganime and statut :
    if statut == "valide" : 
      
      db_manganime.update_one(
        {"_id": ObjectId(id_manganime)},
        {"$set": {
          "valide": True
        }}
      )
    elif statut == "refuse":
      db_manganime.delete_one({"_id": ObjectId(id_manganime)})
    return redirect(url_for("file_d_attente"))
@app.route('/file_d_attente')
def file_d_attente():
  db_manganime = mongo.db.manganime
  manganimes = db_manganime.find({"valide": False})

  return render_template('admin/back_validation.html', manganimes=manganimes)

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=80)
