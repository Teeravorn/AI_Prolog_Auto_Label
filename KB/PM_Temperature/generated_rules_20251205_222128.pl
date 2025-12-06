very_high_pm(PM2_5) :- PM2_5 > 60.
label_pm_risk(PM2_5, 'ระดับมลพิษสูงมาก (Very high concentration)') :- very_high_pm(PM2_5).
