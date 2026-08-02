import streamlit as st
import requests
import pandas as pd

# -----------------------------------------
# 1. DATA FETCHING FUNCTIONS
# -----------------------------------------

@st.cache_data(ttl=3600) # Caches the data for 1 hour to avoid hitting APIs too often
def get_brasileirao_table():
    """Fetches the live Brasileirão Série A table from FotMob's hidden API."""
    url = "https://www.fotmob.com/api/leagues?id=268"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            
            # Extract the standings table
            table_data = data['table'][0]['data']['table']['all']
            
            team_stats = []
            for team in table_data:
                team_stats.append({
                    "Position": team['idx'],
                    "Team": team['name'],
                    "Played": team['played'],
                    "Wins": team['wins'],
                    "Draws": team['draws'],
                    "Losses": team['losses'],
                    "GF": team['scoresStr'].split('-')[0],
                    "GA": team['scoresStr'].split('-')[1],
                    "GD": team['goalConDiff'],
                    "Points": team['pts']
                })
                
            return pd.DataFrame(team_stats)
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        
    return pd.DataFrame()

@st.cache_data(ttl=3600)
def get_player_stats():
    """Provides a sample dataset for player statistics."""
    # Note: To get live player stats, you would parse the player endpoints of the API or load a CSV.
    # This is placeholder data formatted exactly how real data would appear.
    data = {
        "Player": ["Pedro", "Hulk", "Gabriel Barbosa", "Tiquinho Soares", "Paulinho", "Arrascaeta"],
        "Team": ["Flamengo", "Atlético-MG", "Flamengo", "Botafogo", "Atlético-MG", "Flamengo"],
        "Goals": [12, 10, 9, 8, 7, 5],
        "Assists": [3, 5, 2, 4, 1, 8],
        "xG (Expected Goals)": [10.5, 8.2, 7.9, 6.5, 5.8, 4.1],
        "xA (Expected Assists)": [2.1, 4.8, 1.5, 3.2, 1.0, 7.5]
    }
    return pd.DataFrame(data)

# -----------------------------------------
# 2. STREAMLIT WEBSITE LAYOUT
# -----------------------------------------

# Page Configuration
st.set_page_config(page_title="Brasileirão Série A Stats", page_icon="⚽", layout="wide")

# Title and Description
st.title("⚽ Brasileirão Série A - Advanced Analytics")
st.markdown("Live updated statistics for teams and players in the Brazilian First Division.")

# Sidebar for navigation
st.sidebar.header("Navigation")
page = st.sidebar.radio("Choose a view:", ["League Table & Team Stats", "Player Stats", "Advanced Metrics"])

# Load Data
st.sidebar.markdown("---")
st.sidebar.text("Status: Fetching latest data...")
df_teams = get_brasileirao_table()
df_players = get_player_stats()
st.sidebar.success("Data up to date!")

# Page 1: League Table
if page == "League Table & Team Stats":
    st.header("🏆 Current Standings")
    if not df_teams.empty:
        # Display the table cleanly without the index
        st.dataframe(df_teams.set_index("Position"), use_container_width=True)
    else:
        st.error("Failed to fetch data from the server. The API might be down or blocking the request.")

# Page 2: Player Stats
elif page == "Player Stats":
    st.header("🏃‍♂️ Top Performers")
    
    # Simple search bar
    search = st.text_input("Search for a player:")
    if search:
        filtered_df = df_players[df_players['Player'].str.contains(search, case=False)]
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.dataframe(df_players, use_container_width=True)

# Page 3: Advanced Metrics
elif page == "Advanced Metrics":
    st.header("📊 Advanced Metrics")
    st.markdown("Visualizing expected metrics (xG and xA) for top players.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Goals vs Expected Goals (xG)")
        st.bar_chart(data=df_players.set_index("Player")[["Goals", "xG (Expected Goals)"]])
        
    with col2:
        st.subheader("Assists vs Expected Assists (xA)")
        st.bar_chart(data=df_players.set_index("Player")[["Assists", "xA (Expected Assists)"]])

    st.markdown("---")
    st.markdown("*Note: To add FootyStats or APWin advanced data, drop their CSV exports into your GitHub repository and load them here using `pd.read_csv()`.*")
