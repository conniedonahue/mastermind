class GameManager {
    constructor() {
      this.state = {
        sessionId: null,
        gameConfig: null,
        gameState: null,
      };
      this.initializeEventListeners();
    }
  
    initializeEventListeners() {
      // Handle game start
      const startGameForm = document.getElementById("game-settings-form");
      startGameForm.addEventListener("submit", this.handleGameStart.bind(this));
  
      // Handle guess submission
      const guessForm = document.getElementById("guess-form");
      guessForm.addEventListener("submit", this.handleGuessSubmission.bind(this));
    }
  
    async handleGameStart(event) {
      event.preventDefault();
  
      // Collect game settings
      const allowedAttempts = document.getElementById("allowed_attempts").value;
      const codeLength = document.getElementById("code_length").value;
      const wordleify = document.getElementById("wordle_ify").checked;
  
      const gameConfig = {
        allowed_attempts: parseInt(allowedAttempts),
        code_length: parseInt(codeLength),
        wordleify,
      };
  
      try {
        const response = await fetch("/game", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(gameConfig),
        });
  
        const data = await response.json();
  
        if (data.session_id) {
          this.state.sessionId = data.session_id;
          this.state.gameConfig = gameConfig;
          this.navigateToGamePage();
        } else {
          throw new Error("Failed to create game.");
        }
      } catch (error) {
        console.error("Game creation error:", error);
        alert("Error creating game.");
      }
    }
  
    navigateToGamePage() {
      // Hide welcome page and show game page
      document.getElementById("welcome-page").style.display = "none";
      document.getElementById("game-page").style.display = "block";
  
      // Initialize game UI with data
      this.updateGameUI();
    }
  
    async handleGuessSubmission(event) {
      event.preventDefault();
  
      const guessInput = document.getElementById("guess-input");
      const guess = guessInput.value;
  
      try {
        const response = await fetch(`/game/${this.state.sessionId}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ guess }),
        });
  
        const data = await response.json();
        this.state.gameState = data.game_state;
        this.updateGameUI();
        guessInput.value = ""; // Clear input
      } catch (error) {
        console.error("Error submitting guess:", error);
        alert("Error processing guess.");
      }
    }
  
    updateGameUI() {
      const { gameState } = this.state;
  
      if (!gameState) return;
  
      // Update remaining guesses
      const remainingGuessesEl = document.getElementById("remaining-guesses");
      remainingGuessesEl.textContent = gameState.remaining_guesses;
  
      // Update guess history
      const guessHistoryEl = document.getElementById("guess-history");
      guessHistoryEl.innerHTML = gameState.guesses
        .map(
          (guess) =>
            `<div>Guess: ${guess.guess.join(" ")} | Correct: ${guess.correct_numbers} | Positions: ${guess.correct_positions}</div>`
        )
        .join("");
  
      // Handle game win/loss
      if (gameState.status === "won") {
        alert("You won!");
      } else if (gameState.status === "lost") {
        alert("You lost!");
      }
    }
  }
  
  // Initialize on DOM load
  document.addEventListener("DOMContentLoaded", () => {
    new GameManager();
  });
  