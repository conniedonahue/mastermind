class GameManager {
  constructor() {
    this.gameState = null;
    this.sessionId = null;
    this.initializeEventListeners();
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
    console.log("form: ", formData);

    try {
      const response = await fetch("/game", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      console.log("data: ", data);

      if (data.session_id) {
        this.sessionId = data.session_id;
        this.updateGameUI(data.session_state);

        const isMultiplayer = !!data.join_link;
        const url = isMultiplayer
          ? `/multiplayer-game/${this.sessionId}`
          : `/game/${this.sessionId}`;

        window.location.href = `/game/${this.sessionId}`;
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
      this.updateGameUI(this.gameState);
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

    try {
      const response = await fetch(`/game/${this.sessionId}`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (data.result) {
        this.updateGuessUI(data.result.player1.guesses);
        this.updateGameStateUI(data.result);
      } else if (data.error) {
        throw new Error(data.error);
      }
    } catch (error) {
      console.error("Error submitting guess:", error);
      this.handleError(error);
    }
  }

  // UI Update Methods
  updateGameUI(gameState) {
    this.updateRemainingGuesses(gameState);
    this.updateGuessUI(gameState);
    this.checkGameStatus(gameState);
  }

  updateRemainingGuesses(gameState) {
    const remainingGuessesEl = document.getElementById("remaining-guesses");
    if (remainingGuessesEl) {
      remainingGuessesEl.textContent = gameState.player1.remaining_guesses;
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

class MultiplayerGameManager extends GameManager {
  async loadGameState() {
    try {
      await super.loadGameState();
      console.log("multiplayer GS: ", this.gameState);

      if (!this.gameState.player2) {
        this.startWaitingForPlayer();
      } else {
        this.initializeGuessHandlers();
      }
    } catch (error) {
      console.error("Error loading game state:", error);
      this.handleError(error);
    }
  }

  startWaitingForPlayer() {
    const waitingMessage = document.createElement("div");
    waitingMessage.innerHTML = `
        <p>Waiting for Player 2 to join...</p>
        <p>Share this link: ${window.location.href}</p>
      `;
    document.getElementById("waiting-section").appendChild(waitingMessage);

    const interval = setInterval(async () => {
      try {
        const response = await fetch(`/game/${this.sessionId}/state`);
        const data = await response.json();

        if (data.game_state.player2) {
          waitingMessage.innerHTML = "<p>Player 2 has joined!</p>";
          clearInterval(interval);
        }
      } catch (error) {
        console.error("Error checking player status:", error);
      }
    }, 5000);
  }

  // Initialize handlers for Player 1 and Player 2 guesses
  initializeGuessHandlers() {
    const formPlayer1 = document.getElementById("guess-form-player1");
    const formPlayer2 = document.getElementById("guess-form-player2");

    if (formPlayer1) {
      formPlayer1.addEventListener("submit", (event) =>
        this.handleGuessSubmit(event, "player1")
      );
    }

    if (formPlayer2) {
      formPlayer2.addEventListener("submit", (event) =>
        this.handleGuessSubmit(event, "player2")
      );
    }
  }

  // Handle guess submission for both players
  async handleGuessSubmit(event, player) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    formData.append("player", player);

    try {
      const response = await fetch(`/game/${this.sessionId}`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (data.result) {
        // Update UI with the result
        this.updateGuessUI(data.result);
        this.updateRemainingGuesses(data.result, player);
      }
    } catch (error) {
      console.error(`Error submitting ${player} guess:`, error);
    }
  }

  // Update the guess history UI
  updateGuessUI(result) {
    const player1Guesses = result.player1.guesses;
    const player2Guesses = result.player2?.guesses;
    const guesses = player1Guesses.concat(player2Guesses);
    const guessHistoryEl = document.getElementById("guess-history");
    if (guessHistoryEl) {
      guessHistoryEl.innerHTML = "";
      player1Guesses.forEach((guess) => {
        const guessResultEl = document.createElement("li");
        guessResultEl.innerHTML = `
          Player 1 | Guess: ${guess.guess} | Correct Numbers: ${guess.correct_numbers}
          | Correct Positions: ${guess.correct_positions}
        `;
        guessHistoryEl.appendChild(guessResultEl);
      });
      player2Guesses.forEach((guess) => {
        const guessResultEl = document.createElement("li");
        guessResultEl.innerHTML = `
          Player 2 | Guess: ${guess.guess} | Correct Numbers: ${guess.correct_numbers}
          | Correct Positions: ${guess.correct_positions}
        `;
        guessHistoryEl.appendChild(guessResultEl);
      });
    }
  }

  // Update the remaining guesses for the specific player
  updateRemainingGuesses(result, player) {
    const remainingGuesses = result[player]?.remaining_guesses;
    const remainingGuessesEl = document.getElementById(
      `remaining-guesses-${player}`
    );
    const submitButtonEl = document.getElementById(
      `guess-submit-btn-${player}`
    );

    if (remainingGuessesEl) {
      remainingGuessesEl.textContent = remainingGuesses;
    }

    if (submitButtonEl) {
      submitButtonEl.disabled = remainingGuesses === 0;
    }
  }

  checkGameStatus(gameState) {
    super.checkGameStatus(gameState);

    if (this.isMultiplayer) {
      this.handleMultiplayerGameStatus(gameState);
    }
  }

  handleMultiplayerGameStatus(gameState) {
    if (gameState.status === "player1_won") {
      alert("You won! Waiting for Player 2 to finish.");
    } else if (gameState.status === "player1_wins_player2_loses") {
      alert("You won! Player 2 did not guess in time.");
    }
  }
}

// Initialize the game manager when the page loads
document.addEventListener("DOMContentLoaded", () => {
  const gameContainer = document.getElementById("game-container");
  const isMultiplayer = gameContainer?.dataset.isMultiplayer === "True";
  const gameManager = isMultiplayer
    ? new MultiplayerGameManager()
    : new GameManager();
  gameManager.init();
});
