:- encoding(utf8).
high_moderate_pm(PM2_5) :- PM2_5 > 45.
hot_temperature(Temperature) :- Temperature > 30.
morning_peak_hour(TimeHour) :- TimeHour >= 8, TimeHour =< 10.
label_pm_concentration(PM2_5, 'Moderate to high concentration') :- high_moderate_pm(PM2_5).
label_atmosphere_type(Temperature, 'Hot and turbulent atmosphere') :- hot_temperature(Temperature).
label_overall_risk(PM2_5, TimeHour, 'High Risk') :- high_moderate_pm(PM2_5), morning_peak_hour(TimeHour).
