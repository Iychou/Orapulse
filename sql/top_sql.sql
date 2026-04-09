SELECT *
FROM (
    SELECT
        s.sql_id,
        ROUND(s.elapsed_time_delta / 1000000, 2) AS elapsed_sec,
        s.executions_delta AS executions,
        ROUND(
            CASE
                WHEN s.executions_delta = 0 THEN s.elapsed_time_delta / 1000000
                ELSE (s.elapsed_time_delta / 1000000) / s.executions_delta
            END,
            2
        ) AS avg_elapsed_sec,
        s.buffer_gets_delta AS buffer_gets,
        s.disk_reads_delta AS disk_reads,
        SUBSTR(t.sql_text, 1, 160) AS sql_text
    FROM dba_hist_sqlstat s
    JOIN dba_hist_snapshot sn
      ON s.snap_id = sn.snap_id
     AND s.dbid = sn.dbid
     AND s.instance_number = sn.instance_number
    JOIN dba_hist_sqltext t
      ON s.dbid = t.dbid
     AND s.sql_id = t.sql_id
    WHERE sn.begin_interval_time > SYSDATE - (1/24)
    ORDER BY s.elapsed_time_delta DESC
)
WHERE ROWNUM <= 10
