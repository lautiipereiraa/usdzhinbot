# Usa una imagen liviana de Python
FROM python:3.11-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia solo lo necesario
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de la app
COPY . .

# Asegura que .env no sea accidentalmente expuesto
RUN rm -f .env

# Comando para iniciar el bot
CMD ["python", "bot.py"]
