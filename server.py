from flask import Flask, request, jsonify
import subprocess
import os
import uuid
from pydub import AudioSegment

app = Flask(__name__)

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'data' not in request.files:
        return jsonify({"error": "No se encontró el archivo en la solicitud."}), 400

    audio = request.files['data']
    ext = audio.filename.split('.')[-1]
    input_path = f"/tmp/{uuid.uuid4()}.{ext}"
    output_path = input_path.replace(f".{ext}", ".wav")

    # Guardar archivo recibido
    audio.save(input_path)

    try:
        # Convertir a WAV usando pydub + ffmpeg
        sound = AudioSegment.from_file(input_path)
        sound.export(output_path, format="wav")
    except Exception as e:
        return jsonify({"error": f"Error al convertir audio: {str(e)}"}), 500

    # Ejecutar Whisper.cpp
    command = f"./main -m models/ggml-base.en.bin -f {output_path} -otxt -l es"
    try:
        subprocess.run(command.split(), check=True)
    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Error al ejecutar whisper.cpp: {str(e)}"}), 500

    txt_file = output_path.replace(".wav", ".txt")
    try:
        with open(txt_file, "r") as f:
            result = f.read()
    except FileNotFoundError:
        return jsonify({"error": "No se encontró el archivo de transcripción."}), 500

    # Limpiar archivos temporales
    for f in [input_path, output_path, txt_file]:
        try: os.remove(f)
        except: pass

    return jsonify({"text": result})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
