import os
import cloudinary

cloudinary.config(
    cloud_name="TU_CLOUD_NAME",
    api_key="TU_API_KEY",
    api_secret="TU_API_SECRET"
)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ALLOWED_EXTENSIONS = {"pdf"}
BIBLIOTECA_JSON = os.path.join(BASE_DIR, "biblioteca.json")