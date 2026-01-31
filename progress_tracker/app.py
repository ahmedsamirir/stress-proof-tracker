import os
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime

st.set_page_config(page_title="Stress-Proof Tracker", layout="centered")

# Paths relative to this app file (works when deployed or run from any folder)
_BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(_BASE, "data.csv")
BOOKS_FILE = os.path.join(_BASE, "books.csv")
ENTERTAINMENT_FILE = os.path.join(_BASE, "entertainment.csv")

DEFAULT_DATA_COLUMNS = [
    "date", "work", "work_minutes", "gym", "gym_minutes", "learning", "learning_minutes",
    "learning_type", "reading", "reading_book", "reading_minutes",
    "entertainment", "entertainment_item", "entertainment_minutes",
    "mood", "notes"
]


def load_data():
    try:
        df = pd.read_csv(DATA_FILE)
    except Exception:
        df = pd.DataFrame(columns=DEFAULT_DATA_COLUMNS)
    for col in DEFAULT_DATA_COLUMNS:
        if col not in df.columns:
            df[col] = 0 if "minutes" in col or col in ["work", "gym", "learning", "reading", "entertainment"] else ""
    return df


def load_books():
    try:
        return pd.read_csv(BOOKS_FILE)
    except Exception:
        return pd.DataFrame(columns=["title", "finished"])


def load_entertainment():
    try:
        return pd.read_csv(ENTERTAINMENT_FILE)
    except Exception:
        return pd.DataFrame(columns=["title", "item_type", "finished"])


def save_books(books_df):
    books_df.to_csv(BOOKS_FILE, index=False)


def save_entertainment(ent_df):
    ent_df.to_csv(ENTERTAINMENT_FILE, index=False)


df = load_data()
books_df = load_books()
ent_df = load_entertainment()

st.title("📊 Stress-Proof Workday Tracker")

# Today's date — unique display
today_obj = date.today()
weekday = today_obj.strftime("%A")
day_num = today_obj.strftime("%d")
month_short = today_obj.strftime("%b")
year = today_obj.strftime("%Y")
st.markdown(
    f"""
    <div style="
        text-align: center;
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin: 0.5rem 0 1.5rem 0;
        font-family: system-ui, sans-serif;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    ">
        <span style="font-size: 0.85rem; opacity: 0.9; letter-spacing: 0.05em;">{weekday}</span>
        <br>
        <span style="font-size: 2rem; font-weight: 700; line-height: 1.2;">{day_num}</span>
        <span style="font-size: 1.25rem; font-weight: 500; opacity: 0.95;"> {month_short}</span>
        <span style="font-size: 1rem; opacity: 0.85;"> {year}</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# -------- Manage lists (above form so lists are ready when submitting) --------
with st.expander("📚 Manage books", expanded=False):
    add_book = st.text_input("Add a book to your list", key="add_book")
    if st.button("Add book"):
        if add_book and add_book.strip():
            if books_df.empty or "title" not in books_df.columns:
                books_df = pd.DataFrame({"title": [add_book.strip()], "finished": [0]})
            else:
                books_df = pd.concat([books_df, pd.DataFrame({"title": [add_book.strip()], "finished": [0]})], ignore_index=True)
            save_books(books_df)
            st.success(f"Added: {add_book.strip()}")
            st.rerun()
    st.caption("Mark as finished:")
    unfinished_books = books_df[books_df["finished"] == 0]["title"].tolist() if not books_df.empty and "finished" in books_df.columns else []
    if unfinished_books:
        mark_book = st.selectbox("Select book", unfinished_books, key="mark_book_done")
        if st.button("Mark book as finished"):
            books_df.loc[books_df["title"] == mark_book, "finished"] = 1
            save_books(books_df)
            st.success(f"Finished: {mark_book}")
            st.rerun()
    else:
        st.info("No books in progress. Add a book above.")

with st.expander("🎬 Manage watchlist", expanded=False):
    add_item = st.text_input("Add a movie or series", key="add_ent")
    item_type = st.radio("Type", ["Movie", "Series"], key="ent_type")
    if st.button("Add to watchlist"):
        if add_item and add_item.strip():
            if ent_df.empty or "title" not in ent_df.columns:
                ent_df = pd.DataFrame({"title": [add_item.strip()], "item_type": [item_type], "finished": [0]})
            else:
                ent_df = pd.concat([ent_df, pd.DataFrame({"title": [add_item.strip()], "item_type": [item_type], "finished": [0]})], ignore_index=True)
            save_entertainment(ent_df)
            st.success(f"Added: {add_item.strip()}")
            st.rerun()
    st.caption("Mark as finished:")
    unfinished_ent = ent_df[ent_df["finished"] == 0]["title"].tolist() if not ent_df.empty and "finished" in ent_df.columns else []
    if unfinished_ent:
        mark_ent = st.selectbox("Select item", unfinished_ent, key="mark_ent_done")
        if st.button("Mark as finished"):
            ent_df.loc[ent_df["title"] == mark_ent, "finished"] = 1
            save_entertainment(ent_df)
            st.success(f"Finished: {mark_ent}")
            st.rerun()
    else:
        st.info("No items in progress. Add something above.")

# -------- Daily Check-in --------
st.subheader("Daily Check-in")

with st.form("checkin_form"):
    today = str(date.today())

    work = st.checkbox("Worked (Al-Dawaa)")
    work_minutes = st.number_input("Work (minutes)", 0, 600, 0, 15, key="work_m")

    gym = st.checkbox("Gym")
    gym_minutes = st.number_input("Gym (minutes)", 0, 300, 0, 15, key="gym_m")

    learning = st.checkbox("Learning Block")
    learning_minutes = st.number_input("Learning (minutes)", 0, 600, 0, 15, key="learn_m")
    learning_type = st.selectbox(
        "Learning Type",
        ["None", "German A1.3", "Data Science / Software"]
    )

    st.divider()
    reading = st.checkbox("Reading")
    book_options = ["— Select book —"] + (books_df[books_df["finished"] == 0]["title"].tolist() if not books_df.empty and "finished" in books_df.columns else [])
    if not book_options:
        book_options = ["— No books in list —"]
    reading_book = st.selectbox("What did you read?", book_options, key="reading_book")
    reading_minutes = st.number_input("Reading (minutes)", 0, 300, 0, 15, key="reading_m")

    st.divider()
    entertainment = st.checkbox("Entertainment (movie/series)")
    ent_options = ["— Select —"] + (ent_df[ent_df["finished"] == 0]["title"].tolist() if not ent_df.empty and "finished" in ent_df.columns else [])
    if not ent_options:
        ent_options = ["— Nothing in watchlist —"]
    entertainment_item = st.selectbox("What did you watch?", ent_options, key="ent_item")
    entertainment_minutes = st.number_input("Entertainment (minutes)", 0, 300, 0, 15, key="ent_m")

    st.divider()
    mood = st.slider("Mood", 1, 5, 3)
    notes = st.text_input("Notes (optional)")

    submitted = st.form_submit_button("Save Today")

    if submitted:
        new_row = {
            "date": today,
            "work": int(work),
            "work_minutes": work_minutes,
            "gym": int(gym),
            "gym_minutes": gym_minutes,
            "learning": int(learning),
            "learning_minutes": learning_minutes,
            "learning_type": learning_type,
            "reading": int(reading),
            "reading_book": reading_book if reading_book and not reading_book.startswith("—") else "",
            "reading_minutes": reading_minutes,
            "entertainment": int(entertainment),
            "entertainment_item": entertainment_item if entertainment_item and not entertainment_item.startswith("—") else "",
            "entertainment_minutes": entertainment_minutes,
            "mood": mood,
            "notes": notes or "",
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df = df[DEFAULT_DATA_COLUMNS]
        df.to_csv(DATA_FILE, index=False)
        st.success("Saved ✔")

# -------- Charts --------
st.subheader("Progress Overview")

if not df.empty:
    df["date"] = pd.to_datetime(df["date"])
    last_7 = df.tail(7)

    tasks = ["Work", "Gym", "Learning", "Reading", "Entertainment"]
    completed = [
        last_7["work"].mean() * 100,
        last_7["gym"].mean() * 100,
        last_7["learning"].mean() * 100,
        last_7["reading"].mean() * 100,
        last_7["entertainment"].mean() * 100,
    ]
    completion = pd.DataFrame({"Task": tasks, "Completed": completed})

    fig1 = px.bar(
        completion,
        x="Task",
        y="Completed",
        title="Last 7 Days Completion (%)",
        range_y=[0, 100],
    )
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.line(
        df.tail(14),
        x="date",
        y="mood",
        title="Mood Trend (14 Days)",
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Time spent per task (last 7 days)
    time_cols = ["work_minutes", "gym_minutes", "learning_minutes", "reading_minutes", "entertainment_minutes"]
    for c in time_cols:
        if c not in last_7.columns:
            last_7 = last_7.copy()
            last_7[c] = 0
    time_totals = last_7[time_cols].sum()
    time_df = pd.DataFrame({
        "Task": ["Work", "Gym", "Learning", "Reading", "Entertainment"],
        "Minutes": time_totals.values,
    })
    fig_time = px.bar(time_df, x="Task", y="Minutes", title="Time spent (last 7 days, minutes)")
    st.plotly_chart(fig_time, use_container_width=True)

    learning_dist = df[df["learning"] == 1]["learning_type"].value_counts()
    if len(learning_dist) > 0:
        fig3 = px.pie(
            values=learning_dist.values,
            names=learning_dist.index,
            title="Learning Distribution",
        )
        st.plotly_chart(fig3, use_container_width=True)

    if df["reading"].sum() > 0 and "reading_book" in df.columns:
        reading_dist = df.loc[(df["reading"] == 1) & (df["reading_book"] != ""), "reading_book"].value_counts()
        if len(reading_dist) > 0:
            fig4 = px.pie(
                values=reading_dist.values,
                names=reading_dist.index,
                title="Reading distribution",
            )
            st.plotly_chart(fig4, use_container_width=True)

    if df["entertainment"].sum() > 0 and "entertainment_item" in df.columns:
        ent_dist = df.loc[(df["entertainment"] == 1) & (df["entertainment_item"] != ""), "entertainment_item"].value_counts()
        if len(ent_dist) > 0:
            fig5 = px.pie(
                values=ent_dist.values,
                names=ent_dist.index,
                title="Entertainment (what you watched)",
            )
            st.plotly_chart(fig5, use_container_width=True)
else:
    st.info("No data yet. Start with today.")
