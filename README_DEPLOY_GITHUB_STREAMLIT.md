# Deploy Alboran Atlas on Streamlit Community Cloud

The error "the app's code is not connected to a remote GitHub repository" means the app is still local.

## 1. Put the app in a GitHub repository

Open a terminal in this folder and run:

```bash
git init
git add .
git commit -m "Initial Alboran Atlas DTO platform"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/alboran-atlas.git
git push -u origin main
```

Or double-click `setup_git_repository.bat` and paste your GitHub repo URL.

## 2. Add your logo

For cloud deployment, local paths like:

```text
C:\Users\Asus\Downloads\Al Boran Atlas LOGO.png
```

will not exist on Streamlit Cloud.

Copy your logo into:

```text
assets/Al Boran Atlas LOGO.png
```

Then commit and push it to GitHub.

## 3. Deploy on Streamlit Community Cloud

Choose:
- Repository: your GitHub repository
- Branch: main
- Main file path: app.py

## 4. Add secrets

In Streamlit Cloud app settings, add:

```toml
[auth]
username = "asma"
password = "choose_a_secure_password"
```

## 5. Important data note

The app can run online, but Streamlit Cloud cannot access your local files such as:

```text
C:\Users\Asus\Desktop\aquasafe data\...
```

For a true online version, use one of these:
- put small demo NetCDF files inside the repository,
- host NetCDF/Zarr/GeoTIFF files in cloud storage,
- connect to THREDDS/OPeNDAP/CMEMS endpoints,
- or deploy locally/institutionally where the data paths exist.


## Updating from MVP v2 to MVP v3

After replacing files locally, push the changes:

```bash
git add .
git commit -m "Improve UI, SeaExplorer logo, and clean glider tracks"
git push
```

Then Streamlit Cloud will redeploy from GitHub.


## If GitHub says: rejected because remote contains work

Run:

```bash
git pull --rebase origin main
git push -u origin main
```

If the repository is only for Alboran Atlas and you intentionally want your local folder to replace GitHub, use:

```bash
git push --force-with-lease origin main
```

This is safer than plain `--force`.


## Conflict-marker fix

If Streamlit shows this error:

```text
SyntaxError: invalid syntax
<<<<<<< HEAD
```

your `app.py` contains unfinished Git merge-conflict markers.

Fast solution:
1. Extract the v5 clean package into a NEW folder.
2. Run `force_sync_clean_v5_to_github.bat`.
3. Refresh GitHub and redeploy.
