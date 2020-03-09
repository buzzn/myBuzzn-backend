from os import path
from flask import Blueprint, jsonify
from flask_api import status
from util.error import Error

Conditions = Blueprint('Conditions', __name__)


@Conditions.route('/conditions', methods=['GET'])
def get_conditions():
    conditions_path = path.join(path.dirname(path.abspath(__file__)), '../util/conditions.txt')
    try:
        conditions_file = open(conditions_path, 'r')
    except Exception:
        return (Error('Conditions not found', 'Conditions are not available.').to_json(),
                status.HTTP_404_NOT_FOUND)
    conditions_text = conditions_file.read()
    return jsonify(conditions=conditions_text), status.HTTP_200_OK
