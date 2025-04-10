from flask import Flask, request, jsonify
import subprocess
import os
import uuid
from pydub import AudioSegment

app = Flask(__name__)

@app.route('/transcribe', methods=['POST'])
def transcribe():
    try:
        # Archivo no enviado
        if 'data' not in request.files:
            return jsonify({"error": "Archivo binario 'data' no fue enviado"}), 400

        audio = request.files['data']

        # Archivo vacío o sin nombre válido
        if not audio.filename or audio.filename == '':
            return jsonify({"error": "Archivo sin nombre o vacío"}), 401

        # Validar formato
        ext = audio.filename.split('.')[-1].lower()
        if ext not in ['oga', 'ogg', 'mp3', 'm4a', 'wav']:
            return jsonify({"error": f"Formato de archivo '{ext}' no soportado"}), 501

        # Guardar archivo recibido
        input_path = f"/tmp/{uuid.uuid4()}.{ext}"
        output_path = input_path.replace(f".{ext}", ".wav")
        audio.save(input_path)
        print(f"[INFO] Archivo recibido y guardado en {input_path}")

        # Simular progreso (informativo, no real para HTTP)
        print("[INFO] Procesando audio...")  # Simula código 102 (no se puede usar en respuesta final)

        # Convertir a WAV
        try:
            sound = AudioSegment.from_file(input_path)
            sound.export(output_path, format="wav")
        except Exception as e:
            return jsonify({"error": f"No se pudo convertir a WAV: {str(e)}"}), 500

        # Ejecutar whisper.cpp
        try:
            command = f"./main -m models/ggml-base.en.bin -f {output_path} -otxt -l es"
            print(f"[INFO] Ejecutando: {command}")
            subprocess.run(command.split(), check=True)
        except subprocess.CalledProcessError as e:
            return jsonify({"error": f"Error en whisper.cpp: {str(e)}"}), 500

        # Leer resultado
        txt_file = output_path.replace(".wav", ".txt")
        try:
            with open(txt_file, "r") as f:
                result = f.read()
        except FileNotFoundError:
            return jsonify({"error": "Whisper no generó el archivo de texto"}), 500

        # Limpiar archivos
        for f in [input_path, output_path, txt_file]:
            try:
                os.remove(f)
            except:
                pass

        return jsonify({"text": result})

    except Exception as e:
        return jsonify({"error": f"Error inesperado del servidor: {str(e)}"}), 500

# Ejecutar el servidor
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
