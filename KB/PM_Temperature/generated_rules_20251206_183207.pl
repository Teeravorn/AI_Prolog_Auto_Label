:- encoding(utf8).
pm_label(_, Temp, Time, 'บรรยากาศร้อนและปั่นป่วนสูง') :- Temp > 30, Time >= 12, Time =< 17.
pm_label(PM2_5, _, _, 'ระดับมลพิษปานกลางถึงสูง (Moderate to high concentration)') :- PM2_5 >= 45, PM2_5 =< 60.
