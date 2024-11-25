# blogs.py
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from blog.models import (
    get_posts,
    get_post_by_id,
    create_post,
    update_post,
    delete_post,
    get_tags_for_post,
    associate_tags_with_post
)

bp = Blueprint('blog', __name__)

# Utility function to format timestamps
def format_post(post, tags):
    return {
        "id": post['id'],
        "title": post['title'],
        "content": post['content'],
        "category": post['category'],
        "tags": tags,
        "createdAt": post['created_at'],
        "updatedAt": post['updated_at']
    }


# GET all posts with optional search term
@bp.route('/posts', methods=['GET'])
@jwt_required()
def get_all_posts():
    user_id = get_jwt_identity()
    term = request.args.get('term', '')

    posts = get_posts(user_id, term)
    formatted_posts = []
    for post in posts:
        tags = get_tags_for_post(post['id'])
        formatted_posts.append(format_post(dict(post), tags))
    
    return jsonify(formatted_posts), 200


# GET a specific post by ID
@bp.route('/posts/<int:post_id>', methods=['GET'])
@jwt_required()
def get_single_post(post_id):
    user_id = get_jwt_identity()
    post = get_post_by_id(post_id, user_id)
    if post is None:
        return jsonify({'error': 'Post not found'}), 404
    
    tags = get_tags_for_post(post_id)
    return jsonify(format_post(dict(post), tags)), 200


# POST a new post
@bp.route('/posts', methods=['POST'])
@jwt_required()
def create_new_post():
    current_user_id = get_jwt_identity()
    data = request.get_json()

    # Validate input
    if not data or not all(k in data for k in ('title', 'content', 'category', 'tags')):
        return jsonify({'error': 'Bad Request', 'message': 'Title, content, category, and tags are required.'}), 400

    post_id = create_post(data['title'], data['content'], data['category'], current_user_id)
    tags = data['tags']
    associate_tags_with_post(post_id, tags)

    new_post = get_post_by_id(post_id, current_user_id)
    return jsonify(format_post(dict(new_post), tags)), 201


# PUT to update a post by ID
@bp.route('/posts/<int:post_id>', methods=['PUT'])
@jwt_required()
def update_existing_post(post_id):
    user_id = get_jwt_identity()
    data = request.get_json()

    # Validate input
    if not data or not all(k in data for k in ('title', 'content', 'category', 'tags')):
        return jsonify({'error': 'Bad Request', 'message': 'Title, content, category, and tags are required.'}), 400

    update_post(post_id, user_id, data['title'], data['content'], data['category'])
    associate_tags_with_post(post_id, data['tags'])

    updated_post = get_post_by_id(post_id, user_id)
    tags = get_tags_for_post(post_id)

    return jsonify(format_post(dict(updated_post), tags)), 200


# DELETE a post by ID
@bp.route('/posts/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_existing_post(post_id):
    user_id = get_jwt_identity()
    result = delete_post(post_id, user_id)

    if result == 0:
        return jsonify({'error': 'Post not found or you do not have permission to delete this post.'}), 404
    
    return jsonify({'message': 'Post deleted successfully'}), 204
