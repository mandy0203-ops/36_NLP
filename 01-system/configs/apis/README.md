# API Keys Management

This directory contains the `API-Keys.md` file which stores environment variables and secrets.
The agent reads this file to load secrets into the process environment only when required.

**Security Note:**
- Never commit `API-Keys.md` with real values to version control if this repo is public.
- The agent will never log the values found in this file.
