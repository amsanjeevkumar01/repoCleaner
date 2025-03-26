# repoCleaner

## Overview
`repoCleaner` is a Python utility that identifies and deletes stale branches in GitHub repositories. It reads a list of repositories from a file (`masterRepoList.txt`), summarizes stale branches, prompts the user for deletion, and generates an execution summary.

## Features
- Reads repositories from `masterRepoList.txt`
- Identifies stale branches older than a defined time window (default: 1 year)
- Displays a summary of all branches and stale branches per repository
- Allows user selection of branches to delete
- Deletes selected branches
- Generates an execution summary

## Prerequisites
### 1. Install Dependencies
Ensure Python 3 is installed. Then install the required libraries:
```sh
pip install PyGithub python-dotenv
```

### 2. Set Up GitHub API Token
Obtain a **GitHub Personal Access Token** with `repo` scope from [GitHub Developer Settings](https://github.com/settings/tokens) and save it in a `.env` file:

```sh
GITHUB_TOKEN=your_personal_access_token_here
```

### 3. Create Repository List
Create a `masterRepoList.txt` file and add repository names (forked in your GitHub account), one per line:

```
github_username/docs
github_username/gh-ost
github_username/dmca
github_username/nPG-guidance
```

## Usage

### 1. Run the Utility
```sh
python repoCleaner.py
```

### 2. View Summary
After processing, `repoCleaner` displays:
- Total branches in each repository
- Stale branches (older than 1 year)
- A numbered list of stale branches

### 3. Select Branches for Deletion
Enter branches to delete using:
- `<repo_name>:<branch_number>` format (e.g., `docs:1, dmca:2`)
- `all` to delete all stale branches
- Press **Enter** to skip deletion

### 4. Review Execution Summary
Deleted branches and recommendations are stored in `repoCleaner_summary.txt`.

