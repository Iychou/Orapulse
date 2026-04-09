SELECT *
FROM (
    SELECT
        df.file_name,
        ROUND(
            CASE
                WHEN fs.phyrds = 0 THEN 0
                ELSE (fs.readtim / fs.phyrds)
            END,
            2
        ) AS avg_read_ms,
        fs.phyrds AS reads
    FROM v$filestat fs
    JOIN dba_data_files df
      ON fs.file# = df.file_id
    ORDER BY avg_read_ms DESC
)
WHERE ROWNUM <= 10
