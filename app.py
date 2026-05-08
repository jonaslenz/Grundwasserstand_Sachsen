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
import plotly.graph_objects as go

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
                      decimal=',',
                      dtype={'MKZ': "string"},
                      encoding='cp1252'
                      )

Mess_GWK = pd.read_csv('./MKZ_GWK.csv',
                      sep=';',
                      thousands='.',
                      decimal=',',
                      dtype={'MKZ': "string"},
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
  if st.toggle("Monatsbericht", value = False):
    monat = True
    MKZs = ['43420072','44406436','44416534','44416552','44425470','44429484',
'45400522','45400717','45416459','45426108','45430523','45440655',
'45460301','4639E0101','46410041','46410074','46410356','46420526',
'46421125','46430531','46436307','46450134','46460564','46460565',
'46460567','46470571','46510609','46530582','46553001','46553055',
'46553074','47390020','47400049','47410003','47410404','47410489',
'47420080','47420490','47430865','47431238','47440551','47440625',
'47440649','47450143','47450159','47456213','47460266','47460555',
'47491159','47510387','47528106','47553032','48390509','48391946',
'48400028','48410061','48410497','48410663','48420179','48420501',
'48421093','48421983','48440993','48500906','48511111','48518081',
'48530992','48531208','48553013','48553037','49400890','49410630',
'49410738','49411930','49420959','49430964','49441688','49461050',
'49483516','49510347','49520931','49530979','49531740','49540967',
'49541224','50420635','50420844','50431936','50453283','50550642',
'51410818','51431694','51481216','52393650','52403660','52403663',
'52410759','52411193','52411234','52411556','54393683','54393684',
'54393688','55403703','56393708','56393711','43425103','43435074',
'43435085','43435086','43435089','44416485','44416493','44416517',
'44426567','44533080','45406477','45410449','45416104','45420899',
'45426110','45426111','45426142','45431737','45445019','46390103',
'46391316','46400021','46400023','46400026','46410001','46410660',
'46411088','46420896','46420901','46431146','46434009','46440927',
'46441106','46441147','46450664','46451168','46460259','46460563',
'46471515','46491138','46500576','46500578','46501982','46513565',
'46521933','46553056','47410005','47410079','47411263','47440188',
'47450165','47450187','47451413','47470250','47470585','47480623',
'47481057','47481369','47481371','47490591','47490593','47500596',
'47520320','47520415','47530317','47533077','47543025','47543093',
'47553033','47553058','47553063','47553064','47563065','48391942',
'48411448','48411607','48421100','48430989','48431017','48431019',
'48431021','48431031','48431181','48431999','48441277','48450148',
'48450886','48451034','48451273','48461044','48461447','48470229',
'48470602','48471173','48471656','48473500','48480903','48481979',
'48483517','48491135','48511110','48520395','48520396','48520414',
'48540439','48540858','48543021','48543022','48553039','48553041',
'49391880','49410686','49411142','49411254','49411591','49411995',
'49420761','49420840','49451041','49451474','49461043','49470922',
'49471239','49483524','49483595','49483596','49483613','49484004',
'49484007','49490997','49510947','49511387','49520342','49530278',
'49530335','49550648','49551384','50420821','50420824','50421458',
'50431950','50441209','50491445','50491961','50530329','50540290',
'50540292','50550708','51400744','51410820','51410936','51433277',
'51546006','52393653','52400752','52403662','52403666','52410805',
'52431108','53393668','53393669','53401126','53403678','53420826',
'54383682','54393685','54396012','54403690','55393699','55393700',
'56383704','56393712','56401226']

  else:
  
    columns = ['MKZ', 'Erstes_Messdatum', 'Letztes_Messdatum', 'GWK', 'GWK25', 'WRRL', 'RW_ETRS89', 'HW_ETRS89']
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
                      encoding='cp1252',
                      dtype={'MKZ': "string"},
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

    if type == "WERT_IM_HOEHENSYSTEM":
      if st.checkbox("zeichne Filterlage"):
        nofilter = ""
        color_map = {trace.name: trace.line.color for trace in fig.data}
        for allex in MKZs:
          if pd.isna(Auswahl[Auswahl['MKZ']==allex]['FILTERUNTERKANTE'].item()):
            nofilter += allex+ "; "
            continue

          fig.add_trace(go.Scatter(
            x=[Auswahl[Auswahl['MKZ']==allex]['Erstes_Messdatum'].item(), Auswahl[Auswahl['MKZ']==allex]['Letztes_Messdatum'].item(),
               Auswahl[Auswahl['MKZ']==allex]['Letztes_Messdatum'].item(), Auswahl[Auswahl['MKZ']==allex]['Erstes_Messdatum'].item()],
            y=[Auswahl[Auswahl['MKZ']==allex]['FILTERUNTERKANTE'].item()]*2 + [Auswahl[Auswahl['MKZ']==allex]['FILTEROBERKANTE'].item()]*2,
            fill="toself",
            fillcolor=color_map.get(allex, "blue"),
            opacity=0.15,
            line=dict(width=0),
            showlegend=False,
            mode="lines",
            legendgroup=allex
          ))

        if nofilter != "":
          st.write("Keine Filterlageninformation bei: "+ nofilter)


    st.plotly_chart(fig)
  if monat:
    alle.index
    # 1. Monat aus dem Datum extrahieren (alternativ kann man auch resample verwenden)
    alle['Monat'] = alle['MESSZEITPUNKT'].dt.to_period('M')
    # 2. Nach Kategorie und Monat gruppieren und Mittelwert berechnen
    monatliche_mittel = alle.groupby(['MKZ', 'Monat'])['WERT_UNTER_GELAENDE'].mean().reset_index()
    st.write(monatliche_mittel)
    
    monatliche_mittel_NW = alle.groupby(['MKZ', 'Monat'])['WERT_UNTER_GELAENDE'].min().reset_index()
    st.write(monatliche_mittel_NW.head())

    monatliche_mittel.set_index('Monat', inplace=True)
    monatliche_mittel.index += pd.Timedelta(days=14)
    st.write(monatliche_mittel)
