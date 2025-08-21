# Frontend_ft.py

import streamlit as st
import pandas as pd
from datetime import date, timedelta
import Backend_fft as be # Import the backend logic

# --- App Configuration ---
st.set_page_config(page_title="Fitness Tracker", layout="wide", initial_sidebar_state="expanded")

# For this single-user demo, we'll hardcode the current user's ID.
# In a real app, this would come from a login system.
CURRENT_USER_ID = 1 

# --- Helper Functions ---
def get_current_user_name():
    """Fetches the current user's name for display."""
    profile = be.get_user_profile(CURRENT_USER_ID)
    return profile[0] if profile else "User"

# --- UI Sections ---

def show_profile():
    st.header("👤 My Profile")
    profile = be.get_user_profile(CURRENT_USER_ID)
    if profile:
        with st.form("profile_form"):
            name = st.text_input("Name", value=profile[0])
            email = st.text_input("Email", value=profile[1])
            weight = st.number_input("Weight (kg)", value=float(profile[2]))
            height = st.number_input("Height (cm)", value=float(profile[3]))
            
            submitted = st.form_submit_button("Update Profile")
            if submitted:
                be.update_user_profile(CURRENT_USER_ID, name, email, weight, height)
                st.success("Profile updated successfully!")
                st.experimental_rerun()
    else:
        st.warning("Could not load user profile.")

def log_workout():
    st.header("🏋️ Log a New Workout")
    with st.form("workout_form"):
        workout_date = st.date_input("Workout Date", value=date.today())
        duration = st.number_input("Duration (minutes)", min_value=1, step=1)
        calories = st.number_input("Calories Burned (optional)", min_value=0, step=1)
        st.markdown("---")
        st.subheader("Exercises")
        
        # Use a list in session state to manage exercises dynamically
        if 'exercises' not in st.session_state:
            st.session_state.exercises = [{'name': '', 'sets': 3, 'reps': 10, 'weight': 20.0}]

        for i, ex in enumerate(st.session_state.exercises):
            cols = st.columns([3, 1, 1, 1])
            ex['name'] = cols[0].text_input("Exercise Name", value=ex['name'], key=f"name_{i}")
            ex['sets'] = cols[1].number_input("Sets", min_value=1, value=ex['sets'], key=f"sets_{i}")
            ex['reps'] = cols[2].number_input("Reps", min_value=1, value=ex['reps'], key=f"reps_{i}")
            ex['weight'] = cols[3].number_input("Weight (kg)", min_value=0.0, value=ex['weight'], step=0.5, key=f"weight_{i}")
        
        cols_buttons = st.columns(2)
        if cols_buttons[0].form_submit_button("Add Another Exercise"):
             st.session_state.exercises.append({'name': '', 'sets': 3, 'reps': 10, 'weight': 20.0})
             st.experimental_rerun()

        submitted = cols_buttons[1].form_submit_button("Log Workout", type="primary")

        if submitted:
            # Filter out empty exercises before logging
            valid_exercises = [ex for ex in st.session_state.exercises if ex['name'].strip() != ""]
            if valid_exercises:
                be.log_workout(CURRENT_USER_ID, workout_date, duration, calories, valid_exercises)
                st.success("Workout logged successfully!")
                # Clear exercises from state after logging
                del st.session_state.exercises
            else:
                st.error("Please add at least one exercise with a name.")

def view_history():
    st.header("📈 My Workout History")
    workouts = be.get_user_workouts(CURRENT_USER_ID)
    if not workouts:
        st.info("No workouts logged yet. Go log one!")
        return

    df_workouts = pd.DataFrame(workouts, columns=['ID', 'Date', 'Duration (min)', 'Calories Burned'])
    df_workouts['Date'] = pd.to_datetime(df_workouts['Date'])
    
    st.subheader("Progress Over Time")
    st.line_chart(df_workouts.set_index('Date')['Duration (min)'])
    
    st.subheader("Workout Logs")
    for index, row in df_workouts.iterrows():
        with st.expander(f"{row['Date'].strftime('%Y-%m-%d')} - {row['Duration (min)']} minutes"):
            exercises = be.get_workout_details(row['ID'])
            df_exercises = pd.DataFrame(exercises, columns=['Exercise', 'Sets', 'Reps', 'Weight (kg)'])
            st.table(df_exercises)

def set_goals():
    st.header("🎯 Set & View Goals")
    
    with st.form("goal_form"):
        st.subheader("Set a New Goal")
        description = st.text_area("Goal Description (e.g., 'Workout 5 times a week')")
        target_value = st.number_input("Target Value (optional)", min_value=0)
        cols = st.columns(2)
        start_date = cols[0].date_input("Start Date", date.today())
        end_date = cols[1].date_input("End Date", date.today() + timedelta(days=30))

        submitted = st.form_submit_button("Set Goal")
        if submitted:
            be.set_goal(CURRENT_USER_ID, description, target_value, start_date, end_date)
            st.success("Goal set!")

    st.markdown("---")
    st.subheader("Active Goals")
    goals = be.get_user_goals(CURRENT_USER_ID)
    if goals:
        df_goals = pd.DataFrame(goals, columns=['ID', 'Description', 'Target', 'Start', 'End', 'Status'])
        st.table(df_goals[['Description', 'Target', 'Start', 'End', 'Status']])
    else:
        st.info("You have no active goals.")

def social_leaderboard():
    st.header("🏆 Friends & Leaderboard")
    
    tab1, tab2 = st.tabs(["Leaderboard", "Manage Friends"])

    with tab1:
        st.subheader("This Week's Leaderboard")
        st.caption("Ranking based on total workout minutes this week.")
        leaderboard_data = be.get_weekly_leaderboard(CURRENT_USER_ID)
        if leaderboard_data:
            df_leaderboard = pd.DataFrame(leaderboard_data, columns=['Name', 'Total Minutes'])
            df_leaderboard.index = df_leaderboard.index + 1 # Rank
            st.dataframe(df_leaderboard, use_container_width=True)
        else:
            st.info("Not enough data for a leaderboard yet.")

    with tab2:
        st.subheader("My Friends")
        friends = be.get_user_friends(CURRENT_USER_ID)
        friend_ids = [f[0] for f in friends]

        if friends:
            for friend_id, friend_name in friends:
                cols = st.columns([4, 1])
                cols[0].write(friend_name)
                if cols[1].button("Remove", key=f"remove_{friend_id}"):
                    be.remove_friend(CURRENT_USER_ID, friend_id)
                    st.success(f"Removed {friend_name} from friends.")
                    st.experimental_rerun()
        else:
            st.info("You haven't added any friends yet.")

        st.markdown("---")
        st.subheader("Add a Friend")
        all_users = be.get_all_users()
        # Exclude self and current friends from the list of potential friends
        potential_friends = [u for u in all_users if u[0] != CURRENT_USER_ID and u[0] not in friend_ids]
        
        if potential_friends:
            selected_user_id = st.selectbox("Select a user to add", options=potential_friends, format_func=lambda x: x[1])
            if st.button("Add Friend"):
                be.add_friend(CURRENT_USER_ID, selected_user_id[0])
                st.success(f"Added {selected_user_id[1]} as a friend!")
                st.experimental_rerun()
        else:
            st.write("No other users to add.")

def show_fitness_insights():
    st.header("📊 Fitness Insights")
    st.subheader(f"Your Personal Fitness Dashboard")

    stats = be.get_user_dashboard_stats(CURRENT_USER_ID)
    workouts = be.get_user_workouts(CURRENT_USER_ID)

    if not stats or stats.get('total_workouts', 0) == 0:
        st.warning("Log a workout to see your insights!")
        return

    # Calculate weekly stats
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    
    workouts_this_week = [w for w in workouts if w[1] >= start_of_week]
    minutes_this_week = sum(w[2] for w in workouts_this_week)

    cols = st.columns(3)
    cols[0].metric(label="Workouts This Week", value=len(workouts_this_week))
    cols[1].metric(label="Total Minutes This Week", value=minutes_this_week)
    
    avg_duration = stats.get('avg_duration', 0)
    cols[2].metric(label="Average Workout Length", value=f"{avg_duration:.1f} min")

    st.markdown("---")
    st.subheader("Recent Activity")
    if workouts:
        latest_workout = workouts[0]
        st.write(f"Your last workout was on **{latest_workout[1].strftime('%B %d, %Y')}** for **{latest_workout[2]} minutes**.")
        
        with st.expander("View details of your last workout"):
            exercises = be.get_workout_details(latest_workout[0])
            if exercises:
                df_exercises = pd.DataFrame(exercises, columns=['Exercise', 'Sets', 'Reps', 'Weight (kg)'])
                st.table(df_exercises)
            else:
                st.write("No specific exercises were logged for this workout.")
    else:
        st.info("No recent workouts found.")


# --- Main App ---
def main():
    # Run setup on first load
    be.create_tables()
    be.seed_data()
    
    st.sidebar.title(f"Welcome, {get_current_user_name()}!")
    
    menu = {
        "📊 Fitness Insights": show_fitness_insights,
        "🏋️ Log Workout": log_workout,
        "📈 My History": view_history,
        "🏆 Friends & Leaderboard": social_leaderboard,
        "🎯 Goals": set_goals,
        "👤 My Profile": show_profile,
    }

    choice = st.sidebar.radio("Navigation", list(menu.keys()))
    
    # Call the selected page function
    menu[choice]()

if __name__ == '__main__':
    main()
