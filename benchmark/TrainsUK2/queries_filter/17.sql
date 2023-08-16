SELECT SUM(CAST("TrainsUK2_2"."Number_of_Records" AS BIGINT)) AS "sum_Number_of_Records_ok" FROM "TrainsUK2_2" HAVING (COUNT(1) > 0);
