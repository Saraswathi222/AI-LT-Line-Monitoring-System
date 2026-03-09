let streets = [];
let loadChart;
let statusChart;
let previousFaultCount = 0;   // ✅ ADD THIS LINE

// ================= LOAD DASHBOARD =================
document.addEventListener("DOMContentLoaded", function () {

    const username = localStorage.getItem("username");
    if (username) {
        document.getElementById("username").innerText = username;
    }

    fetchLiveData();
    setInterval(fetchLiveData, 15000);
});

// ================= FETCH FROM BACKEND =================
function fetchLiveData() {

    fetch("/live-data", {
        credentials: "include"
    })
    .then(res => {
        if (!res.ok) throw new Error("Unauthorized");
        return res.json();
    })
    .then(data => {
        streets = data;
        updateDashboard();
    })
    .catch(err => {
        console.error("Error:", err);
    });
}

// ================= SOLVE ISSUE =================
function solveIssue(index) {

    const street = streets[index];

    fetch("/resolve", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        credentials: "include",
        body: JSON.stringify({
            street: street.street,
            fault_status: street.fault_status
        })
    })
    .then(res => res.json())
    .then(data => {

        alert("Issue Resolved Successfully ✅");

        streets[index].fault_status = "NORMAL";

        updateDashboard();   // No fetchLiveData()
    });
}

// ================= UPDATE DASHBOARD =================
function updateDashboard() {
    updateKPIs();
    renderTable();
    updateCharts();
    updateAIInsights();
}

// ================= KPI =================
function updateKPIs() {

    document.getElementById("totalStreets").innerText = streets.length;

    let faults = streets.filter(s => s.fault_status === "FAULT").length;
    let normal = streets.filter(s => s.fault_status === "NORMAL").length;
    let warning = streets.filter(s => s.fault_status === "WARNING").length;

    document.getElementById("faultCount").innerText = faults;
    document.getElementById("normalCount").innerText = normal;
    document.getElementById("alertCount").innerText = warning;
}

// ================= TABLE =================
function renderTable(filter = "ALL") {

    const table = document.getElementById("streetTable");
    table.innerHTML = "";

    let filteredData = streets;

    if (filter !== "ALL") {
        filteredData = streets.filter(s => s.fault_status === filter);
    }

    filteredData.forEach((street, index) => {

        let row = document.createElement("tr");
        row.classList.add("fade-in");

        row.innerHTML = `
            <td>${street.street}</td>
            <td>${street.line_no}</td>
            <td>${street.phase}</td>
            <td>${street.voltage}</td>
            <td>${street.current}</td>
            <td>${street.load_kw}</td>
            <td class="status-${street.fault_status.toLowerCase()}">${street.fault_status}</td>
            <td>${street.confidence_percent}%</td>
            <td>${new Date().toLocaleTimeString()}</td>
            <td>${street.solution}</td>
            <td>
                ${street.fault_status !== "NORMAL"
                    ? `<button class="solve-btn" onclick="solveIssue(${index})">Solve</button>`
                    : `<span class="no-action">—</span>`}
            </td>
        `;

        table.appendChild(row);
    });
}

// ================= FILTER =================
function filterRows(type) {
    renderTable(type);
}

// ================= AI INSIGHTS =================
function updateAIInsights() {

    let faults = streets.filter(
        s => s.fault_status === "FAULT" || s.fault_status === "WARNING"
    );

    document.getElementById("aiFaults").innerText = faults.length;

    let statusText = "Stable";

    if (faults.length > 2) {
        statusText = "Critical";
    } else if (faults.length > 0) {
        statusText = "Warning";
    }

    document.getElementById("aiConfidence").innerText = statusText;

    // ================= Recent AI Predictions =================
    const predictionsList = document.getElementById("aiPredictions");
    predictionsList.innerHTML = "";

    streets.forEach(s => {
        let li = document.createElement("li");
        li.innerText = `${s.street} → ${s.fault_status} (${s.confidence_percent}%)`;
        predictionsList.appendChild(li);
    });

    // ================= Alert Center =================
    const alertList = document.getElementById("alertList");
    alertList.innerHTML = "";

    faults.forEach(f => {
        let div = document.createElement("div");
        div.innerText = `🚨 ${f.fault_status} at ${f.street}`;
        alertList.appendChild(div);
    });

    // ================= Navbar Notification =================
    document.getElementById("notifCount").innerText = faults.length;

    const notificationList = document.getElementById("notificationList");
    notificationList.innerHTML = "";

    if (faults.length === 0) {
        notificationList.innerHTML = "<div>No active faults</div>";
    } else {
        faults.forEach(f => {
            let div = document.createElement("div");
            div.innerText = `🚨 ${f.street} - ${f.fault_status}`;
            notificationList.appendChild(div);
        });
    }

    // Popup when new critical detected
    if (faults.length > previousFaultCount && statusText === "Critical") {
        showPopup("🚨 CRITICAL ALERT! Multiple faults detected!");
    }

    previousFaultCount = faults.length;
}
function toggleNotifications() {
    const panel = document.getElementById("notificationPanel");
    panel.style.display = panel.style.display === "block" ? "none" : "block";
}
function showPopup(message) {

    const popup = document.createElement("div");
    popup.className = "critical-popup";
    popup.innerText = message;

    document.body.appendChild(popup);

    setTimeout(() => {
        popup.remove();
    }, 4000);
}
// ================= CHARTS =================
function updateCharts() {

    const loadData = streets.map(s => s.load_kw);
    const statusCounts = [
        streets.filter(s => s.fault_status === "NORMAL").length,
        streets.filter(s => s.fault_status === "WARNING").length,
        streets.filter(s => s.fault_status === "FAULT").length
    ];

    if (!loadChart) {
        loadChart = new Chart(document.getElementById("loadChart"), {
            type: 'bar',
            data: {
                labels: streets.map(s => s.street),
                datasets: [{
                    label: 'Load (kW)',
                    data: loadData
                }]
            }
        });
    } else {
        loadChart.data.labels = streets.map(s => s.street);
        loadChart.data.datasets[0].data = loadData;
        loadChart.update();
    }

    if (!statusChart) {
        statusChart = new Chart(document.getElementById("statusChart"), {
            type: 'pie',
            data: {
                labels: ['Normal', 'Warning', 'Fault'],
                datasets: [{
                    data: statusCounts
                }]
            }
        });
    } else {
        statusChart.data.datasets[0].data = statusCounts;
        statusChart.update();
    }
}
