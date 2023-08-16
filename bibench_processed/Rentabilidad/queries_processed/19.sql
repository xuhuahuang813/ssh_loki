SELECT rentabilidad_1.ruta_de_venta AS ruta_de_venta FROM rentabilidad_1 WHERE ((rentabilidad_1.locacion = 'Bogota Sur') AND (rentabilidad_1.zona = 'CE')) GROUP BY rentabilidad_1.ruta_de_venta;
