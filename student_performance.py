"""
Student Performance Tracker
Informatics Practices (065) Project | Credence High School, Dubai | 2026-27
Developed by Rasheed & Ammar

Run with:  streamlit run student_performance.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF

# Works with both the old "fpdf" (1.7.x) and the newer "fpdf2" library
try:
    from fpdf.enums import XPos, YPos
    NEW_FPDF = True
except ImportError:
    NEW_FPDF = False

# =====================================================================
# SETTINGS  (change these numbers to change the rules of the whole app)
# =====================================================================
SCHOOL_NAME = "Credence High School, Dubai"
SESSION = "2026-27"
CLASS_SECTION = "XII C"

FAIL_MARK = 35          # below this = Fail
TOP_MARK = 70           # above this = Top Performer (35 to 70 = Average)
ATTENDANCE_REQUIRED = 75  # minimum attendance % required
WORKING_DAYS = 180      # total working days in the session

GRADE_COLORS = {"Fail": "#e74c3c", "Average": "#f39c12", "Top Performer": "#2ecc71"}
CONDUCT_AREAS = ["Punctuality", "Homework", "Class Participation", "Behaviour"]

# --- Page Configuration ---
st.set_page_config(
    page_title="Student Performance Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
st.markdown("""
    <style>
    .report-header {
        text-align: center;
        border: 2px solid #1f4e79;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .report-header h2, .report-header h4 { margin: 0.2rem 0; }
    .remark-box {
        border-left: 5px solid #1f4e79;
        background-color: rgba(31, 78, 121, 0.08);
        padding: 1rem;
        border-radius: 0.3rem;
    }
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# STUDENT DATASET
# Marks are out of 100. A mark of 0 in Islamic Education means the
# student does not take that subject (see the sidebar option).
# Attendance and conduct ratings (1 = poor, 5 = excellent) are sample data.
# =====================================================================
data = [
    {"Roll No": 1, "Name": "Rasheed Ahamed", "English": 69, "Informatics Practices": 81, "Accountancy": 65, "Business Studies": 66, "Economics": 67, "Physical Education": 78, "Islamic Education": 83,
     "Days Present": 170, "Punctuality": 5, "Homework": 4, "Class Participation": 4, "Behaviour": 5},
    {"Roll No": 2, "Name": "Aisha Khan", "English": 48, "Informatics Practices": 52, "Accountancy": 89, "Business Studies": 37, "Economics": 51, "Physical Education": 63, "Islamic Education": 92,
     "Days Present": 158, "Punctuality": 4, "Homework": 3, "Class Participation": 4, "Behaviour": 4},
    {"Roll No": 3, "Name": "Liam O'Connor", "English": 61, "Informatics Practices": 92, "Accountancy": 73, "Business Studies": 95, "Economics": 90, "Physical Education": 50, "Islamic Education": 0,
     "Days Present": 165, "Punctuality": 4, "Homework": 4, "Class Participation": 5, "Behaviour": 4},
    {"Roll No": 4, "Name": "Sofia Martinez", "English": 75, "Informatics Practices": 81, "Accountancy": 37, "Business Studies": 76, "Economics": 92, "Physical Education": 91, "Islamic Education": 0,
     "Days Present": 172, "Punctuality": 5, "Homework": 4, "Class Participation": 4, "Behaviour": 5},
    {"Roll No": 5, "Name": "Chen Wei", "English": 71, "Informatics Practices": 83, "Accountancy": 68, "Business Studies": 89, "Economics": 82, "Physical Education": 60, "Islamic Education": 0,
     "Days Present": 168, "Punctuality": 5, "Homework": 5, "Class Participation": 4, "Behaviour": 5},
    {"Roll No": 6, "Name": "Amara Okafor", "English": 95, "Informatics Practices": 45, "Accountancy": 48, "Business Studies": 56, "Economics": 87, "Physical Education": 47, "Islamic Education": 0,
     "Days Present": 150, "Punctuality": 3, "Homework": 3, "Class Participation": 4, "Behaviour": 4},
    {"Roll No": 7, "Name": "Yuki Tanaka", "English": 38, "Informatics Practices": 23, "Accountancy": 18, "Business Studies": 25, "Economics": 41, "Physical Education": 8, "Islamic Education": 0,
     "Days Present": 118, "Punctuality": 2, "Homework": 2, "Class Participation": 2, "Behaviour": 3},
    {"Roll No": 8, "Name": "Lucas Silva", "English": 82, "Informatics Practices": 49, "Accountancy": 87, "Business Studies": 81, "Economics": 89, "Physical Education": 67, "Islamic Education": 0,
     "Days Present": 160, "Punctuality": 4, "Homework": 3, "Class Participation": 3, "Behaviour": 4},
    {"Roll No": 9, "Name": "Elena Petrova", "English": 38, "Informatics Practices": 70, "Accountancy": 56, "Business Studies": 54, "Economics": 38, "Physical Education": 77, "Islamic Education": 0,
     "Days Present": 130, "Punctuality": 3, "Homework": 2, "Class Participation": 3, "Behaviour": 3},
    {"Roll No": 10, "Name": "Omar Al-Fayed", "English": 78, "Informatics Practices": 91, "Accountancy": 62, "Business Studies": 83, "Economics": 78, "Physical Education": 86, "Islamic Education": 53,
     "Days Present": 175, "Punctuality": 5, "Homework": 5, "Class Participation": 5, "Behaviour": 5},
]

subjects = ["English", "Informatics Practices", "Accountancy", "Business Studies",
            "Economics", "Physical Education", "Islamic Education"]

# --- Sidebar Navigation and Options ---
st.sidebar.title("📚 Navigation")
page = st.sidebar.radio("Select a page:", ["Dashboard", "Student Details", "Report Card",
                                            "Behaviour & Attendance", "Analytics", "Download Data"])
st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Options")
zero_as_not_taken = st.sidebar.checkbox(
    "Treat 0 marks as 'subject not taken'", value=True,
    help="Students who do not study Islamic Education have 0 recorded. "
         "When ticked, those zeros are left out of the average instead of counting as a fail.")


# =====================================================================
# HELPER FUNCTIONS
# =====================================================================
def get_grade(avg):
    """Overall band based on the average score."""
    if avg < FAIL_MARK:
        return "Fail"
    elif avg <= TOP_MARK:
        return "Average"
    else:
        return "Top Performer"


def cbse_grade(mark):
    """Subject grade on the CBSE 8-point scale (used on the report card)."""
    if pd.isna(mark):
        return "N/A"
    if mark >= 91: return "A1"
    if mark >= 81: return "A2"
    if mark >= 71: return "B1"
    if mark >= 61: return "B2"
    if mark >= 51: return "C1"
    if mark >= 41: return "C2"
    if mark >= 33: return "D"
    return "E"


def check_status(row):
    """A student passes only if the average AND every subject are at least FAIL_MARK."""
    if row["Average Score"] < FAIL_MARK:
        return "Failing"
    for subject in subjects:
        if pd.notna(row[subject]) and row[subject] < FAIL_MARK:
            return "Failing"
    return "Passing"


def weak_subjects(row):
    """List of subjects in which the student scored below FAIL_MARK."""
    return [s for s in subjects if pd.notna(row[s]) and row[s] < FAIL_MARK]


def conduct_grade(score):
    """Turns the average conduct rating (1-5) into words."""
    if score >= 4.5:
        return "Excellent"
    elif score >= 3.5:
        return "Good"
    elif score >= 2.5:
        return "Satisfactory"
    else:
        return "Needs Improvement"


def generate_remarks(row):
    """Builds a teacher's remark from marks, attendance and conduct."""
    first_name = row["Name"].split()[0]
    marks = row[subjects].dropna()
    best = marks.idxmax()
    lowest = marks.idxmin()
    remarks = []

    # 1. Academic performance
    if row["Grade"] == "Top Performer":
        remarks.append(f"{first_name} is a top performer with an average of {row['Average Score']:.1f}%.")
    elif row["Grade"] == "Average":
        remarks.append(f"{first_name} has shown steady progress with an average of {row['Average Score']:.1f}%.")
    else:
        remarks.append(f"{first_name} is finding the coursework difficult and needs close support.")

    remarks.append(f"Strongest subject is {best} ({marks[best]:.0f}).")

    weak = weak_subjects(row)
    if weak:
        remarks.append(f"Remedial classes are recommended in {', '.join(weak)}.")
    elif marks[lowest] < 60:
        remarks.append(f"More practice is needed in {lowest} ({marks[lowest]:.0f}).")

    # 2. Attendance
    if row["Attendance %"] < ATTENDANCE_REQUIRED:
        remarks.append(f"Attendance of {row['Attendance %']:.1f}% is below the required "
                       f"{ATTENDANCE_REQUIRED}% and must improve.")
    elif row["Attendance %"] >= 90:
        remarks.append("Attendance is very regular.")

    # 3. Conduct
    if row["Homework"] <= 2:
        remarks.append("Homework must be completed on time.")
    if row["Conduct Score"] >= 4.5:
        remarks.append("Conduct in class is exemplary.")
    elif row["Conduct Score"] < 3:
        remarks.append("Needs to be more punctual and attentive in class.")

    return " ".join(remarks)


def show_marks(frame):
    """Copy of a table with marks shown as whole numbers and 'N/A' for subjects not taken."""
    frame = frame.copy()
    for s in subjects:
        frame[s] = frame[s].apply(lambda m: "N/A" if pd.isna(m) else f"{m:.0f}")
    return frame


def stars(rating):
    """Shows a 1-5 rating as stars, e.g. 4 -> ★★★★☆"""
    return "★" * int(rating) + "☆" * (5 - int(rating))


# =====================================================================
# DATAFRAME AND CALCULATED COLUMNS
# =====================================================================
df = pd.DataFrame(data)

if zero_as_not_taken:
    # Replace 0 with "missing" (NaN) so that mean() skips it
    df[subjects] = df[subjects].replace(0, float("nan"))

df["Subjects Taken"] = df[subjects].notna().sum(axis=1)
df["Total Marks"] = df[subjects].sum(axis=1)
df["Average Score"] = df[subjects].mean(axis=1).round(2)
df["Grade"] = df["Average Score"].apply(get_grade)
df["Status"] = df.apply(check_status, axis=1)
df["Rank"] = df["Average Score"].rank(ascending=False, method="min").astype(int)

df["Attendance %"] = (df["Days Present"] / WORKING_DAYS * 100).round(1)
df["Conduct Score"] = df[CONDUCT_AREAS].mean(axis=1).round(2)
df["Conduct Grade"] = df["Conduct Score"].apply(conduct_grade)
df["Remarks"] = df.apply(generate_remarks, axis=1)

class_subject_avg = df[subjects].mean()


# =====================================================================
# PDF REPORT CARD
# =====================================================================
def pdf_safe(text):
    """The built-in PDF fonts only support basic characters, so replace the rest."""
    text = str(text).replace("—", "-").replace("–", "-").replace("’", "'")
    return text.encode("latin-1", "replace").decode("latin-1")


def pdf_cell(pdf, w, h, text, border=0, ln=0, align="L", fill=False):
    """Writes one cell. ln=1 moves to the next line, ln=0 stays on the same line."""
    if not NEW_FPDF:
        pdf.cell(w, h, text, border, ln, align, fill)
    elif ln == 1:
        pdf.cell(w, h, text, border=border, align=align, fill=fill, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    else:
        pdf.cell(w, h, text, border=border, align=align, fill=fill, new_x=XPos.RIGHT, new_y=YPos.TOP)


def generate_pdf(student):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Header
    pdf.set_font("Helvetica", "B", 16)
    pdf_cell(pdf, 0, 9, pdf_safe(SCHOOL_NAME), 0, 1, "C")
    pdf.set_font("Helvetica", "", 12)
    pdf_cell(pdf, 0, 7, f"Progress Report Card - Session {SESSION}", 0, 1, "C")
    pdf.ln(3)

    # Student information
    pdf.set_font("Helvetica", "", 11)
    pdf_cell(pdf, 95, 7, pdf_safe(f"Name: {student['Name']}"), 1)
    pdf_cell(pdf, 95, 7, f"Class: {CLASS_SECTION}", 1, 1)
    pdf_cell(pdf, 95, 7, f"Roll No: {student['Roll No']}", 1)
    pdf_cell(pdf, 95, 7, f"Class Rank: {student['Rank']} of {len(df)}", 1, 1)
    pdf.ln(4)

    # Part A - Scholastic
    pdf.set_font("Helvetica", "B", 12)
    pdf_cell(pdf, 0, 8, "Part A: Scholastic Areas", 0, 1)
    pdf.set_fill_color(31, 78, 121)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 11)
    for heading, width in [("Subject", 70), ("Marks (100)", 35), ("Grade", 30), ("Class Avg", 30), ("Result", 25)]:
        pdf_cell(pdf, width, 8, heading, 1, 0, "C", True)
    pdf.ln()
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 11)
    for subject in subjects:
        mark = student[subject]
        if pd.isna(mark):
            values = ["Not taken", "-", "-", "-"]
        else:
            values = [f"{mark:.0f}", cbse_grade(mark), f"{class_subject_avg[subject]:.1f}",
                      "Pass" if mark >= FAIL_MARK else "Fail"]
        pdf_cell(pdf, 70, 7, subject, 1)
        for value, width in zip(values, [35, 30, 30, 25]):
            pdf_cell(pdf, width, 7, value, 1, 0, "C")
        pdf.ln()
    pdf.set_font("Helvetica", "B", 11)
    pdf_cell(pdf, 70, 7, "Total / Average", 1)
    pdf_cell(pdf, 35, 7, f"{student['Total Marks']:.0f} / {student['Subjects Taken'] * 100}", 1, 0, "C")
    pdf_cell(pdf, 85, 7, f"Average: {student['Average Score']:.2f}%   ({student['Grade']})", 1, 1, "C")
    pdf.ln(4)

    # Part B - Attendance
    pdf.set_font("Helvetica", "B", 12)
    pdf_cell(pdf, 0, 8, "Part B: Attendance", 0, 1)
    pdf.set_font("Helvetica", "", 11)
    pdf_cell(pdf, 0, 7, f"Days present: {student['Days Present']} of {WORKING_DAYS}   "
                   f"({student['Attendance %']:.1f}%)   Required: {ATTENDANCE_REQUIRED}%", 1, 1)
    pdf.ln(4)

    # Part C - Conduct
    pdf.set_font("Helvetica", "B", 12)
    pdf_cell(pdf, 0, 8, "Part C: Conduct and Behaviour", 0, 1)
    pdf.set_font("Helvetica", "", 11)
    for area in CONDUCT_AREAS:
        pdf_cell(pdf, 70, 7, area, 1)
        pdf_cell(pdf, 120, 7, f"{student[area]} / 5   ({conduct_grade(student[area])})", 1, 1)
    pdf.set_font("Helvetica", "B", 11)
    pdf_cell(pdf, 70, 7, "Overall Conduct", 1)
    pdf_cell(pdf, 120, 7, f"{student['Conduct Score']:.2f} / 5   ({student['Conduct Grade']})", 1, 1)
    pdf.ln(4)

    # Part D - Remarks and result
    pdf.set_font("Helvetica", "B", 12)
    pdf_cell(pdf, 0, 8, "Part D: Class Teacher's Remarks", 0, 1)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 6, pdf_safe(student["Remarks"]), border=1, align="L")
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 12)
    result = "PROMOTED" if student["Status"] == "Passing" else "NEEDS IMPROVEMENT - NOT CLEARED"
    pdf_cell(pdf, 0, 8, f"Result: {result}", 0, 1)
    pdf.ln(15)

    # Signatures
    pdf.set_font("Helvetica", "", 11)
    for _ in range(3):
        pdf_cell(pdf, 63, 7, "____________________", 0, 0, "C")
    pdf.ln()
    for label in ["Class Teacher", "Principal", "Parent"]:
        pdf_cell(pdf, 63, 7, label, 0, 0, "C")

    if NEW_FPDF:
        return bytes(pdf.output())
    return pdf.output(dest="S").encode("latin-1")


# =====================================================================
# PAGE 1: DASHBOARD
# =====================================================================
if page == "Dashboard":
    st.title("📊 Student Performance Dashboard")
    st.markdown("---")

    # Warning banners
    failing_count = len(df[df["Status"] == "Failing"])
    low_attendance = len(df[df["Attendance %"] < ATTENDANCE_REQUIRED])
    if failing_count > 0:
        st.error(f"⚠️ **{failing_count} student(s) are failing!** Immediate attention required.")
    else:
        st.success("✅ All students have cleared every subject!")
    if low_attendance > 0:
        st.warning(f"📅 **{low_attendance} student(s)** have attendance below {ATTENDANCE_REQUIRED}%.")

    # Key Metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Students", len(df))
    col2.metric("Passing", len(df[df["Status"] == "Passing"]))
    col3.metric("Failing", failing_count)
    col4.metric("Class Average", f"{df['Average Score'].mean():.2f}")
    col5.metric("Avg Attendance", f"{df['Attendance %'].mean():.1f}%")

    topper = df.loc[df["Average Score"].idxmax()]
    st.info(f"🏆 **Class Topper:** {topper['Name']} with an average of {topper['Average Score']:.2f}%")

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        fig_avg = px.bar(
            df.sort_values("Average Score", ascending=False),
            x="Name", y="Average Score", color="Grade",
            color_discrete_map=GRADE_COLORS,
            title="Average Scores by Student",
            labels={"Average Score": "Score", "Name": "Student"}
        )
        fig_avg.add_hline(y=FAIL_MARK, line_dash="dash", line_color="red", annotation_text=f"Fail ({FAIL_MARK})")
        fig_avg.add_hline(y=TOP_MARK, line_dash="dash", line_color="green", annotation_text=f"Top ({TOP_MARK})")
        fig_avg.update_layout(height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig_avg)

    with col2:
        grade_counts = df["Grade"].value_counts()
        fig_pie = px.pie(values=grade_counts.values, names=grade_counts.index,
                         title="Grade Distribution", color=grade_counts.index,
                         color_discrete_map=GRADE_COLORS)
        st.plotly_chart(fig_pie)

    st.markdown("---")

    def highlight_fail(row):
        # Dark red text on light red so the row is readable in light and dark mode
        style = 'background-color: #ffcccc; color: #7b241c; font-weight: bold'
        return [style if row["Status"] == "Failing" else '' for _ in row]

    st.subheader("📋 Student Performance Table")
    table_cols = ["Rank", "Name"] + subjects + ["Average Score", "Grade", "Status", "Attendance %", "Conduct Grade"]
    styled = show_marks(df[table_cols].sort_values("Rank")).style.apply(highlight_fail, axis=1).format(precision=2)
    st.dataframe(styled, hide_index=True)

# =====================================================================
# PAGE 2: STUDENT DETAILS
# =====================================================================
elif page == "Student Details":
    st.title("👤 Individual Student Details")
    st.markdown("---")

    selected = st.selectbox("Select a student:", df["Name"].tolist())
    student = df[df["Name"] == selected].iloc[0]

    col1, col2, col3, col4, col5 = st.columns([1, 1.6, 1, 1, 1])
    col1.metric("Average Score", f"{student['Average Score']:.2f}")
    col2.metric("Grade", student["Grade"])
    col3.metric("Status", student["Status"])
    col4.metric("Class Rank", f"{student['Rank']} / {len(df)}")
    col5.metric("Attendance", f"{student['Attendance %']:.1f}%")

    weak = weak_subjects(student)
    if weak:
        st.error(f"Below {FAIL_MARK} in: **{', '.join(weak)}**")

    st.markdown("---")

    subject_df = pd.DataFrame([
        {"Subject": s, "Score": student[s], "Class Average": round(class_subject_avg[s], 2),
         "Difference": round(student[s] - class_subject_avg[s], 2)}
        for s in subjects if pd.notna(student[s])
    ])

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📚 Subject-wise Scores")
        st.dataframe(subject_df, hide_index=True)
    with col2:
        # Radar chart: student vs class average
        # Orange = student, blue dashed = class average (clear in light and dark mode)
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=subject_df["Score"], theta=subject_df["Subject"], name=selected,
            fill="toself", fillcolor="rgba(243, 156, 18, 0.25)",
            line=dict(color="#f39c12", width=3), marker=dict(size=7)))
        # Class average is drawn on top, as a line only, so it is never hidden
        fig_radar.add_trace(go.Scatterpolar(
            r=subject_df["Class Average"], theta=subject_df["Subject"], name="Class Average",
            line=dict(color="#3fa9f5", width=3, dash="dash"), marker=dict(size=6)))
        fig_radar.update_layout(
            title="Student vs Class Average", height=420,
            margin=dict(l=90, r=90, t=60, b=40),
            legend=dict(orientation="h", y=-0.1),
            polar=dict(
                bgcolor="rgba(0, 0, 0, 0)",   # transparent, so it matches the page theme
                radialaxis=dict(range=[0, 100], angle=90, tickangle=90, tickvals=[20, 40, 60, 80, 100],
                                gridcolor="rgba(128, 128, 128, 0.4)", linecolor="rgba(128, 128, 128, 0.4)"),
                angularaxis=dict(gridcolor="rgba(128, 128, 128, 0.4)", linecolor="rgba(128, 128, 128, 0.6)")))
        st.plotly_chart(fig_radar)

    fig_subject = px.bar(subject_df, x="Subject", y="Score", color="Score",
                         color_continuous_scale="RdYlGn", range_color=[0, 100],
                         title=f"Subject Performance for {selected}")
    fig_subject.add_hline(y=FAIL_MARK, line_dash="dash", line_color="red", annotation_text=f"Fail ({FAIL_MARK})")
    fig_subject.add_hline(y=TOP_MARK, line_dash="dash", line_color="green", annotation_text=f"Top ({TOP_MARK})")
    fig_subject.update_layout(height=400, xaxis_tickangle=-45)
    st.plotly_chart(fig_subject)

# =====================================================================
# PAGE 3: REPORT CARD
# =====================================================================
elif page == "Report Card":
    st.title("📝 Student Report Card")
    selected = st.selectbox("Select a student:", df["Name"].tolist())
    student = df[df["Name"] == selected].iloc[0]

    # Header
    st.markdown(f"""
        <div class="report-header">
            <h2>{SCHOOL_NAME}</h2>
            <h4>Progress Report Card &nbsp;|&nbsp; Session {SESSION}</h4>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.markdown(f"**Name:** {student['Name']}")
    col2.markdown(f"**Class:** {CLASS_SECTION}")
    col3.markdown(f"**Roll No:** {student['Roll No']}")
    col4.markdown(f"**Class Rank:** {student['Rank']} of {len(df)}")

    # Part A - Scholastic
    st.subheader("Part A: Scholastic Areas")
    marks_rows = []
    for s in subjects:
        mark = student[s]
        if pd.isna(mark):
            marks_rows.append({"Subject": s, "Marks (100)": "Not taken", "Grade": "-",
                               "Class Average": "-", "Result": "-"})
        else:
            marks_rows.append({"Subject": s, "Marks (100)": f"{mark:.0f}", "Grade": cbse_grade(mark),
                               "Class Average": f"{class_subject_avg[s]:.1f}",
                               "Result": "Pass" if mark >= FAIL_MARK else "Fail"})
    marks_table = pd.DataFrame(marks_rows)

    def color_result(value):
        if value == "Fail":
            return "background-color: #ffcccc; color: #922b21; font-weight: bold"
        if value == "Pass":
            return "background-color: #d5f5e3; color: #145a32; font-weight: bold"
        return ""

    st.dataframe(marks_table.style.map(color_result, subset=["Result"]), hide_index=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Marks", f"{student['Total Marks']:.0f} / {student['Subjects Taken'] * 100}")
    col2.metric("Percentage", f"{student['Average Score']:.2f}%")
    col3.metric("Overall Grade", student["Grade"])

    # Part B - Attendance
    st.subheader("Part B: Attendance")
    col1, col2 = st.columns([1, 2])
    col1.metric("Days Present", f"{student['Days Present']} / {WORKING_DAYS}")
    with col2:
        st.progress(min(student["Attendance %"] / 100, 1.0),
                    text=f"Attendance: {student['Attendance %']:.1f}% (required {ATTENDANCE_REQUIRED}%)")
        if student["Attendance %"] < ATTENDANCE_REQUIRED:
            st.error("Attendance is below the required minimum.")

    # Part C - Conduct
    st.subheader("Part C: Conduct and Behaviour")
    conduct_table = pd.DataFrame([
        {"Area": area, "Rating": stars(student[area]), "Score": f"{student[area]} / 5",
         "Remark": conduct_grade(student[area])}
        for area in CONDUCT_AREAS
    ])
    st.dataframe(conduct_table, hide_index=True)
    st.markdown(f"**Overall Conduct:** {student['Conduct Score']:.2f} / 5 — **{student['Conduct Grade']}**")

    # Part D - Remarks
    st.subheader("Part D: Class Teacher's Remarks")
    st.markdown(f"<div class='remark-box'>{student['Remarks']}</div>", unsafe_allow_html=True)
    st.write("")

    if student["Status"] == "Passing":
        st.success("**Result: PROMOTED**")
    else:
        st.error("**Result: NEEDS IMPROVEMENT — NOT CLEARED**")

    st.download_button(
        label="📄 Download Report Card (PDF)",
        data=generate_pdf(student),
        file_name=f"{student['Name']}_Report_Card.pdf",
        mime="application/pdf"
    )

# =====================================================================
# PAGE 4: BEHAVIOUR & ATTENDANCE
# =====================================================================
elif page == "Behaviour & Attendance":
    st.title("🧑‍🏫 Behaviour & Attendance")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    col1.metric("Average Attendance", f"{df['Attendance %'].mean():.1f}%")
    col2.metric(f"Below {ATTENDANCE_REQUIRED}%", len(df[df["Attendance %"] < ATTENDANCE_REQUIRED]))
    col3.metric("Average Conduct Score", f"{df['Conduct Score'].mean():.2f} / 5")

    # Attendance bar chart
    att_df = df.sort_values("Attendance %", ascending=False).copy()
    att_df["Attendance Check"] = att_df["Attendance %"].apply(
        lambda a: "Below required" if a < ATTENDANCE_REQUIRED else "OK")
    fig_att = px.bar(att_df, x="Name", y="Attendance %", color="Attendance Check",
                     color_discrete_map={"OK": "#2ecc71", "Below required": "#e74c3c"},
                     title="Attendance by Student")
    fig_att.add_hline(y=ATTENDANCE_REQUIRED, line_dash="dash", line_color="red",
                      annotation_text=f"Required ({ATTENDANCE_REQUIRED}%)")
    fig_att.update_layout(height=400, xaxis_tickangle=-45, yaxis_range=[0, 100])
    st.plotly_chart(fig_att)

    col1, col2 = st.columns(2)
    with col1:
        # Heatmap of conduct ratings
        conduct = df.set_index("Name")[CONDUCT_AREAS]
        fig_heat = px.imshow(conduct, text_auto=True, color_continuous_scale="RdYlGn",
                             zmin=1, zmax=5, aspect="auto", title="Conduct Ratings (1-5)")
        fig_heat.update_layout(height=450)
        st.plotly_chart(fig_heat)
    with col2:
        # Does attendance affect marks?
        correlation = df["Attendance %"].corr(df["Average Score"])
        fig_scatter = px.scatter(df, x="Attendance %", y="Average Score", color="Grade",
                                 color_discrete_map=GRADE_COLORS, hover_name="Name",
                                 size="Conduct Score", title="Attendance vs Average Score")
        fig_scatter.update_layout(height=450)
        st.plotly_chart(fig_scatter)
        st.caption(f"Correlation between attendance and average score: **{correlation:.2f}** "
                   "(close to +1 means students who attend more tend to score higher).")

    st.subheader("⚠️ Students Needing Attention")
    attention = df[(df["Attendance %"] < ATTENDANCE_REQUIRED) | (df["Conduct Score"] < 3) |
                   (df["Status"] == "Failing")]
    if attention.empty:
        st.success("No students need attention right now.")
    else:
        st.dataframe(attention[["Name", "Attendance %", "Conduct Score", "Conduct Grade",
                                "Average Score", "Status"]], hide_index=True)

# =====================================================================
# PAGE 5: ANALYTICS
# =====================================================================
elif page == "Analytics":
    st.title("📈 Class Analytics")
    st.markdown("---")

    st.subheader("📊 Subject-wise Class Average")
    subject_avg_df = pd.DataFrame(
        [{"Subject": s, "Average Score": round(class_subject_avg[s], 2)} for s in subjects]
    ).sort_values("Average Score", ascending=False)

    fig_subject = px.bar(subject_avg_df, x="Subject", y="Average Score", color="Average Score",
                         color_continuous_scale="Viridis", title="Class Average by Subject")
    fig_subject.add_hline(y=50, line_dash="dash", line_color="orange", annotation_text="Target (50)")
    fig_subject.update_layout(height=400, xaxis_tickangle=-45)
    st.plotly_chart(fig_subject)

    # Subject toppers
    st.subheader("🏅 Subject Toppers")
    toppers = pd.DataFrame([
        {"Subject": s, "Topper": df.loc[df[s].idxmax(), "Name"], "Marks": df[s].max(),
         "Lowest": df[s].min(), f"Students Below {FAIL_MARK}": int((df[s] < FAIL_MARK).sum())}
        for s in subjects
    ])
    st.dataframe(toppers, hide_index=True)

    st.markdown("---")
    st.subheader("📊 Score Distribution Analysis")
    col1, col2 = st.columns(2)
    with col1:
        fig_hist = px.histogram(df, x="Average Score", nbins=10, title="Distribution of Average Scores",
                                color_discrete_sequence=["#3498db"])
        fig_hist.update_layout(height=400)
        st.plotly_chart(fig_hist)
    with col2:
        fig_box = go.Figure()
        for subject in subjects:
            fig_box.add_trace(go.Box(y=df[subject], name=subject))
        fig_box.update_layout(title="Score Distribution by Subject", yaxis_title="Score",
                              height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig_box)

    st.markdown("---")
    st.subheader("📊 Performance Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Highest Average", f"{df['Average Score'].max():.2f}")
    col2.metric("Lowest Average", f"{df['Average Score'].min():.2f}")
    col3.metric("Median Average", f"{df['Average Score'].median():.2f}")

    st.subheader("📋 Grade Distribution")
    grade_dist = df["Grade"].value_counts().reset_index()
    grade_dist.columns = ["Grade", "Count"]
    st.dataframe(grade_dist, hide_index=True)

# =====================================================================
# PAGE 6: DOWNLOAD DATA
# =====================================================================
elif page == "Download Data":
    st.title("📥 Download Data")
    st.markdown("---")

    export_df = df.drop(columns=["Remarks"])
    # Int64 keeps marks as whole numbers while allowing empty cells for subjects not taken
    export_df[subjects + ["Total Marks"]] = export_df[subjects + ["Total Marks"]].round().astype("Int64")
    csv = export_df.to_csv(index=False)
    st.download_button(label="📥 Download CSV", data=csv,
                       file_name="student_performance.csv", mime="text/csv")

    st.markdown("---")
    st.subheader("📊 Data Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Records", len(df))
    col2.metric("Total Subjects", len(subjects))
    col3.metric("Passing Students", len(df[df["Status"] == "Passing"]))
    col4.metric("Failing Students", len(df[df["Status"] == "Failing"]))

    st.markdown("---")
    st.subheader("📋 Full Dataset")
    st.dataframe(show_marks(export_df).style.format(precision=2), hide_index=True)

# --- Footer ---
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>Student Performance Tracker | "
            "School Project 2026 | Developed by Rasheed & Ammar</p>", unsafe_allow_html=True)