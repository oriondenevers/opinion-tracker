import os, datetime, requests, yaml, textwrap
from dotenv import load_dotenv
load_dotenv()

CL = "https://www.courtlistener.com/api/rest/v3/opinions/"
params = {
    "type": "concurring,dissenting",
    "date_filed__gte": (datetime.date.today() - datetime.timedelta(days=1)).isoformat(),
    "ordering": "-date_filed",
    "page_size": 100,
}

def grab():                       # pull yesterday-to-today opinions
    r = requests.get(CL, params=params,
                     headers={"User-Agent": os.getenv("USER_AGENT","OpinionBot")})
    r.raise_for_status()
    return r.json()["results"]

def summarize(prompt):            # ***BEGINNER-SAFE STUB***
    # later we'll drop in OpenAI here; for now return first 200 chars
    return textwrap.shorten(prompt, 200, " […]")

os.makedirs("_posts", exist_ok=True)
for op in grab():
    body = (op["plain_text"] or op["html_lawbox"] or op["html"] or "")
    body = textwrap.shorten(body, 16000, " […]")
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