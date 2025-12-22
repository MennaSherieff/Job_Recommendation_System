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
├── data/
│   ├── raw/               # Original scraped and collected data
│   ├── processed/          # Intermediate datasets
│   └── final/              # Final modeling-ready datasets
│
├── notebooks/
│   ├── 01_data_collection/
│   │   └── 01_linkedin_job_scraping_egypt.ipynb
│   │
│   ├── 02_feature_extraction/
│   │   ├── 02_1_audio_feature_extraction_from_video.ipynb
│   │   └── 02_2_visual_feature_extraction_vgg_frames.ipynb
│   │
│   ├── 03_skill_extraction_matching/
│   │   └── 03_jd_cv_hard_skill_extraction_and_matching.ipynb
│   │
│   ├── 04_soft_skill_modeling/
│   │   └── 04_soft_skill_annotation_and_prediction_model.ipynb
│   │
│   ├── 05_scoring_and_labeling/
│   │   └── 05_soft_skill_matching_scoring_and_label_generation.ipynb
│   │
│   └── 06_ranking_model/
│       └── 06_learning_to_rank_job_recommendation.ipynb
│
├── models/                 # Saved ML models
│
├── README.md
└── requirements.txt

