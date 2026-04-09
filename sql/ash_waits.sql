SELECT *
FROM (
    SELECT
        event,
        COUNT(*) AS samples,
        ROUND(RATIO_TO_REPORT(COUNT(*)) OVER () * 100, 2) AS pct
    FROM v$active_session_history
    WHERE sample_time > SYSTIMESTAMP - INTERVAL '15' MINUTE
      AND session_state = 'WAITING'
    GROUP BY event
    ORDER BY samples DESC
)
WHERE ROWNUM <= 10
