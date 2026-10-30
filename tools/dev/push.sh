#!/bin/bash
# 사용: push.sh "메시지" 파일1 파일2 ...  (index.html, sw.js는 항상 포함)
cd "$(dirname "$0")/../.." || exit 1
msg="$1"; shift
git add index.html sw.js "$@" && git -c user.name=Claude -c user.email=noreply@anthropic.com commit -q -m "$msg

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_016h8XMGrWrPcmD8aYjNwtqy" && git push -q origin main 2>&1 | tail -1
git status -sb | head -3
