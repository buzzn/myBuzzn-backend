from flask import Blueprint, request, jsonify
from flask_api import status
from os import path
from util.error import Error

Copyright = Blueprint('Copyright', __name__)


@Copyright.route('/copyright', methods=['GET'])
def copyright():
    copyright_path = path.join(path.dirname(path.abspath(__file__)), '../util/copyright.txt')
    try:
        copyright_file = open(copyright_path, 'r')
    except Exception as e:
        return Error('Copyright not found', 'Copyright is not available.').to_json(), status.HTTP_404_NOT_FOUND
    copyright_text = copyright_file.read()
    return jsonify(copyright=copyright_text), status.HTTP_200_OK
