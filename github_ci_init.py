import requests
import os
import subprocess

repoName = os.environ["GITHUB_REPOSITORY"]
githubToken = os.environ["GITHUB_TOKEN"]

headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {githubToken}",
    "X-GitHub-Api-Version": "2022-11-28",
}

print("Downloading last data artifact")

resp = requests.get(f"https://api.github.com/repos/{repoName}/actions/artifacts?name=data&per_page=1", headers = headers).json()

print("Last response:", resp)

url = resp["artifacts"][0]["archive_download_url"]
subprocess.run(["wget", "--header", f"Authorization: Bearer {githubToken}", "-O", "tmp_data.zip", url])
subprocess.run(["unzip", "tmp_data.zip", "-d", "data"])
os.remove("tmp_data.zip")

with open(".github_env", "w", encoding="utf8") as fp:
    fp.write("TEST_CONDITION_1=true\n")
    fp.write("TEST_CONDITION_2=true\n")
