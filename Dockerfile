FROM debian:bullseye

# Instalar dependencias del sistema
RUN apt update && apt install -y \
    build-essential cmake curl ffmpeg libsndfile1 python3 python3-pip git

# Clonar whisper.cpp y compilar
RUN git clone https://github.com/ggml-org/whisper.cpp /app
WORKDIR /app
RUN make
RUN chmod +x main

# Descargar el modelo base
RUN mkdir -p models && curl -L -o models/ggml-base.en.bin https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin

# Instalar Python y librerías
RUN pip3 install flask pydub

# Copiar el servidor Flask
COPY server.py /app/server.py

# Garantizar que todo corre desde /app
WORKDIR /app

# Exponer el puerto
EXPOSE 5000

# Ejecutar
CMD ["python3", "server.py"]
