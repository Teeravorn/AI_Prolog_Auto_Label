:- encoding(utf8).
is_humid(H) :- H > 80.
is_moderate_humid(H) :- H >= 60, H =< 80.
is_dry(H) :- H < 60.
is_low_press(P) :- P < 1000.
is_moderate_press(P) :- P >= 1000, P =< 1015.
is_high_press(P) :- P > 1015.
is_large_drop(PD) :- PD > 3.
is_small_drop(PD) :- PD >= 1, PD =< 3.
is_stable_press(PD) :- PD < 1.
is_strong_wind(WS) :- WS > 30.
is_moderate_wind(WS) :- WS >= 10, WS =< 30.
is_light_wind(WS) :- WS < 10.
is_above_freezing(T) :- T > 0.
label_rain_forecast(Temperature, _, _, _, _, 'no_rain') :- \+ is_above_freezing(Temperature).
label_rain_forecast(Temperature, Humidity, Pressure, PressureDrop, WindSpeed, 'heavy_rain') :- is_above_freezing(Temperature), is_humid(Humidity), is_low_press(Pressure), is_large_drop(PressureDrop), is_strong_wind(WindSpeed).
label_rain_forecast(Temperature, Humidity, Pressure, PressureDrop, WindSpeed, 'light_rain') :- is_above_freezing(Temperature), is_humid(Humidity), (is_low_press(Pressure) ; is_moderate_press(Pressure)), (is_large_drop(PressureDrop) ; is_small_drop(PressureDrop)).
label_rain_forecast(Temperature, Humidity, Pressure, PressureDrop, WindSpeed, 'possible_rain') :- is_above_freezing(Temperature), is_moderate_humid(Humidity), (is_moderate_press(Pressure) ; is_low_press(Pressure)), (is_small_drop(PressureDrop) ; is_stable_press(PressureDrop)).
label_rain_forecast(Temperature, Humidity, Pressure, PressureDrop, WindSpeed, 'no_rain') :- is_above_freezing(Temperature), is_dry(Humidity), is_high_press(Pressure), is_stable_press(PressureDrop), is_light_wind(WindSpeed).
label_rain_forecast(_, _, _, _, _, 'no_rain').
