PM_label(PM2_5, _, _, 'ระดับมลพิษปานกลางถึงสูง (Moderate to high concentration)') :- PM2_5 >= 45, PM2_5 =< 60.
PM_label(_, Temperature, Hour, 'บรรยากาศร้อนและปั่นป่วนสูง') :- Temperature > 30, Hour >= 12, Hour =< 17.
