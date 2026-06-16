#!/usr/bin/env bash
# Hermes — updates-Карлик delivery script
# Posts daily Stack Watch digest to operator's Telegram chat.
# Cron schedule: 5 10 * * * (right after bridge-antigravity-research.sh at 10:00)
#
# Usage:
#   updates-news-deliver.sh                  # today's summary, real send
#   updates-news-deliver.sh --dry-run        # today, print, do not send
#   updates-news-deliver.sh --date 2026-05-27        # specific date, real send
#   updates-news-deliver.sh --date 2026-05-27 --dry-run
#   updates-news-deliver.sh --force          # re-send today even if marker present
#
# Reads token from macOS Keychain (service: TELEGRAM_TOKEN_UPDATES, account: hermes).
# Idempotency marker: ~/.hermes/state/updates-last-sent.txt

set -euo pipefail

# --- defaults ---
SUMMARY_DIR="${SUMMARY_DIR:-$HOME/Projects/Project Instructions Template/project-status/_summary}"
RESEARCH_DIR="${RESEARCH_DIR:-$HOME/Projects/Project Instructions Template/external-research}"
STATE_FILE="${STATE_FILE:-$HOME/.hermes/state/updates-last-sent.txt}"
STATE_FILE_IMMEDIATE="${STATE_FILE_IMMEDIATE:-$HOME/.hermes/state/updates-immediate-sent.txt}"
STATE_FILE_WEEKLY="${STATE_FILE_WEEKLY:-$HOME/.hermes/state/updates-weekly-sent.txt}"
CHAT_ID="${TELEGRAM_HOME_CHANNEL:-7656475139}"
TOKEN_KEY="${TOKEN_KEY:-TELEGRAM_TOKEN_UPDATES}"

DATE="$(date '+%Y-%m-%d')"
DRY_RUN=0
FORCE=0
IMMEDIATE=0
WEEKLY_ROLLUP=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --date)    DATE="${2:?--date needs YYYY-MM-DD}"; shift 2 ;;
    --force)   FORCE=1; shift ;;
    --weekly-rollup) WEEKLY_ROLLUP="${2:?--weekly-rollup needs file path}"; shift 2 ;;
    --immediate) IMMEDIATE=1; shift ;;
    -h|--help) sed -n '2,16p' "$0"; exit 0 ;;
    *) echo "[updates] unknown arg: $1" >&2; exit 2 ;;
  esac
done

SUMMARY_FILE="$SUMMARY_DIR/$DATE-stack-watch.md"

# --- guards ---
if [[ -z "$WEEKLY_ROLLUP" ]]; then
  if [[ ! -f "$SUMMARY_FILE" ]]; then
    echo "[updates] no summary for $DATE: $SUMMARY_FILE" >&2
    # Exit 0 — not an error; bridge may not have run yet today.
    exit 0
  fi

  if [[ $FORCE -eq 0 && $DRY_RUN -eq 0 && -f "$STATE_FILE" ]]; then
    if grep -qx "$DATE" "$STATE_FILE"; then
      echo "[updates] already sent for $DATE (marker in $STATE_FILE)" >&2
      exit 0
    fi
  fi
else
  if [[ $FORCE -eq 0 && $DRY_RUN -eq 0 && -f "$STATE_FILE_WEEKLY" ]]; then
    if grep -qx "$DATE" "$STATE_FILE_WEEKLY"; then
      echo "[updates] Weekly rollup already sent for $DATE (marker in $STATE_FILE_WEEKLY)" >&2
      exit 0
    fi
  fi
fi

# --- parsers ---

# Extract slug+title pairs from a section header (e.g. "## Experiment").
# Reads lines until next "## " or EOF, picks "- <slug> — <title>" or "- <slug> -- <title>".
extract_section() {
  local section="$1"
  awk -v header="## $section" '
    $0 == header { active = 1; next }
    /^## / && active { active = 0 }
    active && /^- / {
      sub(/^- /, "", $0)
      # split on em-dash with spaces (canonical separator in summary)
      n = split($0, parts, / — /)
      if (n >= 2) {
        slug = parts[1]
        # rejoin everything after first em-dash as title
        title = parts[2]
        for (i = 3; i <= n; i++) title = title " — " parts[i]
        gsub(/^[ \t]+|[ \t]+$/, "", slug)
        gsub(/^[ \t]+|[ \t]+$/, "", title)
        if (slug != "" && slug !~ /^_/) print slug "\t" title
      }
    }
  ' "$SUMMARY_FILE"
}

# Look up metadata for a slug.
# Returns: url<TAB>touches<TAB>severity<TAB>tags
lookup_meta() {
  local slug="$1"
  local f="$RESEARCH_DIR/$slug.md"
  [[ -f "$f" ]] || { printf '\t\t\t\n'; return; }
  local url touches severity tags
  url=$(grep -m1 -E '^\*\*Original URL:\*\*' "$f" | sed -E 's/^\*\*Original URL:\*\*[[:space:]]*//' || echo "")
  touches=$(grep -m1 -E '^\*\*Touches:\*\*' "$f" | sed -E 's/^\*\*Touches:\*\*[[:space:]]*//' || echo "")
  severity=$(grep -m1 -E '^\*\*Severity:\*\*' "$f" | sed -E 's/^\*\*Severity:\*\*[[:space:]]*//' | tr '[:upper:]' '[:lower:]' || echo "")
  tags=$(grep -m1 -E '^\*\*Tags:\*\*' "$f" | sed -E 's/^\*\*Tags:\*\*[[:space:]]*//' || echo "")
  printf '%s\t%s\t%s\t%s\n' "$url" "$touches" "$severity" "$tags"
}

# MarkdownV2 escape: per Telegram docs, escape: _ * [ ] ( ) ~ ` > # + - = | { } . !
# We use HTML formatting instead (simpler — only escape & < >).
html_escape() {
  sed -e 's/&/\&amp;/g' -e 's/</\&lt;/g' -e 's/>/\&gt;/g'
}

# Map components to thematic layers:
# 1 = AI Agents & LLMs (🤖)
# 2 = Local Dev Environment (💻)
# 3 = System Memory & CLI (🗄️)
# 4 = Other
get_component_layer() {
  local touches="$1"
  case "$touches" in
    *ChatGPT*|*Codex*|*Claude*|*Kimi*|*Hermes*|*OpenClaw*|*Ollama*|*Gemini*|*NotebookLM*|*Pi*|*GLM*|*Minimax*|*Qwen*|*Wispr*|*Antigravity*)
      echo "1" ;;
    *Obsidian*|*Chrome*|*macOS*|*Homebrew*|*npm*|*tmux*|*iTerm2*)
      echo "2" ;;
    *Mem0*|*Desktop*|*Git*)
      echo "3" ;;
    *)
      echo "4" ;;
  esac
}

# Global list of slugs to attach as documents
SLUGS_TO_SEND=""

# --- build message ---

format_findings() {
  local section="$1"
  local layer1=""
  local layer2=""
  local layer3=""
  local layer4=""
  local minor=""
  
  while IFS=$'\t' read -r slug title; do
    [[ -z "$slug" ]] && continue
    
    local url touches severity tags
    IFS=$'\t' read -r url touches severity tags < <(lookup_meta "$slug")
    
    # Phase 4.1 routing: If immediate mode, only send breaking/security findings
    if [[ ${IMMEDIATE:-0} -eq 1 && "$severity" != "breaking/security" ]]; then
      continue
    fi
    
    SLUGS_TO_SEND+="$slug "
    
    local title_esc touches_esc emoji="•"
    title_esc=$(printf '%s' "$title" | html_escape)
    touches_esc=$(printf '%s' "${touches:-}" | html_escape)
    
    case "$severity" in
      "breaking/security") emoji="🚨" ;;
      "performance")       emoji="⚡" ;;
      "integration")       emoji="🧩" ;;
      *)                   emoji="•" ;;
    esac
    
    local item=""
    if [[ -n "$url" ]]; then
      item="  $emoji <b>$title_esc</b> (${touches_esc}) — <a href=\"$url\">источник</a>"
    else
      item="  $emoji <b>$title_esc</b> (${touches_esc}) — <i>ссылка не найдена</i>"
    fi
    
    if [[ "$severity" == "minor" ]]; then
      if [[ -n "$url" ]]; then
        minor+="• $title_esc (${touches_esc}) — <a href=\"$url\">источник</a>"$'\n'
      else
        minor+="• $title_esc (${touches_esc})"$'\n'
      fi
      continue
    fi
    
    local layer_id
    layer_id=$(get_component_layer "${touches:-}")
    case "$layer_id" in
      1) layer1+="$item"$'\n' ;;
      2) layer2+="$item"$'\n' ;;
      3) layer3+="$item"$'\n' ;;
      *) layer4+="$item"$'\n' ;;
    esac
  done < <(extract_section "$section")
  
  local output=""
  if [[ -n "$layer1" ]]; then
    output+="🤖 <b>AI Agents & LLMs:</b>"$'\n'"$layer1"
  fi
  if [[ -n "$layer2" ]]; then
    output+="💻 <b>Local Dev Environment:</b>"$'\n'"$layer2"
  fi
  if [[ -n "$layer3" ]]; then
    output+="🗄️ <b>System Memory & CLI:</b>"$'\n'"$layer3"
  fi
  if [[ -n "$layer4" ]]; then
    output+="📦 <b>Other Components:</b>"$'\n'"$layer4"
  fi
  if [[ -n "$minor" ]]; then
    output+="<i>Мелкие обновления (Minor):</i>"$'\n'"$minor"
  fi
  
  printf '%s' "$output"
}

build_message() {
  local stats=""
  if [[ -f "$SUMMARY_FILE" ]]; then
    stats=$(grep -m1 -i "By verdict:" "$SUMMARY_FILE" | sed -E 's/^\*\*By verdict:\*\*[[:space:]]*//I' | sed -E 's/^\*By verdict:\*[[:space:]]*//I' | sed -E 's/^By verdict:[[:space:]]*//I' || echo "")
  fi
  
  local body=""
  if [[ ${IMMEDIATE:-0} -eq 1 ]]; then
    body+="🚨 <b>CRITICAL ALERT: Stack Watch — $DATE</b>"$'\n\n'
  else
    if [[ -n "$stats" ]]; then
      body+="📰 <b>Stack Watch — $DATE</b> [${stats}]"$'\n\n'
    else
      body+="📰 <b>Stack Watch — $DATE</b>"$'\n\n'
    fi
  fi

  local do_now exp park
  do_now=$(format_findings 'Do now (high confidence)')
  exp=$(format_findings 'Experiment')
  park=$(format_findings 'Parking')

  if [[ -n "$do_now" ]]; then
    body+="<b>Внедрить сейчас (Do now):</b>"$'\n'"$do_now"$'\n'
  fi
  if [[ -n "$exp" ]]; then
    body+="<b>Эксперименты (Experiment):</b>"$'\n'"$exp"$'\n'
  fi
  if [[ -n "$park" ]]; then
    body+="<b>Отложено (Parking):</b>"$'\n'"$park"$'\n'
  fi

  if [[ -z "$do_now$exp$park" ]]; then
    if [[ ${IMMEDIATE:-0} -eq 1 ]]; then
      # If immediate mode had no breaking alerts, send nothing
      body=""
    else
      body+="<i>Сегодня ничего не появилось — summary пустой.</i>"$'\n'
    fi
  fi

  printf '%s' "$body"
}

# --- send ---

send_telegram() {
  local text="$1"
  local reply_markup="${2:-}"
  local token
  token="${TELEGRAM_TOKEN_UPDATES:-}"
  if [[ -z "$token" ]]; then
    token=$(security find-generic-password -a hermes -s "$TOKEN_KEY" -w 2>/dev/null || true)
  fi
  if [[ -z "$token" ]]; then
    echo "[updates] ERROR: token '$TOKEN_KEY' not found in env or Keychain. Run:" >&2
    echo "  security add-generic-password -a hermes -s $TOKEN_KEY -w '<token>'" >&2
    exit 3
  fi

  local attempt=1
  local max_attempts=3
  local delay=5
  local resp=""
  local success=0

  while [[ $attempt -le $max_attempts ]]; do
    echo "[updates] Sending to Telegram (attempt $attempt/$max_attempts)..."
    if [[ -n "$reply_markup" ]]; then
      resp=$(curl -sS -X POST "https://api.telegram.org/bot${token}/sendMessage" \
        --data-urlencode "chat_id=${CHAT_ID}" \
        --data-urlencode "parse_mode=HTML" \
        --data-urlencode "disable_web_page_preview=true" \
        --data-urlencode "reply_markup=${reply_markup}" \
        --data-urlencode "text=${text}" 2>&1) || {
          echo "[updates] Curl connection error on attempt $attempt: $resp" >&2
          resp=""
        }
    else
      resp=$(curl -sS -X POST "https://api.telegram.org/bot${token}/sendMessage" \
        --data-urlencode "chat_id=${CHAT_ID}" \
        --data-urlencode "parse_mode=HTML" \
        --data-urlencode "disable_web_page_preview=true" \
        --data-urlencode "text=${text}" 2>&1) || {
          echo "[updates] Curl connection error on attempt $attempt: $resp" >&2
          resp=""
        }
    fi

    if [[ -n "$resp" ]] && echo "$resp" | grep -q '"ok":true'; then
      success=1
      break
    else
      echo "[updates] Attempt $attempt failed. Telegram response: $resp" >&2
      if [[ $attempt -lt $max_attempts ]]; then
        echo "[updates] Waiting $delay seconds before retry..." >&2
        sleep $delay
        delay=$((delay * 3))
      fi
    fi
    attempt=$((attempt + 1))
  done

  if [[ $success -eq 1 ]]; then
    echo "[updates] sent OK for $DATE"
    if [[ -n "$WEEKLY_ROLLUP" ]]; then
      mkdir -p "$(dirname "$STATE_FILE_WEEKLY")"
      echo "$DATE" >> "$STATE_FILE_WEEKLY"
      sort -u "$STATE_FILE_WEEKLY" -o "$STATE_FILE_WEEKLY"
    elif [[ ${IMMEDIATE:-0} -eq 1 ]]; then
      mkdir -p "$(dirname "$STATE_FILE_IMMEDIATE")"
      echo "$DATE" >> "$STATE_FILE_IMMEDIATE"
      sort -u "$STATE_FILE_IMMEDIATE" -o "$STATE_FILE_IMMEDIATE"
    else
      mkdir -p "$(dirname "$STATE_FILE")"
      echo "$DATE" >> "$STATE_FILE"
      sort -u "$STATE_FILE" -o "$STATE_FILE"
    fi
  else
    echo "[updates] ERROR: Failed to send Telegram notification after $max_attempts attempts." >&2
    exit 4
  fi
}

send_telegram_chunked() {
  local full_text="$1"
  local reply_markup="${2:-}"
  local len=${#full_text}
  if [[ $len -le 4000 ]]; then
    send_telegram "$full_text" "$reply_markup"
    return
  fi
  
  echo "[updates] Message length ($len) exceeds 4000 chars. Chunking..."
  local chunk=""
  local chunk_num=1
  
  while IFS= read -r line; do
    if [[ $(( ${#chunk} + ${#line} + 1 )) -gt 4000 ]]; then
      echo "[updates] Sending chunk $chunk_num..."
      send_telegram "$chunk"
      chunk=""
      chunk_num=$((chunk_num + 1))
      sleep 1
    fi
    chunk+="$line"$'\n'
  done <<< "$full_text"
  
  if [[ -n "$chunk" ]]; then
    echo "[updates] Sending final chunk $chunk_num..."
    send_telegram "$chunk" "$reply_markup"
  fi
}

send_document() {
  local slug="$1"
  local f="$RESEARCH_DIR/$slug.md"
  [[ -f "$f" ]] || return
  token="${TELEGRAM_TOKEN_UPDATES:-}"
  if [[ -z "$token" ]]; then
    token=$(security find-generic-password -a hermes -s "$TOKEN_KEY" -w 2>/dev/null || true)
  fi
  [[ -n "$token" ]] || return
  
  echo "[updates] Attaching document details for $slug..."
  curl -sS -X POST "https://api.telegram.org/bot${token}/sendDocument" \
    -F "chat_id=${CHAT_ID}" \
    -F "document=@$f" \
    -F "caption=Детали исследования: $slug" >/dev/null || true
}

# --- main ---

# Read updates-specific state files
# (Already defined above)

# Guard for immediate alert deduplication
if [[ $IMMEDIATE -eq 1 && $FORCE -eq 0 && $DRY_RUN -eq 0 && -f "$STATE_FILE_IMMEDIATE" ]]; then
  if grep -qx "$DATE" "$STATE_FILE_IMMEDIATE"; then
    echo "[updates] Immediate alert already sent for $DATE (marker in $STATE_FILE_IMMEDIATE)" >&2
    exit 0
  fi
fi

# Build or read message
if [[ -n "$WEEKLY_ROLLUP" ]]; then
  if [[ ! -f "$WEEKLY_ROLLUP" ]]; then
    echo "[updates] ERROR: Weekly rollup file $WEEKLY_ROLLUP does not exist." >&2
    exit 5
  fi
  MSG=$(cat "$WEEKLY_ROLLUP")
  SLUGS_TO_SEND=""
else
  MSG="$(build_message)"
  # Collect slugs in parent shell to avoid subshell scoping issues
  SLUGS_TO_SEND=""
  for section in 'Do now (high confidence)' 'Experiment' 'Parking'; do
    while IFS=$'\t' read -r slug title; do
      if [[ -n "$slug" ]]; then
        url="" touches="" severity="" tags=""
        IFS=$'\t' read -r url touches severity tags < <(lookup_meta "$slug")
        if [[ ${IMMEDIATE:-0} -eq 1 && "$severity" != "breaking/security" ]]; then
          continue
        fi
        SLUGS_TO_SEND+="$slug "
      fi
    done < <(extract_section "$section")
  done
fi

# Dry run mode exit
if [[ $DRY_RUN -eq 1 ]]; then
  echo "===== DRY RUN — $DATE — chat_id=$CHAT_ID ====="
  if [[ -z "$MSG" ]]; then
    echo "(Empty message - no alerts)"
  else
    printf '%s\n' "$MSG"
  fi
  echo "===== END DRY RUN ====="
  exit 0
fi

# Exit gracefully if immediate alert has no breaking findings
if [[ $IMMEDIATE -eq 1 && -z "$MSG" ]]; then
  echo "[updates] No breaking findings for immediate alert, exiting."
  exit 0
fi

# Generate inline keyboard markup if there are findings and not weekly rollup
KEYBOARD_JSON=""
if [[ -z "$WEEKLY_ROLLUP" && -n "$SLUGS_TO_SEND" ]]; then
  rows=""
  for slug in $SLUGS_TO_SEND; do
    if [[ -n "$rows" ]]; then
      rows+=","
    fi
    rows+="[{\"text\":\"🅿️ Park: $slug\",\"callback_data\":\"park:$slug:$DATE\"},{\"text\":\"❌ Skip: $slug\",\"callback_data\":\"skip:$slug:$DATE\"}]"
  done
  if [[ -n "$rows" ]]; then
    KEYBOARD_JSON="{\"inline_keyboard\":[$rows]}"
  fi
fi

send_telegram_chunked "$MSG" "$KEYBOARD_JSON"

# Send detail documents only if main send succeeded
sent_marker="$STATE_FILE"
[[ $IMMEDIATE -eq 1 ]] && sent_marker="$STATE_FILE_IMMEDIATE"
[[ -n "$WEEKLY_ROLLUP" ]] && sent_marker="$STATE_FILE_WEEKLY"

if [[ -f "$sent_marker" ]] && grep -qx "$DATE" "$sent_marker"; then
  for slug in $SLUGS_TO_SEND; do
    send_document "$slug"
  done
fi
