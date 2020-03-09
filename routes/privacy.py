from os import path
from flask import Blueprint, jsonify
from flask_api import status
from util.error import Error

Privacy = Blueprint('Privacy', __name__)


@Privacy.route('/privacy', methods=['GET'])
def get_privacy():
    privacy_path = path.join(path.dirname(path.abspath(__file__)), '../util/copyright.txt')
    try:
        privacy_file = open(privacy_path, 'r')
    except Exception:
        return (Error('Privacy not found', 'Privacy is not available.').to_json(),
                status.HTTP_404_NOT_FOUND)
    privacy_text = privacy_file.read()
    return jsonify(privacy=privacy_text), status.HTTP_200_OK
