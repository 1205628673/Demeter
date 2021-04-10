from flask import Flask, jsonify
from flask import Flask,render_template,request,redirect,url_for
from app.model import metadata
from flask_sqlalchemy import SQLAlchemy
import os
import sys
sys.path.append('..') #添加上层路径
import gabp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:mysql@127.0.0.1:3306/demeter'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = True
db = SQLAlchemy(app)

@app.route('/', methods = ['GET', 'POST'])
def hello():
    return 'Hello world!'
@app.route('/upload', methods = ['GET', 'POST'])
def upload():
    if request.method == 'POST':
        f = request.files.get('file')
        basepath = os.path.dirname(__file__)
        uploadpath = os.path.join(basepath, f.filename)
        f.save(uploadpath)
        result = {
            'code':200,
            'message':'上传完成'
        }
        fileMapper = FileMapper()
        metadata.path = uploadpath
        db.session.add(fileMapper)
        return jsonify(result)
    result = {
            'code':503,
            'message':'Invalid method'
        }
    return jsonify(result)
@app.route('/level', methods = ['GET', 'POST'])
def level():
    fid = request.args.get('fid')

    if fid != None:
        #fileMapper = metadata.FileMapper.query.filter_by(id=fid).first()
        #path = fileMapper.path
        drawer = gabp.Draw('../bpnn-linear.pickle', '../bpnn-individual.txt')
        drawer.featuresPath = path
        features, labels = drawer.loadFeature('../bpnn-individual.txt')

if __name__ == '__main__':
    app.run()
