# Cleaning up this repository

Background
----------
This repository was created by copying an existing project tree into `C:\Projects\pipboy` during prototyping. As a result, the repository currently contains many files from the original project (for example `epstein_downloader_gui.py`, Playwright scripts, tests for a different project, etc.).

Recommended options
-------------------
Pick one and run the corresponding action (or tell me which option you want and I can run it for you):

1) Prune everything except `raspi_pipboy/` (recommended for a focused repo)
   - Action: delete all entries at repo root except `.git`, `.github`, `raspi_pipboy/`, and `README*` files.
   - Command (PowerShell):
     ```powershell
     Get-ChildItem -Path . -Force | Where-Object { $_.Name -notin '.git','.github','raspi_pipboy','README.md','RASPIPIPBOY.md' } | Remove-Item -Recurse -Force
     git add -A
     git commit -m 'Prune repo to only raspi_pipboy prototype and docs'
     ```

2) Move unrelated files to `archive/` (safe, keeps everything)
   - Action: create `archive/` and move non-raspi files there.
   - Command (PowerShell):
     ```powershell
     New-Item -ItemType Directory -Path archive -Force
     Get-ChildItem -Path . -Force | Where-Object { $_.Name -notin '.git','.github','raspi_pipboy','README.md','RASPIPIPBOY.md' } | Move-Item -Destination archive
     git add -A
     git commit -m 'Move non-prototype files into archive/'
     ```

3) Create a fresh repository with only `raspi_pipboy/` (clean start)
   - Action: git sparse checkout / new repo creation or copy `raspi_pipboy/` into a fresh repo.
   - I can create a new GitHub repository for you (public/private as you choose) and push the subset. Ask me and provide a token if you want me to create the remote for you.

Notes
-----
- All these steps will create commits so you can revert if needed.
- I can run these actions for you and open a PR if you prefer a code-reviewable change instead.

Tell me which option you prefer and I will perform it (I'll make a backup commit first before destructive changes).