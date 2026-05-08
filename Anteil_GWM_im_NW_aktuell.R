#library(openxlsx)
#library(readxl)
library(dplyr)
library(ggplot2)
library(pracma) #only for moving average

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
### check if there are 279 GWM
MKZ_Liste <- unique(alle$MKZ)

### Mittelwert per MKZ,Jahr,Monat
GWS_MM <- aggregate(GWS~ MKZ+JAHR+MONAT_Nr, data = alle, FUN = mean)
GWS_MM$TAG <- "15"
GWS_MM$DATUM <- paste(GWS_MM$TAG, GWS_MM$MONAT_Nr, GWS_MM$JAHR, sep="-")
GWS_MM$DATUM <- as.Date(GWS_MM$DATUM, format = "%d-%m-%Y")


### calc Niedrigwasser # minimum per GWM+year+month
GWS_min <- aggregate(GWS ~ MKZ+JAHR+MONAT_Nr, data = alle, FUN = min)
# MNW ... mittleres Niedigwasser per GWM+month
GWS_MNW <- aggregate(GWS ~ MKZ+MONAT_Nr, data = GWS_min, FUN = mean)
# merge
GWS_MM_MNW <- merge(x = GWS_MM, y = GWS_MNW, by = c("MKZ","MONAT_Nr"), all = TRUE)
GWS_MM_MNW <- rename(GWS_MM_MNW, GWS_MM = GWS.x, GWS_MNW = GWS.y)


# check: GWM at/below MNW
GWS_MM_MNW$at_MNW <- GWS_MM_MNW$GWS_MNW - GWS_MM_MNW$GWS_MM

GWS_MM_MNW$at_MNW <- dplyr::case_when(
  GWS_MM_MNW$at_MNW >= 0 ~ FALSE,
  GWS_MM_MNW$at_MNW < 0 ~ TRUE
  #mean_MNW_MKZ$at_MNW == 0 ~ "?"
)

# GWS_MM_MNW %>% count(at_MNW)


GWS_MM_MNW_TRUE <- filter(GWS_MM_MNW, at_MNW == TRUE)

# Anzahl gesamt
n_ges <- GWS_MM_MNW %>% group_by(DATUM) %>% summarise(n_ges=n())
# Anzahl unter MNW
n_MNW <- GWS_MM_MNW_TRUE %>% group_by(DATUM) %>% summarise(n_MNW=n())

# merge
GWS_MM_MNW_Anzahl <- merge(n_ges, n_MNW, by = 'DATUM')
#GWS_MM_MNW_Anzahl <- mean_MNW_MKZ_Anzahl[order(mean_MNW_MKZ_Anzahl$DATUM),]
GWS_MM_MNW_Anzahl <- GWS_MM_MNW_Anzahl[order(GWS_MM_MNW_Anzahl$DATUM),]

# percent
GWS_MM_MNW_Anzahl$n_MNW_perc <- GWS_MM_MNW_Anzahl$n_MNW / GWS_MM_MNW_Anzahl$n_ges * 100

### moving average
### Angaben anpassen, die if-Klammerung gewährleistet externe Verarbeitung des Skriptes und überspringt die nachfolgenden Variablenbelegungen
if (!exists("Berichtsmonatsende")) {
  Berichtsmonatsende <- "2026-04-30"  #<------------------------------ für laufenden Monat wg. Datengrundlage (letzter voller Berichtsmonat)
}
sma12 <- movavg(x = GWS_MM_MNW_Anzahl$n_MNW_perc, n = 12, type = "s") #simple
GWS_MM_MNW_Anzahl$n_MNW_perc_sma12 <- as.numeric(sma12)

#Monatsmin_2018 <- filter(GWS_MM_MNW_Anzahl, DATUM >= "2017-11-01" & DATUM <="2018-10-31")
#Monatsmin_2019 <- filter(GWS_MM_MNW_Anzahl, DATUM >= "2018-11-01" & DATUM <="2019-10-31")
#Monatsmin_2020 <- filter(GWS_MM_MNW_Anzahl, DATUM >= "2019-11-01" & DATUM <="2020-10-31")
Monatsmin_2021 <- filter(GWS_MM_MNW_Anzahl, DATUM >= "2020-11-01" & DATUM <="2021-10-31")
Monatsmin_2022 <- filter(GWS_MM_MNW_Anzahl, DATUM >= "2021-11-01" & DATUM <="2022-10-31")
Monatsmin_2023 <- filter(GWS_MM_MNW_Anzahl, DATUM >= "2022-11-01" & DATUM <="2023-10-31") 
Monatsmin_2024 <- filter(GWS_MM_MNW_Anzahl, DATUM >= "2023-11-01" & DATUM <="2024-10-31") 
Monatsmin_2025 <- filter(GWS_MM_MNW_Anzahl, DATUM >= "2024-11-01" & DATUM <="2025-10-31") 
Monatsmin_2026 <- filter(GWS_MM_MNW_Anzahl, DATUM >= "2025-11-01" & DATUM <=Berichtsmonatsende) 



# plot(GWS_MM_MNW_Anzahl$DATUM, GWS_MM_MNW_Anzahl$n_MNW_perc_sma12, type = 'l')


#####################################################################
#PLOT

#Plot erstellen
Plot_GWStand<-ggplot(data=GWS_MM_MNW_Anzahl, aes(x=DATUM, y=n_MNW_perc_sma12, group=1))+
  geom_col(data = Monatsmin_2026, width=20, aes(x=DATUM, y=n_MNW_perc, fill="Abflussjahr 2026"))+
  geom_col(data = Monatsmin_2025, width=20, aes(x=DATUM, y=n_MNW_perc, fill="Abflussjahr 2025"))+
  geom_col(data = Monatsmin_2024, width=20, aes(x=DATUM, y=n_MNW_perc, fill="Abflussjahr 2024"))+
  geom_col(data = Monatsmin_2023, width=20, aes(x=DATUM, y=n_MNW_perc, fill="Abflussjahr 2023"))+
  geom_col(data = Monatsmin_2022, width=20, aes(x=DATUM, y=n_MNW_perc, fill="Abflussjahr 2022"))+
  geom_col(data = Monatsmin_2021, width=20, aes(x=DATUM, y=n_MNW_perc, fill="Abflussjahr 2021"))+
#  geom_col(data = Monatsmin_2020, width=20, aes(x=DATUM, y=n_MNW_perc, fill="Abflussjahr 2020"))+
#  geom_col(data = Monatsmin_2019, width=20, aes(x=DATUM, y=n_MNW_perc, fill="Abflussjahr 2019"))+
#  geom_col(data = Monatsmin_2018, width=20, aes(x=DATUM, y=n_MNW_perc, fill="Abflussjahr 2018"))+
  geom_line(data = GWS_MM_MNW_Anzahl, size=1, aes(y = n_MNW_perc_sma12 , color = "gleitender Mittelwert über 12 Monate"))+
  labs(x = "", y = "Anteil Grundwassermessstellen 
       im Niedrigwasser [%]", 
       title = "Anteil der Grundwassermessstellen im Niedrigwasser",
       caption= "© LfULG")+
  scale_y_reverse(limits=c(100,0), breaks=seq(100,0,-10))+
  coord_cartesian(ylim=c(100,20))+
  # coord_cartesian(ylim=c(100,00))+
  #limits einstellen
  scale_x_date(limits = as.Date(c("2020-11-01", Berichtsmonatsende)), 
               date_labels = "%b, %y", date_breaks = "4 month")+
  scale_fill_manual("", 
                   breaks = c("Abflussjahr 2021","Abflussjahr 2022","Abflussjahr 2023","Abflussjahr 2024","Abflussjahr 2025", "Abflussjahr 2026"),
                   values = c("Abflussjahr 2021"="mediumpurple", "Abflussjahr 2022"="khaki4", "Abflussjahr 2023"="lightblue", "Abflussjahr 2024"="pink2", "Abflussjahr 2025"="yellowgreen", "Abflussjahr 2026"="orange2"))+
  scale_colour_manual("", 
                   breaks = "gleitender Mittelwert über 12 Monate",
                   values = "black")+
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
        axis.text = element_text(size=15),
        axis.text.x=element_text(angle=60, hjust=1),
        axis.title = element_text(size=17),
        panel.background = element_rect(fill = "white", colour = "grey50"),
        panel.spacing.y = unit(6, "cm"),
        panel.grid.major.x = element_line(colour = "grey70"),
        panel.grid.minor.x = element_line(colour = "grey70"),
        panel.grid.major.y = element_line(colour = "grey70"),
        panel.grid.minor.y = element_line(colour = "grey70"),
        legend.key = element_rect(fill = "white", color= "white"),
        legend.key.width= unit(1., 'cm'),
        legend.key.height= unit(0.2, 'cm')) 
Plot_GWStand


### save plot as png
filename <- paste0("Anteil_GWM_im_NW_",format(Sys.time(), "%Y%m%d"),".png")
png(file = filename, width = 800, height = 570)
Plot_GWStand
dev.off()

#write_xlsx(merged_Anzahl, "GWM_im_NW_",format(Sys.time(), "%Y%m%d"),".xlsx")
