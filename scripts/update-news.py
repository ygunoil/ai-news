#!/usr/bin/env python3
"""
AI News Daily - 每日自动更新脚本
功能：搜索 AI 新闻 → 生成 JSON → 更新 HTML → 推送 GitHub
"""
import os
import sys
import json
import subprocess
import re
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = os.environ.get("WORKSPACE", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(WORKSPACE, "data", "news")
HTML_PATH = os.path.join(WORKSPACE, "index.html")
TEMPLATE_PATH = os.path.join(WORKSPACE, "scripts", "html_template.html")

def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(os.path.join(WORKSPACE, "scripts"), exist_ok=True)

def save_news_json(date_str, news_data):
    """保存当日新闻 JSON"""
    path = os.path.join(DATA_DIR, f"{date_str}.json")
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(news_data, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved news JSON: {path}")

def load_all_news():
    """加载所有日期的新闻数据"""
    all_news = {}
    if os.path.exists(DATA_DIR):
        for fname in sorted(os.listdir(DATA_DIR)):
            if fname.endswith('.json'):
                date_key = fname.replace('.json', '')
                fpath = os.path.join(DATA_DIR, fname)
                with open(fpath, 'r', encoding='utf-8') as f:
                    all_news[date_key] = json.load(f)
    return all_news

def build_html(all_news):
    """用新闻数据替换 HTML 模板中的占位符"""
    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        html = f.read()
    
    news_json = json.dumps(all_news, ensure_ascii=False, indent=2)
    # 替换占位符
    pattern = r'/\*__NEWS_DATA\*/\{.*?\}/\*__END_NEWS_DATA\*/'
    replacement = f'/*__NEWS_DATA__*/{news_json}/*__END_NEWS_DATA__*/'
    new_html = re.sub(pattern, replacement, html, flags=re.DOTALL)
    
    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print(f"✅ Updated index.html with {len(all_news)} days of news")

def git_push():
    """提交并推送到 GitHub"""
    os.chdir(WORKSPACE)
    today = datetime.now().strftime('%Y-%m-%d')
    
    cmds = [
        ["git", "add", "-A"],
        ["git", "commit", "-m", f"📰 Daily AI News Update: {today}"],
        ["git", "push", "origin", "main"],
    ]
    for cmd in cmds:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0 and "nothing to commit" not in result.stdout:
            print(f"⚠️  {' '.join(cmd)}: {result.stderr}")
        else:
            print(f"✅ {' '.join(cmd)}")

def main():
    ensure_dirs()
    
    # 此脚本作为定时任务触发时，AI 会先搜索新闻并调用此脚本
    # 如果只是推送已有数据
    if "--push-only" in sys.argv:
        all_news = load_all_news()
        build_html(all_news)
        git_push()
        return
    
    # 如果传入了新闻数据文件
    if "--news-file" in sys.argv:
        idx = sys.argv.index("--news-file")
        news_file = sys.argv[idx + 1]
        with open(news_file, 'r', encoding='utf-8') as f:
            news_data = json.load(f)
        date_str = news_data.get("date", datetime.now().strftime('%Y-%m-%d'))
        save_news_json(date_str, news_data)
    
    all_news = load_all_news()
    build_html(all_news)
    git_push()

if __name__ == "__main__":
    main()
