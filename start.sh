#!/bin/bash

# Iniciar Gunicorn
gunicorn --bind 127.0.0.1:8000 --access-logfile - --error-logfile - app:app &

# Iniciar Nginx
nginx -g "daemon off;"


