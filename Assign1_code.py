import streamlit as st
from google.cloud import bigquery
import pandas as pd
import requests
import os

# Set page configuration
st.set_page_config(page_title="Movie Database", layout="wide")

st.title("BigQuery Movie Database")

# Inject custom CSS for a blurred purple background
page_bg_css = """
<style>
/* Target the main app container for the background */
.stApp {
    background-color: #0d0614 !important; /* Very dark purple base */
    background-image: 
        radial-gradient(at 10% 20%, rgba(100, 40, 150, 0.4) 0px, transparent 50%),
        radial-gradient(at 90% 80%, rgba(70, 20, 120, 0.5) 0px, transparent 50%),
        radial-gradient(at 50% 50%, rgba(130, 50, 180, 0.2) 0px, transparent 60%) !important;
    background-attachment: fixed !important;
    color: #ffffff; /* Ensure text is readable */
}

/* Optional: slight transparency for the main content block and expanders for a glassmorphism effect */
.st-emotion-cache-1jicfl2, .st-emotion-cache-16txtl3, div[data-testid="stExpander"] > details {
    background-color: rgba(20, 10, 30, 0.6) !important;
    backdrop-filter: blur(10px) !important;
    border-radius: 10px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}
</style>
"""
st.markdown(page_bg_css, unsafe_allow_html=True)

# Initialize BigQuery client
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "eighth-sandbox-480216-t1-22241b4171f4.json"

@st.cache_resource
def get_bq_client():
    return bigquery.Client()

try:
    client = get_bq_client()
    # BigQuery client initialized successfully (hidden from user)
except Exception as e:
    st.error(f"Failed to initialize BigQuery client: {e}")
    st.info("Make sure you have set the GOOGLE_APPLICATION_CREDENTIALS environment variable pointing to your JSON key.")

# No title here, just the main page title above

# We need project ID and dataset earlier now for the autocomplete query
project_id = "eighth-sandbox-480216-t1"
dataset_id = "assignement1"

# Import the searchbox component
from streamlit_searchbox import st_searchbox

# Define the search function that queries BigQuery as the user types
def search_movies(searchterm: str):
    if not searchterm or len(searchterm) < 2:
        return []
    
    # Query BigQuery for title suggestions
    autocomplete_query = f"""
        SELECT DISTINCT title 
        FROM `{project_id}.{dataset_id}.movies` 
        WHERE LOWER(title) LIKE '%{searchterm.lower()}%'
        ORDER BY title
        LIMIT 10
    """
    try:
        suggestions_df = client.query(autocomplete_query).to_dataframe()
        if not suggestions_df.empty:
            return suggestions_df['title'].tolist()
        return []
    except Exception as e:
        print(f"Autocomplete error: {e}")
        return []

# === 1. User Inputs (UI) ===
st.markdown("### 🔎 Search Parameters")

# The autocomplete bar taking full width
selected_title = st_searchbox(
    search_function=search_movies,
    placeholder="Type a movie title (e.g. Batman)...",
    label="",
    clear_on_submit=False,
)
search_title = selected_title if selected_title else ""

# Advanced filters in an expander
with st.expander("⚙️ Advanced Filters", expanded=False):
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        languages = st.multiselect("Language", ["en", "fr", "es", "de", "hi", "ja"])
        search_genre = st.text_input("Genre", placeholder="e.g. Comedy")
    with col_f2:
        year_range = st.slider("Release Year Range", min_value=1890, max_value=2024, value=(1890, 2024))
        min_rating = st.slider("Minimum Average Rating", min_value=0.0, max_value=5.0, value=0.0, step=0.1)

st.write("") # Spacer

# === 2. Construct Query ===
# We will use the 'assignement1' dataset based on the previous test.
project_id = "eighth-sandbox-480216-t1"
dataset_id = "assignement1"

# Base query joining movies and ratings, grouping by movie properties to get avg rating
query = f"""
    SELECT 
        m.movieId,
        m.title,
        m.genres,
        m.tmdbId,
        m.language,
        m.release_year,
        AVG(r.rating) as avg_rating
    FROM `{project_id}.{dataset_id}.movies` m
    LEFT JOIN `{project_id}.{dataset_id}.ratings` r ON m.movieId = r.movieId
    WHERE 1=1
"""

# Dynamically append filters
if search_title:
    # Use LOWER for case-insensitive search
    query += f" AND LOWER(m.title) LIKE '%{search_title.lower()}%'"
    
if languages:
    # Create a string like ('en', 'fr')
    lang_str = ", ".join([f"'{lang}'" for lang in languages])
    query += f" AND m.language IN ({lang_str})"
    
if search_genre:
    query += f" AND LOWER(m.genres) LIKE '%{search_genre.lower()}%'"
    
query += f" AND m.release_year BETWEEN {year_range[0]} AND {year_range[1]}"

# Group by columns (everything selected except the aggregate avg_rating)
query += """
    GROUP BY 
        m.movieId, m.title, m.genres, m.tmdbId, m.language, m.release_year
"""

# Having clause for the average rating threshold
query += f" HAVING AVG(r.rating) >= {min_rating}"

# Order and limit
query += " ORDER BY avg_rating DESC, release_year DESC LIMIT 50"

# === 3. Execute Query & Display ===
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    search_clicked = st.button("🚀 Search Movies", use_container_width=True, type="primary")

# Run default query on first load to populate suggestions if nothing is in session state
if 'movie_results' not in st.session_state and not search_clicked:
    # First time loading: Force a default search with the widest parameters 
    # but ordered by rating and year to get modern good movies.
    search_clicked = True

if search_clicked:
    # REQUIRMENT: Display the executed SQL command in the terminal!
    print("----- EXECUTING SQL QUERY -----")
    print(query)
    print("-------------------------------")
    
    with st.spinner("Querying BigQuery..."):
        try:
            # Execute query and convert to pandas dataframe
            query_job = client.query(query)
            df = query_job.to_dataframe()
            
            if df.empty:
                st.warning("No movies found matching your criteria.")
            else:
                if 'movie_results' not in st.session_state:
                     st.write("### 🌟 Suggested Movies")
                else:
                     st.success(f"Found {len(df)} movies!")

                # Store the dataframe in session state so we don't lose it on widget interaction
                st.session_state['movie_results'] = df
                # Reset any selected movie from a previous search
                st.session_state['selected_movie_id'] = None
        except Exception as e:
            st.error(f"Error executing query: {e}")

# === 4. Display Results & Selected Movie Details ===
st.write("---")

TMDB_ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI5OTBmNjUwMTIxMGFmZTk2MWQ5OTAyY2ZhMWMzNjViMyIsIm5iZiI6MTc3MTUxNDk1NC41MDMsInN1YiI6IjY5OTcyYzRhNTk2YjIxZGJjYWM4NTVhMCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.vYci1WRYzk0N8aB_Rig2I2YiZRjKZFoxUmzaLLRf5WE"

@st.cache_data(show_spinner=False)
def get_movie_poster(tmdb_id):
    if pd.isna(tmdb_id) or tmdb_id == "": 
        return None
    api_url = f"https://api.themoviedb.org/3/movie/{int(tmdb_id)}"
    headers = {"accept": "application/json", "Authorization": f"Bearer {TMDB_ACCESS_TOKEN}"}
    try:
        res = requests.get(api_url, headers=headers, timeout=2)
        if res.status_code == 200:
            p_path = res.json().get('poster_path')
            if p_path: 
                return f"https://image.tmdb.org/t/p/w300{p_path}"
    except:
        pass
    return None

# Check if we have results in session state
if 'movie_results' in st.session_state and not st.session_state['movie_results'].empty:
    df_results = st.session_state['movie_results']
    
    # Initialize selected movie state if not present
    if 'selected_movie_id' not in st.session_state:
        st.session_state['selected_movie_id'] = None
        
    # --- GRID VIEW ---
    if st.session_state['selected_movie_id'] is None:
        st.write("### 🍿 Search Results")
        
        # Display as a grid, 5 columns
        num_cols = 5
        cols = st.columns(num_cols)
        
        # Adding a progress bar since fetching 50 posters can take a few seconds
        with st.spinner("Loading movie posters..."):
            displayed_items = 0
            for i in range(len(df_results)):
                row = df_results.iloc[i]
                poster_url = get_movie_poster(row['tmdbId'])
                
                # Only display if we successfully got a poster
                if poster_url:
                    col = cols[displayed_items % num_cols]
                    with col:
                        st.image(poster_url, use_container_width=True)
                        # Button underneath each poster
                        if st.button("Voir les détails", key=f"btn_{row['movieId']}", use_container_width=True):
                            st.session_state['selected_movie_id'] = row['movieId']
                            st.rerun()
                    displayed_items += 1
            
            if displayed_items == 0:
                st.info("Aucun des films trouvés ne possède d'affiche sur TMDB.")
                        
    # --- DETAILS VIEW ---
    else:
        if st.button("⬅️ Retour aux résultats"):
            st.session_state['selected_movie_id'] = None
            st.rerun()
            
        selected_movie = df_results[df_results['movieId'] == st.session_state['selected_movie_id']].iloc[0]
        
        st.markdown(f"## 🎬 {selected_movie['title']}")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Year", selected_movie['release_year'])
        c2.metric("Rating", f"{selected_movie['avg_rating']:.2f}/5.0")
        c3.metric("Language", selected_movie['language'].upper() if pd.notnull(selected_movie['language']) else "N/A")
        c4.metric("Genres", selected_movie['genres'].replace("|", ", ") if pd.notnull(selected_movie['genres']) else "N/A")
        
        st.write("---")
        
        tmdb_id = selected_movie['tmdbId']
        
        if pd.isna(tmdb_id) or tmdb_id == "":
            st.warning("No TMDB ID available for this movie in our database.")
        else:
            api_url = f"https://api.themoviedb.org/3/movie/{int(tmdb_id)}?append_to_response=credits"
            headers = {"accept": "application/json", "Authorization": f"Bearer {TMDB_ACCESS_TOKEN}"}
            
            with st.spinner("Fetching extended details from TMDB..."):
                try:
                    response = requests.get(api_url, headers=headers)
                    if response.status_code == 200:
                        movie_data = response.json()
                        col1, col2 = st.columns([1, 2])
                        
                        with col1:
                            poster_path = movie_data.get('poster_path')
                            if poster_path:
                                poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                                st.image(poster_url, width=250)
                            else:
                                st.write("No poster available")
                                
                        with col2:
                            st.write(f"**Tagline:** {movie_data.get('tagline', '')}")
                            st.write(f"**Plot:** {movie_data.get('overview', 'N/A')}")
                            st.write(f"**Runtime:** {movie_data.get('runtime', 'N/A')} minutes")
                            st.write(f"**TMDB Rating:** {movie_data.get('vote_average', 'N/A')}/10 ({movie_data.get('vote_count', 0)} votes)")
                            
                            credits = movie_data.get('credits', {})
                            directors = [crew['name'] for crew in credits.get('crew', []) if crew['job'] == 'Director']
                            st.write(f"**Director(s):** {', '.join(directors) if directors else 'N/A'}")
                            
                            cast = [actor['name'] for actor in credits.get('cast', [])[:5]]
                            st.write(f"**Top Cast:** {', '.join(cast) if cast else 'N/A'}")
                            
                            if movie_data.get('homepage'):
                                st.markdown(f"[Official Website]({movie_data.get('homepage')})")
                    else:
                        st.warning(f"Could not fetch details from TMDB. Status code: {response.status_code}")
                        st.error(response.text)
                except Exception as e:
                    st.error(f"Error fetching API details: {e}")

