SELECT rentabilidad_1.figura AS figura FROM rentabilidad_1 WHERE ((rentabilidad_1.sede_foraneo_sintec = 'Sede') AND (rentabilidad_1.zona = 'OC')) GROUP BY rentabilidad_1.figura;
