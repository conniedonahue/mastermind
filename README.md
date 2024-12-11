# Mastermind

## Docker instructions

### Prerequisites:

- Docker and Docker Compose installed on your machine
- Git installed on your machine

### Development Environment

1. _Clone this repo:_ Open a Terminal and change the current working directory to where you'd like the cloned repository to be stored. Use following git command: `git clone https://github.com/conniedonahue/mastermind.git`.
2. _Enter the directory in your terminal:_ `cd mastermind`
3. _Start the Dev Server:_ `docker-compose up` Note:
4. _Access the Application:_ After running the `docker-compose` command, open up your browser to `http://localhost:5001`

5. _Access the User Databse:_

- through Docker's psql: `docker-compose exec db psql -U user -d dev_db`
- or through your local psql: `psql -h localhost -p 5432 -U user -d dev_db`

Some helpful Docker commands while using the app:

To close the docker server: `docker-compose down`
To view logs: `docker-compose logs`
To continously follow the logs: `docker-compose logs -f`
To see all Docker container-ids: `docker ps`
To create database backup: `docker-compose exec db pg_dump -U user dev_db > backup.sql`
To restore database: `docker-compose exec -T db psql -U user dev_db < backup.sql`

### Production Environment

In a real life deployment, I would ask you to create your own .env files by running these commands:

```
cp .env.development.example .env.development
cp .env.production.example .env.production
```

and then edit the files with the correct secret information. For ease of turnover for this project, I amd using dummy environmental variables in my docker-compose.prod.yml. It will load up a production server, but it won't connect you to my Heroku deployed server and postgress database (more on that below).

To access the production server, complete steps 1-2 above, and then:

1. _Start the Production Server:_ `docker-compose -f docker-compose.prod.yml up --build`
2. _Access the Application:_ After running the `docker-compose` command, open up your browser to `http://localhost:8000`
3. _Access the User Databse:_

- through Docker's psql: `docker-compose exec db psql -U user -d prod_db`
- or through your local psql: `psql -h localhost -p 5432 -U user -d prod_db`

### Troubleshooting:

- Port Conflicts

  - Make sure no other services are using ports 5001, 8000, or 5432
    - If they are, change the left side of the port mapping in the docker-compose.yml files. e.g. ports: "5001:5000" -> "5011:5000"
  - Stop local PostgreSQL if running: e.g. `brew services stop postgresql`

- Database Connection Issues
  - Verify the database container is running: docker-compose ps
  - Check database logs: docker-compose logs db
  - Ensure environment variables are correctly set

## Local Python instructions

To run this server locally using Python, do the following:

1. _Install pyenv:_ If you don't already have it, pyenv helps you manage different python versions on your local machine. You'll need to know which shell you're currently using, if you don't, run: `echo $SHELL` in your terminal.
   Here's how to download pyenv with Homebrew:

```
# Using Homebrew
brew update
brew install pyenv

# Add to your shell (for zsh)
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc

source ~/.zshrc

# Add to your shell (for bash)
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc

source ~/.bashrc
echo 'if [ -f ~/.bashrc ]; then source ~/.bashrc; fi' >> ~/.bash_profile

```

2. _Install Python 3.12.0 and pipenv:_

```
pyenv install 3.12.0
pyenv global 3.12.0  # Set as default Python version
pip install pipenv
```

3. _Set up your project_:

```
# Navigate to your project directory
cd your-project-directory

# Initialize pipenv with Python 3.12
pipenv --python 3.12.0

# Install dependencies from your Pipfile
pipenv install

# Install dev dependencies if needed
pipenv install --dev

# Initiate the virtual environment
pipenv shell

# Start postgres
brew services start postgres

# Run the server
make dev
```

Note the project's `makefile` to find other helpful commands.

## Design considerations

Here is an early sketch of the system design.
![System-Design](./assets/images/early-system-sketch.png)

### Functional Requirements

- Can be played by user against computer
- Secret Code must be pulled from Random generator API
- Default rules:
  - Player must guess a four digit number (0-7)
  - Player has 10 Attempts
  - Game provides feedback at the end of the turn
    - number of correct numbers and number of correct positions
- User Interface:
  - Ability to guess the combinations of 4 numbers
  - Ability to view the history of guesses and their feedback
  - The number of guesses remaining is displayed
  - NOTE: UI will be bare-bones since this is a backend review

### Nonfunctional Requirements

- Prioritize availability over consistency:

  - we want fast response times (no waiting for global syncs, session-based data)
  - fault tolerance if a node goes down
  - game is casual and simple enough to allow for some inconsistencies to score etc.
  - Multiplayer (extension) will highlight this trade-off

- Low latency (<300 msec)

  - websockets for multiplayer???
  - ultimately the front end is a little laggy

- Scalable to 1M active sessions

  - (Note, this is my own suggestion)
  - Early estimate of _Default Session_ Size = 248 bytes
    - 246 MB for cache of 1M active sessions
  - Updated Estimate:
    - 514 MB for 1M active sessions
    - This would go up with extensions (added attempts)

### Core Entities

- Sessions
- Users (players)

### Data Flow

- User lands on home page
- Adjust settings (extensions)
- Start (game) session
- (Optional: Player2 joins)
- Results at Game End -> Database

### Python

I decided to write the backend of this project in Python, following the suggestion from the prompt to use a backend-focused language (my primary tech stack is JavaScript/Node, although I have worked with python in the past). Development was lightning quick Python's easy database integration (SQLAlchemy's ORM, Redis Library), and out-of-the-box testing.

### Flask Web Framework

The backend is built using Flask. It's lightweight, unopinionated framework made it easy to set up routes and handle HTTP requests, and it has template system for HTML rendering.

### Session Manager

The first major design decision I had to make was how to handle game state. At first, I was considering making a stateless, RESTful API that stored game state in the front end using JWT tokens since I had estimated the game state to be less that 500 bytes. However, I really wanted to create a multiplayer game, and I was worried about state synchronization with the need for clients to send their JWTs back to the server.

So I opted for a session-based architecture. Session data is stored locally in a cache (in memory in dev and in a Redis cloud instance in prod) and updated with each guess. This meets my nonfunctional requirement of low-latency, allowing for fast retrievals and updates of game state while still providing consistency for multiplayer games

### User Database

I added a User Database to keep track of User's gamme history. It currently has one model, User, that looks like this:

- User:
  - id (primary key)
  - username (str)
  - games_won (int)
  - games_lost (int)
  - total_games_played (int)
  - created_at (DateTime)

The database is updated at two points (synchronously): upon entering a game and when the session status changes from `"active"`.

### Heroku Deployment

I've deployed this application on Heroku, available here:
`https://connor-donahue-mastermind-5f53191544e3.herokuapp.com/`

I also used Heroku's built-in Postgres database for the User Database.

## Production Readiness Checklist

### 🔒 Security

- [x] Environment-based configuration
- [x] Input validation for guesses
- [x] Database connection security
- [ ] Implement rate limiting
- [ ] Add HTTPS support
- [ ] Add security headers
- [ ] Add CSRF protection
- [ ] Sanitize user inputs in templates

### 🚀 Performance

- [x] Redis Session Caching
  - Configured for 1M continuous sessions or 514MB
  - 1-hour cache retention
- [ ] Configure User_DB for async operations
- [ ] Add Message Queue to handle User_DB Operations
- [ ] Configure Gunicorn workers

### 📊 Reliability

- [x] Comprehensive error handling
- [x] Detailed error responses in OpenAPI spec
- [x] Containerized with Docker
- [x] Add Random API failover strategy
- [ ] Graceful error pages for front end
- [ ] Add database failover strategy
- [ ] Implement `/health` check endpoint

### 🧪 Testing

- [x] Unit tests for routing and logic
- [x] Session Manager Tests
- [ ] Extensions Tests
- [ ] User Database Tests
- [ ] Error scenario testing
- [ ] Performance/load testing
- [ ] End-to-end testing
- [ ] Contract testing

### 📝 Documentation

- [x] OpenAPI specification
- [x] Docker Setup Instructions
- [ ] Add performance and scaling recommendations

### 🔍 Observability

- [x] Basic logging
- [ ] Add request tracing
- [ ] Configure application monitoring

### ⚙️ Configuration

- [x] Environment-based port configuration
- [ ] Logging configuration

### 🌟 Extensions

- [x] Increase Allowed Attempts
- [x] Increase # of digits in codeword
- [x] Dev / Prod environment
- [x] Deployed to Heroku
- [x] Session Manager Cache
- [x] User Database
- [x] Logging

### 🌟 Potential Features Roadmap

- [ ] User Authentication System
  - User registration
  - Secure login / OAuth etc.
- [ ] Wordleify
  - Color feedback for users
  - (I left this in as a possible extension to tackle during intv)
- [ ] Asynch Database Configuration
- [ ] Leaderboard
  - User_DB could keep track of top 10 payers with most game_wins

### Next Steps for Production Readiness

1. Add testing of User DB
2. Add more unit tests of the extensions
3. Session Failover
4. Rate Limiting
5. Message Queue
