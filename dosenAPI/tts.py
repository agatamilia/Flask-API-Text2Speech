from flask import Flask, render_template, request, jsonify
from gtts import gTTS
import os
from datetime import datetime
import mysql.connector

app = Flask(__name__)

# Konfigurasi database MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="universitas"
)
cursor = db.cursor()

# Periksa koneksi database
if db.is_connected():
    print("Connected to MySQL database")

# Tambahkan kode untuk membuat tabel jika belum ada
cursor.execute("""
CREATE TABLE IF NOT EXISTS tts_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    text TEXT,
    timestamp DATETIME,
    audio_path VARCHAR(255)
)
""")

@app.route('/')
def index():
    return render_template('convert.html')

@app.route('/history', methods=['GET'])
def history():
    cursor.execute("SELECT * FROM tts_history")
    data = cursor.fetchall()
    return render_template('history.html', history=data)

@app.route('/convert', methods=['POST'])
def convert_text_to_speech():
    text = request.form['text']
    timestamp = datetime.now().strftime("%Y-%m-%d")
    audio_path = f"static/history/speech_{timestamp}.mp3"

    # Konversi teks ke suara menggunakan gTTS
    tts = gTTS(text=text, lang='en')
    tts.save(audio_path)
    
    # Simpan data ke database
    cursor.execute("INSERT INTO tts_history (text, timestamp, audio_path) VALUES (%s, %s, %s)", (text, timestamp, audio_path))
    db.commit()  # Komit transaksi

    return render_template('convert.html', audio_path=audio_path)

if __name__ == "__main__":
    app.run(debug=True)
