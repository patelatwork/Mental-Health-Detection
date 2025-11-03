import pymongo
from pymongo import MongoClient
from datetime import datetime, timedelta
import streamlit as st
from typing import Dict, List, Optional
import hashlib
import secrets
import uuid

class MongoDBHandler:
    def __init__(self, connection_string: str = None):
        """Initialize MongoDB connection"""
        if connection_string is None:
            # Default local MongoDB connection
            connection_string = "mongodb+srv://aadipatel1911:MyPassword123@cluster0.lp33q.mongodb.net/carenestt?retryWrites=true&w=majority&appName=Cluster0"
        
        try:
            self.client = MongoClient(connection_string)
            self.db = self.client['carenestt']
            self.users_collection = self.db['users']
            self.analysis_collection = self.db['analysis_history']
            self.dashboard_collection = self.db['dashboard_data']
            self.sessions_collection = self.db['sessions']
            
            # Create indexes for better performance
            self.users_collection.create_index("username", unique=True)
            self.analysis_collection.create_index([("user_id", 1), ("timestamp", -1)])
            self.sessions_collection.create_index("session_token", unique=True)
            self.sessions_collection.create_index("expires_at", expireAfterSeconds=0)  # Auto-delete expired sessions
            
        except Exception as e:
            st.error(f"Failed to connect to MongoDB: {str(e)}")
            self.client = None
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username: str, password: str, email: str) -> bool:
        """Create a new user"""
        try:
            user_data = {
                "username": username,
                "password": self.hash_password(password),
                "email": email,
                "created_at": datetime.now(),
                "last_login": None
            }
            self.users_collection.insert_one(user_data)
            return True
        except pymongo.errors.DuplicateKeyError:
            return False
        except Exception as e:
            st.error(f"Error creating user: {str(e)}")
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user and return user data"""
        try:
            user = self.users_collection.find_one({
                "username": username,
                "password": self.hash_password(password)
            })
            
            if user:
                # Update last login
                self.users_collection.update_one(
                    {"_id": user["_id"]},
                    {"$set": {"last_login": datetime.now()}}
                )
                return {
                    "user_id": str(user["_id"]),
                    "username": user["username"],
                    "email": user["email"]
                }
            return None
        except Exception as e:
            st.error(f"Authentication error: {str(e)}")
            return None
    
    def create_session(self, user_id: str, username: str, email: str, expiry_days: int = 30) -> str:
        """Create a new session and return session token"""
        try:
            # Generate a secure random session token
            session_token = secrets.token_urlsafe(32)
            
            # Calculate expiry time
            expires_at = datetime.now() + timedelta(days=expiry_days)
            
            session_data = {
                "session_token": session_token,
                "user_id": user_id,
                "username": username,
                "email": email,
                "created_at": datetime.now(),
                "expires_at": expires_at,
                "last_accessed": datetime.now()
            }
            
            self.sessions_collection.insert_one(session_data)
            return session_token
        except Exception as e:
            print(f"Error creating session: {str(e)}")
            return None
    
    def get_session(self, session_token: str) -> Optional[Dict]:
        """Retrieve session data by token"""
        try:
            session = self.sessions_collection.find_one({
                "session_token": session_token,
                "expires_at": {"$gt": datetime.now()}  # Only get non-expired sessions
            })
            
            if session:
                # Update last accessed time
                self.sessions_collection.update_one(
                    {"session_token": session_token},
                    {"$set": {"last_accessed": datetime.now()}}
                )
                
                return {
                    "user_id": session["user_id"],
                    "username": session["username"],
                    "email": session["email"]
                }
            return None
        except Exception as e:
            print(f"Error retrieving session: {str(e)}")
            return None
    
    def delete_session(self, session_token: str) -> bool:
        """Delete a session (logout)"""
        try:
            result = self.sessions_collection.delete_one({"session_token": session_token})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting session: {str(e)}")
            return False
    
    def delete_user_sessions(self, user_id: str) -> bool:
        """Delete all sessions for a user"""
        try:
            self.sessions_collection.delete_many({"user_id": user_id})
            return True
        except Exception as e:
            print(f"Error deleting user sessions: {str(e)}")
            return False
    
    def save_analysis(self, user_id: str, analysis_type: str, analysis_data: Dict) -> bool:
        """Save analysis data for a user"""
        try:
            analysis_record = {
                "user_id": user_id,
                "analysis_type": analysis_type,
                "timestamp": datetime.now(),
                "data": analysis_data
            }
            result = self.analysis_collection.insert_one(analysis_record)
            print(f" Saved {analysis_type} analysis to MongoDB with ID: {result.inserted_id}")
            return True
        except Exception as e:
            print(f"✗ Error saving analysis: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_user_analysis_history(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get analysis history for a user"""
        try:
            history = list(self.analysis_collection.find(
                {"user_id": user_id}
            ).sort("timestamp", -1).limit(limit))
            
            print(f"Retrieved {len(history)} history records for user {user_id}")
            
            # Convert ObjectId to string and format data
            for record in history:
                record['_id'] = str(record['_id'])
                record['timestamp'] = record['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            
            return history
        except Exception as e:
            print(f"✗ Error fetching history: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_user_statistics(self, user_id: str) -> Dict:
        """Get user statistics for dashboard"""
        try:
            # Count analyses by type
            pipeline = [
                {"$match": {"user_id": user_id}},
                {"$group": {
                    "_id": "$analysis_type",
                    "count": {"$sum": 1}
                }}
            ]
            analysis_counts = list(self.analysis_collection.aggregate(pipeline))
            
            # Get total analyses
            total_analyses = self.analysis_collection.count_documents({"user_id": user_id})
            
            # Get recent analyses (last 30 days)
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_analyses = self.analysis_collection.count_documents({
                "user_id": user_id,
                "timestamp": {"$gte": thirty_days_ago}
            })
            
            print(f" Statistics for user {user_id}:")
            print(f"   Total: {total_analyses}, Recent (30d): {recent_analyses}")
            print(f"   By type: {analysis_counts}")
            
            return {
                "total_analyses": total_analyses,
                "recent_analyses": recent_analyses,
                "analysis_by_type": {item['_id']: item['count'] for item in analysis_counts}
            }
        except Exception as e:
            print(f"Error fetching statistics: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "total_analyses": 0,
                "recent_analyses": 0,
                "analysis_by_type": {}
            }
    
    def save_dashboard_data(self, user_id: str, dashboard_data: Dict) -> bool:
        """Save or update dashboard data for a user"""
        try:
            self.dashboard_collection.update_one(
                {"user_id": user_id},
                {"$set": {
                    "user_id": user_id,
                    "data": dashboard_data,
                    "updated_at": datetime.now()
                }},
                upsert=True
            )
            return True
        except Exception as e:
            st.error(f"Error saving dashboard data: {str(e)}")
            return False
    
    def get_dashboard_data(self, user_id: str) -> Optional[Dict]:
        """Get dashboard data for a user"""
        try:
            dashboard = self.dashboard_collection.find_one({"user_id": user_id})
            if dashboard:
                return dashboard.get('data', {})
            return None
        except Exception as e:
            st.error(f"Error fetching dashboard data: {str(e)}")
            return None
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
