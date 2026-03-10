from flask import Flask, render_template, request, send_file, redirect
import os
from pypdf import PdfWriter, PdfReader
import config
from werkzeug.utils import secure_filename
app = Flask(__name__)
os.makedirs(config.BIBLIOTECA, exist_ok=True)
os.makedirs(config.SETLISTS, exist_ok=True)
def archivo_valido(nombre):

    return "." in nombre and \
        nombre.rsplit(".",1)[1].lower() in config.ALLOWED_EXTENSIONS

def obtener_canciones():

    canciones = []

    for archivo in os.listdir(config.BIBLIOTECA):

        if archivo.endswith(".pdf"):
            canciones.append(archivo)

    canciones.sort()

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

        ruta = os.path.join(
            config.BIBLIOTECA,
            nombre
        )

        archivo.save(ruta)

        print("Archivo guardado en:", ruta)

        return redirect("/")

    return "Solo se permiten archivos PDF"
@app.route("/crear_setlist", methods=["POST"])
@app.route("/crear_setlist", methods=["POST"])
def crear_setlist():

    seleccionadas = request.form.getlist("canciones")

    # Validar que haya canciones seleccionadas
    if len(seleccionadas) == 0:
        return redirect("/")

    writer = PdfWriter()

    for cancion in seleccionadas:

        ruta = os.path.join(
            config.BIBLIOTECA,
            cancion
        )

        reader = PdfReader(ruta)

        for pagina in reader.pages:
            writer.add_page(pagina)

    salida = os.path.join(
        config.SETLISTS,
        "culto_actual.pdf"
    )

    with open(salida, "wb") as f:
        writer.write(f)

    return send_file(salida)
if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )
