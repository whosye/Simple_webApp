
from flask import Flask, render_template, session
from flask_restful import Api, Resource, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user,login_required

app = Flask(__name__)
api = Api(app)
login_manager = LoginManager(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'


db = SQLAlchemy(app)

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(10), unique=True, nullable=False)
    email = db.Column(db.String(15),  unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self) -> str:
        return f"User {self.username}, {self.email}"


@app.route("/", methods = ['GET','POST'])
def home():
    return render_template("main.html")

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/movie')
@login_required
def movie():
    return render_template('movie.html')
  


class UsersLogin(Resource):
    def post(self):
        item = request.json
        print(item)

        if User.query.filter_by(email  = item.get('email'), password=item.get('password')).first() != None:
            user = User.query.filter_by(email  = item.get('email'), password=item.get('password')).first()
            login_user(user)
            response_message = "ok"
            return {"message": response_message}, 201
        else:

            response_message = "no"
            return {"message": response_message}, 201

        #print("Creating new User")
        #new_user = User(username = "zkuska", email=item.get('email'), password=item.get('password'))
        #db.session.add(new_user)
        #db.session.commit()



api.add_resource(UsersLogin,"/post_login")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
    db.init_app()