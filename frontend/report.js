/* ================= USER ================= */
document.getElementById("username").innerText =
  localStorage.getItem("username") || "Guest";

/* ================= ELEMENTS ================= */
const totalIncidentsEl = document.getElementById("totalIncidents");
const resolvedFaultsEl = document.getElementById("resolvedFaults");
const warningsIssuedEl = document.getElementById("warningsIssued");
const avgResponseEl = document.getElementById("avgResponse");
const incidentTable = document.getElementById("incidentTable");

const startDateEl = document.getElementById("startDate");
const endDateEl = document.getElementById("endDate");

/* ================= LOAD REPORTS ================= */
async function loadReports() {

  try {

    const start = startDateEl.value || "";
    const end = endDateEl.value || "";

    let url = `/report-data?start=${start}&end=${end}`;

    const res = await fetch(url);
    const data = await res.json();

    let total = 0;
    let resolved = 0;
    let warnings = 0;
    let responseSum = 0;

    incidentTable.innerHTML = "";

    data.forEach(i => {

      total++;

      // ✅ Fix counting logic
      if (i.status === "RESOLVED") resolved++;
      if (i.incident === "WARNING") warnings++;

      responseSum += i.response_time || 0;

      const row = document.createElement("tr");

      row.innerHTML = `
        <td>${i.date || "-"}</td>
        <td>${i.street || "-"}</td>
        <td>${i.incident || "FAULT"}</td>
        <td class="severity-${(i.severity || "LOW").toLowerCase()}">
            ${i.severity || "LOW"}
        </td>
        <td>${i.status || "-"}</td>
        <td>${i.officer || "-"}</td>
      `;

      incidentTable.appendChild(row);
    });

    totalIncidentsEl.innerText = total;
    resolvedFaultsEl.innerText = resolved;
    warningsIssuedEl.innerText = warnings;

    avgResponseEl.innerText =
      total ? Math.round(responseSum / total) + " min" : "0 min";

  } catch (error) {
    console.error("Report Load Error:", error);
  }
}

/* ================= FILTER ================= */
function applyFilter() {
  loadReports();
}

/* ================= EXPORT PDF ================= */
function exportPDF() {

  if (!window.jspdf || !window.jspdf.jsPDF) {
    alert("jsPDF not loaded!");
    return;
  }

  const { jsPDF } = window.jspdf;
  const doc = new jsPDF();

  doc.setFontSize(16);
  doc.text("LT Power Monitoring - Incident Report", 14, 20);

  const startDate = startDateEl.value || "N/A";
  const endDate = endDateEl.value || "N/A";

  doc.setFontSize(11);
  doc.text(`From: ${startDate}  To: ${endDate}`, 14, 28);

  const headers = Array.from(
    document.querySelectorAll("thead th")
  ).map(th => th.innerText);

  const rows = Array.from(
    document.querySelectorAll("#incidentTable tr")
  ).map(tr =>
    Array.from(tr.querySelectorAll("td")).map(td => td.innerText)
  ).filter(r => r.length);

  doc.autoTable({
    head: [headers],
    body: rows,
    startY: 35,
    theme: "grid"
  });

  doc.save(`Incident_Report_${startDate}_to_${endDate}.pdf`);
}

/* ================= EXPORT EXCEL ================= */
function exportExcel() {

  const wb = XLSX.utils.book_new();
  const ws_data = [];

  ws_data.push(["LT Power Monitoring - Incident Report"]);
  ws_data.push([]);

  ws_data.push([
    "Total Incidents",
    totalIncidentsEl.innerText
  ]);

  ws_data.push([
    "Faults Resolved",
    resolvedFaultsEl.innerText
  ]);

  ws_data.push([
    "Warnings Issued",
    warningsIssuedEl.innerText
  ]);

  ws_data.push([
    "Avg Response Time",
    avgResponseEl.innerText
  ]);

  ws_data.push([]);

  const headers = Array.from(
    document.querySelectorAll("thead th")
  ).map(th => th.innerText);

  ws_data.push(headers);

  const tableRows = document.querySelectorAll("#incidentTable tr");

  tableRows.forEach(tr => {
    const row = Array.from(tr.querySelectorAll("td")).map(td => td.innerText);
    if (row.length) ws_data.push(row);
  });

  const ws = XLSX.utils.aoa_to_sheet(ws_data);
  XLSX.utils.book_append_sheet(wb, ws, "Report");

  XLSX.writeFile(wb, "Incident_Report.xlsx");
}

/* ================= LOGOUT ================= */
function logout() {
  localStorage.clear();
  window.location.href = "/";
}

/* ================= INIT ================= */
loadReports();