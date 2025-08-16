#!/bin/bash

# -------- CONFIGURE THESE --------
GITHUB_USERNAME="The3DP"
REPO_NAME="ai-code-translator"
BRANCH="main"
# --------------------------------

# Navigate into the project folder
cd "$REPO_NAME" || { echo "Folder '$REPO_NAME' not found"; exit 1; }

# Initialize git and commit
git init
git add .
git commit -m "Initial commit"

# Create main branch (if not already created)
git branch -M $BRANCH

# Add GitHub remote
git remote add origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"

# Push to GitHub
git push -u origin $BRANCH

echo "✅ Project pushed to GitHub at https://github.com/$GITHUB_USERNAME/$REPO_NAME"
