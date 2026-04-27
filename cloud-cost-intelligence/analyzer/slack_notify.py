import requests
import os
from dotenv import load_dotenv

load_dotenv()

def send_slack_alert(idle_instances):
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')

    if not idle_instances:
        message = "✅ *Cloud Cost Intelligence* — No idle instances found. You're clean!"
    else:
        lines = ["🚨 *Cloud Cost Intelligence — Idle Instances Detected!*\n"]
        for inst in idle_instances:
            lines.append(
                f"• Instance `{inst['instance_id']}` ({inst['instance_type']}) "
                f"— Avg CPU: {inst['avg_cpu']}% over 7 days"
            )
        lines.append("\n📋 A Terraform fix PR has been raised automatically.")
        message = "\n".join(lines)

    payload = {"text": message}
    response = requests.post(webhook_url, json=payload)

    if response.status_code == 200:
        print("✅ Slack alert sent successfully")
    else:
        print(f"❌ Slack alert failed: {response.status_code}")


if __name__ == "__main__":
    # Test with dummy data
    test_instances = [
        {'instance_id': 'i-1234567890abcdef0', 'instance_type': 't2.micro', 'avg_cpu': 1.2},
        {'instance_id': 'i-abcdef1234567890', 'instance_type': 't3.medium', 'avg_cpu': 3.5}
    ]
    send_slack_alert(test_instances)