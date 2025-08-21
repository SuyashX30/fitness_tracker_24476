# fitness_tracker_24476

Fitness Tracker Application
A full-stack personal fitness tracking application built with Python. It allows users to monitor their workouts, connect with friends, set goals, and compete on a dynamic leaderboard. The frontend is powered by Streamlit, and it uses a PostgreSQL database for robust data storage.

✨ Features
User Profile Management: Create and update your personal profile (name, email, weight, height).

Workout Logging: Log detailed workout sessions, including date, duration, calories burned, and specific exercises with sets, reps, and weight.

Workout History: View a complete history of all your workouts and visualize your progress over time with an interactive chart.

Goal Setting: Set personal fitness goals with start and end dates to stay motivated.

Social Connections: Add and remove friends to share your fitness journey.

Dynamic Leaderboard: Compete with friends on a weekly leaderboard ranked by total workout minutes.

Fitness Insights: Get a personalized dashboard with key stats like your weekly workout count, total minutes, and a summary of your most recent activity.

🛠️ Tech Stack
Frontend: Streamlit

Backend: Python

Database: PostgreSQL

Database Connector: psycopg2-binary

Data Manipulation: Pandas

🚀 Setup and Installation
Follow these steps to get the application running on your local machine.

1. Prerequisites
Python 3.8+

PostgreSQL installed and running.

2. Clone the Repository (Optional)
If this were a Git repository, you would clone it. For now, just ensure you have the required files.

git clone https://your-repository-url.git
cd fitness-tracker-app

3. Install Python Dependencies
Create and activate a virtual environment, then install the required libraries.

# Create a virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Activate it (macOS/Linux)
source venv/bin/activate

# Install libraries
pip install streamlit psycopg2-binary pandas

🗄️ Database Setup
You need to create a PostgreSQL database and a user for the application to connect to.

Open psql or your preferred PostgreSQL client.

Create a new database:

CREATE DATABASE fitness_tracker;

Create a new user and grant privileges:
(Replace 'your_secure_password' with a strong password)

CREATE USER fitness_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE fitness_tracker TO fitness_user;

Update Backend Configuration:
Open the Backend_fft.py file and update the connection details with your credentials:

# Backend_fft.py

DB_NAME = "fitness_tracker"
DB_USER = "fitness_user"
DB_PASS = "your_secure_password" # <-- IMPORTANT: Update this line
DB_HOST = "localhost"
DB_PORT = "5432"

▶️ How to Run the Application
Make sure your PostgreSQL server is running.

Navigate to the project directory in your terminal.

Run the Streamlit application:

streamlit run Frontend_ft.py

Your web browser should automatically open to the application's URL (usually http://localhost:8501). The first time you run it, the backend script will automatically create the necessary tables and seed the database with sample data.

📁 File Structure
.
├── Backend_fft.py      # Handles all database logic (connection, CRUD operations, insights).
├── Frontend_ft.py      # Defines the Streamlit user interface and application flow.
└── README.md           # You are here!
