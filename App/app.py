import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
import altair as alt
from pathlib import Path

# Configuration de la page
st.set_page_config(
    page_title="Analyse des Tendances d'Actualités",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fonction pour charger les données
@st.cache_data
def load_data():
    current_dir = Path(__file__).resolve().parent
    # Chargement des données d'analyse de sentiment
    csv_sentiment = current_dir.parent / 'Scraping & Analysis' / 'data_processed' / 'data_sentiment_finetuned_m.csv'
    sentiments_df = pd.read_csv(csv_sentiment)
    
    # Mapping des valeurs numériques vers des catégories de sentiment
    sentiment_mapping = {
        -1: "négatif",
        0: "neutre",
        1: "positif",
        "UNKNOWN": "unknown"
    }
    # Créer une colonne de sentiment textuel si nécessaire
    if 'sentiment' in sentiments_df.columns and pd.api.types.is_numeric_dtype(sentiments_df['sentiment']):
        sentiments_df['sentiment_text'] = sentiments_df['sentiment'].map(sentiment_mapping)
    else:
        sentiments_df['sentiment_text'] = sentiments_df['sentiment']
    
    # Chargement des données de topics
    csv_topics = current_dir.parent / 'Scraping & Analysis' / 'data_processed' / 'lda_topics.csv'
    topics_df = pd.read_csv(csv_topics)
    
    # Chargement des données de mots tendances
    csv_words = current_dir.parent / 'Scraping & Analysis' / 'data_processed' / 'mots_tendance.csv'
    trending_words_df = pd.read_csv(csv_words)
    # Assurer les noms de colonnes corrects
    if 'mot' in trending_words_df.columns and 'score' in trending_words_df.columns:
        trending_words_df = trending_words_df.rename(columns={'mot': 'word', 'score': 'frequency'})
    
    return sentiments_df, topics_df, trending_words_df

# Style CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #0D47A1;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #f8f9fa;
        box-shadow: 0 0.25rem 0.75rem rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1E88E5;
    }
    .metric-label {
        font-size: 1rem;
        color: #424242;
    }
</style>
""", unsafe_allow_html=True)

# En-tête principal
st.markdown('<div class="main-header">Analyse de Données Textuelles</div>', unsafe_allow_html=True)

# Barre latérale pour la navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Choisissez une page:",
    ["Tableau de bord", "Analyse des sentiments", "Modélisation des topics", "Mots tendances", "À propos"]
)

try:
    # Chargement des données
    sentiments_df, topics_df, trending_words_df = load_data()
    data_loaded = True
except Exception as e:
    st.error(f"Erreur lors du chargement des données: {e}")
    data_loaded = False
    st.stop()

# Page du tableau de bord principal
if page == "Tableau de bord":
    st.markdown('<div class="sub-header">Tableau de bord principal</div>', unsafe_allow_html=True)
    
    # Disposition en colonnes
    col1, col2, col3 = st.columns(3)
    
    # Métriques principales
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        total_docs = len(sentiments_df)
        st.markdown(f'<div class="metric-value">{total_docs:,}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Textes analysés</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        total_topics = len(topics_df)
        st.markdown(f'<div class="metric-value">{total_topics}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Thèmes identifiés</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        if 'sentiment_text' in sentiments_df.columns:
            sentiment_distribution = sentiments_df['sentiment_text'].value_counts()
            positive_ratio = sentiment_distribution.get('positif', 1) / len(sentiments_df) * 100
            st.markdown(f'<div class="metric-value">{positive_ratio:.1f}%</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Sentiments positifs</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="metric-value">N/A</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Données de sentiment non disponibles</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Graphiques résumés
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="sub-header">Distribution des Topics</div>', unsafe_allow_html=True)
        topic_counts = topics_df['topic_id'].value_counts().reset_index()
        topic_counts.columns = ['Topic', 'Count']
        
        fig = px.bar(
            topic_counts, 
            x='Topic', 
            y='Count',
            color='Count',
            color_continuous_scale='Blues',
            title="Distribution des Topics",
            labels={'Topic': 'Topic ID', 'Count': 'Nombre de documents'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown('<div class="sub-header">Analyse des Sentiments</div>', unsafe_allow_html=True)
        sentiment_col = 'sentiment_text' if 'sentiment_text' in sentiments_df.columns else 'sentiment'
        sentiment_counts = sentiments_df[sentiment_col].value_counts().reset_index()
        sentiment_counts.columns = ['Sentiment', 'Count']
        
        # Déterminer les catégories de sentiment
        if 'Sentiment' in sentiment_counts.columns:
            # Si les sentiments sont numériques, on les convertit en texte pour l'affichage
            sentiment_map = {0: 'négatif', 1: 'neutre', 2: 'positif'}
            if sentiment_counts['Sentiment'].dtype in [np.int64, np.float64]:
                sentiment_counts['Sentiment'] = sentiment_counts['Sentiment'].map(sentiment_map)
            
            # Définir les couleurs pour les sentiments
            colors = {'positif': '#4CAF50', 'neutre': '#FFC107', 'négatif': '#F44336'}
            
            fig = px.pie(
                sentiment_counts, 
                values='Count', 
                names='Sentiment', 
                title="Distribution des Sentiments",
                color='Sentiment',
                color_discrete_map=colors
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Données de sentiment non disponibles dans le format attendu.")
    
    # Top topics avec leurs mots-clés
    st.markdown('<div class="sub-header">Top Topics et leurs Mots-clés</div>', unsafe_allow_html=True)
    
    if 'topic_id' in topics_df.columns and 'topic_words' in topics_df.columns:
        # Préparer les données pour l'affichage
        top_topics = topics_df.head(5)  # Top 5 topics
        
        # Créer une table pour afficher les topics
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=['Topic ID', 'Mots-clés'],
                fill_color='#0D47A1',
                align='left',
                font=dict(color='white', size=12)
            ),
            cells=dict(
                values=[
                    top_topics['topic_id'],
                    top_topics['topic_words']
                ],
                fill_color='#f1f8fe',
                align='left',
                font=dict(size=11),
                height=30
            )
        )])
        fig.update_layout(height=250, margin=dict(l=5, r=5, t=5, b=5))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Format de données de topics non reconnu.")

# Page d'analyse des sentiments
elif page == "Analyse des sentiments":
    st.markdown('<div class="sub-header">Analyse détaillée des sentiments</div>', unsafe_allow_html=True)
    
    sentiment_col = 'sentiment_text' if 'sentiment_text' in sentiments_df.columns else 'sentiment'
    
    # Visualisations pour l'analyse des sentiments
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Distribution des sentiments")
        sentiment_counts = sentiments_df[sentiment_col].value_counts().reset_index()
        sentiment_counts.columns = ['Sentiment', 'Count']
        
        # Si les sentiments sont numériques, on les convertit en texte pour l'affichage
        sentiment_map = {0: 'négatif', 1: 'neutre', 2: 'positif'}
        if sentiment_counts['Sentiment'].dtype in [np.int64, np.float64]:
            sentiment_counts['Sentiment'] = sentiment_counts['Sentiment'].map(sentiment_map)
        
        colors = {'positif': '#4CAF50', 'neutre': '#FFC107', 'négatif': '#F44336', 'unknown': '#FFD347'}
        
        fig = px.bar(
            sentiment_counts,
            x='Sentiment',
            y='Count',
            color='Sentiment',
            color_discrete_map=colors,
            title="Distribution des sentiments"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Proportion des sentiments")
        fig = px.pie(
            sentiment_counts,
            values='Count',
            names='Sentiment',
            color='Sentiment',
            color_discrete_map=colors,
            title="Proportion des sentiments"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Si nous avons des données temporelles, montrer l'évolution des sentiments
    if 'date' in sentiments_df.columns:
        st.markdown("### Évolution des sentiments au fil du temps")
        
        # Préparer les données
        sentiments_df['date'] = pd.to_datetime(sentiments_df['date'])
        
        # Grouper par date et sentiment
        sentiments_over_time = sentiments_df.groupby([
            pd.Grouper(key='date', freq='D'), 
            sentiment_col
        ]).size().reset_index(name='count')
        
        # Si les sentiments sont numériques, les convertir en texte pour l'affichage
        if sentiments_over_time[sentiment_col].dtype in [np.int64, np.float64]:
            sentiments_over_time[sentiment_col] = sentiments_over_time[sentiment_col].map(sentiment_map)
        
        # Graphique d'évolution
        fig = px.line(
            sentiments_over_time,
            x='date',
            y='count',
            color=sentiment_col,
            color_discrete_map=colors,
            title="Évolution des sentiments au fil du temps"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Échantillon de textes pour chaque sentiment
    st.markdown("### Exemples de textes par sentiment")
    
    # Déterminer les sentiments uniques
    unique_sentiments = sentiments_df[sentiment_col].unique()
    if any(isinstance(s, (int, float)) for s in unique_sentiments):
        unique_sentiments = sorted([sentiment_map.get(s, str(s)) for s in unique_sentiments])
    else:
        unique_sentiments = sorted(unique_sentiments)
    
    sentiment_to_show = st.selectbox("Choisir un sentiment à explorer:", unique_sentiments)
    
    # Mapper le sentiment textuel au numérique si nécessaire
    if sentiment_to_show in ['positif', 'neutre', 'négatif', 'unknown']:
        reverse_map = {'négatif': -1, 'neutre': 0, 'positif': 1, 'unknown': 'UNKNOWN'}
        sentiment_value = reverse_map.get(sentiment_to_show, sentiment_to_show)
    else:
        sentiment_value = sentiment_to_show
    
    # Choisir la colonne de texte à afficher
    text_columns = ['normalized_text', 'text_processed', 'cleanned_text']
    text_column = next((col for col in text_columns if col in sentiments_df.columns), None)
    
    if text_column:
        # Filtrer les textes pour le sentiment sélectionné
        filter_col = 'sentiment' if 'sentiment_text' not in sentiments_df.columns else sentiment_col
        filtered_texts = sentiments_df[sentiments_df[filter_col] == sentiment_value][text_column].sample(
            min(5, len(sentiments_df[sentiments_df[filter_col] == sentiment_value]))
        ).tolist()
        
        for i, text in enumerate(filtered_texts):
            st.markdown(f"**Exemple {i+1}:** {text}")
    else:
        st.info("Les textes originaux ne sont pas disponibles dans les données.")

# Page de modélisation des topics
elif page == "Modélisation des topics":
    st.markdown('<div class="sub-header">Analyse détaillée des topics</div>', unsafe_allow_html=True)
    
    # Distribution des topics
    st.markdown("### Distribution des documents par topic")
    topic_counts = topics_df['topic_id'].value_counts().reset_index()
    topic_counts.columns = ['Topic', 'Count']
    
    fig = px.bar(
        topic_counts, 
        x='Topic', 
        y='Count',
        color='Count',
        color_continuous_scale='Viridis',
        title="Nombre de documents par topic"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Visualisation des topics et leurs mots-clés
    if 'topic_id' in topics_df.columns and 'topic_words' in topics_df.columns and 'topic_probs' in topics_df.columns:
        st.markdown("### Exploration des topics et leurs mots-clés")
        
        # Sélection du topic à explorer
        topic_to_explore = st.selectbox(
            "Choisissez un topic à explorer:",
            topics_df['topic_id'].unique()
        )
        
        # Afficher les mots-clés du topic sélectionné
        selected_topic = topics_df[topics_df['topic_id'] == topic_to_explore].iloc[0]
        words = selected_topic['topic_words'].split(', ')
        probs = [float(p) for p in selected_topic['topic_probs'].split(', ')]
        
        # Limiter aux 10 premiers mots pour une meilleure visualisation
        words = words[:10]
        probs = probs[:10]
        
        # Créer un DataFrame pour le graphique
        topic_words_df = pd.DataFrame({
            'Mot': words,
            'Probabilité': probs
        }).sort_values(by='Probabilité', ascending=False)
        
        # Graphique des mots-clés
        fig = px.bar(
            topic_words_df,
            x='Mot',
            y='Probabilité',
            color='Probabilité',
            color_continuous_scale='Blues',
            title=f"Mots-clés du Topic {topic_to_explore}"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Nuage de mots pour le topic
        st.markdown("### Nuage de mots du topic")
        
        word_freq = {word: prob for word, prob in zip(words, probs)}
        
        # Création du nuage de mots
        wc = WordCloud(
            background_color='white',
            width=800,
            height=400,
            max_words=100,
            colormap='viridis'
        ).generate_from_frequencies(word_freq)
        
        # Affichage du nuage de mots
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)
    else:
        st.warning("Le format des données de topics ne correspond pas à ce qui est attendu.")

# Page des mots tendances
elif page == "Mots tendances":
    st.markdown('<div class="sub-header">Analyse des mots tendances</div>', unsafe_allow_html=True)
    
    # Vérifier que les données des mots tendances ont le format attendu
    word_col = 'word' if 'word' in trending_words_df.columns else next((col for col in trending_words_df.columns if 'mot' in col.lower()), trending_words_df.columns[0])
    freq_col = 'frequency' if 'frequency' in trending_words_df.columns else next((col for col in trending_words_df.columns if 'freq' in col.lower() or 'score' in col.lower()), trending_words_df.columns[1])
    
    # Top mots tendances
    st.markdown("### Top mots tendances")
    
    # Limiter le nombre de mots à afficher
    top_n = st.slider("Nombre de mots à afficher:", 5, 50, 20)
    
    top_words = trending_words_df.sort_values(by=freq_col, ascending=False).head(top_n)
    
    # Graphique des mots tendances
    fig = px.bar(
        top_words,
        x=word_col,
        y=freq_col,
        color=freq_col,
        color_continuous_scale='Viridis',
        title=f"Top {top_n} mots tendances"
    )
    fig.update_layout(xaxis_title="Mot", yaxis_title="Fréquence/Score")
    st.plotly_chart(fig, use_container_width=True)
    
    # Nuage de mots pour les mots tendances
    st.markdown("### Nuage de mots tendances")
    
    word_freq = dict(zip(top_words[word_col], top_words[freq_col]))
    
    # Création du nuage de mots
    wc = WordCloud(
        background_color='white',
        width=800,
        height=400,
        max_words=100,
        colormap='plasma'
    ).generate_from_frequencies(word_freq)
    
    # Affichage du nuage de mots
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wc, interpolation='bilinear')
    ax.axis('off')
    st.pyplot(fig)
    
    # Si nous avons des données temporelles, montrer l'évolution des mots tendances
    if 'date' in trending_words_df.columns:
        st.markdown("### Évolution des mots tendances au fil du temps")
        
        # Sélection des mots à suivre
        words_to_track = st.multiselect(
            "Sélectionnez les mots à suivre:",
            trending_words_df[word_col].unique(),
            default=top_words[word_col].head(5).tolist()
        )
        
        if words_to_track:
            # Préparer les données
            trending_words_df['date'] = pd.to_datetime(trending_words_df['date'])
            filtered_df = trending_words_df[trending_words_df[word_col].isin(words_to_track)]
            
            # Graphique d'évolution
            fig = px.line(
                filtered_df,
                x='date',
                y=freq_col,
                color=word_col,
                title="Évolution des mots tendances au fil du temps"
            )
            st.plotly_chart(fig, use_container_width=True)

# Page À propos
elif page == "À propos":
    st.markdown('<div class="sub-header">À propos de cette application</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### Description de l'application
    
    Cette application a été développée pour analyser des données textuelles avec:
    
    - **Analyse des sentiments**: Visualisation de la distribution des sentiments dans le corpus
    - **Modélisation des topics**: Découverte et exploration des thématiques principales
    - **Analyse des mots tendances**: Identification des mots-clés les plus fréquents
    
    ### Comment utiliser l'application
    
    1. Utilisez la barre latérale pour naviguer entre les différentes pages
    2. Explorez les graphiques interactifs en survolant ou cliquant dessus
    3. Filtrez et sélectionnez les données qui vous intéressent
    
    ### Technologies utilisées
    
    - **Streamlit**: Framework pour le développement de l'interface web
    - **Pandas**: Manipulation et analyse des données
    - **Plotly**: Visualisations interactives
    - **WordCloud**: Génération des nuages de mots
    - **Matplotlib**: Visualisations statiques
    """)

    st.markdown("### Contact")
    st.markdown("Pour toute question ou suggestion concernant cette application, veuillez nous contacter à l'adresse suivante: walk.compaore@gmail.com")

# Pied de page
st.markdown("---")
st.markdown("© 2025 - Analyse des Tendances d'Actualités - Tous droits réservés")