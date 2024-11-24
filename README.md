# Blogging Platform API

## Overview

The Blogging Platform API is a RESTful API that allows users to create, read, update, and delete blog posts. Users can also manage tags associated with their posts and search for posts using a search term. This API is built using Flask and SQLite.

## Features

- User authentication with JWT (JSON Web Tokens)
- CRUD operations for blog posts
- Tag management for posts
- Filtering posts by search terms
- Responsive error handling

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
  - [Authentication](#authentication)
  - [Posts](#posts)
- [Database Schema](#database-schema)
- [Contributing](#contributing)
- [License](#license)

## Requirements

- Python 3.6+
- Flask
- Flask-JWT-Extended
- SQLite3

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/blogging-platform-api.git
   cd blogging-platform-api
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:
   - Create a file named `schema.sql` in the root of your project with the following content:
   ```sql
   CREATE TABLE user (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       username VARCHAR(50) UNIQUE NOT NULL,
       password VARCHAR(128) NOT NULL
   );

   CREATE TABLE post (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       title VARCHAR(100) NOT NULL,
       content TEXT NOT NULL,
       category VARCHAR(50) NOT NULL,
       user_id INTEGER NOT NULL,
       created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
       updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
       FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
   );

   CREATE TABLE tag (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       name VARCHAR(50) UNIQUE NOT NULL
   );

   CREATE TABLE post_tags (
       post_id INTEGER NOT NULL,
       tag_id INTEGER NOT NULL,
       PRIMARY KEY (post_id, tag_id),
       FOREIGN KEY (post_id) REFERENCES post(id) ON DELETE CASCADE,
       FOREIGN KEY (tag_id) REFERENCES tag(id) ON DELETE CASCADE
   );
   ```

   - Initialize the database using the command line:
   ```bash
   python -m flask --app blog init-db
   ```

## Usage

To run the API, execute the following command:
```bash
flask run
```
The API will be available at `http://localhost:5000`.

## API Endpoints

### Authentication

- **POST /login**
  - **Description**: Authenticate user and return a JWT token.
  - **Request Body**:
    ```json
    {
      "username": "your_username",
      "password": "your_password"
    }
    ```
  - **Response**:
    ```json
    {
      "access_token": "<JWT_TOKEN>"
    }
    ```

### Posts

- **GET /posts**
  - **Description**: Retrieve all posts for the authenticated user. Supports optional search.
  - **Query Parameters**: 
    - `term` (optional): A search term to filter posts by title, content, or category.
  - **Response**:
    ```json
    [
      {
        "id": 1,
        "title": "My First Blog Post",
        "content": "This is the content of my first blog post.",
        "category": "Technology",
        "tags": ["Tech", "Programming"],
        "createdAt": "2021-09-01T12:00:00Z",
        "updatedAt": "2021-09-01T12:00:00Z"
      }
    ]
    ```

- **POST /posts**
  - **Description**: Create a new post.
  - **Request Body**:
    ```json
    {
      "title": "My First Blog Post",
      "content": "This is the content of my first blog post.",
      "category": "Technology",
      "tags": ["Tech", "Programming"]
    }
    ```
  - **Response**:
    ```json
    {
      "id": 1,
      "title": "My First Blog Post",
      "content": "This is the content of my first blog post.",
      "category": "Technology",
      "tags": ["Tech", "Programming"],
      "createdAt": "2021-09-01T12:00:00Z",
      "updatedAt": "2021-09-01T12:00:00Z"
    }
    ```

- **GET /posts/<post_id>**
  - **Description**: Retrieve a specific post by ID.
  - **Response**:
    ```json
    {
      "id": 1,
      "title": "My First Blog Post",
      "content": "This is the content of my first blog post.",
      "category": "Technology",
      "tags": ["Tech", "Programming"],
      "createdAt": "2021-09-01T12:00:00Z",
      "updatedAt": "2021-09-01T12:00:00Z"
    }
    ```

- **PUT /posts/<post_id>**
  - **Description**: Update an existing post by ID.
  - **Request Body**:
    ```json
    {
      "title": "Updated Blog Post",
      "content": "This is the updated content.",
      "category": "Technology",
      "tags": ["Tech", "Updates"]
    }
    ```
  - **Response**:
    ```json
    {
      "id": 1,
      "title": "Updated Blog Post",
      "content": "This is the updated content.",
      "category": "Technology",
      "tags": ["Tech", "Updates"],
      "createdAt": "2021-09-01T12:00:00Z",
      "updatedAt": "2021-09-02T12:00:00Z"
    }
    ```

- **DELETE /posts/<post_id>**
  - **Description**: Delete a specific post by ID.
  - **Response**:
    ```json
    {
      "message": "Post deleted successfully"
    }
    ```

## Database Schema

```sql
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL
);

CREATE TABLE post (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    user_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

CREATE TABLE tag (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE post_tags (
    post_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (post_id, tag_id),
    FOREIGN KEY (post_id) REFERENCES post(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tag(id) ON DELETE CASCADE
);
```

## Contributing

Contributions are welcome! Please fork the repository and create a pull request for any changes or enhancements.

## Project Link
[Project URL](https://roadmap.sh/projects/blogging-platform-api)