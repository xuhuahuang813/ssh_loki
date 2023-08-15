SELECT rentabilidad_1.rutadeventa AS rutadeventa FROM rentabilidad_1 WHERE ((rentabilidad_1.locación = 'Bogota Sur') AND (rentabilidad_1.zona = 'CE')) GROUP BY rentabilidad_1.rutadeventa;
