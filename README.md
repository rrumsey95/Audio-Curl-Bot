# Audio-Curl-Bot

Audio-Curl-Bot is a Discord music bot written in Python that can join voice channels, play YouTube playlists, and manage a song queue with skip, pause, resume, and leave commands. It uses [discord.py](https://github.com/Rapptz/discord.py) and [yt-dlp](https://github.com/yt-dlp/yt-dlp) for audio streaming.

## Features

- Join your voice channel with `/join`
- Play an entire YouTube playlist with `/play_playlist`
- View the current queue with `/queue`
- Skip, pause, and resume playback with `/skip`, `/pause`, and `/resume`
- Leave the voice channel and clear the queue with `/leave`
- Per-guild song queues

## Requirements

- Python 3.8+
- FFmpeg (must be installed and available in your system PATH)
- Discord bot token

## Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/Audio-Curl-Bot.git
   cd Audio-Curl-Bot
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
4. **Run the bot:**
   ```sh
   python bot.py
   ```

## Usage

- Invite the bot to your server using the OAuth2 URL generated in the Discord Developer Portal.
- Join a voice channel and use the `/join` command to have the bot join you.
- Use the `/play_playlist` command followed by a YouTube playlist URL to play a playlist.
- Manage the song queue with `/queue`, `/skip`, `/pause`, and `/resume`.
- Use the `/leave` command to make the bot leave the voice channel and clear the queue.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any bugs, features, or improvements.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
