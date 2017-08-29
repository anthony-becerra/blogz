from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz-password@localhost:8889/blogz' #://database-user:password@database_location:port-number/database-name
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'l337s3cr37K3yz0r5@Pb&Js4ndw1ch'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    date = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self,title,body,owner,date=None):
        self.title = title
        self.body = body
        self.owner = owner
        if date == None:
            date = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        self.date = date

    def __repr__(self):
        return '<Blog %r>' % self.title


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')
    
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username

# Run following function before you call request handler for incoming request
@app.before_request 
def require_login():
    allowed_routes = ['login','signup','blog','index'] # List of routes user can see without logging in.
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', title="DragonBlogZ - Home", users=users)
    

@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == 'GET':
        return render_template('login.html', title="DragonBlogZ - Login")
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = User.query.filter_by(username=username)
        if users.count() == 1:
            user = users.first()
            if password != user.password:
                flash('bad password', 'error2')
                return redirect("/login")
            elif password == user.password:
                session['username'] = user.username
                # flash('Welcome back, '+user.username) >>> figure work around to do this AND errors on /newpost
                return redirect("/newpost")
        flash('bad username', 'error1')
        return redirect("/login")


@app.route('/logout')
def logout():
  del session['username']
  return redirect('/')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if username == '':
            flash("Please enter a username", 'username_error')
        if password == '':
            flash("Please enter a password", 'password_error')
        if verify == '':
            flash("Passwords don't match", 'verify_error')
    
        username_db_count = User.query.filter_by(username=username).count()
        if username_db_count > 0:
            # flash username error...password reminders are not implemented
            flash(username + ' is already taken', 'user_taken')
            return redirect('/signup')
        if not password or not username:
            return redirect('/signup')
        if password != verify:
            return redirect('/signup')
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        session['username'] = user.username
        return redirect("/newpost")
    else:
        return render_template('signup.html', title="DragonBlogZ - Signup")

@app.route('/blog')
def blog():

    blogs = Blog.query.order_by(Blog.date.desc()).all()
    users = User.query.all()

    blog_id = request.args.get('id')
    get_user = request.args.get('user')

    if blog_id:
        single_blog = Blog.query.filter_by(id=blog_id).first()
        return render_template('single_blog.html', title="DragonBlogZ - All Posts", single_blog=single_blog)

    if get_user:
        owner = User.query.filter_by(username=get_user).first()
        blogs = Blog.query.filter_by(owner=owner).order_by(Blog.date.desc()).all()
        return render_template('blog.html', title="DragonBlogZ - All Posts", blogs=blogs, users=users)


    return render_template('blog.html', title="DragonBlogZ - All Posts", blogs=blogs, users=users)


@app.route('/newpost', methods=["POST", "GET"])
def newpost():

    # If form is submitted, get info and pass to database. Then redirect to /blog.
    if request.method == "POST":
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']
        owner = owner = User.query.filter_by(username=session["username"]).first()
        if blog_title and blog_body:
            new_blog = Blog(blog_title, blog_body, owner)
            db.session.add(new_blog)
            db.session.commit()
            blog_id = str(new_blog.id)
            return redirect('/blog?id='+ blog_id)

        if not blog_title:
            flash("Please enter a blog title.", "error1")
        if not blog_body:
            flash("Please enter a blog body.", "error2")
        return redirect('/newpost')

    return render_template('newpost.html', title="DragonBlogZ - New Post")


if __name__ == '__main__':
  app.run()