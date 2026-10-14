"""Configuration lue depuis le fichier .env (voir .env.example)."""
import os

from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

ODOO_URL = os.getenv("ODOO_URL", "http://localhost:8069/")
ODOO_DB = os.getenv("ODOO_DB", "sie")
ODOO_USERNAME = os.getenv("ODOO_USERNAME")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD")
