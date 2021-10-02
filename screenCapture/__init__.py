from flask import Blueprint

api = Blueprint('api', __name__)

# Capture Api
from . import makeScreenShot

# make Sound to Text
from . import getStt