import os
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime

st.set_page_config(page_title="Stress-Proof Tracker", layout="centered", initial_sidebar_state="collapsed")

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


def _use_sheets():
    try:
        return ("gcp_service_account" in st.secrets or "gcp_service_account_json" in st.secrets) and "sheet_id" in st.secrets
    except Exception:
        return False


def _get_sheet_client():
    if not _use_sheets():
        return None
    try:
        import gspread
        import json
        if "gcp_service_account_json" in st.secrets:
            creds = json.loads(st.secrets["gcp_service_account_json"])
        else:
            creds = dict(st.secrets["gcp_service_account"])
        gc = gspread.service_account_from_dict(creds)
        return gc.open_by_key(st.secrets["sheet_id"])
    except Exception:
        return None


def load_data():
    sh = _get_sheet_client()
    if sh:
        try:
            ws = sh.worksheet("data")
            rows = ws.get_all_records()
            if not rows:
                df = pd.DataFrame(columns=DEFAULT_DATA_COLUMNS)
            else:
                df = pd.DataFrame(rows)
        except Exception:
            try:
                sh.add_worksheet(title="data", rows=1000, cols=20)
                ws = sh.worksheet("data")
                ws.append_row(DEFAULT_DATA_COLUMNS)
                df = pd.DataFrame(columns=DEFAULT_DATA_COLUMNS)
            except Exception:
                df = pd.DataFrame(columns=DEFAULT_DATA_COLUMNS)
    else:
        try:
            df = pd.read_csv(DATA_FILE)
        except Exception:
            df = pd.DataFrame(columns=DEFAULT_DATA_COLUMNS)
    for col in DEFAULT_DATA_COLUMNS:
        if col not in df.columns:
            df[col] = 0 if "minutes" in col or col in ["work", "gym", "learning", "reading", "entertainment"] else ""
    return df


def save_data(df):
    df = df[DEFAULT_DATA_COLUMNS]
    sh = _get_sheet_client()
    if sh:
        try:
            ws = sh.worksheet("data")
            ws.clear()
            ws.append_row(list(df.columns))
            for _, row in df.iterrows():
                ws.append_row([row[c] for c in df.columns])
        except Exception:
            pass
    df.to_csv(DATA_FILE, index=False)


def load_books():
    sh = _get_sheet_client()
    if sh:
        try:
            ws = sh.worksheet("books")
            rows = ws.get_all_records()
            if not rows:
                return pd.DataFrame(columns=["title", "finished"])
            return pd.DataFrame(rows)
        except Exception:
            try:
                ws = sh.add_worksheet(title="books", rows=200, cols=5)
                ws.append_row(["title", "finished"])
                return pd.DataFrame(columns=["title", "finished"])
            except Exception:
                return pd.DataFrame(columns=["title", "finished"])
    try:
        return pd.read_csv(BOOKS_FILE)
    except Exception:
        return pd.DataFrame(columns=["title", "finished"])


def save_books(books_df):
    sh = _get_sheet_client()
    if sh:
        try:
            ws = sh.worksheet("books")
            ws.clear()
            ws.append_row(["title", "finished"])
            for _, row in books_df.iterrows():
                ws.append_row([str(row["title"]), int(row["finished"])])
        except Exception:
            pass
    books_df.to_csv(BOOKS_FILE, index=False)


def load_entertainment():
    sh = _get_sheet_client()
    if sh:
        try:
            ws = sh.worksheet("entertainment")
            rows = ws.get_all_records()
            if not rows:
                return pd.DataFrame(columns=["title", "item_type", "finished"])
            return pd.DataFrame(rows)
        except Exception:
            try:
                ws = sh.add_worksheet(title="entertainment", rows=200, cols=5)
                ws.append_row(["title", "item_type", "finished"])
                return pd.DataFrame(columns=["title", "item_type", "finished"])
            except Exception:
                return pd.DataFrame(columns=["title", "item_type", "finished"])
    try:
        return pd.read_csv(ENTERTAINMENT_FILE)
    except Exception:
        return pd.DataFrame(columns=["title", "item_type", "finished"])


def save_entertainment(ent_df):
    sh = _get_sheet_client()
    if sh:
        try:
            ws = sh.worksheet("entertainment")
            ws.clear()
            ws.append_row(["title", "item_type", "finished"])
            for _, row in ent_df.iterrows():
                ws.append_row([str(row["title"]), str(row["item_type"]), int(row["finished"])])
        except Exception:
            pass
    ent_df.to_csv(ENTERTAINMENT_FILE, index=False)


df = load_data()
books_df = load_books()
ent_df = load_entertainment()

# -------- Electric / AI theme CSS --------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Space+Grotesk:wght@400;500;600;700&display=swap');
    .stApp { background: linear-gradient(180deg, #0a0e17 0%, #0f1629 35%, #0d1322 100%); }
    .main .block-container { padding-top: 1.5rem; max-width: 720px; }
    h1, h2, h3 { font-family: 'Space Grotesk', sans-serif !important; color: #e0e7ff !important; }
    .electric-date {
        text-align: center;
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 40%, #3730a3 100%);
        color: #fff;
        padding: 1.25rem 1.5rem;
        border-radius: 16px;
        margin: 0.5rem 0 1.25rem 0;
        font-family: 'Space Grotesk', sans-serif;
        box-shadow: 0 0 24px rgba(99, 102, 241, 0.25), 0 4px 12px rgba(0,0,0,0.3);
        border: 1px solid rgba(129, 140, 248, 0.2);
    }
    .electric-date .day-num { font-size: 2.25rem; font-weight: 700; color: #a5b4fc; }
    .electric-date .weekday { font-size: 0.8rem; letter-spacing: 0.15em; opacity: 0.9; color: #c7d2fe; }
    .ai-insight-card {
        background: linear-gradient(135deg, rgba(30, 27, 75, 0.6) 0%, rgba(49, 46, 129, 0.4) 100%);
        border: 1px solid rgba(129, 140, 248, 0.25);
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin: 0.75rem 0;
        font-family: 'Space Grotesk', sans-serif;
        color: #c7d2fe;
        box-shadow: 0 4px 16px rgba(0,0,0,0.2);
    }
    .ai-insight-card .label { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: #818cf8; margin-bottom: 0.25rem; }
    .digest-header { font-family: 'Space Grotesk', sans-serif; color: #a5b4fc; }
    .digest-item { padding: 0.5rem 0; border-bottom: 1px solid rgba(129, 140, 248, 0.15); }
    .digest-item a { color: #818cf8; text-decoration: none; }
    .digest-item a:hover { color: #a5b4fc; text-decoration: underline; }
    div[data-testid="stExpander"] { border: 1px solid rgba(129, 140, 248, 0.2); border-radius: 12px; }
    .stForm { border: 1px solid rgba(129, 140, 248, 0.15); border-radius: 12px; padding: 1rem; }
</style>
""", unsafe_allow_html=True)

st.title("📊 Stress-Proof Workday Tracker")

# Today's date — electric display
today_obj = date.today()
weekday = today_obj.strftime("%A")
day_num = today_obj.strftime("%d")
month_short = today_obj.strftime("%b")
year = today_obj.strftime("%Y")
st.markdown(
    f"""
    <div class="electric-date">
        <span class="weekday">{weekday}</span><br>
        <span class="day-num">{day_num}</span>
        <span style="font-size: 1.2rem; font-weight: 500;"> {month_short}</span>
        <span style="font-size: 0.95rem; opacity: 0.9;"> {year}</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# -------- Tech & AI daily digest (pop-up style) --------
@st.cache_data(ttl=3600)
def fetch_tech_digest():
    try:
        import feedparser
        entries = []
        feeds = [
            ("https://techcrunch.com/feed/", "TechCrunch"),
            ("https://venturebeat.com/feed/", "VentureBeat"),
            ("https://www.theverge.com/rss/index.xml", "The Verge"),
        ]
        for url, source in feeds:
            try:
                feed = feedparser.parse(url)
                for e in feed.entries[:4]:
                    entries.append({
                        "title": e.get("title", "")[:80] + ("..." if len(e.get("title", "")) > 80 else ""),
                        "link": e.get("link", "#"),
                        "source": source,
                        "published": e.get("published", "")[:10] if e.get("published") else "",
                    })
            except Exception:
                continue
        entries.sort(key=lambda x: x["published"] or "", reverse=True)
        return entries[:12]
    except Exception:
        return []

digest_entries = fetch_tech_digest()
with st.expander("⚡ Today's Tech & AI digest — stay updated", expanded=True):
    st.caption("Headlines from tech and AI sources. Refreshes hourly.")
    if digest_entries:
        for e in digest_entries:
            st.markdown(
                f'<div class="digest-item">'
                f'<a href="{e["link"]}" target="_blank" rel="noopener">{e["title"]}</a> '
                f'<span style="color:#6366f1;font-size:0.75rem;">[{e["source"]}]</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
    else:
        st.info("Could not load digest. Check connection or try again later.")

# -------- AI-powered insights (from your data) --------
if not df.empty and len(df) > 0:
    df_temp = df.copy()
    if "date" in df_temp.columns:
        df_temp["date"] = pd.to_datetime(df_temp["date"], errors="coerce")
    last_7 = df_temp.tail(7)
    insights = []
    if "work" in last_7.columns:
        w = last_7["work"].sum()
        if w >= 5:
            insights.append("Strong work week — 5+ days logged.")
        elif w >= 3:
            insights.append("Solid work days this week. Keep the rhythm.")
    if "gym" in last_7.columns:
        g = last_7["gym"].sum()
        if g >= 3:
            insights.append("Gym streak: 3+ days. You're on fire.")
        elif g == 0 and len(last_7) >= 3:
            insights.append("No gym yet this week — one session can start the habit.")
    if "learning" in last_7.columns:
        lr = last_7["learning"].sum()
        if lr >= 4:
            insights.append("Learning consistency is high. Great for long-term growth.")
    if "mood" in last_7.columns:
        avg_mood = last_7["mood"].mean()
        if avg_mood >= 4:
            insights.append("Mood trend is up. Nice.")
        elif avg_mood <= 2.5 and len(last_7) >= 5:
            insights.append("Mood has been lower — small wins (one task, one walk) help.")
    if insights:
        st.markdown('<p class="ai-insight-card"><span class="label">AI insights</span><br>' + " ".join(insights[:3]) + "</p>", unsafe_allow_html=True)

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

    work = st.checkbox("Full-Time Work")
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
        save_data(df)
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

    _layout = dict(
        paper_bgcolor="rgba(10, 14, 23, 0.9)",
        plot_bgcolor="rgba(15, 22, 41, 0.6)",
        font=dict(color="#c7d2fe", size=12),
        title_font=dict(color="#a5b4fc"),
        xaxis=dict(gridcolor="rgba(99, 102, 241, 0.15)"),
        yaxis=dict(gridcolor="rgba(99, 102, 241, 0.15)"),
        margin=dict(t=50, b=40, l=50, r=30),
    )
    _bar_colors = ["#6366f1", "#818cf8", "#a5b4fc", "#818cf8", "#6366f1"]

    fig1 = px.bar(
        completion,
        x="Task",
        y="Completed",
        title="Last 7 Days Completion (%)",
        range_y=[0, 100],
        color_discrete_sequence=_bar_colors,
    )
    fig1.update_layout(**_layout)
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.line(
        df.tail(14),
        x="date",
        y="mood",
        title="Mood Trend (14 Days)",
        color_discrete_sequence=["#818cf8"],
    )
    fig2.update_layout(**_layout)
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
    fig_time = px.bar(time_df, x="Task", y="Minutes", title="Time spent (last 7 days, minutes)", color_discrete_sequence=_bar_colors)
    fig_time.update_layout(**_layout)
    st.plotly_chart(fig_time, use_container_width=True)

    learning_dist = df[df["learning"] == 1]["learning_type"].value_counts()
    if len(learning_dist) > 0:
        fig3 = px.pie(
            values=learning_dist.values,
            names=learning_dist.index,
            title="Learning Distribution",
            color_discrete_sequence=["#6366f1", "#818cf8", "#a5b4fc", "#c7d2fe"],
        )
        fig3.update_layout(**_layout)
        st.plotly_chart(fig3, use_container_width=True)

    if df["reading"].sum() > 0 and "reading_book" in df.columns:
        reading_dist = df.loc[(df["reading"] == 1) & (df["reading_book"] != ""), "reading_book"].value_counts()
        if len(reading_dist) > 0:
            fig4 = px.pie(
                values=reading_dist.values,
                names=reading_dist.index,
                title="Reading distribution",
                color_discrete_sequence=px.colors.sequential.Indigo_r,
            )
            fig4.update_layout(**_layout)
            st.plotly_chart(fig4, use_container_width=True)

    if df["entertainment"].sum() > 0 and "entertainment_item" in df.columns:
        ent_dist = df.loc[(df["entertainment"] == 1) & (df["entertainment_item"] != ""), "entertainment_item"].value_counts()
        if len(ent_dist) > 0:
            fig5 = px.pie(
                values=ent_dist.values,
                names=ent_dist.index,
                title="Entertainment (what you watched)",
                color_discrete_sequence=px.colors.sequential.Indigo_r,
            )
            fig5.update_layout(**_layout)
            st.plotly_chart(fig5, use_container_width=True)
else:
    st.info("No data yet. Start with today.")

# -------- How to enable persistent storage (Google Sheets) --------
with st.expander("🔐 How to keep data after Streamlit reboots (Google Sheets)", expanded=False):
    st.markdown("""
    **Data is lost on reboot unless you use Google Sheets.**

    1. **Google Cloud:** [console.cloud.google.com](https://console.cloud.google.com) → Create project → APIs & Services → Enable **Google Sheets API**.
    2. **Service account:** APIs & Services → Credentials → Create credentials → Service account → Create key (JSON). Download the JSON file.
    3. **Google Sheet:** Create a new [Google Sheet](https://sheets.google.com). Copy the **Sheet ID** from the URL:  
       `https://docs.google.com/spreadsheets/d/**SHEET_ID**/edit`
    4. **Share the sheet:** Share the sheet with the **service account email** (from the JSON, e.g. `xxx@xxx.iam.gserviceaccount.com`) with **Editor** access.
    5. **Streamlit Cloud:** Your app → Settings → Secrets. Add (TOML):
       - `sheet_id = "your_sheet_id"`
       - Either paste the whole JSON as a string: `gcp_service_account_json = '''{"type":"service_account", ...}'''`  
         Or use nested keys: `[gcp_service_account]` then `type = "service_account"`, `project_id = "..."`, `private_key = "..."`, `client_email = "..."`, etc.
    6. Redeploy the app. Data will be stored in the sheet and survive reboots.
    """)
