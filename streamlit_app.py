import streamlit as st
import pandas as pd
from rapidfuzz import process, fuzz
import unicodedata

# Fonction pour normaliser les noms des produits
def normalize_text(text):
    text = text.lower()
    text = ''.join(
        c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn'
    )
    text = text.replace(".", "").replace("-", "").replace("!", "").strip()
    return text

# Fonction pour comparer les produits
def match_products(df1, df2, threshold=85):
    df1['Produit Normalisé'] = df1['Produit'].apply(normalize_text)
    df2['Produit Normalisé'] = df2['Produit'].apply(normalize_text)
    
    matches = []
    for index1, row1 in df1.iterrows():
        best_match, score, index2 = process.extractOne(row1['Produit Normalisé'], df2['Produit Normalisé'], scorer=fuzz.ratio)
        if score >= threshold:
            price_warning = "⚠️ Prix différent" if row1['Prix Unitaire'] != df2.loc[index2, 'Prix Unitaire'] else "✔️ Prix identique"
            matches.append({
                "Produit 1": row1['Produit'],
                "Prix Unitaire 1": row1['Prix Unitaire'],
                "Produit 2": df2.loc[index2, 'Produit'],
                "Prix Unitaire 2": df2.loc[index2, 'Prix Unitaire'],
                "Comparaison": price_warning
            })
    return pd.DataFrame(matches)

# Interface Streamlit
st.title("📊 Comparaison Automatique des Produits")

st.sidebar.header("📂 Charger les fichiers CSV")
uploaded_file1 = st.sidebar.file_uploader("Téléchargez le premier fichier CSV", type=["csv"])
uploaded_file2 = st.sidebar.file_uploader("Téléchargez le deuxième fichier CSV", type=["csv"])

if uploaded_file1 and uploaded_file2:
    df1 = pd.read_csv(uploaded_file1)
    df2 = pd.read_csv(uploaded_file2)
    
    st.subheader("🔍 Fichiers chargés")
    col1, col2 = st.columns(2)
    with col1:
        st.write("📄 Premier fichier")
        st.dataframe(df1.head())
    with col2:
        st.write("📄 Deuxième fichier")
        st.dataframe(df2.head())
    
    # Comparaison des produits
    st.subheader("🔬 Résultats de la comparaison")
    result_df = match_products(df1, df2)
    
    if not result_df.empty:
        st.dataframe(result_df)
    else:
        st.warning("Aucune correspondance trouvée avec un score élevé.")

    # Option pour télécharger les résultats
    csv_result = result_df.to_csv(index=False).encode('utf-8')
    st.download_button(label="📥 Télécharger les résultats", data=csv_result, file_name="resultat_comparaison.csv", mime="text/csv")
