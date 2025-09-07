#!/bin/bash

# Check if both parameters are provided
if [ $# -ne 2 ]; then
    echo "Usage: $0 <year> <month>"
    echo "Example: $0 2025 8"
    exit 1
fi

# Get input parameters
YEAR=$1
MONTH=$2

# Calculate previous month
PREV_MONTH=$((MONTH - 1))
PREV_YEAR=$YEAR

# Handle year rollover if previous month is 0
if [ $PREV_MONTH -eq 0 ]; then
    PREV_MONTH=12
    PREV_YEAR=$((YEAR - 1))
fi

# Format months with leading zeros
CURRENT_MONTH_FORMATTED=$(printf "%02d" $MONTH)
PREV_MONTH_FORMATTED=$(printf "%02d" $PREV_MONTH)

# Create search and replace strings
SEARCH_STRING="${PREV_YEAR}-${PREV_MONTH_FORMATTED}"
REPLACE_STRING="${YEAR}-${CURRENT_MONTH_FORMATTED}"

echo "Searching for: $SEARCH_STRING"
echo "Replacing with: $REPLACE_STRING"

# Find and replace in specific folders and files only
CHANGES_MADE=false
{
    find ./src -type f \( -name "*.py" -o -name "*.md" -o -name "*.html" \) 2>/dev/null
    [ -f "./README.md" ] && echo "./README.md"
} | while read file; do
    if grep -q "$SEARCH_STRING" "$file" 2>/dev/null; then
        echo "Updating file: $file"
        sed -i.bak "s/$SEARCH_STRING/$REPLACE_STRING/g" "$file"
        rm "$file.bak"  # Remove backup file
        echo "CHANGED" > /tmp/script_changed_flag
    fi
done

# Check if any files were changed
if [ -f /tmp/script_changed_flag ]; then
    echo "Files were changed. Running git commands..."
    git add .
    git commit -m "update monthly data to $REPLACE_STRING"
    git push origin master
    echo "Git commit completed."
    rm /tmp/script_changed_flag  # Clean up the flag file
else
    echo "No files were changed. Skipping git commands."
fi
