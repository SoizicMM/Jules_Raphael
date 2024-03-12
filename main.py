from flask import Flask, render_template, request, url_for, redirect, session
import os
app = Flask(__name__)

import pymongo
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

@app.route('/mangas')
def mangas():
  return render_template("mangas.html")

@app.route('/animes')
def animes():
  return render_template("animes.html")

@app.route('/manganime/<type>/<id_manganime>')
def manganime(type, id_manganime):
  if type == "anime" :
    db_animes = mongo.db.animes
    anime = db_animes.find_one({"_id": id_manganime})
    return render_template("manganime.html", anime=anime)
  elif type == "manga" :
    db_mangas = mongo.db.mangas
    manga = db_mangas.find_one({"_id": id_manganime})
    return render_template("manganime.html", manga=manga)
  return render_template("manganime.html")

@app.route('/login')
def login():
  return render_template("login.html")

@app.route('/register')
def register():
  return render_template("register.html")

@app.route('/add')
def add():
  return render_template("add.html")

@app.route('/admin')
def admin():
  return render_template("admin.html")

@app.route('/logout')
def logout():
  return render_template("logout.html")

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=80)
