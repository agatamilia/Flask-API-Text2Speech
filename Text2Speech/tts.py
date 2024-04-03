from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
from pymongo import MongoClient
from gtts import gTTS
from datetime import datetime
import pymongo
from io import BytesIO
from bson import ObjectId

app = Flask(__name__)

client = MongoClient("mongodb+srv://text2speech:12345@cluster0.kdkxezc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['TTS']
collection = db['tts_history']

@app.route('/')
def index():
    return render_template('convert.html')

@app.route('/history', methods=['GET'])
def history():
    history_data = list(collection.find().sort('updated_at', pymongo.DESCENDING))
    return render_template('history.html', history=history_data)

@app.route('/convert', methods=['POST'])
def convert():
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
    return render_template('search.html', search_query=search_query, search_results=search)

@app.route('/delete/<entry_id>', methods=['POST'])
def delete_entry(entry_id):
    collection.delete_one({'_id': entry_id})
    return redirect(url_for('history'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='2363', debug=True)
