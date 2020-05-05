from functools import wraps
from flask import render_template, Blueprint, Response, request, redirect
from flask_jwt_extended import (create_access_token, get_raw_jwt, get_jwt_identity,
                                set_access_cookies, verify_jwt_in_request, unset_jwt_cookies)
from models.user import User, StateType, RoleType
from util.database import db


Employee = Blueprint('Employee', __name__)


def employee_required(fn):
    """ Wraps a function and injects an admin/employee check before each call.
    Redirects to the login page, if the current user is not an admin/employee, or no
    user is logged in.
    :param fn: The function to wrap.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        target_user = User.query.filter_by(id=user_id).first()

        if target_user is None:
            return redirect('employee/login_employee.html', code=403)

        if target_user.role != RoleType.ADMINISTRATOR and target_user.role != RoleType.EMPLOYEE:
            return redirect('employee/login_employee.html', code=403)
        return fn(*args, **kwargs)
    return wrapper


@Employee.route('/favicon.ico', methods=['GET'])
def favicon():
    """Prevents the logger from logging 404 when the browser asks for a favicon.
    """
    return ''


@Employee.route('/employee/login', methods=['POST'])
def do_employee_login():
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

    resp = Response(render_template('employee/employee.html', user=target_user.name,
                                    message="Login succeeded"))
    set_access_cookies(resp, create_access_token(identity=target_user.id))
    return resp


@Employee.route('/employee/login')
def employee_login():
    """Returns a login form.
    """
    return Response(render_template('employee/login_employee.html'))


@Employee.route('/employee/logout')
def logout():
    """Performs a logout for the current user.
    """
    resp = Response(render_template('employee/login_employee.html',
                                    message='Your session has been canceled.'))
    unset_jwt_cookies(resp)
    return resp


@Employee.route('/employee/')
@employee_required
def employee():
    """Returns the employee home page.
    """
    return Response(render_template('employee/employee.html'))


@Employee.route('/employee/baseline', methods=['GET'])
@employee_required
def search_user(message=''):

    return Response(render_template('employee/baseline.html',
                                    message=message,
                                    csrf_token=(get_raw_jwt() or {}).get("csrf")))


@Employee.route('/employee/user/update', methods=['POST'])
@employee_required
def do_user_baseline_update():
    """Updates an existing user baseline.
    :param str baseline: The user's baseline.
    """
    targetUsers = User.query.filter_by(id=request.form['id']).all()
    if not any(targetUsers):
        return user_list("Unknown user.")

    targetUser = targetUsers[0]

    targetUser.baseline = request.form['baseline']

    db.session.commit()
    return Response(render_template('employee/user/list.html',
                                    users=targetUsers,
                                    message=f"Updated baseline for {targetUser.name}"),
                    mimetype='text/html')


@Employee.route('/employee/user/update', methods=['GET'])
@employee_required
def request_user_baseline_update():
    """Returns a form to update an existing user.
    :param str id: The id to identify the user to update.
    """
    target_user = User.query.filter_by(id=request.args['id']).first()
    if target_user is None:
        return user_list("Unknown user.")

    return Response(render_template('employee/user/update_baseline.html',
                                    csrf_token=(
                                        get_raw_jwt() or {}).get("csrf"),
                                    target="/employee/user/update",
                                    first_name=target_user.first_name,
                                    name=target_user.name,
                                    baseline=target_user.baseline,
                                    id=target_user.id,
                                    mimetype='text/html'))


@Employee.route('/employee/user/all', methods=['GET'])
@employee_required
def user_list_all(message=''):
    """ Lists all existing users.
    """
    return Response(render_template('employee/user/list.html',
                                    users=User.query.all(),
                                    message=message),
                    mimetype='text/html')


@Employee.route('/employee/user/name', methods=['POST'])
@employee_required
def user_list(message=''):
    """ Lists all existing users.
    """
    target_users = User.query.filter_by(name=request.form['name']).all()

    if not any(target_users):
        return search_user("Unknown user.")

    return Response(render_template('employee/user/list.html',
                                    users=target_users,
                                    message=message),
                    mimetype='text/html')
