# Cube-qa-bot

為了煩躁的 國泰 Cube 卡 權益查詢而生的 Telegram Bot

## Prerequisites

- Docker and Docker Compose installed on your machine
- OpenAI API key
- Telegram Bot Token

## Setup

1. Clone this repository:

```bash
git clone https://github.com/Crazycurly/Cube-qa-bot.git
cd Cube-qa-bot
```

2. Create a `.env` file in the root directory of the project:

```bash
touch .env
```

3. Open the `.env` file and add your OpenAI API key and Telegram Bot Token:

```env
OPENAI_API_KEY=your_openai_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
```

Replace `your_openai_api_key` and `your_telegram_bot_token` with your actual API keys.

4. Build and run the Docker container:

```bash
docker-compose up
```

## Usage

Once the bot is running, you can interact with it on Telegram. Send a `/start` command to initiate a conversation.