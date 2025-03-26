import os
import datetime
from github import Github
from dotenv import load_dotenv

# Load GitHub token from .env file
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    print("GitHub token not found. Please set GITHUB_TOKEN in the environment.")
    exit(1)

# Initialize GitHub API client
g = Github(GITHUB_TOKEN)

# Configuration
TW_YEARS = 1  # Time window: 1 year
SUMMARY_FILE = "repoCleaner_summary.txt"


def read_repositories(file_path="masterRepoList.txt"):
    """Read repository names from a text file."""
    with open(file_path, "r") as file:
        return [line.strip() for line in file if line.strip()]


def get_stale_branches(repo, tw_years=TW_YEARS):
    """Identify stale branches based on last commit date."""
    stale_branches = []
    all_branches = []
    cutoff_date = datetime.datetime.utcnow() - datetime.timedelta(days=tw_years * 365)

    for branch in repo.get_branches():
        commit_date = branch.commit.commit.committer.date
        commit_date = commit_date.replace(tzinfo=None)

        all_branches.append(branch.name)

        if commit_date < cutoff_date:
            stale_branches.append(branch.name)

    return {
        "total_branches": len(all_branches),
        "stale_branches": len(stale_branches),
        "stale_branch_list": stale_branches,
    }


def display_summary(repo_summaries):
    """Display a consolidated summary of all repositories."""
    print("\nConsolidated Summary:")
    print("=" * 50)

    for repo_name, summary in repo_summaries.items():
        print(f"\nRepository: {repo_name}")
        print(f"   - Total branches: {summary['total_branches']}")
        print(f"   - Stale branches: {summary['stale_branches']}")

        if summary["stale_branches"] > 0:
            for i, branch in enumerate(summary["stale_branch_list"], 1):
                print(f"     {i}. {branch}")


def user_confirmation(repo_summaries):
    """Ask user which stale branches should be deleted across all repos."""
    to_delete = {}

    print("\nEnter branches to delete across all repositories")
    print("   - Use format: <repo_name>:<branch_number>")
    print("   - Example: docs:1, dmca:2, docs:3")
    print("   - Type 'all' to delete ALL stale branches")
    print("   - Press Enter to skip deletion")

    choices = input("\nEnter selection: ").strip()

    if choices.lower() == "all":
        for repo, summary in repo_summaries.items():
            to_delete[repo] = summary["stale_branch_list"]
    elif choices:
        try:
            entries = [x.strip() for x in choices.split(",")]
            for entry in entries:
                repo_name, branch_idx = entry.split(":")
                repo_name = repo_name.strip()
                branch_idx = int(branch_idx.strip()) - 1

                if repo_name in repo_summaries and 0 <= branch_idx < len(
                        repo_summaries[repo_name]["stale_branch_list"]):
                    to_delete.setdefault(repo_name, []).append(
                        repo_summaries[repo_name]["stale_branch_list"][branch_idx])
                else:
                    print(f"Invalid selection: {entry}")
        except Exception as e:
            print(f"Error processing input: {e}")

    return to_delete


def delete_branch(repo, branch_name):
    """Delete a branch from a repository."""
    try:
        ref = repo.get_git_ref(f"heads/{branch_name}")
        ref.delete()
        print(f"Deleted branch: {repo.full_name}/{branch_name}")
        return True
    except Exception as e:
        print(f"Error deleting {repo.full_name}/{branch_name}: {e}")
        return False


def generate_summary(repo_summaries, deleted_branches):
    """Write an executive summary to a file."""
    with open(SUMMARY_FILE, "w") as file:
        file.write("RepoCleaner Execution Summary\n")
        file.write("=" * 50 + "\n")

        for repo, summary in repo_summaries.items():
            file.write(f"\nRepository: {repo}\n")
            file.write(f"   - Total branches: {summary['total_branches']}\n")
            file.write(f"   - Stale branches: {summary['stale_branches']}\n")

        if deleted_branches:
            file.write("\nDeleted Branches:\n")
            for repo, branches in deleted_branches.items():
                file.write(f"{repo}:\n")
                for branch in branches:
                    file.write(f"   - {branch}\n")

    print(f"\nExecution summary saved in {SUMMARY_FILE}")


def main():
    repositories = read_repositories()
    repo_summaries = {}

    print("\nProcessing all repositories...\n")

    for repo_name in repositories:
        try:
            repo = g.get_repo(repo_name)
            summary = get_stale_branches(repo)
            repo_summaries[repo_name] = summary
        except Exception as e:
            print(f"Error accessing {repo_name}: {e}")

    # Display summary first
    display_summary(repo_summaries)

    # Get user selection for deletion
    to_delete = user_confirmation(repo_summaries)

    deleted_branches = {}

    for repo_name, branches in to_delete.items():
        try:
            repo = g.get_repo(repo_name)
            deleted_branches[repo_name] = []
            for branch in branches:
                if delete_branch(repo, branch):
                    deleted_branches[repo_name].append(branch)
        except Exception as e:
            print(f"Error processing {repo_name}: {e}")

    # Generate execution summary
    generate_summary(repo_summaries, deleted_branches)


if __name__ == "__main__":
    main()
