class GameManager {
  constructor() {
    this.gameState = null;
    this.sessionId = null;
    this.initializeEventListeners();
  }

  async createGame(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    try {
      const response = await fetch("/game", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      console.log("data: ", data);

      if (data.session_id) {
        this.sessionId = data.session_id;
        this.updateGameUI(data);
        console.log("this.sessionId: ", this.sessionId);
        return (window.location.href = `/game/${this.sessionId}`);
      } else {
        throw new Error("Game creation failed");
      }
    } catch (error) {
      console.error("Error creating game:", error);
      throw error;
    }
  }

  async loadGameState() {
    console.log("loading....");
    if (!this.sessionId) {
      this.sessionId = window.location.pathname.split("/").pop();
    }
    const response = await fetch(`/game/${this.sessionId}/state`, {
      method: "GET",
    });
    const data = await response.json();
    this.gameState = data.game_state;
    console.log("gameState: ", this.gameState);
  }

  updateGameUI(gameState) {
    // Update entire game state
    console.log("Updating game UI:", gameState);

    // Update remaining guesses
    const remainingGuessesEl = document.getElementById("remaining-guesses");
    if (remainingGuessesEl) {
      remainingGuessesEl.textContent = gameState.remaining_guesses;
    }

    // Populate existing guesses
    const guessHistoryEl = document.getElementById("guess-history");
    if (guessHistoryEl && gameState.guesses) {
      guessHistoryEl.innerHTML = gameState.guesses
        .map(
          (guess) => `
                <div class="guess-result">
                    Guess: ${guess.guess.join(" ")} 
                    | Correct Numbers: ${guess.correct_numbers} 
                    | Correct Positions: ${guess.correct_positions}
                </div>
            `
        )
        .join("");
    }

    // Handle game end conditions
    if (gameState.status === "won") {
      this.handleGameWon();
    } else if (gameState.status === "lost") {
      this.handleGameLost();
    }
  }

  async submitGuess(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    try {
      const response = await fetch(`/game/${this.sessionId}`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      console.log("data: ", data);

      if (data.guesses) {
        this.updateGuessUI(data.guesses[data.guesses.length - 1]);
        this.updateGameStateUI(data);
        console.log("updated");
        return;
      } else if (data.error) {
        throw new Error(data.error);
      }
    } catch (error) {
      console.error("Error submitting guess:", error);
      throw error;
    }
  }

  updateUIForNewGame(config) {
    // Update UI to show game has started
    // This might involve showing the game board, hiding welcome screen, etc.
    console.log("New game created with config:", config);
  }

  updateGuessUI(guessData) {
    // Add the latest guess to the history
    const guessHistoryEl = document.getElementById("guess-history");
    if (guessHistoryEl) {
      const guessResultEl = document.createElement("div");
      guessResultEl.classList.add("guess-result");
      guessResultEl.innerHTML = `
                Guess: ${guessData.guess.join(" ")} 
                | Correct Numbers: ${guessData.correct_numbers} 
                | Correct Positions: ${guessData.correct_positions}
            `;
      guessHistoryEl.appendChild(guessResultEl);
    }
  }

  updateGameStateUI(gameState) {
    // Update remaining guesses
    const remainingGuessesEl = document.getElementById("remaining-guesses");
    if (remainingGuessesEl) {
      remainingGuessesEl.textContent = gameState.remaining_guesses;
    }

    // Handle game end conditions
    if (gameState.status === "won") {
      this.handleGameWon();
    } else if (gameState.status === "lost") {
      this.handleGameLost();
    }
  }

  handleGameWon() {
    alert("Congratulations! You won the game!");
    // Additional win game logic
  }

  handleGameLost() {
    alert("Game over! You ran out of guesses.");
    // Additional lost game logic
  }

  initializeEventListeners() {
    // Welcome page game start button
    const startGameForm = document.getElementById("game-settings-form");
    if (startGameForm) {
      startGameForm.addEventListener("submit", this.createGame.bind(this));
    }

    // Game page guess submission
    const guessForm = document.getElementById("guess-form");
    if (guessForm) {
      guessForm.addEventListener("submit", this.submitGuess.bind(this));
    }
  }

  async handleGameStart(event) {
    event.preventDefault();

    // Gather game settings from welcome page using selects
    const allowedAttempts = document.getElementById("allowed_attempts").value;
    const codeLength = document.getElementById("code_length").value;
    const wordleify = document.getElementById("wordle_ify").checked;

    try {
      const gameConfig = {
        allowed_attempts: parseInt(allowedAttempts),
        code_length: parseInt(codeLength),
        wordleify: wordleify,
      };

      const result = await this.createGame(gameConfig);
      this.gameState = result;
      this.sessionId = result.sessionId;

      // Navigate to game page or update UI
      window.location.href = `/game/${result.session_id}`;
    } catch (error) {
      console.error("Failed to start game:", error);
      alert("Failed to create game. Please try again.");
    }
  }

  //   async handleGuessSubmission(event) {
  //     event.preventDefault();

  //     const guessInput = document.getElementById("guess-input");
  //     const guess = guessInput.value;

  //     try {
  //       await this.submitGuess(guess);
  //       guessInput.value = ""; // Clear input
  //     } catch (error) {
  //       alert(error.message);
  //     }
  //   }

  // Initialize the game when the page loads
  async init() {
    // Check if we're on the game page
    if (document.getElementById("game-container")) {
      await this.loadGameState();
    }
  }
}

// Initialize the game manager when the page loads
document.addEventListener("DOMContentLoaded", () => {
  const gameManager = new GameManager();
  gameManager.init();
});

function getCookie(name) {
  console.log("cookie: ", document.cookie);
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  console.log("parts: ", parts);
  if (parts.length === 2) return parts.pop().split(";").shift();
  return null;
}
