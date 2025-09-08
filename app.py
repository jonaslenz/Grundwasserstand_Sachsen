import streamlit as st
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates
from urllib.request import urlretrieve
from pyproj import Transformer
import os.path
import seaborn as sns
import plotly
import plotly.tools as tls


st.set_page_config(layout="wide")

def cacheorload(filename):
  if not os.path.isfile('./cache/'+filename):
    url = ("https://www.umwelt.sachsen.de/umwelt/infosysteme/niwis/weitere/")
    urlretrieve(url+filename, './cache/'+filename)
  return


cacheorload('Export_MKZ_Uebersicht.csv')
Messstellen = pd.read_csv('./cache/Export_MKZ_Uebersicht.csv',
                      sep=';',
                      thousands='.',
                      decimal=','
                      )

c1, c2 = st.columns([0.2,0.8])

transformer = Transformer.from_crs("EPSG:25833", "EPSG:4326")

lat, lon = transformer.transform(Messstellen.RW_ETRS89, Messstellen.HW_ETRS89)

Messstellen['lat'] = lat
Messstellen['lon'] = lon

#st.write(Messstellen.columns.values)

with c1:
  columns = ['MKZ', 'Erstes_Messdatum', 'Letztes_Messdatum']
  df1 = pd.DataFrame(Messstellen, columns=columns)
  event = st.dataframe(
        df1,
        use_container_width=True,
        on_select="rerun",
        hide_index = True,
        selection_mode="multi-row",
    )

  MKZs = event.selection.rows

#  st.write(MKZs)
#  st.write(Messstellen.loc[MKZs, "MKZ"])
  st.map(data=Messstellen.iloc[MKZs])

with c2:
  if st.checkbox("Zeige Diagramm"):
    type = st.radio(label = "type", options = ["WERT_IM_HOEHENSYSTEM", "WERT_UNTER_GELAENDE"])
    series = {}
    
    fig, ax = plt.subplots()
    
    for x in Messstellen.loc[MKZs, "MKZ"]:
      # st.write(x)
      cacheorload("ExportSN_GWS-Rohdaten_"+x+".csv")
      
      dateparse = lambda x: datetime.datetime.strptime(x, '%Y-%m-%d')

      series[x] = pd.read_csv('./cache/ExportSN_GWS-Rohdaten_'+x+'.csv',
                      sep=';',
                      thousands='.',
                      decimal=',',
                      parse_dates=["MESSZEITPUNKT"],
                      date_parser=dateparse,
                      index_col = "MESSZEITPUNKT"
                      )

      sns.lineplot(x="MESSZEITPUNKT",y=type, data = series[x], label = x)
#    st.write(series)
    plotly_fig = tls.mpl_to_plotly(fig)
    st.plotly_chart(plotly_fig)
#    st.pyplot(fig)

    
