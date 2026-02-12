import streamlit as st
import pandas as pd
import numpy as np
import datetime
import glob
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


Messstellen = Messstellen.merge(Mess_GWK, on = "MKZ", how = "outer")

Messstellen['Erstes_Messdatum'] = pd.to_datetime(Messstellen['Erstes_Messdatum'], format='%Y-%m-%d')
Messstellen['Letztes_Messdatum'] = pd.to_datetime(Messstellen['Letztes_Messdatum'], format='%Y-%m-%d')

transformer = Transformer.from_crs("EPSG:25833", "EPSG:4326")
lat, lon = transformer.transform(Messstellen.RW_ETRS89, Messstellen.HW_ETRS89)

Messstellen['lat'] = lat
Messstellen['lon'] = lon

del lat, lon

#st.write(Messstellen.columns.values)
c1, c2 = st.columns([0.4,0.6])

with c1:
  columns = ['MKZ', 'Erstes_Messdatum', 'Letztes_Messdatum',
             'GWK', 'GWK25', 'RW_ETRS89', 'HW_ETRS89',
             'MESSSTELLENART_ID', 'Netzart']
  df1 = pd.DataFrame(Messstellen, columns=columns)
  df1 = df1.fillna(-42)
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
  st.write("ausgewählt sind: "+
           str(len(Auswahl))+" Messstellen.")
  if len(Auswahl) > 0:
    st.write("Davon sind laut Styx "+
           str(len(Auswahl[Auswahl['GRIMM-STRELE'] <= -1]))+" fallend ("+
           str(round(len(
             Auswahl[Auswahl['GRIMM-STRELE'] <= -1])/len(Auswahl)*100))+"%).")
    with st.expander("fallende MKZS", expanded = False):
      Auswahl.MKZ[Auswahl['GRIMM-STRELE'] <= -1]

#  st.write(MKZs)
#  st.write(Auswahl)
#  st.write(Messstellen.loc[MKZs, "MKZ"])
  st.map(data=Auswahl,
             width="stretch",
             height=200,
             zoom = 5)


  ## Download / Löschen schon durchgeführter Trendanalysen
  files = glob.glob('Trend*')
  if(len(files) >0):
      filename = st.radio("Trendanalyse über alle MKZ zum Download", options = files)
      with open(filename, "rb") as file:
          st.download_button(
                label="Download",
                data=file,
                file_name=filename,
                mime="text/csv"
          )
      if st.button("Datei löschen"):
          os.remove(filename)
          st.rerun()

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
    with st.expander("Gangliniendarstellung mit allen Messzeitpunkten", expanded=True):
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
          add['WERT_UNTER_GELAENDE'] = add['WERT_UNTER_GELAENDE'].astype('Float64')
          add['MKZ'] = add['MKZ'].astype('string')
          try:
            len(alle.index)
          except NameError:
            alle = add.copy()
          else:
            alle = pd.concat([alle, add])
    
        fig = px.line(alle, x="MESSZEITPUNKT",y=type, color = "MKZ", height=500)
    
        if type == "WERT_UNTER_GELAENDE":
          fig['layout']['yaxis']['autorange'] = "reversed"
    
        st.plotly_chart(fig)
        alle["pred"] = "Messung"
    #    st.write(alle.head())

# Trendberechnung
    with st.expander("Trendberechnung - monatliche Mittelwerte", expanded=False):
        c2c1, c2c2, c2c3 = st.columns([0.4,0.4,0.2])
        with c2c1:
            st.write("Filter für Messstellen")
            Mindatum = st.date_input("Daten müssen seit mindestens vorliegen:",
                                 value = datetime.date(2010, 1, 1),
                                 min_value = datetime.date(1930, 1, 1),
                                 max_value = "today")
            
            Enddatum = st.date_input("Daten müssen bis mindestens vorliegen:",
                                 value = datetime.date(2023, 12, 31),
                                 min_value = datetime.date(1930, 1, 1),
                                 max_value = "today")
        # TrendAb = datetime.date(1995, 1, 1)
        # Enddatum = datetime.date(2024, 1, 1)
        with c2c2:
            st.write("Trend Zeitraum")
            TrendAb = st.date_input("Trend ab:",
                                   value = datetime.date(1995, 1, 1),
                                   min_value = datetime.date(1930, 1, 1),
                                   max_value = "today")
            TrendBis = st.date_input("Trend bis:",
                                   value = datetime.date(2025, 12, 31),
                                   min_value = datetime.date(1930, 1, 1),
                                   max_value = "today")
        with c2c3:    
           runtrend = st.button("Trend berechnen")
           runtrendall = st.button("Alle berechnen - keine Grafik, dauert")
        
        if runtrend or runtrendall:
            Messstellen["TrendFehler"] = ""
            first_notice = True
            if runtrendall:
                MKZs = Messstellen["MKZ"]
                counter = 1
                my_bar = st.progress(0., text="Bearbeitungsfortschritt")
            for z in MKZs:

                if first_notice:
                    st.write("Versuche Trendberechnung für "+str(len(MKZs))+" Messstellen seit "+str(TrendAb)+".")
                    first_notice = False
                if runtrendall:
                    if (counter % 10) == 0:
                        percent_complete = counter / len(MKZs)
                        my_bar.progress(percent_complete, text="Bearbeitungsfortschritt")
                    counter += 1

                if ((Messstellen.loc[
                        Messstellen["MKZ"]==z, "Letztes_Messdatum"] <
                        pd.to_datetime(Enddatum)).values[0]):
                    #st.warning("Zeitreihe zu früh zu Ende bei: "+z)
                    Messstellen.loc[(Messstellen["MKZ"]==z, "TrendFehler")] = "fail"
                    continue
                if ((Messstellen.loc[
                        Messstellen["MKZ"]==z, "Erstes_Messdatum"] >
                        pd.to_datetime(Mindatum)).values[0]):
                    #st.warning("Zeitreihe zu spät begonnen bei: "+z)
                    Messstellen.loc[(Messstellen["MKZ"]==z, "TrendFehler")] = "fail"
                    continue
            # Laden der Datenreihe
                cacheorload("ExportSN_GWS-Rohdaten_"+z+".csv")
                add = pd.read_csv('./cache/ExportSN_GWS-Rohdaten_'+z+'.csv',
                                     sep=';',
                                     thousands='.',
                                     decimal=',',
                     )
                add['WERT_UNTER_GELAENDE'] = add['WERT_UNTER_GELAENDE'].astype('Float64')
                add['MESSZEITPUNKT'] = pd.to_datetime(add['MESSZEITPUNKT'], format='%Y-%m-%d')
                add = add.set_index('MESSZEITPUNKT')
                add = add.loc[:,"WERT_UNTER_GELAENDE"]
                add = add.resample('MS').mean()
                add = add.dropna()
#                st.write(add)
                add = add.loc[add.index>=pd.to_datetime(TrendAb)]
                add = add.loc[add.index<=pd.to_datetime(TrendBis)]
                if(add.shape[0]<=0):
                    #st.warning("Keine Daten bei: "+z)
                    Messstellen.loc[(Messstellen["MKZ"]==z, "TrendFehler")] = "fail"
                    continue

        # Lineare Regression
                x = (add.index - add.index[0]).days.values.reshape(-1, 1) / 365 # /365 ändert die Zeitwerte von Tag auf Jahr
                y = add.values                                                  # Die WERT_UNTER_GELAENDE Werte sind in cm
                a = linear_model.LinearRegression().fit(x, y)
                linear_model.LinearRegression(copy_X=True, fit_intercept=True, n_jobs=1)


        # Berechnung Grimm Strele Trendwerte und Anfügen an Dataframe
                Messstellen.loc[(Messstellen["MKZ"]==z, "Trend Grimm Strele")] = -a.coef_ / (y.max()-y.min()) *100 # Anstieg in cm/a / Spannweite der cm --> Grimm-Strele Test
                Messstellen.loc[(Messstellen["MKZ"]==z, "Anstieg Regression")] = -a.coef_  # Anstieg in cm/a
                Messstellen.loc[(Messstellen["MKZ"]==z, "Spanne")] = y.max()-y.min() # Spannweite der cm
                Messstellen.loc[(Messstellen["MKZ"]==z, "Anzahl Werte")] = len(y) # Anzahl der Werte
                Turnus = np.median(np.diff([xss for xs in x for xss in xs]))*365
                Messstellen.loc[(Messstellen["MKZ"]==z, "Messturnus [Tage] geschätzt")] = Turnus # Anzahl der Werte
                
        # Darstellung der Regressionsgeraden im Plot
                if runtrend:
                    try:
                      len(alle.index)
                    except NameError:
                      alle = add.copy()
                    else:
                      alle = pd.concat([alle, add])
                    # Hinzufügen der Regressionsgeraden zu dataframe mit allen Messstellenwerten
                    pred = alle.iloc[0:2,].copy()
                    pred.loc[0,"MKZ"] = z
                    pred.loc[0,"MESSZEITPUNKT"] = add.index[0]
                    pred.loc[0,"WERT_UNTER_GELAENDE"] = a.predict([[x.min()]])[0]
                    pred.loc[0,"pred"] = "Trend"

                    pred.loc[1,"MKZ"] = z
                    pred.loc[1,"MESSZEITPUNKT"] = add.index[-1]
                    pred.loc[1,"WERT_UNTER_GELAENDE"] = a.predict([[x.max()]])[0]
                    pred.loc[1,"pred"] = "Trend"

                    alle = pd.concat([alle, pred])

            #        plt.plot(x,y)
            #        plt.plot([x.min(),x.max()],y_pred)
            #        plt.text(0,y.min(), a.coef_)
            #        plt.show()

        if runtrend:
            fig = px.line(alle,
                          x="MESSZEITPUNKT",
                          y="WERT_UNTER_GELAENDE",
                          line_dash = "pred",
                          color = "MKZ",
                          height=500
                          )
            fig['layout']['yaxis']['autorange'] = "reversed"
            st.plotly_chart(fig)

            #    Darstellung Histogram und Prozent
            trends = Messstellen["Trend Grimm Strele"].copy()
            trends = trends.dropna()
            fig2 = px.histogram(Messstellen, x="Trend Grimm Strele", height=250)
            st.plotly_chart(fig2)
            if trends.shape[0]>=1:
                st.write("Anteil negativer Trend laut Streamlit: "+
                         str(round(len(trends[trends<=-1]) / len(trends) * 100))+
                         "% von "+
                         str(len(trends))+" Messstellen.")
            st.write(Messstellen[Messstellen['MKZ'].isin(MKZs)])

        if runtrendall:

            Messstellen.to_excel("Trendanalyse_"+
                                 datetime.datetime.now().strftime("%Y%m%d_%H%M")+
                                 "_TrendAb"+str(TrendAb)+
                                 "_TrendBis"+str(TrendBis)+
                                 "_DatenAb"+str(Mindatum)+
                                 "_DatenBis"+str(Enddatum)+
                                 ".xlsx",
                                 index = False)
            my_bar.empty()
            st.write("Tabelle zum Download bereit.")
            st.rerun()
