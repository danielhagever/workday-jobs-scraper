# Workday Jobs Scraper: every posting from any Workday careers site, by company name

Pull every open job from a Workday careers site (`*.myworkdayjobs.com`) as clean JSON or
CSV. Type a company name, such as `NVIDIA`, `Wells Fargo` or `Procter & Gamble`, for over
3,000 employers, or paste any Workday careers URL. No Workday account, no API key for
Workday, no proxy.

This repo is the quick start for the hosted
[**Workday Jobs Scraper**](https://apify.com/glitchbound/workday-jobs-scraper) on Apify:
one HTTP call from the shell, a standard-library Python script, and the setup for using it
as a tool in Claude, ChatGPT or Cursor. If you would rather call Workday's public endpoint
yourself, [that is documented too](#doing-it-yourself).

- [Quick start: one curl](#quick-start-one-curl)
- [Quick start: Python](#quick-start-python)
- [Use it from an AI agent (MCP)](#use-it-from-an-ai-agent-mcp)
- [Input](#input) · [Output](#output)
- [Companies you can ask for by name](#companies-you-can-ask-for-by-name)
- [Doing it yourself](#doing-it-yourself)
- [FAQ](#faq)

## Quick start: one curl

Get a free Apify API token at
[console.apify.com/settings/integrations](https://console.apify.com/settings/integrations),
then:

```bash
export APIFY_TOKEN=apify_api_...
curl -s -X POST \
  -H "Authorization: Bearer $APIFY_TOKEN" -H "Content-Type: application/json" \
  -d '{"companies": ["NVIDIA", "Wells Fargo"], "titleKeywords": ["engineer"], "maxItems": 20}' \
  "https://api.apify.com/v2/acts/glitchbound~workday-jobs-scraper/run-sync-get-dataset-items"
```

The response is a JSON array, one object per job. For runs longer than five minutes, start
the run and fetch the dataset when it finishes (`/runs` then `/datasets/{id}/items`).

## Quick start: Python

[`example.py`](example.py) uses only the standard library and writes a CSV:

```bash
python3 example.py --company NVIDIA --company "Wells Fargo" --title engineer --max 20
python3 example.py inputs/engineers-remote.json
```

A real run of the first command, with `--max 6`:

```
6 jobs written to jobs.csv
  NVIDIA: Director, Engineering – Software Engineering (Hanoi, Vietnam)
  NVIDIA: Senior Software Engineer, Platform Engineering (US, CA, Santa Clara)
  NVIDIA: Senior System Engineer, Solution Engineering (Poland)
  Wells Fargo: Principal Engineer, AI Engineering (CITY OF LONDON,)
  Wells Fargo: Principal Engineer (Bengaluru, India)
```

Locations are kept as the employer typed them; `country`, and `city` where the location
names one, are parsed out separately.

## Use it from an AI agent (MCP)

The Actor is a ready-made tool for any MCP client through Apify's MCP server. Add this as a
connector in Claude or ChatGPT:

```
https://mcp.apify.com?tools=glitchbound/workday-jobs-scraper
```

In Cursor or VS Code, the same address goes in `mcp.json`:

```json
{ "mcpServers": { "apify": { "url": "https://mcp.apify.com?tools=glitchbound/workday-jobs-scraper" } } }
```

The first call asks you to sign in to Apify or takes an API token. Then you can ask
"which software engineering roles does NVIDIA have open in Israel?" and the agent calls the
Actor with the right input.

## Input

| Field | What it does |
|---|---|
| `companies` | Company names, written the way people write them: "Wells Fargo" finds the `wf` tenant, "Procter & Gamble" finds `pg`. All of a company's Workday sites are read. A name that is not on Workday is looked up on the other career systems the Actor reads (Oracle, Eightfold, SAP SuccessFactors and more) and read there. |
| `boards` | Workday careers URLs, e.g. `https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite` |
| `titleKeywords` | Keep roles whose title contains any of these. Plain text, so `c++` means c++. |
| `locationKeywords` | Keep roles whose location contains any of these, e.g. `London`. |
| `remoteOnly` | Keep remote roles only. |
| `includeDescription` | Also read each job's page: full description, the real posting date, every office and the employment type. One extra request per job. |
| `maxResultsPerCompany` | Ceiling per company (default 1,000). |
| `maxItems` | Ceiling for the whole run. |

Ready-made inputs are in [`inputs/`](inputs). Rows your filters drop are not charged.

## Output

One row per job. Two real rows from a run are in [`sample-output.json`](sample-output.json):

```json
{
  "jobId": "JR2015832",
  "title": "Senior Software Engineer, Platform Engineering",
  "location": "US, CA, Santa Clara",
  "url": "https://nvidia.wd5.myworkdayjobs.com/nvidiaexternalcareersite/job/US-CA-Santa-Clara/Senior-Software-Engineer--Platform-Engineering_JR2015832",
  "postedAt": "2026-10-20T00:00:00Z",
  "postedAtRelative": "Posted 5 Days Ago",
  "company": "NVIDIA",
  "atsPlatform": "workday",
  "boardUrl": "https://nvidia.wd5.myworkdayjobs.com/nvidiaexternalcareersite",
  "seniority": "senior",
  "workArrangement": "onsite",
  "isRemote": false,
  "country": "United States"
}
```

`jobId` is Workday's own requisition id and stays the same across runs, so a scheduled run
can tell new postings from old ones. Error rows (`"recordType": "error"`) say why a company
returned nothing and are not charged.

## Companies you can ask for by name

A sample of the employers the Actor answers by name on Workday: 3M, Accenture, Adobe,
AT&T, Bank of America, Boeing, Capital One, Caterpillar, Chevron, Cisco, Citi, CVS
Health, Disney, FedEx, General Motors, Home Depot, HP, Humana, Intel, Johnson & Johnson,
Lowe's, Mastercard, Merck, Morgan Stanley, Netflix, Nike, NVIDIA, PayPal, Pfizer, Procter &
Gamble, PwC, Salesforce, Target, T-Mobile, Verizon, Visa, Walmart, Wells Fargo.

Companies that hire on other systems answer too, read where they really post: Marriott,
Kroger and JPMorgan Chase on Oracle; Microsoft, Starbucks and Lockheed Martin on Eightfold;
EY and Nestle on SAP career sites; UPS and Eli Lilly on Phenom; Costco on Jibe. The full,
dated list is on the [Actor page](https://apify.com/glitchbound/workday-jobs-scraper).

## Doing it yourself

Every Workday careers page loads its jobs from a public endpoint:

```bash
curl -s -X POST "https://nvidia.wd5.myworkdayjobs.com/wday/cxs/nvidia/NVIDIAExternalCareerSite/jobs" \
  -H "Content-Type: application/json" \
  -d '{"limit":20,"offset":0,"searchText":"","appliedFacets":{}}' | jq '.total, (.jobPostings | length)'
```

Three things will catch you out, each measured:

1. **`limit` is capped at 20.** Ask for 50 and Workday answers HTTP 400 with an empty
   message.
2. **`total` is only real on the first page.** NVIDIA reports 2,000 at offset 0 and 0 at
   offset 20, so a loop written as `while offset < total` stops after one page and reports
   no error. Keep the first page's number.
3. **The address has three unknowns.** Host label, data centre (`wd1`, `wd5`, ...) and site
   name are all the employer's choice, so a Workday board cannot be derived from a company's
   domain. That is why the Actor ships a map of career sites it has already read real
   postings from, and refuses to guess at names outside it.

The list rows carry no description and only a phrase for the date ("Posted 30+ Days Ago");
the full posting is one more GET per job. The same notes for 16 other systems (Greenhouse,
Lever, Ashby, Oracle, ADP, ...) are in
[**job-board-apis**](https://github.com/danielhagever/job-board-apis).

## FAQ

**How do I scrape Workday jobs by company name?**
Put the name in `companies` as you would say it. Over 3,000 employers resolve to their
Workday site without a URL.

**Does it get past Workday's 2,000-result limit?**
Yes. Workday reports 2,000 for any bigger board; set `maxResultsPerCompany` above 2,000 and
the Actor reads the rest category by category. With a title or a place it uses Workday's own
search instead, which finds every match.

**Do I need a Workday account or API key?**
No. This reads the public feed Workday publishes so job boards can index it. Nothing is
behind a login. You need an Apify token only to run the hosted Actor.

**What does it cost?**
It is paid per result, and rows dropped by your filters and error rows are not charged. The
current rate for your plan is on the [Actor page](https://apify.com/glitchbound/workday-jobs-scraper).

**A board came back empty. Is the company not hiring?**
On Workday an empty board cannot be told apart from a wrong id, so the Actor says exactly
that instead of claiming the company has nothing open.

**Is there an Indeed or Glassdoor API instead?**
No public one. Those sites aggregate from company career pages like these; going to the
source is fresher.

## Related

- [Company Career Page Jobs Scraper](https://apify.com/glitchbound/ats-jobs-scraper): a company name or domain in, its open jobs out, across 24 career systems.
- [Job Listings API](https://apify.com/glitchbound/ats-jobs-search): search one index of career-site jobs by title, place or salary, with a daily feed of new roles.
- [Oracle Recruiting Jobs Scraper](https://apify.com/glitchbound/oracle-jobs-scraper): the same rows from Oracle Cloud careers sites (Marriott, Kroger, Hilton).
- [Workday Jobs API](https://apify.com/glitchbound/workday-jobs-api): a ready-made dataset of Workday postings across employers, no company list needed.
- Write-up: [Workday Jobs Scraper: every posting from any Workday careers site, by company name](https://dev.to/glitchbound/workday-jobs-scraper-every-posting-from-any-workday-careers-site-by-company-name-8bd).

Questions or a company that does not resolve? Open an issue here or on the Actor page.

## License

MIT
