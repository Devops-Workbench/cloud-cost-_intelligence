import os
from github import Github
from dotenv import load_dotenv

load_dotenv()

def generate_terraform_fix(resources):
    lines = ["# Auto-generated Terraform fix — Cloud Cost Intelligence\n"]

    for r in resources:
        if r['resource_type'] == 'EC2':
            lines.append(f'''
resource "aws_instance" "{r['instance_id']}" {{
  # Type: {r['instance_type']}
  # Recommendation: {r['recommendation']}
  instance_type = "t3.micro"
  lifecycle {{
    prevent_destroy = false
  }}
}}
''')
        elif r['resource_type'] == 'RDS':
            lines.append(f'''
# RDS: {r['instance_id']} — {r['recommendation']}
# Action: Stop this RDS instance from AWS console or CLI
# aws rds stop-db-instance --db-instance-identifier {r['instance_id']}
''')
        elif r['resource_type'] == 'EBS':
            lines.append(f'''
# EBS Volume: {r['instance_id']} — {r['recommendation']}
# Action: Delete this unattached volume
# aws ec2 delete-volume --volume-id {r['instance_id']}
''')
        elif r['resource_type'] == 'ElasticIP':
            lines.append(f'''
# Elastic IP: {r['instance_id']} — {r['recommendation']}
# Action: Release this unused Elastic IP
# aws ec2 release-address --public-ip {r['instance_id']}
''')

    return "\n".join(lines)


def raise_github_pr(resources):
    token = os.getenv('GITHUB_TOKEN')
    repo_name = os.getenv('GITHUB_REPO')

    g = Github(token)
    repo = g.get_repo(repo_name)

    branch_name = "fix/cloud-cost-rightsizing"
    main_branch = repo.get_branch("main")

    try:
        repo.create_git_ref(
            ref=f"refs/heads/{branch_name}",
            sha=main_branch.commit.sha
        )
        print(f"✅ Branch {branch_name} created")
    except Exception as e:
        print(f"Branch may already exist: {e}")

    tf_content = generate_terraform_fix(resources)

    try:
        existing = repo.get_contents("terraform_fixes/rightsizing.tf", ref=branch_name)
        repo.update_file(
            path="terraform_fixes/rightsizing.tf",
            message="fix: auto-generated cloud cost rightsizing",
            content=tf_content,
            sha=existing.sha,
            branch=branch_name
        )
    except Exception:
        repo.create_file(
            path="terraform_fixes/rightsizing.tf",
            message="fix: auto-generated cloud cost rightsizing",
            content=tf_content,
            branch=branch_name
        )

    summary = "\n".join([f"- [{r['resource_type']}] `{r['instance_id']}` → {r['recommendation']}" for r in resources])

    pr = repo.create_pull(
        title=f"💰 Cost Fix: {len(resources)} Wasteful Resource(s) Detected",
        body=f"## Auto-generated Cloud Cost Intelligence PR\n\n"
             f"### Resources Found:\n{summary}\n\n"
             f"### Action\nReview and merge to apply Terraform fixes.",
        head=branch_name,
        base="main"
    )

    print(f"✅ PR raised: {pr.html_url}")
    return pr.html_url


if __name__ == "__main__":
    test_resources = [
        {'resource_type': 'EC2', 'instance_id': 'i-1234567890', 'instance_type': 't2.micro', 'recommendation': 'stop or downsize'},
    ]
    raise_github_pr(test_resources)