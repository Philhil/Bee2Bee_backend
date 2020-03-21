from flask import Flask, jsonify
from models import db
from api.routes.company import company_api
from api.routes.user import user_api
from os import environ

def create_app(config=None):
    app = Flask(__name__)
    # TODO: load config from env

    db_config = {
        'DB_PASS': '',
        'DB_PORT': '',
        'DB_USER': '',
        'DB_HOST': '',
        'DB_DATABASE': '',
        'DB_DRIVER': ''
    }

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    if 'SQLALCHEMY_DATABASE_URI' in environ:
        app.config['SQLALCHEMY_DATABASE_URI'] = environ['SQLALCHEMY_DATABASE_URI']
    else:
        for key in db_config.keys():
            if key not in environ:
                raise SystemExit("db config key {} missing from env".format(key))
        db_config = { key: environ[key] for key in db_config.keys() }
        app.config['SQLALCHEMY_DATABASE_URI'] = "{DB_DRIVER}://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}".format(**db_config)


    setup_app(app)
    return app

def setup_app(app):
    db.init_app(app)

    app.register_blueprint(company_api)
    app.register_blueprint(user_api)
    @app.route('/')
    def index():
        return jsonify(status=200, message='OK')

    @app.route('/healthcheck')
    def healthcheck():
        return jsonify(status=200, message='healthcheck OK')

    @app.route('/dbtest')
    def dbtest():
        from sqlalchemy.sql import select
        from sqlalchemy import Table, Column, BigInteger, Text, ForeignKey
        # select * from skills where skillset_id = 4;
        skills = Table('skills', db.metadata, autoload=True, autoload_with=db.engine)
        conn = db.session.connection()
        s = select([skills]).where(skills.c.skillset_id == 4)
        result = conn.execute(s)
        return jsonify(result.fetchone()["name"])

    @app.route('/dbtest_insert')
    def dbtest_insert():
        from sqlalchemy.sql import insert
        from sqlalchemy import Table
        # select * from skills where skillset_id = 4;
        playground = Table('playground', db.metadata, autoload=True, autoload_with=db.engine)
        ins = playground.insert().values(data='{"foo": "bar"')
        conn = db.session.connection()
        result = conn.execute(ins)
        db.session.commit()
        return jsonify({"playground_id": result.inserted_primary_key})
