#!/usr/bin/env python3
"""
Griptape Nodes Docs Synchronizer & Auto-Translator

이 스크립트는 Upstream(griptape-ai/griptape-nodes-engine)의 최신 문서와
로컬 한국어 문서를 비교하여 신규/수정 문서를 감지하고,
Gemini API를 활용해 번역 및 mkdocs.yml 메뉴 갱신, Git Push까지 자동 수행합니다.
"""

import os
import sys
import json
import time
import argparse
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import requests
from dotenv import load_dotenv
from ruamel.yaml import YAML

# .env 로드
load_dotenv()

# 환경 변수 기본값 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.7-flash")
UPSTREAM_REPO = os.getenv("UPSTREAM_REPO", "griptape-ai/griptape-nodes-engine")
UPSTREAM_BRANCH = os.getenv("UPSTREAM_BRANCH", "main")
AUTO_PUSH = os.getenv("AUTO_PUSH", "false").lower() in ("true", "1", "yes")
SSL_VERIFY = os.getenv("SSL_VERIFY", "true").lower() not in ("false", "0", "no")

STATE_FILE = Path(".sync_state.json")
MKDOCS_FILE = Path("mkdocs.yml")
DOCS_DIR = Path("docs")

TRANSLATION_SYSTEM_PROMPT = """당신은 인공지능(AI) 및 기술 문서 전문 번역가입니다.
제공된 영어 마크다운 문서를 자연스럽고 가독성 높은 기술 한국어로 번역하세요.

[번역 가이드라인]
1. 어조: 정중하고 명확한 기술 문서 톤(~합니다, ~입니다, ~하세요)을 유지하세요.
2. 마크다운 서식 유지:
   - 마크다운 문법(제목 `#`, 목록 `-`, 표 `|`, 굵게 `**`, 기울임 `*` 등)을 완벽히 유지하세요.
   - Frontmatter(`---`로 감싸진 영역)는 구조를 유지하고 값만 필요시 번역하세요.
   - 코드 블록(```...```) 및 인라인 코드(`...`) 내부의 소스코드, 명령어, 변수명, 파일명 등은 절대 번역하지 마세요. (코드 주석은 번역 가능)
   - 링크 URL, 이미지 경로, 앵커 링크(`(#...)`)는 절대 수정하지 마세요.
   - Admonition 블록(`!!! note`, `???+ tip` 등)의 형식은 유지하되, 제목 텍스트(`"..."`)는 한국어로 번역하세요.
   - HTML 태그(`<picture>`, `<img>`, `<div>` 등)와 속성은 원본 그대로 유지하세요.
3. 용어 통일:
   - Node(노드), Workflow(워크플로), Pipeline(파이프라인), Prompt(프롬프트), Latent(레이턴트),
     Model(모델), Parameter(파라미터), Widget(위젯), Canvas(캔버스), Engine(엔진) 등 기술 용어는 널리 쓰이는 표기법을 준수하세요.
4. 출력 형식:
   - 부가 설명이나 인사말 없이 오직 번역된 마크다운 문서 내용만을 출력하세요.
"""

NAV_TRANSLATION_PROMPT = """다음 영문 문서 제목/메뉴명을 공식 한글 가이드에 어울리는 간결하고 직관적인 메뉴명으로 번역하세요.
부연 설명 없이 오직 번역된 메뉴명 단어만 1줄로 출력하세요.
예시:
"Getting Started" -> "시작하기"
"Workflow Versions" -> "워크플로 버전 관리"
"Advanced Media" -> "고급 미디어"
"Node Groups" -> "노드 그룹"

번역할 영문 제목: """


import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Session 생성
session = requests.Session()
session.verify = SSL_VERIFY


class GeminiTranslator:
    """Gemini API를 이용한 번역 엔진"""

    def __init__(self, api_key: str, model: str = GEMINI_MODEL):
        self.api_key = api_key.strip()
        self.model = model
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

    def translate_markdown(self, markdown_text: str, max_retries: int = 3) -> str:
        """마크다운 본문 번역"""
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다. .env 파일에 키를 입력하세요.")

        if not markdown_text.strip():
            return markdown_text

        payload = {
            "system_instruction": {
                "parts": [{"text": TRANSLATION_SYSTEM_PROMPT}]
            },
            "contents": [
                {
                    "parts": [{"text": f"다음 문서를 한국어로 번역해주세요:\n\n{markdown_text}"}]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 8192
            }
        }

        for attempt in range(1, max_retries + 1):
            try:
                response = session.post(self.api_url, json=payload, timeout=90)
                if response.status_code == 200:
                    data = response.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts and "text" in parts[0]:
                            translated = parts[0]["text"].strip()
                            # 만약 앞뒤에 ```markdown ... ``` 이 붙어있다면 제거
                            if translated.startswith("```markdown") and translated.endswith("```"):
                                translated = translated[len("```markdown"): -3].strip()
                            elif translated.startswith("```") and translated.endswith("```"):
                                translated = translated[3:-3].strip()
                            return translated
                    raise ValueError(f"예상치 못한 응답 형식: {data}")
                elif response.status_code == 429:
                    # Rate limit 백오프
                    wait_time = attempt * 5
                    print(f"  ⏳ [Rate Limit] {wait_time}초 대기 후 재시도... (시도 {attempt}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    raise RuntimeError(f"Gemini API 오류 (HTTP {response.status_code}): {response.text}")
            except Exception as e:
                if attempt == max_retries:
                    raise e
                time.sleep(attempt * 3)

        return markdown_text

    def translate_nav_title(self, title: str) -> str:
        """메뉴 제목 번역"""
        if not self.api_key or not title.strip():
            return title

        payload = {
            "contents": [
                {
                    "parts": [{"text": NAV_TRANSLATION_PROMPT + title}]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 60
            }
        }

        try:
            response = session.post(self.api_url, json=payload, timeout=20)
            if response.status_code == 200:
                data = response.json()
                parts = data["candidates"][0]["content"]["parts"]
                res = parts[0]["text"].strip().strip('"').strip("'")
                return res
        except Exception as e:
            print(f"  ⚠️ 메뉴명 번역 실패 ('{title}'): {e}")

        return title


class SyncEngine:
    """문서 동기화 및 관리 엔진"""

    def __init__(self, translator: Optional[GeminiTranslator] = None, dry_run: bool = False):
        self.translator = translator
        self.dry_run = dry_run
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.state = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        """로컬 동기화 상태 로드"""
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"last_sync": None, "files": {}}

    def _save_state(self):
        """로컬 동기화 상태 저장"""
        if not self.dry_run:
            self.state["last_sync"] = datetime.now(timezone.utc).isoformat()
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)

    def _request_get(self, url: str, **kwargs) -> requests.Response:
        """SSL fallback을 포함한 GET 요청 래퍼"""
        try:
            return session.get(url, **kwargs)
        except requests.exceptions.SSLError:
            return requests.get(url, verify=False, **kwargs)

    def fetch_upstream_tree(self) -> List[Dict[str, Any]]:
        """Upstream GitHub 저장소의 전체 파일 트리 조회"""
        url = f"https://api.github.com/repos/{UPSTREAM_REPO}/git/trees/{UPSTREAM_BRANCH}?recursive=1"
        headers = {"User-Agent": "gtn-doc-sync-tool"}
        resp = self._request_get(url, headers=headers, timeout=30)
        if resp.status_code != 200:
            raise RuntimeError(f"Upstream 트리 조회 실패 ({resp.status_code}): {resp.text}")
        return resp.json().get("tree", [])

    def fetch_raw_content(self, path: str) -> bytes:
        """Upstream 파일 원본 바이너리/텍스트 다운로드"""
        url = f"https://raw.githubusercontent.com/{UPSTREAM_REPO}/{UPSTREAM_BRANCH}/{path}"
        resp = self._request_get(url, timeout=30)
        if resp.status_code != 200:
            raise RuntimeError(f"파일 다운로드 실패 ({path}): HTTP {resp.status_code}")
        return resp.content

    def initialize_state(self):
        """현재 로컬 파일 상태를 기반으로 .sync_state.json 초기화"""
        print("🔍 현재 Upstream 트리와 로컬 파일 비교하여 상태 초기화 중...")
        tree = self.fetch_upstream_tree()
        files_state = {}
        for item in tree:
            path = item["path"]
            if (path.startswith("docs/") or path == "mkdocs.yml") and item["type"] == "blob":
                local_path = Path(path)
                if local_path.exists():
                    files_state[path] = item["sha"]

        self.state["files"] = files_state
        self._save_state()
        print(f"✅ 초기화 완료: {len(files_state)}개 파일의 동기화 상태가 기록되었습니다.")

    def sync_files(self, docs_only: bool = False, assets_only: bool = False) -> Tuple[List[str], List[str], List[str]]:
        """신규 및 수정 파일 감지 및 동기화/번역 수행"""
        tree = self.fetch_upstream_tree()
        known_files = self.state.get("files", {})

        new_files = []
        modified_files = []
        synced_assets = []
        translated_docs = []

        upstream_docs_items = [
            item for item in tree
            if item["path"].startswith("docs/") and item["type"] == "blob"
        ]

        # 모드 안내
        if docs_only:
            print("📄 [모드] 마크다운 문서(.md)만 동기화 및 번역합니다.")
        elif assets_only:
            print("🖼️  [모드] 이미지 및 에셋 파일만 다운로드합니다. (Gemini API 호출 없음)")

        print(f"📂 Upstream 문서 파일 총 {len(upstream_docs_items)}개 분석 중...")

        for item in upstream_docs_items:
            path = item["path"]
            sha = item["sha"]
            local_path = Path(path)
            ext = local_path.suffix.lower()
            is_md = (ext == ".md")

            # 필터링 조건
            if docs_only and not is_md:
                continue
            if assets_only and is_md:
                continue

            is_new = not local_path.exists()
            is_modified = (path in known_files and known_files[path] != sha)

            if is_new or is_modified:
                if is_new:
                    new_files.append(path)
                else:
                    modified_files.append(path)

                if is_md:
                    # 마크다운 문서 번역 대상
                    status_label = "[신규 문서]" if is_new else "[수정 문서]"
                    print(f"  📝 {status_label} 번역 처리 중: {path}")

                    raw_bytes = self.fetch_raw_content(path)
                    raw_text = raw_bytes.decode("utf-8", errors="replace")

                    if not self.dry_run:
                        if self.translator:
                            translated_text = self.translator.translate_markdown(raw_text)
                        else:
                            translated_text = raw_text

                        local_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(local_path, "w", encoding="utf-8") as f:
                            f.write(translated_text)

                        self.state["files"][path] = sha
                        translated_docs.append(path)
                else:
                    # 이미지, 코드, 에셋 등 바이너리/비-md 파일
                    status_label = "[신규 에셋]" if is_new else "[수정 에셋]"
                    print(f"  📦 {status_label} 다운로드 중: {path}")

                    if not self.dry_run:
                        content = self.fetch_raw_content(path)
                        local_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(local_path, "wb") as f:
                            f.write(content)

                        self.state["files"][path] = sha
                        synced_assets.append(path)

        self._save_state()
        return new_files, modified_files, translated_docs

    def sync_mkdocs_nav(self) -> int:
        """Upstream mkdocs.yml과 로컬 mkdocs.yml의 nav 구조 비교 및 자동 등록"""
        print("\n📑 mkdocs.yml 메뉴(nav) 동기화 검사 중...")
        try:
            upstream_raw = self.fetch_raw_content("mkdocs.yml").decode("utf-8")
        except Exception as e:
            print(f"  ⚠️ Upstream mkdocs.yml 다운로드 실패: {e}")
            return 0

        if not MKDOCS_FILE.exists():
            print("  ⚠️ 로컬 mkdocs.yml이 존재하지 않습니다.")
            return 0

        # 로컬 mkdocs.yml 로드
        with open(MKDOCS_FILE, "r", encoding="utf-8") as f:
            local_config = self.yaml.load(f)

        upstream_config = self.yaml.load(upstream_raw)

        local_nav = local_config.get("nav", [])
        upstream_nav = upstream_config.get("nav", [])

        # 모든 경로 수집
        def extract_paths(nav_item, result_set):
            if isinstance(nav_item, dict):
                for k, v in nav_item.items():
                    extract_paths(v, result_set)
            elif isinstance(nav_item, list):
                for elem in nav_item:
                    extract_paths(elem, result_set)
            elif isinstance(nav_item, str):
                result_set.add(nav_item.replace("\\", "/"))

        local_paths = set()
        extract_paths(local_nav, local_paths)

        added_count = 0

        # 신규 항목 탐색 및 로컬 nav에 추가
        def check_and_merge_nav(u_nav, l_nav):
            nonlocal added_count
            if not isinstance(u_nav, list) or not isinstance(l_nav, list):
                return

            for u_item in u_nav:
                if isinstance(u_item, dict):
                    for u_title, u_val in u_item.items():
                        # 파일 경로인 경우
                        if isinstance(u_val, str):
                            path_str = u_val.replace("\\", "/")
                            if path_str not in local_paths:
                                # 로컬 nav에 추가 필요
                                print(f"  ➕ 새 메뉴 항목 발견: '{u_title}' -> '{path_str}'")
                                ko_title = u_title
                                if self.translator:
                                    ko_title = self.translator.translate_nav_title(u_title)
                                    print(f"     ↳ 한글 메뉴명: '{ko_title}'")
                                l_nav.append({ko_title: path_str})
                                local_paths.add(path_str)
                                added_count += 1
                        # 하위 목록인 경우
                        elif isinstance(u_val, list):
                            # 매칭되는 로컬 섹션 찾기 (대응되는 dict 검색)
                            matched_l_val = None
                            for l_item in l_nav:
                                if isinstance(l_item, dict):
                                    for l_title, l_sub in l_item.items():
                                        if isinstance(l_sub, list):
                                            # 이름 유사도나 경로 일치 확인
                                            matched_l_val = l_sub
                                            break
                            if matched_l_val is not None:
                                check_and_merge_nav(u_val, matched_l_val)

        check_and_merge_nav(upstream_nav, local_nav)

        if added_count > 0:
            if not self.dry_run:
                with open(MKDOCS_FILE, "w", encoding="utf-8") as f:
                    self.yaml.dump(local_config, f)
            print(f"✅ mkdocs.yml에 {added_count}개의 새로운 메뉴가 등록되었습니다.")
        else:
            print("✨ 모든 메뉴가 이미 최신 상태입니다.")

        return added_count


class GitPusher:
    """Git 자동 스테이징, 커밋 및 푸시 유틸리티"""

    @staticmethod
    def commit_and_push(branch: str = "main", custom_msg: Optional[str] = None) -> bool:
        """변경 사항 커밋 및 원격 저장소 푸시"""
        print("\n🚀 Git 변경 사항 확인 및 Push 준비...")

        # 변경 사항 확인
        status_res = subprocess.run(
            ["git", "status", "--porcelain", "docs", "mkdocs.yml", str(STATE_FILE)],
            capture_output=True,
            text=True
        )

        if not status_res.stdout.strip():
            print("✨ 커밋할 변경 사항이 없습니다.")
            return True

        print("📦 변경된 파일 목록:")
        for line in status_res.stdout.strip().split("\n"):
            print(f"  {line}")

        # Git add
        subprocess.run(["git", "add", "docs", "mkdocs.yml", str(STATE_FILE)], check=True)

        # Commit message
        if not custom_msg:
            date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            commit_msg = f"docs: upstream 문서 동기화 및 한글 번역 ({date_str})"
        else:
            commit_msg = custom_msg

        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        print(f"✅ 커밋 완료: {commit_msg}")

        # Git push
        print(f"📤 원격 저장소(origin) {branch} 브랜치로 푸시 중...")
        push_res = subprocess.run(["git", "push", "origin", branch], capture_output=True, text=True)
        if push_res.returncode == 0:
            print("🎉 Git Push가 성공적으로 완료되었습니다!")
            return True
        else:
            print(f"❌ Git Push 실패:\n{push_res.stderr}")
            return False


def main():
    parser = argparse.ArgumentParser(description="Griptape Nodes 공식 문서 동기화 및 자동 번역 도구")
    parser.add_argument("--dry-run", action="store_true", help="실제 파일 작성 및 번역을 수행하지 않고 변경 목록만 확인")
    parser.add_argument("--docs-only", action="store_true", help="마크다운(.md) 문서만 번역 및 동기화")
    parser.add_argument("--assets-only", action="store_true", help="이미지 및 에셋 파일만 다운로드 (Gemini API 미사용)")
    parser.add_argument("--push", action="store_true", help="작업 완료 후 자동으로 git commit & push 수행")
    parser.add_argument("--no-push", action="store_true", help="git push를 건너뜁니다.")
    parser.add_argument("--init", action="store_true", help="기존 파일들을 기준으로 .sync_state.json 상태 파일 초기화")
    parser.add_argument("--file", type=str, help="특정 단일 파일만 동기화/번역 (예: docs/index.md)")

    args = parser.parse_args()

    if args.docs_only and args.assets_only:
        print("❌ --docs-only 옵션과 --assets-only 옵션은 동시에 사용할 수 없습니다.")
        return

    print("=" * 60)
    print(" 🌟 Griptape Nodes Documentation Synchronizer")
    print(f" 🎯 Upstream: {UPSTREAM_REPO} ({UPSTREAM_BRANCH})")
    print(f" 🤖 Model: {GEMINI_MODEL}")
    if args.docs_only:
        print(" 🎯 모드: 문서 전용 (--docs-only)")
    elif args.assets_only:
        print(" 🎯 모드: 에셋 전용 (--assets-only)")
    else:
        print(" 🎯 모드: 전체 동기화 (문서 + 에셋)")
    print("=" * 60)

    # 번역기 인스턴스 생성
    translator = None
    if not args.assets_only:
        if GEMINI_API_KEY:
            translator = GeminiTranslator(api_key=GEMINI_API_KEY, model=GEMINI_MODEL)
        else:
            print("⚠️ [주의] GEMINI_API_KEY가 설정되지 않았습니다.")
            print("   마크다운 번역을 수행하려면 .env 파일에 GEMINI_API_KEY를 설정하세요.")
            print("   (키가 없으면 원본 파일 다운로드 및 에셋 동기화만 수행됩니다.)\n")

    sync_engine = SyncEngine(translator=translator, dry_run=args.dry_run)

    # 1. 초기화 모드
    if args.init:
        sync_engine.initialize_state()
        return

    # 2. 단일 파일 처리 모드
    if args.file:
        file_path = args.file.replace("\\", "/")
        print(f"🎯 단일 파일 처리: {file_path}")
        raw_bytes = sync_engine.fetch_raw_content(file_path)
        if file_path.endswith(".md") and translator:
            translated = translator.translate_markdown(raw_bytes.decode("utf-8", errors="replace"))
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(translated)
            print(f"✅ 번역 완료: {file_path}")
        else:
            with open(file_path, "wb") as f:
                f.write(raw_bytes)
            print(f"✅ 다운로드 완료: {file_path}")
        return

    # 3. 파일 동기화 실행
    new_files, modified_files, translated_docs = sync_engine.sync_files(
        docs_only=args.docs_only,
        assets_only=args.assets_only
    )

    # 4. mkdocs.yml nav 갱신 (에셋 전용 모드가 아닐 때만)
    nav_updated = 0
    if not args.assets_only:
        nav_updated = sync_engine.sync_mkdocs_nav()

    # 5. 요약 리포트
    print("\n" + "=" * 60)
    print(" 📊 동기화 요약 결과")
    print(f"  • 감지된 신규 파일: {len(new_files)}개")
    print(f"  • 감지된 수정 파일: {len(modified_files)}개")
    if not args.assets_only:
        print(f"  • 번역 완료 문서: {len(translated_docs)}개")
        print(f"  • 메뉴(nav) 추가: {nav_updated}개")
    print("=" * 60)

    # 6. Git Push 처리
    should_push = (args.push or AUTO_PUSH) and not args.no_push and not args.dry_run
    if should_push:
        GitPusher.commit_and_push()
    else:
        print("\n💡 Git Push를 실행하려면 '--push' 옵션을 사용하거나 .env에서 AUTO_PUSH=true로 설정하세요.")


if __name__ == "__main__":
    main()
