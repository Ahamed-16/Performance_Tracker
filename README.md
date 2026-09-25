# Student Performance Tracker

## Project Overview

The Student Performance Tracker is an interactive web application built with Python and Streamlit to track and analyse students' academic performance and behaviour. It turns raw marks, attendance and conduct ratings into clear dashboards, class-level analytics and complete report cards that can be downloaded as PDFs. It was developed as an Informatics Practices (065) project at Credence High School, Dubai, for the 2026-27 session.

## Features

- **Interactive Dashboard**: Shows total students, passing and failing counts, the class average and average attendance. Red and yellow banners warn about failing students and low attendance, and a banner names the class topper. It also includes a bar chart of averages, a grade distribution pie chart, and a performance table where failing students are highlighted.

- **Individual Student Details**: For any selected student, shows their average, grade, status, class rank and attendance, lists any subjects below the pass mark, and compares their marks with the class average in a table, a radar chart and a bar chart.

- **Report Card**: A school-style report card for each student:
  - Part A: marks, CBSE grades (A1–E), class averages and Pass/Fail for every subject
  - Part B: attendance
  - Part C: conduct and behaviour ratings
  - Part D: the class teacher's remarks

  The report card ends with the final result and can be downloaded as a printable PDF with signature lines.

- **Automatic Teacher's Remarks**: A personalised remark is written for every student from their marks, attendance and conduct.

- **Behaviour & Attendance**: An attendance chart with the 75% requirement line, a colour-coded heatmap of conduct ratings, a scatter plot of attendance against average score (with the correlation), and a list of students who need attention.

- **Class Analytics**: Subject-wise class averages, the topper in each subject, a histogram of average scores, a box plot for every subject, a performance summary and the grade distribution.

- **Data Download**: Exports the full processed dataset, including all calculated columns, as a CSV file.

- **Subjects Not Taken**: A sidebar option (on by default) treats a mark of 0 as "subject not taken", so it doesn't count as a fail or lower the student's average.

## Technologies Used

- **Python**: The core programming language.

- **Pandas**: For storing and processing the data in DataFrames.

- **Streamlit**: For building the interactive web application and user interface.

- **Plotly** (Express and Graph Objects): For interactive charts, including bar charts, pie charts, histograms, box plots, radar charts, heatmaps and scatter plots.

- **fpdf2**: For generating the PDF report cards. The code also works with the older `fpdf` 1.7 library.

## Setup and Installation

To run this project locally, follow these steps:

1. **Prerequisites**: Make sure Python 3.10 or higher is installed on your system.

1. **Get the Project Files**: Save `student_performance.py` and `requirements.txt` in the same project folder.

1. **Install Dependencies**: Open your terminal or command prompt, go to your project folder, and install the required libraries:

   ```bash
   pip install -r requirements.txt
   ```

   The file installs these libraries:

   ```
   streamlit>=1.50.0
   pandas>=2.2.2
   plotly>=5.22.0
   fpdf2>=2.7.0
   ```

   > **Note:** `fpdf` (old) and `fpdf2` (new) are both imported as `fpdf`, so don't install both. If you already have the old one, the app still works. To switch, run `pip uninstall fpdf` first, then `pip install fpdf2`.

## How to Run the Application

1. **Go to the Project Folder**: Open your terminal or command prompt and change to the folder where you saved `student_performance.py`.

1. **Start the App**: Run the application using the Streamlit CLI:

   ```bash
   streamlit run student_performance.py
   ```

1. **Open the Application**: Streamlit opens the app in a new browser tab automatically. If it doesn't, go to `http://localhost:8501` (or the address shown in your terminal).

1. **Use the App**: Choose a page from the sidebar menu: Dashboard, Student Details, Report Card, Behaviour & Attendance, Analytics or Download Data.

## Data Structure and Logic

The application uses an embedded dataset of 10 students. For each student it stores:

- **Marks** out of 100 in seven subjects: English, Informatics Practices, Accountancy, Business Studies, Economics, Physical Education and Islamic Education.
- **Days Present** out of 180 working days.
- **Conduct Ratings** from 1 (poor) to 5 (excellent) for Punctuality, Homework, Class Participation and Behaviour.

The attendance and conduct figures are sample data.

The app calculates the following:

| Measure | How it is calculated |
|---|---|
| **Average Score** | Mean of all the subjects a student takes. A 0 is skipped when the "subject not taken" option is on. |
| **Grade** | Below 35 = **Fail**, 35 to 70 = **Average**, above 70 = **Top Performer** |
| **Status** | **Passing** only if the average **and every subject** are 35 or above; otherwise **Failing** |
| **Subject Grade** | CBSE 8-point scale: A1 (91–100), A2 (81–90), B1 (71–80), B2 (61–70), C1 (51–60), C2 (41–50), D (33–40), E (below 33) |
| **Class Rank** | Students are ranked 1 to 10 by average score |
| **Attendance %** | Days present ÷ 180 × 100. Below 75% is flagged. |
| **Conduct Grade** | Average of the four ratings: 4.5+ Excellent, 3.5+ Good, 2.5+ Satisfactory, below 2.5 Needs Improvement |
| **Remarks** | Generated from the grade, strongest and weakest subjects, attendance and conduct |

All thresholds (pass mark, top mark, required attendance and working days) are set as constants at the top of `student_performance.py`, so they can be changed in one place.

## Project Files

| File | Description |
|---|---|
| `student_performance.py` | The main Streamlit application |
| `requirements.txt` | Python libraries needed to run the app |
| `student_performance.csv` | Sample export of the processed data |
| `Project Report (Final).docx` | Full project report |

## Author

Rasheed & Ammar
