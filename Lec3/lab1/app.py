from flask import Flask, jsonify, request

app = Flask(__name__)

posts = [
    {
        "id": 1,
        "title": "Bài viết đầu tiên",
        "content": "Nội dung bài viết đầu tiên",
        "author": "Nguyen Van A",
    }
]


@app.get("/api/v1/posts")
def get_posts():
    return jsonify(posts)


@app.post("/api/v1/posts")
def create_post():
    data = request.get_json(silent=True) or {}

    if not data.get("title") or not data.get("content"):
        return jsonify({"error": "title và content là bắt buộc"}), 400

    post = {
        "id": len(posts) + 1,
        "title": data["title"],
        "content": data["content"],
        "author": data.get("author", "Anonymous"),
    }
    posts.append(post)
    return jsonify(post), 201


@app.get("/api/v1/posts/<int:post_id>")
def get_post(post_id):
    post = next((post for post in posts if post["id"] == post_id), None)

    if post is None:
        return jsonify({"error": "Không tìm thấy bài viết"}), 404

    return jsonify(post)


if __name__ == "__main__":
    app.run(debug=True)
