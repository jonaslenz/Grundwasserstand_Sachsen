import streamlit as st
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt

Messstellen = pd.read_csv('https://www.umwelt.sachsen.de/umwelt/infosysteme/niwis/weitere/Export_MKZ_Uebersicht.csv',
                          sep=';',
                          thousands='.',
                          decimal=',',
                          index_col='MKZ')
c1, c2 = st.columns([0.3,0.7])

with c1:
  st.write(Messstellen)

with c2:
  st.map(data=Messstellen, latitude='RW_ETRS89', longitude='HW_ETRS89')
