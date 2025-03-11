import streamlit as st
import wikipedia
import pyttsx3
import pymysql
import re
from datetime import datetime

# MySQL Configuration
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "nyfa@27octP"
MYSQL_DB = "wikipedia_app"



# Connect to MySQL
def get_db_connection():
    return pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB)

# Function to check if username exists
def check_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

# Function to register a new user
def register_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
    conn.commit()
    conn.close()

# Store search history
def save_search_history(username, title, summary, lang):
    conn = get_db_connection()
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO history (username, title, summary, lang, timestamp) VALUES (%s, %s, %s, %s, %s)",
                   (username, title, summary, lang, timestamp))
    conn.commit()
    conn.close()

# Retrieve search history
def get_search_history(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT title, summary, lang, timestamp FROM history WHERE username = %s ORDER BY timestamp DESC", (username,))
    history = cursor.fetchall()
    conn.close()
    return history

# Clear search history
def clear_history(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM history WHERE username = %s", (username,))
    conn.commit()
    conn.close()

# Wikipedia Summary with Approximate Word Limit
def get_wikipedia_summary(title, word_limit, lang):
    try:
        wikipedia.set_lang(lang)
        summary = wikipedia.summary(title)
        words = summary.split()

        if len(words) <= word_limit:
            return summary

        approx_text = " ".join(words[:word_limit + 20])
        sentences = re.findall(r'[^.?!]+[.?!]', approx_text)
        final_summary = ""
        word_count = 0

        for sentence in sentences:
            word_count += len(sentence.split())
            if word_count > word_limit:
                break
            final_summary += sentence + " "

        return final_summary.strip()

    except wikipedia.exceptions.DisambiguationError as e:
        return f"Disambiguation Error! Choose a more specific title: {', '.join(e.options)}"
    except wikipedia.exceptions.PageError:
        return "Page not found! Enter a valid Wikipedia title."
    except wikipedia.exceptions.HTTPTimeoutError:
        return "Error: Wikipedia API request timed out."
    except Exception as e:
        return f"An error occurred: {e}"

# Text-to-Speech Function
def speak_text(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.say(text)
    engine.runAndWait()

# Streamlit UI
st.title("📚 Wikipedia Summarizer")

# Initialize session state for login
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["username"] = None
    st.session_state["show_history"] = False

# Sidebar for Login/Register options
st.sidebar.subheader("🔑 Select an Option")
auth_option = st.sidebar.selectbox("Login or Register", ["Login", "Register"])

# If user is not logged in, show login/register interface
if not st.session_state["logged_in"]:
    if auth_option == "Login":
        st.subheader("🔑 Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = check_user(username, password)
            if user:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.success(f"Welcome, {username}!")
                st.experimental_rerun()
            else:
                st.error("Invalid username or password. Please try again.")

    elif auth_option == "Register":
        st.subheader("📝 Register")

        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        if st.button("Register"):
            if new_password != confirm_password:
                st.warning("Passwords do not match! Try again.")
            elif new_username and new_password:
                register_user(new_username, new_password)
                st.success("Registration successful! You can now login.")
            else:
                st.warning("Please fill in all fields.")

# If user is logged in, show Wikipedia summarizer
if st.session_state["logged_in"]:
    username = st.session_state["username"]

    col1, col2 = st.columns([0.8, 0.2])

    with col1:
        st.subheader(f"Hello, {username}! Start Searching on Wikipedia 📖")

    with col2:
        if st.button("📜 View History"):
            st.session_state["show_history"] = not st.session_state["show_history"]
            st.experimental_rerun()

    # Show history if button is clicked
    if st.session_state["show_history"]:
        st.subheader("📜 Search History")
        history = get_search_history(username)

        if history:
            for entry in history:
                st.markdown(f"**🔹 {entry[0]} ({entry[2]})** - {entry[3]}")
                st.write(f"{entry[1][:300]}...")  # Show only first 300 chars
                st.markdown("---")

            if st.button("🗑 Clear History"):
                clear_history(username)
                st.session_state["show_history"] = False
                st.experimental_rerun()
        else:
            st.info("No search history found.")

    # Language selection
    LANGUAGES = {
        "English": "en",
        "Telugu": "te",
        "Hindi": "hi",
        "Spanish": "es",
        "French": "fr",
        "German": "de",
        "Chinese": "zh",
        "Russian": "ru",
    }
    selected_language = st.selectbox("Choose Language:", list(LANGUAGES.keys()))
    lang_code = LANGUAGES.get(selected_language, "en")


    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        st.session_state["username"] = None
        st.session_state["show_history"] = False  # ✅ Ensure show_history is initialized

    # Wikipedia inputs
    page_title = st.text_input("Enter Wikipedia page title:")
    word_limit = st.number_input("Enter number of words:", min_value=10, max_value=500, value=50, step=10)

    if st.button("Get Summary"):
        if page_title:
            summary = get_wikipedia_summary(page_title, word_limit, lang_code)
            st.subheader(f"Summary of '{page_title}' in {selected_language}:")
            st.write(summary)

            # Save search history
            save_search_history(username, page_title, summary, lang_code)

            # Read Aloud Button
            if st.button("Read Aloud"):
                speak_text(summary)
        else:
            st.warning("Please enter a Wikipedia page title.")

    # Logout Button
    if st.sidebar.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = None
        st.session_state["show_history"] = False
        st.experimental_rerun()
