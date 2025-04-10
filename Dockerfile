FROM debian:bullseye

RUN apt update && apt install -y \
    build-essential cmake curl ffmpeg libsndfile1 python3 python3-pip git

# Clonar y compilar whisper.cpp
RUN git clone https://github.com/ggml-org/whisper.cpp /app
WORKDIR /app
RUN make

# Descargar modelo base (solo inglés; puedes cambiarlo por multilingüe si prefieres)
RUN mkdir -p models && curl -L -o models/ggml-base.en.bin https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin

# Instala Flask
RUN pip3 install flask

COPY server.py .

EXPOSE 5000
CMD ["python3", "server.py"]
