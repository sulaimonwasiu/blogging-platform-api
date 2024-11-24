from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from datetime import datetime
from blog.db import get_db

bp = Blueprint('blog', __name__)

# Utility function to format timestamps
def format_post(post, tags):
    return {
        "id": post['id'],
        "title": post['title'],
        "content": post['content'],
        "category": post['category'],
        "tags": tags,  # Include tags in the response
        "createdAt": post['created_at'],
        "updatedAt": post['updated_at']
    }

# GET all posts with optional search term
@bp.route('/posts', methods=['GET'])
@jwt_required()
def get_posts():
    user_id = get_jwt_identity()
    term = request.args.get('term', '')

    db = get_db()
    # Use wildcard search for the title, content, or category
    cursor = db.execute('''
        SELECT post.id, post.title, post.content, post.category, post.created_at, post.updated_at
        FROM post
        WHERE post.user_id = ? AND 
              (post.title LIKE ? OR post.content LIKE ? OR post.category LIKE ?)
    ''', (user_id, f'%{term}%', f'%{term}%', f'%{term}%'))
    
    posts = cursor.fetchall()
    
    formatted_posts = []
    for post in posts:
        # Get tags associated with each post
        tags_cursor = db.execute('''
            SELECT tag.name
            FROM tag
            JOIN post_tags ON tag.id = post_tags.tag_id
            WHERE post_tags.post_id = ?
        ''', (post['id'],))
        tags = [tag['name'] for tag in tags_cursor.fetchall()]
        formatted_posts.append(format_post(dict(post), tags))
    
    return jsonify(formatted_posts), 200


# GET a specific post by ID
@bp.route('/posts/<int:post_id>', methods=['GET'])
@jwt_required()
def get_post(post_id):
    user_id = get_jwt_identity()
    db = get_db()
    
    post = db.execute('''
        SELECT post.id, post.title, post.content, post.category, post.created_at, post.updated_at
        FROM post
        WHERE post.id = ? AND post.user_id = ?
    ''', (post_id, user_id)).fetchone()

    if post is None:
        return jsonify({'error': 'Post not found'}), 404
    
    # Get tags associated with the post
    tags_cursor = db.execute('''
        SELECT tag.name
        FROM tag
        JOIN post_tags ON tag.id = post_tags.tag_id
        WHERE post_tags.post_id = ?
    ''', (post_id,))
    tags = [tag['name'] for tag in tags_cursor.fetchall()]

    return jsonify(format_post(dict(post), tags)), 200

# POST a new post
@bp.route('/posts', methods=['POST'])
@jwt_required()
def create_post():
    current_user_id = get_jwt_identity()
    data = request.get_json()

    # Validate input
    if not data or not all(k in data for k in ('title', 'content', 'category', 'tags')):
        return jsonify({'error': 'Bad Request', 'message': 'Title, content, category, and tags are required.'}), 400

    # Insert post into the database
    db = get_db()
    cursor = db.execute('''
        INSERT INTO post (title, content, category, user_id)
        VALUES (?, ?, ?, ?)
    ''', (data['title'], data['content'], data['category'], current_user_id))
    
    post_id = cursor.lastrowid
    db.commit()
    
    # Handle tags and associate them with the post
    tags = data['tags']
    for tag in tags:
        # Check if tag exists, if not create it
        cursor = db.execute('SELECT id FROM tag WHERE name = ?', (tag,))
        tag_record = cursor.fetchone()
        if tag_record is None:
            cursor = db.execute('INSERT INTO tag (name) VALUES (?)', (tag,))
            tag_id = cursor.lastrowid
        else:
            tag_id = tag_record['id']
        
        # Create association in post_tags table
        db.execute('INSERT INTO post_tags (post_id, tag_id) VALUES (?, ?)', (post_id, tag_id))
    
    db.commit()
    
    # Fetch the newly created post
    new_post = db.execute('SELECT * FROM post WHERE id = ?', (post_id,)).fetchone()
    return jsonify(format_post(dict(new_post), tags)), 201


# PUT to update a post by ID
@bp.route('/posts/<int:post_id>', methods=['PUT'])
@jwt_required()
def update_post(post_id):
    user_id = get_jwt_identity()
    data = request.get_json()

    # Validate input
    if not data or not all(k in data for k in ('title', 'content', 'category', 'tags')):
        return jsonify({'error': 'Bad Request', 'message': 'Title, content, category, and tags are required.'}), 400

    db = get_db()
    db.execute('''
        UPDATE post
        SET title = ?, content = ?, category = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND user_id = ?
    ''', (data['title'], data['content'], data['category'], post_id, user_id))
    
    db.commit()

    # Update tags
    db.execute('DELETE FROM post_tags WHERE post_id = ?', (post_id,))  # Remove existing tags
    for tag in data['tags']:
        cursor = db.execute('SELECT id FROM tag WHERE name = ?', (tag,))
        tag_record = cursor.fetchone()
        if tag_record is None:
            cursor = db.execute('INSERT INTO tag (name) VALUES (?)', (tag,))
            tag_id = cursor.lastrowid
        else:
            tag_id = tag_record['id']
        
        db.execute('INSERT INTO post_tags (post_id, tag_id) VALUES (?, ?)', (post_id, tag_id))

    db.commit()

    updated_post = db.execute('SELECT * FROM post WHERE id = ?', (post_id,)).fetchone()
    # Get updated tags
    tags_cursor = db.execute('''
        SELECT tag.name
        FROM tag
        JOIN post_tags ON tag.id = post_tags.tag_id
        WHERE post_tags.post_id = ?
    ''', (post_id,))
    tags = [tag['name'] for tag in tags_cursor.fetchall()]

    return jsonify(format_post(dict(updated_post), tags)), 200


# DELETE a post by ID
@bp.route('/posts/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    user_id = get_jwt_identity()
    db = get_db()
    result = db.execute('''
        DELETE FROM post
        WHERE id = ? AND user_id = ?
    ''', (post_id, user_id))

    db.commit()

    if result.rowcount == 0:
        return jsonify({'error': 'Post not found or you do not have permission to delete this post.'}), 404
    
    return jsonify({'message': 'Post deleted successfully'}), 204