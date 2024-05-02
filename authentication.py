import jwt
import streamlit as st
from streamlit import write
from datetime import datetime, timedelta
import hashlib

# Replace with your secure storage mechanism (e.g., database)
usernames = {"user1": "password1_hashed", "user2": "password2_hashed"}  # Hashed passwords

# Secret key for JWT encoding (**never store this in your code!**). Use a secure environment variable.
SECRET_KEY = "mysecretkey"

# Function to validate user credentials (replace with your backend logic)
def validate_user(username, password):
    if username in usernames and usernames[username] == password:
        return True
    return False

def generate_jwt_token(username):
    payload = {
        "username": username,
        "exp": datetime.utcnow() + timedelta(minutes=60)  # Token expiration time (1 hour)
    }
    encoded = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return encoded  # Decode for string representation

def verify_jwt_token(token):
    try:
        payload = jwt.decode(token.encode("utf-8"), SECRET_KEY, algorithms=["HS256"])
        return payload["username"]
    except jwt.exceptions.JWTError:
        return None

def hash_password(password):
    # Replace with your preferred hashing algorithm (e.g., bcrypt, argon2)
    return hashlib.sha256(password.encode("utf-8")).hexdigest()  # Example using SHA-256

def auth(mongo_client):
    # Set up authentication state and login form
    authenticated = False
    username = None
    if "token" in st.session_state:
        username = verify_jwt_token(st.session_state["token"])
        authenticated = username is not None

    # Display login or signup form based on authentication status
    if not authenticated:
        page = st.selectbox("Select Page", ["Login", "Signup"])

        if page == "Login":
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_button = st.button("Login")

            if login_button:
                if validate_user(username, password):
                    token = generate_jwt_token(username)
                    st.session_state["token"] = token
                    authenticated = True
                else:
                    st.error("Invalid username or password")

        elif page == "Signup":
            new_username = st.text_input("New Username")
            new_password = st.text_input("New Password", type="password")
            signup_button = st.button("Signup")

            if signup_button:
                if new_username not in usernames:
                    usernames[new_username] = hash_password(new_password)  # Store hashed password
                    st.success("Signup successful. Please login to proceed.")
                else:
                    st.error("Username already exists.")

    else:
        st.write(f"Welcome, {username}!")

        # App functionality accessible only to logged-in users
        st.write("This content is visible only after successful login.")

        # Example: Display data based on user role (if implemented)
        if username == "user1":
            st.write("You have access to user1-specific data.")
        else:
            st.write("You have access to user2-specific data.")

        logout_button = st.button("Logout")
        if logout_button:
            del st.session_state["token"]
            authenticated = False
            st.experimental_rerun()  # Refresh app after logout