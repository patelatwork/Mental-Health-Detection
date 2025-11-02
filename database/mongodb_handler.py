import pymongo
from pymongo import MongoClient
from datetime import datetime, timedelta
import streamlit as st
from typing import Dict, List, Optional
import hashlib

class MongoDBHandler:
    def __init__(self, connection_string: str = None):
        """Initialize MongoDB connection"""
        if connection_string is None:
            # Default local MongoDB connection
            connection_string = "mongodb://localhost:27017/"
        
        try:
            self.client = MongoClient(connection_string)
            self.db = self.client['mental_health_db']
            self.users_collection = self.db['users']
            self.analysis_collection = self.db['analysis_history']
            self.dashboard_collection = self.db['dashboard_data']
            
            # Create indexes for better performance
            self.users_collection.create_index("username", unique=True)
            self.analysis_collection.create_index([("user_id", 1), ("timestamp", -1)])
            
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
