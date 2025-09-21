# Etapa 1: Construir la imagen para Gunicorn + Python
FROM python:3.11-slim as base

# Instalar dependencias del sistema necesarias para Nginx y Gunicorn
RUN apt-get update && apt-get install -y \
    nginx \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Crear el usuario nginx (si es necesario)
RUN adduser --system --no-create-home --disabled-login nginx

# Crear un directorio de trabajo
WORKDIR /app

# Copiar los archivos de la aplicación
COPY . /app

# Instalar las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Etapa 2: Configurar Nginx
# Copiar la configuración de Nginx al contenedor
COPY nginx.conf /etc/nginx/nginx.conf

# Copiar los certificados al contenedor
COPY ./certificates/server.crt /etc/ssl/certs/server.crt
COPY ./certificates/server.key /etc/ssl/private/server.key
COPY ./certificates/ca.crt /etc/ssl/certs/ca.crt

# Exponer los puertos necesarios
EXPOSE 80 443

# Etapa 3: Ejecutar Gunicorn y Nginx
# Crear un script para iniciar Gunicorn y Nginx juntos
COPY start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]

