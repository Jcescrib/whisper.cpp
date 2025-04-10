FROM debian:bullseye

# Instalar dependencias
RUN apt update && apt install -y \
  build-essential cmake curl ffmpeg libsndfile1 python3 python3-pip git

# Clonar y compilar whisper.cpp
RUN git clone https://github.com/ggml-org/whisper.cpp /app
WORKDIR /app
RUN make

# Descargar modelo base (puedes cambiar por multilingüe si quieres)
RUN mkdir -p models && curl -L -o models/ggml-base.en.bin https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin

# Instalar Flask y Pydub
RUN pip3 install flask pydub

# Copiar tu servidor al directorio correcto
COPY server.py /app/server.py

# Garantizar que el CMD se ejecute desde /app
WORKDIR /app

# Exponer el puerto de Flask
EXPOSE 5000

# Ejecutar el servidor
CMD ["python3", "server.py"]
