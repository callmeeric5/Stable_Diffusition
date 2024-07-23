import streamlit as st
import requests
from datetime import datetime

# API URLs
SIGNUP_URL = 'http://localhost:8000/signup'
LOGIN_URL = 'http://localhost:8000/login'
PROTECTED_URL = 'http://localhost:8000/protected'

def signup(username, email, password, date_of_birth):
    """Sign up a new user."""
    response = requests.post(SIGNUP_URL, json={
        'username': username,
        'email': email,
        'password': password,
        'date_of_birth': date_of_birth.strftime('%Y-%m-%d')  # Convert date to string
    })
    if response.status_code == 201:
        st.success('User created successfully')
    else:
        st.error(f'Error creating user: {response.text}')

def login(identifier, password):
    """Log in a user and store the JWT token."""
    response = requests.post(LOGIN_URL, json={
        'identifier': identifier,
        'password': password
    })
    if response.status_code == 200:
        token = response.json().get('token')
        st.session_state.token = token
        st.success(f'Login successful! Token: {token}')
    else:
        st.error(f'Error logging in: {response.text}')

def access_protected_route():
    """Access a protected route using the stored JWT token."""
    if 'token' not in st.session_state:
        st.error('You need to log in first')
        return

    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    response = requests.get(PROTECTED_URL, headers=headers)
    if response.status_code == 200:
        data = response.json()
        st.write("Protected data:", data)
    else:
        st.error("Failed to access protected route.")

# Streamlit interface
st.title('User Authentication')

# Sidebar for navigation
st.sidebar.title('Navigation')
option = st.sidebar.selectbox('Choose an option', ['Signup', 'Login', 'Access Protected Route'])

if option == 'Signup':
    st.header('Signup')
    with st.form(key='signup_form'):
        username = st.text_input('Username')
        email = st.text_input('Email')
        password = st.text_input('Password', type='password')
        date_of_birth = st.date_input('Date of Birth')

        submit_button = st.form_submit_button('Signup')
        if submit_button:
            if username and email and password and date_of_birth:
                signup(username, email, password, date_of_birth)
            else:
                st.error('Please fill all fields')

elif option == 'Login':
    st.header('Login')
    with st.form(key='login_form'):
        identifier = st.text_input('Username or Email')
        password = st.text_input('Password', type='password')

        login_button = st.form_submit_button('Login')
        if login_button:
            if identifier and password:
                login(identifier, password)
            else:
                st.error('Please fill all fields')

elif option == 'Access Protected Route':
    st.header('Protected Route')
    if st.button('Access'):
        access_protected_route()
