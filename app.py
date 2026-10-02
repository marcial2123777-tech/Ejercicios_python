from flask import Flask, render_template, request, jsonify, redirect
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
import os

# ==========================================
# CARGAR VARIABLES DEL ARCHIVO .ENV
# ==========================================

load_dotenv()

app = Flask(__name__)


# ==========================================
# CONEXIÓN CON MONGODB ATLAS
# ==========================================

MONGO_URI = os.getenv("MONGO_URI")

cliente = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=10000
)

db = cliente["ejercicios_python"]

coleccion_par_impar = db["par_impar"]


# ==========================================
# COMPROBAR CONEXIÓN
# ==========================================

try:
    cliente.admin.command("ping")
    print("✅ CONECTADO A MONGODB ATLAS")

except Exception as e:
    print("❌ ERROR DE MONGODB:", e)


# ==========================================
# PÁGINA PRINCIPAL
# ==========================================

@app.route("/")
def inicio():

    # Obtener los números guardados
    documentos = list(
        coleccion_par_impar.find().sort("_id", -1)
    )

    # Evitar números repetidos
    numeros_unicos = {}

    for numero in documentos:

        valor = numero["numero"]

        if valor not in numeros_unicos:
            numeros_unicos[valor] = numero

    # Convertir a lista
    numeros = list(numeros_unicos.values())

    # Preparar información para la tabla
    for numero in numeros:

        if numero["numero"] % 2 == 0:
            numero["tipo"] = "Par"
        else:
            numero["tipo"] = "Impar"

        if "fecha" in numero:
            numero["fecha"] = numero["fecha"].strftime(
                "%d/%m/%Y %H:%M"
            )

    return render_template(
        "index.html",
        numeros=numeros
    )


# ==========================================
# AGREGAR NÚMERO
# ==========================================

@app.route("/agregar", methods=["POST"])
def agregar():

    numero_texto = request.form["numero"].strip()

    # Comprobar que solamente sean números
    if not numero_texto.isdigit():
        return "Error: solo se permiten números", 400

    # Máximo 15 dígitos
    if len(numero_texto) > 15:
        return "Error: el número no puede tener más de 15 dígitos", 400

    numero = int(numero_texto)

    # Determinar si es par o impar
    if numero % 2 == 0:
        resultado = "Par"
    else:
        resultado = "Impar"

    # Comprobar si ya existe
    numero_existente = coleccion_par_impar.find_one({
        "numero": numero
    })

    if numero_existente:
        return "El número ya está registrado", 400

    # Crear documento
    documento = {
        "numero": numero,
        "resultado": resultado,
        "fecha": datetime.now()
    }

    # Guardar en MongoDB
    coleccion_par_impar.insert_one(documento)

    return redirect("/")


# ==========================================
# API PAR O IMPAR
# ==========================================

@app.route("/par-impar", methods=["POST"])
def par_impar():

    datos = request.get_json()

    numero = int(datos["numero"])

    # Comprobar si es par o impar
    if numero % 2 == 0:
        resultado = "Par"
    else:
        resultado = "Impar"

    # Comprobar si ya existe
    numero_existente = coleccion_par_impar.find_one({
        "numero": numero
    })

    if numero_existente:
        return jsonify({
            "numero": numero,
            "resultado": resultado,
            "mensaje": "El número ya está registrado"
        })

    # Crear documento
    documento = {
        "numero": numero,
        "resultado": resultado,
        "fecha": datetime.now()
    }

    # Guardar
    coleccion_par_impar.insert_one(documento)

    return jsonify({
        "numero": numero,
        "resultado": resultado,
        "mensaje": "Resultado guardado en MongoDB Atlas"
    })


# ==========================================
# EJECUTAR FLASK
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)