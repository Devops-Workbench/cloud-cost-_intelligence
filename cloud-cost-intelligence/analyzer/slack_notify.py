import requests
import os
from dotenv import load_dotenv

load_dotenv()

COST_MAP = {
    'EC2': 50,
    'RDS': 100,
    'EBS': 10,
    'ElasticIP': 3.6
}

def estimate_savings(resources):
    total = 0
    for r in resources:
        total += COST_MAP.get(r['resource_type'], 10)
    return round(total, 2)

def send_slack_alert(resources):
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')

    if not resources:
        message = "✅ *Cloud Cost Intelligence* — No wasteful resources found. You're clean!"
    else:
        savings = estimate_savings(resources)
        lines = [f"🚨 *Cloud Cost Intelligence — {len(resources)} Wasteful Resource(s) Detected!*\n"]

        for r in resources:
            lines.append(
                f"• [{r['resource_type']}] `{r['instance_id']}` ({r['instance_type']}) "
                f"→ _{r['recommendation']}_"
            )

        lines.append(f"\n💰 *Estimated Monthly Savings: ${savings}*")
        lines.append("📋 A Terraform fix PR has been raised automatically.")
        message = "\n".join(lines)

    payload = {"text": message}
    response = requests.post(webhook_url, json=payload)

    if response.status_code == 200:
        print("✅ Slack alert sent successfully")
    else:
        print(f"❌ Slack alert failed: {response.status_code}")

if __name__ == "__main__":
    test_resources = [
        {'resource_type': 'EC2', 'instance_id': 'i-1234567890', 'instance_type': 't2.micro', 'recommendation': 'stop or downsize'},
        {'resource_type': 'EBS', 'instance_id': 'vol-1234567890', 'instance_type': '50GB gp2', 'recommendation': 'delete orphaned volume'},
        {'resource_type': 'ElasticIP', 'instance_id': '54.123.45.67', 'instance_type': 'Elastic IP', 'recommendation': 'release unused IP'}
    ]
    send_slack_alert(test_resources)