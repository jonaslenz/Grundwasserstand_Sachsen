#######################################################
# --- PAKET-MANAGEMENT (Überarbeitung 16.02.2026) ---
#######################################################

library(ggplot2)
library(dplyr)
library(tibble)
library(magrittr)
library(ragg)
library(farver)
library(tidyr)
library(lubridate)
library(svglite)


for (MKZ in c(
'43420072','44406436','44416534','44416552','44425470','44429484',
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
'56383704','56393712','56401226'
))
{
  Styxexport <- read.csv2(paste0("./cache/ExportSN_GWS-Rohdaten_",MKZ,".csv"))

  ### set format
  Styxexport$MKZ <- as.character(Styxexport$MKZ)
  Styxexport$MESSZEITPUNKT <- as.Date(Styxexport$MESSZEITPUNKT, format = "%Y-%m-%d")
  Styxexport$JAHR <- strftime(Styxexport$MESSZEITPUNKT, "%Y")
  Styxexport$MONAT_Nr <- strftime(Styxexport$MESSZEITPUNKT, "%m")
  Styxexport$MONAT <- strftime(Styxexport$MESSZEITPUNKT, "%b")
  Styxexport$GWS <- Styxexport$`WERT_UNTER_GELAENDE`
  Styxexport <- Styxexport[c("MKZ","JAHR","MONAT_Nr","MONAT","GWS")]
  
  if (exists("alle"))
  {
    alle <- rbind(alle, Styxexport)
  }
  else(
    alle <- Styxexport
  )
  rm(Styxexport)
}

# Hartes schreiben der deutschen Monate, da kein deutsches locale auf streamlit 
alle$MONAT[alle$MONAT_Nr == 1] <- "Jan"
alle$MONAT[alle$MONAT_Nr == 2] <- "Feb"
alle$MONAT[alle$MONAT_Nr == 3] <- "Mrz"
alle$MONAT[alle$MONAT_Nr == 4] <- "Apr"
alle$MONAT[alle$MONAT_Nr == 5] <- "Mai"
alle$MONAT[alle$MONAT_Nr == 6] <- "Jun"
alle$MONAT[alle$MONAT_Nr == 7] <- "Jul"
alle$MONAT[alle$MONAT_Nr == 8] <- "Aug"
alle$MONAT[alle$MONAT_Nr == 9] <- "Sep"
alle$MONAT[alle$MONAT_Nr == 10] <- "Okt"
alle$MONAT[alle$MONAT_Nr == 11] <- "Nov"
alle$MONAT[alle$MONAT_Nr == 12] <- "Dez"


### check wie viele einzelne GWM
MKZ_Liste <- unique(alle$MKZ)

### Mittelwert/MKZ,Jahr,Monat
mean_MKZ<- aggregate(GWS~ MKZ+JAHR+MONAT_Nr+MONAT, data = alle, FUN = mean)
#mean_MKZ$JAHR<-as.character(mean_MKZ$JAHR)
mean_MKZ$TAG <- "15"
mean_MKZ$DATUM <- paste(mean_MKZ$TAG,mean_MKZ$MONAT_Nr,mean_MKZ$JAHR, sep="-")
mean_MKZ$DATUM <- as.Date(mean_MKZ$DATUM, format = "%d-%m-%Y")

###############################################################################################################################################
### Anzahl GWM einzelner Monate prüfen
GWM_Vormonat <-  unique(filter(mean_MKZ, JAHR=="2026" & MONAT_Nr=="03")) #<---------------------------------------------Vormonat eingeben
GWM_lfd_Monat <-unique(filter(mean_MKZ, JAHR=="2026" & MONAT_Nr=="04")) #<----------------------------------------------laufenden Monat eingeben (letzter voller Berichtsmonat)
print("Anzahl GWM prüfen")
Anzahl_GWM_Vormonat <- length(unique(GWM_Vormonat$MKZ))
Anzahl_GWM_lfd_Monat <- length(unique(GWM_lfd_Monat$MKZ))

### Anzahl GMW pro Jahr und Monat (vollständig für alle Zeiträume)
Anzahl_GMW <- mean_MKZ %>%
  group_by(JAHR, MONAT) %>%
  summarise(
    Anzahl_GMW = n_distinct(MKZ),
    .groups = "drop"
  )

### 3.Tabelle: Mittelwerte/Jahr,Monat
Monatsmittel0 <- aggregate(GWS~ JAHR+MONAT+DATUM, data = mean_MKZ, FUN = mean)

### Anzahl GMW an Monatsmittel anhängen
Monatsmittel0 <- Monatsmittel0 %>%
  left_join(Anzahl_GMW, by = c("JAHR", "MONAT"))


### 
#Monatsmittel_2019 <- dplyr::filter(Monatsmittel0, DATUM >= "2018-11-01" & DATUM <= "2019-10-31")
#Monatsmittel_2020 <- dplyr::filter(Monatsmittel0, DATUM >= "2019-11-01" & DATUM <= "2020-10-31")
#Monatsmittel_2021 <- dplyr::filter(Monatsmittel0, DATUM >= "2020-11-01" & DATUM <= "2021-10-31")
#Monatsmittel_2022 <- dplyr::filter(Monatsmittel0, DATUM >= "2021-11-01" & DATUM <= "2022-10-31")
#Monatsmittel_2023 <- dplyr::filter(Monatsmittel0, DATUM >= "2022-11-01" & DATUM <= "2023-10-31")
#Monatsmittel_2024 <- dplyr::filter(Monatsmittel0, DATUM >= "2023-11-01" & DATUM <= "2024-10-31")
Monatsmittel_2025 <- dplyr::filter(Monatsmittel0, DATUM >= "2024-11-01" & DATUM <= "2025-10-31")
Monatsmittel_2026 <- dplyr::filter(Monatsmittel0, DATUM >= "2025-11-01" & DATUM <= "2026-04-30") #<------------------------------laufenden Monat wg. Datengrundlage (letzter voller Berichtsmonat)

### mehrjähriges Monatsmittel mit Quantilsbereich #for 50 years
#Monatsmittel <- filter(Monatsmittel, JAHR %in% (1969:2021)) # old
Monatsmittel <- dplyr::filter(Monatsmittel0, DATUM >= "1970-11-01" & DATUM <= "2025-10-31") #50 Abflussjahre Rücksprache mit UM bzw. bis aktuell

calc_Quantile <- aggregate(GWS~ MONAT, data = Monatsmittel, FUN = quantile)
calc_Mean <- aggregate(GWS~ MONAT, data = Monatsmittel, FUN = mean)

draw_Quantile <- as.data.frame(cbind(calc_Quantile$MONAT,
                                     calc_Quantile$GWS[,"0%"],
                                     calc_Quantile$GWS[,"25%"],
                                     calc_Quantile$GWS[,"50%"],
                                     calc_Mean$GWS,
                                     calc_Quantile$GWS[,"75%"],
                                     calc_Quantile$GWS[,"100%"]))

colnames(draw_Quantile) <- c("MONAT","Q0","Q25","Q50","mean0","Q75","Q100")
draw_Quantile$Q0 <- as.numeric(draw_Quantile$Q0)
draw_Quantile$Q25 <- as.numeric(draw_Quantile$Q25)
draw_Quantile$Q50 <- as.numeric(draw_Quantile$Q50)
draw_Quantile$mean0 <- as.numeric(draw_Quantile$mean0)
draw_Quantile$Q75 <- as.numeric(draw_Quantile$Q75)
draw_Quantile$Q100 <- as.numeric(draw_Quantile$Q100)

#####################################################################
### prep
Jahresablauf <- c("Nov","Dez","Jan","Feb","Mrz","Apr","Mai","Jun","Jul","Aug","Sep","Okt")

### create plot
Plot_GWStand <- ggplot(data=draw_Quantile, aes(x=factor(MONAT, level=Jahresablauf), y=mean0, group=1)) +
  geom_ribbon(data=draw_Quantile, linetype="blank", aes(ymin = Q25, ymax = Q75, fill="Quantilsbereich Q25-Q75"), alpha=0.4) +
  geom_ribbon(data=draw_Quantile, aes(x=MONAT, ymin=Q100, ymax=Q75, fill="Quantilsbereich Q75-Q100"), alpha=0.3)  +
  geom_ribbon(data=draw_Quantile, aes(x=MONAT, ymin=Q0, ymax=Q25, fill="Quantilsbereich Q0-Q25"), alpha=0.3)  +
#  geom_line(data = Monatsmittel_2019, linewidth=1.0, linetype="solid", aes(x=MONAT, y=GWS, color="Abflussjahr 2019", linetype="2019")) +
#  geom_line(data = Monatsmittel_2020, linewidth=1.0, linetype="solid", aes(x=MONAT, y=GWS, color="Abflussjahr 2020", linetype="2020")) +
#  geom_line(data = Monatsmittel_2021, linewidth=1.0, linetype="solid", aes(x=MONAT, y=GWS, color="Abflussjahr 2021", linetype="2021")) +
#  geom_line(data = Monatsmittel_2022, linewidth=1.0, linetype="solid", aes(x=MONAT, y=GWS, color="Abflussjahr 2022", linetype="2022")) +
#  geom_line(data = Monatsmittel_2023, linewidth=1.0, linetype="solid", aes(x=MONAT, y=GWS, color="Abflussjahr 2023", linetype="2023")) +
#  geom_line(data = Monatsmittel_2024, linewidth=1.5, linetype="solid", aes(x=MONAT, y=GWS, color="Abflussjahr 2024", linetype="2024")) +
  geom_line(data = Monatsmittel_2025, linewidth=1.5, linetype="solid", aes(x=MONAT, y=GWS, color="Abflussjahr 2025", linetype="2025")) +
  geom_line(data = Monatsmittel_2026, linewidth=1.5, linetype="solid", aes(x=MONAT, y=GWS, color="Abflussjahr 2026", linetype="2026")) +
#  geom_point(data = Monatsmittel_2026, size=3, aes(x=MONAT, y=GWS, color="Abflussjahr 2026")) +                                          #nur für November, da noch kein Mittelwert möglich ist
  geom_line(data = draw_Quantile, linewidth=1., color= "black", aes(x=MONAT, y=mean0, linetype="mehrjähriges Monatsmittel")) +
  geom_line(data = draw_Quantile, linewidth=1., color= "black", aes(x=MONAT, y=Q100, linetype="mehrjähriges Monatsminimum")) +
  geom_line(data = draw_Quantile, linewidth=1., color= "black", aes(x=MONAT, y=Q0, linetype="mehrjähriges Monatsmaximum")) +
  labs(x = "", y = "Mittlerer Grundwasserstand\nunter Geländeoberkante [cm]", 
       title = "Mittlerer Grundwasserstand",
       caption= "© LfULG") +
  scale_y_reverse(limits=c(575,350), breaks=seq(700,200,-50)) +
  scale_x_discrete() +
  scale_fill_manual("", 
                    values = c("Quantilsbereich Q25-Q75" = "gray75",
                               "Quantilsbereich Q75-Q100" = "saddlebrown",
                               "Quantilsbereich Q0-Q25" = "steelblue3")) +
  scale_linetype_manual("", 
                        breaks = c("mehrjähriges Monatsmittel", "mehrjähriges Monatsmaximum", "mehrjähriges Monatsminimum"),
                        values = c("mehrjähriges Monatsmittel" = "dotted", "mehrjähriges Monatsmaximum" = "dashed", "mehrjähriges Monatsminimum" = "dotdash")) +
  scale_colour_manual("", 
                      breaks = c("Abflussjahr 2019","Abflussjahr 2020", "Abflussjahr 2021", "Abflussjahr 2022", "Abflussjahr 2023", "Abflussjahr 2024", "Abflussjahr 2025", "Abflussjahr 2026"),
                      values = c("Abflussjahr 2019" = "gray40", "Abflussjahr 2020" = "orange", "Abflussjahr 2021" = "purple2", "Abflussjahr 2022" = "olivedrab", "Abflussjahr 2023" = "skyblue1", "Abflussjahr 2024" = "pink2", "Abflussjahr 2025" = "yellowgreen", "Abflussjahr 2026" = "orange")) +
  theme(legend.position = "bottom",
        legend.box = "vertical",
        legend.box.background = element_rect(),
        legend.box.margin = margin(t = 0.1, r = 0.1, b = 0.1, l = 0.1, unit = "cm"),
        legend.text = element_text(size=15),
        legend.spacing = unit(0,'cm'),
        plot.background = element_rect(fill = "gray93"),
        plot.margin = margin(0.5,0.5,0.1,0.2, "cm"),
        plot.title = element_text(size=24, face="bold", hjust=0.5),
        plot.caption = element_text(size=16, color = "gray65"),
        axis.text = element_text(size=16),
        axis.title = element_text(size=17),
        panel.background = element_rect(fill = "white", colour = "grey50"),
        panel.spacing.y = unit(6, "cm"),
        panel.grid.major.x = element_line(colour = "grey70"),
        panel.grid.major.y = element_line(colour = "grey70"),
        panel.grid.minor.y = element_line(colour = "grey70"),
        legend.key = element_rect(fill = "white", color= "white"),
        legend.key.width= unit(1., 'cm'),
        legend.key.height= unit(0.2, 'cm'))
Plot_GWStand


### save plot as png
filename <- paste0("GWS_sachsenweit_",format(Sys.time(), "%Y%m%d"),".png")
png(file = filename, width = 850, height = 570)
Plot_GWStand
dev.off()

# ### adds
# # Colorblind-palette: "#96D005", "#785EF0", "#FE6100"
# 
# ### manchmal Exporte für UM
# # Monatsmittel zusammenführen
# Monatsmittel_export <- bind_rows(Monatsmittel, Monatsmittel_2025, Monatsmittel_2026) %>%
#   distinct(JAHR, MONAT, DATUM, .keep_all = TRUE) %>%
#   arrange(DATUM)
# 
# # Erstellt vollständige Tabelle für das Quantil-Sheet mit Jahres- und Datumsinfos + Quantilen
# quantile_export <- Monatsmittel_export %>%
#   select(JAHR, MONAT, DATUM) %>%
#   distinct() %>%
#   left_join(draw_Quantile, by = "MONAT")
# quantile_export <- quantile_export %>%
#   left_join(
#     Monatsmittel_export %>%
#       group_by(JAHR, MONAT) %>%
#       summarise(Anzahl = n(), .groups = "drop"),
#     by = c("JAHR", "MONAT")
#   )
# 
# 
# # exportiert eine Excel-Datei mit zwei Arbeitsblättern 
# # write_xlsx(
# #  list(
# #    "Sheet1" = Monatsmittel_export,
# #    "Quantile" = quantile_export
# #  ),
# #  path = paste0("Monatsmittel_", format(Sys.time(), "%Y%m%d"), ".xlsx")
# #)
# 
# 
# ### Vollständigkeit: letzte 24 volle Monate ------------------------------------
# 
# # Zeitraum: letzte 24 volle Monate
# m_end <- as.Date(format(Sys.Date(), "%Y-%m-01")) - 1
# month_keys <- format(seq.Date(as.Date(format(m_end, "%Y-%m-01")) - months(23), 
#                               by = "1 month", length.out = 24), "%Y-%m")
# 
# # Vollständigkeit berechnen
# vollstaendigkeit <- data %>%
#   mutate(MONAT_KEY = sprintf("%04d-%02d", JAHR, MONAT_Nr)) %>%
#   filter(MONAT_KEY %in% month_keys) %>%
#   group_by(MKZ, MONAT_KEY) %>%
#   summarise(Werte = sum(!is.na(GWS)), .groups = "drop") %>%
#   right_join(expand_grid(MKZ = sort(unique(data$MKZ)), MONAT_KEY = month_keys), 
#              by = c("MKZ", "MONAT_KEY")) %>%
#   mutate(Werte = replace_na(Werte, 0L)) %>%
#   pivot_wider(names_from = MONAT_KEY, values_from = Werte, values_fill = 0) %>%
#   arrange(MKZ)
# 
# # Export
# #write_xlsx(
# #  list("Vollstaendigkeit" = vollstaendigkeit),
# #  path = paste0("Vollstaendigkeit_", format(Sys.Date(), "%Y%m%d"), ".xlsx")
# #)
