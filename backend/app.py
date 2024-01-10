from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime
from models import BlogPost
from models import User
from models import Comment
from models import Like
from models import tag
from models import BlogPostTag


app = Flask(__name__)
app.config['SECRET_KEY'] = ''
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    location = db.Column(db.String(100))  
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Routes with Validations and Error Handling

@app.route('/blogposts', methods=['GET'])
def get_all_blog_posts():
    blog_posts = BlogPost.query.all()
    posts = [{'id': post.id, 'title': post.title, 'content': post.content} for post in blog_posts]
    return jsonify({'posts': posts})

@app.route('/blogpost/<int:post_id>', methods=['GET'])
def get_blog_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    return jsonify({'id': post.id, 'title': post.title, 'content': post.content})

@app.route('/blogpost/create', methods=['POST'])
def create_blog_post():
    
    
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['username', 'password', 'email', 'title', 'content']
        if not all(field in data for field in required_fields):
            raise ValueError('Missing required fields')

        # Validate email format
        if '@' not in data['email']:
            raise ValueError('Invalid email')

        # Check if the user already exists
        user = User.query.filter_by(username=data['username']).first()
        if not user:
            hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
            user = User(username=data['username'], email=data['email'], password=hashed_password)
            db.session.add(user)
            db.session.commit()

        # Creates a new blog post
        new_post = BlogPost(title=data['title'], content=data['content'], user_id=user.id)
        db.session.add(new_post)
        db.session.commit()

        return jsonify({'message': 'Blog post created successfully'})

    except ValueError as e:
        return jsonify({'error': str(e)}), 400  # Bad Request

    except Exception as e:
        return jsonify({'error': str(e)}), 500  # Internal Server Error

@app.route('/blogpost/update/<int:post_id>', methods=['PUT'])
def update_blog_post(post_id):
    
    try:
        post = BlogPost.query.get_or_404(post_id)
        data = request.get_json()

        # Validation
        required_fields = ['title', 'content']
        if not all(field in data for field in required_fields):
            raise ValueError('Missing required fields')

        
        post.title = data['title']
        post.content = data['content']

        db.session.commit()

        return jsonify({'message': 'Blog post updated successfully'})

    except ValueError as e:
        return jsonify({'error': str(e)}), 400  

    except Exception as e:
        return jsonify({'error': str(e)}), 500  

@app.route('/blogpost/delete/<int:post_id>', methods=['DELETE'])
def delete_blog_post(post_id):
    
    #validation
    try:
        post = BlogPost.query.get_or_404(post_id)
        db.session.delete(post)
        db.session.commit()

        return jsonify({'message': 'Blog post deleted successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500  

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)