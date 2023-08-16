SELECT CAST(EXTRACT(YEAR FROM (cast("CommonGovernment_4"."signeddate" as DATE) + 3 * INTERVAL '1' MONTH)) AS BIGINT) AS "yr_signeddate_ok" FROM "CommonGovernment_4" GROUP BY "yr_signeddate_ok";
