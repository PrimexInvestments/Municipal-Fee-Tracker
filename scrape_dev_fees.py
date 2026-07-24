name: Daily fee tracker update

on:
  schedule:
    # 14:00 UTC = 7:00 AM Pacific, every day
    - cron: "0 14 * * *"
  workflow_dispatch: {}   # adds a "Run workflow" button for manual runs

permissions:
  contents: write

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - name: Get the site files
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install what the scripts need
        run: pip install requests beautifulsoup4 lxml pdfplumber

      - name: Fetch news
        run: python fetch_news.py
        continue-on-error: true   # a dead feed shouldn't kill the run

      - name: Check municipal sites for rate changes
        run: python scrape_dev_fees.py
        continue-on-error: true

      - name: Apply high-confidence changes
        run: python apply_changes.py --yes
        continue-on-error: true

      - name: Rebuild the website
        run: python build_site.py

      - name: Save and publish
        run: |
          git config user.name "fee-tracker-bot"
          git config user.email "actions@users.noreply.github.com"
          git add -A
          if git diff --cached --quiet; then
            echo "No changes today."
          else
            git commit -m "Daily update: $(date -u +%Y-%m-%d)"
            git push
          fi
