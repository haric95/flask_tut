import os

from flask import Flask

# This is a factory function for creating an instance of our flask app.
def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # adding the teardown and init cli command to our app instance.
    # need to do it here because we are using a factory function.
    from . import db
    db.init_app(app)

    # registering the auth blueprint.
    from . import auth
    app.register_blueprint(auth.bp)

    # registering the blog blueprint
    from . import blog
    app.register_blueprint(blog.bp)
    # seeing as this is the main page, it makes sense to rename the endpoint to
    # just index rather than blog.index (blog.index will still work however)
    app.add_url_rule('/', endpoint='index')

    return app