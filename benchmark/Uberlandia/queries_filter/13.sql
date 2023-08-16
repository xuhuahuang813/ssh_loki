SELECT CAST(EXTRACT(YEAR FROM "Uberlandia_1"."data_de_inicio") AS BIGINT) AS "yr_data_de_inicio_ok" FROM "Uberlandia_1" GROUP BY "yr_data_de_inicio_ok" ORDER BY "yr_data_de_inicio_ok" ASC ;
