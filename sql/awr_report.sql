-- Example:
-- @awr_report.sql 100 101 /tmp/awr_100_101.html

DEFINE begin_snap=&1
DEFINE end_snap=&2
DEFINE report_file=&3

SET LONG 1000000 LONGCHUNKSIZE 1000000 LINESIZE 200 PAGESIZE 0 FEEDBACK OFF VERIFY OFF TRIMSPOOL ON
SPOOL &report_file

SELECT output
FROM TABLE(
    DBMS_WORKLOAD_REPOSITORY.AWR_REPORT_HTML(
        (SELECT dbid FROM v$database),
        (SELECT instance_number FROM v$instance),
        &&begin_snap,
        &&end_snap
    )
);

SPOOL OFF
