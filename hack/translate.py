#!/usr/bin/env python3
"""把 lowlighter/metrics 生成的 SVG 中的英文文本就地替换为中文。

放在 GitHub Actions workflow 末尾跑：metrics 跑完自己 commit 后，本步先
git pull --rebase 拿最新 SVG，再调本脚本对所有 ``metrics*.svg`` 做替换，
最后 commit 一次。

替换分两层：
1. ``PATTERNS``：先用正则把"数字 + 名词"模板（如 ``1886 Commits``）翻成
   中文，避免后续整词替换误伤局部子串；
2. ``FIXED``：再把固定标题（如 ``Activity`` / ``Community stats``）替换成
   中文。包成 ``>en<`` 形式只匹配 HTML/SVG 节点内容，避免改到属性。

新增上游 plugin 时按需扩展两张表即可。
"""
from __future__ import annotations

import glob
import re
import sys

PATTERNS: list[tuple[str, str]] = [
    # base header
    (r"Joined GitHub (\d+) years? ago", r"加入 GitHub 已 \1 年"),
    (r"Followed by (\d+) users?", r"被 \1 人关注"),
    (r"Following (\d+) users?", r"关注了 \1 人"),
    (r"Contributed to (\d+) repositories", r"贡献了 \1 个仓库"),
    # activity
    (r"(\d+) Commits\b", r"提交 \1 次"),
    (r"(\d+) Pull requests opened", r"发起 PR \1 次"),
    (r"(\d+) Pull requests reviewed", r"评审 PR \1 次"),
    (r"(\d+) Issues opened", r"发起 Issue \1 次"),
    (r"(\d+) issue comments", r"\1 条 Issue 评论"),
    # community
    (r"Member of (\d+) organizations?", r"属于 \1 个组织"),
    (r"Sponsoring (\d+) repositories", r"赞助 \1 个仓库"),
    (r"Starred (\d+) repositories", r"Star 了 \1 个仓库"),
    (r"Watching (\d+) repositories", r"Watch 了 \1 个仓库"),
    # repositories
    (r"(\d+) Repositories\b", r"\1 个仓库"),
    (r"Prefers ([\w\-.]+) license", r"常用 \1 协议"),
    (r"(\d+) Releases\b", r"\1 次 Release"),
    (r"(\d+) Packages\b", r"\1 个 Package"),
    (r"([\d.]+\s*[KMGT]?B) used", r"占用 \1"),
    (r"(\d+) Sponsors\b", r"\1 位赞助者"),
    (r"(\d+) Stargazers\b", r"\1 人 Star"),
    (r"(\d+) Forkers\b", r"\1 人 Fork"),
    (r"(\d+) Watchers\b", r"\1 人 Watch"),
    # languages
    (r"(\d+) Languages\b", r"\1 种语言"),
    # people
    (r"(\d+) followers?\b", r"关注者 \1"),
    (r"(\d+) followed\b", r"已关注 \1"),
    # isocalendar
    (r"Current streak (\d+) days?", r"当前连击 \1 天"),
    (r"Best streak (\d+) days?", r"最长连击 \1 天"),
    (r"Highest in a day at (\d+)", r"单日最高 \1 次"),
    (r"Average per day at ~?([\d.]+)", r"日均约 \1 次"),
    # footer
    (
        r"Last updated (.+?) with lowlighter/metrics@([\w.\-]+)",
        r"更新于 \1 · 由 lowlighter/metrics@\2 生成",
    ),
]

FIXED: dict[str, str] = {
    # section headers
    "Activity": "活动",
    "Community stats": "社区统计",
    "Most used languages": "常用语言",
    "Overall issues and pull requests status": "Issue 与 PR 概览",
    "From communities": "来自社区",
    "From self and collaborators": "本人与合作者",
    "Contributions calendar": "贡献日历",
    "Commits streaks": "连续提交",
    "Commits per day": "每日提交",
    "Recent coding habits": "近期编码习惯",
    "Unexpected error": "（上游错误）",
    "Notable contributions": "重要外部贡献",
    "Created by TMY": "TMY 创建的",
    "Issues": "Issues",
    "Pull requests": "Pull Requests",
    "On TMY&#x27;s repositories": "TMY 自己仓库中",
    "On TMY's repositories": "TMY 自己仓库中",
    # PR/issue 状态
    "open": "开放",
    "closed": "已关闭",
    "drafts": "草稿",
    "draft": "草稿",
    "merged": "已合并",
    "skipped": "已跳过",
    # footer
    "These metrics do not include all private contributions": "本卡未包含全部私有贡献",
}


def translate(text: str) -> str:
    for pat, rep in PATTERNS:
        text = re.sub(pat, rep, text)
    for en, zh in FIXED.items():
        text = re.sub(rf">\s*{re.escape(en)}\s*<", f">{zh}<", text)
    return text


def main() -> int:
    paths = sorted(glob.glob("metrics*.svg"))
    if not paths:
        print("no SVGs found in cwd", file=sys.stderr)
        return 0
    changed = 0
    for p in paths:
        with open(p, encoding="utf-8") as f:
            src = f.read()
        out = translate(src)
        if out != src:
            with open(p, "w", encoding="utf-8") as f:
                f.write(out)
            print(f"translated: {p}")
            changed += 1
        else:
            print(f"unchanged:  {p}")
    print(f"\n{changed}/{len(paths)} files translated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
