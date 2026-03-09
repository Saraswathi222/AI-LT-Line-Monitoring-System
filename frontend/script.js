const API = "http://127.0.0.1:5000";

/* ================= AUTO LOGIN CHECK ================= */
if (localStorage.getItem("assigned_streets")) {
    console.log("User already logged in");
}

/* ================= MODALS ================= */
const loginModal = document.getElementById("loginModal");
const signupModal = document.getElementById("signupModal");

function openLogin() {
    loginModal.style.display = "flex";
}
function closeLogin() {
    loginModal.style.display = "none";
}
function openSignup() {
    signupModal.style.display = "flex";
    setTimeout(initMap, 300);
    detectLocation();
}
function closeSignup() {
    signupModal.style.display = "none";
}
function switchToSignup() {
    closeLogin();
    openSignup();
}
function switchToLogin() {
    closeSignup();
    openLogin();
}

/* ================= MAP ================= */
let map, marker;

function initMap() {
    if (map) return;

    map = L.map("map").setView([10.7905, 78.7047], 13);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "© OpenStreetMap"
    }).addTo(map);

    map.on("click", e => setMarker(e.latlng.lat, e.latlng.lng));
}

function setMarker(lat, lng) {
    if (marker) map.removeLayer(marker);

    marker = L.marker([lat, lng]).addTo(map);

    document.getElementById("signup-lat").value = lat;
    document.getElementById("signup-lng").value = lng;
}

/* ================= AUTO LOCATION ================= */
function detectLocation() {
    if (!navigator.geolocation) {
        alert("Geolocation not supported.");
        return;
    }

    navigator.geolocation.getCurrentPosition(
        pos => {
            const lat = pos.coords.latitude;
            const lng = pos.coords.longitude;
            setMarker(lat, lng);
            map.setView([lat, lng], 15);
        },
        err => {
            console.warn("Location denied:", err.message);
        }
    );
}

/* ================= SIGNUP ================= */
function signup() {
    const email = document.getElementById("signup-email").value.trim();
    const username = document.getElementById("signup-username").value.trim();
    const password = document.getElementById("signup-password").value;
    const lat = parseFloat(document.getElementById("signup-lat").value);
    const lng = parseFloat(document.getElementById("signup-lng").value);

    if (!email || !username || !password) {
        alert("Please fill all fields.");
        return;
    }

    if (isNaN(lat) || isNaN(lng)) {
        alert("Please select your location on the map.");
        return;
    }

    const btn = event.target;
    btn.disabled = true;
    btn.innerText = "Creating...";

    fetch(API + "/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, username, password, lat, lng })
    })
    .then(async res => {
        const data = await res.json();
        if (!res.ok) throw data;
        return data;
    })
    .then(data => {
        alert(
            "Signup successful!\n\nAssigned Streets:\n" +
            (data.assigned_streets || []).join(", ")
        );

        closeSignup();
        openLogin();
    })
    .catch(err => {
        alert(err.error || "Signup failed.");
        console.error(err);
    })
    .finally(() => {
        btn.disabled = false;
        btn.innerText = "Sign Up";
    });
}

/* ================= LOGIN ================= */
function login() {
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    if (!email || !password) {
        alert("Enter email and password.");
        return;
    }

    const btn = event.target;
    btn.disabled = true;
    btn.innerText = "Logging in...";

    fetch(API + "/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",   // ⭐ ADD THIS
    body: JSON.stringify({ email, password })
})

    .then(async res => {
        const data = await res.json();
        if (!res.ok) throw data;
        return data;
    })
    .then(data => {
        localStorage.setItem(
            "assigned_streets",
            JSON.stringify(data.assigned_streets || [])
        );

        localStorage.setItem("username", data.username);

        window.location.href = "/dashboard";
    })
    .catch(err => {
        alert(err.error || "Login failed");
        console.error(err);
    })
    .finally(() => {
        btn.disabled = false;
        btn.innerText = "Login";
    });
}

/* ================= LOGOUT ================= */
function logout() {
    localStorage.clear();
    window.location.href = "/";
}
function openForgot() {
    document.getElementById("loginModal").style.display = "none";
    document.getElementById("forgotModal").style.display = "flex";
}

function closeForgot() {
    document.getElementById("forgotModal").style.display = "none";
}

function backToLogin() {
    document.getElementById("forgotModal").style.display = "none";
    document.getElementById("loginModal").style.display = "flex";
}

function sendReset() {
    const email = document.getElementById("reset-email").value;
    alert("Reset link sent to " + email);
    closeForgot();
}
