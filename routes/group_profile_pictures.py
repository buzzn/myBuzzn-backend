from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.group import Group
from models.user import User


GroupProfilePictures = Blueprint('GroupProfilePictures', '__name__')


def get_group_members(user_id):
    """ Get the parameters from the database to create a group picture list for
    the given user.
    :param in user_id: the user's id
    :return: the group members' ids and profile pictures
    :rtype: list
    """

    target_user = User.query.filter_by(id=user_id).first()
    target_group = Group.query.filter_by(id=target_user.group_id).first()
    group_users = User.query.filter_by(group_id=target_group.id).all()
    group_members = []
    for group_user in group_users:
        group_members.append(dict(id=group_user.id, avatar=group_user.avatar))
    return group_members


@GroupProfilePictures.route('/assets/group-profile-pictures', methods=['GET'])
@jwt_required
def group_profile_pictures():
    """ Get all profile pictures of the user's group, together with their user
    ids.
    """

    user_id = get_jwt_identity()
    get_group_members(user_id)
