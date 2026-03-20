import streamlit as st
import pandas as pd
from analyzer import calculate_results, parse_pdf

st.set_page_config(
    page_title="JNTUK Result Analyzer",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- MAIN TITLE ---
st.title("🎓 JNTUK Result Analyzer")
st.caption("Upload semester memos to calculate SGPA, CGPA, backlogs and compare students.")

# --- SIDEBAR: UPLOAD ---
with st.sidebar:
    st.header("Upload Center")
    uploaded_files = st.file_uploader(
        "Upload Memos (PDF/CSV)",
        type=["csv", "pdf"],
        accept_multiple_files=True
    )
    use_demo = st.checkbox("Use Demo Data")
    st.info("Supports JNTUK R16/R19/R20/R23 formats")

all_semesters_data = []

# --- DATA LOADING ---
if use_demo:
    # Demo data with 3 students for comparison demo
    data = {
        'RollNo': ['22HJ1A4301']*6 + ['22HJ1A4302']*6 + ['22HJ1A4303']*6,
        'StudentName': ['Divakar']*6 + ['Ravi']*6 + ['Priya']*6,
        'Semester': ['1-1', '1-1', '1-2', '1-2', '2-1', '2-1'] * 3,
        'Subject': ['Python', 'Maths-I', 'Data Structures', 'Maths-II', 'Java', 'OS'] * 3,
        'Grade': ['B', 'A', 'S', 'B', 'A', 'B',
                  'A', 'B', 'B', 'A', 'S', 'A',
                  'F', 'A', 'A', 'B', 'B', 'F'],
        'Credits': [3, 3, 3, 3, 3, 3] * 3,
        'Points': [8, 9, 10, 8, 9, 8,
                   9, 8, 8, 9, 10, 9,
                   0, 9, 9, 8, 8, 0]
    }
    all_semesters_data.append(pd.DataFrame(data))

elif uploaded_files:
    for file in uploaded_files:
        try:
            file.seek(0)
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            elif file.name.endswith('.pdf'):
                df = parse_pdf(file)

            if df is not None:
                all_semesters_data.append(df)
        except Exception as e:
            st.error(f"Could not read {file.name}. Please check the file format.")

# --- DASHBOARD ---
if all_semesters_data:
    full_history = pd.concat(all_semesters_data, ignore_index=True)

    # CLEANUP — keep highest grade per subject per student
    if 'Points' in full_history.columns:
        full_history.sort_values(by='Points', ascending=False, inplace=True)
    full_history.drop_duplicates(subset=['RollNo', 'Subject'], keep='first', inplace=True)
    full_history.sort_values(by=['RollNo', 'Semester', 'Subject'], inplace=True)

    # --- DETECT MULTIPLE STUDENTS ---
    unique_students = full_history['RollNo'].unique()
    is_multi = len(unique_students) > 1

    st.divider()

    # ===================================================
    # MODE 1: MULTI-STUDENT COMPARISON
    # ===================================================
    if is_multi:
        st.subheader(f"Comparing {len(unique_students)} Students")

        # --- BUILD COMPARISON TABLE ---
        comparison_rows = []
        for roll in unique_students:
            student_df = full_history[full_history['RollNo'] == roll]
            name = student_df['StudentName'].iloc[0]

            academic = student_df[~student_df['Grade'].isin(['COMPLETED', 'Y'])]
            total_creds = academic['Credits'].sum()
            total_pts = (academic['Credits'] * academic['Points']).sum()
            cgpa = round(total_pts / total_creds, 2) if total_creds > 0 else 0.0
            percentage = round((cgpa - 0.5) * 10, 2)
            backlogs = int((student_df['Grade'].isin(['F', 'AB', 'M'])).sum())
            semesters_count = student_df['Semester'].nunique()

            comparison_rows.append({
                'Rank': 0,
                'Roll No': roll,
                'Name': name,
                'CGPA': cgpa,
                'Percentage': f"{percentage}%",
                'Backlogs': backlogs,
                'Semesters': semesters_count,
                'Status': 'Clear' if backlogs == 0 else f'{backlogs} Backlog(s)'
            })

        comp_df = pd.DataFrame(comparison_rows)
        comp_df.sort_values(by='CGPA', ascending=False, inplace=True)
        comp_df['Rank'] = range(1, len(comp_df) + 1)

        # --- TOP 3 METRICS ---
        top3 = comp_df.head(3)
        cols = st.columns(len(top3))
        medals = ['🥇', '🥈', '🥉']
        for i, (_, row) in enumerate(top3.iterrows()):
            cols[i].metric(
                f"{medals[i]} {row['Name']}",
                f"CGPA: {row['CGPA']}",
                f"Backlogs: {row['Backlogs']}"
            )

        st.divider()

        # --- FULL COMPARISON TABLE ---
        st.subheader("Full Rankings")
        st.dataframe(
            comp_df[['Rank', 'Roll No', 'Name', 'CGPA', 'Percentage', 'Backlogs', 'Status']],
            use_container_width=True,
            hide_index=True
        )

        # --- CGPA BAR CHART ---
        st.divider()
        st.subheader("CGPA Comparison")
        chart_df = comp_df[['Name', 'CGPA']].set_index('Name')
        st.bar_chart(chart_df)

        # --- BACKLOG COMPARISON ---
        st.divider()
        st.subheader("Backlog Comparison")
        backlog_df = comp_df[['Name', 'Backlogs']].set_index('Name')
        st.bar_chart(backlog_df)

        # --- DOWNLOAD COMPARISON REPORT ---
        st.divider()
        csv = comp_df.to_csv(index=False)
        st.download_button(
            label="Download Comparison Report (CSV)",
            data=csv,
            file_name="student_comparison.csv",
            mime="text/csv"
        )

        st.divider()

        # --- PER STUDENT DETAIL (EXPANDABLE) ---
        st.subheader("Individual Student Details")
        for roll in unique_students:
            student_df = full_history[full_history['RollNo'] == roll]
            name = student_df['StudentName'].iloc[0]

            with st.expander(f"View details — {name} ({roll})"):
                failed = student_df[student_df['Grade'].isin(['F', 'AB', 'M'])]
                if not failed.empty:
                    st.error(f"Backlogs: {len(failed)}")
                    st.dataframe(failed[['Semester', 'Subject', 'Grade']], hide_index=True)
                else:
                    st.success("No backlogs")

                semesters = sorted(student_df['Semester'].unique())
                if semesters:
                    tabs = st.tabs(semesters)
                    for i, sem in enumerate(semesters):
                        with tabs[i]:
                            sem_data = student_df[student_df['Semester'] == sem]
                            res = calculate_results(pd.DataFrame(sem_data))
                            sgpa = res.iloc[0]['SGPA']
                            st.metric(f"SGPA ({sem})", sgpa)
                            display_df = sem_data.copy()
                            display_df['Status'] = display_df['Grade'].apply(
                                lambda x: 'Fail' if x in ['F', 'AB', 'M'] else 'Pass'
                            )
                            st.dataframe(
                                display_df[['Subject', 'Grade', 'Status', 'Credits']],
                                use_container_width=True,
                                hide_index=True
                            )

    # ===================================================
    # MODE 2: SINGLE STUDENT (original flow)
    # ===================================================
    else:
        roll = unique_students[0]
        student_df = full_history[full_history['RollNo'] == roll]
        name = student_df['StudentName'].iloc[0]

        st.success(f"Student: {name}  |  Roll No: {roll}")

        # --- SECTION A: FAILURES ---
        failed_df = student_df[student_df['Grade'].isin(['F', 'AB', 'M'])]
        if not failed_df.empty:
            st.error(f"Active Backlogs: {len(failed_df)}")
            st.dataframe(
                failed_df[['Semester', 'Subject', 'Grade']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("All Clear! No Backlogs.")

        # --- SECTION B: SEMESTER TABS ---
        semesters = sorted(student_df['Semester'].unique())
        if semesters:
            tabs = st.tabs(semesters)
            for i, sem in enumerate(semesters):
                with tabs[i]:
                    sem_data = student_df[student_df['Semester'] == sem]
                    if not sem_data.empty:
                        res = calculate_results(pd.DataFrame(sem_data))
                        sgpa = res.iloc[0]['SGPA']
                    else:
                        sgpa = 0.0
                    st.metric(f"SGPA ({sem})", sgpa)
                    display_df = sem_data.copy()
                    display_df['Status'] = display_df['Grade'].apply(
                        lambda x: 'Fail' if x in ['F', 'AB', 'M'] else 'Pass'
                    )
                    st.dataframe(
                        display_df[['Subject', 'Grade', 'Status', 'Credits']],
                        use_container_width=True,
                        hide_index=True
                    )

        # --- SECTION C: FINAL CGPA ---
        st.divider()
        academic = student_df[~student_df['Grade'].isin(['COMPLETED', 'Y'])]
        total_creds = academic['Credits'].sum()
        total_pts = (academic['Credits'] * academic['Points']).sum()
        cgpa = round(total_pts / total_creds, 2) if total_creds > 0 else 0.0
        percentage = round((cgpa - 0.5) * 10, 2)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Credits", total_creds)
        c2.metric("Total Semesters", len(semesters))
        c3.metric("Final CGPA", cgpa)
        c4.metric("Percentage", f"{percentage}%")

        # --- SECTION D: VISUALIZATIONS ---
        st.divider()
        st.subheader("Performance Trend")

        trend_data = []
        for sem in semesters:
            sem_df = student_df[student_df['Semester'] == sem]
            if not sem_df.empty:
                res = calculate_results(pd.DataFrame(sem_df))
                trend_data.append({'Semester': sem, 'SGPA': res.iloc[0]['SGPA']})

        if trend_data:
            trend_df = pd.DataFrame(trend_data)
            st.line_chart(trend_df.set_index('Semester')['SGPA'])

            if len(trend_df) > 1:
                first = trend_df.iloc[0]['SGPA']
                last = trend_df.iloc[-1]['SGPA']
                diff = round(last - first, 2)
                if diff > 0:
                    st.success(f"Improvement: +{diff} points since start!")
                elif diff < 0:
                    st.warning(f"Drop: {diff} points since start.")

        # Subject-wise grade bar chart
        st.divider()
        st.subheader("Subject-wise Grade Points")
        chart_data = student_df[['Subject', 'Points']].set_index('Subject')
        st.bar_chart(chart_data)

        # --- DOWNLOAD ---
        st.divider()
        csv = student_df.to_csv(index=False)
        st.download_button(
            label="Download Results (CSV)",
            data=csv,
            file_name=f"{roll}_results.csv",
            mime="text/csv"
        )

# --- FOOTER ---
st.divider()
st.caption("Built by Lekkala Divakar | linkedin.com/in/lekkaladivakar")

elif not use_demo:
    st.info("Upload PDF or CSV files to begin, or enable Demo Data from the sidebar.")
