# Portfolio

A Flask portfolio website with dynamic projects and a contact form. It uses JSON files instead of a database.

## Features

- Flask backend
- Dynamic projects from `data/projects.json`
- Project detail pages
- Contact messages saved to `data/messages.json`
- Email notification when a contact form is submitted
- No MySQL or other database required

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set your email settings. The application reads environment variables; it does not read `.env` automatically, so on Windows PowerShell you can set them with `$env:NAME="value"`, or use a deployment platform's environment-variable settings.

For Gmail, enable 2-Step Verification and create a Google App Password. Use that App Password as `SMTP_PASSWORD`, not your normal Gmail password.

Then run:

```bash
python backend/app.py
```

Open `http://127.0.0.1:5000`.

## Deployment

Set the same environment variables in your hosting provider's Environment Variables/Secrets section. Never commit your real SMTP password or secret key to GitHub.
