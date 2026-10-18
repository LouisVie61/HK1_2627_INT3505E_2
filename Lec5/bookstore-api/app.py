from pathlib import Path

from flask import Flask, jsonify

from models import Author, Book, Category, User, db
from routes import authors, books, categories, reviews, users

DB_PATH = Path(__file__).with_name("bookstore.db")


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    app.register_blueprint(books.bp)
    app.register_blueprint(authors.bp)
    app.register_blueprint(categories.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(reviews.bp)

    @app.get("/")
    def index():
        return jsonify({"service": "bookstore-api", "endpoints": [
            "/api/v1/books", "/api/v1/authors", "/api/v1/categories",
            "/api/v1/users", "/api/v1/reviews",
        ]})

    with app.app_context():
        db.create_all()
        seed(app)

    return app


def seed(app):
    if Category.query.first() is not None:
        return
    fiction = Category(name="Fiction", slug="fiction")
    tech = Category(name="Technology", slug="technology")
    db.session.add_all([fiction, tech])

    tolkien = Author(name="J.R.R. Tolkien", bio="English author, best known for The Lord of the Rings")
    martin = Author(name="Robert C. Martin", bio="Author of Clean Code")
    db.session.add_all([tolkien, martin])
    db.session.flush()

    hobbit = Book(title="The Hobbit", isbn="9780547928227", price_vnd=180000, stock=12, category=fiction)
    hobbit.authors = [tolkien]
    clean_code = Book(title="Clean Code", isbn="9780132350884", price_vnd=250000, stock=5, category=tech)
    clean_code.authors = [martin]
    db.session.add_all([hobbit, clean_code])

    reader = User(email="reader@example.com", display_name="Reader One")
    db.session.add(reader)

    db.session.commit()


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
