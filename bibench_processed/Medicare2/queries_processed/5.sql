SELECT medicare2_2.nppes_entity_code AS nppes_entity_code FROM medicare2_2 WHERE (medicare2_2.nppes_provider_state = 'NY') GROUP BY medicare2_2.nppes_entity_code ORDER BY nppes_entity_code ASC ;
