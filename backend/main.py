from flask import Flask, jsonify,make_response
from flask import Flask,render_template,request,redirect,url_for
from app.model import metadata
from flask_sqlalchemy import SQLAlchemy
from flask_cors import * 
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import accuracy_score,r2_score
import os
import time
import numpy as np
import sys,math
from hashlib import md5
sys.path.append('..') #添加上层路径
import gabp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@127.0.0.1:3306/demeter'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = True
db = SQLAlchemy(app)
def regressionResultWarpper(preds, labels):
    #回归结果包装函数
    rmse = mean_squared_error(labels,preds) ** 0.5
    mape = mean_absolute_error(labels,preds)
    r2 = r2_score(labels, preds)
    mean_observe_value = 0
    observe_sum = 0
    for y in labels:
        observe_sum = observe_sum + y
    mean_observe_value = observe_sum / len(labels)
    sd = 0 #观察值的方差
    for y in labels:
        sd = sd + (y - mean_observe_value) ** 2
    sd = math.sqrt(sd / len(labels))
    rpd = sd / rmse 
    level = 0
    levelArr = []
    for p in preds:
        if p > 40:
            level = '一级 (%d > 40 g/kg-1)'
        elif p >= 30:
            level = '二级 (40 > %d > 30 g/kg-1)'
        elif p >= 20:
            level = '三级 (30 > %d > 20 g/kg-1)'
        elif p >= 10:
            level = '四级 (20 > %d > 10 g/kg-1)'
        elif p >= 6:
            level = '五级 (10 > %d > 6 g/kg-1)'
        else:
            level = '六级 (%d < 6 g/kg-1)'
        levelArr.append(level)
    result = {
        'code' : '200',
        'message' : 'ok',
        'data' : {
            'preds' : preds,
            'levels' : levelArr,
            'labels' : labels,
            'rmse' : rmse,
            'mape' : mape,
            'r2' : r2,
            'rpd' : rpd
        }
    }
    return result
@app.route('/', methods = ['GET', 'POST'])
def hello():
    return 'Hello world!'
@app.route('/train', methods=['GET'])
def train():
    fid = request.args.get('fid')
    regressor = request.args.get('regressor')
    fileMapper = metadata.FileMapper.query.filter_by(id = fid).first()
    filename = fileMapper.filename
    ga = gabp.GA()
    if regressor == 'svr':
        ga.cls = gabp.SvrRegression(filename)
    elif regressor == 'plsr':
        ga.cls = gabp.PlsrRegression(filename)
    elif regressor == 'bpnn':
        ga.cls = gabp.BpnnRegression(filename)
    elif regressor == 'bp':
        ga.cls = gabp.PlsrBpnnRegression(filename)
    else:
        return {'message':'找不到模型','code':10002}
    #设置训练中所选择的特征向量和模型的保存位置
    timesuffix = str(time.time())
    md5Name = md5(bytes(timesuffix)).hexdigest()
    #设置txt格式的individual个体文件
    ga.individualFile = os.path.join('D:\\pyProjects\\Demeter\\upload', md5Name + '.txt')
    #设置pickle格式的模型文件
    ga.modelFile = os.path.join('D:\\pyProjects\\Demeter\\upload', md5Name + '.pickle')
    #设置xls格式的保留文件
    ga.xlsFile = os.path.join('D:\\pyProjects\\Demeter\\upload', md5Name + '.xlsx')
    meanFitnesses,bestFitnesses = ga.evolution()
    return {'message':'ok','code':200,'data':{'meanFitnesses':meanFitnesses,'bestFitnesses':bestFitnesses}}
@app.route('/upload', methods = ['GET', 'POST'])
def upload():
    if request.method == 'POST':
        f = request.files.get('file')
        filename = f.filename
        if not(filename.endswith('.xls') or filename.endswith('.xlsx')):
            return jsonify({
                'code':500,
                'message':'invalid file extension'
            })
        extension = '.' + filename.split(".")[1]
        timesuffex = str(time.time())
        md5Name = md5(filename.encode('utf8') + bytes(timesuffex,'utf8')).hexdigest() + extension
        basepath = 'D:\\pyProjects\\Demeter\\upload'
        uploadpath = os.path.join(basepath, md5Name)
        f.save(uploadpath)
        result = {
            'code':200,
            'message':'上传完成'
        }
        fileMapper = metadata.FileMapper()
        fileMapper.path = uploadpath
        fileMapper.filename = filename
        db.session.add(fileMapper)
        db.session.commit()
        return jsonify(result)
        result = {
            'code':503,
            'message':'Invalid method'
        }
    return jsonify(result)
def plsrguide(fid):
    #PLSR模型回归
    if fid != None:
        fileMapper = metadata.FileMapper.query.filter_by(id = fid).first()
        path = fileMapper.path
        drawer = gabp.Draw('../plsr-linear.pickle', '../plsr-individual.txt')
        drawer.featuresPath = path
        features, labels = drawer.loadFeature('../plsr-individual.txt')
        #labels = [] #取消标签
        regressor = drawer.model
        preds = regressor.predict(features)
        result = regressionResultWarpper(preds.flatten().tolist(), labels)
        return result
    result = {
        'code' : 404,
        'massage' : 'null filemapper id'
    }
    return result
def bpnnguide(fid):
    #bpnn模型回归
    if fid != None:
        fileMapper = metadata.FileMapper.query.filter_by(id = fid).first()
        path = fileMapper.path
        drawer = gabp.Draw('../bpnn-linear.pickle', '../bpnn-individual.txt')
        drawer.featuresPath = path
        features, labels = drawer.loadFeature('../bpnn-individual.txt')
        #labels = [] #取消标签
        regressor = drawer.model
        preds = regressor.predict(features)
        result = regressionResultWarpper(preds.tolist(), labels)
        return result
    result = {
        'code' : 404,
        'massage' : 'null filemapper id'
    }
    return result
def svrguide(fid):
    #svr模型回归
    if fid != None:
        fileMapper = metadata.FileMapper.query.filter_by(id = fid).first()
        path = fileMapper.path
        drawer = gabp.Draw('../svr-linear.pickle', '../svr-individual.txt')
        drawer.featuresPath = path
        features, labels = drawer.loadFeature('../svr-individual.txt')
        #labels = [] #取消标签
        regressor = drawer.model
        preds = regressor.predict(features)
        result = regressionResultWarpper(preds.tolist(), labels)
        return result
    result = {
        'code' : 404,
        'massage' : 'null filemapper id'
    }
    return result
def bpguide(fid):
    #根据回归模型指导土地营养程度分类
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
        plsrbpnnRegressor.k1File = '../k1.txt'
        plsrbpnnRegressor.k2File = '../k2.txt'
        preds = plsrbpnnRegressor.predict(plsrFeatures, bpnnFeatures)
        result = regressionResultWarpper(preds, bpnnLabels)
        return result
    result = {
        'code' : 404,
        'massage' : 'null filemapper id'
    }
    return result
def saveSoilSample(fid, preds, regressor):
    #如果库中没有该excel文件的样本数据则存库
        samples = metadata.SoilSample.query.filter_by(fid = fid, regressor=regressor).first()
        print(samples)
        if samples == None:
            samples = []
            for i in range(len(preds)):
                soilSample = metadata.SoilSample()
                soilSample.fid = fid
                soilSample.sid = i
                soilSample.som_value = preds[i]
                soilSample.regressor = regressor
                samples.append(soilSample)
            try:
                db.session.add_all(samples)
                db.session.commit()
            except:
                db.session.rollback()
            finally:
                db.session.close()
@app.route('/findsample', methods = ['GET', 'POST'])
def findSample():
    fid = request.args.get('fid')
    page = int(request.args.get('page'))
    pageSize = 20
    regressor = request.args.get('regressor')
    paginateObj = metadata.SoilSample.query.filter_by(fid = fid, regressor = regressor).paginate(page, pageSize, error_out = False)
    samples = paginateObj.items
    total = paginateObj.total
    currentPage = paginateObj.page
    data = []
    for s in samples:
        data.append({
            'id':s.id,
            'fid':s.fid,
            'sid':s.sid + 1,
            'somValue':s.som_value,
            'regressor':s.regressor
        })
    result = {
        'code' : 200,
        'massage' : 'ok',
        'data':data,
        'page':currentPage,
        'total':total,
        'pageSize':pageSize
    }
    return result
@app.route('/guide', methods = ['GET', 'POST'])
def level():
    fid = request.args.get('fid')
    regressor = request.args.get('regressor')
    if regressor in ['plsr', 'bpnn', 'bp', 'svr']:
        if regressor == 'plsr':
            result = plsrguide(fid)
        elif regressor == 'bpnn':
            result = bpnnguide(fid)
        elif regressor == 'bp':
            result = bpguide(fid)
        elif regressor == 'svr':
            result = svrguide(fid)
        saveSoilSample(fid, result['data']['preds'], regressor)
    else:
        result = {'code':404, 'message':'not that %sregressor'%regressor}
    return jsonify(result)
@app.route('/findall', methods = ['GET', 'POST', 'OPTIONS'])
def findall():
    page = int(request.args.get('page'))
    pageSize = 10
    paginateObj = metadata.FileMapper.query.paginate(page, pageSize, error_out = False)
    fileMappers = paginateObj.items
    total = paginateObj.total
    currentPage = paginateObj.page
    data = []
    for f in fileMappers:
        data.append({'id':f.id, 'filename':f.filename})
    result = {
        'code' : 200,
        'massage' : 'ok',
        'data':data,
        'page':currentPage,
        'total':total,
        'pageSize':pageSize
    }
    return jsonify(result)
if __name__ == '__main__':
    app.run()
    CORS(app)
