AI-Interview-Assistant/
│
├── app.py
├── requirements.txt
├── README.md
├── screenshots/
│   ├── home.png
│   ├── analysis.png
│   └── interview.png
└── assets/
 
 # 🤖 AI Interview Assistant

An AI-powered interview preparation platform built with Streamlit and Google's Gemini API.

The application analyzes resumes, generates personalized interview questions, and evaluates candidate responses using Large Language Models (LLMs).

---

## 📌 Project Overview

Preparing for technical interviews can be challenging because candidates often struggle to:

- Identify weaknesses in their resume
- Practice role-specific interview questions
- Receive meaningful feedback on answers

This project addresses these challenges by leveraging Google's Gemini AI model to create a personalized interview experience.

---

## 🚀 Features

### Resume Analysis

Upload a PDF or TXT resume and receive:

- Candidate Summary
- Key Skills Extraction
- Strength Analysis
- Interview Focus Areas

### AI Question Generation

Generate interview questions based on:

- Resume Content
- Target Job Role
- Difficulty Level

Question categories include:

- Technical Questions
- Behavioral Questions
- Problem Solving Questions

### AI Answer Evaluation

Each response is evaluated on:

- Technical Accuracy (0-10)
- Communication Skills (0-10)
- Confidence (0-10)

Detailed feedback is generated for improvement.

---

## 🏗 System Architecture

```text
User Resume
      │
      ▼
 PDF/TXT Parser
      │
      ▼
 Gemini API
      │
 ┌───────────────┐
 │ Resume Review │
 └───────────────┘
      │
      ▼
 Question Generator
      │
      ▼
 Candidate Answers
      │
      ▼
 AI Evaluation Engine
      │
      ▼
 Performance Feedback
