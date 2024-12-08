class GameManager {
  constructor() {
    this.gameState = null;
    this.sessionId = null;
    this.initializeEventListeners();
    this.isMultiplayer = null;
  }

  // Game Initialization Methods

  /* Sends config to server
     Receives confirmation
     Redirects to game page
  */
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

      if (data.session_id) {
        this.sessionId = data.session_id;
        this.updateGameUI(data.session_state);

        if (data.join_link) {
          window.location.href = `/multiplayer-game/${this.sessionId}`;
        } else {
          window.location.href = `/game/${this.sessionId}`;
        }
      } else {
        throw new Error("Game creation failed");
      }
    } catch (error) {
      console.error("Error creating game:", error);
      this.handleError(error);
    }
  }

  // Loads game state after redirect
  async init() {
    if (document.getElementById("game-container")) {
      await this.loadGameState();
    }
  }

  /**
   * Pulls sessionId from URL
   * Fetches games state from server
   * Updates UI
   */
  async loadGameState() {
    try {
      // Extract session ID from URL if not already set
      if (!this.sessionId) {
        this.sessionId = window.location.pathname.split("/").pop();
      }

      const response = await fetch(`/game/${this.sessionId}/state`);
      const data = await response.json();

      this.gameState = data.game_state;
      this.isMultiplayer = document.body.classList.contains("multiplayer");

      this.updateGameUI(this.gameState);

      if (this.isMultiplayer && !this.gameState.player2) {
        this.startWaitingForPlayer();
      }
    } catch (error) {
      console.error("Error loading game state:", error);
      this.handleError(error);
    }
  }

  // Game Interaction Methods

  /**
   * Submits guess to server and updates UI with results
   * @param {*} event
   */
  async submitGuess(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    if (this.isMultiplayer) {
      formData.append("player", "player1");
    }

    try {
      const response = await fetch(`/game/${this.sessionId}`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (data.result) {
        this.updateGuessUI(data.result.guesses);
        this.updateGameStateUI(data.result);
      } else if (data.error) {
        throw new Error(data.error);
      }
    } catch (error) {
      console.error("Error submitting guess:", error);
      this.handleError(error);
    }
  }

  startWaitingForPlayer() {
    // Add UI for waiting for player 2
    const waitingSection = document.createElement("div");
    waitingSection.innerHTML = `
      <p>Waiting for Player 2 to join...</p>
      <p>Share this link: ${window.location.href}</p>
    `;
    document.getElementById("multiplayer-section").appendChild(waitingSection);
  }

  handleMultiplayerGameStatus(gameState) {
    switch (gameState.status) {
      case "player1_won":
        alert("You won! Waiting for Player 2 to finish.");
        break;
      case "player1_wins_player2_loses":
        alert("You won! Player 2 did not guess in time.");
        break;
      // Add more multiplayer-specific status handlers
    }
  }

  // UI Update Methods
  updateGameUI(gameState) {
    this.updateRemainingGuesses(gameState);
    this.updateGuessUI(gameState.guesses);
    this.checkGameStatus(gameState);
  }

  updateRemainingGuesses(gameState) {
    const remainingGuessesEl = document.getElementById("remaining-guesses");
    if (remainingGuessesEl) {
      remainingGuessesEl.textContent = gameState.remaining_guesses;
    }
  }

  updateGuessUI(guessData) {
    const guessHistoryEl = document.getElementById("guess-history");

    if (guessHistoryEl) {
      guessHistoryEl.innerHTML = "";

      if (guessData && guessData.length > 0) {
        guessData.forEach((guess) => {
          const guessResultEl = document.createElement("li");
          guessResultEl.innerHTML = `
              Guess: ${guess.guess.join(" ")} 
              | Correct Numbers: ${guess.correct_numbers} 
              | Correct Positions: ${guess.correct_positions}
            `;
          guessHistoryEl.appendChild(guessResultEl);
        });
      }
    }
  }

  updateGameStateUI(gameState) {
    this.updateRemainingGuesses(gameState);
    this.checkGameStatus(gameState);
  }

  checkGameStatus(gameState) {
    if (gameState.status === "won") {
      this.handleGameWon();
    } else if (gameState.status === "lost") {
      this.handleGameLost();
    }
  }

  // Game End Handlers
  handleGameWon() {
    alert("Congratulations! You won the game!");
    // Additional win game logic
  }

  handleGameLost() {
    alert("Game over! You ran out of guesses.");
    // Additional lost game logic
  }

  // Error Handling
  handleError(error) {
    alert(`An error occurred: ${error.message}`);
    console.error(error);
  }

  // Event Listener Setup
  initializeEventListeners() {
    const startGameForm = document.getElementById("game-settings-form");
    if (startGameForm) {
      startGameForm.addEventListener("submit", this.createGame.bind(this));
    }

    const guessForm = document.getElementById("guess-form");
    if (guessForm) {
      guessForm.addEventListener("submit", this.submitGuess.bind(this));
    }
  }
}

// Initialize the game manager when the page loads
document.addEventListener("DOMContentLoaded", () => {
  const gameManager = new GameManager();
  gameManager.init();
});
