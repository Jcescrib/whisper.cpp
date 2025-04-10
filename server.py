from flask import Flask, request, jsonify
import subprocess
import os
import uuid
from pydub import AudioSegment

app = Flask(__name__)

# Rutas absolutas
WHISPER_DIR = "/app"
WHISPER_MAIN = os.path.join(WHISPER_DIR, "main")
WHISPER_MODEL = os.path.join(WHISPER_DIR, "models", "ggml-base.en.bin")

@app.route('/transcribe', methods=['POST'])
def transcribe():
    try:
        # 1. Verifica si se recibió el archivo binario
        if 'data' not in request.files:
            return jsonify({"error": "Archivo binario 'data' no fue enviado"}), 400

        audio = request.files['data']

        # 2. Verifica si el archivo tiene nombre válido
        if not audio.filename or audio.filename.strip() == '':
            return jsonify({"error": "Archivo sin nombre o vacío"}), 401

        # 3. Verifica formato soportado
        ext = audio.filename.split('.')[-1].lower()
        if ext not in ['oga', 'ogg', 'mp3', 'm4a', 'wav']:
            return jsonify({"error": f"Formato de archivo '{ext}' no soportado"}), 501

        # 4. Rutas de entrada/salida
        input_path = f"/tmp/{uuid.uuid4()}.{ext}"
        output_path = input_path.replace(f".{ext}", ".wav")
        txt_file = output_path.replace(".wav", ".txt")

        # 5. Guarda el archivo temporal
        print(f"[INFO] Guardando archivo original en: {input_path}")
        audio.save(input_path)

        # 6. Convierte el audio a formato WAV
        try:
            print(f"[INFO] Convirtiendo a WAV: {output_path}")
            sound = AudioSegment.from_file(input_path)
            sound.export(output_path, format="wav")
        except Exception as e:
            return jsonify({"error": f"No se pudo convertir a WAV: {str(e)}"}), 500

        # 7. Ejecuta whisper.cpp
        try:
            command = f"{WHISPER_MAIN} -m {WHISPER_MODEL} -f {output_path} -otxt -l es"
            print(f"[INFO] Ejecutando: {command}")
            subprocess.run(command.split(), check=True)
        except subprocess.CalledProcessError as e:
            return jsonify({"error": f"Whisper falló al ejecutar: {str(e)}"}), 500
        except FileNotFoundError as e:
            return jsonify({"error": f"Archivo ejecutable no encontrado: {str(e)}"}), 500

        # 8. Lee el archivo generado por whisper
        try:
            with open(txt_file, "r") as f:
                result = f.read()
        except FileNotFoundError:
            return jsonify({"error": "No se generó el archivo de texto"}), 500

        # 9. Limpieza de archivos temporales
        for f in [input_path, output_path, txt_file]:
            try:
                os.remove(f)
            except Exception as e:
                print(f"[WARN] No se pudo borrar {f}: {str(e)}")

        # 10. Éxito
        return jsonify({"text": result})

    except Exception as e:
        return jsonify({"error": f"Error inesperado del servidor: {str(e)}"}), 500

# Ejecutar el servidor
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
