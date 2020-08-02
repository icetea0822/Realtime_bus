# coding=utf-8
from flask import Flask
from flask_restful import reqparse, abort, Api, Resource, request
import bus_service as bus
import json

app = Flask(__name__)
api = Api(app)
app.config['JSON_AS_ASCII'] = False


@app.route('/numbers', methods=['POST'])
def getNumbsers():
    number = request.values.get('numbers', type=str, default='')
    response = bus.getNumbers(number)
    code = 0
    msg = ''
    return json.dumps({'code': code, 'msg': msg, 'data': response})


@app.route('/forward', methods=['POST'])
def getForward():
    number = request.values.get('number', type=str, default=-1)
    forwardOption = bus.getForward(number)
    code = 0
    msg = ''
    list = []
    if len(forwardOption) < 1:
        code = 1
        msg = '未查询到该线路车辆'
        response = {'code': code, 'msg': msg, 'data': list}
        return json.dumps(response)
    for key, value in forwardOption.items():
        entity = {}
        entity['value'] = key
        entity['description'] = value
        list.append(entity)
    response = {}
    response['code'] = code
    response['msg'] = msg
    response['data'] = list
    return json.dumps(response)


@app.route('/stop', methods=['POST'])
def getStop():
    number = request.values.get('number', type=str, default=-1)
    forward = request.values.get('forward', type=str, default=-1)
    stopOption = bus.getStopName(number, forward)
    code = 0
    msg = ''
    list = []
    if len(stopOption) < 1:
        code = 1
        msg = '未查询到该方向车辆'
        response = {'code': code, 'msg': msg, 'data': list}
        return json.dumps(response)

    for key, value in stopOption.items():
        entity = {'id': key, 'description': value}
        list.append(entity)
    response = {'code': code, 'msg': msg, 'data': list}
    return json.dumps(response)


@app.route('/info', methods=['POST'])
def getGpsInfo():
    number = request.values.get('number', type=str, default=-1)
    forward = request.values.get('forward', type=str, default=-1)
    stopId = request.values.get('stopId', type=str, default=-1)
    info = bus.getGpsInfo(number, forward, stopId)
    code = 0
    msg = ''
    list = []
    if len(info) < 1:
        code = 1
        msg = '未查询到该方向车辆'
        response = {'code': code, 'msg': msg, 'data': list}
        return json.dumps(response)
    response = {'code': code, 'msg': msg, 'data': info}
    return json.dumps(response)


if __name__ == '__main__':
    app.run()
