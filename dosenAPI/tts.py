from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
from gtts import gTTS
from datetime import datetime
import pymongo
from io import BytesIO
from bson import ObjectId

app = Flask(__name__)

# Setup MongoDB connection
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["TTS"]
collection = db["tts_history"]

@app.route('/')
def index():
    return render_template('convert.html')

@app.route('/history', methods=['GET'])
def history():
    history_data = list(collection.find())
    return render_template('history.html', history=history_data)

@app.route('/convert', methods=['POST'])
def convert_text_to_speech():
    text = request.form['text']
    lang = request.form['voice']  # Get selected voice from the form
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Include timestamp with time
    entry_id = str(ObjectId())  # Generate a new ObjectId and convert it to string

    # Convert text to speech using gTTS with the selected language
    tts = gTTS(text=text, lang=lang)
    
    # Save audio data to MongoDB
    audio_data = BytesIO()
    tts.write_to_fp(audio_data)
    
    # Save data to MongoDB along with the generated ObjectId
    data = {
        '_id': entry_id,  # Save the generated ObjectId
        'text': text,
        'language': lang,  # Save selected language
        'timestamp': timestamp,
        'audio_data': audio_data.getvalue()  # Save audio data as binary
    }
    collection.insert_one(data)

    # Render convert.html with audio_path
    audio_path = url_for('play_audio', entry_id=entry_id)
    return render_template('convert.html', audio_path=audio_path)

@app.route('/audio/<entry_id>')
def play_audio(entry_id):
    # Retrieve audio data from MongoDB
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
    lang = request.json['voice']  # Get selected voice from the request JSON
    
    # Retrieve text from the database
    entry = collection.find_one({'_id': entry_id})
    text = entry['text']
    
    # Convert text to speech using gTTS with the selected language
    tts = gTTS(text=text, lang=lang)
    
    # Save audio data to MongoDB
    audio_data = BytesIO()
    tts.write_to_fp(audio_data)
    
    # Update data in MongoDB
    collection.update_one({'_id': entry_id}, {'$set': {'audio_data': audio_data.getvalue(), 'language': lang}})
    
    return jsonify({'message': 'Entry updated successfully'})

@app.route('/search', methods=['GET'])
def search():
    search_query = request.args.get('search_query', '')
    # Cari entri yang cocok dengan query
    search_results = list(collection.find({'text': {'$regex': search_query, '$options': 'i'}}))
    return render_template('search.html', search_query=search_query, search_results=search_results)

@app.route('/delete/<entry_id>', methods=['POST'])
def delete_entry(entry_id):
    # Delete entry from MongoDB
    collection.delete_one({'_id': entry_id})
    return redirect(url_for('history'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='2363', debug=True)
