SELECT
    cmsprovider_2.hcpcs_description AS hcpcs_description,
    CAST(cmsprovider_2.nppes_provider_zip AS BIGINT) AS nppes_provider_zip,
    SUM(cmsprovider_2.average_medicare_payment_amt) AS sum :average_medicare_payment_amt :ok
FROM
    cmsprovider_2
WHERE
    (cmsprovider_2.nppes_provider_state = 'CA')
GROUP BY
    cmsprovider_2.hcpcs_description,
    cmsprovider_2.nppes_provider_zip,
    cmsprovider_2.nppes_provider_zip;