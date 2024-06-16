import datetime
import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

def create_app(test_config=None):
    #create and configure the app
    app=Flask(__name__,instance_relative_config=True)
    #Flask类实例 参数1：当前模块的名称 参数2：配置文件的相对路径，实例文件夹在 flaskr 包的外面，用于存放本地数据（例如配置密钥和数据库），不应当 提交到版本控制系统。

    # CORS(app, resources={r"/*": {"origins": "http://localhost:5173", "allow_credentials": True}})
    CORS(app, origins='http://localhost:5173',supports_credentials=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path,'flask.sqlite'),
        JWT_ACCESS_TOKEN_EXPIRES=datetime.timedelta(minutes=0.5),
    )
#jwt配置

    jwt= JWTManager(app)

    #设置一个默认配置
    """SECRET_KEY 是被 Flask 和扩展用于保证数据安全的。
    在开发过程中， 为了方便可以设置为 'dev' ，
    但是在发布的时候应当使用一个随机值来 重载它。
    DATABASE SQLite 数据库文件存放在路径。它位于 Flask 用于存放实例的 app.instance_path 之内。
    下一节会更详细 地学习数据库的东西。"""
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py',silent=True)
        """通过py文件来加载配置"""
    else:
        app.config_class.from_mapping(test_config)
        """否则通过test_config加载配置"""


    try:
        os.makedirs((app.instance_path))
    except OSError:
        pass

    @jwt.expired_token_loader
    def my_expired_token_callback(jwt_header, jwt_payload):
        return jsonify(code="401", err="Token expired"), 401
    @app.route('/hello')

    def hello():
        return 'Hello, World!'
    """路由装饰器"""


#自定义JWT过期错误

    from . import db
    db.init_app(app)
    # 注册数据库
    from. import auth
    app.register_blueprint(auth.bp)
    # 注册认证组件
    from. import blog
    app.register_blueprint(blog.bp)
    # app.add_url_rule('/', endpoint='index')
    # 注册博客组件

    return app