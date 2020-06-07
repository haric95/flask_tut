"""
This code creates the auth blueprint. Views are registered to a blueprint and
then this blueprint is registered to the application.
"""

import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

# First argument is the name of the blueprint
# The second says where the instance is defined
# The third will prepend the /auth prefix to any url associated with this
# blueprint.
bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    # if the HTTP request is POST.
    if request.method == 'POST':
        # request.form is an object that contains the user's inputs to the form
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        # if there is not already a user with the same details.
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)

        # insert the new user's details into the database.
        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                # don't store passwords directly in the database. store the hashes,
                # for security reasons.
                (username, generate_password_hash(password))
            )
            # as we are modifying the database, we need to call db.commit().
            db.commit()
            return redirect(url_for('auth.login'))

        # if registering fails, flash stores the error in a message that can be
        # retrived in the template.
        flash(error)

    # the return value of the blueprint is the response when the user vists a url
    # that uses this blueprint.
    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        # check username and password are correct
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        # session is a dict that contains information that is saved across requests.
        # it is saved in a cookie which is signed by flask to avoid tampering.
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

# this decorator means this function is always run befor anything else in the
# view.
@bp.before_app_request
def load_logged_in_user():
    # if user is logged in, the session dict (stored in cookie) will have a
    # user_id value.
    user_id = session.get('user_id')

    # if not then g.user is set to none, as no user is logged in.
    if user_id is None:
        g.user = None
    # if the user is logged in then we fetch their data.
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

# to logout, we just need to clear the session dict and route the user to the
# landing page.
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# this decorator function ensures that the user is logged in before any other
# views are loaded.
# include the line @login_required above any views that require the user to be
# logged in, to apply this logic.
def login_required(view):
    @functools.wraps(view)
    # **kwargs is used to define a function that you can pass an unknown number
    # of named variables to. *args is for an unknown number of unnamed variables.
    def wrapped_view(**kwargs):
        # if user is not logged in, route to the login page.
        if g.user is None:
            return redirect(url_for('auth.login'))
        # else return the view.
        return view(**kwargs)

    return wrapped_view


# Note on endpoints and views:

# the url_for function generates the url to a certain view taking the name of the
# view and perhaps any arguments. the name of this view is the endpoint and it
# defaults to be the name of the function. for example url_for('hello') would
# generate the url to load the hello view. to call with arguments:
# url_for('hello', name='world')
# When you want to get the url for a view that is loaded through a blueprint, you
# prepend the name of the blueprint. eg to get the url for login view for our auth
# blueprint, we use: url_for('auth.login').
