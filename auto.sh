#!/bin/bash

# Make sure README.md exists
touch README.md

for i in {1..15}
do
  # Generate a random date between Jan 1 and June 30, 2025
  start_date="2025-01-01"
  end_date="2025-06-30"

  # Convert to timestamps
  start_ts=$(date -d "$start_date" +%s)
  end_ts=$(date -d "$end_date" +%s)

  # Generate a better random timestamp in that range
  range=$((end_ts - start_ts))
  random_offset=$(((RANDOM << 15 | RANDOM) % range))
  random_ts=$((start_ts + random_offset))

  # Format it back to a date string
  commit_date=$(date -d "@$random_ts" +"%Y-%m-%dT%H:%M:%S")

  # Make a commit
  echo "Random Commit $i" >> README.md
  git add README.md
  GIT_AUTHOR_DATE="$commit_date" GIT_COMMITTER_DATE="$commit_date" \
  git commit -m "Random Commit $i on $commit_date"
