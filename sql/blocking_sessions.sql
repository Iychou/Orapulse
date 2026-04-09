SELECT
    s1.sid AS blocking_sid,
    s1.serial# AS blocking_serial,
    s2.sid AS blocked_sid,
    s2.serial# AS blocked_serial,
    s2.wait_class,
    s2.event,
    s2.seconds_in_wait
FROM v$session s1
JOIN v$session s2
  ON s1.sid = s2.blocking_session
WHERE s2.blocking_session IS NOT NULL
ORDER BY s2.seconds_in_wait DESC
