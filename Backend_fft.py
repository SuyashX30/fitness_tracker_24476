# Backend_fft.py

import psycopg2
import os
from datetime import date, timedelta

# --- Database Connection ---
# Replace with your actual PostgreSQL connection details
DB_NAME = "fitness_tracker"
DB_USER = "postgres"
DB_PASS = "root"
DB_HOST = "localhost"
DB_PORT = "5432"

def get_db_connection():
    """Establishes and returns a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT
        )
        return conn
    except psycopg2.OperationalError as e:
        print(f"Error connecting to the database: {e}")
        return None

def create_tables():
    """Creates all necessary tables in the database if they don't already exist."""
    conn = get_db_connection()
    if not conn:
        return
    
    commands = (
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            weight_kg NUMERIC(5, 2),
            height_cm NUMERIC(5, 2),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS friends (
            user_id_1 INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
            user_id_2 INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
            PRIMARY KEY (user_id_1, user_id_2)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS workouts (
            workout_id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
            workout_date DATE NOT NULL,
            duration_minutes INTEGER,
            calories_burned INTEGER,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS exercises (
            exercise_id SERIAL PRIMARY KEY,
            workout_id INTEGER NOT NULL REFERENCES workouts(workout_id) ON DELETE CASCADE,
            exercise_name VARCHAR(255) NOT NULL,
            sets INTEGER,
            reps INTEGER,
            weight_kg NUMERIC(6, 2)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS goals (
            goal_id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
            goal_description TEXT NOT NULL,
            target_value NUMERIC,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            status VARCHAR(50) DEFAULT 'Active'
        )
        """
    )
    
    try:
        with conn.cursor() as cur:
            for command in commands:
                cur.execute(command)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error creating tables: {error}")
    finally:
        if conn:
            conn.close()

# --- CRUD Operations ---

# CREATE
def add_user(name, email, weight, height):
    """Adds a new user to the database."""
    sql = "INSERT INTO users(name, email, weight_kg, height_cm) VALUES(%s, %s, %s, %s) RETURNING user_id;"
    conn = get_db_connection()
    user_id = None
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (name, email, weight, height))
            user_id = cur.fetchone()[0]
            conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error adding user: {error}")
    finally:
        if conn:
            conn.close()
    return user_id

def log_workout(user_id, workout_date, duration, calories, exercises):
    """Logs a new workout and its associated exercises."""
    workout_sql = "INSERT INTO workouts(user_id, workout_date, duration_minutes, calories_burned) VALUES(%s, %s, %s, %s) RETURNING workout_id;"
    exercise_sql = "INSERT INTO exercises(workout_id, exercise_name, sets, reps, weight_kg) VALUES(%s, %s, %s, %s, %s);"
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(workout_sql, (user_id, workout_date, duration, calories))
            workout_id = cur.fetchone()[0]
            for ex in exercises:
                cur.execute(exercise_sql, (workout_id, ex['name'], ex['sets'], ex['reps'], ex['weight']))
            conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error logging workout: {error}")
    finally:
        if conn:
            conn.close()

def add_friend(user_id, friend_id):
    """Connects two users as friends."""
    sql = "INSERT INTO friends(user_id_1, user_id_2) VALUES(%s, %s);"
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Insert both ways to make querying easier
            cur.execute(sql, (user_id, friend_id))
            cur.execute(sql, (friend_id, user_id))
            conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error adding friend: {error}")
    finally:
        if conn:
            conn.close()

def set_goal(user_id, description, target_value, start_date, end_date):
    """Sets a new fitness goal for a user."""
    sql = "INSERT INTO goals(user_id, goal_description, target_value, start_date, end_date) VALUES(%s, %s, %s, %s, %s);"
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (user_id, description, target_value, start_date, end_date))
            conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error setting goal: {error}")
    finally:
        if conn:
            conn.close()

# READ
def get_all_users():
    """Retrieves all users from the database."""
    conn = get_db_connection()
    users = []
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT user_id, name, email FROM users ORDER BY name;")
            users = cur.fetchall()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error fetching users: {error}")
    finally:
        if conn:
            conn.close()
    return users
    
def get_user_profile(user_id):
    """Retrieves a specific user's profile."""
    conn = get_db_connection()
    user = None
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT name, email, weight_kg, height_cm FROM users WHERE user_id = %s;", (user_id,))
            user = cur.fetchone()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error fetching user profile: {error}")
    finally:
        if conn:
            conn.close()
    return user

def get_user_workouts(user_id):
    """Retrieves all workouts for a specific user."""
    sql = """
        SELECT workout_id, workout_date, duration_minutes, calories_burned 
        FROM workouts 
        WHERE user_id = %s 
        ORDER BY workout_date DESC;
    """
    conn = get_db_connection()
    workouts = []
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (user_id,))
            workouts = cur.fetchall()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error fetching workouts: {error}")
    finally:
        if conn:
            conn.close()
    return workouts

def get_workout_details(workout_id):
    """Retrieves all exercises for a specific workout."""
    sql = "SELECT exercise_name, sets, reps, weight_kg FROM exercises WHERE workout_id = %s;"
    conn = get_db_connection()
    exercises = []
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (workout_id,))
            exercises = cur.fetchall()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error fetching workout details: {error}")
    finally:
        if conn:
            conn.close()
    return exercises

def get_user_friends(user_id):
    """Retrieves all friends for a specific user."""
    sql = """
        SELECT u.user_id, u.name 
        FROM users u
        JOIN friends f ON u.user_id = f.user_id_2
        WHERE f.user_id_1 = %s
        ORDER BY u.name;
    """
    conn = get_db_connection()
    friends = []
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (user_id,))
            friends = cur.fetchall()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error fetching friends: {error}")
    finally:
        if conn:
            conn.close()
    return friends

def get_user_goals(user_id):
    """Retrieves all goals for a specific user."""
    sql = "SELECT goal_id, goal_description, target_value, start_date, end_date, status FROM goals WHERE user_id = %s;"
    conn = get_db_connection()
    goals = []
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (user_id,))
            goals = cur.fetchall()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error fetching goals: {error}")
    finally:
        if conn:
            conn.close()
    return goals

# UPDATE
def update_user_profile(user_id, name, email, weight, height):
    """Updates a user's profile information."""
    sql = "UPDATE users SET name = %s, email = %s, weight_kg = %s, height_cm = %s WHERE user_id = %s;"
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (name, email, weight, height, user_id))
            conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error updating profile: {error}")
    finally:
        if conn:
            conn.close()

# DELETE
def remove_friend(user_id, friend_id):
    """Removes a friend connection."""
    sql = "DELETE FROM friends WHERE (user_id_1 = %s AND user_id_2 = %s) OR (user_id_1 = %s AND user_id_2 = %s);"
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (user_id, friend_id, friend_id, user_id))
            conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error removing friend: {error}")
    finally:
        if conn:
            conn.close()
            
# --- Business Insights & Leaderboard ---

def get_user_dashboard_stats(user_id):
    """Calculates key fitness statistics for the user's dashboard."""
    stats = {}
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # COUNT: Total workouts
            cur.execute("SELECT COUNT(*) FROM workouts WHERE user_id = %s;", (user_id,))
            stats['total_workouts'] = cur.fetchone()[0]
            
            # SUM: Total workout minutes
            cur.execute("SELECT SUM(duration_minutes) FROM workouts WHERE user_id = %s;", (user_id,))
            stats['total_minutes'] = cur.fetchone()[0] or 0

            # AVG: Average workout duration
            cur.execute("SELECT AVG(duration_minutes) FROM workouts WHERE user_id = %s;", (user_id,))
            stats['avg_duration'] = cur.fetchone()[0] or 0

            # MAX: Longest workout
            cur.execute("SELECT MAX(duration_minutes) FROM workouts WHERE user_id = %s;", (user_id,))
            stats['max_duration'] = cur.fetchone()[0] or 0

            # MIN: Shortest workout
            cur.execute("SELECT MIN(duration_minutes) FROM workouts WHERE user_id = %s;", (user_id,))
            stats['min_duration'] = cur.fetchone()[0] or 0
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error fetching dashboard stats: {error}")
    finally:
        if conn:
            conn.close()
    return stats

def get_weekly_leaderboard(user_id):
    """Generates a leaderboard of the user and their friends based on total workout minutes this week."""
    # The user and their friends
    friend_ids = [friend[0] for friend in get_user_friends(user_id)]
    user_and_friends_ids = tuple(friend_ids + [user_id])
    
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    
    sql = """
        SELECT u.name, SUM(w.duration_minutes) as total_minutes
        FROM users u
        JOIN workouts w ON u.user_id = w.user_id
        WHERE u.user_id IN %s AND w.workout_date >= %s
        GROUP BY u.name
        ORDER BY total_minutes DESC;
    """
    
    leaderboard = []
    conn = get_db_connection()
    # Ensure there's at least one ID to prevent SQL error with empty IN clause
    if not user_and_friends_ids:
        return []
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (user_and_friends_ids, start_of_week))
            leaderboard = cur.fetchall()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error fetching leaderboard: {error}")
    finally:
        if conn:
            conn.close()
    return leaderboard


# --- Initial Data Seeding (for demonstration) ---
def seed_data():
    """Adds some initial data to the database for demonstration purposes."""
    if not get_all_users(): # Only seed if users table is empty
        print("Seeding initial data...")
        # Users
        u1 = add_user("Alice", "alice@email.com", 60.5, 165)
        u2 = add_user("Bob", "bob@email.com", 85.0, 180)
        u3 = add_user("Charlie", "charlie@email.com", 72.3, 175)
        
        # Friendships (Alice is friends with Bob and Charlie)
        add_friend(u1, u2)
        add_friend(u1, u3)
        
        # Workouts
        today = date.today()
        # Alice's Workouts
        log_workout(u1, today - timedelta(days=1), 60, 300, [{'name': 'Squat', 'sets': 3, 'reps': 10, 'weight': 50}])
        log_workout(u1, today - timedelta(days=3), 45, 250, [{'name': 'Bench Press', 'sets': 3, 'reps': 8, 'weight': 60}])
        # Bob's Workouts
        log_workout(u2, today - timedelta(days=2), 90, 500, [{'name': 'Deadlift', 'sets': 5, 'reps': 5, 'weight': 120}])
        # Charlie's Workouts
        log_workout(u3, today, 75, 400, [{'name': 'Running', 'sets': 1, 'reps': 1, 'weight': 0}])
        
        # Goals for Alice
        set_goal(u1, "Workout 3 times this week", 3, today - timedelta(days=today.weekday()), today + timedelta(days=6-today.weekday()))
        print("Seeding complete.")


# Main execution
if __name__ == "__main__":
    create_tables()
    seed_data()