# Server-Side Session Management

## Overview
The application uses **server-side session management** with MongoDB and **browser localStorage** to persist user login sessions across page refreshes and browser sessions.

## How It Works

### 1. **Session Creation (Login)**
- When a user logs in successfully, the system:
  - Creates a secure session token using `secrets.token_urlsafe(32)`
  - Stores session data in MongoDB (`sessions` collection)
  - Saves token to browser's **localStorage** via JavaScript
  - Adds token to URL **query parameters** for immediate access
  - Session expires after 30 days (configurable)

### 2. **Session Validation (Page Refresh)**
- On each page load:
  - JavaScript reads token from localStorage
  - Adds token to URL query parameters automatically
  - Python validates token against MongoDB
  - If valid, restores user session automatically
  - User stays logged in! ✨

### 3. **Session Termination (Logout)**
- When user logs out:
  - Deletes session from MongoDB
  - Clears localStorage via JavaScript
  - Removes query parameters
  - Clears Streamlit session state

## Features

### ✅ Persistent Login
- Users stay logged in even after refreshing the page (F5)
- Sessions persist across browser tabs
- Login survives browser restart (until localStorage is cleared)
- Works across all modern browsers

### 🔒 Security
- Secure random session tokens (256-bit)
- Server-side session validation
- Automatic expiration after 30 days
- MongoDB TTL index for auto-cleanup of expired sessions
- No sensitive data stored in browser

### 📊 Session Data Stored
Each session stores:
- `session_token`: Unique identifier
- `user_id`: User's database ID
- `username`: User's username
- `email`: User's email
- `created_at`: Session creation timestamp
- `expires_at`: Session expiration timestamp
- `last_accessed`: Last activity timestamp

## Technical Implementation

### MongoDB Collections

#### `sessions` Collection
```javascript
{
  "session_token": "random_secure_token_here",
  "user_id": "user_object_id",
  "username": "john_doe",
  "email": "john@example.com",
  "created_at": ISODate("2025-11-03T10:00:00Z"),
  "expires_at": ISODate("2025-12-03T10:00:00Z"),
  "last_accessed": ISODate("2025-11-03T10:00:00Z")
}
```

### Indexes
- `session_token`: Unique index for fast lookup
- `expires_at`: TTL index (expireAfterSeconds=0) for automatic cleanup

### Browser Storage
- **localStorage Key**: `mental_health_session`
- **URL Query Param**: `?session_token=...`
- **Storage Type**: Browser localStorage (persistent)
- **Scope**: Per origin (domain + protocol + port)

## Dependencies

- `streamlit`: Built-in components for JavaScript injection
- `pymongo`: For MongoDB operations
- `secrets`: For secure token generation
- **No external cookie libraries required!**

## Configuration

To change session expiration time, modify the `expiry_days` parameter in `create_session()`:

```python
session_token = db_handler.create_session(
    user['user_id'],
    user['username'],
    user['email'],
    expiry_days=30  # Change this value
)
```

## Browser Compatibility

Works on all modern browsers that support:
- localStorage API (all browsers since IE 8)
- URL query parameters (universal support)
- JavaScript (enabled by default)

## Troubleshooting

### Session Not Persisting
1. Check MongoDB is running
2. Check browser allows localStorage (not in private/incognito mode)
3. Check JavaScript is enabled
4. Clear browser localStorage: `localStorage.clear()` in browser console

### Session Expires Too Quickly
- Increase `expiry_days` in session creation
- Check MongoDB TTL index is properly configured
- Verify server time is correct

### Multiple Logins
- System allows multiple active sessions per user
- Each device/browser gets its own session token
- Use `delete_user_sessions()` to clear all sessions for a user

## API Methods

### `create_session(user_id, username, email, expiry_days=30)`
Creates a new session and returns session token.

### `get_session(session_token)`
Retrieves and validates session data.

### `delete_session(session_token)`
Deletes a specific session.

### `delete_user_sessions(user_id)`
Deletes all sessions for a user.

### `set_session_cookie(session_token)`
Saves token to browser localStorage via JavaScript.

### `get_session_cookie()`
Reads token from localStorage or URL query params.

### `clear_session_cookie()`
Removes token from browser localStorage.

## Privacy & Security Notes

- Sessions are stored server-side in MongoDB
- Only session tokens are stored in browser localStorage
- No sensitive data (passwords) in browser storage
- Automatic cleanup of expired sessions
- Last accessed timestamp tracks activity
- localStorage is domain-specific (not shared across sites)
- Tokens are cryptographically secure random strings

## Migration from Cookies

Previous implementation used `extra-streamlit-components` for cookies, which had reliability issues. The new localStorage + query params approach is:
- ✅ More reliable across page refreshes
- ✅ Better browser compatibility  
- ✅ No external dependencies
- ✅ Simpler implementation
- ✅ More maintainable
