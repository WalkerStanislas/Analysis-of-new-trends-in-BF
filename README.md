# 🌍 Analysis of New Trends in Burkina Faso 🇧🇫

This project uses **Natural Language Processing (NLP)** techniques to analyze **public sentiment** and detect **emerging trends** in **Burkina Faso** based on data extracted from social media, speacialy on faso.net web page in this use case.

---

## 🚀 Features

- 🔍 Web scraping from Faso.net pages
- 🧹 Preprocessing of scraped data
- 💬 Sentiment analysis using NLP
- 📊 Interactive dashboard with Streamlit
- 📆 Weekly trend tracking

---

## 🛠️ Installation

### 1. Clone the repository
```bash
git clone https://github.com/WalkerStanislas/Analysis-of-new-trends-in-BF.git
cd Analysis-of-new-trends-in-BF
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```
## 🕸️ Run Scraping Script
```bash
python "./Scraping & Analysis/scraping_script.py"
```
## 🧽 Pre-process the Data
Open the Jupyter Notebook file : processing.ipynb
Then:
#### ➡️ Run all cells step-by-step.
#### ✅ A clean CSV dataset named dataset_nlp.csv will be generated in the data_processed directory.

## ❤️ Sentiment Analysis
Open the Jupyter Notebook file : sentiment_analysis.ipynb Then:
#### This step will analyze the sentiments of the processed content.

## 🌐 Launch the Application
```bash
streamlit run ./App/app.py
```