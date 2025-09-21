# Gestión de Finanzas Personales

Una aplicación web Flask para la gestión y seguimiento de finanzas personales con funcionalidades de dashboard, gráficos interactivos y análisis de flujo de ingresos y gastos.

## 🚀 Características

- **Gestión de Cuentas**: Agregar y administrar diferentes tipos de cuentas (remunerada, indexado, normal, efectivo)
- **Registro de Movimientos**: Registrar ingresos y gastos por cuenta
- **Dashboard Interactivo**: Visualización de saldos con gráficos circulares y de barras apiladas
- **Análisis de Flujo**: Diagrama Sankey para visualizar ingresos y gastos
- **Historial Completo**: Seguimiento de todos los movimientos financieros
- **Captura de Saldos**: Exportación de saldos a CSV con fecha
- **Despliegue Seguro**: Configuración con HTTPS y mTLS usando Nginx

## 📋 Tecnologías

- **Backend**: Flask (Python)
- **Base de Datos**: SQLite
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 4
- **Gráficos**: Chart.js, Google Charts (Sankey)
- **Servidor Web**: Nginx con Gunicorn
- **Contenedores**: Docker
- **Seguridad**: Certificados SSL/TLS para mTLS

## 🛠️ Instalación y Configuración

### Prerequisitos

- Python 3.11+
- Docker (opcional)
- OpenSSL (para certificados)

### Instalación Local

1. **Clona el repositorio**
```bash
git clone https://github.com/joseajrgr/finzanzas-personales
cd finzanzas-personales
```

2. **Instala las dependencias**
```bash
pip install -r requirements.txt
```

3. **Ejecuta la aplicación**
```bash
python app.py
```

4. **Accede a la aplicación**
   - Navegador: `http://localhost:5000`

### Instalación con Docker

1. **Construye la imagen**
```bash
docker build -t finanzas-app .
```

2. **Ejecuta el contenedor**
```bash
docker run -p 80:80 -p 443:443 finanzas-app
```

3. **Accede con HTTPS**
   - Navegador: `https://localhost` (requiere certificado cliente)


## 🎯 Funcionalidades Principales

### 1. Gestión de Cuentas
- Agregar nuevas cuentas con tipos específicos
- Definir saldo inicial
- Visualización organizada por tipo de cuenta

### 2. Registro de Movimientos
- Ingresos y gastos por cuenta
- Actualización automática de saldos
- Registro con fecha automática

### 3. Dashboard Analítico
- **Gráfico Circular**: Distribución de saldos por cuenta
- **Gráfico de Barras Apiladas**: Progresión temporal de saldos
- **Resumen Total**: Suma de todos los saldos

### 4. Análisis de Flujo (Sankey)
- Visualización de ingresos y gastos
- Diagrama interactivo de flujo de dinero
- Gestión dinámica de datos

### 5. Captura de Saldos
- Exportación automática a CSV
- Archivos con fecha para seguimiento histórico
- Función AJAX para captura sin recargar página

## 🔧 Configuración de Seguridad

### Certificados SSL/TLS

La aplicación incluye configuración para mTLS (mutual TLS) con:

- **CA Certificate**: [`certificates/ca.crt`](certificates/ca.crt)
- **Server Certificate**: [`certificates/server.crt`](certificates/server.crt)
- **Server Private Key**: [`certificates/server.key`](certificates/server.key)

### Nginx Configuration

El archivo [`nginx.conf`](nginx.conf) configura:
- HTTPS en puerto 443
- Verificación de certificado cliente
- Proxy reverso a Gunicorn (puerto 8000)


## 🌐 API Endpoints

- `GET /` - Página principal
- `GET/POST /agregar_cuenta` - Gestión de cuentas
- `GET/POST /registrar_movimiento` - Registro de movimientos
- `GET /dashboard` - Dashboard con gráficos
- `GET /historial` - Historial de movimientos
- `GET /ingresos_gastos` - Análisis de flujo
- `POST /capturar_saldo` - Exportar saldos a CSV
- `POST /agregar` - Agregar dato a análisis flujo
- `POST /limpiar` - Limpiar datos análisis flujo

## 🔄 Scripts Automatizados

### [`start.sh`](start.sh)
Script para iniciar Gunicorn y Nginx simultáneamente:
```bash
#!/bin/bash
gunicorn --bind 127.0.0.1:8000 --access-logfile - --error-logfile - app:app &
nginx -g "daemon off;"
```


## 🚀 Despliegue en Producción

### Con Docker
```bash
# Construir imagen
docker build -t finanzas-app .

# Ejecutar con volúmenes para persistencia
docker run -d \
  -p 443:443 \
  -v $(pwd)/finanzas.db:/app/finanzas.db \
  -v $(pwd)/captura_saldo_*.csv:/app/ \
  finanzas-app
```
