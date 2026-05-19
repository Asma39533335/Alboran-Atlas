# Fixing the `<<<<<<< HEAD` SyntaxError

The error means your local `app.py` contains Git merge-conflict markers:

```text
<<<<<<< HEAD
=======
>>>>>>> ...
```

Python cannot run while these markers exist.

## Fast clean fix

1. Extract this v5 ZIP to a NEW folder.
2. Copy your logos into:
   - `assets/Al Boran Atlas LOGO.png`
   - `assets/SeaExplorer2-scaled-removebg-preview.png`
3. Double-click:
   `force_sync_clean_v5_to_github.bat`

This pushes a clean app to:

```text
https://github.com/Asma39533335/Alboran-Atlas
```

## Streamlit Cloud settings

Use:

```text
Repository: Asma39533335/Alboran-Atlas
Branch: main
Main file path: app.py
```

## Local run

Double-click:

```text
run_Alboran_Atlas.bat
```

Default login:

```text
username: asma
password: alboran2026
```
