SELECT medicare2_2.provider_type AS provider_type FROM medicare2_2 WHERE (medicare2_2.nppes_provider_state = 'NY') GROUP BY medicare2_2.provider_type ORDER BY provider_type ASC ;
