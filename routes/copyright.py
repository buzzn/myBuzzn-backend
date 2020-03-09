from os import path
from flask import Blueprint, jsonify
from flask_api import status
from util.error import Error

Copyright = Blueprint('Copyright', __name__)


@Copyright.route('/copyright', methods=['GET'])
def get_copyright():
    copyright_path = path.join(path.dirname(path.abspath(__file__)), '../util/copyright.txt')
    try:
        copyright_file = open(copyright_path, 'r')
    except Exception:
        return (Error('Copyright not found', 'Copyright is not available.').to_json(),
                status.HTTP_404_NOT_FOUND)
    copyright_text = copyright_file.read()
    return jsonify(copyright=copyright_text), status.HTTP_200_OK
