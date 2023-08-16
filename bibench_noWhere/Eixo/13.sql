SELECT CAST(EXTRACT(YEAR FROM "Eixo_1"."data_de_inicio") AS BIGINT) AS "yr_data_de_inicio_ok" FROM "Eixo_1" GROUP BY "yr_data_de_inicio_ok" ORDER BY "yr_data_de_inicio_ok" ASC ;
