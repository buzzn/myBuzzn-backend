from os import path
import json
from flask import Blueprint, jsonify
from flask_api import status
from util.error import Error

Widgets = Blueprint('Widgets', __name__)


@Widgets.route('/widgets', methods=['GET'])
def get_widgets():
    widgets_path = path.join(path.dirname(path.abspath(__file__)), '../util/widgets.json')
    try:
        widgets_file = open(widgets_path, 'r')
    except Exception:
        return (Error('Widgets not found', 'Widgets are not available.').to_json(),
                status.HTTP_404_NOT_FOUND)
    try:
        widgets_json = json.load(widgets_file)
    except Exception:
        return (Error('Widgets could not be loaded', 'Widgets could not be loaded.').to_json(),
                status.HTTP_404_NOT_FOUND)
    return jsonify(widgets_json), status.HTTP_200_OK
