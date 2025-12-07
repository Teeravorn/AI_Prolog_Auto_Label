:- encoding(utf8).
likely_rain(Temp, Humidity, 'LikelyRain') :- Temp < 22.5, Humidity > 80.
no_rain(Humidity, 'NoRain') :- Humidity < 60.
possible_rain(Temp, Humidity, 'PossibleRain') :- Temp > 24, Humidity >= 60, Humidity =< 80.
