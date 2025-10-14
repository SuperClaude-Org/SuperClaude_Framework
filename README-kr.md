<div align="center">

# 🚀 SuperClaude 프레임워크

### **Claude Code를 구조화된 개발 플랫폼으로 변환**

<p align="center">
  <img src="https://img.shields.io/badge/version-4.1.5-blue" alt="Version">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome">
</p>

<p align="center">
  <a href="https://superclaude.netlify.app/">
    <img src="https://img.shields.io/badge/🌐_웹사이트_방문-blue" alt="Website">
  </a>
  <a href="https://pypi.org/project/superclaude/">
    <img src="https://img.shields.io/pypi/v/SuperClaude.svg?" alt="PyPI">
  </a>
  <a href="https://www.npmjs.com/package/@bifrost_inc/superclaude">
    <img src="https://img.shields.io/npm/v/@bifrost_inc/superclaude.svg" alt="npm">
  </a>
</p>

<!-- Language Selector -->
<p align="center">
  <a href="README.md">
    <img src="https://img.shields.io/badge/🇺🇸_English-blue" alt="English">
  </a>
  <a href="README-zh.md">
    <img src="https://img.shields.io/badge/🇨🇳_中文-red" alt="中文">
  </a>
  <a href="README-ja.md">
    <img src="https://img.shields.io/badge/🇯🇵_日本語-green" alt="日本語">
  </a>
  <a href="README-kr.md">
    <img src="https://img.shields.io/badge/🇰🇷_한국어-orange" alt="한국어">
  </a>
</p>

<p align="center">
  <a href="#-빠른-설치">빠른 시작</a> •
  <a href="#-프로젝트-후원하기">후원</a> •
  <a href="#-v4의-새로운-기능">새로운 기능</a> •
  <a href="#-문서">문서</a> •
  <a href="#-기여하기">기여</a>
</p>

</div>

---

<div align="center">

## 📊 **프레임워크 통계**

| **명령어 수** | **에이전트** | **모드** | **MCP 서버** |
|:------------:|:----------:|:---------:|:---------------:|
| **21** | **14** | **5** | **6** |
| 슬래시 명령어 | 전문 AI | 작동 모드 | 통합 서비스 |

</div>

---

<div align="center">

## 🎯 **개요**

SuperClaude는 **메타프로그래밍 설정 프레임워크**로, 동작 지시 주입과 컴포넌트 통제를 통해 Claude Code를 구조화된 개발 플랫폼으로 변환합니다. 강력한 도구와 지능형 에이전트를 갖춘 체계적인 워크플로우 자동화를 제공합니다.

## ⚡ **빠른 설치**

### **설치 방법 선택**

| 방법 | 명령어 | 최적 사용처 |
|:------:|---------|----------|
| **🐍 pipx** | `pipx install SuperClaude && pipx upgrade SuperClaude && SuperClaude install` | **✅ 권장** - Linux/macOS |
| **📦 pip** | `pip install SuperClaude && pip upgrade SuperClaude && SuperClaude install` | 기존 Python 환경 |
| **🌐 npm** | `npm install -g @bifrost_inc/superclaude && superclaude install` | 크로스 플랫폼, Node.js 사용자 |

</div>

<details>
<summary><b>⚠️ 중요: SuperClaude V3에서 업그레이드</b></summary>

**SuperClaude V3가 설치되어 있다면 V4를 설치하기 전에 제거해야 합니다:**

```bash
# 먼저 V3 제거
관련된 모든 파일과 디렉토리 삭제:
*.md *.json 및 commands/

# 그런 다음 V4 설치
pipx install SuperClaude && pipx upgrade SuperClaude && SuperClaude install
```

**✅ 업그레이드 시 유지되는 내용:**
- ✓ 커스텀 슬래시 명령어 (`commands/sc/` 외부)
- ✓ `CLAUDE.md` 내의 커스텀 콘텐츠
- ✓ Claude Code의 `.claude.json`, `.credentials.json`, `settings.json`, `settings.local.json`
- ✓ 추가한 커스텀 에이전트 및 파일

**⚠️ 참고:** V3의 다른 SuperClaude 관련 `.json` 파일은 충돌을 일으킬 수 있으므로 삭제하세요.

</details>

<details>
<summary><b>💡 PEP 668 오류 해결방법</b></summary>

```bash
# 옵션 1: pipx 사용 (권장)
pipx install SuperClaude

# 옵션 2: 사용자 설치
pip install --user SuperClaude

# 옵션 3: 강제 설치 (주의해서 사용)
pip install --break-system-packages SuperClaude
```
</details>

---

<div align="center">

## 💖 **프로젝트 후원하기**

> 솔직히 말씀드리면, SuperClaude를 유지하는 데는 시간과 리소스가 필요합니다.
> 
> *테스트를 위한 Claude Max 구독료만 매월 100달러이고, 거기에 문서화, 버그 수정, 기능 개발에 쓰는 시간이 추가됩니다.*
> *일상 업무에서 SuperClaude의 가치를 느끼신다면, 프로젝트 후원을 고려해주세요.*
> *몇 달러라도 기본 비용을 충당하고 개발을 계속할 수 있게 해줍니다.*
> 
> 코드, 피드백, 또는 후원을 통해, 모든 기여자가 중요합니다. 이 커뮤니티의 일원이 되어주셔서 감사합니다! 🙏

<table>
<tr>
<td align="center" width="33%">
  
### ☕ **Ko-fi**
[![Ko-fi](https://img.shields.io/badge/Support_on-Ko--fi-ff5e5b?logo=ko-fi)](https://ko-fi.com/superclaude)

*일회성 기여*

</td>
<td align="center" width="33%">

### 🎯 **Patreon**
[![Patreon](https://img.shields.io/badge/Become_a-Patron-f96854?logo=patreon)](https://patreon.com/superclaude)

*월간 후원*

</td>
<td align="center" width="33%">

### 💜 **GitHub**
[![GitHub Sponsors](https://img.shields.io/badge/GitHub-Sponsor-30363D?logo=github-sponsors)](https://github.com/sponsors/SuperClaude-Org)

*유연한 티어*

</td>
</tr>
</table>

### **여러분의 후원으로 가능한 것들:**

| 항목 | 비용/영향 |
|------|-------------|
| 🔬 **Claude Max 테스트** | 검증과 테스트를 위해 월 100달러 |
| ⚡ **기능 개발** | 새로운 기능과 개선 사항 |
| 📚 **문서화** | 포괄적인 가이드와 예제 |
| 🤝 **커뮤니티 지원** | 신속한 이슈 대응과 도움 |
| 🔧 **MCP 통합** | 새로운 서버 연결 테스트 |
| 🌐 **인프라** | 호스팅 및 배포 비용 |

> **참고:** 하지만 부담은 없습니다. 프레임워크는 어쨌든 오픈소스로 유지됩니다. 사람들이 사용하고 가치를 느끼고 있다는 것만 알아도 동기부여가 됩니다. 코드, 문서, 또는 정보 확산을 통한 기여도 큰 도움이 됩니다! 🙏

</div>

---

<div align="center">

## 🎉 **V4의 새로운 기능**

> *버전 4는 커뮤니티 피드백과 실제 사용 패턴을 기반으로 중요한 개선 사항을 제공합니다.*

<table>
<tr>
<td width="50%">

### 🤖 **더 스마트한 에이전트 시스템**
**14개의 전문 에이전트**가 도메인 전문성을 제공:
- 보안 엔지니어가 실제 취약점 포착
- 프론트엔드 아키텍트가 UI 패턴 이해
- 컨텍스트 기반 자동 조정
- 필요 시 도메인별 전문 지식 제공

</td>
<td width="50%">

### 📝 **개선된 네임스페이스**
모든 명령어에 **`/sc:` 접두사**:
- 커스텀 명령어와 충돌 없음
- 전체 라이프사이클을 다루는 21개 명령어
- 브레인스토밍부터 배포까지
- 정리된 명령어 구조

</td>
</tr>
<tr>
<td width="50%">

### 🔧 **MCP 서버 통합**
**6개의 강력한 서버**가 함께 작동:
- **Context7** → 최신 문서
- **Sequential** → 복잡한 분석
- **Magic** → UI 컴포넌트 생성
- **Playwright** → 브라우저 테스트
- **Morphllm** → 대량 변환
- **Serena** → 세션 지속성

</td>
<td width="50%">

### 🎯 **작동 모드**
다양한 컨텍스트를 위한 **5가지 적응형 모드**:
- **브레인스토밍** → 적절한 질문하기
- **오케스트레이션** → 효율적인 도구 조정
- **토큰 효율성** → 30-50% 컨텍스트 절약
- **작업 관리** → 체계적인 구성
- **성찰** → 메타인지 분석

</td>
</tr>
<tr>
<td width="50%">

### ⚡ **최적화된 성능**
**더 작은 프레임워크, 더 큰 프로젝트:**
- 프레임워크 풋프린트 감소
- 코드를 위한 더 많은 컨텍스트
- 더 긴 대화 가능
- 복잡한 작업 활성화

</td>
<td width="50%">

### 📚 **문서 전면 개편**
**개발자를 위한 완전한 재작성:**
- 실제 예제와 사용 사례
- 일반적인 함정 문서화
- 실용적인 워크플로우 포함
- 개선된 탐색 구조

</td>
</tr>
</table>

</div>

---

<div align="center">

## 📚 **문서**

### **🇰🇷 SuperClaude 완전 한국어 가이드**

<table>
<tr>
<th align="center">🚀 시작하기</th>
<th align="center">📖 사용자 가이드</th>
<th align="center">🛠️ 개발자 리소스</th>
<th align="center">📋 레퍼런스</th>
</tr>
<tr>
<td valign="top">

- 📝 [**빠른 시작 가이드**](docs/getting-started/quick-start.md)  
  *즉시 시작하기*

- 💾 [**설치 가이드**](docs/getting-started/installation.md)  
  *상세한 설정 단계*

</td>
<td valign="top">

- 🎯 [**명령어 레퍼런스**](docs/user-guide/commands.md)  
  *전체 21개 슬래시 명령어*

- 🤖 [**에이전트 가이드**](docs/user-guide/agents.md)  
  *14개 전문 에이전트*

- 🎨 [**작동 모드**](docs/user-guide/modes.md)  
  *5가지 적응형 모드*

- 🚩 [**플래그 가이드**](docs/user-guide/flags.md)  
  *동작 제어 매개변수*

- 🔧 [**MCP 서버**](docs/user-guide/mcp-servers.md)  
  *6개 서버 통합*

- 💼 [**세션 관리**](docs/user-guide/session-management.md)  
  *상태 저장 및 복원*

</td>
<td valign="top">

- 🏗️ [**기술 아키텍처**](docs/developer-guide/technical-architecture.md)  
  *시스템 설계 세부사항*

- 💻 [**코드 기여**](docs/developer-guide/contributing-code.md)  
  *개발 워크플로우*

- 🧪 [**테스트 및 디버깅**](docs/developer-guide/testing-debugging.md)  
  *품질 보증*

</td>
<td valign="top">

- ✨ [**모범 사례**](docs/reference/quick-start-practices.md)  
  *전문가 팁과 패턴*

- 📓 [**예제 모음**](docs/reference/examples-cookbook.md)  
  *실제 사용 예제*

- 🔍 [**문제 해결**](docs/reference/troubleshooting.md)  
  *일반적인 문제와 수정*

</td>
</tr>
</table>

</div>

---

<div align="center">

## 🤝 **기여하기**

### **SuperClaude 커뮤니티에 참여하세요**

모든 종류의 기여를 환영합니다! 도움을 줄 수 있는 방법:

| 우선순위 | 영역 | 설명 |
|:--------:|------|-------------|
| 📝 **높음** | 문서 | 가이드 개선, 예제 추가, 오타 수정 |
| 🔧 **높음** | MCP 통합 | 서버 설정 추가, 통합 테스트 |
| 🎯 **중간** | 워크플로우 | 명령어 패턴과 레시피 작성 |
| 🧪 **중간** | 테스트 | 테스트 추가, 기능 검증 |
| 🌐 **낮음** | 국제화 | 문서를 다른 언어로 번역 |

<p align="center">
  <a href="CONTRIBUTING.md">
    <img src="https://img.shields.io/badge/📖_읽기-기여_가이드-blue" alt="Contributing Guide">
  </a>
  <a href="https://github.com/SuperClaude-Org/SuperClaude_Framework/graphs/contributors">
    <img src="https://img.shields.io/badge/👥_보기-모든_기여자-green" alt="Contributors">
  </a>
</p>

</div>

---

<div align="center">

## ⚖️ **라이선스**

이 프로젝트는 **MIT 라이선스** 하에 라이선스가 부여됩니다 - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg?" alt="MIT License">
</p>

</div>

---

<div align="center">

## ⭐ **Star 히스토리**

<a href="https://www.star-history.com/#SuperClaude-Org/SuperClaude_Framework&Timeline">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=SuperClaude-Org/SuperClaude_Framework&type=Timeline&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=SuperClaude-Org/SuperClaude_Framework&type=Timeline" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=SuperClaude-Org/SuperClaude_Framework&type=Timeline" />
 </picture>
</a>

</div>

---

<div align="center">

### **🚀 SuperClaude 커뮤니티가 열정으로 구축**

<p align="center">
  <sub>한계를 뛰어넘는 개발자들을 위해 ❤️로 제작되었습니다</sub>
</p>

<p align="center">
  <a href="#-superclaude-프레임워크">맨 위로 ↑</a>
</p>

</div>

