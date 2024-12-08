class MultiplayerGameManager extends GameManager {
  async loadGameState() {
    try {
      await super.loadGameState();
      this.isMultiplayer = document.body.classList.contains("multiplayer");

      if (this.isMultiplayer && !this.gameState.player2) {
        this.startWaitingForPlayer();
      }
    } catch (error) {
      this.handleError(error);
    }
  }

  startWaitingForPlayer() {
    const waitingSection = document.createElement("div");
    waitingSection.innerHTML = `
        <p>Waiting for Player 2 to join...</p>
        <p>Share this link: ${window.location.href}</p>
      `;
    document.getElementById("multiplayer-section").appendChild(waitingSection);
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
