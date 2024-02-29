<div align="center">

# TheDartbot
This codebase is of [Dartbot](https://t.me/TheDartBot) running on python3 with an sqlite database. it can be used for capturing and preserving data associated with [dice](https://core.telegram.org/api/dice) transmitted within group chats on Telegram.
</div>

## Table of Contents

- [Introduction](#introduction)
- [Prerequisites](#prerequisites)
  - [Running with Docker](#running-with-docker)
  - [Running Locally / without docker](#running-locally)
  - [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

### Running with Docker
- Install docker from [here](https://docs.docker.com/engine/install/)

- Clone the repo  
```
git clone https://github.com/HyperNB/Telegram-TheDartbot.git
```

- Create docker volume
```
docker volume create data
```

- Build and run docker image
```
docker build ./Telegram-TheDartbot -t dart && docker run -v data:/dart --restart unless-stopped dart
```

### Running Locally

- Clone the repo  
```
git clone https://github.com/HyperNB/Telegram-TheDartbot.git
```
- Install Python dependencies

```
pip3 install -r requirements.txt
```

- Run the script
```
python3 dart.py
```

## Configuration
create .env file in root path and inside .env add bot token
```
BOT_TOKEN="12345567890"
```

# Contributing

First of all, thank you for considering contributing! 🎉

## How Can You Contribute?

- **Report Bugs:** If you encounter any issues, please use the GitHub issue tracker to report them.

- **Request Features:** Feel free to use the issue tracker to suggest new features or improvements.

- **Contribute Code:** If you want to contribute code, please fork the repository, create a feature branch, and submit a pull request.

## License

See the [LICENSE.md](LICENSE) file for details.
