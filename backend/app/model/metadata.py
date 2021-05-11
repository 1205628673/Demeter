from flask_sqlalchemy import SQLAlchemy
from main import app


db = SQLAlchemy(app)
class DB():
    def getDB():
        return db
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

class UserModel(db.Model):
    __tablename__ = 'user_train'
    id = db.Column(db.Integer, primary_key = True)
    best_fitness_values = db.Column(db.String)
    mean_fitness_values = db.Column(db.String)
    fid = db.Column(db.Integer)
    regressor = db.Column(db.String(255))
    path = db.Column(db.String(255))
    create_time = db.Column(db.String(255))
    def __repr__(self):
        return str(self.id)

    