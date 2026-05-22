#!/bin/bash
# AI News Daily - 每日自动更新脚本
# 每天早上8点执行：搜索新闻 → 更新HTML → 推送GitHub

WORKSPACE="/Users/hrr/Desktop/项目/agent/clawBot/workspace/temp/ai-news"
LOG_FILE="$WORKSPACE/data/cron.log"
TODAY=$(date +%Y-%m-%d)

echo "[$TODAY $(date +%H:%M:%S)] 🚀 Starting daily AI news update..." >> "$LOG_FILE"

cd "$WORKSPACE" || exit 1

# 运行 Python 更新脚本（推送已有数据）
python3 scripts/update-news.py --push-only 2>> "$LOG_FILE"

echo "[$TODAY $(date +%H:%M:%S)] ✅ Daily update completed" >> "$LOG_FILE"
