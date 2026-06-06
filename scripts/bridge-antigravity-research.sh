#!/usr/bin/env bash
# bridge-antigravity-research.sh
# Picks up AntiGravity research drops from ~/Projects/Research/<date>/
# and merges into project repo + Cowork memory + Google Drive knowledge-base (General, Daily, Components).
# Deterministic file operations only — no LLM, no network.
# Runs via launchd 10:00 daily (after AntiGravity 09:30 scheduled task).

set -euo pipefail

export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

# --- paths ---
RESEARCH_DIR="$HOME/Projects/Stack Watch"
REPO_DIR="$HOME/Projects/Project Instructions Template"
MEMORY_DIR="$HOME/Library/Application Support/Claude/local-agent-mode-sessions/29e8364e-108e-4b8c-a6e9-844642d34378/d2a14a4a-842c-4a14-8d08-e95e3332da6f/spaces/63d0d81e-7790-437b-822f-e30b21f6e8d7/memory"
LOG_FILE="$HOME/Library/Logs/bridge-antigravity-research.log"
GDRIVE_KNOWLEDGE_DIR="$HOME/My Drive/Stack Watch/knowledge-base"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"; }

compile_weekly_rollup() {
    local rollup_file="$RESEARCH_DIR/processed/weekly_rollup.txt"
    mkdir -p "$(dirname "$rollup_file")"
    
    echo "📅 <b>Stack Watch — Итоги недели (Weekly Rollup)</b>" > "$rollup_file"
    echo "Период: за последние 7 дней" >> "$rollup_file"
    echo "" >> "$rollup_file"
    
    # Find last 7 summaries in repo, preserving spaces in paths
    local files=()
    local old_ifs="$IFS"
    IFS=$'\n'
    files=($(find "$REPO_DIR/project-status/_summary" -name "*-stack-watch.md" 2>/dev/null | sort | tail -n 7 || echo ""))
    IFS="$old_ifs"
    
    if [[ ${#files[@]} -eq 0 ]]; then
        echo "<i>За прошедшую неделю обновлений не найдено.</i>" >> "$rollup_file"
        return
    fi
    
    for f in "${files[@]}"; do
        local fname
        fname=$(basename "$f")
        local fdate="${fname%-stack-watch.md}"
        
        # Extract Do now and Experiment sections using stateful awk to avoid range pitfalls
        local do_now exp
        do_now=$(awk '{ gsub(/\r/, ""); clean = $0; gsub(/^[ \t*•-]+|[ \t]+$/, "", clean); } /^## Do now/ { active = 1; next } /^## / && active { active = 0 } active { if (clean != "" && clean != "(none)" && clean != "_(none)_") print $0 }' "$f" | sed -e 's/^- /  • /' || echo "")
        exp=$(awk '{ gsub(/\r/, ""); clean = $0; gsub(/^[ \t*•-]+|[ \t]+$/, "", clean); } /^## Experiment/ { active = 1; next } /^## / && active { active = 0 } active { if (clean != "" && clean != "(none)" && clean != "_(none)_") print $0 }' "$f" | sed -e 's/^- /  • /' || echo "")
        
        if [[ -n "$do_now" || -n "$exp" ]]; then
            echo "📅 <b>$fdate:</b>" >> "$rollup_file"
            if [[ -n "$do_now" ]]; then
                echo "  <b>Do now:</b>" >> "$rollup_file"
                echo "$do_now" >> "$rollup_file"
            fi
            if [[ -n "$exp" ]]; then
                echo "  <b>Experiment:</b>" >> "$rollup_file"
                echo "$exp" >> "$rollup_file"
            fi
            echo "" >> "$rollup_file"
        fi
    done
    
    log "Compiled weekly rollup to $rollup_file"
    # Trigger bot to deliver weekly rollup
    "$HOME/Projects/Stack Watch/scripts/updates-news-deliver.sh" --weekly-rollup "$rollup_file" >> "$LOG_FILE" 2>&1 || log "Failed to deliver weekly rollup."
}

if [[ "${1:-}" == "--weekly" ]]; then
    log "=== bridge run start (weekly rollup mode) ==="
    compile_weekly_rollup
    log "=== bridge run end (weekly rollup) ==="
    exit 0
fi

log "=== bridge run start ==="

# --- find drops to process ---
DROPS=()
if [[ -n "${1:-}" ]]; then
    # Specific date folder requested
    DROPS+=("$RESEARCH_DIR/$1")
else
    # Find all YYYY-MM-DD directories in RESEARCH_DIR
    # Using nullglob to avoid literal pattern if no match
    shopt -s nullglob
    for d in "$RESEARCH_DIR"/[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]; do
        if [[ -d "$d" ]]; then
            DROPS+=("$d")
        fi
    done
    shopt -u nullglob
fi

if [[ ${#DROPS[@]} -eq 0 ]]; then
    log "No pending drop zones found. Exiting."
    log "=== bridge run end ==="
    exit 0
fi

for DROP in "${DROPS[@]}"; do
    TODAY="$(basename "$DROP")"
    log "--- Processing drop zone: $TODAY ---"

    # 1. Sanity: drop zone exists?
    if [[ ! -d "$DROP" ]]; then
        log "Drop zone directory $DROP does not exist, skipping."
        continue
    fi

    # 2. EMPTY marker — nothing to bridge
    if [[ -f "$DROP/EMPTY" ]]; then
        log "EMPTY marker found, no findings today."
        mkdir -p "$RESEARCH_DIR/processed"
        rm -rf "$RESEARCH_DIR/processed/${TODAY}_empty"
        mv "$DROP" "$RESEARCH_DIR/processed/${TODAY}_empty"
        log "Moved empty drop to processed/${TODAY}_empty."
        continue
    fi

    # 3. Already-processed guard
    if [[ ! -f "$DROP/REPORT.md" ]]; then
        # Clean up orphan drops older than 3 days to avoid accumulation
        if [[ "$TODAY" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
            folder_sec=$(date -j -f "%Y-%m-%d" "$TODAY" "+%s" 2>/dev/null || echo "0")
            current_sec=$(date "+%s")
            diff_days=$(((current_sec - folder_sec) / 86400))
            if [[ $diff_days -ge 3 ]]; then
                log "[ALERT] Orphan drop zone $TODAY is $diff_days days old and missing REPORT.md. Pruning folder."
                rm -rf "$DROP"
                continue
            fi
        fi
        log "REPORT.md missing — AntiGravity may still be writing or failed. Skipping $TODAY."
        continue
    fi

    if [[ -f "$DROP/.bridged" ]]; then
        log "Drop already bridged earlier today, skipping."
        continue
    fi

    # 4. Copy body files
    if [[ -d "$DROP/external-research" ]]; then
        mkdir -p "$REPO_DIR/external-research"
        mkdir -p "$GDRIVE_KNOWLEDGE_DIR/general/findings"
        mkdir -p "$GDRIVE_KNOWLEDGE_DIR/daily-digest"
        n=0
        for f in "$DROP/external-research"/*.md; do
            [[ -e "$f" ]] || continue
            base=$(basename "$f")
            base_txt="${base%.md}.txt"
            
            # Copy to Repo (keeps .md extension)
            if [[ ! -f "$REPO_DIR/external-research/$base" ]]; then
                cp "$f" "$REPO_DIR/external-research/"
            fi
            
            # Copy to GDrive General Findings (converts to .txt for NotebookLM)
            if [[ ! -f "$GDRIVE_KNOWLEDGE_DIR/general/findings/$base_txt" ]]; then
                cp "$f" "$GDRIVE_KNOWLEDGE_DIR/general/findings/$base_txt"
            fi
            
            # Copy to GDrive Daily Digest (converts to .txt for NotebookLM)
            if [[ ! -f "$GDRIVE_KNOWLEDGE_DIR/daily-digest/$base_txt" ]]; then
                cp "$f" "$GDRIVE_KNOWLEDGE_DIR/daily-digest/$base_txt"
            fi
            
            # Copy to GDrive Component specific folders (converts to .txt for NotebookLM) by parsing Touches line
            if grep -q "^\*\*Touches:\*\*" "$f"; then
                touches_line=$(grep "^\*\*Touches:\*\*" "$f" | sed 's/^\*\*Touches:\*\*[[:space:]]*//I')
                IFS=',' read -ra ADDR <<< "$touches_line"
                for comp in "${ADDR[@]}"; do
                    # Trim spaces, lowercase, slugify (replace spaces/slashes with hyphens)
                    comp_folder=$(echo "$comp" | xargs | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g' | sed 's/^-//;s/-$//')
                    if [[ -n "$comp_folder" ]]; then
                        mkdir -p "$GDRIVE_KNOWLEDGE_DIR/components/$comp_folder"
                        if [[ ! -f "$GDRIVE_KNOWLEDGE_DIR/components/$comp_folder/$base_txt" ]]; then
                            cp "$f" "$GDRIVE_KNOWLEDGE_DIR/components/$comp_folder/$base_txt"
                        fi
                    fi
                done
            fi
            
            n=$((n+1))
        done
        log "Copied $n body file(s) to repo (.md) and GDrive general, daily-digest, and components (.txt)."
    fi

    # 5. Append log rows
    if [[ -f "$DROP/log-additions.md" && -s "$DROP/log-additions.md" ]]; then
        cat "$DROP/log-additions.md" >> "$REPO_DIR/external-research-log.md"
        rows=$(wc -l < "$DROP/log-additions.md" | tr -d ' ')
        log "Appended $rows log row(s) to external-research-log.md."
    fi

    # 6. Copy project-status summary
    if [[ -f "$DROP/summary.md" ]]; then
        mkdir -p "$REPO_DIR/project-status/_summary"
        mkdir -p "$GDRIVE_KNOWLEDGE_DIR/general/summaries"
        mkdir -p "$GDRIVE_KNOWLEDGE_DIR/daily-digest"
        dest_repo="$REPO_DIR/project-status/_summary/${TODAY}-stack-watch.md"
        dest_general_summary="$GDRIVE_KNOWLEDGE_DIR/general/summaries/${TODAY}-stack-watch.txt"
        dest_daily_summary="$GDRIVE_KNOWLEDGE_DIR/daily-digest/${TODAY}-stack-watch.txt"
        
        if [[ ! -f "$dest_repo" ]]; then
            cp "$DROP/summary.md" "$dest_repo"
        fi
        if [[ ! -f "$dest_general_summary" ]]; then
            cp "$DROP/summary.md" "$dest_general_summary"
        fi
        if [[ ! -f "$dest_daily_summary" ]]; then
            cp "$DROP/summary.md" "$dest_daily_summary"
        fi
        log "Copied summary to repo (.md) and GDrive general and daily-digest (.txt)."
    fi

    # 7. Copy memory entries
    if [[ -d "$DROP/memory-entries" ]]; then
        n=0
        for f in "$DROP/memory-entries"/*.md; do
            [[ -e "$f" ]] || continue
            base=$(basename "$f")
            if [[ ! -f "$MEMORY_DIR/$base" ]]; then
                cp "$f" "$MEMORY_DIR/"
            fi
            n=$((n+1))
        done
        log "Copied $n memory entry file(s)."
    fi

    # 8. Append to MEMORY.md index
    if [[ -f "$DROP/memory-index-additions.txt" && -s "$DROP/memory-index-additions.txt" ]]; then
        cat "$DROP/memory-index-additions.txt" >> "$MEMORY_DIR/MEMORY.md"
        lines=$(wc -l < "$DROP/memory-index-additions.txt" | tr -d ' ')
        log "Appended $lines MEMORY.md index line(s)."
    fi

    # 9. Update _seen-urls.txt
    if [[ -f "$DROP/new-urls.txt" && -s "$DROP/new-urls.txt" ]]; then
        cat "$DROP/new-urls.txt" >> "$RESEARCH_DIR/_seen-urls.txt"
        # dedup in-place
        sort -u "$RESEARCH_DIR/_seen-urls.txt" -o "$RESEARCH_DIR/_seen-urls.txt"
        urls=$(wc -l < "$DROP/new-urls.txt" | tr -d ' ')
        log "Added $urls URL(s) to _seen-urls.txt (deduped)."
    fi

    # 10. Mark drop as bridged + move to processed
    has_breaking=0
    if [[ -f "$DROP/breaking-marker" ]]; then
        has_breaking=1
    fi

    touch "$DROP/.bridged"
    mkdir -p "$RESEARCH_DIR/processed"
    rm -rf "$RESEARCH_DIR/processed/$TODAY"
    mv "$DROP" "$RESEARCH_DIR/processed/$TODAY"
    log "Moved drop to processed/$TODAY."

    if [[ $has_breaking -eq 1 ]]; then
        log "Breaking marker found. Triggering immediate Telegram alert..."
        "$HOME/Projects/Stack Watch/scripts/updates-news-deliver.sh" --immediate --date "$TODAY" >> "$LOG_FILE" 2>&1 || log "Failed to trigger immediate alert."
    fi
done

# --- daily-digest clean up (sliding window of 7 days) ---
if [[ -d "$GDRIVE_KNOWLEDGE_DIR/daily-digest" ]]; then
    # Delete files older than 7 days in daily-digest folder
    find "$GDRIVE_KNOWLEDGE_DIR/daily-digest" -type f -mtime +7 -delete
    # Clean up empty directories if any
    find "$GDRIVE_KNOWLEDGE_DIR/daily-digest" -depth -type d -empty -delete
    log "Cleaned up daily-digest files older than 7 days."
fi

# --- generate rolling files for NotebookLM ---
log "Generating rolling files for NotebookLM..."

# 1. Rolling Daily Digest (7-Day sliding window)
if [[ -d "$GDRIVE_KNOWLEDGE_DIR/daily-digest" ]]; then
    rolling_daily="$GDRIVE_KNOWLEDGE_DIR/daily-digest-rolling.txt"
    echo "# Stack Watch Daily Digest — Rolling 7-Day Window" > "$rolling_daily"
    echo "Generated: $(date '+%Y-%m-%d %H:%M:%S')" >> "$rolling_daily"
    echo "---" >> "$rolling_daily"
    for f in "$GDRIVE_KNOWLEDGE_DIR/daily-digest"/*.txt; do
        if [[ -f "$f" ]]; then
            echo "" >> "$rolling_daily"
            cat "$f" >> "$rolling_daily"
            echo "" >> "$rolling_daily"
            echo "---" >> "$rolling_daily"
        fi
    done
    log "Regenerated daily-digest-rolling.txt."
fi

# 2. Rolling General Archive (Complete history)
if [[ -d "$GDRIVE_KNOWLEDGE_DIR/general" ]]; then
    rolling_archive="$GDRIVE_KNOWLEDGE_DIR/general-archive-rolling.txt"
    echo "# Stack Watch General Archive — Complete History" > "$rolling_archive"
    echo "Generated: $(date '+%Y-%m-%d %H:%M:%S')" >> "$rolling_archive"
    echo "---" >> "$rolling_archive"
    
    if [[ -d "$GDRIVE_KNOWLEDGE_DIR/general/summaries" ]]; then
        echo "" >> "$rolling_archive"
        echo "## PART 1: DAILY SUMMARIES" >> "$rolling_archive"
        echo "---" >> "$rolling_archive"
        for f in "$GDRIVE_KNOWLEDGE_DIR/general/summaries"/*.txt; do
            if [[ -f "$f" ]]; then
                cat "$f" >> "$rolling_archive"
                echo "" >> "$rolling_archive"
                echo "---" >> "$rolling_archive"
            fi
        done
    fi
    
    if [[ -d "$GDRIVE_KNOWLEDGE_DIR/general/findings" ]]; then
        echo "" >> "$rolling_archive"
        echo "## PART 2: DETAILED FINDINGS" >> "$rolling_archive"
        echo "---" >> "$rolling_archive"
        for f in "$GDRIVE_KNOWLEDGE_DIR/general/findings"/*.txt; do
            if [[ -f "$f" ]]; then
                cat "$f" >> "$rolling_archive"
                echo "" >> "$rolling_archive"
                echo "---" >> "$rolling_archive"
            fi
        done
    fi
    log "Regenerated general-archive-rolling.txt."
fi

# 3. Rolling Component specific files
if [[ -d "$GDRIVE_KNOWLEDGE_DIR/components" ]]; then
    for comp_dir in "$GDRIVE_KNOWLEDGE_DIR/components"/*; do
        if [[ -d "$comp_dir" ]]; then
            comp_name=$(basename "$comp_dir")
            # Slugify the component name for a clean, safe filename
            comp_slug=$(echo "$comp_name" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g' | sed 's/^-//;s/-$//')
            comp_archive="$comp_dir/${comp_slug}-rolling.txt"
            
            # Clean up old default rolling.txt file if it exists
            rm -f "$comp_dir/rolling.txt"
            
            echo "# Stack Watch Component Archive — $comp_name" > "$comp_archive"
            echo "Generated: $(date '+%Y-%m-%d %H:%M:%S')" >> "$comp_archive"
            echo "---" >> "$comp_archive"
            
            for f in "$comp_dir"/*.txt; do
                if [[ -f "$f" && "$(basename "$f")" != "${comp_slug}-rolling.txt" ]]; then
                    cat "$f" >> "$comp_archive"
                    echo "" >> "$comp_archive"
                    echo "---" >> "$comp_archive"
                fi
            done
        fi
    done
    log "Regenerated component-specific rolling files."
fi

# 4. Optional Direct Cloud Sync via rclone
if command -v rclone &>/dev/null; then
    if rclone listremotes 2>/dev/null | grep -q "^gdrive:$"; then
        log "Rclone with gdrive remote found. Running direct cloud sync..."
        rclone copy "$GDRIVE_KNOWLEDGE_DIR" gdrive:"Stack Watch/knowledge-base" >> "$LOG_FILE" 2>&1 || log "Rclone sync encountered errors."
    else
        log "Rclone found, but 'gdrive' remote is not configured. Run 'rclone config' to set up a 'gdrive' remote."
    fi
else
    log "Rclone not found. To bypass local macOS Drive client dependency, run 'brew install rclone' and configure a 'gdrive' remote."
fi

# 5. Static HTML Dashboard Generation
log "Generating premium status dashboard..."
python3 "$RESEARCH_DIR/scripts/generate_dashboard.py" >> "$LOG_FILE" 2>&1 || log "Dashboard generation encountered errors."

log "=== bridge run end (ok) ==="
exit 0
