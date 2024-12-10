from flask import Blueprint, request, jsonify, current_app
from app.db.user_db.service import UserService
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import asyncio
from functools import wraps

user_routes = Blueprint('user', __name__)

def with_async_session(f):
    """Decorator to handle async sessions"""
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        async with current_app.db_manager.get_session() as session:
            return await f(session, *args, **kwargs)
    return decorated_function

@user_routes.route('/register', methods=['POST'])
async def register():
    async with current_app.db_manager.get_session() as session:
        user_service = UserService(session)
        
        try:
            data = request.json
            user = await user_service.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password']
            )
            
            # Generate JWT token
            access_token = create_access_token(identity=user.id)
            
            return jsonify({
                'message': 'User created successfully',
                'user_id': user.id,
                'access_token': access_token
            }), 201
        except ValueError as e:
            return jsonify({'error': str(e)}), 400

@user_routes.route('/login', methods=['POST'])
async def login():
    async with current_app.db_manager.get_session() as session:
        user_service = UserService(session)
        
        try:
            data = request.json
            user = await user_service.authenticate_user(
                username=data['username'],
                password=data['password']
            )
            
            # Generate JWT token
            access_token = create_access_token(identity=user.id)
            
            return jsonify({
                'message': 'Login successful',
                'user_id': user.id,
                'access_token': access_token
            }), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 401

# New method to update user stats using the queue
@user_routes.route('/update_stats', methods=['POST'])
@jwt_required()
async def update_stats():
    try:
        data = request.json
        username = data['username']
        won = data['won']
        
        # Use the queue system we created
        await current_app.update_queue.enqueue_update(username, won)
        
        return jsonify({
            'message': 'Stats update queued successfully'
        }), 202
    except Exception as e:
        return jsonify({'error': str(e)}), 400