# Usar la imagen oficial de Python
FROM python:3.11-slim

# Directorio de trabajo en el contenedor
WORKDIR /app

# Copiar archivos necesarios
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Exponer puerto
EXPOSE 5000

# Comando para ejecutar la app
CMD ["python", "app.py"]

