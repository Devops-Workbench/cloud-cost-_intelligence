import os
from github import Github
from dotenv import load_dotenv

load_dotenv()

def generate_terraform_fix(idle_instances):
    tf_lines = ["# Auto-generated Terraform fix"]
    for inst in idle_instances:
        tf_lines.append(f"# Instance: {inst[chr(39)+'instance_id'+chr(39)]} - {inst[chr(39)+'instance_type'+chr(39)]} - CPU: {inst[chr(39)+'avg_cpu'+chr(39)]}%")
    return chr(10).join(tf_lines)

def raise_github_pr(idle_instances):
    token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("GITHUB_REPO")
    g = Github(token)
    repo = g.get_repo(repo_name)
    branch_name = "fix/idle-ec2-rightsizing"
    main_branch = repo.get_branch("main")
    try:
        repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=main_branch.commit.sha)
    except Exception as e:
        print(f"Branch may exist: {e}")
    tf_content = generate_terraform_fix(idle_instances)
    try:
        existing = repo.get_contents("terraform_fixes/rightsizing.tf", ref=branch_name)
        repo.update_file("terraform_fixes/rightsizing.tf", "fix: rightsizing", tf_content, existing.sha, branch=branch_name)
    except Exception:
        repo.create_file("terraform_fixes/rightsizing.tf", "fix: rightsizing", tf_content, branch=branch_name)
    pr = repo.create_pull(title="Cost Fix: Idle EC2 Instances", body="Auto-generated", head=branch_name, base="main")
    print(f"PR raised: {pr.html_url}")
    return pr.html_url
