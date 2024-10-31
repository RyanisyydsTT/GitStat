# GitStat

GitStat is a Discord bot that provides various GitHub-related functionalities. It allows users to fetch information about GitHub users, repositories, and more directly from Discord.

## Features

1. **User Info**: Get detailed information about a GitHub user.
2. **Repository List**: View a paginated list of a user's repositories.
3. **Starred Repository List**: See a paginated list of repositories starred by a user.
4. **Recent Commits**: Fetch and display recent commits for a given repository.
5. **File Download**: Upload a file from a Git repository to file.io and get a download link.

## Commands

- `/userinfo <username>`: Shows GitHub user's profile information.
- `/repolist <username>`: Displays a paginated list of the user's repositories.
- `/starredlist <username>`: Shows a paginated list of repositories starred by the user.
- `/gitcommits <repo_url> [num_commits]`: Displays recent commits for a repository (default: 5 commits).
- `/download <repo_url> <file_path>`: Uploads a file from a Git repository to file.io and provides a download link.


## Dependencies

- nextcord
- pillow
- requests

## Notes

- The bot uses the GitHub API to fetch data, so it's subject to GitHub's rate limiting.
- Some commands may take a moment to respond due to API calls and data processing.
- The bot requires appropriate permissions in your Discord server to function correctly.
- Please edit the token in the main.py file to run the bot.

## License

This Repo is using the MIT License

