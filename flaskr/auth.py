import functools

import jwt
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify, make_response, current_app,
)
from flask_cors import cross_origin

from werkzeug.security import check_password_hash, generate_password_hash

import flaskr
from flaskr.db import get_db

from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

import logging
logger = logging.getLogger(__name__)


bp=Blueprint('auth',__name__,url_prefix='/auth')
#创建蓝图对象auth


"""@bp.route 关联了 URL /register 和 register 视图函数。
当 Flask 收到一个指向 /auth/register 的请求时就会调用 register 视图并把其返回值作为响应。"""

@bp.route('/register',methods=('GET','POST'))
# @cross_origin()
def register():
    """如果用户提交了表单，那么 request.method 将会是 'POST' 。这咱情况下 会开始验证用户的输入内容。"""
    if request.method=='POST':
        # username=request.form['username']
        # password=request.form['password']
        data=request.get_json()
        username=data['username']
        password=data['password']
        #接受用户名和密码 request.form是一种dict，可以通过key username password提取

        db=get_db()

        error=None

        if not username:
            error="Username is required"
            return jsonify({'message':f'{error}'}),400
        elif not password:
            error="Password is required"
            return jsonify({'message': f'{error}'}), 400
            #验证用户名密码不为空
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error='User {} is already registered'.format(username)
        # db.execute 使用了带有 ? 占位符 的 SQL 查询语句。
        # 占位符可以代替后面的元组参数中相应的值。使用占位符的 好处是会自动帮你转义输入值，
        # 以抵御 SQL 注入攻击 。
        # 例如 'SELECT id FROM user WHERE username = ?', (username,) 问号占位符和元组username互换。
        # fetchone() 根据查询返回一个记录行。 如果查询没有结果，则返回 None 。后面还用到 fetchall() ，它返回包括所有结果的列表。
        if error is None:
            db.execute(
                'INSERT INTO user (username,password) VALUES (?,?)',
                (username,generate_password_hash((password)))
            )
            #这个和上一句同理，values(?,?)占位符和元组(username,password)互相替换
            db.commit()
            #保存修改
            # return redirect(url_for('auth.login'))
            return jsonify({'message':'Register Successful'})
        #用户数据保存后将转到登录页面。
        # url_for() 根据登录视图的名称生成相应的 URL 。
        # 与写固定的 URL 相比， 这样做的好处是如果以后需要修改该视图相应的 URL ，
        # 那么不用修改所有涉及到 URL 的代码。
        # redirect() 为生成的 URL 生成一个重定向响应。
        # flash(error)
        # 如果验证失败，那么会向用户显示一个出错信息。
        # flash() 用于储存在渲染模块时可以调用的信息。
    #return render_template('auth/register.html')


@bp.route('/login', methods=['GET','POST','OPTIONS'])
# @cross_origin(origin='localhost:5173')
def login():
    if request.method=='POST':
        data = request.get_json()
        username=data['username']
        password=data['password']
        db=get_db()
        error=None
        user=db.execute(
            'SELECT * FROM user WHERE username = ?',(username,)
        ).fetchone()
        #fetchone 返回一行查询结果

        if user is None:
            error = "username not exist"
            return jsonify({"message": "Username Wrong"}), 400

        elif not check_password_hash(user['password'],password):
            error = "Wrong password"
            return jsonify({"message": "Wrong password"}), 400

            # check_password_hash() 以相同的方式哈希提交的 密码并安全的比较哈希值。
            # 如果匹配成功，那么密码就是正确的。

        if error is None:
            session.clear()
            session['user_id']=user['id']
            # return redirect(url_for('blog.index'))
            access_token=create_access_token(identity=user['id'])
            refresh_token=create_access_token(identity=user['id'])
            return jsonify({'message':'Login Successful','AccessToken':access_token,'RefreshToken':refresh_token})#直接返回jwt

        #session 是一个 dict ，它用于储存横跨请求的值。
        # 当验证 成功后，用户的 id 被储存于一个新的会话中。
        # 会话数据被储存到一个 向浏览器发送的 cookie 中，在后继请求中，浏览器会返回它。
        # Flask 会安全对数据进行 签名 以防数据被篡改
    #     flash(error)
    # return render_template('auth/login.html')
    else:
        return jsonify({"message": "This is a GET request. Use POST to login."})





@bp.route('/getusername',methods=['GET'])
def getusername():
    if request.method=='GET':
        user_id=g.user
        if user_id:
            print('have username')
            print(g.user)
            return jsonify({"username": user_id})
        else:
            return jsonify({"username": "None"})


@bp.before_app_request
def load_logged_in_user():
    # logger.debug('Entering load_logged_in_user function')
    # print('load_logged_in_user is being called')
    # user_id=session.get('user_id')
    # print(session)
    #
    # if user_id is None:
    #     g.user=None
    # else:
    #     g.user=get_db().execute(
    #         'SELECT * FROM user WHERE id= ?', (user_id,)
    #     ).fetchone()
    print(request.headers)
    if request.headers.get('Authorization'):
        # token=jwt.decode(request.headers['Authorization'],current_app.config['SECRET_KEY'], algorithms='HS256')
        # user_id=token['sub']
        user_id=get_jwt_identity()
        # print(user_id)
        if user_id is None:
            g.user=None
        else:
            g.user=get_db().execute(
                'SELECT username FROM user WHERE id= ?', (user_id,)
            ).fetchone()
        # print(dict(g.user))
        user=dict(g.user)
        g.user=user['username']

    else:
        g.user=None




@bp.route('/logout' ,methods=['GET'])

def logout():
    print('logout')
    session.clear()
    g.user='None'
    print(g.user)
    # return  redirect(url_for('auth.login'))
    return jsonify({'message':'Logout Successful'})
# def login_required(view):
#     @functools.wraps(view)
#     def wrapped_view(**kwargs):
#         if g.user is None:
#             return redirect(url_for('auth.login'))
#         return view(**kwargs)
#     return wrapped_view
#使用jwt_required() 装饰器来保护视图函数。放弃自己实现login required装饰器。
