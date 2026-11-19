#!/usr/bin/env python3
import datetime as dt
import html
import json
import os
import subprocess
import urllib.request
from pathlib import Path

USER = "wiyw"
ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
MONO = "Fira Code, SF Mono, Menlo, Consolas, monospace"


def github_token():
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        return token
    try:
        return subprocess.check_output(["gh", "auth", "token"], text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return ""


def api(path):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "wiyw-profile-generator"}
    token = github_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request("https://api.github.com/" + path, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def esc(value):
    return html.escape(str(value), quote=True)


def parse_time(value):
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


def relative_time(value):
    when = parse_time(value)
    seconds = max(0, int((dt.datetime.now(dt.timezone.utc) - when).total_seconds()))
    if seconds < 3600:
        return f"{max(1, seconds // 60)}m ago"
    if seconds < 86400:
        return f"{seconds // 3600}h ago"
    if seconds < 2592000:
        return f"{seconds // 86400}d ago"
    return f"{seconds // 2592000}mo ago"


def collect():
    user = api(f"users/{USER}")
    repos = api(f"users/{USER}/repos?per_page=100&type=owner&sort=pushed")
    language_shares = {}
    for repo in repos:
        languages = api(f"repos/{USER}/{repo['name']}/languages")
        repo_total = sum(languages.values())
        if not repo_total:
            continue
        for language, size in languages.items():
            language_shares[language] = language_shares.get(language, 0) + size * 100 / repo_total
    total = sum(language_shares.values()) or 1
    languages = sorted(language_shares.items(), key=lambda item: -item[1])[:6]
    languages = [(name, round(size * 100 / total)) for name, size in languages]
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=30)).isoformat().replace("+00:00", "Z")
    recent = []
    for repo in repos:
        commits = api(f"repos/{USER}/{repo['name']}/commits?author={USER}&since={since}&per_page=100")
        recent.extend((commit, repo["name"]) for commit in commits)
    message = "no recent commit"
    repository = USER
    when = dt.datetime.now(dt.timezone.utc).isoformat()
    if recent:
        commit, name = max(recent, key=lambda item: parse_time(item[0]["commit"]["author"]["date"]))
        repository = f"{USER}/{name}"
        when = commit["commit"]["author"]["date"]
        message = commit["commit"]["message"].splitlines()[0]
    return {
        "followers": user["followers"],
        "stars": sum(repo["stargazers_count"] for repo in repos),
        "repos": user["public_repos"],
        "languages": languages,
        "commits": len(recent),
        "repository": repository,
        "message": message,
        "when": when,
        "updated": dt.datetime.now().strftime("%Y-%m-%d"),
    }


def chrome(title, height):
    return f'''  <rect x="4" y="4" width="1192" height="{height - 8}" rx="12" fill="#080a0c" stroke="#242b31"/>
  <rect x="4" y="4" width="1192" height="40" rx="12" fill="#101417"/>
  <rect x="4" y="28" width="1192" height="16" fill="#101417"/>
  <line x1="4" y1="44" x2="1196" y2="44" stroke="#242b31"/>
  <circle cx="30" cy="24" r="6" fill="#ff5f56"/>
  <circle cx="52" cy="24" r="6" fill="#ffbd2e"/>
  <circle cx="74" cy="24" r="6" fill="#27c93f"/>
  <text x="600" y="29" text-anchor="middle" font-family="{MONO}" font-size="13" fill="#78838b">{esc(title)}</text>'''


def terminal_row(x, y, label, value):
    return f'''  <text x="{x}" y="{y}" font-family="{MONO}" font-size="17"><tspan fill="#aab4bb">{esc(label)}</tspan></text>
  <text x="{x + 168}" y="{y}" font-family="{MONO}" font-size="17" fill="#f2f5f7">{esc(value)}</text>'''


def status_panel(data):
    shades = ["#ffffff", "#e3e9ec", "#c6ced3", "#aab4bb", "#78838b", "#4c555b"]
    segments = []
    legend = []
    used = 0
    for index, (name, percent) in enumerate(data["languages"]):
        width = min(100 - used, percent)
        if width <= 0:
            break
        segments.append(f'  <rect x="{30 + 1140 * used / 100:.1f}" y="244" width="{1140 * width / 100:.1f}" height="12" fill="{shades[index % len(shades)]}"/>')
        legend.append(f'{esc(name)} {percent}%')
        used += width
    if used < 100:
        segments.append(f'  <rect x="{30 + 1140 * used / 100:.1f}" y="244" width="{1140 * (100 - used) / 100:.1f}" height="12" fill="#2b3238"/>')
    rows = [
        (30, 128, "followers", data["followers"]),
        (30, 156, "stars", data["stars"]),
        (30, 184, "repos", data["repos"]),
        (30, 212, "commits", f'{data["commits"]} in 30d'),
        (620, 128, "os", "macOS / Arch Linux"),
        (620, 156, "based", "California, US"),
        (620, 184, "last commit", data["repository"]),
        (620, 212, "updated", data["updated"]),
    ]
    body = "\n".join(terminal_row(x, y, label, value) for x, y, label, value in rows)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 340" width="1200" height="340" role="img" aria-labelledby="status-title status-desc">
  <title id="status-title">Live GitHub status</title>
  <desc id="status-desc">Terminal panel with live followers, stars, repositories, commits, and language mix.</desc>
{chrome("greyson@mac — status — zsh", 340)}
  <text x="30" y="88" font-family="{MONO}" font-size="21"><tspan fill="#ffffff">greyson@mac</tspan><tspan fill="#6b757d"> ~ % </tspan><tspan fill="#f2f5f7">status --all</tspan></text>
{body}
  <rect x="30" y="244" width="1140" height="12" rx="3" fill="#14191d"/>
{chr(10).join(segments)}
  <text x="30" y="286" font-family="{MONO}" font-size="15" fill="#aab4bb">languages  {" · ".join(legend)}</text>
  <text x="30" y="318" font-family="{MONO}" font-size="13" fill="#6b757d"># auto-generated · refreshes daily</text>
  <rect x="1150" y="304" width="11" height="18" fill="#ffffff">
    <animate attributeName="opacity" values="1;0;1" dur="1.1s" repeatCount="indefinite"/>
  </rect>
</svg>
'''


def now_line(data):
    message = data["message"]
    if len(message) > 54:
        message = message[:51] + "..."
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 64" width="1200" height="64" role="img" aria-labelledby="now-title now-desc">
  <title id="now-title">Latest activity</title>
  <desc id="now-desc">The most recent public push and how long ago it happened.</desc>
  <rect x="4" y="4" width="1192" height="56" rx="10" fill="#080a0c" stroke="#242b31"/>
  <text x="30" y="40" font-family="{MONO}" font-size="16"><tspan fill="#ffffff">❯ now</tspan><tspan fill="#6b757d">  committed to </tspan><tspan fill="#f2f5f7">{esc(data["repository"])}</tspan><tspan fill="#6b757d"> · </tspan><tspan fill="#aab4bb">"{esc(message)}"</tspan><tspan fill="#6b757d"> · {esc(relative_time(data["when"]))}</tspan></text>
  <rect x="1160" y="27" width="10" height="16" fill="#ffffff">
    <animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/>
  </rect>
</svg>
'''


def main():
    data = collect()
    (ASSETS / "status-panel.svg").write_text(status_panel(data))
    (ASSETS / "now.svg").write_text(now_line(data))


if __name__ == "__main__":
    main()
