# %% [markdown]
# Ce notebook permet de faire la visualisation et faire un premier prétraitement des données afin de comprendre comment le dataset est structuré, quelles sont les premières conclusions que l'on peut tirer et quelles sont les premières étapes de prétraitement à effectuer.
# 
# Ce notebook est divisé en 3 parties :
# 1. **Visualisation des données** : on va visualiser les données pour comprendre comment elles sont structurées et quelles sont les informations qu'elles contiennent.
# 2. **Prétraitement des données** : on va effectuer un premier prétraitement des données pour les rendre plus faciles à manipuler.
# 3. **Analyse des données** : on va effectuer une analyse des données pour comprendre les relations entre les différentes variables et identifier les variables les plus importantes.
# 
# 

# %% [markdown]
# Import des librairies nécessaires

# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import statsmodels.api as sm
import os
import plotly.express as px
import plotly.graph_objects as go

# %% [markdown]
# Load Dataset

# %%
liste_fichiers = os.listdir("../dataset")
liste_fichiers = ["../dataset/"+f for f in liste_fichiers if f.endswith('.csv')]
print("Liste des fichiers disponibles :", liste_fichiers)

# %%
dataset_init = pd.read_csv(liste_fichiers[2], sep='~').rename(columns={'id':'id_film'})
liste_fichiers.pop(2)

# %%
for f in liste_fichiers:
    data_inter = pd.read_csv(f, sep='~')
    dataset_init = pd.merge(dataset_init, data_inter, on='id_film')


dataset_init.columns

# %% [markdown]
# Data cleaning : On enlève les colonnes en double ou bien les colonnes viides/qui n'apporte pas d'information
# 

# %%
dataset_init.dropna(axis=1, how='all', inplace=True)

# Gestion des colonnes dupliquées avec suffixes (_x et _y)
def clean_duplicate_columns(dataset_init):
    columns = dataset_init.columns
    columns_to_drop = []
    columns_to_rename = {}
    
    for col in columns:
        if col.endswith('_x') or col.endswith('_y'):
            base_col = col[:-2]  # Retirer le suffixe _x ou _y
            col_x = f"{base_col}_x"
            col_y = f"{base_col}_y"
            
            if col_x in dataset_init.columns and col_y in dataset_init.columns:
                # Fusionner en priorisant les valeurs non nulles
                dataset_init[base_col] = dataset_init[col_x].combine_first(dataset_init[col_y])
                columns_to_drop.extend([col_x, col_y])
                columns_to_rename[base_col] = base_col  # Normalisation
    
    dataset_init.drop(columns=columns_to_drop, inplace=True)
    dataset_init.rename(columns=columns_to_rename, inplace=True)
    return dataset_init

# Nettoyage des colonnes en double
dataset_init = clean_duplicate_columns(dataset_init)

# Affichage des colonnes finales
dataset_init.columns

# %%
print(len(dataset_init))

# %% [markdown]
# Visualisaton des données

# %% [markdown]
# Pour la visualisation nous allons voir la répartitions des films et comment ils 

# %%
# 1. Distribution des notes presse et spectateurs
# 11. Scatter des notes presse vs spectateurs
fig12 = px.scatter(dataset_init, x='note_presse', y='note_spectateurs', title="Note presse vs Note spectateurs")

# 12. Nombre moyen de critiques presse par catégorie
df_avg_presse = dataset_init.groupby('categorie')['nb_notes_presse'].mean().reset_index()
fig13 = px.bar(df_avg_presse, x='categorie', y='nb_notes_presse', title="Moyenne de critiques presse par catégorie")

# 13. Top 10 films avec le plus de notes spectateurs
top10_notes = dataset_init.nlargest(10, 'nb_notes_spectateurs')
fig14 = px.bar(top10_notes, x='titre', y='nb_notes_spectateurs', title="Top 10 films avec le plus de notes spectateurs")



# %%
# Conversion de la colonne "date" en format datetime si nécessaire
dataset_init["date"] = pd.to_datetime(dataset_init["date"], errors="coerce")

# Tri du DataFrame par date
dataset_init.sort_values("date", inplace=True)

# %%

fig15 = px.bar(dataset_init, x='date', y='note_spectateurs', title="Évolution des notes spectateurs dans le temps")

# %%
fig12.show()


# %%
fig13.show()


# %%
fig15.show()

# %%



