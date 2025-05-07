from flask import Blueprint

bp = Blueprint('bug', __name__)

from app.bug import routes