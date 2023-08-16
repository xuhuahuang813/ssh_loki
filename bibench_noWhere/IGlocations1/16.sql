SELECT trim(splitpart("IGlocations1_1"."City", ' ', 1),' \\t\ \\x0b\\f\\r') AS "City___Split_1" FROM "IGlocations1_1" GROUP BY "City___Split_1" ORDER BY "City___Split_1" ASC ;
