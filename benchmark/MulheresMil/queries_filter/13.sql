SELECT CAST(EXTRACT(YEAR FROM "MulheresMil_1"."data_de_inicio") AS BIGINT) AS "yr_data_de_inicio_ok" FROM "MulheresMil_1" GROUP BY "yr_data_de_inicio_ok" ORDER BY "yr_data_de_inicio_ok" ASC ;
