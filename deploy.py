#!/usr/bin/env python3
"""
daily_log.md → dayeonYou.github.io 자동 배포 스크립트
사용: python3 deploy.py [daily_log.md 경로]
"""

import sys
import re
import os
import subprocess
from datetime import date
from pathlib import Path

REPO_DIR = Path(__file__).parent
LOG_DIR = Path.home() / "onDeviceAI" / "logs"
DEFAULT_LOG = LOG_DIR / "daily_log.md"

ENTRY_TEMPLATE = """
    <div class="log-entry">
      <div class="log-header">
        <span class="log-day">{day_label}</span>
        <span class="log-date">{date_str}</span>
      </div>
      <div class="log-title">{title}</div>
      {did_html}
      {blocked_html}
      {next_html}
    </div>"""

SECTION_TEMPLATE = """      <div class="log-section">
        <div class="log-section-label">{label}</div>
        <div class="log-section-content {cls}">{content}</div>
      </div>"""


def parse_log(log_path: Path) -> list[dict]:
    """daily_log.md에서 Day 블록들을 파싱"""
    text = log_path.read_text(encoding="utf-8")
    entries = []

    # Day 블록 분리 (## Day XX 또는 # Day XX)
    blocks = re.split(r'\n(?=#{1,2} Day \d+)', text.strip())

    for block in blocks:
        if not block.strip():
            continue
        lines = block.strip().splitlines()
        header = lines[0].strip()

        day_match = re.search(r'Day\s*(\d+)', header, re.IGNORECASE)
        if not day_match:
            continue

        day_num = int(day_match.group(1))

        # 날짜 추출 (헤더에 있으면)
        date_match = re.search(r'(\d{4}[-./]\d{2}[-./]\d{2})', header)
        date_str = date_match.group(1).replace('.', '-').replace('/', '-') if date_match else ""

        # 타이틀 (헤더 뒤에 오는 첫 번째 의미 있는 줄)
        title = ""
        did, blocked, next_day = [], [], []
        current = None

        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            low = line.lower()
            if "오늘 한 것" in low or "한 것" in low:
                current = "did"
            elif "막힌 것" in low or "막힌것" in low:
                current = "blocked"
            elif "내일 할 것" in low or "내일" in low:
                current = "next"
            elif line.startswith("#"):
                continue
            else:
                if current == "did":
                    did.append(line.lstrip("-• "))
                elif current == "blocked":
                    blocked.append(line.lstrip("-• "))
                elif current == "next":
                    next_day.append(line.lstrip("-• "))
                elif not title and current is None:
                    title = line.lstrip("-• ")

        if not title and did:
            title = did[0]

        entries.append({
            "day": day_num,
            "date": date_str,
            "title": title or f"Day {day_num}",
            "did": did,
            "blocked": blocked,
            "next": next_day,
        })

    entries.sort(key=lambda x: x["day"], reverse=True)
    return entries


def render_section(label, items, cls=""):
    if not items:
        return ""
    content = "<br>".join(f"• {i}" for i in items if i)
    return SECTION_TEMPLATE.format(label=label, content=content, cls=cls)


def build_html(entries: list[dict]) -> str:
    if not entries:
        return """
    <div class="empty-state">
      <p>$ waiting for first log...<span class="cursor">_</span></p>
    </div>"""

    html = ""
    for e in entries:
        did_html = render_section("오늘 한 것", e["did"])
        blocked_html = render_section("막힌 것", e["blocked"], "blocked")
        next_html = render_section("내일 할 것", e["next"], "next")
        html += ENTRY_TEMPLATE.format(
            day_label=f"Day {e['day']}",
            date_str=e["date"] or str(date.today()),
            title=e["title"],
            did_html=did_html,
            blocked_html=blocked_html,
            next_html=next_html,
        )
    return html


def inject_logs(entries: list[dict]):
    index_path = REPO_DIR / "index.html"
    html = index_path.read_text(encoding="utf-8")
    new_content = build_html(entries)
    # log-list 사이 내용 교체
    html = re.sub(
        r'(<div class="log-list" id="log-list">).*?(</div>\s*\n\s*<footer)',
        rf'\1{new_content}\n    \2',
        html,
        flags=re.DOTALL
    )
    index_path.write_text(html, encoding="utf-8")
    print(f"[+] {len(entries)}개 로그 주입 완료")


def git_push(day_num: int):
    os.chdir(REPO_DIR)
    cmds = [
        ["git", "add", "index.html"],
        ["git", "commit", "-m", f"log: Day {day_num} - {date.today()}"],
        ["git", "push"],
    ]
    for cmd in cmds:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[!] {' '.join(cmd)} 실패:\n{result.stderr}")
            return False
        print(f"[+] {' '.join(cmd)}")
    return True


def main():
    log_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_LOG

    if not log_path.exists():
        print(f"[!] 로그 파일 없음: {log_path}")
        print(f"    경로를 직접 지정: python3 deploy.py /path/to/daily_log.md")
        sys.exit(1)

    print(f"[*] 로그 파싱: {log_path}")
    entries = parse_log(log_path)

    if not entries:
        print("[!] 파싱된 로그 없음. daily_log.md 형식 확인 필요")
        sys.exit(1)

    print(f"[*] {len(entries)}개 Day 발견: {[e['day'] for e in entries]}")
    inject_logs(entries)

    latest_day = entries[0]["day"]
    success = git_push(latest_day)
    if success:
        print(f"\n✓ https://dayeonYou.github.io 배포 완료!")
    else:
        print("\n[!] push 실패. git 설정 확인 필요")


if __name__ == "__main__":
    main()
