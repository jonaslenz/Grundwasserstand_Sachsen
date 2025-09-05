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

st.write(Messstellen)
