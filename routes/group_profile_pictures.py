import logging.config
from flask import Blueprint, jsonify
from flask_api import status
from flask_jwt_extended import get_jwt_identity
from models.group import Group
from models.user import User
from util.error import NO_USERS, exception_message
from util.login import login_required


logger = logging.getLogger(__name__)
GroupProfilePictures = Blueprint('GroupProfilePictures', '__name__')


def get_group_members(user_id):
    """ Get the parameters from the database to create a group picture list for
    the given user.
    :param in user_id: the user's id
    :returns: the group members' ids and profile pictures
    :rtype: list
    """

    try:
        target_user = User.query.filter_by(id=user_id).first()
        target_group = Group.query.filter_by(id=target_user.group_id).first()
        group_users = User.query.filter_by(group_id=target_group.id).all()
        group_members = []
        for group_user in group_users:
            group_members.append(
                dict(id=group_user.id, avatar=group_user.avatar))
        return group_members

    except Exception as e:
        message = exception_message(e)
        logger.error(message)
        return None


@GroupProfilePictures.route('/assets/group-profile-pictures', methods=['GET'])
@login_required
def group_profile_pictures():
    """ Get all profile pictures of the user's group, together with their user
    ids.
    swagger_from_file: swagger_files/get_assets_group-profile-pictures.yml
    """

    user_id = get_jwt_identity()
    try:
        result = get_group_members(user_id)
        if result is None:
            return NO_USERS.to_json(), status.HTTP_400_BAD_REQUEST
        return jsonify(result), status.HTTP_200_OK

    except Exception as e:
        message = exception_message(e)
        logger.error(message)
        return jsonify({}), status.HTTP_206_PARTIAL_CONTENT
