const $ = (id) => document.getElementById(id);

const state = {
    teams: [],
    format: "ALL"
};

function escapeHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, char => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    })[char]);
}

async function api(url, options = {}) {
    const response = await fetch(url, options);
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Request failed.");
    return data;
}

function showToast(message) {
    const toast = $("toast");
    toast.textContent = message;
    toast.classList.remove("hidden");
    setTimeout(() => toast.classList.add("hidden"), 2800);
}

function formatQuery() {
    return `?format=${encodeURIComponent(state.format)}`;
}

async function loadOverview() {
    const data = await api(`/api/analytics/overview${formatQuery()}`);
    $("stat-matches").textContent = data.total_matches.toLocaleString();
    $("stat-decided").textContent = data.decided_matches.toLocaleString();
    $("stat-teams").textContent = data.teams_count;
    $("stat-tournaments").textContent = data.tournaments_count;
    $("stat-first-year").textContent = data.first_year ?? "--";
    $("stat-latest-year").textContent = data.latest_year ?? "--";
}

async function loadTeams() {
    const data = await api(`/api/analytics/teams${formatQuery()}`);
    state.teams = data.teams || [];

    $("team-list").innerHTML = state.teams.map(team =>
        `<option value="${escapeHTML(team.team)}"></option>`
    ).join("");

    const top = state.teams.slice(0, 5);
    $("top-teams-body").innerHTML = top.length ? top.map(team => `
        <tr>
            <td><strong>${escapeHTML(team.team)}</strong></td>
            <td>${team.matches}</td>
            <td>${team.wins}</td>
            <td class="win-rate">${team.win_rate}%</td>
        </tr>
    `).join("") : `<tr><td colspan="4">No team data available.</td></tr>`;

    $("all-teams-body").innerHTML = state.teams.map(team => `
        <tr>
            <td><strong>${escapeHTML(team.team)}</strong></td>
            <td>${team.matches}</td>
            <td>${team.wins}</td>
            <td>${team.losses}</td>
            <td class="win-rate">${team.win_rate}%</td>
        </tr>
    `).join("");
}

async function loadTournaments() {
    const data = await api(`/api/analytics/tournaments${formatQuery()}`);
    const tournaments = data.tournaments || [];
    $("tournament-body").innerHTML = tournaments.slice().reverse().map(item => `
        <tr>
            <td><strong>${item.year}</strong></td>
            <td>${escapeHTML(item.format)}</td>
            <td>${item.matches}</td>
            <td>${item.decided_matches}</td>
            <td>${item.teams}</td>
        </tr>
    `).join("") || `<tr><td colspan="5">No tournament data available.</td></tr>`;
}

async function loadDashboard() {
    try {
        await Promise.all([loadOverview(), loadTeams(), loadTournaments()]);
    } catch (error) {
        showToast(error.message);
    }
}

async function analyzeTeam() {
    const team = $("team-search").value.trim();
    if (!team) return showToast("Enter a team name first.");

    try {
        const data = await api(
            `/api/analytics/team/${encodeURIComponent(team)}${formatQuery()}`
        );

        const history = data.tournament_history || [];
        $("team-detail").innerHTML = `
            <strong>${escapeHTML(data.team)} — Historical Record</strong>
            <div class="detail-grid">
                <div class="detail-metric"><span>MATCHES</span><strong>${data.matches}</strong></div>
                <div class="detail-metric"><span>WINS</span><strong>${data.wins}</strong></div>
                <div class="detail-metric"><span>LOSSES</span><strong>${data.losses}</strong></div>
                <div class="detail-metric"><span>WIN RATE</span><strong>${data.win_rate}%</strong></div>
            </div>
            <div class="history-list">
                ${history.map(item => `
                    <span class="history-tag">
                        ${item.year} · ${escapeHTML(item.format)} · ${item.wins} wins / ${item.matches} matches
                    </span>
                `).join("")}
            </div>
        `;
        $("team-detail").classList.remove("hidden");
    } catch (error) {
        showToast(error.message);
    }
}

async function compareTeams() {
    const team1 = $("h2h-team1").value.trim();
    const team2 = $("h2h-team2").value.trim();

    if (!team1 || !team2) return showToast("Enter both teams.");
    if (team1.toLowerCase() === team2.toLowerCase()) {
        return showToast("Choose two different teams.");
    }

    try {
        const params = new URLSearchParams({
            team1, team2, format: state.format
        });
        const data = await api(`/api/analytics/head-to-head?${params}`);

        $("h2h-result").innerHTML = `
            <div class="h2h-score">
                <div class="h2h-team">
                    <span>${escapeHTML(data.team1)}</span>
                    <strong>${data.team1_wins}</strong>
                    <span>WINS</span>
                </div>
                <div class="h2h-center">HEAD TO HEAD<br>${data.matches} MATCHES</div>
                <div class="h2h-team">
                    <span>${escapeHTML(data.team2)}</span>
                    <strong>${data.team2_wins}</strong>
                    <span>WINS</span>
                </div>
            </div>
            <div class="h2h-record">
                Unresolved meetings: ${data.unresolved}
            </div>
            <div class="table-wrap">
                <table>
                    <thead><tr><th>YEAR</th><th>FORMAT</th><th>VENUE</th><th>WINNER</th></tr></thead>
                    <tbody>
                        ${(data.history || []).map(item => `
                            <tr>
                                <td>${item.year ?? "--"}</td>
                                <td>${escapeHTML(item.format)}</td>
                                <td>${escapeHTML(item.venue)}</td>
                                <td>${escapeHTML(item.winner || "No winner")}</td>
                            </tr>
                        `).join("") || `<tr><td colspan="4">No meetings found.</td></tr>`}
                    </tbody>
                </table>
            </div>
        `;
        $("h2h-result").classList.remove("hidden");
    } catch (error) {
        showToast(error.message);
    }
}

async function predictMatch(event) {
    event.preventDefault();

    const team1 = $("team1").value.trim();
    const team2 = $("team2").value.trim();
    const matchFormat = $("match-format").value;
    const error = $("prediction-error");
    const button = $("predict-btn");

    error.textContent = "";
    $("prediction-result").classList.add("hidden");

    if (!team1 || !team2) {
        error.textContent = "Please select both teams.";
        return;
    }
    if (team1.toLowerCase() === team2.toLowerCase()) {
        error.textContent = "Please select two different teams.";
        return;
    }
    button.disabled = true;
    button.textContent = "Analyzing Match...";

    try {
        const data = await api("/api/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                team1, team2, format: matchFormat
            })
        });

        $("result-team1").textContent = data.team1;
        $("result-team2").textContent = data.team2;
        $("probability1").textContent = `${data.team1_win_probability}%`;
        $("probability2").textContent = `${data.team2_win_probability}%`;
        $("bar-team1").style.width = `${data.team1_win_probability}%`;
        $("bar-team2").style.width = `${data.team2_win_probability}%`;
        $("prediction-result").classList.remove("hidden");
    } catch (error) {
        $("prediction-error").textContent = error.message;
    } finally {
        button.disabled = false;
        button.textContent = "Generate Prediction →";
    }
}

$("analytics-format").addEventListener("change", async event => {
    state.format = event.target.value;
    $("team-detail").classList.add("hidden");
    $("h2h-result").classList.add("hidden");
    await loadDashboard();
});

$("team-search-btn").addEventListener("click", analyzeTeam);
$("team-search").addEventListener("keydown", event => {
    if (event.key === "Enter") analyzeTeam();
});
$("h2h-search-btn").addEventListener("click", compareTeams);
$("prediction-form").addEventListener("submit", predictMatch);

$("prediction-form").addEventListener("reset", () => {
    $("prediction-result").classList.add("hidden");
    $("prediction-error").textContent = "";
    $("bar-team1").style.width = "0";
    $("bar-team2").style.width = "0";
});

$("menu-toggle").addEventListener("click", () => {
    $("sidebar").classList.toggle("open");
});

document.querySelectorAll(".nav-link").forEach(link => {
    link.addEventListener("click", () => {
        document.querySelectorAll(".nav-link").forEach(item =>
            item.classList.remove("active")
        );
        link.classList.add("active");
        $("sidebar").classList.remove("open");
    });
});

loadDashboard();
