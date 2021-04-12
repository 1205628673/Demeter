from flask import Flask, jsonify
from flask import Flask,render_template,request,redirect,url_for
from app.model import metadata
from flask_sqlalchemy import SQLAlchemy
from flask_cors import * 
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
import os
import numpy as np
import sys
sys.path.append('..') #添加上层路径
import gabp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@127.0.0.1:3306/demeter'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = True
db = SQLAlchemy(app)
CORS(app, reources='/*')
def regressionResultWarpper(preds, labels):
    #回归结果包装函数
    rmse = mean_squared_error(labels,preds) ** 0.5
    mase = mean_absolute_error(labels,preds)
    level = 0
    levelArr = []
    print(preds)
    for p in preds:
        if p > 40:
            level = '一级 (%d > 40 g/kg-1)'
        elif p >= 30:
            level = '二级 (40 > %d > 30 g/kg-1)'
        elif p >= 20:
            level = '三级 (30 > %d > 20 g/kg-1)'
        elif p >= 10:
            level = '四级 (20 > %d > 10 g/kg-1)'
        elif P >= 6:
            level = '五级 (10 > %d > 6 g/kg-1)'
        else:
            level = '六级 (%d < 6 g/kg-1)'
        levelArr.append(level)
    result = {
        'code' : '200',
        'message' : 'ok',
        'preds' : preds,
        'levels' : levelArr,
        'labels' : labels ,
        'rmse' : rmse,
        'mase' : mase
    }
    return result
@app.route('/', methods = ['GET', 'POST'])
def hello():
    return 'Hello world!'
@app.route('/upload', methods = ['GET', 'POST'])
def upload():
    if request.method == 'POST':
        f = request.files.get('file')
        basepath = 'D:\\pyProjects\\Demeter\\upload'
        uploadpath = os.path.join(basepath, f.filename)
        f.save(uploadpath)
        result = {
            'code':200,
            'message':'上传完成'
        }
        fileMapper = metadata.FileMapper()
        fileMapper.path = uploadpath
        print(uploadpath)
        db.session.add(fileMapper)
        db.session.commit()
        return jsonify(result)
    result = {
            'code':503,
            'message':'Invalid method'
        }
    return jsonify(result)
def plsrguide():
    #PLSR模型回归
    fid = request.args.get('fid')
    if fid != None:
        fileMapper = metadata.FileMapper.query.filter_by(id = fid).first()
        path = fileMapper.path
        drawer = gabp.Draw('../plsr-linear.pickle', '../plsr-individual.txt')
        drawer.featuresPath = path
        features, labels = drawer.loadFeature('../plsr-individual.txt')
        regressor = drawer.model
        preds = regressor.predict(features)
        result = regressionResultWarpper(preds.flatten().tolist(), labels)
        return result
    result = {
        'code' : 404,
        'massage' : 'null filemapper id'
    }
    return result
def bpnnguide():
    #bpnn模型回归
    fid = request.args.get('fid')
    if fid != None:
        fileMapper = metadata.FileMapper.query.filter_by(id = fid).first()
        path = fileMapper.path
        drawer = gabp.Draw('../bpnn-linear.pickle', '../bpnn-individual.txt')
        drawer.featuresPath = path
        features, labels = drawer.loadFeature('../bpnn-individual.txt')
        regressor = drawer.model
        preds = regressor.predict(features)
        result = regressionResultWarpper(preds.tolist(), labels)
        return result
    result = {
        'code' : 404,
        'massage' : 'null filemapper id'
    }
    return result
def svrguide():
    #svr模型回归
    fid = request.args.get('fid')
    if fid != None:
        fileMapper = metadata.FileMapper.query.filter_by(id = fid).first()
        path = fileMapper.path
        drawer = gabp.Draw('../svr-linear.pickle', '../svr-individual.txt')
        drawer.featuresPath = path
        features, labels = drawer.loadFeature('../svr-individual.txt')
        regressor = drawer.model
        preds = regressor.predict(features)
        result = regressionResultWarpper(preds.tolist(), labels)
        return result
    result = {
        'code' : 404,
        'massage' : 'null filemapper id'
    }
    return result
def bpguide():
    #根据回归模型指导土地营养程度分类
    fid = request.args.get('fid')
    if fid != None:
        fileMapper = metadata.FileMapper.query.filter_by(id = fid).first()
        path = fileMapper.path
        #传入bpnn的模型和选择的特征号码，获得bpnn模型的特征
        bpnnDrawer = gabp.Draw('../bpnn-linear.pickle', '../bpnn-individual.txt')
        bpnnDrawer.featuresPath = path
        bpnnFeatures, bpnnLabels = bpnnDrawer.loadFeature('../bpnn-individual.txt')
        #传入plsr的模型和选择的特征号码，获得plsr模型的特征
        plsrDrawer = gabp.Draw('../plsr-linear.pickle', '../plsr-individual.txt')
        plsrDrawer.featuresPath = path
        plsrFeatures, plsrLabels = plsrDrawer.loadFeature('../plsr-individual.txt')
        #加载PLSR-BPNN联合回归模型
        plsrbpnnRegressor = gabp.PlsrBpnnRegression('../bpnn-linear.pickle', '../plsr-linear.pickle')
        preds = plsrbpnnRegressor.predict(plsrFeatures, plsrLabels, bpnnFeatures, bpnnLabels)
        result = regressionResultWarpper(preds, bpnnLabels)
        return result
    result = {
        'code' : 404,
        'massage' : 'null filemapper id'
    }
    return result
@app.route('/guide', methods = ['GET', 'POST'])
def level():
    fid = request.args.get('fid')
    regressor = request.args.get('regressor')
    if regressor == 'plsr':
        result = plsrguide()
    elif regressor == 'bpnn':
        result = bpnnguide()
    elif regressor == 'bp':
        result = bpguide()
    elif regressor == 'svr':
        result = svrguide()
    else:
        result = {'code':404, 'message':'not that %sregressor'%regressor}
    return jsonify(result)
if __name__ == '__main__':
    app.run()
