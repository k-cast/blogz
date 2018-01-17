from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "build-a-blog-secret-key"
db = SQLAlchemy(app)


class Entry(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180))
    body = db.Column(db.String(1000))
    created = db.Column(db.DateTime)

    def __init__(self, title, body ):
        self.title = title
        self.body = body
    
    def is_valid(self):
        if self.title and self.body:
            return True
        else:
            return False

@app.route("/")
def index():
    return redirect("/blog")

@app.route("/blog")
def display_blog_entries():

    entry_id = request.args.get('id')
    if (entry_id):
        entry = Entry.query.get(entry_id)
        return render_template('singlepost.html', title="Blog Entry", entry=entry)
    else:
        all_entries = Entry.query.all()   
    return render_template('blog.html', title="All Entries", all_entries=all_entries)


@app.route('/newpost', methods=['GET', 'POST'])
def newpost():

    if request.method == 'POST':
        new_post_title = request.form['title']
        new_post_body = request.form['body']
        new_post = Entry(new_post_title, new_post_body)

        if new_post.is_valid():
            db.session.add(new_post)
            db.session.commit()

            url = "/blog?id=" + str(new_post.id)
            return redirect(url)
        else:
            flash("NOT A VALID BLOG POST")
            return render_template('newpost.html', title="Create new blog post",
                new_post_title=new_post_title, new_post_body=new_post_body)

    else: 
        return render_template('newpost.html', title="Create new blog post!")

if __name__ == '__main__':
    app.run()