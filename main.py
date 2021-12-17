from datetime import datetime
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

# connect to db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# configure table
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


# wtf form
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


@app.route('/')
def get_all_posts():
    posts = db.session.query(BlogPost).all()
    return render_template("index.html", all_posts=posts)


@app.route("/post/<int:index>")
def show_post(index):
    requested_post = db.session.query(BlogPost).filter_by(id=index).first()
    return render_template("post.html", post=requested_post)


@app.route('/new-post', methods=['GET', 'POST'])
def new_post():
    form = CreatePostForm()
    if request.method == 'POST':
        rq = request.form.get
        date = datetime.now().strftime('%B %d, %Y')
        new_blog_post = BlogPost(title=rq('title'), date=date, subtitle=rq('subtitle'),
                                 author=rq('author'), img_url=rq('img_url'), body=rq('body'))
        db.session.add(new_blog_post)
        db.session.commit()
        return redirect(url_for('get_all_posts'))
    return render_template('make-post.html', form=form, header='New Post')


@app.route('/edit-post/<post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    requested_post = db.session.query(BlogPost).filter_by(id=post_id).first()
    rp = requested_post
    if request.method == 'GET':
        form = CreatePostForm(title=rp.title, date=rp.date, subtitle=rp.subtitle,
                              author=rp.author, img_url=rp.img_url, body=rp.body)
        return render_template('make-post.html', form=form, header='Edit Post')
    else:
        rq = request.form.get
        edited_blog_post = BlogPost(title=rq('title'), date=rp.date, subtitle=rq('subtitle'),
                                    author=rq('author'), img_url=rq('img_url'), body=rq('body'))
        ebp = edited_blog_post
        rp.title = ebp.title
        rp.date = ebp.date
        rp.subtitle = ebp.subtitle
        rp.author = ebp.author
        rp.img_url = ebp.img_url
        rp.body = ebp.body
        db.session.commit()
        return redirect(url_for('show_post', index=requested_post.id))


@app.route('/delete/<post_id>', methods=['GET', 'DELETE'])
def delete_post(post_id):
    selected_post = db.session.query(BlogPost).filter_by(id=post_id).first()
    db.session.delete(selected_post)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True)
