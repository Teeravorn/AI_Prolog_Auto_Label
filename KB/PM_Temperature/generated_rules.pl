air_quality_label(PM2_5_Value, 'มีมลพิษทางอากาศสูง') :- PM2_5_Value > 35.
air_quality_label(PM2_5_Value, 'มีมลพิษทางอากาศปานกลาง') :- PM2_5_Value =< 35, PM2_5_Value > 15.
air_quality_label(PM2_5_Value, 'มีมลพิษทางอากาศต่ำ') :- PM2_5_Value =< 15.
