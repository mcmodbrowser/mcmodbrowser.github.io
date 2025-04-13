import requests
import os
import subprocess
import sys

def validate_response(r):
    if not r.ok:
        print(f"Request to {r.url} failed!")
        print("Raw response:")
        print(r.text)
        sys.exit(1)
    else:
        return r

def write_response_content(r, out):
    with open(out, "wb") as fp:
        for data in resp.iter_content(chunk_size=1024*1024):
            fp.write(data)

repoName = os.environ["GITHUB_REPOSITORY"]
githubToken = os.environ["GITHUB_TOKEN"]

headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {githubToken}",
    "X-GitHub-Api-Version": "2022-11-28",
}

print("Downloading last data artifact")

resp = validate_response(requests.get(f"https://api.github.com/repos/{repoName}/actions/artifacts?name=data&per_page=1", headers=headers)).json()

print("Last response:", resp)

url = resp["artifacts"][0]["archive_download_url"]

resp = validate_response(requests.get(url, headers=headers, stream=True))

write_response_content(resp, "tmp_data.zip")

sys.stdout.flush()
subprocess.run(["unzip", "tmp_data.zip", "-d", "data"])
os.remove("tmp_data.zip")

if os.path.isfile("data/.gitkeep"):
    # Dummy file added by the clear-data workflow
    os.remove("data/.gitkeep")
