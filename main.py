from flask import Flask, render_template, request, url_for, redirect, session
import os
import bcrypt
import pymongo

app = Flask(__name__)
app.secret_key = "relativement secret"

mongo = pymongo.MongoClient(os.getenv("MONGO_KEY"))
@app.route('/')
def index():
  db_animes = mongo.db.animes
  animes = db_animes.find({})
  db_mangas = mongo.db.mangas
  mangas = db_mangas.find({})
  # variable qui servira a contenir les infos de la bdd
  # titre du manganime : titre
  # image du manganime : url_image
  # lien du manganime : url_manganime
  # id du manganime : _id
  # return render_template("index.html")
  return render_template("index.html", animes=animes, mangas=mangas)

@app.route('/manganime/<type>/<id_manganime>')
def manganime(type, id_manganime):
  if type == "anime" :
    db_animes = mongo.db.animes
    anime = db_animes.find_one({"_id": id_manganime})
    return render_template("manganime.html", anime=anime, type=type)
  elif type == "manga" :
    db_mangas = mongo.db.mangas
    manga = db_mangas.find_one({"_id": id_manganime})
    return render_template("manganime.html", manga=manga, type=type)
  return render_template("manganime.html")
  
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
          'register.html', erreur="les mots de passe doivent être identiques")
  else:
    return render_template('register.html')


@app.route('/add')
def add():
  return render_template("add.html")

@app.route('/admin')
def admin():
  return render_template("admin.html")

@app.route('/logout')
def logout():
  session.clear()
  return redirect(url_for("index"))

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=80)
