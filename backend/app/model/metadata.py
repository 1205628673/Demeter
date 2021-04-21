from flask_sqlalchemy import SQLAlchemy
from main import app

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://david:123456@127.0.0.1:3306/demeter'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = True

db = SQLAlchemy(app)

class FileMapper(db.Model):
    __tablename__ = 'filemapper'
    id = db.Column(db.Integer, primary_key = True)
    path = db.Column(db.String(255))
    filename = db.Column(db.String(255))
    def __repr__(self):
        return self.path + '<>' + self.filename

class SoilSample(db.Model):
    __tablename__ = 'soil_sample'
    id = db.Column(db.Integer, primary_key = True)
    fid = db.Column(db.Integer)
    sid = db.Column(db.Integer)
    som_value = db.Column(db.Float)
    regressor = db.Column(db.String)
    def __repr__(self):
        return str(self.id) + '<>' + str(self.fid) + '<>' + str(self.sid) + '<>' + str(self.som_value) + '<>' + self.regressor
    
    