#!/bin/bash

set -e  # Exit if any command fails

# Ensure README.md exists
touch README.md

# Make sure we are in a git repository
if [ ! -d ".git" ]; then
  echo "Error: Not a git repository."
  exit 1
fi

# Define date range
start_date="2025-01-01"
end_date="2025-06-30"

# Convert to Unix timestamps
start_ts=$(date -d "$start_date" +%s)
end_ts=$(date -d "$end_date" +%s)

for i in {1..15}
do
  # Generate random timestamp between start and end
  range=$((end_ts - start_ts))
  random_offset=$(( (RANDOM << 15 | RANDOM) % range ))
  random_ts=$((start_ts + random_offset))

  # Format timestamp
  commit_date=$(date -d "@$random_ts" +"%Y-%m-%dT%H:%M:%S")

  # Make a commit
  echo "Random Commit $i" >> README.md
  git add README.md
  GIT_AUTHOR_DATE="$commit_date" GIT_COMMITTER_DATE="$commit_date" \
    git commit -m "Random Commit $i on $commit_date"
done

# Push all commits to remote
git push
