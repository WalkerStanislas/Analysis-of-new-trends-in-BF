# Importer les bibliothèques nécessaires
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import pyLDAvis
import pyLDAvis.gensim_models as gensimvis
import gensim
from gensim.corpora import Dictionary
from gensim.models import LdaModel
import ast
from wordcloud import WordCloud
import matplotlib.pyplot as plt

#######################
