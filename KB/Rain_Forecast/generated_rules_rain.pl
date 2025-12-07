% Helper predicates for humidity and temperature
high_humidity(H) :- H >= 80.
med_humidity(H) :- H >= 60, H < 80.
low_humidity(H) :- H < 60.

high_temp(T) :- T >= 30.
med_temp(T) :- T >= 20, T < 30.
low_temp(T) :- T < 20.

% Labeling rules based only on humidity and temperature (label is last argument)
label_rain_forecast(Temperature, Humidity, _Pressure, _PressureDrop, _Rainfall, 'LikelyRain') :-
    high_humidity(Humidity),
    med_temp(Temperature).

label_rain_forecast(Temperature, Humidity, _Pressure, _PressureDrop, _Rainfall, 'LikelyRain') :-
    high_humidity(Humidity),
    low_temp(Temperature).

label_rain_forecast(Temperature, Humidity, _Pressure, _PressureDrop, _Rainfall, 'PossibleRain') :-
    med_humidity(Humidity),
    \+ high_temp(Temperature).

label_rain_forecast(Temperature, Humidity, _Pressure, _PressureDrop, _Rainfall, 'NoRain') :-
    low_humidity(Humidity).

label_rain_forecast(Temperature, Humidity, _Pressure, _PressureDrop, _Rainfall, 'NoRain') :-
    high_temp(Temperature),
    \+ high_humidity(Humidity).
