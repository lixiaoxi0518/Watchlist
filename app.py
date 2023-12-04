from flask import Flask, url_for, render_template, request, redirect, flash
from markupsafe import escape
import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import click

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #关闭对模型修改的监控
#在扩展类实例化前家在配置

db = SQLAlchemy(app) #初始化扩展，传入程序实例
class User(db.Model): #表名是user
    id = db.Column(db.Integer,primary_key = True) #主键
    name = db.Column(db.String(20)) #名字

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key = True) #主键
    title = db.Column(db.String(60)) #电影标题
    year = db.Column(db.String(4)) #电影年份


# @app.route('/user/<name>')
# def user_page(name):
#     return 'Uswer: %s' %name
# @app.route('/test')
# def test_url_for():
#     print(url_for('index'))
#     return url_for('index')


@app.cli.command() #注册为命令，执行命令就会调用后面的函数
def forge():
    """Generate fake data."""
    db.create_all()
    name = 'Xiaoxi Li'
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1988'},
        {'title': 'Dead Poets Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Devils on the Doorstep', 'year': '1999'},
        {'title': 'WALL-E', 'year': '2008'},
        {'title': 'The Pork of Music', 'year': '2012'},
    ]

    user = User(name = name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title = m['title'], year = m['year'])
        db.session.add(movie)

    db.session.commit()
    click.echo('Done')
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
        title = request.form.get('title')
        year = request.form.get('year')
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('index'))
        movie = Movie(title = title, year = year)
        db.session.add(movie)
        db.session.commit()
        flash('Item created.')
        return redirect(url_for('index'))

    # user = User.query.first() #读取用户记录
    movies = Movie.query.all() #读取所有电影记录
    return render_template('index.html', movies = movies)

@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id) #如果找不到就返回404错误响应

    if request.method == 'POST':  # 处理编辑表单的提交请求
        title = request.form['title']
        year = request.form['year']

        if not title or not year or len(year) != 4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('edit', movie_id=movie_id))  # 重定向回对应的编辑页面

        movie.title = title  # 更新标题
        movie.year = year  # 更新年份
        db.session.commit()  # 提交数据库会话
        flash('Item updated.')
        return redirect(url_for('index'))  # 重定向回主页

    return render_template('edit.html', movie=movie)  # 传入被编辑的电影记录

@app.route('/movie/delete/<int:movie_id>', methods=['POST'])  # 限定只接受 POST 请求
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)  # 获取电影记录
    db.session.delete(movie)  # 删除对应的记录
    db.session.commit()  # 提交数据库会话
    flash('Item deleted.')
    return redirect(url_for('index'))  # 重定向回主页
