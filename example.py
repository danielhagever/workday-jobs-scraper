#!/usr/bin/env python3
"""Pull Workday job postings by company name and write them to a CSV.

Standard library only. Needs an Apify API token in APIFY_TOKEN
(free at https://console.apify.com/settings/integrations).

    export APIFY_TOKEN=apify_api_...
    python3 example.py                                  # inputs/by-name.json
    python3 example.py inputs/engineers-remote.json     # any input file
    python3 example.py --company "Wells Fargo" --title analyst --max 50
"""
import argparse
import csv
import json
import os
import sys
import urllib.error
import urllib.request

ACTOR = "glitchbound~workday-jobs-scraper"
RUN_SYNC = f"https://api.apify.com/v2/acts/{ACTOR}/run-sync-get-dataset-items"
COLUMNS = ["company", "title", "location", "country", "postedAtRelative",
           "isRemote", "seniority", "url"]


def run(actor_input, token):
    """Start one run, wait for it, and return its rows (the call blocks up to 300 s)."""
    req = urllib.request.Request(
        RUN_SYNC, data=json.dumps(actor_input).encode(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=330) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"Apify answered {e.code}: {e.read().decode()[:300]}")


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("input", nargs="?", default=os.path.join(here, "inputs", "by-name.json"),
                    help="a JSON input file (default: inputs/by-name.json)")
    ap.add_argument("--company", action="append", help="company name; repeat for more")
    ap.add_argument("--title", action="append", help="keep titles containing this")
    ap.add_argument("--max", type=int, help="stop after this many rows in total")
    ap.add_argument("--out", default="jobs.csv")
    args = ap.parse_args()

    token = os.environ.get("APIFY_TOKEN")
    if not token:
        sys.exit("Set APIFY_TOKEN first: https://console.apify.com/settings/integrations")

    if args.company:
        actor_input = {"companies": args.company}
    else:
        with open(args.input) as f:
            actor_input = json.load(f)
    if args.title:
        actor_input["titleKeywords"] = args.title
    if args.max:
        actor_input["maxItems"] = args.max

    rows = run(actor_input, token)
    # Job rows carry no recordType. "error" rows (unbilled) say why a company gave
    # nothing; "note" rows say where a name was found or why a board came back short.
    jobs = [r for r in rows if "recordType" not in r]
    for r in rows:
        if r.get("recordType") == "error":
            print(f"error: {r.get('target')}: {r.get('error')}", file=sys.stderr)
        elif r.get("recordType") == "note":
            print(f"note: {r.get('note') or json.dumps(r)[:200]}", file=sys.stderr)

    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        w.writeheader()
        w.writerows(jobs)
    print(f"{len(jobs)} jobs written to {args.out}")
    for j in jobs[:5]:
        print(f"  {j.get('company')}: {j.get('title')} ({j.get('location')})")


if __name__ == "__main__":
    main()
