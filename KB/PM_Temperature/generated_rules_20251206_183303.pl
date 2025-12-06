:- encoding(utf8).
pm_label(_PM2_5, Temp, Time, "บรรยากาศร้อนและปั่นป่วนสูง") :- Temp > 30, Time >= 12, Time =< 17.
pm_label(PM2_5, _Temp, _Time, "ระดับมลพิษปานกลางถึงสูง (Moderate to high concentration)") :- PM2_5 >= 45, PM2_5 =< 60.
