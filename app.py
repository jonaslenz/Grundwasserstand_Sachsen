import streamlit as st
import pandas as pd
import numpy as np
#import matplotlib.pyplot as plt
#import matplotlib.dates
from urllib.request import urlretrieve
from pyproj import Transformer
import os.path
#import seaborn as sns
#import plotly
#import plotly.tools as tls
import plotly.express as px
from sklearn import linear_model

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

if not os.path.isfile('./MKZ_Trend.csv'):
    Mess_GWK["Trend"] = np.nan
else:
    Mess_Trend = pd.read_csv('./MKZ_Trend.csv')
    Mess_GWK = Mess_GWK.merge(Mess_Trend, on = "MKZ")

Messstellen = Messstellen.merge(Mess_GWK, on = "MKZ")

transformer = Transformer.from_crs("EPSG:25833", "EPSG:4326")

lat, lon = transformer.transform(Messstellen.RW_ETRS89, Messstellen.HW_ETRS89)

Messstellen['lat'] = lat
Messstellen['lon'] = lon

del lat, lon

#st.write(Messstellen.columns.values)
c1, c2 = st.columns([0.5,0.5])

with c1:
  columns = ['MKZ', 'Erstes_Messdatum', 'Letztes_Messdatum', 'GWK', 'GWK25', 'WRRL', 'RW_ETRS89', 'HW_ETRS89', 'Trend']
  df1 = pd.DataFrame(Messstellen, columns=columns)
  df1 = filter_dataframe(df1)
  with st.expander("Auswahliste", expanded=True):
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
  c1c1, c1c2 = st.columns([0.5,0.5])
  with c1c1:
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
    type = st.radio(label = "type",
                    options = ["WERT_IM_HOEHENSYSTEM", "WERT_UNTER_GELAENDE"],
                    horizontal = True)

# MKZs = Messstellen.iloc[1:5,].loc[:,"MKZ"].tolist() # Auswahl Messstellen auserhalb Streamlit
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

    if type == "WERT_UNTER_GELAENDE":
      fig['layout']['yaxis']['autorange'] = "reversed"

    st.plotly_chart(fig)

# Trendberechnung
    first_notice = True
    for z in MKZs:
        if pd.isna(Messstellen.loc[(Messstellen["MKZ"]==z, "Trend")]).values[0]:
        # if pd.isna(Messstellen["Trend"][Messstellen["MKZ"]==z]).values[0]:
            if first_notice:
                st.write("Trendberechnung erfolgt für "+str(len(MKZs))+" Messstellen ab Zeitraum 1995.")
                first_notice = False
    # Laden der Datenreihe
            add = pd.read_csv('./cache/ExportSN_GWS-Rohdaten_'+z+'.csv',
                              sep=';',
                              thousands='.',
                              decimal=',',
             #               parse_dates=["MESSZEITPUNKT"],
             #              date_parser=dateparse,
             )
            add['MESSZEITPUNKT'] = pd.to_datetime(add['MESSZEITPUNKT'], format='%Y-%m-%d')
            add = add.set_index('MESSZEITPUNKT')
            add = add.loc[:,"WERT_UNTER_GELAENDE"]
            add = add.dropna()
            add = add.loc[add.index>="1995"]
            if(add.shape[0]<=0):
                st.warning("fail on "+z)
                continue
#            if 

# Lineare Regression
            x = (add.index - add.index[0]).days.values.reshape(-1, 1) / 365 # /365 ändert die Zeitwerte von Tag auf Jahr
            y = add.values                                                  # Die WERT_UNTER_GELAENDE Werte sind in cm
            a = linear_model.LinearRegression().fit(x, y)
            linear_model.LinearRegression(copy_X=True, fit_intercept=True, n_jobs=1)

#            import matplotlib.pyplot as plt
#            y_pred = a.predict([[x.min()],[x.max()]])
#            plt.plot(x,y)
#            plt.plot([x.min(),x.max()],y_pred)
#            plt.text(0,y.min(), a.coef_)
#            plt.show()

# Berechnung Grimm Strele Trend
            Messstellen.loc[(Messstellen["MKZ"]==z, "Trend")] = -a.coef_ / (y.max()-y.min()) *100 # Anstieg in cm/a / Spannweite der cm --> Grimm-Strele Test

    Messstellen.loc[:,("MKZ","Trend")].to_csv('./MKZ_Trend.csv',
                                               index = False)
#    st.write("Trendberechnung beendet.")

#    Darstellung Histogram und Prozent
with c1c2:
    trends = Messstellen["Trend"].copy()
    trends = trends.dropna()
    fig2 = px.histogram(Messstellen, x="Trend", height=250)
    st.plotly_chart(fig2)
    if trends.shape[0]>=1:
        st.write("Anteil negativer Trend: "+
                 str(len(trends[trends<=-2]) / len(trends) * 100)+
                 "%.")
