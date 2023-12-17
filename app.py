from flask import Flask, url_for, render_template, request, redirect, flash
from markupsafe import escape
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey
from datetime import datetime
import click
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager
from flask_login import UserMixin
from flask_login import login_user
from flask_login import login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = 'a_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #关闭对模型修改的监控
#在扩展类实例化前家在配置

login_manager = LoginManager(app) # 实例化扩展类
login_manager.login_view = 'login'
@login_manager.user_loader
def load_user(user_id):  # 创建用户加载回调函数，接受用户 ID 作为参数
    user = User.query.get(int(user_id))  # 用 ID 作为 User 模型的主键查询对应的用户
    return user  # 返回用户对象

db = SQLAlchemy(app) #初始化扩展，传入程序实例
class User(db.Model, UserMixin): #表名是user
    id = db.Column(db.Integer,primary_key = True) #主键
    name = db.Column(db.String(20)) #名字
    username = db.Column(db.String(20))  # 用户名
    password_hash = db.Column(db.String(128))  # 密码散列值

    def set_password(self, password):  # 用来设置密码的方法，接受密码作为参数
        self.password_hash = generate_password_hash(password)  # 将生成的密码保持到对应字段
    def validate_password(self, password):  # 用于验证密码的方法，接受密码作为参数
        return check_password_hash(self.password_hash, password)  # 返回布尔值

class movie_info(db.Model):
    __tablename__ = 'movie_info'
    movie_id = db.Column(db.String(10), primary_key = True) #主键
    movie_name = db.Column(db.String(60)) #电影标题
    release_date = db.Column(db.String(10)) #电影具体日期
    country = db.Column(db.String(2))#出品国家
    type = db.Column(db.String(2))#电影种类
    year = db.Column(db.Integer) #电影年份
    actors = db.relationship('actor_info', secondary = 'movie_actor_relation', backref = 'movie_info')
    # rela_movie = db.relationship('movie_actor_relation', backref='movie_info')
class move_box(db.Model):
     movie_id  = db.Column(db.String(10), primary_key=True)
     box = db.Column(db.Float)
class actor_info(db.Model):
    __tablename__ = 'actor_info'
    actor_id = db.Column(db.String(10), primary_key=True)
    actor_name = db.Column(db.String(20))
    gender = db.Column(db.String(2))
    country = db.Column(db.String(20))
    # rela_actor = db.relationship('movie_actor_relation', backref='actor_info')

class movie_actor_relation(db.Model):
    __tablename__ = 'movie_actor_relation'
    id = db.Column(db.String(10), primary_key=True)
    movie_id = db.Column(db.String(10), db.ForeignKey('movie_info.movie_id'))
    actor_id = db.Column(db.String(10), db.ForeignKey('actor_info.actor_id'))
    relation_type = db.Column(db.String(20), primary_key=True)
    # movie_rela = relationship('movie_info', backref='rela_movie')
    # actor_rela = relationship('actor_info', backref='rela_actor')


# @app.route('/user/<name>')
# def user_page(name):
#     return 'Uswer: %s' %name
# @app.route('/test')
# def test_url_for():
#     print(url_for('index'))
#     return url_for('index')

#
# @app.cli.command() #注册为命令，执行命令就会调用后面的函数
# def forge():
#     """Generate fake data."""
#     db.create_all()
#     name = 'Xiaoxi Li'
#     movies = [
#         {'id': '1001', 'title': 'My Neighbor Totoro', 'year': '1988'},
#         {'title': 'Dead Poets Society', 'year': '1989'},
#         {'title': 'A Perfect World', 'year': '1993'},
#         {'title': 'Leon', 'year': '1994'},
#         {'title': 'Mahjong', 'year': '1996'},
#         {'title': 'Swallowtail Butterfly', 'year': '1996'},
#         {'title': 'King of Comedy', 'year': '1999'},
#         {'title': 'Devils on the Doorstep', 'year': '1999'},
#         {'title': 'WALL-E', 'year': '2008'},
#         {'title': 'The Pork of Music', 'year': '2012'},
#     ]
#
#     user = User(name = name)
#     db.session.add(user)
#     for m in movies:
#         movie = movie_info(title = m['title'], year = m['year'])
#         db.session.add(movie)
#
#     db.session.commit()
#     click.echo('Done')

@app.cli.command() #注册为命令，执行命令就会调用后面的函数
@click.option('--drop', is_flag=True, help='Create after drop.') #‘--drop’是一个布尔选项，不需要任何附加参数
def initdb(drop): #只需要一个drop参数，对应于'--drop'
    """Initialize the database"""
    if drop: #判断是否输入了选项
        db.drop_all()
    db.create_all() #创建SQLAlchemy模型中定义的所有表
    click.echo('Initialized database.') #输出提示信息：已经初始化

@app.context_processor #注册一个模板上下文处理函数，处理多个模板内都需要使用的变量
def inject_user():
    user = User.query.first()
    return dict(user=user) #返回字典，等同于return{'user':user}

@app.errorhandler(404)
def page_not_found(e):
    # user = User.query.first()
    return render_template('404.html'), 404

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if not current_user.is_authenticated:  # 如果当前用户未认证
            return redirect(url_for('index'))  # 重定向到主页
        id = request.form.get('movie_id')
        title = request.form.get('title')
        year = request.form.get('year')
        date = request.form.get('date')
        country = request.form.get('country')
        type = request.form.get('type')
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('index'))
        movie = movie_info(movie_id = id, movie_name = title, year = year, type = type, country = country, release_date = date)
        db.session.add(movie)
        db.session.commit()
        flash('Item created.')
        return redirect(url_for('index'))

    # user = User.query.first() #读取用户记录
    movies = movie_info.query.all() #读取所有电影记录
    return render_template('index.html', movies = movies)

@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def edit(movie_id):
    movie = movie_info.query.get_or_404(movie_id) #如果找不到就返回404错误响应

    if request.method == 'POST':  # 处理编辑表单的提交请求
        title = request.form['title']
        year = request.form['year']
        date = request.form['date']
        country = request.form['country']
        type = request.form['type']

        if not title or not year or len(year) != 4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('edit', movie_id=movie_id))  # 重定向回对应的编辑页面

        movie.movie_name = title  # 更新标题
        movie.release_date = date
        movie.country = country
        movie.type = type
        movie.year = year  # 更新年份
        db.session.commit()  # 提交数据库会话
        flash('Item updated.')
        return redirect(url_for('index'))  # 重定向回主页

    return render_template('edit.html', movie=movie)  # 传入被编辑的电影记录


@app.route('/movie/delete/<int:movie_id>', methods=['POST'])  # 限定只接受 POST 请求
@login_required
def delete(movie_id):
    movie = movie_info.query.get_or_404(movie_id)  # 获取电影记录
    db.session.delete(movie)  # 删除对应的记录
    db.session.commit()  # 提交数据库会话
    flash('Item deleted.')
    return redirect(url_for('index'))  # 重定向回主页

@app.cli.command()
@click.option('--username', prompt=True, help='The username used to login.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login.')
def admin(username, password):
    """Create user."""
    db.create_all()
    user = User.query.first()
    if user is not None:
        click.echo('Updating user...')
        user.username = username
        user.set_password(password)  # 设置密码
    else:
        click.echo('Creating user...')
        user = User(username=username, name='Xiaoxi Li')
        user.set_password(password)  # 设置密码
        db.session.add(user)

    db.session.commit()  # 提交数据库会话
    click.echo('Done.')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login')) #回到login地址

        user = User.query.first()
        # 验证用户名和密码是否一致
        if username == user.username and user.validate_password(password):
            login_user(user)  # 登入用户
            flash('Login success.')
            return redirect(url_for('index'))  # 重定向到主页

        flash('Invalid username or password.')  # 如果验证失败，显示错误消息
        return redirect(url_for('login'))  # 重定向回登录页面

    return render_template('login.html')

@app.route('/logout')
@login_required  # 用于视图保护，后面会详细介绍
def logout():
    logout_user()  # 登出用户
    flash('Goodbye.')
    return redirect(url_for('index'))  # 重定向回首页

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']

        if not name or len(name) > 20:
            flash('Invalid input.')
            return redirect(url_for('settings'))

        current_user.name = name
        # current_user 会返回当前登录用户的数据库记录对象
        # 等同于下面的用法
        # user = User.query.first()
        # user.name = name
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('index'))

    return render_template('settings.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    # movie = movie_info.query.get_or_404(movie_id) #如果找不到就返回404错误响应
    if request.method == 'POST':  # 处理编辑表单的提交请求
        title = request.form['title']

        # if not title or not year or len(year) != 4 or len(title) > 60:
        #     flash('Invalid input.')
        #     return redirect(url_for('edit', movie_id=movie_id))  # 重定向回对应的编辑页面

        # movie.title = title  # 更新标题
        # movie.year = year  # 更新年份
        # db.session.commit()  # 提交数据库会话
        # flash('Item updated.')
        movies = movie_info.query.filter(movie_info.movie_name.like(f"%{title}%")).all() #读取所有电影记录

        movie_list = list()
        for movie in movies:
            actors = movie.actors
            actor_list = list()
            for actor in actors:
                actor_name = actor.actor_name
                actor_type = movie_actor_relation.query.filter_by(movie_id = movie.movie_id, actor_id = actor.actor_id).first().relation_type
                actor_list.append([actor_name,actor_type])
            movie_list.append([movie.movie_id, movie.movie_name, movie.release_date, movie.type, actor_list])
                # print(actor_type.relation_type)

        return render_template('search_result.html', movies=movie_list)

    return render_template('search.html')  # 传入被编辑的电影记录
