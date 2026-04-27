import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from detector import scan_all_resources
from slack_notify import send_slack_alert
from pr_generator import raise_github_pr

def main():
    print("🔍 Scanning all AWS resources for waste...")
    resources = scan_all_resources()

    if not resources:
        print("✅ No wasteful resources found.")
        send_slack_alert([])
        return

    print(f"\n⚠️  Found {len(resources)} wasteful resource(s):")
    for r in resources:
        print(f"   - [{r['resource_type']}] {r['instance_id']} ({r['instance_type']}) → {r['recommendation']}")

    print("\n📋 Raising GitHub PR with Terraform fix...")
    pr_url = raise_github_pr(resources)

    print("\n📣 Sending Slack alert...")
    send_slack_alert(resources)

    print(f"\n✅ Done! PR raised: {pr_url}")

if __name__ == "__main__":
    main()