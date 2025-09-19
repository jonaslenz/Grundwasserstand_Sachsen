import streamlit as st
import pandas as pd
import numpy as np
import datetime
#import matplotlib.pyplot as plt
#import matplotlib.dates
from urllib.request import urlretrieve
from pyproj import Transformer
import os.path
#import seaborn as sns
#import plotly
#import plotly.tools as tls
import plotly.express as px

from DF_Filter import filter_dataframe 

st.set_page_config(layout="wide")

def cacheorload(filename):
  if not os.path.isfile('./cache/'+filename):
    url = ("https://www.umwelt.sachsen.de/umwelt/infosysteme/niwis/weitere/")
    urlretrieve(url+filename, './cache/'+filename)
  return

############################


cacheorload('Export_MKZ_Uebersicht.csv')
Messstellen = pd.read_csv('./cache/Export_MKZ_Uebersicht.csv',
                      sep=';',
                      thousands='.',
                      decimal=','
                      )

Mess_GWK = pd.read_csv('./MKZ_GWK.csv',
                      sep=';',
                      thousands='.',
                      decimal=',',
#                      index = "MKZ"
                      )
Mess_GWK = Mess_GWK.fillna("na")

Messstellen = Messstellen.merge(Mess_GWK, on = "MKZ")

c1, c2 = st.columns([0.3,0.7])

transformer = Transformer.from_crs("EPSG:25833", "EPSG:4326")

lat, lon = transformer.transform(Messstellen.RW_ETRS89, Messstellen.HW_ETRS89)

Messstellen['lat'] = lat
Messstellen['lon'] = lon

#st.write(Messstellen.columns.values)

with c1:
  columns = ['MKZ', 'Erstes_Messdatum', 'Letztes_Messdatum', 'GWK', 'GWK25', 'WRRL, 'RW_ETRS89', 'HW_ETRS89']
  df1 = pd.DataFrame(Messstellen, columns=columns)
  df1 = filter_dataframe(df1)
  event = st.dataframe(
        df1,
        width="stretch",
        on_select="rerun",
        hide_index = True,
        selection_mode="multi-row",
    )

  MKZs_ids = event.selection.rows

  MKZs = df1.loc[MKZs_ids, "MKZ"].tolist()
  
  Auswahl = Messstellen[Messstellen['MKZ'].isin(MKZs)]

#  st.write(MKZs)
#  st.write(Auswahl)
#  st.write(Messstellen.loc[MKZs, "MKZ"])
  st.map(data=Auswahl,
         use_container_width=True,
         height=200,
         zoom = 5)

with c2:
  if len(Auswahl.index) > 300:
    st.warning("Achtung, zuviel Daten in Darstellung ("+str(len(Auswahl.index)) +"), bitte maximal 300 Messstellen auswählen.")
    st.stop()
  if len(Auswahl.index) <= 0:
    st.warning("Bitte Messstellen auswählen.")
    st.stop()
  else:
    type = st.radio(label = "type", options = ["WERT_IM_HOEHENSYSTEM", "WERT_UNTER_GELAENDE"])


    for x in MKZs:
      cacheorload("ExportSN_GWS-Rohdaten_"+x+".csv")
      
      #dateparse = lambda x: datetime.datetime.strptime(x, '%Y-%m-%d')
      
      add = pd.read_csv('./cache/ExportSN_GWS-Rohdaten_'+x+'.csv',
                      sep=';',
                      thousands='.',
                      decimal=',',
       #               parse_dates=["MESSZEITPUNKT"],
        #              date_parser=dateparse,
                      )
      add['MESSZEITPUNKT'] = pd.to_datetime(add['MESSZEITPUNKT'], format='%Y-%m-%d')
      try:
        len(alle.index)
      except NameError:
        alle = add.copy()
      else:
        alle = pd.concat([alle, add])

    fig = px.line(alle, x="MESSZEITPUNKT",y=type, color = "MKZ", height=600)

    st.plotly_chart(fig)


