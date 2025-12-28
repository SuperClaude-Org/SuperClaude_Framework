<div align="center">

# 🚀 SuperClaude 프레임워크

### **Claude Code를 구조화된 개발 플랫폼으로 변환**

<p align="center">
  <img src="https://img.shields.io/badge/version-4.1.9-blue" alt="Version">
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

| **명령어** | **에이전트** | **모드** | **MCP 서버** |
|:------------:|:----------:|:---------:|:---------------:|
| **30** | **16** | **7** | **8** |
| 슬래시 명령어 | 전문 AI | 동작 모드 | 통합 서비스 |

브레인스토밍부터 배포까지 완전한 개발 라이프사이클을 다루는 30개의 슬래시 명령어.

</div>

---

<div align="center">

## 🎯 **개요**

SuperClaude는 **메타프로그래밍 설정 프레임워크**로, 동작 지시 주입과 컴포넌트 통제를 통해 Claude Code를 구조화된 개발 플랫폼으로 변환합니다. 강력한 도구와 지능형 에이전트를 갖춘 체계적인 워크플로우 자동화를 제공합니다.


## 면책 조항

이 프로젝트는 Anthropic과 관련이 없거나 승인받지 않았습니다.
Claude Code는 [Anthropic](https://www.anthropic.com/)에 의해 구축 및 유지 관리되는 제품입니다.

## 📖 **개발자 및 기여자를 위한 안내**

**SuperClaude 프레임워크 작업을 위한 필수 문서:**

| 문서 | 목적 | 언제 읽을까 |
|----------|---------|--------------|
| **[PLANNING.md](PLANNING.md)** | 아키텍처, 설계 원칙, 절대 규칙 | 세션 시작, 구현 전 |
| **[TASK.md](TASK.md)** | 현재 작업, 우선순위, 백로그 | 매일, 작업 시작 전 |
| **[KNOWLEDGE.md](KNOWLEDGE.md)** | 축적된 통찰력, 모범 사례, 문제 해결 | 문제 발생 시, 패턴 학습 시 |
| **[CONTRIBUTING.md](CONTRIBUTING.md)** | 기여 가이드라인, 워크플로우 | PR 제출 전 |

> **💡 전문가 팁**: Claude Code는 세션 시작 시 이러한 파일을 읽어 프로젝트 표준에 부합하는 일관되고 고품질의 개발을 보장합니다.

## ⚡ **빠른 설치**

> **중요**: 이전 문서에서 설명한 TypeScript 플러그인 시스템은
> 아직 사용할 수 없습니다(v5.0에서 계획). v4.x의 현재 설치
> 지침은 아래 단계를 따르세요.

### **현재 안정 버전 (v4.1.9)**

SuperClaude는 현재 슬래시 명령어를 사용합니다.

**옵션 1: pipx (권장)**
```bash
# PyPI에서 설치
pipx install superclaude

# 명령어 설치 (/research, /index-repo, /agent, /recommend 설치)
superclaude install

# 설치 확인
superclaude install --list
superclaude doctor
```

설치 후, 명령어를 사용하려면 Claude Code를 재시작하세요:
- `/sc:research` - 병렬 검색으로 심층 웹 연구
- `/sc:index-repo` - 컨텍스트 최적화를 위한 리포지토리 인덱싱
- `/sc:agent` - 전문 AI 에이전트
- `/sc:recommend` - 명령어 추천
- `/sc` - 사용 가능한 모든 SuperClaude 명령어 표시

**옵션 2: Git에서 직접 설치**
```bash
# 리포지토리 클론
git clone https://github.com/SuperClaude-Org/SuperClaude_Framework.git
cd SuperClaude_Framework

# 설치 스크립트 실행
./install.sh
```

### **v5.0에서 제공 예정 (개발 중)**

새로운 TypeScript 플러그인 시스템을 적극적으로 개발 중입니다(자세한 내용은 [#419](https://github.com/SuperClaude-Org/SuperClaude_Framework/issues/419) 참조). 릴리스 후 설치는 다음과 같이 단순화됩니다:

```bash
# 이 기능은 아직 사용할 수 없습니다
/plugin marketplace add SuperClaude-Org/superclaude-plugin-marketplace
/plugin install superclaude
```

**상태**: 개발 중. ETA는 설정되지 않았습니다.

### **향상된 성능 (선택적 MCP)**

**2-3배** 빠른 실행과 **30-50%** 적은 토큰을 위해 선택적으로 MCP 서버를 설치할 수 있습니다:

```bash
# 향상된 성능을 위한 선택적 MCP 서버 (airis-mcp-gateway 경유):
# - Serena: 코드 이해 (2-3배 빠름)
# - Sequential: 토큰 효율적 추론 (30-50% 적은 토큰)
# - Tavily: 심층 연구를 위한 웹 검색
# - Context7: 공식 문서 검색
# - Mindbase: 모든 대화에 걸친 의미론적 검색 (선택적 향상)

# 참고: 오류 학습은 내장 ReflexionMemory를 통해 사용 가능 (설치 불필요)
# Mindbase는 의미론적 검색 향상을 제공 ("recommended" 프로필 필요)
# MCP 서버 설치: https://github.com/agiletec-inc/airis-mcp-gateway
# 자세한 내용은 docs/mcp/mcp-integration-policy.md 참조
```

**성능 비교:**
- **MCP 없음**: 완전히 기능함, 표준 성능 ✅
- **MCP 사용**: 2-3배 빠름, 30-50% 적은 토큰 ⚡

</div>

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

## 🎉 **V4.1의 새로운 기능**

> *버전 4.1은 슬래시 명령어 아키텍처 안정화, 에이전트 기능 강화 및 문서 개선에 중점을 둡니다.*

<table>
<tr>
<td width="50%">

### 🤖 **더 스마트한 에이전트 시스템**
도메인 전문성을 가진 **16개의 전문 에이전트**:
- PM Agent는 체계적인 문서화를 통해 지속적인 학습 보장
- 자율적인 웹 연구를 위한 심층 연구 에이전트
- 보안 엔지니어가 실제 취약점 포착
- 프론트엔드 아키텍트가 UI 패턴 이해
- 컨텍스트 기반 자동 조정
- 필요 시 도메인별 전문 지식 제공

</td>
<td width="50%">

### ⚡ **최적화된 성능**
**더 작은 프레임워크, 더 큰 프로젝트:**
- 프레임워크 풋프린트 감소
- 코드를 위한 더 많은 컨텍스트
- 더 긴 대화 가능
- 복잡한 작업 활성화

</td>
</tr>
<tr>
<td width="50%">

### 🔧 **MCP 서버 통합**
**8개의 강력한 서버** (airis-mcp-gateway 경유):
- **Tavily** → 주요 웹 검색(심층 연구)
- **Serena** → 세션 지속성 및 메모리
- **Mindbase** → 세션 간 학습(제로 풋프린트)
- **Sequential** → 토큰 효율적 추론
- **Context7** → 공식 문서 검색
- **Playwright** → JavaScript 중심 콘텐츠 추출
- **Magic** → UI 컴포넌트 생성
- **Chrome DevTools** → 성능 분석

</td>
<td width="50%">

### 🎯 **동작 모드**
다양한 컨텍스트를 위한 **7가지 적응형 모드**:
- **브레인스토밍** → 적절한 질문하기
- **비즈니스 패널** → 다중 전문가 전략 분석
- **심층 연구** → 자율적인 웹 연구
- **오케스트레이션** → 효율적인 도구 조정
- **토큰 효율성** → 30-50% 컨텍스트 절약
- **작업 관리** → 체계적인 구성
- **성찰** → 메타인지 분석

</td>
</tr>
<tr>
<td width="50%">

### 📚 **문서 전면 개편**
**개발자를 위한 완전한 재작성:**
- 실제 예제와 사용 사례
- 일반적인 함정 문서화
- 실용적인 워크플로우 포함
- 개선된 탐색 구조

</td>
<td width="50%">

### 🧪 **안정성 강화**
**신뢰성에 중점:**
- 핵심 명령어 버그 수정
- 테스트 커버리지 개선
- 더 견고한 오류 처리
- CI/CD 파이프라인 개선

</td>
</tr>
</table>

</div>

---

<div align="center">

## 🔬 **심층 연구 기능**

### **DR 에이전트 아키텍처에 맞춘 자율적 웹 연구**

SuperClaude v4.2는 자율적이고 적응적이며 지능적인 웹 연구를 가능하게 하는 포괄적인 심층 연구 기능을 도입합니다.

<table>
<tr>
<td width="50%">

### 🎯 **적응형 계획**
**세 가지 지능형 전략:**
- **계획만**: 명확한 쿼리에 대한 직접 실행
- **의도 계획**: 모호한 요청에 대한 명확화
- **통합**: 협업 계획 개선(기본값)

</td>
<td width="50%">

### 🔄 **다중 홉 추론**
**최대 5회 반복 검색:**
- 엔터티 확장(논문 → 저자 → 작품)
- 개념 심화(주제 → 세부사항 → 예제)
- 시간적 진행(현재 → 과거)
- 인과 체인(효과 → 원인 → 예방)

</td>
</tr>
<tr>
<td width="50%">

### 📊 **품질 점수**
**신뢰도 기반 검증:**
- 출처 신뢰성 평가(0.0-1.0)
- 커버리지 완전성 추적
- 종합 일관성 평가
- 최소 임계값: 0.6, 목표: 0.8

</td>
<td width="50%">

### 🧠 **사례 기반 학습**
**세션 간 지능:**
- 패턴 인식 및 재사용
- 시간 경과에 따른 전략 최적화
- 성공적인 쿼리 공식 저장
- 성능 개선 추적

</td>
</tr>
</table>

### **연구 명령어 사용**

```bash
# 자동 깊이로 기본 연구
/research "2024년 최신 AI 개발"

# 제어된 연구 깊이(TypeScript의 옵션 통해)
/research "양자 컴퓨팅 혁신"  # depth: exhaustive

# 특정 전략 선택
/research "시장 분석"  # strategy: planning-only

# 도메인 필터링 연구(Tavily MCP 통합)
/research "React 패턴"  # domains: reactjs.org,github.com
```

### **연구 깊이 수준**

| 깊이 | 소스 | 홉 | 시간 | 최적 용도 |
|:-----:|:-------:|:----:|:----:|----------|
| **빠른** | 5-10 | 1 | ~2분 | 빠른 사실, 간단한 쿼리 |
| **표준** | 10-20 | 3 | ~5분 | 일반 연구(기본값) |
| **심층** | 20-40 | 4 | ~8분 | 종합 분석 |
| **철저한** | 40+ | 5 | ~10분 | 학술 수준 연구 |

### **통합 도구 오케스트레이션**

심층 연구 시스템은 여러 도구를 지능적으로 조정합니다:
- **Tavily MCP**: 주요 웹 검색 및 발견
- **Playwright MCP**: 복잡한 콘텐츠 추출
- **Sequential MCP**: 다단계 추론 및 종합
- **Serena MCP**: 메모리 및 학습 지속성
- **Context7 MCP**: 기술 문서 검색

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

- 🎯 [**슬래시 명령어**](docs/user-guide/commands.md)
  *완전한 `/sc` 명령어 목록*

- 🤖 [**에이전트 가이드**](docs/user-guide/agents.md)
  *16개 전문 에이전트*

- 🎨 [**동작 모드**](docs/user-guide/modes.md)
  *7가지 적응형 모드*

- 🚩 [**플래그 가이드**](docs/user-guide/flags.md)
  *동작 제어 매개변수*

- 🔧 [**MCP 서버**](docs/user-guide/mcp-servers.md)
  *8개 서버 통합*

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


---

## 📋 **전체 30개 명령어**

<details>
<summary><b>전체 명령어 목록 펼치기</b></summary>

### 🧠 계획 및 설계 (4)
- `/brainstorm` - 구조화된 브레인스토밍
- `/design` - 시스템 아키텍처
- `/estimate` - 시간/노력 추정
- `/spec-panel` - 사양 분석

### 💻 개발 (5)
- `/implement` - 코드 구현
- `/build` - 빌드 워크플로우
- `/improve` - 코드 개선
- `/cleanup` - 리팩토링
- `/explain` - 코드 설명

### 🧪 테스트 및 품질 (4)
- `/test` - 테스트 생성
- `/analyze` - 코드 분석
- `/troubleshoot` - 디버깅
- `/reflect` - 회고

### 📚 문서화 (2)
- `/document` - 문서 생성
- `/help` - 명령어 도움말

### 🔧 버전 관리 (1)
- `/git` - Git 작업

### 📊 프로젝트 관리 (3)
- `/pm` - 프로젝트 관리
- `/task` - 작업 추적
- `/workflow` - 워크플로우 자동화

### 🔍 연구 및 분석 (2)
- `/research` - 심층 웹 연구
- `/business-panel` - 비즈니스 분석

### 🎯 유틸리티 (9)
- `/agent` - AI 에이전트
- `/index-repo` - 리포지토리 인덱싱
- `/index` - 인덱스 별칭
- `/recommend` - 명령어 추천
- `/select-tool` - 도구 선택
- `/spawn` - 병렬 작업
- `/load` - 세션 로드
- `/save` - 세션 저장
- `/sc` - 모든 명령어 표시

[**📖 상세 명령어 참조 보기 →**](docs/reference/commands-list.md)

</details>
