import requests
import os
import subprocess

repoName = os.environ["GITHUB_REPOSITORY"]
githubToken = os.environ["GITHUB_TOKEN"]

authHeader = f"Authorization: Bearer {githubToken}"

headers = [
    "Accept: application/vnd.github+json",
    authHeader,
    "X-GitHub-Api-Version: 2022-11-28"
]

print("Downloading last data artifact")

resp = requests.get(f"https://api.github.com/repos/{repoName}/actions/artifacts?name=data&per_page=1", headers = headers).json()

print("Last response:", resp)

url = resp["artifacts"][0]["archive_download_url"]
subprocess.run(["wget", "--header", authHeader, "-O", "tmp_data.zip"])
subprocess.run(["unzip", "tmp_data.zip", "-d", "data"])
os.remove("tmp_data.zip")
