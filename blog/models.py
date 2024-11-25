from blog.db import get_db

def get_posts(user_id, term):
    db = get_db()
    cursor = db.execute('''
        SELECT post.id, post.title, post.content, post.category, post.created_at, post.updated_at
        FROM post
        WHERE post.user_id = ? AND 
              (post.title LIKE ? OR post.content LIKE ? OR post.category LIKE ?)
    ''', (user_id, f'%{term}%', f'%{term}%', f'%{term}%'))
    
    return cursor.fetchall()

def get_post_by_id(post_id, user_id):
    db = get_db()
    return db.execute('''
        SELECT post.id, post.title, post.content, post.category, post.created_at, post.updated_at
        FROM post
        WHERE post.id = ? AND post.user_id = ?
    ''', (post_id, user_id)).fetchone()

def create_post(title, content, category, user_id):
    db = get_db()
    cursor = db.execute('''
        INSERT INTO post (title, content, category, user_id)
        VALUES (?, ?, ?, ?)
    ''', (title, content, category, user_id))
    db.commit()
    return cursor.lastrowid

def update_post(post_id, user_id, title, content, category):
    db = get_db()
    db.execute('''
        UPDATE post
        SET title = ?, content = ?, category = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND user_id = ?
    ''', (title, content, category, post_id, user_id))
    db.commit()

def delete_post(post_id, user_id):
    db = get_db()
    result = db.execute('''
        DELETE FROM post
        WHERE id = ? AND user_id = ?
    ''', (post_id, user_id))
    db.commit()
    return result.rowcount

def get_tags_for_post(post_id):
    db = get_db()
    tags_cursor = db.execute('''
        SELECT tag.name
        FROM tag
        JOIN post_tags ON tag.id = post_tags.tag_id
        WHERE post_tags.post_id = ?
    ''', (post_id,))
    return [tag['name'] for tag in tags_cursor.fetchall()]

def associate_tags_with_post(post_id, tags):
    db = get_db()
    # Remove existing tags
    db.execute('DELETE FROM post_tags WHERE post_id = ?', (post_id,))
    
    for tag in tags:
        cursor = db.execute('SELECT id FROM tag WHERE name = ?', (tag,))
        tag_record = cursor.fetchone()
        if tag_record is None:
            cursor = db.execute('INSERT INTO tag (name) VALUES (?)', (tag,))
            tag_id = cursor.lastrowid
        else:
            tag_id = tag_record['id']
        
        db.execute('INSERT INTO post_tags (post_id, tag_id) VALUES (?, ?)', (post_id, tag_id))
    
    db.commit()