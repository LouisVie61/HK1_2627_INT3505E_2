from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import mapped_column, relationship

db = SQLAlchemy()

book_author = db.Table(
    "book_author",
    db.Column("book_id", db.Integer, db.ForeignKey("book.id"), primary_key=True),
    db.Column("author_id", db.Integer, db.ForeignKey("author.id"), primary_key=True),
)


class Category(db.Model):
    id = mapped_column(db.Integer, primary_key=True)
    name = mapped_column(db.String(120), nullable=False)
    slug = mapped_column(db.String(120), nullable=False, unique=True)

    books = relationship("Book", back_populates="category")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "slug": self.slug}


class Author(db.Model):
    id = mapped_column(db.Integer, primary_key=True)
    name = mapped_column(db.String(120), nullable=False)
    bio = mapped_column(db.Text, nullable=True)

    books = relationship("Book", secondary=book_author, back_populates="authors")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "bio": self.bio}


class Book(db.Model):
    id = mapped_column(db.Integer, primary_key=True)
    title = mapped_column(db.String(200), nullable=False)
    isbn = mapped_column(db.String(20), nullable=False, unique=True)
    price_vnd = mapped_column(db.Integer, nullable=False)
    stock = mapped_column(db.Integer, nullable=False, default=0)
    category_id = mapped_column(db.Integer, db.ForeignKey("category.id"), nullable=True)

    category = relationship("Category", back_populates="books")
    authors = relationship("Author", secondary=book_author, back_populates="books")
    reviews = relationship("Review", back_populates="book", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": f"book_{self.id}",
            "title": self.title,
            "isbn": self.isbn,
            "price_vnd": self.price_vnd,
            "stock": self.stock,
            "category_id": self.category_id,
            "author_ids": [author.id for author in self.authors],
        }


class User(db.Model):
    id = mapped_column(db.Integer, primary_key=True)
    email = mapped_column(db.String(200), nullable=False, unique=True)
    display_name = mapped_column(db.String(120), nullable=False)

    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self):
        return {"id": self.id, "email": self.email, "display_name": self.display_name}


class Review(db.Model):
    id = mapped_column(db.Integer, primary_key=True)
    rating = mapped_column(db.Integer, nullable=False)
    book_id = mapped_column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    user_id = mapped_column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = mapped_column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    book = relationship("Book", back_populates="reviews")
    user = relationship("User", back_populates="reviews")

    def to_dict(self):
        return {
            "id": self.id,
            "rating": self.rating,
            "book_id": self.book_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
