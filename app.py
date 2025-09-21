from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from datetime import datetime
import pandas as pd
import csv, os, glob, sqlite3

app = Flask(__name__)
app.secret_key = 'cambia-esto-por-una-clave-secreta-segura'

# Conectar a la base de datos
def conectar_bd():
    conn = sqlite3.connect("finanzas.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cuentas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE,
            tipo TEXT,
            saldo REAL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            cuenta_id INTEGER,
            tipo TEXT,
            monto REAL,
            FOREIGN KEY(cuenta_id) REFERENCES cuentas(id)
        )
    ''')
    
    conn.commit()
    return conn, cursor

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/agregar_cuenta', methods=['GET', 'POST'])
def agregar_cuenta():
    if request.method == 'POST':
        nombre = request.form['nombre']
        tipo = request.form['tipo']
        saldo_inicial = request.form['saldo_inicial']
        
        if not nombre or not tipo or not saldo_inicial:
            return "Todos los campos son obligatorios.", 400
        
        try:
            saldo_inicial = float(saldo_inicial)
        except ValueError:
            flash('El saldo inicial debe ser un número válido.', 'danger')
            return redirect(url_for('agregar_cuenta'))
        
        conn, cursor = conectar_bd()
        try:
            cursor.execute("INSERT INTO cuentas (nombre, tipo, saldo) VALUES (?, ?, ?)", (nombre, tipo, saldo_inicial))
            conn.commit()
        except sqlite3.IntegrityError:
            flash('Ya existe una cuenta con ese nombre.', 'danger')
            return redirect(url_for('agregar_cuenta'))
        finally:
            conn.close()
        
        return redirect(url_for('index'))
    
    return render_template('agregar_cuenta.html')

@app.route('/registrar_movimiento', methods=['GET', 'POST'])
def registrar_movimiento():
    conn, cursor = conectar_bd()
    cursor.execute("SELECT nombre FROM cuentas")
    cuentas = cursor.fetchall()
    conn.close()
    
    if request.method == 'POST':
        cuenta = request.form['cuenta']
        tipo = request.form['tipo']
        monto = request.form['monto']
        
        if not cuenta or not tipo or not monto:
            return "Todos los campos son obligatorios.", 400
        
        try:
            monto = float(monto)
        except ValueError:
            flash('El monto debe ser un número válido.', 'danger')
            return redirect(url_for('registrar_movimiento'))
        
        fecha = datetime.today().strftime('%Y-%m-%d')
        conn, cursor = conectar_bd()
        cursor.execute("SELECT id, saldo FROM cuentas WHERE nombre = ?", (cuenta,))
        cuenta_data = cursor.fetchone()
        
        if cuenta_data:
            cuenta_id, saldo_actual = cuenta_data
            nuevo_saldo = saldo_actual + monto if tipo == "ingreso" else saldo_actual - monto
            
            cursor.execute("INSERT INTO movimientos (fecha, cuenta_id, tipo, monto) VALUES (?, ?, ?, ?)", (fecha, cuenta_id, tipo, monto))
            cursor.execute("UPDATE cuentas SET saldo = ? WHERE id = ?", (nuevo_saldo, cuenta_id))
            conn.commit()
        else:
            flash('Cuenta no encontrada.', 'danger')
            return redirect(url_for('registrar_movimiento'))
        conn.close()
        
        return redirect(url_for('index'))
    
    return render_template('registrar_movimiento.html', cuentas=cuentas)

@app.route('/dashboard')
def dashboard():
    conn, cursor = conectar_bd()
    cursor.execute("SELECT tipo, nombre, saldo FROM cuentas ORDER BY tipo, nombre")
    cuentas = cursor.fetchall()
    
    total_saldo = sum(float(cuenta[2]) for cuenta in cuentas)
    
    cursor.execute('''
        SELECT strftime('%Y-%m', fecha) as mes, cuentas.nombre, movimientos.tipo, movimientos.monto 
        FROM movimientos 
        JOIN cuentas ON movimientos.cuenta_id = cuentas.id
        ORDER BY fecha
    ''')
    movimientos = cursor.fetchall()
    conn.close()
    
    meses = sorted(set([row[0] for row in movimientos]))
    cuentas_nombres = sorted(set([row[1] for row in movimientos]))
    saldos_por_mes = {mes: {cuenta: 0 for cuenta in cuentas_nombres} for mes in meses}
    
    saldo_acumulado = {cuenta: 0 for cuenta in cuentas_nombres}
    for mes in meses:
        for movimiento in movimientos:
            if movimiento[0] == mes:
                cuenta = movimiento[1]
                tipo = movimiento[2]
                monto = float(movimiento[3])
                if tipo == "ingreso":
                    saldo_acumulado[cuenta] += monto
                else:
                    saldo_acumulado[cuenta] -= monto
            saldos_por_mes[mes][cuenta] = saldo_acumulado[cuenta]
    
    colores = ['blue', 'green', 'red', 'purple']
    datasets = [{'label': cuenta, 'color': colores[i % len(colores)], 'data': [saldos_por_mes[mes][cuenta] for mes in meses]} for i, cuenta in enumerate(cuentas_nombres)]
    
    cuentas_por_tipo = {}
    for tipo, nombre, saldo in cuentas:
        if tipo not in cuentas_por_tipo:
            cuentas_por_tipo[tipo] = []
        cuentas_por_tipo[tipo].append((nombre, float(saldo)))
    
    cuentas_data = [(cuenta[1], float(cuenta[2])) for cuenta in cuentas]
    
    datos_csv = leer_csvs()
    
    return render_template('dashboard.html', cuentas_por_tipo=cuentas_por_tipo, meses=meses, datasets=datasets, total_saldo=total_saldo, cuentas=cuentas_data, datos_csv=datos_csv)




CSV_FILE = "ingresos_gastos.csv"

# Cargar datos del CSV al iniciar
def cargar_datos():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        return df.to_dict(orient="records")  # Lista de diccionarios [{...}, {...}]
    return []

# Guardar datos en el CSV
def guardar_datos(datos):
    df = pd.DataFrame(datos)
    df.to_csv(CSV_FILE, index=False)

@app.route('/ingresos_gastos')
def ingresos_gastos():
    datos = cargar_datos()
    return render_template("ingresos_gastos.html", datos=datos)

@app.route('/agregar', methods=['POST'])
def agregar():
    nuevo_dato = request.json  # Recibe datos en formato JSON
    datos = cargar_datos()
    datos.append(nuevo_dato)
    guardar_datos(datos)
    return jsonify({"success": True})

@app.route('/limpiar', methods=['POST'])
def limpiar():
    if os.path.exists(CSV_FILE):
        os.remove(CSV_FILE)
    return jsonify({"success": True})

@app.route('/historial')
def historial():
    conn, cursor = conectar_bd()
    cursor.execute('''
        SELECT movimientos.fecha, cuentas.nombre, movimientos.tipo, movimientos.monto 
        FROM movimientos 
        JOIN cuentas ON movimientos.cuenta_id = cuentas.id
        ORDER BY movimientos.fecha DESC
    ''')
    movimientos = cursor.fetchall()
    conn.close()
    
    return render_template('historial.html', movimientos=movimientos)



@app.route('/capturar_saldo', methods=['POST'])
def capturar_saldo():
    conn, cursor = conectar_bd()
    cursor.execute("SELECT nombre, saldo FROM cuentas")
    cuentas = cursor.fetchall()
    conn.close()

    fecha = datetime.today().strftime('%Y-%m-%d')
    nombre_archivo = f"captura_saldo_{fecha}.csv"

    with open(nombre_archivo, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Nombre de la Cuenta", "Saldo"])
        for cuenta in cuentas:
            writer.writerow(cuenta)

    return jsonify({"mensaje": "Saldo capturado y guardado en CSV con éxito."})



def leer_csvs():
    archivos_csv = glob.glob("captura_saldo_*.csv")
    datos_csv = {}

    for archivo in archivos_csv:
        with open(archivo, mode='r') as file:
            reader = csv.reader(file)
            next(reader)  # Saltar la cabecera
            fecha = archivo.split('_')[-1].split('.')[0]

            for row in reader:
                cuenta, saldo = row[0], float(row[1])
                if fecha not in datos_csv:
                    datos_csv[fecha] = {}
                datos_csv[fecha][cuenta] = saldo

    fechas = sorted(datos_csv.keys())  # Ordenar las fechas
    cuentas = sorted(set(c for f in datos_csv.values() for c in f))  # Obtener todas las cuentas únicas
    datos_procesados = {
        "fechas": fechas,
        "cuentas": cuentas,
        "saldos": [[datos_csv[fecha].get(cuenta, 0) for cuenta in cuentas] for fecha in fechas],
    }

    return datos_procesados


if __name__ == '__main__':
    app.run(debug=True)