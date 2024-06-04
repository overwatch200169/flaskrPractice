import functools

from flask import(
Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp=Blueprint('auth',__name__,url_prefix='/auth')
#创建蓝图对象auth


"""@bp.route 关联了 URL /register 和 register 视图函数。
当 Flask 收到一个指向 /auth/register 的请求时就会调用 register 视图并把其返回值作为响应。"""

@bp.route('/register',methods=('GET','POST'))
def register():
    """如果用户提交了表单，那么 request.method 将会是 'POST' 。这咱情况下 会开始验证用户的输入内容。"""
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        #接受用户名和密码 request.form是一种dict，可以通过key username password提取吧卢瑟

        db=get_db()

        error=None

        if not username:
            error="Username is required"
        elif not password:
            error="Password is required"
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
            return redirect(url_for('auth.login'))
        #用户数据保存后将转到登录页面。
        # url_for() 根据登录视图的名称生成相应的 URL 。
        # 与写固定的 URL 相比， 这样做的好处是如果以后需要修改该视图相应的 URL ，
        # 那么不用修改所有涉及到 URL 的代码。
        # redirect() 为生成的 URL 生成一个重定向响应。
        flash(error)
        # 如果验证失败，那么会向用户显示一个出错信息。
        # flash() 用于储存在渲染模块时可以调用的信息。
    return render_template('auth/register.html')


@bp.route('/login', methods=('GET','POST'))
def login():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        db=get_db()
        error=None
        user=db.execute(
            'SELECT * FROM user WHERE username = ?',(username,)
        ).fetchone()
        #fetchone 返回一行查询结果

        if user is None:
            error = "username not exist"
        elif not check_password_hash(user['password'],password):
            error = "Wrong password"
            # check_password_hash() 以相同的方式哈希提交的 密码并安全的比较哈希值。
            # 如果匹配成功，那么密码就是正确的。
        print(error)
        if error is None:
            session.clear()
            session['user_id']=user['id']
            return redirect(url_for('blog.index'))
        #session 是一个 dict ，它用于储存横跨请求的值。
        # 当验证 成功后，用户的 id 被储存于一个新的会话中。
        # 会话数据被储存到一个 向浏览器发送的 cookie 中，在后继请求中，浏览器会返回它。
        # Flask 会安全对数据进行 签名 以防数据被篡改
        flash(error)
    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id=session.get('user_id')

    if user_id is None:
        g.user=None
    else:
        g.user=get_db().execute(
            'SELECT * FROM user WHERE id= ?', (user_id,)
        ).fetchone()


@bp.route('/logout')

def logout():
    session.clear()
    return  redirect(url_for('auth.login'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

