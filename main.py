
from flask import Flask, render_template
from flask_restful import Api, Resource, request
import sqlalchemy
from create_db import Movie, DatabaseOperations

db_url = 'sqlite:///mydb.db'  # Update with your actual database URL
db_operations = DatabaseOperations(db_url)


app = Flask(__name__)
api = Api(app)

MyDB = {
    'data' : "Movie"
}

@app.route("/")
def home():
    return render_template("index.html")

class Video(Resource): 
    
    def get(self):
        return {"message":"Hello World"}
    def post(self):
        
        
        movie_name = request.json
    
        
        print(movie_name['movie'])
        db_operations.add_movie(movie_name['movie'])
        return "response", 201
    
    
    def put(self):
        return "response", 201
    def delete(self):
        return "response", 201
        
    
api.add_resource(Video,"/go")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)