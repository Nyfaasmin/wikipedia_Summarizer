# Wikipedia Summarizer with Login & Registration

## 📖 About the Project
This is a **Wikipedia Summarizer** built with **Streamlit**, allowing users to:
- Register and log in
- Search Wikipedia in multiple languages
- Get a summarized version of Wikipedia articles
- Save and view search history
- Convert the summary to speech using Text-to-Speech (TTS)
- Clear search history

## 🚀 Features
- **User Authentication:** Secure login and registration system
- **Multi-language Support:** Search Wikipedia in multiple languages
- **History Management:** Save, view, and clear search history
- **Text-to-Speech:** Listen to the summarized content
- **Responsive UI:** Built using Streamlit for an interactive experience

## 🛠️ Tech Stack
- **Backend:** Python, Streamlit, MySQL, Pyttsx3, Wikipedia API
- **Database:** MySQL
- **Libraries Used:**
  - `streamlit` (UI framework)
  - `wikipedia` (Wikipedia API)
  - `pyttsx3` (Text-to-Speech)
  - `pymysql` (Database connection)

## 🗃 Database Schema
### **Users Table**
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);
```
### **History Table**
```sql
CREATE TABLE history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    summary TEXT NOT NULL,
    lang VARCHAR(10) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 📌 Installation
### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/your-repo/wikipedia-summarizer.git
cd wikipedia-summarizer
```

### **2️⃣ Install Dependencies**
```bash
pip install -r requirements.txt
```

### **3️⃣ Setup MySQL Database**
- Create a database named `wikipedia_app`
- Run the SQL commands to create tables (`users` and `history`)
- Update database credentials in the Python script:
```python
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "your_password"
MYSQL_DB = "wikipedia_app"
```

### **4️⃣ Run the Application**
```bash
streamlit run app.py
```

## 🔥 Usage
1. **Register** for an account.
2. **Log in** to access the summarizer.
3. Choose a **language** and enter a **Wikipedia title**.
4. Click **"Get Summary"** to retrieve and save the summary.
5. Click **"Read Aloud"** to listen to the summary.
6. View search history and clear it if needed.
7. Log out when finished.

## 🎯 Future Enhancements
- Implement OAuth for secure authentication
- Add more language support
- Improve UI design with custom CSS
- Provide an option to download summaries

## 🤝 Contributing
Feel free to fork this repo and submit pull requests! 🚀

## 📜 License
This project is licensed under the **MIT License**.

## 🛠 Author
**Pathan Nyfa Asmin** - B.Tech CSE - Shri Vishnu Engineering College for Women

