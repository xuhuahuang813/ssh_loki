SELECT medicare2_2.hcpcs_description AS hcpcs_description FROM medicare2_2 WHERE (medicare2_2.nppes_provider_state = 'NY') GROUP BY medicare2_2.hcpcs_description ORDER BY hcpcs_description ASC ;
