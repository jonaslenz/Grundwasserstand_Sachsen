import streamlit as st
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
import urllib.request
from pyproj import Transformer

st.set_page_config(layout="wide")

Messstellen = pd.read_csv('https://www.umwelt.sachsen.de/umwelt/infosysteme/niwis/weitere/Export_MKZ_Uebersicht.csv',
                          sep=';',
                          thousands='.',
                          decimal=',',
                          index_col='MKZ')
c1, c2 = st.columns([0.3,0.7])

transformer = Transformer.from_crs("EPSG:25833", "EPSG:4326")

lat, lon = transformer.transform(Messstellen.RW_ETRS89, Messstellen.HW_ETRS89)

Messstellen['lat'] = lat
Messstellen['lon'] = lon

with c1:
  st.write(Messstellen)

with c2:
  st.map(data=Messstellen)
