from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '02gn28h05j'

class Blog(db.Model):
    __tablename__ = 'blog'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1200))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(20))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'blog', 'singleUser']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        #validate data

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/')
        else:
            error_text = "Username already taken"
            return render_template('signup.html', error_text = error_text)

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')

@app.route('/')
def index():
    #owner = User.query.filter_by(username=session['username']).first()
    users = User.query.all()

    return render_template("index.html", users=users)


@app.route('/newpost', methods=['POST', 'GET'])
def posting():

    owner = User.query.filter_by(username=session['username']).first()
    error_text = ''

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        
        if title == '' or body == '':
            error_text = "Please fill out all forms"
            return render_template('newpost.html', title_ph = title, body_ph = body, error_text = error_text)

        new_blog = Blog(title, body, owner)
        db.session.add(new_blog)
        db.session.commit()

        blogs = Blog.query.all()

        new_post = Blog.query.get(len(blogs))

        return render_template('postblog.html', blogs=blogs, post=new_post)
    else:
        return render_template('newpost.html')

    blogs = Blog.query.all()

    return render_template('blog.html', blogs=blogs)

@app.route('/blog')
@app.route('/blog/<bid>', methods=['GET'])
def blog():
    blogs = Blog.query.all()
    blogid=request.args.get('bid')
    if blogid:
        new_post = Blog.query.get(blogid)
        return render_template('postblog.html', blogs=blogs, post=new_post)

    else:
        return render_template('blog.html', blogs=blogs)

@app.route('/singleUser')
@app.route('/singleUser/<user>')
def singleUser():
    user_name_fetch = request.args.get('user')
    user = User.query.filter_by(username=user_name_fetch).first()
    return render_template('singleUser.html', user=user)

if __name__ == '__main__':
    app.run()

