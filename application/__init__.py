"""Initialize app."""
from flask import Flask, session, redirect, url_for, escape, request
def create_app():
    """Construct the core application."""
    app = Flask(__name__,
                instance_relative_config=False)
    app.config.from_object('config.Config')

    app.secret_key = "a s1lly 1ong str1nggg of 11115354q54qw3"
    with app.app_context():

        # Import main Blueprint
        from . import routes
        app.register_blueprint(routes.main_bp)

        # Import Dash application
        from .plotSensorDash import dash_fileviewer
        app = dash_fileviewer.Add_Dash(server=app)

        return app
