"""
MongoDB Configuration for Compliant.one Platform
Handles database connections, user management, and authentication
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import pymongo # type: ignore
from pymongo import MongoClient # type: ignore
from motor.motor_asyncio import AsyncIOMotorClient # type: ignore
import bcrypt # type: ignore
from passlib.context import CryptContext # type: ignore
import jwt # type: ignore
from bson import ObjectId # type: ignore
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class MongoDBConnection:
    """MongoDB connection manager"""
    
    def __init__(self):
        self.connection_string = os.getenv(
            'MONGODB_URL', 
            'mongodb://localhost:27017/'
        )
        self.database_name = os.getenv('MONGODB_DATABASE', 'compliant_one')
        self.client = None
        self.async_client = None
        self.db = None
        self.async_db = None
        
    def connect(self):
        """Establish synchronous MongoDB connection"""
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.database_name]
            # Test connection
            self.client.admin.command('ping')
            logger.info("✅ MongoDB connected successfully")
            return True
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {str(e)}")
            return False
    
    async def connect_async(self):
        """Establish asynchronous MongoDB connection"""
        try:
            self.async_client = AsyncIOMotorClient(self.connection_string)
            self.async_db = self.async_client[self.database_name]
            # Test connection
            await self.async_client.admin.command('ping')
            logger.info("✅ Async MongoDB connected successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Async MongoDB connection failed: {str(e)}")
            return False
    
    def disconnect(self):
        """Close MongoDB connections"""
        if self.client:
            self.client.close()
        if self.async_client:
            self.async_client.close()

# Global MongoDB instance
mongo_connection = MongoDBConnection()

class UserManager:
    """User management and authentication"""
    
    def __init__(self, db):
        self.db = db
        self.users_collection = db.users
        self.sessions_collection = db.user_sessions
        self.roles_collection = db.user_roles
        self.secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
        self.algorithm = 'HS256'
        self.access_token_expire_minutes = 30
        
        # Initialize default roles
        self.init_default_roles()
    
    def init_default_roles(self):
        """Initialize default user roles"""
        default_roles = [
            {
                'name': 'admin',
                'description': 'Full system administrator access',
                'permissions': [
                    'user_management',
                    'data_source_management', 
                    'file_upload',
                    'source_validation',
                    'system_monitoring',
                    'compliance_screening',
                    'reporting',
                    'api_access'
                ]
            },
            {
                'name': 'compliance_officer',
                'description': 'Compliance monitoring and reporting',
                'permissions': [
                    'compliance_screening',
                    'reporting',
                    'source_validation',
                    'file_upload'
                ]
            },
            {
                'name': 'analyst',
                'description': 'Data analysis and screening',
                'permissions': [
                    'compliance_screening',
                    'reporting',
                    'file_upload'
                ]
            },
            {
                'name': 'viewer',
                'description': 'Read-only access',
                'permissions': [
                    'compliance_screening'
                ]
            }
        ]
        
        for role in default_roles:
            existing_role = self.roles_collection.find_one({'name': role['name']})
            if not existing_role:
                self.roles_collection.insert_one({
                    **role,
                    'created_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                })
                logger.info(f"Created default role: {role['name']}")
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_user(self, username: str, email: str, password: str, 
                   role: str = 'viewer', full_name: str = '', 
                   department: str = '') -> Dict:
        """Create a new user"""
        try:
            # Check if user already exists
            existing_user = self.users_collection.find_one({
                '$or': [{'username': username}, {'email': email}]
            })
            
            if existing_user:
                return {
                    'success': False,
                    'message': 'User with this username or email already exists'
                }
            
            # Validate role
            role_doc = self.roles_collection.find_one({'name': role})
            if not role_doc:
                return {
                    'success': False,
                    'message': f'Invalid role: {role}'
                }
            
            # Hash password
            hashed_password = self.hash_password(password)
            
            # Create user document
            user_doc = {
                'username': username,
                'email': email,
                'password_hash': hashed_password,
                'full_name': full_name,
                'department': department,
                'role': role,
                'is_active': True,
                'is_verified': False,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'last_login': None,
                'login_attempts': 0,
                'locked_until': None
            }
            
            # Insert user
            result = self.users_collection.insert_one(user_doc)
            
            logger.info(f"User created: {username} with role {role}")
            
            return {
                'success': True,
                'message': 'User created successfully',
                'user_id': str(result.inserted_id)
            }
            
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return {
                'success': False,
                'message': f'Error creating user: {str(e)}'
            }
    
    def authenticate_user(self, username: str, password: str) -> Dict:
        """Authenticate user credentials"""
        try:
            # Find user
            user = self.users_collection.find_one({
                '$or': [{'username': username}, {'email': username}]
            })
            
            if not user:
                return {
                    'success': False,
                    'message': 'Invalid username or password'
                }
            
            # Check if account is locked
            if user.get('locked_until') and user['locked_until'] > datetime.utcnow():
                return {
                    'success': False,
                    'message': f'Account locked until {user["locked_until"]}'
                }
            
            # Check if account is active
            if not user.get('is_active', False):
                return {
                    'success': False,
                    'message': 'Account is deactivated'
                }
            
            # Verify password
            if not self.verify_password(password, user['password_hash']):
                # Increment login attempts
                login_attempts = user.get('login_attempts', 0) + 1
                update_data = {'login_attempts': login_attempts}
                
                # Lock account after 5 failed attempts
                if login_attempts >= 5:
                    update_data['locked_until'] = datetime.utcnow() + timedelta(minutes=30)
                
                self.users_collection.update_one(
                    {'_id': user['_id']},
                    {'$set': update_data}
                )
                
                return {
                    'success': False,
                    'message': 'Invalid username or password'
                }
            
            # Reset login attempts and update last login
            self.users_collection.update_one(
                {'_id': user['_id']},
                {
                    '$set': {
                        'last_login': datetime.utcnow(),
                        'login_attempts': 0,
                        'locked_until': None
                    }
                }
            )
            
            # Generate access token
            access_token = self.create_access_token(
                data={'sub': str(user['_id']), 'username': user['username']}
            )
            
            # Create session
            session_doc = {
                'user_id': user['_id'],
                'access_token': access_token,
                'created_at': datetime.utcnow(),
                'expires_at': datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes),
                'is_active': True,
                'ip_address': None,  # Can be added later
                'user_agent': None   # Can be added later
            }
            
            self.sessions_collection.insert_one(session_doc)
            
            logger.info(f"User authenticated: {user['username']}")
            
            return {
                'success': True,
                'message': 'Authentication successful',
                'access_token': access_token,
                'token_type': 'bearer',
                'user': {
                    'id': str(user['_id']),
                    'username': user['username'],
                    'email': user['email'],
                    'full_name': user['full_name'],
                    'role': user['role'],
                    'department': user['department']
                }
            }
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return {
                'success': False,
                'message': f'Authentication error: {str(e)}'
            }
    
    def create_access_token(self, data: dict) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({'exp': expire})
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id = payload.get('sub')
            username = payload.get('username')
            
            if user_id is None or username is None:
                return {'success': False, 'message': 'Invalid token'}
            
            # Check if session exists and is active
            session = self.sessions_collection.find_one({
                'access_token': token,
                'is_active': True,
                'expires_at': {'$gt': datetime.utcnow()}
            })
            
            if not session:
                return {'success': False, 'message': 'Session expired or invalid'}
            
            # Get user details
            user = self.users_collection.find_one({'_id': ObjectId(user_id)})
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            return {
                'success': True,
                'user': {
                    'id': str(user['_id']),
                    'username': user['username'],
                    'email': user['email'],
                    'full_name': user['full_name'],
                    'role': user['role'],
                    'department': user['department']
                }
            }
            
        except jwt.ExpiredSignatureError:
            return {'success': False, 'message': 'Token has expired'}
        except jwt.JWTError:
            return {'success': False, 'message': 'Invalid token'}
        except Exception as e:
            logger.error(f"Token verification error: {str(e)}")
            return {'success': False, 'message': 'Token verification failed'}
    
    def logout_user(self, token: str) -> Dict:
        """Logout user and invalidate session"""
        try:
            # Deactivate session
            result = self.sessions_collection.update_one(
                {'access_token': token},
                {'$set': {'is_active': False, 'logged_out_at': datetime.utcnow()}}
            )
            
            if result.modified_count > 0:
                return {'success': True, 'message': 'Logged out successfully'}
            else:
                return {'success': False, 'message': 'Session not found'}
                
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return {'success': False, 'message': 'Logout failed'}
    
    def get_user_permissions(self, user_id: str) -> List[str]:
        """Get user permissions based on role"""
        try:
            user = self.users_collection.find_one({'_id': ObjectId(user_id)})
            if not user:
                return []
            
            role = self.roles_collection.find_one({'name': user['role']})
            if not role:
                return []
            
            return role.get('permissions', [])
            
        except Exception as e:
            logger.error(f"Error getting user permissions: {str(e)}")
            return []
    
    def has_permission(self, user_id: str, permission: str) -> bool:
        """Check if user has specific permission"""
        permissions = self.get_user_permissions(user_id)
        return permission in permissions
    
    def get_all_users(self) -> List[Dict]:
        """Get all users (admin only)"""
        try:
            users = list(self.users_collection.find(
                {},
                {'password_hash': 0}  # Exclude password hash
            ))
            
            # Convert ObjectId to string
            for user in users:
                user['_id'] = str(user['_id'])
            
            return users
            
        except Exception as e:
            logger.error(f"Error getting users: {str(e)}")
            return []
    
    def update_user(self, user_id: str, update_data: Dict) -> Dict:
        """Update user information"""
        try:
            # Remove sensitive fields that shouldn't be updated directly
            forbidden_fields = ['password_hash', '_id', 'created_at']
            for field in forbidden_fields:
                update_data.pop(field, None)
            
            update_data['updated_at'] = datetime.utcnow()
            
            result = self.users_collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                return {'success': True, 'message': 'User updated successfully'}
            else:
                return {'success': False, 'message': 'User not found or no changes made'}
                
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            return {'success': False, 'message': f'Error updating user: {str(e)}'}
    
    def change_password(self, user_id: str, old_password: str, new_password: str) -> Dict:
        """Change user password"""
        try:
            user = self.users_collection.find_one({'_id': ObjectId(user_id)})
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            # Verify old password
            if not self.verify_password(old_password, user['password_hash']):
                return {'success': False, 'message': 'Current password is incorrect'}
            
            # Hash new password
            new_hash = self.hash_password(new_password)
            
            # Update password
            self.users_collection.update_one(
                {'_id': ObjectId(user_id)},
                {
                    '$set': {
                        'password_hash': new_hash,
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
            # Invalidate all existing sessions
            self.sessions_collection.update_many(
                {'user_id': ObjectId(user_id), 'is_active': True},
                {'$set': {'is_active': False, 'logged_out_at': datetime.utcnow()}}
            )
            
            return {'success': True, 'message': 'Password changed successfully'}
            
        except Exception as e:
            logger.error(f"Error changing password: {str(e)}")
            return {'success': False, 'message': f'Error changing password: {str(e)}'}
    
    def delete_user(self, user_id: str) -> Dict:
        """Delete user (admin only)"""
        try:
            # Soft delete - deactivate user instead of removing
            result = self.users_collection.update_one(
                {'_id': ObjectId(user_id)},
                {
                    '$set': {
                        'is_active': False,
                        'deleted_at': datetime.utcnow(),
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                # Invalidate all sessions
                self.sessions_collection.update_many(
                    {'user_id': ObjectId(user_id), 'is_active': True},
                    {'$set': {'is_active': False, 'logged_out_at': datetime.utcnow()}}
                )
                
                return {'success': True, 'message': 'User deactivated successfully'}
            else:
                return {'success': False, 'message': 'User not found'}
                
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            return {'success': False, 'message': f'Error deleting user: {str(e)}'}

# Initialize database and create default admin user
def initialize_user_system():
    """Initialize user management system with default admin"""
    try:
        # Connect to MongoDB
        if not mongo_connection.connect():
            logger.error("Failed to connect to MongoDB")
            return False
        
        # Initialize user manager
        user_manager = UserManager(mongo_connection.db)
        
        # Create default admin user if it doesn't exist
        admin_user = user_manager.users_collection.find_one({'username': 'admin'})
        if not admin_user:
            result = user_manager.create_user(
                username='admin',
                email='admin@compliant.one',
                password='admin123',  # Change this in production!
                role='admin',
                full_name='System Administrator',
                department='IT'
            )
            
            if result['success']:
                logger.info("✅ Default admin user created")
                logger.warning("⚠️  Please change the default admin password!")
            else:
                logger.error(f"❌ Failed to create admin user: {result['message']}")
        
        # Create indexes for better performance
        user_manager.users_collection.create_index([('username', 1)], unique=True)
        user_manager.users_collection.create_index([('email', 1)], unique=True)
        user_manager.sessions_collection.create_index([('access_token', 1)])
        user_manager.sessions_collection.create_index([('expires_at', 1)])
        
        logger.info("✅ User management system initialized")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize user system: {str(e)}")
        return False

if __name__ == "__main__":
    initialize_user_system()
