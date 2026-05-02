# 💰 Cloud Cost Intelligence — GitOps-Driven AWS Cost Optimization Platform

![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)
![Terraform](https://img.shields.io/badge/Terraform-7B42BC?style=for-the-badge&logo=terraform&logoColor=white)
![Slack](https://img.shields.io/badge/Slack-4A154B?style=for-the-badge&logo=slack&logoColor=white)

> An open-source GitOps pipeline that automatically detects idle and over-provisioned AWS resources, generates Terraform remediation PRs, and reports projected savings via Slack — before money is wasted.

---

## 🚨 The Problem

Cloud waste exceeds **30% of total spend** at most companies. Engineers spin up EC2 instances, forget RDS databases running overnight, leave EBS volumes unattached, and hold onto unused Elastic IPs — and nobody notices until the AWS bill arrives.

**No existing open-source tool combines:**
- Multi-resource waste detection
- Automated Terraform fix generation
- GitOps PR workflow for human review
- Real-time Slack alerting with cost estimates

---

## ✅ What This Project Does

```
AWS Resources (EC2 / RDS / EBS / Elastic IP)
        ↓
Python Analyzer (CloudWatch metrics + boto3)
        ↓
Waste Detected → Terraform Fix Generated
        ↓
GitHub PR Auto-Raised (human reviews before applying)
        ↓
Slack Alert → Estimated Monthly Savings Reported
        ↓
Engineer Approves PR → Fix Applied → Money Saved
```

---

## 🔍 Resources Scanned

| Resource | Detection Logic | Recommendation |
|----------|----------------|----------------|
| **EC2 Instances** | CPU < 5% AND Network < 1MB over 30 days | Stop or downsize |
| **RDS Databases** | Zero connections over 30 days | Stop or delete |
| **EBS Volumes** | Status = available (unattached) | Delete orphaned volume |
| **Elastic IPs** | Not associated with any instance | Release ($3.6/month wasted) |

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| **Python + boto3** | AWS resource scanning and CloudWatch metrics |
| **AWS Cost Explorer** | Cost data and usage analysis |
| **GitHub Actions** | Automated scheduled scanning (every Monday 9am) |
| **PyGithub** | Auto-raise PRs with Terraform fixes |
| **Terraform** | Infrastructure fix generation |
| **Slack Webhooks** | Real-time alerts with savings estimates |
| **python-dotenv** | Secure environment configuration |

---

## 📁 Project Structure

```
cloud-cost-intelligence/
├── analyzer/
│   ├── main.py              # Entry point — orchestrates full scan
│   ├── detector.py          # AWS resource scanning (EC2/RDS/EBS/EIP)
│   ├── pr_generator.py      # Terraform fix generation + GitHub PR
│   └── slack_notify.py      # Slack alerts with cost estimates
├── terraform_fixes/         # Auto-generated Terraform remediation files
├── .github/workflows/
│   └── cost-scan.yml        # GitHub Actions — runs every Monday 9am UTC
├── .env.example             # Environment variable template
├── requirements.txt         # Python dependencies
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- AWS account with Cost Explorer enabled
- GitHub account
- Slack workspace

### 1. Clone the repository
```bash
git clone https://github.com/Gokularam-12/cloud-cost-intelligence.git
cd cloud-cost-intelligence
```

### 2. Set up virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure environment variables
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```env
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=us-east-1
GITHUB_TOKEN=your_github_token
GITHUB_REPO=your_username/cloud-cost-intelligence
SLACK_WEBHOOK_URL=your_slack_webhook_url
```

### 4. Run the scanner
```bash
cd analyzer
python3 main.py
```

### 5. Set up GitHub Actions secrets
Add these secrets in your repo Settings → Secrets → Actions:

| Secret Name | Value |
|-------------|-------|
| `AWS_ACCESS_KEY_ID` | Your AWS access key |
| `AWS_SECRET_ACCESS_KEY` | Your AWS secret key |
| `AWS_DEFAULT_REGION` | `us-east-1` |
| `GH_TOKEN` | Your GitHub token |
| `GH_REPO` | `username/cloud-cost-intelligence` |
| `SLACK_WEBHOOK_URL` | Your Slack webhook URL |

---

## 📣 Sample Slack Alert

```
🚨 Cloud Cost Intelligence — 3 Wasteful Resource(s) Detected!

• [EC2] i-1234567890abcdef0 (t2.medium) → stop or downsize
• [EBS] vol-0abc123def456789 (50GB gp2) → delete orphaned volume
• [ElasticIP] 54.123.45.67 (Elastic IP) → release unused IP ($3.6/month wasted)

💰 Estimated Monthly Savings: $85.60
📋 A Terraform fix PR has been raised automatically.
```

---

## 🔄 GitOps Workflow

1. **Scan runs automatically** every Monday at 9am UTC via GitHub Actions
2. **Waste detected** → Terraform fix auto-generated
3. **PR raised** with full breakdown of wasteful resources
4. **Engineer reviews** the Terraform changes
5. **PR merged** → fix applied → savings locked in
6. **Slack alert** confirms action taken

Every infrastructure change is **reviewed, approved, and tracked in Git** — no blind auto-remediation.

---

## 🤔 Why This Is Different

| Tool | Detection | Terraform Fix | GitOps PR | Slack Alert |
|------|-----------|--------------|-----------|-------------|
| AWS Trusted Advisor | ✅ | ❌ | ❌ | ❌ |
| CloudCustodian | ✅ | ❌ | ❌ | Partial |
| Infracost | ❌ | ❌ | Partial | ❌ |
| **Cloud Cost Intelligence** | ✅ | ✅ | ✅ | ✅ |

**The key difference:** Other tools either alert or directly remediate. This project generates a **Terraform PR for human review** — safe, auditable, GitOps-native.

---

## 📊 Resume Impact

```
Built a GitOps cost intelligence pipeline that scans AWS for idle EC2,
RDS, EBS, and Elastic IP resources using CloudWatch metrics, auto-generates
Terraform rightsizing PRs, and reports projected monthly savings via Slack
— combining detection, remediation, and GitOps review in a single automated workflow.
```

---

## 🗺️ Roadmap

- [ ] AI-powered rightsizing recommendations (ML-based, not threshold)
- [ ] Cost forecasting dashboard
- [ ] Multi-region support
- [ ] Slack approval buttons (approve fix directly from Slack)
- [ ] Historical savings tracker

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 🙌 Contributing

Pull requests welcome. For major changes, open an issue first to discuss what you'd like to change.

---

<p align="center">Built with ❤️ by <a href="https://github.com/Gokularam-12">Gokularam</a></p>
