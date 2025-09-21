import pytest
from app import app, conectar_bd
import os
import tempfile
import sqlite3

@pytest.fixture
def client():
    # Usar una base de datos temporal para pruebas
    db_fd, db_path = tempfile.mkstemp()
    app.config['TESTING'] = True
    app.config['DATABASE'] = db_path
    app.config['WTF_CSRF_ENABLED'] = False

    # Parchear conectar_bd para usar la base temporal
    def _conectar_bd():
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS cuentas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE,
            tipo TEXT,
            saldo REAL
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS movimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            cuenta_id INTEGER,
            tipo TEXT,
            monto REAL,
            FOREIGN KEY(cuenta_id) REFERENCES cuentas(id)
        )''')
        conn.commit()
        return conn, cursor
    app.conectar_bd = _conectar_bd

    with app.test_client() as client:
        yield client
    os.close(db_fd)
    os.unlink(db_path)

def test_index(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'finanzas' in resp.data.lower()

def test_dashboard_empty(client):
    resp = client.get('/dashboard')
    assert resp.status_code == 200
    assert b'saldos actuales' in resp.data.lower()

def test_agregar_cuenta_get(client):
    resp = client.get('/agregar_cuenta')
    assert resp.status_code == 200
    assert b'agregar cuenta' in resp.data.lower()

def test_agregar_cuenta_post(client):
    resp = client.post('/agregar_cuenta', data={
        'nombre': 'TestCuenta',
        'tipo': 'normal',
        'saldo_inicial': '100.5'
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b'inicio' in resp.data.lower() or b'dashboard' in resp.data.lower()

def test_agregar_cuenta_post_invalid(client):
    resp = client.post('/agregar_cuenta', data={
        'nombre': '',
        'tipo': '',
        'saldo_inicial': ''
    })
    assert resp.status_code == 400
    assert b'todos los campos son obligatorios' in resp.data.lower()

def test_registrar_movimiento_get(client):
    # Primero agrega una cuenta
    client.post('/agregar_cuenta', data={
        'nombre': 'TestCuenta',
        'tipo': 'normal',
        'saldo_inicial': '100.5'
    })
    resp = client.get('/registrar_movimiento')
    assert resp.status_code == 200
    assert b'cuenta' in resp.data.lower()

def test_registrar_movimiento_post(client):
    # Agrega una cuenta
    client.post('/agregar_cuenta', data={
        'nombre': 'TestCuenta',
        'tipo': 'normal',
        'saldo_inicial': '100.5'
    })
    # Registra movimiento
    resp = client.post('/registrar_movimiento', data={
        'cuenta': 'TestCuenta',
        'tipo': 'Ingreso',
        'monto': '50'
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b'inicio' in resp.data.lower() or b'dashboard' in resp.data.lower()

def test_registrar_movimiento_post_invalid(client):
    resp = client.post('/registrar_movimiento', data={
        'cuenta': '',
        'tipo': '',
        'monto': ''
    })
    assert resp.status_code == 400
    assert b'todos los campos son obligatorios' in resp.data.lower()

def test_ingresos_gastos(client):
    resp = client.get('/ingresos_gastos')
    assert resp.status_code == 200
    assert b'datos' in resp.data.lower() or b'ingresos' in resp.data.lower()

def test_limpiar(client):
    resp = client.post('/limpiar')
    assert resp.status_code == 200
    assert b'success' in resp.data.lower()
