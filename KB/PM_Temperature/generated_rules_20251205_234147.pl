:- encoding(utf8).
pm_label(PM2_5, _, _, 'High health risk') :- PM2_5 >= 45, PM2_5 =< 60.
pm_label(_, Temperature, Time, 'Hot and turbulent atmosphere') :- Temperature > 30, Time >= 12, Time =< 17.
