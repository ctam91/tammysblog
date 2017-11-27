from datetime import datetime
from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://zvuirkakufqxjv:b51d1522d2b84250a368df5e5089e24af06dcddd9791c449f4ea31c07a8de964@ec2-54-83-28-144.compute-1.amazonaws.com:5432/deem7qfpn7d714'
#app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
app.secret_key = 'sunflowerseeds'

# Create a Blog class with id, title, body, and owner_id columns. A relationship is created between Blog and User tables through usage of foreign key in owner_id(Blog) and blogs(User) properties. 
class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    pub_date = db.Column(db.DateTime)

# Iniitaliz title, body, and owner properties for Blog object. 
    def __init__(self, title, body, owner, pub_date=None):
        self.title = title
        self.body = body
        self.owner = owner
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date

#create a User class with id, username, password, and blogs columns. 'blogs' links to Blogs table. 
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

# Initialize username and hashed password properties for User object. 
    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)

# User is allowed to visit /login, /signup, /blog, /index, and static folder items if they are not logged on. If user wants to access a different site and are not logged in, then redirect them to login page ..
@app.before_request
def require_login():
    not_allowed_routes = ['newpost']
    if request.endpoint in not_allowed_routes and 'username' not in session:
        return redirect('/login')

# Create /newpost route and renders add template. If user leaves title or body blank, then return errors. 
@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    '''
    Creates a new blog post
    '''
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        owner = User.query.filter_by(username=session['username']).first()

        if title == "":
            flash("Please fill in the title", "error")

        if body == "":
            flash("Please fill in the body", "error")
            
        if len(title) > 1 and len(body) > 1:   
            new_post = Blog(title, body, owner) #create an instance of a Blog class called new_post
            db.session.add(new_post) 
            db.session.commit() 
            blog_id = str(new_post.id) 
            return redirect('/blog?id='+blog_id)
        else: 
            return render_template('newpost.html', title=title, body=body)
        
    return render_template('newpost.html')

# Create /blog route to display blog
@app.route('/blog', methods=['POST', 'GET'])
def blog():
    '''
    Show all blog entries
    '''
    # Retrieve id of blog post from the url 
    blog_id = request.args.get('id')

    # If a blog_id is retrieved from the url, send your db a query and find the post associated with that id. Render post.html with that post's title and blog
    if blog_id:
        post = Blog.query.filter_by(id=blog_id).first()
        return render_template("post.html", title=post.title, body=post.body, pub_date=post.pub_date)

    # If there are no specific posts to retrieve, show entire blog
    titles = Blog.query.all()
    return render_template('blog.html',titles=titles)

# Create /login route to allow user to login 
@app.route('/login', methods=['POST', 'GET'])
def login():
    '''
    Shows login page and login form
    '''
    # If it is a post method, the user is trying to login and we need to verify email, password, and if user exists in database
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_pw_hash(password, user.pw_hash):
            session['username'] = username   
            flash("Logged in",'info')
            return redirect('/newpost')

        if username == "" and password == "":
            flash('Please enter a username and password','error')

        if user and user.pw_hash != password:
            flash('User password incorrect', 'error')

        if not user and len(password) > 1:
            flash('Please enter a username', 'error')

        if not user and len(username) > 1:
            flash('User does not exist', 'error')

        return render_template('login.html', username=username)

    return render_template('login.html')

# Create /signup route for users to sign up. Return errors if form is filled out incorrectly.
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    '''
    Shows signup page and signup form
    '''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()

        if username == "" or len(username) <= 3:
            flash("Please provide a valid username. Usernames should be more than 3 characters", "error")

        if password == "" or len(password) <= 3:
            flash("Please provide a valid password. Password must be between 3-20 charcters", "error")
        
        if password != verify or verify =="":
            flash("Passwords do not match", "error")

        if existing_user:
            flash("Duplicate username", 'error')

        if len(username) > 3 and len(password) > 3 and password==verify and not existing_user: 
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            return render_template('signup.html', username=username)

    return render_template('signup.html')

# Logs user out and deletes their session
@app.route('/logout')
def logout():
    '''
    Deletes session and logs user out
    '''
    if session: 
        del session['username']
        flash('Logged out','info')
    else:
        flash('You must be logged in to log out', 'info')
        return redirect('/login')
    return redirect('/')

@app.route('/dashboard')
def dashboard():
    '''
    Dashboard for Tammy 
    '''
    return render_template('dashboard.html')


# Index route displays homepage
@app.route('/')
def index():
    return render_template('mainpage.html')

if __name__ == '__main__':
    app.run()