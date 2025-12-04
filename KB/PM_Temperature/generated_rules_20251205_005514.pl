pm_over_35(PM2_5) :- PM2_5 > 35.
temp_over_30(Temperature) :- Temperature > 30.
midday_period(TimeHour) :- TimeHour >= 11, TimeHour =< 14.
health_risk_condition(PM2_5, Temperature, TimeHour, 'high health risk') :- pm_over_35(PM2_5), temp_over_30(Temperature), midday_period(TimeHour).
