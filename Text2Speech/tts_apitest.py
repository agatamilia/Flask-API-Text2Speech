from flask import Flask, request, redirect, url_for, jsonify
from pymongo import MongoClient
from gtts import gTTS
from datetime import datetime
import pymongo
from io import BytesIO
from bson import ObjectId

app = Flask(__name__)

client = MongoClient("mongodb://localhost:27017")
db = client['TTS']
collection = db['tts_history']


@app.route('/convert', methods=['POST'])
def convert():
    try:
        data = request.json
        text = data['text']
        lang = data['voice']
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

        return jsonify({'message': 'Conversion successful', 'entry_id': entry_id})
    except KeyError:
        return jsonify({'error': 'Missing parameter "text" or "voice"', '"status"' : '404'})


@app.route('/history', methods=['GET'])
def get_history():
    history_data = list(collection.find().sort('updated_at', pymongo.DESCENDING))
    formatted_history = []
    for entry in history_data:
        formatted_entry = {
            'entry_id': entry['_id'],
            'text': entry['text'],
            'language': entry['language'],
            'created_at': entry['created_at'],
            'updated_at': entry['updated_at']
        }
        formatted_history.append(formatted_entry)
    return jsonify({'history': formatted_history})



@app.route('/edit/<entry_id>', methods=['PUT'])
def update_entry(entry_id):
    lang = request.json['voice']
    
    entry = collection.find_one({'_id': entry_id})
    text = entry['text']
    
    tts = gTTS(text=text, lang=lang)
    
    audio_data = BytesIO()
    tts.write_to_fp(audio_data)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    update_result = collection.update_one({'_id': entry_id}, {'$set': {'audio_data': audio_data.getvalue(), 'language': lang, 'updated_at': timestamp}})
    
    if update_result.matched_count > 0:
        if update_result.modified_count > 0:
            entry_data = {
                'entry_id': entry_id,
                'text': text,
                'language': lang,
                'created_at': entry['created_at'],
                'updated_at': timestamp
            }
            return jsonify({'message': 'Entry updated successfully', 'entry': entry_data})
        else:
            return jsonify({'message': 'No changes were made. Entry already up to date.'}), 200 
    else:
        return jsonify({'error': 'Entry not found'}), 404



@app.route('/delete/<entry_id>', methods=['DELETE'])
def delete_entry(entry_id):
    if request.method == 'DELETE':
        entry = collection.find_one({'_id': entry_id})
        if entry:
            text = entry['text']
            lang = entry['language']
            collection.delete_one({'_id': entry_id})
            entry_data = {
                'entry_id': entry_id,
                'text': text,
                'language': lang
            }
            return jsonify({'message': 'Entry deleted successfully', 'entry': entry_data}),200
        else:
            return jsonify({'error': 'Entry not found'}), 404



@app.route('/search', methods=[ 'GET'])
def search():
    if request.method == 'GET':
        try:
            search_query = request.json.get('search_query', '')
            search_results = list(collection.find({'text': {'$regex': f'.*{search_query}.*', '$options': 'i'}}))
            if search_results:
                return jsonify({'search_query': search_query, 'search_results': search_results}), 200
            else:
                return jsonify({'message': 'No results found for the search query'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Entry not found'}), 404
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port='5000', debug=True)
