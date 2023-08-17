SELECT medicare2_1.provider_type AS provider_type FROM medicare2_1 WHERE (medicare2_1.nppes_provider_state = 'NY') GROUP BY medicare2_1.provider_type ORDER BY provider_type ASC ;
