
const form = document.getElementById("prediction-form");
const resultPanel = document.getElementById("result");
const errorMessage = document.getElementById("error-message");
const predictButton = document.getElementById("predict-btn");
const refreshButton = document.getElementById("refresh-btn");

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const team1 = document.getElementById("team1").value.trim();
    const team2 = document.getElementById("team2").value.trim();
    const matchFormat = document.getElementById("match-format").value;

    resultPanel.classList.add("hidden");
    errorMessage.textContent = "";

    if (!team1 || !team2) {
        errorMessage.textContent = "Please enter both team names.";
        return;
    }

    if (team1.toLowerCase() === team2.toLowerCase()) {
        errorMessage.textContent = "Please select two different teams.";
        return;
    }

    predictButton.disabled = true;
    predictButton.textContent = "Analyzing Match...";

    try {
        const response = await fetch("/api/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                team1: team1,
                team2: team2,
                format: matchFormat,
                year: 2027,
                venue: "Unknown"
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Prediction failed.");
        }

        document.getElementById("result-team1").textContent = data.team1;
        document.getElementById("result-team2").textContent = data.team2;

        document.getElementById("probability1").textContent =
            data.team1_win_probability + "%";

        document.getElementById("probability2").textContent =
            data.team2_win_probability + "%";

        document.getElementById("bar-team1").style.width =
            data.team1_win_probability + "%";

        document.getElementById("bar-team2").style.width =
            data.team2_win_probability + "%";

        resultPanel.classList.remove("hidden");

    } catch (error) {
        errorMessage.textContent = error.message;

    } finally {
        predictButton.disabled = false;
        predictButton.innerHTML = "Generate Prediction →";
    }
});


// Refresh Button
refreshButton.addEventListener("click", () => {
    form.reset();

    resultPanel.classList.add("hidden");
    errorMessage.textContent = "";

    document.getElementById("probability1").textContent = "0%";
    document.getElementById("probability2").textContent = "0%";

    document.getElementById("bar-team1").style.width = "50%";
    document.getElementById("bar-team2").style.width = "50%";

    predictButton.disabled = false;
    predictButton.innerHTML = "Generate Prediction →";
});
