# Audio-Curl-Bot

Audio-Curl-Bot is a Discord music bot written in Python that can join voice channels, play YouTube playlists, and manage a song queue with skip, pause, resume, shuffle, clear, and leave commands. It uses [discord.py](https://github.com/Rapptz/discord.py) and [yt-dlp](https://github.com/yt-dlp/yt-dlp) for audio streaming.

## Features

- Join your voice channel with `/join`
- Play an entire YouTube playlist with `/play_playlist`
- View the current queue with `/queue`
- Skip, pause, and resume playback with `/skip`, `/pause`, and `/resume`
- Shuffle the current queue with `/shuffle`
- Clear the queue with `/clear_queue`
- Leave the voice channel and clear the queue with `/leave`
- Per-guild song queues
- Error handling for voice and playback operations
- Checks to prevent duplicate voice connections
- **Supports YouTube login cookies** for private/age-restricted playlists (see below)

## Requirements

- Python 3.8+
- FFmpeg (must be installed and available in your system PATH)
- Discord bot token
- [python-dotenv](https://pypi.org/project/python-dotenv/) (for loading environment variables)
- (Optional) `cookies.txt` file for YouTube login cookies

## Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/Audio-Curl-Bot.git
   cd Audio-Curl-Bot/src
   ```
2. **Install the dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
3. **Set up your Discord bot token:**
   - Create a `.env` file in the root of the project.
   - Add your bot token to the `.env` file:
     ```env
     DISCORD_BOT_TOKEN=your_bot_token_here
     ```
4. **(Optional) Add YouTube cookies:**
   - Export your YouTube cookies as `cookies.txt` (see below).
   - Place `cookies.txt` in the same directory as your bot or set the `YTDLP_COOKIES` environment variable to its path.

5. **Run the bot:**
   ```sh
   python Audio-Curl-Bot.py
   ```

## Directory and File Structure 
```
Audio-Curl-Bot/
│
├── src/
│   ├── Audio-Curl-Bot.py
│   └── bot/
│       ├── __init__.py
│       ├── core.py
│       ├── queue.py
│       └── commands.py
├── requirements.txt
├── .env
└── ...
```

## Usage

- Invite the bot to your server using the OAuth2 URL generated in the Discord Developer Portal.
- Join a voice channel and use the `/join` command to have the bot join you.
- Use the `/play_playlist` command followed by a YouTube playlist URL to play a playlist.
- Manage the song queue with `/queue`, `/skip`, `/pause`, `/resume`, `/shuffle`, and `/clear_queue`.
- Use the `/leave` command to make the bot leave the voice channel and clear the queue.

## Using YouTube Login Cookies

To play private or age-restricted playlists, export your YouTube cookies:

1. **Install a browser extension:**
   - [Get cookies.txt](https://chrome.google.com/webstore/detail/get-cookiestxt/hnmpcagpplmpfojmgmnngilcnanddlhb) (Chrome/Edge)
   - [cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/) (Firefox)
2. **Log in to YouTube** in your browser.
3. **Export cookies** as `cookies.txt` using the extension.
4. **Place `cookies.txt`** in your bot directory or set the `YTDLP_COOKIES` environment variable to its path.

**Never commit your cookies file to version control.**

## Using Environment Variables and YouTube Cookies with AWS Secrets Manager

You can securely store your `.env` file (Discord bot token and other secrets) and your `cookies.txt` file (for YouTube login cookies) in **AWS Secrets Manager**. This is especially useful for cloud deployments (e.g., EC2) and helps keep sensitive data out of your repository.

### How to Use AWS Secrets Manager

1. **Store your secrets in AWS Secrets Manager:**
   - Create a secret named (for example) `audio-curl-bot-env` for your `.env` file contents.
   - Create a secret named (for example) `audio-curl-bot-cookies` for your `cookies.txt` contents.

2. **Configure your infrastructure (e.g., Terraform, user data script) to fetch these secrets:**
   - On instance startup, retrieve the secrets and write them to `/home/ubuntu/.env` and `/home/ubuntu/cookies.txt`.
   - Example snippet for your EC2 user data script:
     ```bash
     #!/bin/bash
     cat > /home/ubuntu/.env <<EOF
     ${env_file}
     EOF

     cat > /home/ubuntu/cookies.txt <<EOF
     ${cookies_file}
     EOF
     ```
   - Make sure your application or Docker container uses these files as usual.

3. **Set the `YTDLP_COOKIES` environment variable** (if your cookies file is not in the default location):
   ```env
   YTDLP_COOKIES=/home/ubuntu/cookies.txt
   ```

## Contributing

Contributions are welcome! Please see the [CONTRIBUTING.md](.github/CONTRIBUTING.md) file for guidelines on how to contribute, including how to set up your development environment, coding standards, and the pull request process.

- Use [GitHub Issues](../../issues) for feature requests and bug reports.
- For security issues, please refer to the [SECURITY.md](.github/SECURITY.md) file and report vulnerabilities privately.
- All contributors are expected to follow the [Code of Conduct](.github/CODE_OF_CONDUCT.md).

## Issue and Pull Request Templates

- When opening a new issue, please use the provided [bug report](.github/ISSUE_TEMPLATE/bug_report.md) or [feature request](.github/ISSUE_TEMPLATE/feature_request.md) templates.
- Pull requests should use the [pull request template](.github/PULL_REQUEST_TEMPLATE.md) and ensure all checklist items are addressed.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
