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

To manually deploy this Streamlit application to Google Cloud Run, follow these steps:

1. **Package the Application**:
   Create a zip file containing the essential files (e.g., `app.py` or `Assign1_code.py`, `requirements.txt`, `Dockerfile`, and your GCP service account JSON key if required). 
   Let's assume the archive is named `deployment.zip`.

2. **Upload to Google Cloud Shell**:
   - Log into your [Google Cloud Console](https://console.cloud.google.com/).
   - Open **Cloud Shell** (the terminal icon at the top right).
   - Click the three dots (More) -> **Upload** and upload `deployment.zip`.

3. **Unzip and Navigate to the Directory**:
   Run the following commands in the Cloud Shell terminal:
   ```bash
   unzip deployment.zip
   cd deployment
   ```

4. **Deploy the Service**:
   Use the `gcloud` CLI to build and deploy the application in a single step (replace `mon-app-streamlit` with your desired app name):
   ```bash
   gcloud run deploy mon-app-streamlit \
     --source . \
     --region europe-west1 \
     --allow-unauthenticated
   ```
   *Follow the on-screen prompts to confirm the deployment. Once finished, Cloud Run will provide you with a public URL to access your application.*

---

## 🛠️ Local Development

1. Create a virtual environment and install the requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Set your Google Cloud credentials environment variable:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="[your_service_account_file].json"
   ```
3. Run the Streamlit app:
   ```bash
   streamlit run Assign1_code.py
   ```
# Movie_Database_Cloud_ana_assignment1
