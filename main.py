from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:blog-password@localhost:8889/build-a-blog' #://database-user:password@database_location:port-number/database-name
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'l337s3cr37K3yz0r5@Pb&J'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)

    def __init__(self,title,body):
        self.title = title
        self.body = body


@app.route('/blog')
def blog():

    blogs = Blog.query.all()

    if request.args.get('id'):
        blog_id = request.args.get('id')
        single_blog = Blog.query.filter_by(id=blog_id).first()
        return render_template('single_blog.html', title="Build-a-Blog: New Blog Entry", single_blog=single_blog)

    return render_template('blog.html', title="Build-a-Blog: New Blog Entry", blogs=blogs)


@app.route('/newpost', methods=["POST", "GET"])
def newpost():

    # If form is submitted, get info and pass to database. Then redirect to /blog.
    if request.method == "POST":
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']
        if blog_title and blog_body:
            new_blog = Blog(blog_title, blog_body)
            db.session.add(new_blog)
            db.session.commit()
            blog_id = str(new_blog.id)
            return redirect('/blog?id='+ blog_id)

        if not blog_title:
            flash("Please enter a blog title.", "error")
        if not blog_body:
            flash("Please enter a blog body.", "error")
        return redirect('/newpost')

    return render_template('newpost.html', title="Build-a-Blog: New Blog Entry")


if __name__ == '__main__':
  app.run()