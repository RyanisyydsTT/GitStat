from nextcord.ext import commands
import nextcord
import os
import sys
import requests
import math
from PIL import Image
from io import BytesIO
from typing import List
from nextcord.ui import Button, View
import time
import tempfile
import subprocess
intents = nextcord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
REPOS_PER_PAGE = 10

print(
    "____ _ _ ____ _ _\n/ ___(_) |_/ ___|| |_ __ _| |_\n| | _| | __\\___ \\| __/ _` | __|\n| |_| | | |_ ___) | || (_| | |_\n\\____|_|\\__|____/ \\__\\__,_|\\__|"
)
print("v1.0.0 By https://github.com/RyanisyydsTT")


@bot.event
async def on_ready():
    print(f"Bot is ready. Logged in as {bot.user}")


def get_main_color_from_image(image_url):
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    img = img.convert("RGB")

    img.thumbnail((100, 100))

    colors = img.getcolors(img.size[0] * img.size[1])
    filtered_colors = [c for c in colors if sum(c[1]) > 60]

    if filtered_colors:
        sorted_colors = sorted(
            filtered_colors, key=lambda x: (x[0], sum(x[1])), reverse=True
        )
        max_color = sorted_colors[0]
    else:
        max_color = max(colors, key=lambda x: x[0])

    return "#{:02x}{:02x}{:02x}".format(*max_color[1])


@bot.slash_command(name="userinfo", description="Shows Github user's profile")
async def get_user_info(interaction: nextcord.Interaction, username: str):
    response = requests.get(f"https://api.github.com/users/{username}")
    if response.status_code == 200:
        user_data = response.json()
        profile_pic_url = user_data.get("avatar_url")
        profile_pic_main_color = get_main_color_from_image(profile_pic_url)
        embed = nextcord.Embed(
            title=f"{user_data['login']}'s GitHub Profile",
            color=int(profile_pic_main_color[1:], 16),
        )
        embed.set_thumbnail(url=user_data["avatar_url"])
        embed.add_field(name="Name", value=user_data["name"], inline=True)
        embed.add_field(name="Location", value=user_data["location"], inline=True)
        embed.add_field(
            name="Public Repos", value=user_data["public_repos"], inline=True
        )
        embed.add_field(name="Followers", value=user_data["followers"], inline=True)
        embed.add_field(name="Following", value=user_data["following"], inline=True)
        embed.add_field(name="Bio", value=user_data["bio"], inline=False)
        embed.add_field(name="Profile URL", value=user_data["html_url"], inline=False)
        await interaction.response.send_message(embed=embed)
        print(f"[INFO][{time.asctime(time.localtime(time.time()))}] A user requested {username}'s Info.")
    else:
        await interaction.response.send_message(f"User '{username}' not found.")
        print(f"[ERROR][{time.asctime(time.localtime(time.time()))}] A user requested {username}'s Info, but nothing was found")

class RepoListView(View):
    def __init__(self, repos: List[dict], username: str):
        super().__init__(timeout=60)
        self.repos = repos
        self.username = username
        self.current_page = 0
        self.total_pages = math.ceil(len(repos) / REPOS_PER_PAGE)

    @nextcord.ui.button(label="⏪", style=nextcord.ButtonStyle.gray, disabled=True)
    async def previous_button(self, button: Button, interaction: nextcord.Interaction):
        self.current_page -= 1
        await self.update_message(interaction)

    @nextcord.ui.button(label="⏩", style=nextcord.ButtonStyle.gray)
    async def next_button(self, button: Button, interaction: nextcord.Interaction):
        self.current_page += 1
        await self.update_message(interaction)

    async def update_message(self, interaction: nextcord.Interaction):
        embed = self.create_embed()
        self.update_buttons()
        await interaction.response.edit_message(embed=embed, view=self)

    def create_embed(self) -> nextcord.Embed:
        start_idx = self.current_page * REPOS_PER_PAGE
        end_idx = start_idx + REPOS_PER_PAGE
        current_repos = self.repos[start_idx:end_idx]
        req = requests.get(f"https://api.github.com/users/{self.username}")
        user_data = req.json()
        profile_pic_url = user_data.get("avatar_url")
        profile_pic_main_color = self.get_main_color_from_image(profile_pic_url)

        embed = nextcord.Embed(
            title=f"{self.username}'s Repositories (Page {self.current_page + 1}/{self.total_pages})",
            color=int(profile_pic_main_color[1:], 16),
        )
        for repo in current_repos:
            name = f"{repo['name']} [Fork]" if repo["fork"] else repo["name"]

            embed.add_field(name=name, value=repo["html_url"], inline=False)
            embed.set_thumbnail(url=user_data["avatar_url"])
        return embed

    def update_buttons(self):
        self.previous_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page == self.total_pages - 1

    def get_main_color_from_image(self, image_url):
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        img = img.convert("RGB")

        img.thumbnail((100, 100))

        colors = img.getcolors(img.size[0] * img.size[1])
        filtered_colors = [c for c in colors if sum(c[1]) > 60]

        if filtered_colors:
            sorted_colors = sorted(
                filtered_colors, key=lambda x: (x[0], sum(x[1])), reverse=True
            )
            max_color = sorted_colors[0]
        else:
            max_color = max(colors, key=lambda x: x[0])

        return "#{:02x}{:02x}{:02x}".format(*max_color[1])


@bot.slash_command(name="repolist", description="Shows Github user's repositories")
async def get_user_repos(interaction: nextcord.Interaction, username: str):
    await interaction.response.defer()

    response = requests.get(f"https://api.github.com/users/{username}/repos")
    if response.status_code == 200:
        repos = response.json()
        view = RepoListView(repos, username)
        embed = view.create_embed()
        await interaction.followup.send(embed=embed, view=view)
        print(f"[INFO][{time.asctime(time.localtime(time.time()))}] A user requested {username}'s Repo List.")
    else:
        await interaction.followup.send(
            f"User '{username}' not found or has no starred repositories."
        )
        print(f"[ERROR][{time.asctime(time.localtime(time.time()))}] A user requested {username}'s Starred List, but nothing was found")


class StarredRepoListView(View):
    def __init__(self, repos: List[dict], username: str):
        super().__init__(timeout=60)
        self.repos = repos
        self.username = username
        self.current_page = 0
        self.total_pages = math.ceil(len(repos) / REPOS_PER_PAGE)

    @nextcord.ui.button(label="⏪", style=nextcord.ButtonStyle.gray, disabled=True)
    async def previous_button(self, button: Button, interaction: nextcord.Interaction):
        self.current_page -= 1
        await self.update_message(interaction)

    @nextcord.ui.button(label="⏩", style=nextcord.ButtonStyle.gray)
    async def next_button(self, button: Button, interaction: nextcord.Interaction):
        self.current_page += 1
        await self.update_message(interaction)

    async def update_message(self, interaction: nextcord.Interaction):
        embed = self.create_embed()
        self.update_buttons()
        await interaction.response.edit_message(embed=embed, view=self)

    def create_embed(self) -> nextcord.Embed:
        start_idx = self.current_page * REPOS_PER_PAGE
        end_idx = start_idx + REPOS_PER_PAGE
        current_repos = self.repos[start_idx:end_idx]
        req = requests.get(f"https://api.github.com/users/{self.username}")
        user_data = req.json()
        profile_pic_url = user_data.get("avatar_url")
        profile_pic_main_color = self.get_main_color_from_image(profile_pic_url)

        embed = nextcord.Embed(
            title=f"{self.username}'s Starred Repositories (Page {self.current_page + 1}/{self.total_pages})",
            color=int(profile_pic_main_color[1:], 16),
        )
        for repo in current_repos:
            name = f"{repo['name']} [Fork]" if repo["fork"] else repo["name"]

            embed.add_field(name=name, value=repo["html_url"], inline=False)
            embed.set_thumbnail(url=user_data["avatar_url"])
        return embed

    def update_buttons(self):
        self.previous_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page == self.total_pages - 1

    def get_main_color_from_image(self, image_url):
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        img = img.convert("RGB")

        img.thumbnail((100, 100))

        colors = img.getcolors(img.size[0] * img.size[1])
        filtered_colors = [c for c in colors if sum(c[1]) > 60]

        if filtered_colors:
            sorted_colors = sorted(
                filtered_colors, key=lambda x: (x[0], sum(x[1])), reverse=True
            )
            max_color = sorted_colors[0]
        else:
            max_color = max(colors, key=lambda x: x[0])

        return "#{:02x}{:02x}{:02x}".format(*max_color[1])


@bot.slash_command(
    name="starredlist", description="Shows Github user's starred repositories"
)
async def get_user_repos(interaction: nextcord.Interaction, username: str):
    await interaction.response.defer()

    response = requests.get(f"https://api.github.com/users/{username}/starred")
    if response.status_code == 200:
        repos = response.json()
        view = StarredRepoListView(repos, username)
        embed = view.create_embed()
        await interaction.followup.send(embed=embed, view=view)
        print(f"[INFO][{time.asctime(time.localtime(time.time()))}] A user requested {username}'s Starred List.")
    else:
        await interaction.followup.send(
            f"User '{username}' not found or has no starred repositories."
        )
        print(f"[ERROR][{time.asctime(time.localtime(time.time()))}] A user requested {username}'s Starred List, but nothing was found")


@bot.slash_command(name="gitcommits", description="Shows recent git commits for a repository")
async def get_git_commits(interaction: nextcord.Interaction, repo_url: str, num_commits: int = 5):
    await interaction.response.defer()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Clone the repository
            subprocess.run(['git', 'clone', '--depth', str(num_commits), repo_url, temp_dir], check=True, capture_output=True)
            
            # Get the commit log
            result = subprocess.run(['git', '-C', temp_dir, 'log', f'-{num_commits}', '--pretty=format:%h - %s (%an)'], 
                                    check=True, capture_output=True, text=True)
            commits = result.stdout.split('\n')
            
            # Create embed
            embed = nextcord.Embed(title=f"Recent Commits for {repo_url}", color=0x00ff00)
            for commit in commits:
                embed.add_field(name="Commit", value=commit, inline=False)
            
            await interaction.followup.send(embed=embed)
            print(f"[INFO][{time.asctime(time.localtime(time.time()))}] A user requested commits for {repo_url}.")
        except subprocess.CalledProcessError as e:
            await interaction.followup.send(f"Error: Unable to fetch commits. Make sure the repository URL is correct and publicly accessible.")
            print(f"[ERROR][{time.asctime(time.localtime(time.time()))}] Error fetching commits for {repo_url}: {str(e)}")

@bot.slash_command(name="download", description="Uploads a file from a git repository to file.io")
async def upload_git_file(interaction: nextcord.Interaction, repo_url: str, file_path: str):
    await interaction.response.defer()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Clone the repository
            subprocess.run(['git', 'clone', '--depth', '1', repo_url, temp_dir], check=True, capture_output=True)
            
            # Check if file exists
            full_file_path = os.path.join(temp_dir, file_path)
            if not os.path.exists(full_file_path):
                await interaction.followup.send(f"Error: File '{file_path}' not found in the repository.")
                return
            
            # Upload file to file.io
            with open(full_file_path, 'rb') as file:
                response = requests.post('https://file.io', files={'file': file})
            
            if response.status_code == 200:
                file_url = response.json()['link']
                await interaction.followup.send(f"File uploaded successfully. Download link: {file_url}")
                print(f"[INFO][{time.asctime(time.localtime(time.time()))}] File {file_path} from {repo_url} uploaded to file.io.")
            else:
                await interaction.followup.send("Error: Failed to upload file to file.io.")
                print(f"[ERROR][{time.asctime(time.localtime(time.time()))}] Failed to upload file {file_path} from {repo_url} to file.io.")
        
        except subprocess.CalledProcessError as e:
            await interaction.followup.send(f"Error: Unable to clone repository. Make sure the repository URL is correct and publicly accessible.")
            print(f"[ERROR][{time.asctime(time.localtime(time.time()))}] Error cloning repository {repo_url}: {str(e)}")

bot.run("TOKEN")
