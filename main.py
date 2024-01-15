
from flask import Flask, render_template, redirect, url_for, jsonify, flash
from flask_restful import Api, Resource, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,  login_user, login_required, current_user, logout_user, UserMixin
from datetime import datetime
from functions import resizeImg, resizeMovieImg
import urllib.request
import os 
from  werkzeug.security import generate_password_hash, check_password_hash
import re 
from flask_cors import CORS
from flask_mail import Mail, Message

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = 'initialkey' 
app.config['CLIENT_MAX_BODY_SIZE'] = 16 * 1024 * 1024
app.config['MAIL_SERVER'] = 'smtp.seznam.cz'
app.config['MAIL_PORT'] =465
app.config['MAIL_USERNAME'] = 'projektotesanek@seznam.cz'
app.config['MAIL_PASSWORD'] = ''
app.config['MAIL_USE_TLS'] = False 
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
CORS(app)
CORS(app, origins="*")
api = Api(app)
login_manager = LoginManager(app)

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
    year = db.Column(db.Integer)
    addedBy = db.Column(db.Integer, db.ForeignKey("user.id"))
    date = db.Column(db.Date, default=datetime.utcnow)
    description = db.Column(db.String(100))
    movie_rating = db.Column(db.Integer)
    genre = db.Column(db.String(10))
    direction = db.Column(db.String(20))
    comments = db.relationship('Comments', backref='moviestack', lazy=True)

class Comments(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(10),db.ForeignKey("user.id") )
    Movie = db.Column(db.String(10), db.ForeignKey("moviestack.id"))
    date  = db.Column(db.Date, default=datetime.utcnow)
    rating = db.Column(db.Integer)
    
class Image(db.Model):
    __tablename__ = 'images'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(100), nullable=False)
    date  = db.Column(db.Date, default=datetime.utcnow)

class MovieImage(db.Model):
    __tablename__ = 'movie_images'

    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('moviestack.id'))
    name = db.Column(db.String(100), nullable=False)
    date  = db.Column(db.Date, default=datetime.utcnow)



@app.route("/")
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
    

@app.route('/movie_template/<movie_id>', defaults={'movie_id': None})
@login_required
def movie_template(movie_id):
    return render_template('movie_template.html', movie_id=movie_id)


@app.route('/emailReq')
def emailRequest():
    return render_template('emailReq.html')

@app.route('/RequestPassword', methods=['GET','POST'])
def emailRequest2():
    emailTry =  request.form['email']
    try:  
        user = User.query.filter_by(email=emailTry).first()
        import random as rd
        new =f"{rd.randint(1, 1000)}{rd.randint(1, 1000)}"
        user.password =  generate_password_hash(new)
        db.session.commit()
        msg = Message("Hello from simplewebapp support", sender='projektotesanek@seznam.cz', recipients=[str(emailTry)])
        msg.body = f"This is simple web support. This is your new generated password {new}    When you log in, change it."
        mail.send(msg)
        flash(message=f'We send you email on adress: {emailTry}')
        return render_template('emailReq.html')
    except:
        flash(message=f'Couldnt send email on adress: {emailTry}')
        return render_template('emailReq.html')


class UsersLogin(Resource):
    def post(self):
        item = request.json
        print(f"From post {item}")
        user_obj =User.query.filter_by(email  = item.get('email')).first()
        if user_obj != None:
            if check_password_hash(pwhash= user_obj.password,password=item.get('password')):
                login_user(user_obj,duration=5)
                response_message = "ok"
                return {"message": response_message}, 201
            else:
                response_message = "no"
                return {"message": response_message}, 201
        else:
            response_message = "no"
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
            newUser = User(username=userNick,email= userEmail,password=generate_password_hash(password=userPassword), avatar = "default.png")
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
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                match = re.match(email_pattern, new)
                if match:
                    current_user.email = new
                else:
                    return {"message" : "error"}
            elif item.get('oldPassword'):
                print(f"current password {current_user.password}")
                
                if not check_password_hash(pwhash=current_user.password, password=item.get('oldPassword')):#item.get('oldPassword') != current_user.password:
                    return {"message" : "old_password"}
                else:

                    current_user.password = generate_password_hash(item.get("newPassword"))
                
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
        if not request.files:
            print("problem")
            return {'message': 'No file part'}, 400
        
       
        print("img request")
        file = request.files['file']
        img_db = Image(user_id= current_user.id, name=file.filename )
        db.session.add(img_db)
        db.session.commit()
        key = current_user.id
        print(f" key {key}")
        adress = resizeImg(img=file, name=file.filename, key= key)
        print(f"ADRESS {adress}")
     
        return {'message' : 'ok', 'image' :f'static/images/{adress}' }


    
class SetAvatar(Resource):
    def get(self):
        try:
            return {"current_avatar" :current_user.avatar}
        except:
            return {'message': 'no'}
        
    def put(self):
        current_user.id
        imgs_list = []
        images = Image.query.filter_by(user_id=current_user.id).all()
        for img in images:
            
            imgs_list.append(f'images/{current_user.id}_!_{img.name}')
            
        print(f"From DB = {imgs_list}")
        print({'data' :imgs_list})
        return {'data' :imgs_list}
        
class AlterIMGs(Resource):
    
    def put(self):
        item= request.json
        img_name_raw = item.get("user_avatar")
        img_name_raw= img_name_raw[7:]
        print(img_name_raw)
        current_user.avatar = img_name_raw
        db.session.commit()
        
  
        #current_user.avatar = item.get("delete_image")

    def delete(self):
        item= request.json
        img_name_raw = item.get("delete_image")
        pattern = '_!_(.+)$'
        match = re.search(pattern, img_name_raw )
        if match:
            db_img = Image.query.filter_by(user_id=current_user.id, name=match.group(1)).first()
            db.session.delete(db_img)
            db.session.commit()
        os.path.abspath('static')
        os.remove(os.path.join(os.path.abspath('static'), f'{img_name_raw}'))
        
        print("Deleting", item.get("delete_image"))
     
class InsertMovie(Resource):
    def get(self):
        movies = Moviestack.query.all()
        jsonList=[]
        for movie in movies:
            movie_im = MovieImage.query.filter_by(movie_id = movie.id).first()
            jsonList.append({
                "movieID" : movie.id,
                "movieName" : movie.movieName,
                "year" : movie.year,
                'movie_img' : f"{movie.id}_!_{movie_im.name}"

            })
        return jsonify(jsonList)
    def post(self):
        
            movie_name = request.form.get('movie_name')
            movie_year = request.form.get('movie_year')
            movie_genre= request.form.get('movie_genre')
            movie_direction = request.form.get('movie_direction')
            movie_img = request.files.get('movie_image')
            movie_desc = request.form.get('movie_description')
            print("user id ", current_user.id, " movie name ", movie_img.filename, 'desc',movie_desc  )
                
            newMovie = Moviestack(movieName= movie_name, year=movie_year, addedBy=current_user.id, description= movie_desc, genre= movie_genre, direction = movie_direction )
            db.session.add(newMovie)
            db.session.commit()

            movie_id = Moviestack.query.filter_by(movieName= movie_name, year=movie_year).first()
            img_db = MovieImage(movie_id= movie_id.id, name=movie_img.filename )
            db.session.add(img_db)
            db.session.commit()
            
            
            img_db_key =  MovieImage.query.filter_by(movie_id= movie_id.id, name=movie_img.filename).first()
            resizeMovieImg(img= movie_img, key=  img_db_key.id , name=movie_img.filename)
            print(  movie_name , movie_year, movie_img.filename )
            return{'message' : 'ok'}
class AlterMovies(Resource):
    def get(self):
        
        movies = Moviestack.query.filter_by(addedBy=current_user.id).all()
        MovieList = []
        if len(movies) != 0:
            for movie in movies:
                MovieList.append({
                    'movieName' :  movie.movieName,
                    'year' : movie.year,
                    'description' : movie.description,
                    'genre' : movie.genre,
                    'direction' : movie.direction
                })

            return jsonify(MovieList)
            """
            else:
                return jsonify({'data': 'No movies found for the current user'})
        except:
            return jsonify({'data' : 'error'})
"""




class Movie_template_handle(Resource):

    def get(self, val):
        val = int(val)
        movie_obj = Moviestack.query.filter_by(id= val).first()
        movie_img_obj = MovieImage.query.filter_by(movie_id= val).first()
        creator_obj = User.query.filter_by(id= movie_obj.addedBy).first() 
        comment_objs = Comments.query.filter_by(Movie=int(val)).all()

        if len(comment_objs) != 0:
            rating_sum, comments = 0, []
            for obj in comment_objs:
                rating_sum += int(obj.rating)
                user_obj = User.query.filter_by(id=obj.author).first()
                comments.append({
                    'content' : obj.content,
                    'author'  : user_obj.username,
                    'img' : user_obj.avatar,
                    'rated' : obj.rating
                })

            rating_final = round(rating_sum/len(comment_objs),2)
            movie_obj.movie_rating =  rating_final
            db.session.commit()
        else:
            rating_final = None
            comments = None
      
        data = {
        'movie_img' : f"{val}_!_{movie_img_obj.name}",
        'movieName' : movie_obj.movieName,
        'year' : movie_obj.year,
        'date' : movie_obj.date,
        'description' : movie_obj.description,
        'addedBy' :creator_obj.username,
        'creator_name' : creator_obj.username,
        'creator_img' :  creator_obj.avatar,
        'rating' : rating_final,
        'reviews' : comments,
        'genre' :   movie_obj.genre,
        'direction' :movie_obj.direction,
        }

        print(f"data : {data}")
        return jsonify({'message': data})

    def put(self, val):
        
        val = int(val)
        try:
            comment = Comments.query.filter_by(Movie= val, author=current_user.id).first()
            comment_obj = Comments.query.filter_by(Movie=val, author=current_user.id).first()
            if comment is None:
                return {'data' : 404}
            else:
                return {'data' : comment.content, 'rating' :comment_obj.rating}
        except:
            return {'data' : 'error'}
        
    def post(self, val):
        val = int(val)
        try:
            content = request.json
            comment_obj = Comments.query.filter_by(Movie=val, author=current_user.id).first()
            if comment_obj is None:
                new_comment = Comments(content= content['data'], author = current_user.id, Movie = val, rating=int(content['rating']) )
                db.session.add(new_comment)
                db.session.commit()
                return 201
            else:
                # TODO: Create searching mechanism 
                comment_obj.content = content['data']
                comment_obj.rating = int(content['rating'])
                db.session.commit()
                return 201
                
                
        except:
            return 'error'
        
    def delete(self, val):
        val = int(val)
        comment_obj = Comments.query.filter_by(Movie=val, author=current_user.id).first()

        if comment_obj is not None:
            db.session.delete(comment_obj)
            db.session.commit()
            return 201
        else:
            return 404

                 
api.add_resource(UsersLogin,"/log")
api.add_resource(UserRegister,"/new_user_reg")
api.add_resource(UserAlter,'/alter')
api.add_resource(SetAvatar,'/avatar')
api.add_resource(AlterIMGs,'/alter_img')
api.add_resource(InsertMovie,'/add_movie')
api.add_resource(Movie_template_handle,'/movie_template_info/<val>')
api.add_resource(AlterMovies,'/AlterMovies')


if __name__ == "__main__":
    app.run( host="0.0.0.0",port=5000, debug=True)
    db.init_app(app)