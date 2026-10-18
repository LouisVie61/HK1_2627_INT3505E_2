from flask import Blueprint, jsonify, request

from models import Book, Review, User, db
from routes.common import error, validate

bp = Blueprint("reviews", __name__, url_prefix="/api/v1/reviews")


@bp.get("")
def list_reviews():
    query = Review.query
    book_id = request.args.get("book_id", type=int)
    if book_id is not None:
        query = query.filter(Review.book_id == book_id)
    return jsonify([r.to_dict() for r in query.order_by(Review.id).all()])


@bp.get("/<int:review_id>")
def get_review(review_id):
    review = Review.query.get(review_id)
    if review is None:
        return error("not_found", "Review not found", 404)
    return jsonify(review.to_dict())


@bp.post("")
def create_review():
    data = request.get_json(silent=True)
    problem = validate("review.json", data)
    if problem:
        return error("validation_error", problem, 422)
    if Book.query.get(data["book_id"]) is None:
        return error("validation_error", "book_id does not reference an existing book", 422)
    if User.query.get(data["user_id"]) is None:
        return error("validation_error", "user_id does not reference an existing user", 422)
    review = Review(rating=data["rating"], book_id=data["book_id"], user_id=data["user_id"])
    db.session.add(review)
    db.session.commit()
    return jsonify(review.to_dict()), 201


@bp.delete("/<int:review_id>")
def delete_review(review_id):
    review = Review.query.get(review_id)
    if review is None:
        return error("not_found", "Review not found", 404)
    db.session.delete(review)
    db.session.commit()
    return "", 204
