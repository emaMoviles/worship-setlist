from flask import Flask, render_template, request, send_file, redirect
from pypdf import PdfWriter, PdfReader
import config
import os
import cloudinary.uploader
from werkzeug.utils import secure_filename
import json
import requests
from io import BytesIO

app = Flask(__name__)
def archivo_valido(nombre):

    return "." in nombre and \
        nombre.rsplit(".",1)[1].lower() in config.ALLOWED_EXTENSIONS

def obtener_canciones():

    if not os.path.exists(config.BIBLIOTECA_JSON):
        return []

    with open(config.BIBLIOTECA_JSON, "r") as f:
        canciones = json.load(f)

    return canciones
@app.route("/")
def index():

    canciones = obtener_canciones()

    return render_template(
        "index.html",
        canciones=canciones
    )

@app.route("/subir", methods=["POST"])
def subir_pdf():

    if "archivo" not in request.files:
        return "No se encontró el archivo en la petición"

    archivo = request.files["archivo"]

    if archivo.filename == "":
        return "No seleccionaste ningún archivo"

    if archivo and archivo_valido(archivo.filename):

        nombre = secure_filename(archivo.filename)

        resultado = cloudinary.uploader.upload(
            archivo,
            resource_type="raw",
            public_id=nombre
        )

        url_pdf = resultado["secure_url"]

        # leer biblioteca
        if os.path.exists(config.BIBLIOTECA_JSON):

            with open(config.BIBLIOTECA_JSON, "r") as f:
                canciones = json.load(f)

        else:
            canciones = []

        # agregar nueva canción
        canciones.append({
            "nombre": nombre,
            "url": url_pdf
        })

        # guardar biblioteca
        with open(config.BIBLIOTECA_JSON, "w") as f:
            json.dump(canciones, f, indent=4)

        print("Archivo subido:", url_pdf)

        return redirect("/")

    return "Solo se permiten archivos PDF"



@app.route("/crear_setlist", methods=["POST"])
def crear_setlist():

    seleccionadas = request.form.getlist("canciones")

    if len(seleccionadas) == 0:
        return redirect("/")

    canciones = obtener_canciones()

    writer = PdfWriter()

    for cancion in canciones:

        if cancion["nombre"] in seleccionadas:

            respuesta = requests.get(cancion["url"])

            pdf_bytes = BytesIO(respuesta.content)

            reader = PdfReader(pdf_bytes)

            for pagina in reader.pages:
                writer.add_page(pagina)

    salida = "setlist.pdf"

    with open(salida, "wb") as f:
        writer.write(f)

    return send_file(salida)


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )
