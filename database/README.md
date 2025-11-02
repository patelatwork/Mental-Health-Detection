# MongoDB Setup Guide

## Installation

### Option 1: Local MongoDB Installation

#### Windows:
1. Download MongoDB Community Server from: https://www.mongodb.com/try/download/community
2. Run the installer (.msi file)
3. Choose "Complete" installation
4. Install MongoDB as a Windows Service (default option)
5. MongoDB will run on `mongodb://localhost:27017/`

#### macOS:
```bash
# Using Homebrew
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

#### Linux (Ubuntu/Debian):
```bash
# Import MongoDB public GPG Key
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -

# Add MongoDB repository
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list

# Install MongoDB
sudo apt-get update
sudo apt-get install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod
```

### Option 2: MongoDB Atlas (Cloud - Free Tier Available)

1. Go to https://www.mongodb.com/cloud/atlas/register
2. Create a free account
3. Create a new cluster (M0 Free tier)
4. Create a database user with password
5. Whitelist your IP address (or use 0.0.0.0/0 for development)
6. Get your connection string (looks like: `mongodb+srv://username:password@cluster.mongodb.net/`)
7. Update the connection string in `app.py`:

```python
db = MongoDBHandler("mongodb+srv://username:password@cluster.mongodb.net/")
```

## Quick Start

### 1. Install Python dependencies:
```bash
pip install pymongo
```

### 2. Verify MongoDB is running:

#### For Local MongoDB:
```bash
# Windows (PowerShell)
Get-Service MongoDB

# macOS/Linux
sudo systemctl status mongod
```

#### Test connection with Python:
```python
from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017/")
print(client.list_database_names())  # Should print list of databases
```

### 3. Run the application:
```bash
streamlit run app.py
```

## Database Structure

The application creates the following collections:

### 1. **users** collection:
```json
{
  "_id": ObjectId,
  "username": "string",
  "password": "hashed_string",
  "email": "string",
  "created_at": "datetime",
  "last_login": "datetime"
}
```

### 2. **analysis_history** collection:
```json
{
  "_id": ObjectId,
  "user_id": "string",
  "analysis_type": "text_analysis | voice_analysis | facial_analysis",
  "timestamp": "datetime",
  "data": {
    "sentiment": "string",
    "risk_score": "number",
    "wellness_score": "number",
    // ... other analysis-specific data
  }
}
```

### 3. **dashboard_data** collection:
```json
{
  "_id": ObjectId,
  "user_id": "string",
  "data": {
    // Custom dashboard data
  },
  "updated_at": "datetime"
}
```

## Features

- **User Authentication**: Secure login/signup with password hashing
- **Analysis History**: All analyses are saved per user
- **Dashboard Persistence**: User-specific dashboard data
- **Statistics Tracking**: Automatic calculation of user statistics
- **Privacy**: Each user sees only their own data

## Default Configuration

- **Database Name**: `mental_health_db`
- **Connection**: `mongodb://localhost:27017/`
- **Collections**: `users`, `analysis_history`, `dashboard_data`

## Troubleshooting

### Connection Failed Error
- Ensure MongoDB is running: `sudo systemctl status mongod` (Linux/Mac)
- Check if port 27017 is available
- Verify firewall settings

### Authentication Error
- For MongoDB Atlas, ensure IP whitelist is configured
- Verify username and password in connection string
- Check database user permissions

### Data Not Saving
- Check MongoDB logs: `sudo journalctl -u mongod` (Linux)
- Verify user has write permissions
- Ensure sufficient disk space

## Security Notes

⚠️ **For Production:**
- Change default MongoDB port
- Enable authentication
- Use strong passwords
- Configure proper firewall rules
- Use environment variables for credentials
- Enable SSL/TLS encryption
- Regular backups

## Environment Variables (Recommended)

Create a `.env` file:
```
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB=mental_health_db
```

Update `app.py` to use environment variables:
```python
import os
from dotenv import load_dotenv

load_dotenv()
db = MongoDBHandler(os.getenv('MONGODB_URI'))
```

## Backup Your Data

```bash
# Export database
mongodump --db mental_health_db --out backup/

# Import database
mongorestore --db mental_health_db backup/mental_health_db/
```

## MongoDB Compass (GUI Tool)

Download MongoDB Compass for a graphical interface:
https://www.mongodb.com/try/download/compass

Connect using: `mongodb://localhost:27017/`
