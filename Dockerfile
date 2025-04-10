FROM debian:bullseye

# Instalar dependencias necesarias
RUN apt update && apt install -y \
    build-essential cmake curl ffmpeg libsndfile1 python3 python3-pip git

# Clonar y compilar whisper.cpp
RUN git clone https://github.com/ggml-org/whisper.cpp /app
WORKDIR /app
RUN make

# Descargar el modelo Whisper
RUN mkdir -p models && curl -L -o models/ggml-base.en.bin https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin

# Instalar Flask y Pydub
RUN pip3 install flask pydub

# 👇 COPIAR EL server.py AL DIRECTORIO DONDE ESTÁ `main`
COPY server.py /app/server.py

# Exponer el puerto y arrancar
EXPOSE 5000
CMD ["python3", "server.py"]
