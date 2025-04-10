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
        # ----------------------------
        # 0. Validar que main existe
        # ----------------------------
        if not os.path.isfile(WHISPER_MAIN):
            print(f"[ERROR] Ejecutable no encontrado en: {WHISPER_MAIN}")
            return jsonify({"error": "No se encontró el ejecutable 'main'"}), 500

        # ----------------------------
        # 1. Capturar archivo binario
        # ----------------------------
        input_bytes = None
        filename = f"/tmp/{uuid.uuid4()}.oga"

        if 'data' in request.files:
            file = request.files['data']
            file.save(filename)
            print("[INFO] Archivo recibido como multipart")
        else:
            input_bytes = request.get_data()
            if not input_bytes:
                return jsonify({"error": "No se recibió ningún archivo."}), 400
            with open(filename, "wb") as f:
                f.write(input_bytes)
            print("[INFO] Archivo recibido desde raw body")

        # ----------------------------
        # 2. Convertir a WAV
        # ----------------------------
        output_path = filename.replace(".oga", ".wav")
        txt_file = output_path.replace(".wav", ".txt")

        try:
            sound = AudioSegment.from_file(filename)
            sound.export(output_path, format="wav")
            print(f"[INFO] Convertido a WAV: {output_path}")
        except Exception as e:
            return jsonify({"error": f"Error al convertir a WAV: {str(e)}"}), 500

        # ----------------------------
        # 3. Ejecutar Whisper
        # ----------------------------
        try:
            command = f"{WHISPER_MAIN} -m {WHISPER_MODEL} -f {output_path} -otxt -l es"
            print(f"[INFO] Ejecutando Whisper: {command}")
            subprocess.run(command.split(), check=True)
        except subprocess.CalledProcessError as e:
            return jsonify({"error": f"Whisper falló: {str(e)}"}), 500

        # ----------------------------
        # 4. Leer transcripción
        # ----------------------------
        try:
            with open(txt_file, "r") as f:
                result = f.read()
        except FileNotFoundError:
            return jsonify({"error": "No se generó archivo de texto"}), 500

        # ----------------------------
        # 5. Limpieza
        # ----------------------------
        for f in [filename, output_path, txt_file]:
            try:
                os.remove(f)
            except Exception as e:
                print(f"[WARN] No se pudo borrar {f}: {str(e)}")

        return jsonify({"text": result})

    except Exception as e:
        return jsonify({"error": f"Error inesperado del servidor: {str(e)}"}), 500

# Ejecutar servidor Flask
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
