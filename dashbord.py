import streamlit as st
import sqlite3
import pandas as pd
import os

# ---------- DB CONNECTION ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "attendance.db")

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Attendance Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Face Authentication Attendance Dashboard")

conn = get_connection()

# ---------- SIDEBAR ----------
st.sidebar.header("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Students", "Attendance Records", "Overall Summary"]
)

# ---------- STUDENTS PAGE ----------
if page == "Students":
    st.subheader("👥 Registered Students")

    students_df = pd.read_sql_query(
        "SELECT reg_no, name FROM students",
        conn
    )

    if students_df.empty:
        st.warning("No students enrolled yet.")
    else:
        st.dataframe(students_df, use_container_width=True)

# ---------- ATTENDANCE RECORDS ----------
elif page == "Attendance Records":
    st.subheader("🕒 Attendance Logs (IN / OUT)")

    attendance_df = pd.read_sql_query(
        """
        SELECT reg_no, name, date, in_time, out_time
        FROM attendance
        ORDER BY date DESC
        """,
        conn
    )

    if attendance_df.empty:
        st.warning("No attendance records found.")
    else:
        st.dataframe(attendance_df, use_container_width=True)

# ---------- OVERALL SUMMARY ----------
elif page == "Overall Summary":
    st.subheader("📈 Overall Attendance Summary")

    summary_df = pd.read_sql_query(
        """
        SELECT 
            reg_no,
            name,
            COUNT(date) AS total_days,
            SUM(CASE WHEN in_time IS NOT NULL THEN 1 ELSE 0 END) AS present_days
        FROM attendance
        GROUP BY reg_no, name
        """,
        conn
    )

    if summary_df.empty:
        st.warning("No attendance data available.")
    else:
        summary_df["attendance_percentage"] = (
            summary_df["present_days"] / summary_df["total_days"] * 100
        ).round(2)

        st.dataframe(summary_df, use_container_width=True)

        st.subheader("📊 Attendance Percentage Chart")
        st.bar_chart(
            summary_df.set_index("name")["attendance_percentage"]
        )

conn.close()
