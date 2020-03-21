from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table

db = SQLAlchemy()

def get_table(name):
    return Table(name, db.metadata, autoload=True, autoload_with=db.engine)