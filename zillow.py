from flask import Flask
from flask_mongoengine import MongoEngine
from zillowrun import zillowrun


db = MongoEngine()


def create_app(**config_overrides):
    app = Flask(__name__, static_folder='static', static_url_path='')

    # Load config.
    app.config["MONGODB_SETTINGS"] = {'DB': "my_zillow_db"}
    # apply overrides
    app.config.update(config_overrides)

    # Setup the database.
    db.init_app(app)

    # Register blueprints
    from views import zillow_app
    app.register_blueprint(zillow_app)

    return app

if __name__ == '__main__':
    app = create_app()
    zillowrun(app)



