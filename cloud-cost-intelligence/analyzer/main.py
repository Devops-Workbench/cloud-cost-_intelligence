import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from detector import get_idle_ec2_instances
from slack_notify import send_slack_alert
from pr_generator import raise_github_pr

def main():
    print("Scanning AWS for idle EC2 instances...")
    idle_instances = get_idle_ec2_instances()

    if not idle_instances:
        print("No idle instances found.")
        send_slack_alert([])
        return

    print(f"Found {len(idle_instances)} idle instance(s):")
    for inst in idle_instances:
        print(f"   - {inst['instance_id']} ({inst['instance_type']}) — {inst['avg_cpu']}% avg CPU")

    print("Raising GitHub PR with Terraform fix...")
    pr_url = raise_github_pr(idle_instances)

    print("Sending Slack alert...")
    send_slack_alert(idle_instances)

    print(f"Done! PR raised: {pr_url}")

if __name__ == "__main__":
    main()
