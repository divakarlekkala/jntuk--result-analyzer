# JNTUK Result Analyzer

![Python](https://img.shields.io/badge/Python-3.9-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.0-red)
![Pandas](https://img.shields.io/badge/Pandas-1.3-green)
![Status](https://img.shields.io/badge/Status-Completed-brightgreen)

> A web application that automatically parses JNTUK semester result PDFs and calculates SGPA, CGPA, backlogs, and performance trends — built with Python and Streamlit.

---

## About the Project

JNTUK students receive their results as PDF memos which require manual calculation of SGPA and CGPA. This tool automates the entire process — upload your result PDFs and instantly get a complete academic dashboard.

Supports all major JNTUK regulations: **R16, R19, R20, R23**

---

## Features

- **PDF Parsing** — Automatically extracts student name, roll number, grades, and credits from result PDFs
- **SGPA Calculator** — Calculates Semester Grade Point Average per semester
- **CGPA Calculator** — Computes overall CGPA across all uploaded semesters
- **Backlog Tracker** — Instantly highlights failed subjects (F, AB, M grades)
- **Performance Trend** — Line chart showing SGPA progression across semesters
- **Multi-format Support** — Accepts both PDF memos and CSV files
- **Demo Mode** — Try the app without uploading real documents

---

## Tech Stack

- **Language:** Python 3.9
- **Framework:** Streamlit
- **Libraries:** Pandas, pdfplumber, re (regex)
- **Tools:** Jupyter Notebook, GitHub

---

## How It Works

1. User uploads JNTUK result PDF memos via the sidebar
2. `analyzer.py` parses each PDF using `pdfplumber` and regex
3. Subject codes, grades, and credits are extracted per semester
4. SGPA is calculated using the standard credit-weighted formula
5. Results are displayed in an interactive Streamlit dashboard

---

## Installation and Setup

1. Clone the repository
```
git clone https://github.com/divakarlekkala/jntuk-result-analyzer
```

2. Install dependencies
```
pip install -r requirements.txt
```

3. Run the app
```
streamlit run app.py
```

4. Open your browser at `http://localhost:8501`

---

## Project Structure

```
jntuk-result-analyzer/
│
├── analyzer.py        # PDF parsing, SGPA calculation logic
├── app.py             # Streamlit web app and dashboard UI
├── requirements.txt   # Project dependencies
├── LICENSE            # MIT License
└── README.md          # Project documentation
```

---

## Grade Point System

| Grade | Points |
|-------|--------|
| O / S / A+ | 10 |
| A | 9 |
| B | 8 |
| C | 7 |
| D | 6 |
| E | 5 |
| F / AB / M | 0 (Backlog) |

---

## Screenshots<img width="1920" height="1080" alt="Screenshot 2026-03-20 071722" src="https://github.com/user-attachments/assets/92753223-e689-44d5-92f8-a62def602880" />


> Add screenshots of your running app here — dashboard view, SGPA chart, backlog section

---

## Future Improvements

- Export results as PDF report
- Support for other university formats (JNTU Hyderabad, Anantapur)
- Email notification for backlog alerts
- Rank comparison among uploaded students

---

## Contact

**Lekkala Divakar**
- Email: lekkaladivakar2@gmail.com
- LinkedIn: linkedin.com/in/lekkaladivakar
- GitHub: github.com/divakarlekkala
