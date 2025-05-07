from flask import Blueprint

bp = Blueprint('project', __name__)

from app.project import routes
from app.project import forms