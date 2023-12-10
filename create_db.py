from main import app, db, User, Moviestack


with app.app_context():
    db.create_all()