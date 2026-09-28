"""
Update Notion checklist: add done tasks to Sprint Plan & status pages.

Uses to_do blocks. Run: python3 checklist_notion.py [task_name]

SECURITY: NOTION_API_KEY must come from the environment. Never hardcode.
Setup: export NOTION_API_KEY="your_token"
"""
import sys
import requests
import os

NOTION_API_KEY = os.environ.get("NOTION_API_KEY", "")
if not NOTION_API_KEY:
    print("ERROR: NOTION_API_KEY not set. Export it before running.")
    sys.exit(1)

HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

SPRINT_STATUS_PAGES = {
    1: "Ringkasan Arsitektur Final",
    2: "Arsitektur Rag Chat Assistant",
    3: "Desain Fitur Chat Assistant Rag",
    4: "Skema Database Postgresql",
    5: "Sprint Plan",
}


def add_checklist_item(page_title, task_name, checked=True):
    """Add a to_do block to a Notion page by title."""
    search = requests.post(
        "https://api.notion.com/v1/search",
        headers=HEADERS,
        json={"query": page_title},
    )
    if search.status_code != 200:
        print(f"Search error: {search.text[:200]}")
        return False

    results = search.json().get("results", [])
    if not results:
        print(f"Page not found: {page_title}")
        return False

    page_id = results[0]["id"]
    resp = requests.patch(
        f"https://api.notion.com/v1/blocks/{page_id}/children",
        headers=HEADERS,
        json={
            "children": [{
                "object": "block",
                "type": "to_do",
                "to_do": {
                    "rich_text": [{"type": "text", "text": {"content": task_name}}],
                    "checked": checked,
                },
            }]
        },
    )
    return resp.status_code == 200


if __name__ == "__main__":
    task = sys.argv[1] if len(sys.argv) > 1 else "BUG-003: greeting natural"
    ok = add_checklist_item(SPRINT_STATUS_PAGES[2], task)
    print("Notion updated" if ok else "Notion update failed")
