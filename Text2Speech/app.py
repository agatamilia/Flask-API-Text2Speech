from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
from pymongo import MongoClient
from gtts import gTTS
from datetime import datetime
import pymongo
from io import BytesIO
from bson import ObjectId
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user

app = Flask(__name__)

client = MongoClient("mongodb+srv://text2speech:12345@cluster0.kdkxezc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['TTS']
collection = db['tts_history']

#https://www.geeksforgeeks.org/how-to-add-authentication-to-your-app-with-flask-login/
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SECRET_KEY"] = "abc"
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.init_app(app)

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)

db.init_app(app)

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.route('/')
def index():
    return redirect(url_for("login"))

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = Users(username=request.form.get("username"), password=request.form.get("password"))
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = Users.query.filter_by(username=request.form.get("username")).first()
        if user and user.password == request.form.get("password"):
            login_user(user)
            return redirect(url_for("history"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    logout_user()
    return render_template("logout.html")

@app.route('/history', methods=['GET'])
def history():
    history_data = list(collection.find().sort('updated_at', pymongo.DESCENDING))
    return render_template('history.html', history=history_data)

#https://www.geeksforgeeks.org/convert-text-speech-python/
@app.route('/convert', methods=['GET','POST'])
def convert():
    if request.method == 'POST':
        text = request.form['text']
        lang = request.form['voice']
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry_id = str(ObjectId())  

        tts = gTTS(text=text, lang=lang)
        
        audio_data = BytesIO()
        tts.write_to_fp(audio_data)

        data = {
            '_id': entry_id,
            'text': text,
            'language': lang,
            'created_at': timestamp,
            'updated_at': timestamp,
            'audio_data': audio_data.getvalue()
        }
        collection.insert_one(data)
        audio_path = url_for('play_audio', entry_id=entry_id)
        return render_template('convert.html', audio_path=audio_path)
    elif request.method == 'GET':
        return render_template('convert.html')
    else:
        return "Method Not Allowed", 405

@app.route('/audio/<entry_id>')
def play_audio(entry_id):
    data = collection.find_one({'_id': entry_id})
    if data:
        audio_data = data['audio_data']
        return send_file(BytesIO(audio_data), mimetype='audio/mp3')
    else:
        return "Audio not found"

@app.route('/edit/<entry_id>', methods=['GET'])
def edit_entry(entry_id):
    entry = collection.find_one({'_id': entry_id})
    if entry:
        entry_text = entry['text']
        selected_voice = None
        return render_template('edit.html', entry_id=entry_id, entry_text=entry_text, selected_voice=selected_voice)
    else:
        return "Entry not found", 404

@app.route('/edit/<entry_id>', methods=['PUT'])
def update_entry(entry_id):
    lang = request.json['voice']
    
    entry = collection.find_one({'_id': entry_id})
    text = entry['text']
    
    tts = gTTS(text=text, lang=lang)
    
    audio_data = BytesIO()
    tts.write_to_fp(audio_data)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    collection.update_one({'_id': entry_id}, {'$set': {'audio_data': audio_data.getvalue(), 'language': lang, 'updated_at': timestamp}})
    
    return jsonify({'message': 'Entry updated successfully'})

@app.route('/search', methods=['GET'])
def search():
    search_query = request.args.get('search_query', '')
    search_results = list(collection.find({'text': {'$regex': search_query, '$options': 'i'}}))
    return render_template('search.html', search_query=search_query, search_results=search_results)

@app.route('/delete/<entry_id>', methods=['POST'])
def delete_entry(entry_id):
    if request.method == 'POST':
        deleted_entry = collection.find_one_and_delete({'_id': entry_id})
        if deleted_entry:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            response = {
                'message': 'Entry deleted successfully',
                'entry_id': entry_id,
                'deleted_at': timestamp,
                'deleted_entry': deleted_entry
            }
            return jsonify(response), 200
        else:
            return jsonify({'error': 'Entry not found'}), 404 
    else:
        return jsonify({'error': 'Method Not Allowed'}), 405

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='5000', debug=True)
