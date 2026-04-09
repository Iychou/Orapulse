# OraPulse

OraPulse is a simple Oracle DBA project.
The idea is to make some daily DBA work easier by collecting Oracle performance information in one place and showing the main problems in a clear way.

This is not meant to look like a big enterprise platform.
It is just a practical project that helps a DBA review performance faster.

## Project Idea

When a database has a performance issue, a DBA often checks many things manually:

- AWR information
- ASH activity
- ADDM reports
- top SQL
- wait events
- blocking sessions

This project tries to simplify that work.
Instead of checking everything by hand, OraPulse gathers the important information and creates simple reports.

## What The Project Does

The project helps detect common Oracle performance problems such as:

- high CPU usage
- I/O contention
- long-running SQL queries
- blocking sessions

It works with Oracle performance data from:

- `V$ACTIVE_SESSION_HISTORY`
- `DBA_HIST_SNAPSHOT`
- `DBA_HIST_SQLSTAT`
- `V$SESSION`
- `V$FILESTAT`

## Main Parts Of The Project

- [src/orapulse/collector.py](/c:/Users/X1/Documents/web%20porjects/bank%20projet/src/orapulse/collector.py)
Reads Oracle performance data or sample data

- [src/orapulse/analyzer.py](/c:/Users/X1/Documents/web%20porjects/bank%20projet/src/orapulse/analyzer.py)
Checks the collected data and detects simple issues

- [src/orapulse/formatter.py](/c:/Users/X1/Documents/web%20porjects/bank%20projet/src/orapulse/formatter.py)
Creates easy-to-read HTML, JSON, and TXT reports

- [src/orapulse/alerts.py](/c:/Users/X1/Documents/web%20porjects/bank%20projet/src/orapulse/alerts.py)
Creates simple alerts using logs or email

- [sql](/c:/Users/X1/Documents/web%20porjects/bank%20projet/sql)
Contains the Oracle SQL scripts used for the project

- [scripts](/c:/Users/X1/Documents/web%20porjects/bank%20projet/scripts)
Contains helper shell scripts

## Project Structure

```text
OraPulse/
|-- config/
|   `-- orapulse.yml
|-- reports/
|-- scripts/
|-- sql/
|-- src/orapulse/
`-- requirements.txt
```

## Simple Workflow

1. Read Oracle performance data
2. Check for common issues
3. Generate a report
4. Help the DBA decide what to investigate next

## Example Of What It Can Show

- top SQL statements with high elapsed time
- important wait events
- active session activity
- blocking sessions
- basic recommendations

## Configuration

The configuration file is [config/orapulse.yml](/c:/Users/X1/Documents/web%20porjects/bank%20projet/config/orapulse.yml).

It contains:

- database connection information
- credentials
- thresholds
- output folder
- alert options

Example:

```yaml
databases:
  - name: primary
    host: db.example.com
    port: 1521
    service_name: ORCLPDB1
    username: monitor_user
    password_env: ORAPULSE_DB_PASSWORD
    thresholds:
      cpu_percent: 80
      io_wait_ms: 20
      long_running_sql_seconds: 300
      blocking_sessions: 1
```

## SQL Files

The SQL folder includes scripts for:

- top SQL
- ASH activity
- wait events
- blocking sessions
- I/O hotspots
- AWR report export
- ASH report export
- ADDM report export

## Reports

The project can create:

- HTML report
- JSON report
- TXT report

The reports are written in [reports](/c:/Users/X1/Documents/web%20porjects/bank%20projet/reports).

## Why This Project Is Useful

This project is useful because it:

- saves time
- reduces repetitive DBA work
- helps organize Oracle performance checks
- makes investigation easier

## Why This Is A Good Junior Project

This project shows:

- Oracle performance basics
- SQL scripting
- Python scripting
- simple automation
- practical DBA thinking

It is simple enough to understand and explain, but still useful and realistic.
