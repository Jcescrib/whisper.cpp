from flask import Flask, request, jsonify
import subprocess
import os
import uuid

app = Flask(__name__)

@app.route('/transcribe', methods=['POST'])
def transcribe():
    # Verificar si el archivo 'data' está en la solicitud
    if 'data' not in request.files:
        return jsonify({"error": "No se encontró el archivo en la solicitud."}), 400

    audio = request.files['data']

    # Verificar si el archivo tiene un nombre válido
    if audio.filename == '':
        return jsonify({"error": "Nombre de archivo no válido."}), 400

    # Crear un nombre de archivo único en el directorio temporal
    filename = f"/tmp/{uuid.uuid4()}.wav"
    audio.save(filename)

    # Ejecutar whisper.cpp
    command = f"./main -m models/ggml-base.en.bin -f {filename} -otxt -l es"
    try:
        subprocess.run(command.split(), check=True)
    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Error al ejecutar whisper.cpp: {str(e)}"}), 500

    # Leer el resultado
    txt_file = filename.replace(".wav", ".txt")
    try:
        with open(txt_file, "r") as f:
            result = f.read()
    except FileNotFoundError:
        return jsonify({"error": "No se encontró el archivo de transcripción."}), 500

    # Eliminar archivos temporales
    os.remove(filename)
    os.remove(txt_file)

    return jsonify({"text": result})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
