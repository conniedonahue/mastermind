class GameManager {
  constructor() {
    this.gameState = null;
    this.gameId = null;
    this.initializeEventListeners();
  }

  //   async fetchGameConfig() {
  //     try {
  //       const response = await fetch("/game-config", {
  //         method: "GET",
  //         headers: {
  //           Accept: "application/json",
  //         },
  //       });
  //       return await response.json();
  //     } catch (error) {
  //       console.error("Error fetching game configuration:", error);
  //       throw error;
  //     }
  //   }

  async createGame(gameConfig) {
    try {
      const response = await fetch("/game", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify(gameConfig),
      });

      const data = await response.json();
      console.log("data: ", data);

      if (data.session_id) {
        this.sessionId = data.session_id;
        this.updateGameUI(data);
        return data;
      } else {
        throw new Error("Game creation failed");
      }
    } catch (error) {
      console.error("Error creating game:", error);
      throw error;
    }
  }

  async loadGameState() {
    try {
      const response = await fetch("/game", {
        method: "GET",
        headers: {
          Accept: "application/json",
        },
      });

      const data = await response.json();

      if (data.game_id) {
        this.gameId = data.game_id;
        this.gameState = data;
        this.updateGameUI(data.session);
      }
    } catch (error) {
      console.error("Error loading game state:", error);
    }
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

  async submitGuess(guess) {
    try {
      const response = await fetch("/game/guess", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({ guess }),
      });

      const data = await response.json();

      if (data.guess) {
        this.updateGuessUI(data.guess);
        this.updateGameStateUI(data.game_state);
        return data;
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
                Guess: ${guessData.values.join(" ")} 
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
      startGameForm.addEventListener("submit", this.handleGameStart.bind(this));
    }

    // Game page guess submission
    const guessForm = document.getElementById("guess-form");
    if (guessForm) {
      guessForm.addEventListener(
        "submit",
        this.handleGuessSubmission.bind(this)
      );
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

      // Navigate to game page or update UI
      window.location.href = `/game/${result.session_id}`;
    } catch (error) {
      console.error("Failed to start game:", error);
      alert("Failed to create game. Please try again.");
    }
  }

  async handleGuessSubmission(event) {
    event.preventDefault();

    const guessInput = document.getElementById("guess-input");
    const guess = guessInput.value;

    try {
      await this.submitGuess(guess);
      guessInput.value = ""; // Clear input
    } catch (error) {
      alert(error.message);
    }
  }

  // Initialize the game when the page loads
  async init() {
    // Check if we're on the game page
    // if (document.getElementById("game-container")) {
    //   await this.loadGameState();
    // }
  }
}

// Initialize the game manager when the page loads
document.addEventListener("DOMContentLoaded", () => {
  const gameManager = new GameManager();
  gameManager.init();
});
