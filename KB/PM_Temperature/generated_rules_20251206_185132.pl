:- encoding(utf8).
pm_label(PM2_5, _, _, 'high health risk') :- PM2_5 >= 45, PM2_5 =< 60.
