
from flask import Flask, render_template, redirect, url_for
from flask_restful import Api, Resource, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,  login_user, login_required, current_user, logout_user, UserMixin
from datetime import datetime
from functions import resizeImg
import urllib.request
import os 



app = Flask(__name__)
api = Api(app)
login_manager = LoginManager(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = 'initialkey' 

db = SQLAlchemy(app)

class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(10), unique=True, nullable=False)
    email = db.Column(db.String(15),  unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    joined  = db.Column(db.Date, default=datetime.utcnow)
    avatar = db.Column(db.String)
    movies = db.relationship('Moviestack', backref='user', lazy=True)
    comments = db.relationship('Comments', backref='user', lazy=True)
    images = db.relationship('Image', backref='user', lazy=True)
    def __repr__(self):
        return f"User {self.username}, {self.email}"
@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(int(user_id))

class Moviestack(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    movieName = db.Column(db.String(10), unique=True, nullable=False)
    year = db.Column(db.Integer, db.CheckConstraint('year >= 1800 AND year <= 3000'))
    addedBy = db.Column(db.Integer, db.ForeignKey("user.id"))
    date = db.Column(db.Date, default=datetime.utcnow)
    comments = db.relationship('Comments', backref='moviestack', lazy=True)

class Comments(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(10),db.ForeignKey("user.id") )
    Movie = db.Column(db.String(10), db.ForeignKey("moviestack.id"))
    date  = db.Column(db.Date, default=datetime.utcnow)

class Image(db.Model):
    __tablename__ = 'images'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(100), nullable=False)
    date  = db.Column(db.Date, default=datetime.utcnow)





@app.route("/", methods = ['GET','POST'])
def home():
    return render_template("main.html")

@app.route('/register')
def register():
    if current_user:
        if current_user.is_authenticated:
            logout_user()
    return render_template('register.html')

@app.route('/movie')
@login_required
def movie():
    if current_user.is_authenticated:
        print(f"User is autenticated {current_user}")
        user_data = {
            'username': current_user.username,
            'email': current_user.email,
        }

        return render_template('movie.html', user_data=user_data)
    else:
        return redirect(url_for('main.html'))
  


class UsersLogin(Resource):
    def post(self):
        item = request.json
        print(f"From post {item}")
        if User.query.filter_by(email  = item.get('email'), password=item.get('password')).first() != None:
            user = User.query.filter_by(email  = item.get('email'), password=item.get('password')).first()
            login_user(user)
            response_message = "ok"
            return {"message": response_message}, 201
        else:
            response_message = "nol"
            return {"message": response_message}, 201
    def put(self):
        item = request.json
        print(f"{current_user} is active, goodbye")
        if item.get('message') == "logOut" and current_user.is_authenticated:
            try:
                logout_user()
                return {"message" : "succes"}
            except:
                return {"message" : "somethingWentWrong"}



class UserRegister(Resource):
    def post(self):

        item = request.json

        if User.query.filter_by(email  = item.get('email')).first() == None:
            userEmail = item.get('email')
            userPassword = item.get('password')
            userNick = item.get('nick')
            print(userEmail)
            print(userPassword)
            print(userNick)
            newUser = User(username=userNick,email= userEmail,password=userPassword, avatar = "default")
            db.session.add( newUser )
            db.session.commit()
            response_message = "ok"
            return {"message": response_message}, 201
        else:
            response_message = "no"
            return {"message": response_message}, 201

class UserAlter(Resource):
    
    def put(self):
  
        try:
            item = request.json
        
            if item.get('newEmail'):
                new = item.get('newEmail')
                current_user.email = new
            elif item.get('oldPassword'):
                print(f"current password {current_user.password}")
                
                if item.get('oldPassword') != current_user.password:
                    return {"message" : "old_password"}
                else:
                    current_user.password = item.get("newPassword")
                
            else:
                new = item.get('newNick')
                current_user.username = new
                
            if current_user.is_authenticated:
                db.session.commit()
                return {"message" : "ok"}
               
        except:
            return {"message" : "error"}
        
    def post(self):
        print("hi post ", current_user.id)
        if 'file' not in request.files:
            print("problem")
            return {'message': 'No file part'}, 400
        
       
        print("img request")
        file = request.files['file']
        img_db = Image(user_id= current_user.id, name=file.filename )
        db.session.add(img_db)
        db.session.commit()
        key = img_db.id
        print(f" key {key}")
        resizeImg(img=file, name=file.filename, key= key)

        return {'message' : 'ok'}

    
class SetAvatar(Resource):
    def get(self):
        try:
            return {"current_avatar" : current_user.avatar}
        except:
            return {'message': 'no'}
        
    def put(self):
        
        item= request.json
        current_user.id
        imgs_list = ['static/default.png']
        for img in os.listdir('images'):
            imgs_list.append(f'images/{img}')
        return {'data' :imgs_list}
        
        
        
       
        
api.add_resource(UsersLogin,"/log")
api.add_resource(UserRegister,"/new_user_reg")
api.add_resource(UserAlter,'/alter')
api.add_resource(SetAvatar,'/avatar')


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000, debug=True)
    db.init_app(app)