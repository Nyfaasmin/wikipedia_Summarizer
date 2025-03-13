import streamlit as st
import wikipedia
import pyttsx3
import pymongo
import re
import threading
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")

# Connect to MongoDB
client = pymongo.MongoClient(MONGO_URI)
db = client[MONGO_DB]
users_collection = db["users"]
history_collection = db["history"]

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.update({"logged_in": False, "username": None, "show_history": False, "summary": ""})

# Initialize pyttsx3 engine globally
engine = pyttsx3.init()
engine.setProperty('rate', 150)

def check_user(username, password):
    return users_collection.find_one({"username": username, "password": password})

def register_user(username, password):
    users_collection.insert_one({"username": username, "password": password})

def save_search_history(username, title, summary, lang):
    history_collection.insert_one({
        "username": username, "title": title, "summary": summary, "lang": lang, "timestamp": datetime.now()
    })

def get_search_history(username):
    return list(history_collection.find({"username": username}).sort("timestamp", -1))

def clear_history(username):
    history_collection.delete_many({"username": username})

def get_wikipedia_summary(title, word_limit, lang):
    try:
        wikipedia.set_lang(lang)
        summary = wikipedia.summary(title)
        words = summary.split()

        if len(words) <= word_limit:
            return summary

        approx_text = " ".join(words[:word_limit + 20])
        sentences = re.findall(r'[^.?!]+[.?!]', approx_text)
        final_summary, word_count = "", 0

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

def speak_text_pyttsx3(text):
    global engine
    engine.stop()  # Stop previous speech
    def run_speech():
        engine.say(text)
        engine.runAndWait()
    threading.Thread(target=run_speech, daemon=True).start()

def stop_speech():
    global engine
    engine.stop()

# Streamlit UI
st.title("📚 Wikipedia Summarizer")

st.sidebar.subheader("🔑 Select an Option")
auth_option = st.sidebar.selectbox("Login or Register", ["Login", "Register"])

if not st.session_state["logged_in"]:
    if auth_option == "Login":
        st.subheader("🔑 Login")
        username, password = st.text_input("Username"), st.text_input("Password", type="password")
        if st.button("Login"):
            if check_user(username, password):
                st.session_state.update({"logged_in": True, "username": username})
                st.success(f"Welcome, {username}!")
                st.rerun()
            else:
                st.error("Invalid credentials. Try again.")
    else:
        st.subheader("📝 Register")
        new_username, new_password = st.text_input("New Username"), st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        if st.button("Register"):
            if new_password != confirm_password:
                st.warning("Passwords do not match!")
            elif new_username and new_password:
                register_user(new_username, new_password)
                st.success("Registration successful! You can now login.")
            else:
                st.warning("Please fill in all fields.")

if st.session_state["logged_in"]:
    username = st.session_state["username"]
    st.subheader(f"Hello, {username}! Start Searching on Wikipedia 📖")

    if st.button("📜 View History"):
        st.session_state["show_history"] = not st.session_state["show_history"]
        st.rerun()

    if st.session_state["show_history"]:
        st.subheader("📜 Search History")
        history = get_search_history(username)
        if history:
            for entry in history:
                st.markdown(f"**🔹 {entry['title']} ({entry['lang']})** - {entry['timestamp']}")
                st.write(f"{entry['summary'][:300]}...")
                st.markdown("---")
            if st.button("🗑 Clear History"):
                clear_history(username)
                st.session_state["show_history"] = False
                st.rerun()
        else:
            st.info("No search history found.")

    LANGUAGES = {"English": "en", "Telugu": "te", "Hindi": "hi", "Spanish": "es", "French": "fr", "German": "de", "Chinese": "zh", "Russian": "ru"}
    lang_code = LANGUAGES[st.selectbox("Choose Language:", list(LANGUAGES.keys()))]

    page_title = st.text_input("Enter Wikipedia page title:")
    word_limit = st.number_input("Enter number of words:", min_value=10, max_value=500, value=50, step=10)

    if st.button("Get Summary") and page_title:
        st.session_state["summary"] = get_wikipedia_summary(page_title, word_limit, lang_code)
        save_search_history(username, page_title, st.session_state["summary"], lang_code)

    if st.session_state["summary"]:
        st.subheader(f"Summary of '{page_title}':")
        st.write(st.session_state["summary"])
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Read Aloud"):
                speak_text_pyttsx3(st.session_state["summary"])
        with col2:
            if st.button("Stop Voice"):
                stop_speech()

    if st.sidebar.button("Logout"):
        st.session_state.update({"logged_in": False, "username": None, "show_history": False, "summary": ""})
        st.rerun()
