-- Example:
-- @ash_report.sql /tmp/ash_report.txt

DEFINE report_file=&1

SET LINESIZE 200 PAGESIZE 100 TRIMSPOOL ON
SPOOL &report_file

SELECT
    sample_time,
    session_id,
    session_serial#,
    sql_id,
    session_state,
    wait_class,
    event,
    module
FROM v$active_session_history
WHERE sample_time > SYSTIMESTAMP - INTERVAL '15' MINUTE
ORDER BY sample_time DESC;

SPOOL OFF
