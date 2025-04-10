from flask import Flask, request, jsonify
import subprocess
import os
import uuid

app = Flask(__name__)

@app.route('/transcribe', methods=['POST'])
def transcribe():
    audio = request.files['data']
    filename = f"/tmp/{uuid.uuid4()}.wav"
    audio.save(filename)

    # Ejecuta whisper.cpp
    command = f"./main -m models/ggml-base.en.bin -f {filename} -otxt -l es"
    subprocess.run(command.split(), check=True)

    # Lee resultado
    txt_file = filename.replace(".wav", ".txt")
    try:
        with open(txt_file, "r") as f:
            result = f.read()
    except FileNotFoundError:
        result = "ERROR: No transcription file found."

    return jsonify({"text": result})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
