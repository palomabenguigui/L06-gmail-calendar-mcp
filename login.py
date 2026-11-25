"""Run once: opens the browser for Google login and saves token.json in GOOGLE_PRIVATE_DIR.

Usage:  GOOGLE_PRIVATE_DIR="$HOME/my-private" uv run login.py
"""
import sys

from google_auth_oauthlib.flow import InstalledAppFlow

from google_auth import SCOPES, client_secret_file, save_token, token_file


def main() -> int:
    try:
        secret = client_secret_file()
    except RuntimeError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1
    flow = InstalledAppFlow.from_client_secrets_file(str(secret), SCOPES)
    print("Opening your browser for Google login...")
    creds = flow.run_local_server(port=0, prompt="consent", access_type="offline")
    save_token(creds)
    print(f"Login OK. Token saved to {token_file()} (permissions 600).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
