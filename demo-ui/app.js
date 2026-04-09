const sampleResult = {
  database: "ORCLPDB1",
  metrics: {
    captured_at: "2026-04-09T15:20:00Z",
    cpu: {
      cpu_cores: 8,
      avg_active_sessions: 10.5,
      cpu_usage_pct: 131.25
    },
    wait_events: [
      { event: "db file sequential read", samples: 220, pct: 48.5 },
      { event: "log file sync", samples: 90, pct: 19.8 },
      { event: "enq: TX - row lock contention", samples: 54, pct: 11.9 }
    ],
    top_sql: [
      {
        sql_id: "8abc1234xyz99",
        avg_elapsed_sec: 300.05,
        executions: 2,
        buffer_gets: 800000,
        sql_text: "SELECT * FROM ORDERS WHERE STATUS = :B1"
      },
      {
        sql_id: "4kkk7777pqr11",
        avg_elapsed_sec: 410.0,
        executions: 1,
        buffer_gets: 650000,
        sql_text: "UPDATE INVENTORY SET QUANTITY = QUANTITY - :B1 WHERE PRODUCT_ID = :B2"
      }
    ],
    blocking_sessions: [
      {
        blocking_sid: 101,
        blocked_sid: 202,
        event: "enq: TX - row lock contention",
        seconds_in_wait: 120
      }
    ],
    io_hotspots: [
      { file_name: "/oradata/users01.dbf", avg_read_ms: 22.4, reads: 14000 }
    ],
    session_activity: [
      { module: "JDBC Thin Client", active_sessions: 5, wait_class: "User I/O" },
      { module: "Batch Job", active_sessions: 3, wait_class: "Application" },
      { module: "SQL Developer", active_sessions: 2, wait_class: "CPU" }
    ]
  },
  findings: [
    {
      severity: "high",
      title: "High CPU usage detected",
      summary: "Estimated CPU usage is 131.25%, above the threshold of 80%.",
      recommendation: "Check active sessions and top SQL statements to find which workload is using CPU."
    },
    {
      severity: "medium",
      title: "Important wait event detected",
      summary: "The top wait event is 'db file sequential read' with 48.5% of wait samples.",
      recommendation: "Check the sessions and SQL statements related to this wait event."
    },
    {
      severity: "critical",
      title: "Blocking sessions detected",
      summary: "1 blocking session chain was found.",
      recommendation: "Identify the blocking transaction and decide whether it should be committed, rolled back, or optimized."
    }
  ]
};

function renderResult(result) {
  const metrics = result.metrics || {};
  const cpu = metrics.cpu || {};

  document.getElementById("metric-db").textContent = result.database || "-";
  document.getElementById("metric-cpu").textContent = formatValue(cpu.cpu_usage_pct, "%");
  document.getElementById("metric-aas").textContent = cpu.avg_active_sessions ?? "-";
  document.getElementById("metric-blocking").textContent = (metrics.blocking_sessions || []).length;

  renderFindings(result.findings || []);
  renderTable(
    "top-sql-body",
    metrics.top_sql || [],
    (row) => `
      <tr>
        <td>${safe(row.sql_id)}</td>
        <td>${safe(row.avg_elapsed_sec)}</td>
        <td>${safe(row.executions)}</td>
        <td>${safe(row.buffer_gets)}</td>
        <td>${safe(row.sql_text)}</td>
      </tr>
    `
  );

  renderTable(
    "wait-events-body",
    metrics.wait_events || [],
    (row) => `
      <tr>
        <td>${safe(row.event)}</td>
        <td>${safe(row.samples)}</td>
        <td>${safe(row.pct)}%</td>
      </tr>
    `
  );

  renderTable(
    "session-activity-body",
    metrics.session_activity || [],
    (row) => `
      <tr>
        <td>${safe(row.module)}</td>
        <td>${safe(row.active_sessions)}</td>
        <td>${safe(row.wait_class)}</td>
      </tr>
    `
  );
}

function renderFindings(findings) {
  const container = document.getElementById("findings-list");
  if (!findings.length) {
    container.innerHTML = `<div class="empty-state">Aucun finding a afficher.</div>`;
    return;
  }

  container.innerHTML = findings.map((finding) => `
    <article class="finding ${safe(finding.severity)}">
      <span class="badge">${safe(finding.severity)}</span>
      <h3>${safe(finding.title)}</h3>
      <p><strong>Resume:</strong> ${safe(finding.summary)}</p>
      <p><strong>Recommendation:</strong> ${safe(finding.recommendation)}</p>
    </article>
  `).join("");
}

function renderTable(targetId, rows, rowTemplate) {
  const target = document.getElementById(targetId);
  if (!rows.length) {
    target.innerHTML = `<tr><td colspan="5" class="empty-state">Aucune donnee disponible.</td></tr>`;
    return;
  }
  target.innerHTML = rows.map(rowTemplate).join("");
}

function formatValue(value, suffix = "") {
  if (value === undefined || value === null || value === "") {
    return "-";
  }
  return `${value}${suffix}`;
}

function safe(value) {
  if (value === undefined || value === null) {
    return "-";
  }
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

renderResult(sampleResult);
