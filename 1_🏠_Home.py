import streamlit as st
from utils import init_session_state, signup, login, logout
from sqlalchemy.orm import Session
from utils import get_db

st.set_page_config(page_title="Image Generation App", layout="wide")

init_session_state()


def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "current_user" not in st.session_state:
        st.session_state.current_user = None

    st.title("The NextDiffusion🌟")

    if not st.session_state.logged_in:
        login_signup()
    else:
        logged_in_view()


def login_signup():
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        st.header("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            db: Session = get_db().__next__()
            user = login(username, password, db)
            if user:
                st.session_state.logged_in = True
                st.session_state.current_user = {
                    "id": user.id,
                    "username": user.username,
                }
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid username or password")

    with tab2:
        st.header("Sign Up")
        new_username = st.text_input("Username", key="signup_username")
        new_password = st.text_input("Password", type="password", key="signup_password")
        email = st.text_input("Email", key="email")
        date_of_birth = st.date_input("Date of Birth", key="date_of_birth")

        if st.button("Sign Up"):

            if signup(new_username, new_password, email, date_of_birth):
                st.success("Account created successfully! Please log in.")
            else:
                st.error("Username already exists")


def logged_in_view():
    st.markdown("""
       <style>
       .welcome-container {
           padding: 2rem;
           border-radius: 10px;
           box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
       }
       .welcome-header {

           font-size: 1.8rem;
           font-weight: bold;
           margin-bottom: 1rem;
       }
       .welcome-text {
    
           font-size: 1rem;
           line-height: 1.6;
           margin-bottom: 1rem;
       }
       .welcome-highlight {

           font-weight: bold;
           font-size: 1.2rem;
       }
       </style>
       """, unsafe_allow_html=True)

    # Welcome message
    st.markdown(f"""
       <div class="welcome-container">
           <h1 class="welcome-header">Welcome to the land of infinite canvases, {st.session_state.current_user['username']}!</h1>
           <p class="welcome-text">Your words are the paintbrushes! You've successfully logged in and are now ready to turn your imagination into stunning visuals.</p>
           <p class="welcome-text">Dive into the world of text-to-image magic and watch your ideas come alive in vibrant detail. Whether you're crafting eye-catching graphics or exploring creative concepts, we're thrilled to have you on board.</p>
           <p class="welcome-text">Let's create something amazing together!</p>
           <p class="welcome-highlight">Happy Generating! 🚀</p>
       </div>
       """, unsafe_allow_html=True)

    if st.button("Logout"):
        logout()
        st.rerun()

    st.sidebar.success("Select a page above.")


if __name__ == "__main__":
    main()
