# QUICKSTART (Windows / PowerShell)

Exact commands to get the OSINT Research Dashboard running locally on
Windows using PowerShell. Run these from the project's root folder
(the folder containing `app.py`).

Requires **Python 3.11+** installed and available as `python` on your
PATH. Check with:

```powershell
python --version
```

## 1. Create a virtual environment

```powershell
python -m venv venv
```

## 2. Activate it

```powershell
venv\Scripts\Activate.ps1
```

> If PowerShell blocks the script with an execution-policy error, run
> this once (in an admin PowerShell, or just for your user) and then
> retry the activate command:
>
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```

Your prompt should now start with `(venv)`.

## 3. Install dependencies

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

### Optional: better entity extraction

```powershell
python -m spacy download en_core_web_sm
```

Skip this if you want — the app automatically falls back to a
simpler regex-based entity extractor if the spaCy model isn't
installed.

## 4. (Optional) Configure environment variables

```powershell
copy .env.example .env
```

Then open `.env` in a text editor if you want to set a `NEWSAPI_KEY`
or enable AI-enhanced summaries. **This step is entirely optional —
the app runs correctly with no `.env` file at all.**

## 5. Run the test suite

```powershell
pytest tests/ -v
```

All tests should pass. This does not require network access or any
API keys.

## 6. Start the Streamlit app

```powershell
streamlit run app.py
```

## 7. Open the application

Streamlit will print a local URL in the terminal, typically:

```
http://localhost:8501
```

It should also open automatically in your default browser. If not,
copy that URL into your browser manually.

## Fastest possible first run (no network research)

If you just want to see the app working immediately with **zero**
network access and **zero** configuration:

1. Complete steps 1–3 above (venv + install).
2. Run `streamlit run app.py`.
3. In the sidebar, check **"Use demo mode (no network required)"**.
4. Click **Start Investigation**.

This loads a complete sample investigation instantly, with no API
keys, no `.env` file, and no internet connection required.

## Next time you come back

You don't need to repeat steps 1 and 3 (venv creation and dependency
install) every time. Just activate the existing environment and run
the app:

```powershell
venv\Scripts\Activate.ps1
streamlit run app.py
```

## Deactivating the virtual environment

```powershell
deactivate
```
