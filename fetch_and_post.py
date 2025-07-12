# fetch_and_post.py
"""
Pull yesterday-to-today concurring & dissenting opinions from CourtListener
and drop stub summaries into _posts/  (ready for Jekyll/GitHub Pages).
"""

import os
import datetime
import textwrap
import requests
import yaml
from dotenv import load_dotenv

load_dotenv()  # lets the script also run inside Codespaces

# --- Configuration ---------------------------------------------------------

CL_API = "https://www.courtlistener.com/api/rest/v3/opinions/"
YESTERDAY = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()

# Use the secret if present, otherwise fall back to a hard-coded, polite header
USER_AGENT = os.getenv(
    "USER_AGENT",
    "OpinionTrackerBot/0.1 (+https://github.com/oriondenevers/opinion-tracker; contact oriondenevers@gmail.com)",
)

HEADERS = {"User-Agent": USER_AGENT}

PARAMS = {
    "type": "concurring,dissenting",
    "date_filed__gte": YESTERDAY,
    "ordering": "-date_filed",
    "page_size": 100,
}

# --- Helper functions ------------------------------------------------------


def grab():
    """Return today’s list of opinion JSON objects (or empty list)."""
    r = requests.get(CL_API, params=PARAMS, headers=HEADERS, timeout=30)
    if r.status_code == 403:
        raise SystemExit(
            "CourtListener refused the request (403). "
            "Double-check that USER_AGENT is a descriptive string "
            "and *not* the default."
        )
    r.raise_for_status()
    return r.json().get("results", [])


def summarize(prompt: str) -> str:
    """
    BEGINNER-safe stub: just returns the first 200 characters.
    Later you can drop real OpenAI code in here.
    """
    return textwrap.shorten(prompt, 200, " […]")


# --- Main ------------------------------------------------------------------

os.makedirs("_posts", exist_ok=True)

for op in grab():
    body = op.get("plain_text") or op.get("html_lawbox") or op.get("html") or ""
    body = textwrap.shorten(body, 16_000, " […]")
    summary = summarize(f"Summarize this {op['type']} opinion:\n\n{body}")

    slug = f"{op['date_filed']}-{op['id']}.md"
    front = {
        "title": f"{op['case_name']} ({op['court']})",
        "date": op["date_filed"],
        "tags": [op["type"]],
        "link": op["absolute_url"],
    }
    with open(f"_posts/{slug}", "w") as f:
        f.write("---\n")
        yaml.safe_dump(front, f, sort_keys=False)
        f.write("---\n\n" + summary + "\n")

print("▶︎ Done — posts written to _posts/")
