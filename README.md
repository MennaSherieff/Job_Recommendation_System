# ML Job Recommendation System (CV–JD Matching with Soft Skills from Video)

## Overview
This project implements an end-to-end **Machine Learning Job Recommendation System** that matches candidates to job opportunities by jointly considering **hard skills** (from CVs and Job Descriptions) and **soft skills** (predicted from candidate videos).

Unlike traditional ATS systems that rely only on text similarity, this system:
- Extracts **soft skills from audio–visual signals**
- Combines them with **hard skill matching**
- Learns a **ranking model** to recommend the most suitable jobs per candidate

The system is designed for real-world recruitment scenarios and supports **learning-to-rank** based recommendations.

---

## Project Pipeline

The project follows a structured, sequential ML pipeline:

1. **Job Data Collection**
2. **Video Feature Extraction (Audio + Visual)**
3. **Hard Skill Extraction & Matching (CV ↔ JD)**
4. **Soft Skill Annotation & Prediction**
5. **Scoring, Label Construction & Dataset Finalization**
6. **Learning-to-Rank Job Recommendation**

Each stage is implemented in a dedicated notebook.

---
## Repository Structure

```text
ML_Job_Recommendation_System/
│
├── Data/                   # Datasets (Raw, Processed, Final)
├── notebooks/              # ML Pipeline Stage Notebooks
├── src/                    # Source Code
│   ├── pipeline/           # Feature extraction logic
│   └── services/           # Business logic services
├── static/                 # Frontend static files (CSS, JS)
├── templates/              # Flask HTML templates
├── app.py                  # App factory
├── models.py               # Database models
├── route.py                # Flask routes
├── run.py                  # Entry point
├── setup.py                # Package setup
├── requirements.txt        # Dependencies
└── .env                    # Environment variables
```

---

## Getting Started

### Prerequisites
- Python 3.8+
- MySQL Server

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd jd
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration:**
   Create a `.env` file in the root directory and add your secrets:
   ```env
   SECRET_KEY=your_secret_key_here
   ```

5. **Database Setup:**
   - Create a MySQL database named `recommendation_system_db`.
   - Update the database URI in `app.py` if necessary.
   - Run migrations:
     ```bash
     flask db upgrade
     ```

### Running the Application

Start the Flask development server:
```bash
python run.py
```
The application will be available at `http://localhost:5500`.

---

## Machine Learning Pipeline

The project follows a structured, sequential ML pipeline:

1. **Job Data Collection**: Scraped from LinkedIn (Egypt).
2. **Video Feature Extraction**: Audio + Visual signals using VGG16.
3. **Hard Skill Extraction**: Pattern matching between CV and JD.
4. **Soft Skill Annotation**: Predicted from candidate videos.
5. **Scoring & Labeling**: Final dataset generation.
6. **Ranking Model**: Learning-to-Rank using Logistic Regression.

Each stage is documented in the `notebooks/` directory.
