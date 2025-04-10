FROM debian:bullseye

# Instalar dependencias necesarias
RUN apt update && apt install -y \
  build-essential cmake curl ffmpeg libsndfile1 python3 python3-pip git

# Clonar whisper.cpp y compilar
RUN git clone https://github.com/ggml-org/whisper.cpp /app
WORKDIR /app
RUN make && chmod +x main  # 👈 Ejecuta chmod solo si main existe

# Descargar modelo base
RUN mkdir -p models && curl -L -o models/ggml-base.en.bin https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin

# Instalar Flask y Pydub
RUN pip3 install flask pydub

# Copiar servidor
COPY server.py /app/server.py

# Establecer el directorio de trabajo
WORKDIR /app

# Exponer el puerto de Flask
EXPOSE 5000

# Ejecutar el servidor
CMD ["python3", "server.py"]
