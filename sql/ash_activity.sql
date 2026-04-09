SELECT *
FROM (
    SELECT
        NVL(module, 'UNKNOWN') AS module,
        COUNT(*) AS active_sessions,
        NVL(wait_class, 'CPU') AS wait_class
    FROM v$active_session_history
    WHERE sample_time > SYSTIMESTAMP - INTERVAL '15' MINUTE
    GROUP BY module, wait_class
    ORDER BY active_sessions DESC
)
WHERE ROWNUM <= 15
