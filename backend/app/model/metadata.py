from flask_sqlalchemy import SQLAlchemy
from main import app

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://david:123456@127.0.0.1:3306/demeter'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = True

db = SQLAlchemy(app)

class FileMapper(db.Model):
    __tablename__ = 'filemapper'
    id = db.Column(db.Integer, primary_key = True)
    path = db.Column(db.String)

    def __repr__(self):
        print('path : {}'.format(path))
    
    