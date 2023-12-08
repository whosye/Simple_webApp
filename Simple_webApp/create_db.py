
from sqlalchemy import create_engine, Column, ForeignKey, String, Integer, CHAR, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json

Base = declarative_base()

class Movie(Base):
    
    __tablename__ = "movie_list"
    
    movie_id     = Column(Integer, primary_key=True)
    name         = Column(String)
    release_year = Column(Integer)
    Genre        = Column(String)
    
    
    def __init__(self, movie_id, name, release, Genre):
        self.movie_id       = movie_id
        self.name           = name 
        self.release_year   = release 
        self.Genre          = Genre 
        
    def __repr__ (self):
        return f"{self.movie_id}_{self.name}_{self.release_year}_{self.Genre}"


class DatabaseOperations:
    def __init__(self, db_url):
        self.engine = create_engine(db_url, echo=True)
        Base.metadata.create_all(bind=self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def add_movie(self, movie):
        with self.Session() as session:
            session.add(movie)
            session.commit()

    def get_all_movies(self):
        with self.Session() as session:
            return session.query(Movie).all()

    def update_movie(self, movie_id, new_release_year):
        with self.Session() as session:
            movie_to_update = session.query(Movie).filter_by(movie_id=movie_id).first()
            if movie_to_update:
                movie_to_update.release_year = new_release_year
                session.commit()

    def delete_movie(self, movie_id):
        with self.Session() as session:
            movie_to_delete = session.query(Movie).filter_by(movie_id=movie_id).first()
            if movie_to_delete:
                session.delete(movie_to_delete)
                session.commit()

