:- encoding(utf8).
high_pm_for_moderate_level(PM2_5) :- PM2_5 > 45.
very_hot_temp(Temperature) :- Temperature > 30.
noon_to_late_afternoon(TimeHour) :- TimeHour >= 12, TimeHour =< 17.
label_pm_concentration(PM2_5, 'Moderate to high concentration') :- high_pm_for_moderate_level(PM2_5).
label_atmosphere_condition(Temperature, TimeHour, 'hot and turbulent atmosphere') :- very_hot_temp(Temperature), noon_to_late_afternoon(TimeHour).
