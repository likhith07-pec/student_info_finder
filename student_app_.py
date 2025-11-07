import os
import sys
import subprocess
import webbrowser
import time
import streamlit as st
import pandas as pd
import numpy as np
import socket


def is_port_in_use(port: int) -> bool:
    """Check if the given port is already in use (Streamlit running)."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0

if __name__ == "__main__":
    port = 8501
    script = os.path.abspath(__file__)

    # Check if Streamlit is already running
    if not is_port_in_use(port):
        # Launch Streamlit with browser-disabling flags
        subprocess.Popen([
            "streamlit", "run", script, 
            "--server.port", str(port),
            "--browser.gatherUsageStats", "false",
            "--server.headless", "true"
        ], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(5)  # Wait longer for Streamlit server to start

        # Open browser only once
        webbrowser.open_new(f"http://localhost:{port}")
        sys.exit()





# --- Streamlit Page Config (must be first Streamlit command) ---
st.set_page_config(page_title="Student Info Finder", layout="wide", page_icon="🎓")

# --- Load Excel File ---
@st.cache_data
def load_data():
    df = pd.read_excel(r"Sample Copy.xlsx", skiprows=2, dtype=str)
    df = df.dropna(how='all').reset_index(drop=True)
    if len(df.columns) >= 12:
        df.columns = [
            'Sl_No', 'USN_LIBRARY', 'Course_Code', 'Student_Name',
            'BMATS201', 'BCHES202', 'BCEDK203', 'BESCK204A', 
            'BPLCK205B', 'BPWSK206', 'BICOK207', 'BSFHK258'
        ]
    df = df.fillna('').replace(['nan', 'NaN', 'None'], '')
    return df

def format_student_details(student):
    details = []
    details.append("🎓 STUDENT INFORMATION")
    details.append("=" * 50)
    details.append(f"👤 Student Name: {student['Student_Name']}")
    details.append(f"📚 USN: {student['USN_LIBRARY']}")
    details.append(f"🔢 Serial No: {student['Sl_No']}")
    details.append(f"📖 Course Code: {student['Course_Code']}")
    details.append("")
    details.append("📊 ACADEMIC PERFORMANCE")
    details.append("=" * 50)

    subjects = [
        ('BMATS201', 'Mathematics'),
        ('BCHES202', 'Chemistry'), 
        ('BCEDK203', 'Basic Electronics'),
        ('BESCK204A', 'Environmental Science'),
        ('BPLCK205B', 'Programming in C'),
        ('BPWSK206', 'Web Programming'),
        ('BICOK207', 'Indian Constitution'),
        ('BSFHK258', 'Soft Skills')
    ]

    total_marks = 0
    subjects_counted = 0
    for subject_code, subject_name in subjects:
        marks = str(student[subject_code])
        if marks.upper() == 'AB' or marks == '':
            details.append(f"  {subject_code} ({subject_name}): Absent")
        else:
            try:
                marks_int = int(float(marks))
                details.append(f"  {subject_code} ({subject_name}): {marks_int}/50")
                total_marks += marks_int
                subjects_counted += 1
            except (ValueError, TypeError):
                details.append(f"  {subject_code} ({subject_name}): N/A")

    details.append("")
    details.append("📈 PERFORMANCE SUMMARY")
    details.append("=" * 50)

    if subjects_counted > 0:
        avg = total_marks / subjects_counted
        perc = (total_marks / (subjects_counted * 50)) * 100
        details.append(f"Total Marks: {total_marks}/{subjects_counted * 50}")
        details.append(f"Average Marks: {avg:.1f}/50")
        details.append(f"Percentage: {perc:.1f}%")
    details.append("=" * 50)
    return "\n".join(details)

# --- Load Data ---
df = load_data()

# --- UI Styling (Dark Theme Like Your Screenshot) ---
st.markdown("""
<style>
body {background-color: #0E1117;}
[data-testid="stAppViewContainer"] {
    background-color: #0E1117;
    color: white;
}
h1, h2, h3, h4, h5, h6 {
    color: #8AB4F8;
}
.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

# --- App Title ---
st.title("🎓 Student Information Finder")

# --- Dataset Viewer ---
with st.expander("📘 View Full Dataset"):
    st.dataframe(df.astype(str), use_container_width=True)

# --- Search Section ---
st.subheader("🔍 Search Student")
search_option = st.radio("Search by:", ["Student Name", "USN"])
search_by = "Student_Name" if search_option == "Student Name" else "USN_LIBRARY"
search_value = st.text_input(f"Enter {search_option}")

if search_value:
    result = df[df[search_by].astype(str).str.lower() == search_value.lower()]

    if not result.empty:
        student = result.iloc[0]
        st.success("✅ Student Found")

        # --- Profile Card ---
        st.markdown("### 🧑‍🎓 Student Profile")
        col1, col2 = st.columns(2)
        col1.write(f"**Student Name:** {student['Student_Name']}")
        col1.write(f"**USN:** {student['USN_LIBRARY']}")
        col2.write(f"**Serial No:** {student['Sl_No']}")
        col2.write(f"**Course Code:** {student['Course_Code']}")

        # --- Academic Performance ---
        st.markdown("### 📚 Academic Performance")
        subjects = [
            ('BMATS201', 'Mathematics'),
            ('BCHES202', 'Chemistry'), 
            ('BCEDK203', 'Basic Electronics'),
            ('BESCK204A', 'Environmental Science'),
            ('BPLCK205B', 'Programming in C'),
            ('BPWSK206', 'Web Programming'),
            ('BICOK207', 'Indian Constitution'),
            ('BSFHK258', 'Soft Skills')
        ]
        cols = st.columns(4)
        total_marks, subjects_counted = 0, 0
        for i, (code, name) in enumerate(subjects):
            marks = str(student[code])
            if marks.upper() == 'AB' or marks == '':
                display_text = "Absent"
                color = "#FF6B6B"
            else:
                try:
                    marks_int = int(float(marks))
                    display_text = f"{marks_int}/50"
                    color = "#4ECDC4"
                    total_marks += marks_int
                    subjects_counted += 1
                except:
                    display_text = "N/A"
                    color = "#FF6B6B"

            with cols[i % 4]:
                st.markdown(f"""
                <div style='background:#1E1E1E; padding:10px; border-radius:10px; text-align:center; margin:5px;'>
                    <div style='color:#4FC3F7; font-weight:bold;'>{code}</div>
                    <div style='color:#CCC; font-size:12px;'>{name}</div>
                    <div style='color:{color}; font-size:18px; font-weight:bold;'>{display_text}</div>
                </div>
                """, unsafe_allow_html=True)

        # --- Copy Student Details ---
        st.markdown("### 📋 Copy Student Details")
        copy_text = format_student_details(student)
        st.code(copy_text, language='text')

        # --- Performance Summary at Bottom ---
        st.markdown("### 📈 Performance Summary")
        if subjects_counted > 0:
            avg = total_marks / subjects_counted
            perc = (total_marks / (subjects_counted * 50)) * 100
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Marks", f"{total_marks}/{subjects_counted * 50}")
            col2.metric("Average Marks", f"{avg:.1f}/50")
            col3.metric("Percentage", f"{perc:.1f}%")
    else:
        st.error("❌ No matching student found.")