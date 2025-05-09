# Teledict Bot

Teledict Bot is a Python-based Telegram bot that provides dictionary functionalities. This README will guide you through setting up the project and running the bot.

## Features
- Look up word definitions.
- Synonyms and antonyms.
- Easy-to-use Telegram interface.

## Prerequisites
- Python 3.8 or higher
- Telegram Bot API token (get it from [BotFather](https://core.telegram.org/bots#botfather))

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/teledict-bot.git
cd teledict-bot
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
```

### 3. Activate the Virtual Environment
- **Windows**:
    ```bash
    venv\Scripts\activate
    ```
- **macOS/Linux**:
    ```bash
    source venv/bin/activate
    ```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Set Up Environment Variables

Refer to the `.env.example` file in the project root for the required environment variables. Copy the file and rename it to `.env`, then update it with your credentials:


### 6. Run the Bot
```bash
python bot.py
```

## Usage
- Start the bot on Telegram.
- Send a word to get its definition, synonyms, or antonyms.

## Contributing
Feel free to fork the repository and submit pull requests.

## License
This project is licensed under the MIT License.
