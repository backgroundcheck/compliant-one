"""
Streamlit Authentication Interface for Compliant.one
Handles user login, registration, and session management
"""

import streamlit as st
import time
from datetime import datetime
from typing import Optional, Dict
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from core.auth import mongo_connection, UserManager, initialize_user_system
except ImportError as e:
    st.error(f"Authentication system not available: {e}")
    st.stop()

class StreamlitAuth:
    """Streamlit authentication manager"""
    
    def __init__(self):
        self.user_manager = None
        self.init_auth_system()
    
    def init_auth_system(self):
        """Initialize authentication system"""
        try:
            # Initialize MongoDB connection
            if mongo_connection.connect():
                self.user_manager = UserManager(mongo_connection.db)
                
                # Initialize session state
                if 'authenticated' not in st.session_state:
                    st.session_state.authenticated = False
                if 'user_info' not in st.session_state:
                    st.session_state.user_info = None
                if 'access_token' not in st.session_state:
                    st.session_state.access_token = None
                
                return True
            else:
                st.error("❌ Failed to connect to MongoDB")
                return False
                
        except Exception as e:
            st.error(f"❌ Authentication system initialization failed: {str(e)}")
            return False
    
    def login_form(self):
        """Display login form"""
        st.title("🔐 Compliant.one Login")
        st.markdown("**Secure Access to RegTech Platform**")
        
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                with st.form("login_form"):
                    st.markdown("### Sign In")
                    
                    username = st.text_input(
                        "Username or Email",
                        placeholder="Enter your username or email"
                    )
                    
                    password = st.text_input(
                        "Password",
                        type="password",
                        placeholder="Enter your password"
                    )
                    
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        login_submitted = st.form_submit_button(
                            "🚀 Login",
                            use_container_width=True
                        )
                    
                    with col_b:
                        register_clicked = st.form_submit_button(
                            "📝 Register",
                            use_container_width=True
                        )
                    
                    if login_submitted:
                        if username and password:
                            self.authenticate_user(username, password)
                        else:
                            st.error("❌ Please enter username and password")
                    
                    if register_clicked:
                        st.session_state.show_register = True
                        st.rerun()
                
                # Show demo credentials
                with st.expander("🔍 Demo Credentials"):
                    st.info("""
                    **Default Admin Account:**
                    - Username: `admin`
                    - Password: `admin123`
                    
                    ⚠️ **Please change the default password after first login!**
                    """)
    
    def registration_form(self):
        """Display registration form"""
        st.title("📝 Register New User")
        
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                with st.form("register_form"):
                    st.markdown("### Create Account")
                    
                    username = st.text_input(
                        "Username *",
                        placeholder="Choose a unique username"
                    )
                    
                    email = st.text_input(
                        "Email *",
                        placeholder="Enter your email address"
                    )
                    
                    full_name = st.text_input(
                        "Full Name",
                        placeholder="Enter your full name"
                    )
                    
                    department = st.text_input(
                        "Department",
                        placeholder="Enter your department"
                    )
                    
                    role = st.selectbox(
                        "Role *",
                        options=['viewer', 'analyst', 'compliance_officer'],
                        help="Admin role can only be assigned by existing admins"
                    )
                    
                    password = st.text_input(
                        "Password *",
                        type="password",
                        placeholder="Enter a strong password"
                    )
                    
                    confirm_password = st.text_input(
                        "Confirm Password *",
                        type="password",
                        placeholder="Confirm your password"
                    )
                    
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        register_submitted = st.form_submit_button(
                            "✅ Create Account",
                            use_container_width=True
                        )
                    
                    with col_b:
                        back_to_login = st.form_submit_button(
                            "🔙 Back to Login",
                            use_container_width=True
                        )
                    
                    if register_submitted:
                        if password != confirm_password:
                            st.error("❌ Passwords do not match")
                        elif len(password) < 6:
                            st.error("❌ Password must be at least 6 characters")
                        elif not username or not email or not password:
                            st.error("❌ Please fill in all required fields")
                        else:
                            self.register_user(username, email, password, role, full_name, department)
                    
                    if back_to_login:
                        st.session_state.show_register = False
                        st.rerun()
    
    def authenticate_user(self, username: str, password: str):
        """Authenticate user credentials"""
        if not self.user_manager:
            st.error("❌ Authentication system not available")
            return
        
        with st.spinner("🔐 Authenticating..."):
            result = self.user_manager.authenticate_user(username, password)
            
            if result['success']:
                # Set session state
                st.session_state.authenticated = True
                st.session_state.user_info = result['user']
                st.session_state.access_token = result['access_token']
                
                st.success(f"✅ Welcome back, {result['user']['full_name'] or result['user']['username']}!")
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"❌ {result['message']}")
    
    def register_user(self, username: str, email: str, password: str, 
                     role: str, full_name: str, department: str):
        """Register new user"""
        if not self.user_manager:
            st.error("❌ Authentication system not available")
            return
        
        with st.spinner("📝 Creating account..."):
            result = self.user_manager.create_user(
                username=username,
                email=email,
                password=password,
                role=role,
                full_name=full_name,
                department=department
            )
            
            if result['success']:
                st.success("✅ Account created successfully! Please login.")
                st.session_state.show_register = False
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"❌ {result['message']}")
    
    def logout(self):
        """Logout current user"""
        if self.user_manager and st.session_state.get('access_token'):
            self.user_manager.logout_user(st.session_state.access_token)
        
        # Clear session state
        st.session_state.authenticated = False
        st.session_state.user_info = None
        st.session_state.access_token = None
        
        st.success("✅ Logged out successfully")
        time.sleep(1)
        st.rerun()
    
    def verify_session(self) -> bool:
        """Verify current user session"""
        if not st.session_state.get('authenticated'):
            return False
        
        if not self.user_manager or not st.session_state.get('access_token'):
            return False
        
        # Verify token
        result = self.user_manager.verify_token(st.session_state.access_token)
        
        if not result['success']:
            # Invalid token - logout user
            self.logout()
            return False
        
        # Update user info if needed
        st.session_state.user_info = result['user']
        return True
    
    def require_permission(self, permission: str) -> bool:
        """Check if current user has required permission"""
        if not self.verify_session():
            return False
        
        user_id = st.session_state.user_info.get('id')
        if not user_id:
            return False
        
        return self.user_manager.has_permission(user_id, permission)
    
    def show_user_info(self):
        """Display current user information in sidebar"""
        if st.session_state.get('authenticated') and st.session_state.get('user_info'):
            user = st.session_state.user_info
            
            st.sidebar.markdown("---")
            st.sidebar.markdown("### 👤 User Info")
            st.sidebar.write(f"**Name:** {user.get('full_name', user['username'])}")
            st.sidebar.write(f"**Role:** {user['role'].title()}")
            st.sidebar.write(f"**Department:** {user.get('department', 'N/A')}")
            
            if st.sidebar.button("🚪 Logout"):
                self.logout()
    
    def render_auth_page(self):
        """Render authentication page"""
        # Check if user is already authenticated
        if self.verify_session():
            return True
        
        # Show registration form if requested
        if st.session_state.get('show_register', False):
            self.registration_form()
        else:
            self.login_form()
        
        return False

# Global authentication instance
auth_manager = StreamlitAuth()

def require_auth(permission: str = None):
    """Decorator function to require authentication"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not auth_manager.verify_session():
                st.warning("🔐 Please login to access this page")
                auth_manager.render_auth_page()
                return None
            
            if permission and not auth_manager.require_permission(permission):
                st.error(f"❌ Access denied. Required permission: {permission}")
                return None
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def get_current_user() -> Optional[Dict]:
    """Get current authenticated user"""
    if auth_manager.verify_session():
        return st.session_state.user_info
    return None

def has_permission(permission: str) -> bool:
    """Check if current user has permission"""
    return auth_manager.require_permission(permission)

# User management interface for admin
def render_user_management():
    """Render user management interface (admin only)"""
    if not has_permission('user_management'):
        st.error("❌ Access denied. Admin privileges required.")
        return
    
    st.header("👥 User Management")
    
    # Get all users
    users = auth_manager.user_manager.get_all_users()
    
    # User statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Users", len(users))
    
    with col2:
        active_users = len([u for u in users if u.get('is_active', False)])
        st.metric("Active Users", active_users)
    
    with col3:
        admin_users = len([u for u in users if u.get('role') == 'admin'])
        st.metric("Admin Users", admin_users)
    
    with col4:
        recent_users = len([u for u in users if u.get('last_login')])
        st.metric("Recent Logins", recent_users)
    
    # User list
    st.subheader("📋 User List")
    
    if users:
        import pandas as pd
        
        # Prepare data for display
        user_data = []
        for user in users:
            user_data.append({
                'Username': user['username'],
                'Full Name': user.get('full_name', ''),
                'Email': user['email'],
                'Role': user['role'].title(),
                'Department': user.get('department', ''),
                'Active': '✅' if user.get('is_active') else '❌',
                'Last Login': user.get('last_login', 'Never'),
                'Created': user.get('created_at', '')
            })
        
        df = pd.DataFrame(user_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No users found")
    
    # Add new user (admin only)
    with st.expander("➕ Add New User"):
        with st.form("add_user_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_username = st.text_input("Username *")
                new_email = st.text_input("Email *")
                new_full_name = st.text_input("Full Name")
            
            with col2:
                new_role = st.selectbox("Role *", 
                    options=['viewer', 'analyst', 'compliance_officer', 'admin'])
                new_department = st.text_input("Department")
                new_password = st.text_input("Temporary Password *", type="password")
            
            if st.form_submit_button("👤 Create User"):
                if new_username and new_email and new_password:
                    result = auth_manager.user_manager.create_user(
                        username=new_username,
                        email=new_email,
                        password=new_password,
                        role=new_role,
                        full_name=new_full_name,
                        department=new_department
                    )
                    
                    if result['success']:
                        st.success(f"✅ User '{new_username}' created successfully!")
                        st.rerun()
                    else:
                        st.error(f"❌ {result['message']}")
                else:
                    st.error("❌ Please fill in all required fields")

# Password change interface
def render_password_change():
    """Render password change interface"""
    st.header("🔒 Change Password")
    
    user = get_current_user()
    if not user:
        st.error("❌ Not authenticated")
        return
    
    with st.form("change_password_form"):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        if st.form_submit_button("🔄 Change Password"):
            if not current_password or not new_password:
                st.error("❌ Please fill in all fields")
            elif new_password != confirm_password:
                st.error("❌ New passwords do not match")
            elif len(new_password) < 6:
                st.error("❌ Password must be at least 6 characters")
            else:
                result = auth_manager.user_manager.change_password(
                    user['id'], current_password, new_password
                )
                
                if result['success']:
                    st.success("✅ Password changed successfully! Please login again.")
                    auth_manager.logout()
                else:
                    st.error(f"❌ {result['message']}")

if __name__ == "__main__":
    # Initialize user system
    initialize_user_system()
    
    # Test authentication
    if auth_manager.render_auth_page():
        st.success("Authentication successful!")
        st.write("User info:", get_current_user())
