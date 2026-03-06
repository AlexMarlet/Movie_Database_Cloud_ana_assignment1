# Cloud Analytics Assignment 1 - Streamlit Movie Database

## 📌 Project Overview
This project is an interactive movie database application built with Streamlit. It connects to a Google BigQuery dataset to fetch and display movie information, ratings, and integrates with the TMDB API to display movie posters and extended metadata.

### 🎯 Key Features and Exercise Requirements Met:
1. **Interactive Data Visualization & User Inputs**: 
   - We implemented dynamic search functionality using an autocomplete search box (`streamlit-searchbox`).
   - Advanced filtering options (Language, Genre, Release Year Range, Minimum Rating) allow users to interact with and query data seamlessly.
2. **Custom UI/UX & Aesthetics**: 
   - A custom dark purple glassmorphism theme was applied via CSS for a polished, modern look.
   - Movie posters are fetched from TMDB and displayed in an interactive 5-column grid.
3. **Detail View & External API Integration**:
   - Clicking on a movie poster seamlessly transitions the user to a detailed view showing plot, cast, crew, and external links, all dynamically fetched from TMDB.
4. **Cloud Database connection**:
   - Uses `google-cloud-bigquery` to securely execute dynamic SQL queries based on user inputs. The app handles BigQuery credentials and connection reliably.
5. **Cloud Deployment (Google Cloud Run)**:
   - Successfully containerized and deployed the application to Google Cloud Run to make it publicly accessible.

---

## 🚀 How to Deploy to Google Cloud Run

To manually deploy this Streamlit application to Google Cloud Run, i followed these steps:

1. **Package the Application**:
   Create a zip file containing the essential files (e.g., `app.py` or `Assign1_code.py`, `requirements.txt`, `Dockerfile`, and your GCP service account JSON key if required). 
   Let's assume the archive is named `deployment.zip`.

2. **Upload to Google Cloud Shell**
In Cloud Shell, i imported the zip file, unzip it with "unzip deployment.zip", then i deploy it by the following commands:
"
gcloud run deploy mon-app-streamlit \
  --source . \
  --region europe-west1 \
  --allow-unauthenticated
"
