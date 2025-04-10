FROM debian:bullseye

# Instalar dependencias del sistema
RUN apt update && apt install -y \
    build-essential cmake curl ffmpeg libsndfile1 python3 python3-pip git

# Clonar whisper.cpp y compilar
RUN git clone https://github.com/ggml-org/whisper.cpp /app
WORKDIR /app
RUN make

# Descargar el modelo base (puedes cambiarlo por otro si quieres multilingüe)
RUN mkdir -p models && curl -L -o models/ggml-base.en.bin https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin

# Instalar dependencias de Python
RUN pip3 install flask pydub

# Copiar el servidor Flask al mismo directorio que `main`
COPY server.py /app/server.py

# Exponer el puerto Flask
EXPOSE 5000

# Ejecutar la API
CMD ["python3", "server.py"]

