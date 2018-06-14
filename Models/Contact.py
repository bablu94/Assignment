import sys
sys.path.append('../')
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from DAOMysql.configuration import configuration
from sqlalchemy.dialects.mysql import BIGINT


config = configuration()

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] =  config.configString
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db = SQLAlchemy(app)

class Contact(db.Model):
    __tablename__ = 'contacts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(256), index=True)
    mobile = db.Column(BIGINT(unsigned=True))
    userid = db.Column(db.Integer)

    userSearch = {}

    @property
    def serialize(self):
        return {
            'contact name': self.name,
            'contact email': self.email,
            'contact mobile': self.mobile,
        }