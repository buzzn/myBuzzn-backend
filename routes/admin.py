import secrets
from functools import wraps
from flask import render_template, Blueprint, Response, request, redirect
from flask_jwt_extended import (create_access_token, get_raw_jwt, get_jwt_identity,
                                set_access_cookies, verify_jwt_in_request, unset_jwt_cookies)
from models.user import User, GenderType, StateType, RoleType
from models.group import Group
from util.database import db


Admin = Blueprint('Admin', __name__)


def admin_required(fn):
    """ Wraps a function and injects an admin check before each call.
    Redirects to the login page, if the current user is not an admin, or no
    user is logged in.
    :param fn: The function to wrap.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        target_user = User.query.filter_by(id=user_id).first()

        if target_user is None:
            return redirect("/admin/login", code=403)

        if target_user.role != RoleType.ADMINISTRATOR:
            return redirect("/admin/login", code=403)
        return fn(*args, **kwargs)
    return wrapper

@Admin.route('/favicon.ico', methods=['GET'])
def favicon():
    """Prevents the logger from logging 404 when the browser asks for a favicon.
    """
    return ''


@Admin.route('/admin/login', methods=['POST'])
def do_admin_login():
    """Log-in for the given user..
    :param str email: The mail which is used to identify the user.
    :param str password: The user's password.
    """
    user_requested = request.form['email'].lower()
    password_requested = request.form['password']

    target_user = User.query.filter_by(mail=user_requested).first()
    if target_user is None:
        return Response(render_template('admin/login.html',
                                        message="Unknown Credentials"))

    if not target_user.check_password(password_requested):
        return Response(render_template('admin/login.html',
                                        message="Unknown Credentials"))

    if not target_user.state == StateType.ACTIVE:
        return Response(render_template('admin/login.html',
                                        message="User account deactivated. Cannot login."))

    resp = Response(render_template('admin/admin.html', user=target_user.name,
                                    message="Login succeeded"))
    set_access_cookies(resp, create_access_token(identity=target_user.id))
    return resp


@Admin.route('/admin/login')
def admin_login():
    """Returns a login form.
    """
    return Response(render_template('admin/login.html'))


@Admin.route('/admin/logout')
def logout():
    """Performs a logout for the current user.
    """
    resp = Response(render_template('admin/login.html',
                                    message='Your session has been canceled.'))
    unset_jwt_cookies(resp)
    return resp


@Admin.route('/admin/')
@admin_required
def admin():
    """Returns the admin home page.
    """
    return Response(render_template('admin.html'))


@Admin.route('/admin/user/create', methods=['POST'])
@admin_required
def do_user_create():
    """Generates a new user. Generats a password token. Does not send a mail.
    :param str gender: The new user's gender.
    :param str name: The new user's name.
    :param str mail: The new user's mail.
    :param str meter_id: The new user's meter id.
    :param str group_id: The new user's group id.
    :param str role: The new user's role.
    """
    target = User(
        request.form['gender'],
        request.form['first_name'],
        request.form['name'],
        request.form['mail'],
        request.form['meter_id'],
        request.form['group_id'],
        secrets.token_hex(33))
    target.set_role(request.form['role'])
    target.nick = request.form['nick']
    db.session.add(target)
    db.session.commit()
    return user_list("Created user " + target.name)


@Admin.route('/admin/user/create', methods=['GET'])
@admin_required
def request_user_create():
    """Returns a form to create a new user.
    The form contains an csrf_token to prevent cross side attacks.
    And some preselected values.
    """
    return Response(render_template('admin/user/create-update.html',
                                    csrf_token=(
                                        get_raw_jwt() or {}).get("csrf"),
                                    target="/admin/user/create",
                                    genders=list(GenderType),
                                    states=list(StateType),
                                    groups=Group.query.all(),
                                    roles=list(RoleType),
                                    gender=GenderType.FEMALE,
                                    role=RoleType.LOCAL_POWER_TAKER,
                                    state=StateType.ACTIVATION_PENDING),
                    mimetype='text/html')


@Admin.route('/admin/user/update', methods=['POST'])
@admin_required
def do_user_update():
    """Updates an existing user.
    :param str id: The id to identify the user to update.
    :param str name: The user's name.
    :param str mail: The user's mail.
    :param str role: The user's role.
    :param str state: The user's state.
    :param str gender: The user's gender.
    :param str meter_id: The user's meter_id.
    :param str group_id: The user's group_id.
    """
    targetUsers = User.query.filter_by(id=request.form['id']).all()
    if not any(targetUsers):
        return user_list("Unknown user.")

    targetUser = targetUsers[0]

    targetUser.first_name = request.form['first_name']
    targetUser.name = request.form['name']
    targetUser.nick = request.form['nick']
    targetUser.mail = request.form['mail']
    targetUser.role = request.form['role']
    targetUser.state = request.form['state']
    targetUser.gender = request.form['gender']
    targetUser.meter_id = request.form['meter_id']
    targetUser.group_id = request.form['group_id']

    db.session.commit()
    return user_list("Updated user " + targetUser.name)


@Admin.route('/admin/user/update', methods=['GET'])
@admin_required
def request_user_update():
    """Returns a form to update an existing user.
    :param str id: The id to identify the user to update.
    """
    target_user = User.query.filter_by(id=request.args['id']).first()
    if target_user is None:
        return user_list("Unknown user.")

    return Response(render_template('admin/user/create-update.html',
                                    csrf_token=(
                                        get_raw_jwt() or {}).get("csrf"),
                                    target="/admin/user/update",
                                    genders=list(GenderType),
                                    states=list(StateType),
                                    groups=Group.query.all(),
                                    roles=list(RoleType),
                                    id=target_user.id,
                                    gender=target_user.gender,
                                    first_name=target_user.first_name,
                                    name=target_user.name,
                                    nick=target_user.nick,
                                    mail=target_user.mail,
                                    meter_id=target_user.meter_id,
                                    group_id=target_user.group_id,
                                    role=target_user.role,
                                    state=target_user.state),
                    mimetype='text/html')


@Admin.route('/admin/user/delete', methods=['GET'])
@admin_required
def user_delete():
    """Deletes a user.
    :param str id: The id to identify the user to delete.
    """
    target_user = User.query.filter_by(id=request.args['id']).first()
    if target_user is None:
        return user_list("Unknown user.")

    db.session.delete(target_user)
    db.session.commit()

    return user_list("Deleted user " + target_user.name)


@Admin.route('/admin/user/', methods=['GET'])
@admin_required
def user_list(message=''):
    """ Lists all existing users.
    """
    return Response(render_template('admin/user/list.html',
                                    users=User.query.all(),
                                    message=message),
                    mimetype='text/html')


@Admin.route('/admin/group/create', methods=['POST'])
@admin_required
def do_group_create():
    """ Creates a group.
    :param str name: the new group's name
    :param str meter: the new group's community consumption meter id
    :param str group_production_meter_id_first: the new group's first
    production meter id
    :param str group_production_meter_id_second: the new group's second
    production meter id
    """
    target_group = Group(request.form['name'], request.form['meter'],
                         request.form['group_production_meter_id_first'],
                         request.form['group_production_meter_id_second'])
    db.session.add(target_group)
    db.session.commit()
    return group_list("Created group " + target_group.name)


@Admin.route('/admin/group/create', methods=['GET'])
@admin_required
def request_group_create():
    """Returns a form to create a new group.
    """
    return Response(render_template('admin/group/create-update.html',
                                    csrf_token=(
                                        get_raw_jwt() or {}).get("csrf"),
                                    target="/admin/group/create"),
                    mimetype='text/html')


@Admin.route('/admin/group/update', methods=['POST'])
@admin_required
def do_group_update():
    """ Updates an existing group.
    :param str id: the id of the group to update
    :param str name: the group's name
    :param str meter: the group's community consumption meter id
    """
    target_group = Group.query.filter_by(id=request.form['id']).first()
    if target_group is None:
        return group_list("Unknown group.")

    target_group.name = request.form['name']
    target_group.group_meter_id = request.form['meter']
    target_group.group_production_meter_id_first = request.form['group_production_meter_id_first']
    target_group.group_production_meter_id_second = request.form[
        'group_production_meter_id_second']

    db.session.commit()
    return group_list("Updated group " + target_group.name)


@Admin.route('/admin/group/update', methods=['GET'])
@admin_required
def request_group_update():
    """Returns a form to update an existing group.
    :param str id: The id of the group to update.
    """
    target_group = Group.query.filter_by(id=request.args['id']).first()
    if target_group is None:
        return group_list("Unknown group.")

    return Response(
        render_template(
            'admin/group/create-update.html',
            csrf_token=(
                get_raw_jwt() or {}).get("csrf"),
            target="/admin/group/update",
            id=target_group.id,
            name=target_group.name,
            meter=target_group.group_meter_id,
            group_production_meter_id_first=target_group.group_production_meter_id_first,
            group_production_meter_id_second=target_group.group_production_meter_id_second),
        mimetype='text/html')


@Admin.route('/admin/group/delete')
@admin_required
def group_delete():
    """Deletes a group.
    :param str id: The id of the group to delete.
    """
    target_group = Group.query.filter_by(id=request.args['id']).first()
    if target_group is None:
        return group_list("Unknown group.")

    db.session.delete(target_group)
    db.session.commit()

    return group_list("Deleted group " + target_group.name)


@Admin.route('/admin/group/')
@admin_required
def group_list(message=''):
    """Lists all the existing groups.
    """
    return Response(render_template('admin/group/list.html',
                                    groups=Group.query.all(),
                                    message=message),
                    mimetype='text/html')
