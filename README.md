<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github.com/griptape-ai/griptape-nodes-engine/raw/main/docs/assets/img/griptape_nodes_from_foundry_white.svg">
  <img alt="Griptape Nodes" src="https://github.com/griptape-ai/griptape-nodes-engine/raw/main/docs/assets/img/griptape_nodes_from_foundry_black.svg" width="600">
</picture>


Griptape Nodes의 한국어 가이드 문서입니다.

Griptape Nodes는 전문 아티스트와 크리에이터를 위해 설계된 강력한 시각적 노드 기반 워크플로 빌더입니다. 직관적인 드래그 앤 드롭 인터페이스인 클라우드 기반 [Griptape Nodes IDE](https://app.nodes.griptape.ai/?utm_source=gemini)를 통해 복잡한 AI 워크플로를 구축하고 실행하세요.

이 저장소에는 로컬 머신에서 안전하게 실행되며 워크플로 실행을 위한 고성능 기반을 제공하는 로컬 구성 요소인 Griptape Nodes Engine이 포함되어 있습니다. 이 엔진은 PyPI에 `griptape-nodes-engine` 라이브러리로 게시되어 있으며 `griptape-nodes` 애플리케이션에 의해 실행됩니다. 로컬 체크아웃을 통해 엔진을 개발하려면 [CONTRIBUTING.md](https://www.google.com/search?q=CONTRIBUTING.md&utm_source=gemini)를 참조하세요.

[![Griptape Nodes 예시 영상](https://github.com/griptape-ai/griptape-nodes-engine/raw/main/docs/assets/img/video-thumbnail.jpg)](https://www.google.com/search?q=%5Bhttps%3A%2F%2Fvimeo.com%2F1064451891%5D%28https%3A%2F%2Fvimeo.com%2F1064451891%29)
*(이미지를 클릭하면 Vimeo에서 영상을 시청할 수 있습니다)*

**✨ 주요 기능:**

* **🎯 시각적 워크플로 에디터:** 클라우드 기반 IDE를 통해 다양한 AI 작업, 도구 및 로직을 나타내는 노드를 설계하고 연결
* **🏠 로컬 엔진:** 자체 머신이나 인프라에서 워크플로를 안전하게 실행
* **🐍 이식 가능한 Python 워크플로:** 이식성, 디버깅 용이성 및 학습을 위해 워크플로가 자체 실행 가능한 Python 파일로 저장됨
* **🌐 다중 디바이스 액세스:** 클라이언트/서버 아키텍처를 통해 모든 디바이스에서 워크플로에 액세스 가능
* **🧩 확장성:** 자체 사용자 지정 노드 및 라이브러리를 구축하여 기능 확장
* **⚡ 스크립트 기능 인터페이스:** 프로그래밍 방식으로 플로우와 상호작용하고 제어

**🔗 자세히 보기:**

* **📚 전체 문서:** [docs.griptapenodes.com](https://docs.griptapenodes.com?utm_source=gemini)
* **⚙️ 설치:** [docs.griptapenodes.com/en/stable/installation/](https://docs.griptapenodes.com/en/latest/installation/?utm_source=gemini)
* **🔧 엔진 구성:** [docs.griptapenodes.com/en/stable/configuration/](https://docs.griptapenodes.com/en/latest/configuration/?utm_source=gemini)
* **📋 마이그레이션 가이드:** [MIGRATION.md](https://www.google.com/search?q=MIGRATION.md&utm_source=gemini) - 더 이상 사용되지 않는(deprecated) 노드로부터의 마이그레이션 가이드

**🧩 Griptape Nodes 확장하기:**

특정 워크플로 니즈에 맞는 사용자 지정 노드를 만들고 싶으신가요? Griptape Nodes는 사용자 지정 라이브러리를 통해 확장할 수 있도록 설계되었습니다:

* **📦 사용자 지정 라이브러리 템플릿:** [Griptape Nodes Library Template](https://github.com/griptape-ai/griptape-nodes-library-template?utm_source=gemini)을 사용하여 시작하기
* **🛠️ 사용자 지정 노드 구축:** 예술 및 창작 워크플로에 맞춘 전용 노드 생성

---

## 🚀 빠른 설치

### 옵션 1: Griptape Nodes Desktop (권장)

엔진과 에디터가 모두 포함된 번들 앱인 [Griptape Nodes Desktop](https://www.griptapenodes.com/griptape-nodes-desktop?utm_source=gemini)을 다운로드하세요. 추가 설정이 필요하지 않습니다.

### 옵션 2: 수동 엔진 설치

엔진을 직접 설치하는 것을 선호하는 사용자의 경우:

1. **🔐 로그인:** [Griptape Nodes](https://app.nodes.griptape.ai/?utm_source=gemini)를 방문하여 Griptape Cloud 자격 증명을 사용해 로그인하거나 가입하세요.
2. **💾 엔진 설치:** [uv](https://docs.astral.sh/uv/?utm_source=gemini)를 사용하여 엔진을 설치합니다:
```bash
uv tool install griptape-nodes

```


3. **⚙️ 초기 구성 (첫 실행 시 자동 진행):**
* 엔진 명령(`griptape-nodes` 또는 `gtn`)을 처음 실행하면 초기 설정을 안내합니다.
* **📁 워크스페이스 디렉터리:** Griptape Nodes가 구성, 프로젝트 파일, 시크릿(`.env`) 및 생성된 자산을 저장할 디렉터리를 선택하라는 메시지가 표시됩니다. 기본값(`<현재_디렉터리>/GriptapeNodes`)을 수락하거나 사용자 지정 경로를 지정할 수 있습니다.
* **🔑 Griptape Cloud API 키:** 브라우저에서 [Griptape Nodes 설정 페이지](https://app.nodes.griptape.ai/?utm_source=gemini)로 돌아가 "Generate API Key"를 클릭하고 키를 복사한 다음 터미널에 프롬프트가 표시될 때 붙여넣습니다.


4. **🚀 엔진 시작:** 구성 후 다음을 실행하여 엔진을 시작합니다:
```bash
griptape-nodes

```


*(또나 더 짧은 별칭인 `gtn` 사용)*
5. **🔗 워크플로 에디터 연결:** 브라우저에서 Griptape Nodes Workflow Editor 페이지를 새로 고칩니다. 이제 실행 중인 엔진에 연결되어야 합니다.

이제 플로우를 구축할 준비가 되었습니다! 🎉 더 자세한 설정 옵션 및 문제 해결은 전체 [문서](https://docs.griptapenodes.com/?utm_source=gemini)를 참조하세요.

---

## 🔄 공식 영문 문서 자동 동기화 & 한글 번역 도구

Upstream 공식 문서([griptape-nodes-engine](https://github.com/griptape-ai/griptape-nodes-engine))의 최신 변경사항을 감지하여 자동으로 번역하고, 메뉴 등록 및 Git Push까지 한 번에 수행할 수 있습니다.

### 1. 환경 설정
`.env` 파일에 발급받은 Gemini API Key를 설정합니다:
```env
GEMINI_API_KEY=AIzaSy...
GEMINI_MODEL=gemini-3.7-flash
AUTO_PUSH=false
```

### 2. 실행 명령어

* **변경사항 미리보기 (Dry-run):**
  ```bash
  python sync_docs.py --dry-run
  ```

* **🖼️ 이미지 및 에셋 파일만 동기화 (API 토큰 미사용, 초고속):**
  ```bash
  python sync_docs.py --assets-only
  ```

* **📄 마크다운 문서만 번역 및 메뉴 등록:**
  ```bash
  python sync_docs.py --docs-only
  ```

* **전체 동기화 (문서 번역 + 에셋 다운로드):**
  ```bash
  python sync_docs.py
  ```

* **동기화 후 GitHub에 자동 커밋 & 푸시:**
  ```bash
  python sync_docs.py --docs-only --push
  ```

* **특정 단일 파일만 다시 번역하기:**
  ```bash
  python sync_docs.py --file docs/index.md
  ```

