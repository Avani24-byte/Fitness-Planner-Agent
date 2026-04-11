import streamlit as st
import os
from datetime import datetime
import pandas as pd

from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun


# ------------------ CONFIG ------------------

st.set_page_config(page_title="AI Fitness Planner", page_icon="💪", layout="wide")

st.markdown("""
<style>
/* Buttons */
.stButton>button {
    border-radius: 10px;
    height: 50px;
    font-size: 16px;
}

/* 🔥 Sidebar width */
section[data-testid="stSidebar"] {
    width: 350px !important;
}
</style>
""", unsafe_allow_html=True)

# ------------------ LLM SETUP ------------------
from dotenv import load_dotenv
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY") or st.secrets["GROQ_API_KEY"]

llm = ChatGroq(
    groq_api_key=groq_api_key,
    model_name="llama-3.1-8b-instant"
)

# ------------------ TOOLS ------------------

search = DuckDuckGoSearchRun()

def workout_tool(user_input):
    prompt = f"""
    Create a highly detailed 7-day workout plan.

    User Details:
    {user_input}

    Requirements:
    - Day-wise schedule
    - Time table (morning/evening)
    - Exercises with sets, reps, rest
    - Warm-up and cool-down
    - Tips for each day

    Format properly.
    """
    return llm.invoke(prompt).content

def diet_tool(user_input):
    prompt = f"""
    Create a detailed Indian diet plan.

    User Details:
    {user_input}

    Requirements:
    - Full day timetable
    - Breakfast, lunch, dinner, snacks
    - Calories (approx)
    - Protein-rich suggestions
    - Hydration tips

    Format clearly.
    """
    return llm.invoke(prompt).content

def tutorial_tool(query):
    return search.run(f"{query} exercise tutorial video")


# ------------------ SESSION STATE ------------------

if "history" not in st.session_state:
    st.session_state.history = []

if "progress" not in st.session_state:
    st.session_state.progress = []

# ------------------ UI HEADER ------------------

st.title("💪 AI Fitness & Workout Planner")
st.markdown("### Your Smart Fitness Coach 🧠")

# ------------------ USER INPUT ------------------

col1, col2, col3 = st.columns(3)
with col1:
    age = st.number_input("Age", min_value=10, max_value=80, value=None, placeholder="Enter age")
    weight = st.number_input("Weight (kg)", min_value=30.0, max_value=150.0, value=None, placeholder="Enter weight")
    height = st.number_input("Height (cm)", min_value=120, max_value=220, value=None, placeholder="Enter height")
    gender = st.selectbox("Gender", ["Select", "Male", "Female"])

with col2:
    goal = st.selectbox("Goal", ["Weight Loss", "Muscle Gain", "Maintenance"])
    level = st.selectbox("Fitness Level", ["Beginner", "Intermediate", "Advanced"])

with col3:
    equipment = st.selectbox("Equipment", ["Home", "Gym", "None"])

if age and weight and height and gender != "Select":
    user_input = f"""
    Age: {age}
    Weight: {weight}
    Height: {height} cm
    Gender: {gender}
    Goal: {goal}
    Level: {level}
    Equipment: {equipment}
    """
else:
    user_input = None
#--------------------BMI CALCULATION------------------
st.markdown("### 📊 Body Metrics")

if weight and height:
    bmi = weight / ((height / 100) ** 2)

    colA, colB = st.columns(2)

    with colA:
        st.metric("BMI", f"{bmi:.2f}")

    with colB:
        if bmi < 18.5:
            st.info("Underweight")
        elif bmi < 24.9:
            st.success("Normal")
        elif bmi < 29.9:
            st.warning("Overweight")
        else:
            st.error("Obese")
else:
    st.info("Enter weight & height to calculate BMI")

# ------------------ TABS ------------------

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["🏋️ Workout", "🥗 Diet", "🎥 Tutorials", "📊 History", "📈 Progress Tracker"]
)

# ------------------ WORKOUT ------------------

with tab1:
    if st.button("Generate Workout Plan 💪"):
        with st.spinner("Creating your workout plan..."):

            prompt = f"""
You are a professional fitness coach.

Create a HIGHLY PERSONALIZED 7-day workout plan.

User Details:
{user_input}

STRICT INSTRUCTIONS:
- Day-wise timetable (Morning/Evening)
- Warm-up, workout, rest, cool-down
- Sets, reps, rest time
- Daily tips

Make it structured and practical.
"""

            result = llm.invoke(prompt).content

            st.success("Done!")
            st.markdown(result)

            # ✅ SAVE HISTORY
            st.session_state.history.append({
                "type": "Workout",
                "data": result,
                "time": datetime.now()
            })

# ------------------ DIET ------------------

with tab2:
    if st.button("Generate Diet Plan 🥗"):
        with st.spinner("Preparing diet plan..."):

            prompt = f"""
You are a certified nutritionist.

Create a PERSONALIZED Indian diet plan.

User Details:
{user_input}

Include:
- Full day timetable with timings
- Meals + snacks
- Calories (approx)
- Protein focus
- Hydration tips
"""

            result = llm.invoke(prompt).content

            st.success("Done!")
            st.markdown(result)

            # ✅ SAVE HISTORY
            st.session_state.history.append({
                "type": "Diet",
                "data": result,
                "time": datetime.now()
            })
# ------------------ TUTORIALS ------------------

with tab3:
    exercise_name = st.text_input("Enter exercise (e.g., push-ups)")

    if st.button("Search Tutorials 🎥"):
        if exercise_name:
            with st.spinner("Searching tutorials..."):
                import re

                query = f"{exercise_name} workout tutorial site:youtube.com"
                results = search.run(query)

                st.markdown("### 🎥 Watch Tutorials")

                links = re.findall(r'(https?://[^\s]+)', results)

                if links:
                    for link in links[:5]:
                        st.markdown(f"▶️ [Watch Video]({link})")
                else:
                    st.write(results)

# ------------------ HISTORY ------------------

with tab4:
    st.subheader("📊 Your Activity History")

    if st.session_state.history:
        for item in reversed(st.session_state.history):
            st.markdown(f"**{item['type']}** ({item['time'].strftime('%H:%M:%S')})")
            st.write(item["data"])
            st.markdown("---")
    else:
        st.info("No history yet. Start generating plans!")

# ------------------ PROGRESS TRACKER ------------------

with tab5:
    st.subheader("📈 Track Your Progress")

    date = st.date_input("Select Date")
    weight_today = st.number_input("Enter today's weight", 30.0, 150.0)

    if st.button("Save Progress"):
        st.session_state.progress.append({
            "date": date,
            "weight": weight_today
        })
        st.success("Progress saved!")

    if st.session_state.progress:
        df = pd.DataFrame(st.session_state.progress)
        df = df.sort_values("date")

        st.line_chart(df.set_index("date"))
    else:
        st.info("No progress data yet.")

# ------------------ SIDEBAR ------------------

st.sidebar.title("⚙️ Settings")

if st.sidebar.button("Clear History"):
    st.session_state.history = []
    st.sidebar.success("History cleared!")

if st.sidebar.button("Clear Progress"):
    st.session_state.progress = []
    st.sidebar.success("Progress cleared!")

st.sidebar.markdown("### About")
st.sidebar.info("AI Fitness Planner using LangChain + Groq 🚀")
st.sidebar.markdown("### 📜 Recent Activity")

if st.session_state.history:
    for item in reversed(st.session_state.history[-5:]):
        st.sidebar.markdown(f"**{item['type']}**")
        st.sidebar.caption(item['time'].strftime('%H:%M'))
else:
    st.sidebar.info("No activity yet")

    st.sidebar.markdown("## 🤖 AI Fitness Coach")

if "chat_history_sidebar" not in st.session_state:
    st.session_state.chat_history_sidebar = []

user_msg = st.sidebar.text_input("Ask me anything 💬")

if st.sidebar.button("Send"):
    if user_msg:
        with st.spinner("Thinking..."):
            response = llm.invoke(f"You are a professional fitness coach. Answer clearly:\n{user_msg}").content

            # Save chat
            st.session_state.chat_history_sidebar.append(("You", user_msg))
            st.session_state.chat_history_sidebar.append(("Coach", response))

# Show chat history
for role, msg in st.session_state.chat_history_sidebar:
    if role == "You":
        st.sidebar.markdown(f"**🧑 You:** {msg}")
    else:
        st.sidebar.markdown(f"**🤖 Coach:** {msg}")