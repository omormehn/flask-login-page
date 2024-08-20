from flask import redirect, render_template, url_for, flash, request
from blog import app, db, bcrypt
from blog.forms import RegistrationForm, LoginForm, Update_Form
from blog.modules import User, Post
from flask_login import login_user, current_user, logout_user, login_required
import secrets 
import os


#list of dictionarries to represent a single blog post
posts = [
    {
        'author': 'Nathan Useni',
        'title' : 'A work in Progress',
        'content': 'Basic flask project with no special stuffs, for learning purposes',
        'date_posted': 'gooood'
    },
    {
        'author': '2',
        'title' : '2',
        'content': '2',
        'date_posted': '2'
    },
]




@app.route('/')
def home():
    return render_template('source.html', posts=posts)
#the first posts represent the html temp, while the second rep the lists of dic

@app.route('/administration')
def administration_page():
    return render_template('some.html', title='Administration')
@app.route('/faculty')
def faculty():
    return render_template('faculty.html', title='Faculty')
@app.route('/news')
def news_page():
    return render_template('news.html', title='News')
@app.route('/about')
def about_page():
    return render_template('about.html', title='About')
@app.route('/contact_page')
def contact_page():
    return render_template('contact us.html', title='Contact')

@app.route('/register', methods=['GET' , 'POST'])
def register():

    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created! Login to continue', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET' , 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
      
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username= form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='login', form=form)
@app.route('/logout')
def exit():
    logout_user()
    return redirect(url_for('home'))

def save_pic(form_picture):
    random_hex = secrets.token_hex(8)
    f_name, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    form_picture.save(picture_path)

    return picture_fn

@app.route('/account', methods=['GET' , 'POST'])
@login_required
def account():
    form=Update_Form()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_pic(form.picture.data)
            current_user.image_file = picture_file
        current_user.username=form.username.data
        current_user.email=form.email.data
        db.session.commit()
        flash('Your account has been Updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data=current_user.username
        form.email.data=current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    
    return render_template('account.html',
                        title='Account', image_file=image_file, form=form)
    