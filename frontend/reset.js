const API = "http://127.0.0.1:5000";

// get token or email from URL
const params = new URLSearchParams(window.location.search);
const token = params.get("token"); // if using token-based reset
const email = params.get("email"); // if using direct email-based reset

function reset() {
    const newPassword = document.getElementById("new-password").value;

    if (!newPassword) {
        document.getElementById("reset-msg").innerText = "Password is required";
        return;
    }

    fetch(API + "/reset-password", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            token: token,      // or email if you use email-based reset
            password: newPassword
        })
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("reset-msg").innerText =
            data.message || data.error;

        if (data.message) {
            setTimeout(() => {
                window.location.href = "index.html";
            }, 2000);
        }
    })
    .catch(() => {
        document.getElementById("reset-msg").innerText = "Server error";
    });
}
