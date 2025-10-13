# SuperClaude 명령어 가이드

SuperClaude는 Claude Code를 위한 25개의 명령어를 제공합니다: 워크플로우를 위한 `/sc:*` 명령어와 전문가를 위한 `@agent-*`.

## 명령어 유형

| 유형 | 사용 위치 | 형식 | 예제 |
|------|------------|--------|---------|
| **슬래시 명령어** | Claude Code | `/sc:[명령어]` | `/sc:implement "기능"` |
| **에이전트** | Claude Code | `@agent-[이름]` | `@agent-security "검토"` |
| **설치** | 터미널 | `SuperClaude [명령어]` | `SuperClaude install` |

## 빠른 테스트
```bash
# 터미널: 설치 확인
python3 -m SuperClaude --version
# Claude Code CLI 확인: claude --version

# Claude Code: 명령어 테스트
/sc:brainstorm "테스트 프로젝트"    # 발견 질문을 해야 함
/sc:analyze README.md              # 분석을 제공해야 함
```

**워크플로우**: `/sc:brainstorm "아이디어"` → `/sc:implement "기능"` → `/sc:test`

## 🎯 SuperClaude 명령어 이해하기

## SuperClaude 작동 방식

SuperClaude는 Claude Code가 읽어 전문화된 동작을 채택하는 행동 컨텍스트 파일을 제공합니다. `/sc:implement`를 입력하면 Claude Code는 `implement.md` 컨텍스트 파일을 읽고 행동 지침을 따릅니다.

**SuperClaude 명령어는 소프트웨어로 실행되지 않습니다** - 프레임워크의 전문 지침 파일을 읽어 Claude Code의 동작을 수정하는 컨텍스트 트리거입니다.

### 명령어 유형:
- **슬래시 명령어** (`/sc:*`): 워크플로우 패턴 및 행동 모드 트리거
- **에이전트 호출** (`@agent-*`): 특정 도메인 전문가를 수동으로 활성화
- **플래그** (`--think`, `--safe-mode`): 명령어 동작 및 깊이 수정

### 컨텍스트 메커니즘:
1. **사용자 입력**: `/sc:implement "인증 시스템"` 입력
2. **컨텍스트 로딩**: Claude Code가 `~/.claude/superclaude/Commands/implement.md` 읽음
3. **동작 채택**: Claude가 도메인 전문 지식, 도구 선택, 검증 패턴 적용
4. **향상된 출력**: 보안 고려사항 및 모범 사례를 갖춘 구조화된 구현

**핵심 포인트**: 이는 전통적인 소프트웨어 실행이 아닌 컨텍스트 관리를 통해 정교한 개발 워크플로우를 만듭니다.

### 설치 vs 사용 명령어

**🖥️ 터미널 명령어** (실제 CLI 소프트웨어):
- `SuperClaude install` - 프레임워크 컴포넌트 설치
- `SuperClaude update` - 기존 설치 업데이트
- `SuperClaude uninstall` - 프레임워크 설치 제거
- `python3 -m SuperClaude --version` - 설치 상태 확인

**💬 Claude Code 명령어** (컨텍스트 트리거):
- `/sc:brainstorm` - 요구사항 발견 컨텍스트 활성화
- `/sc:implement` - 기능 개발 컨텍스트 활성화
- `@agent-security` - 보안 전문가 컨텍스트 활성화
- 모든 명령어는 Claude Code 채팅 인터페이스 내에서만 작동

> **빠른 시작**: 핵심 워크플로우를 경험하려면 `/sc:brainstorm "프로젝트 아이디어"` → `/sc:implement "기능 이름"` → `/sc:test`를 시도해보세요.

## 🧪 설정 테스트

### 🖥️ 터미널 확인 (터미널/CMD에서 실행)
```bash
# SuperClaude 작동 확인 (주요 방법)
python3 -m SuperClaude --version
# 예상 출력: SuperClaude 4.1.5

# Claude Code CLI 버전 확인
claude --version

# 설치된 컴포넌트 확인
python3 -m SuperClaude install --list-components | grep mcp
# 예상 출력: 설치된 MCP 컴포넌트 표시
```

### 💬 Claude Code 테스트 (Claude Code 채팅에 입력)
```
# 기본 /sc: 명령어 테스트
/sc:brainstorm "테스트 프로젝트"
# 예상 동작: 대화형 요구사항 발견 시작

# 명령어 도움말 테스트
/sc:help
# 예상 동작: 사용 가능한 명령어 목록
```

**테스트가 실패하면**: [설치 가이드](../Getting-Started/installation.md) 또는 [문제 해결](#troubleshooting) 확인

### 📝 명령어 빠른 참조

| 명령어 유형 | 실행 위치 | 형식 | 목적 | 예제 |
|-------------|--------------|--------|---------|----------|
| **🖥️ 설치** | 터미널/CMD | `SuperClaude [명령어]` | 설정 및 유지보수 | `SuperClaude install` |
| **🔧 구성** | 터미널/CMD | `python3 -m SuperClaude [명령어]` | 고급 구성 | `python3 -m SuperClaude --version` |
| **💬 슬래시 명령어** | Claude Code | `/sc:[명령어]` | 워크플로우 자동화 | `/sc:implement "기능"` |
| **🤖 에이전트 호출** | Claude Code | `@agent-[이름]` | 수동 전문가 활성화 | `@agent-security "검토"` |
| **⚡ 향상된 플래그** | Claude Code | `/sc:[명령어] --플래그` | 동작 수정 | `/sc:analyze --think-hard` |

> **기억하세요**: 모든 `/sc:` 명령어와 `@agent-` 호출은 터미널이 아닌 Claude Code 채팅 내에서 작동합니다. 이들은 Claude Code가 SuperClaude 프레임워크에서 특정 컨텍스트 파일을 읽도록 트리거합니다.

## 목차

- [필수 명령어](#필수-명령어) - 여기서 시작하세요 (8개 핵심 명령어)
- [일반적인 워크플로우](#일반적인-워크플로우) - 작동하는 명령어 조합
- [전체 명령어 참조](#전체-명령어-참조) - 카테고리별로 정리된 25개 명령어
- [문제 해결](#문제-해결) - 일반적인 문제 및 해결책
- [명령어 인덱스](#명령어-인덱스) - 카테고리별로 명령어 찾기

---

## 필수 명령어

**즉각적인 생산성을 위한 핵심 워크플로우 명령어:**

### `/sc:brainstorm` - 프로젝트 발견
**목적**: 대화형 요구사항 발견 및 프로젝트 계획
**구문**: `/sc:brainstorm "아이디어"` `[--strategy systematic|creative]`

**사용 사례**:
- 새 프로젝트 계획: `/sc:brainstorm "전자상거래 플랫폼"`
- 기능 탐색: `/sc:brainstorm "사용자 인증 시스템"`
- 문제 해결: `/sc:brainstorm "느린 데이터베이스 쿼리"`

### `/sc:help` - 명령어 참조
**목적**: 사용 가능한 모든 `/sc` 명령어와 설명 목록 표시
**구문**: `/sc:help`

**사용 사례**:
- 사용 가능한 명령어 발견: `/sc:help`
- 명령어 이름 빠른 확인: `/sc:help`

### `/sc:research` - 심층 연구 명령어
**목적**: 적응형 계획 및 지능형 검색을 통한 포괄적인 웹 연구
**구문**: `/sc:research "[쿼리]"` `[--depth quick|standard|deep|exhaustive] [--strategy planning|intent|unified]`

**사용 사례**:
- 기술 연구: `/sc:research "최신 React 19 기능" --depth deep`
- 시장 분석: `/sc:research "2024년 AI 코딩 어시스턴트 현황" --strategy unified`
- 학술 조사: `/sc:research "양자 컴퓨팅 돌파구" --depth exhaustive`
- 최신 정보: `/sc:research "2024년 최신 AI 개발"`

**핵심 기능**:
- **6단계 워크플로우**: 이해 → 계획 → TodoWrite → 실행 → 추적 → 검증
- **적응형 깊이**: Quick(기본 검색), Standard(확장), Deep(포괄적), Exhaustive(최대 깊이)
- **계획 전략**: Planning(직접), Intent(먼저 명확화), Unified(협업)
- **병렬 실행**: 기본 병렬 검색 및 추출
- **증거 관리**: 관련성 점수가 있는 명확한 인용
- **출력 표준**: 보고서가 `claudedocs/research_[주제]_[타임스탬프].md`에 저장됨

### `/sc:implement` - 기능 개발
**목적**: 지능형 전문가 라우팅을 통한 풀스택 기능 구현
**구문**: `/sc:implement "기능 설명"` `[--type frontend|backend|fullstack] [--focus security|performance]`

**사용 사례**:
- 인증: `/sc:implement "JWT 로그인 시스템"`
- UI 컴포넌트: `/sc:implement "반응형 대시보드"`
- API: `/sc:implement "REST 사용자 엔드포인트"`
- 데이터베이스: `/sc:implement "관계를 가진 사용자 스키마"`

### `/sc:analyze` - 코드 평가
**목적**: 품질, 보안, 성능에 걸친 포괄적인 코드 분석
**구문**: `/sc:analyze [경로]` `[--focus quality|security|performance|architecture]`

**사용 사례**:
- 프로젝트 상태: `/sc:analyze .`
- 보안 감사: `/sc:analyze --focus security`
- 성능 검토: `/sc:analyze --focus performance`

### `/sc:business-panel` - 전략적 비즈니스 분석
**목적**: 9명의 저명한 사상가와 함께하는 다중 전문가 비즈니스 전략 분석
**구문**: `/sc:business-panel "내용"` `[--mode discussion|debate|socratic] [--experts "name1,name2"]`

**사용 사례**:
- 전략 평가: `/sc:business-panel "우리의 시장 진출 전략"`
- 경쟁 분석: `/sc:business-panel @competitor_analysis.pdf --mode debate`
- 혁신 평가: `/sc:business-panel "AI 제품 아이디어" --experts "christensen,drucker"`
- 전략적 학습: `/sc:business-panel "경쟁 전략" --mode socratic`

**전문가 패널**: Christensen, Porter, Drucker, Godin, Kim/Mauborgne, Collins, Taleb, Meadows, Doumont

### `/sc:spec-panel` - 전문가 사양 검토
**목적**: 저명한 사양 및 소프트웨어 엔지니어링 전문가를 사용한 다중 전문가 사양 검토 및 개선
**구문**: `/sc:spec-panel [내용|@파일]` `[--mode discussion|critique|socratic] [--focus requirements|architecture|testing|compliance]`

**사용 사례**:
- 사양 검토: `/sc:spec-panel @api_spec.yml --mode critique --focus requirements,architecture`
- 요구사항 워크숍: `/sc:spec-panel "사용자 스토리 내용" --mode discussion`
- 아키텍처 검증: `/sc:spec-panel @microservice.spec.yml --mode socratic --focus architecture`
- 규정 준수 검토: `/sc:spec-panel @security_requirements.yml --focus compliance`
- 반복적 개선: `/sc:spec-panel @complex_system.spec.yml --iterations 3`

**전문가 패널**: Wiegers, Adzic, Cockburn, Fowler, Nygard, Newman, Hohpe, Crispin, Gregory, Hightower

### `/sc:troubleshoot` - 문제 진단
**목적**: 근본 원인 분석을 통한 체계적인 문제 진단
**구문**: `/sc:troubleshoot "문제 설명"` `[--type build|runtime|performance]`

**사용 사례**:
- 런타임 오류: `/sc:troubleshoot "로그인 시 500 오류"`
- 빌드 실패: `/sc:troubleshoot --type build`
- 성능 문제: `/sc:troubleshoot "느린 페이지 로드"`

### `/sc:test` - 품질 보증
**목적**: 커버리지 분석을 통한 포괄적인 테스팅
**구문**: `/sc:test` `[--type unit|integration|e2e] [--coverage] [--fix]`

**사용 사례**:
- 전체 테스트 스위트: `/sc:test --coverage`
- 단위 테스팅: `/sc:test --type unit --watch`
- E2E 검증: `/sc:test --type e2e`

### `/sc:improve` - 코드 향상
**목적**: 체계적인 코드 개선 및 최적화 적용
**구문**: `/sc:improve [경로]` `[--type performance|quality|security] [--preview]`

**사용 사례**:
- 일반적인 개선: `/sc:improve src/`
- 성능 최적화: `/sc:improve --type performance`
- 보안 강화: `/sc:improve --type security`

### `/sc:document` - 문서 생성
**목적**: 코드 및 API에 대한 포괄적인 문서 생성
**구문**: `/sc:document [경로]` `[--type api|user-guide|technical] [--format markdown|html]`

**사용 사례**:
- API 문서: `/sc:document --type api`
- 사용자 가이드: `/sc:document --type user-guide`
- 기술 문서: `/sc:document --type technical`

### `/sc:workflow` - 구현 계획
**목적**: 요구사항에서 구조화된 구현 계획 생성
**구문**: `/sc:workflow "기능 설명"` `[--strategy agile|waterfall] [--format markdown]`

**사용 사례**:
- 기능 계획: `/sc:workflow "사용자 인증"`
- 스프린트 계획: `/sc:workflow --strategy agile`
- 아키텍처 계획: `/sc:workflow "마이크로서비스 마이그레이션"`

---

## 일반적인 워크플로우

**검증된 명령어 조합:**

### 새 프로젝트 설정
```bash
/sc:brainstorm "프로젝트 개념"      # 요구사항 정의
/sc:design "시스템 아키텍처"        # 기술 설계 생성
/sc:workflow "구현 계획"            # 개발 로드맵 생성
```

### 기능 개발
```bash
/sc:implement "기능 이름"           # 기능 구축
/sc:test --coverage                 # 테스트로 검증
/sc:document --type api             # 문서 생성
```

### 코드 품질 개선
```bash
/sc:analyze --focus quality         # 현재 상태 평가
/sc:improve --preview               # 개선 사항 미리보기
/sc:test --coverage                 # 변경 사항 검증
```

### 버그 조사
```bash
/sc:troubleshoot "문제 설명"       # 문제 진단
/sc:analyze --focus problem-area    # 심층 분석
/sc:improve --fix --safe-mode       # 대상 수정 적용
```

### 사양 개발
```bash
/sc:spec-panel @existing_spec.yml --mode critique  # 전문가 검토
/sc:spec-panel @improved_spec.yml --iterations 2    # 반복적 개선
/sc:document --type technical                        # 문서 생성
```

## 전체 명령어 참조

### 개발 명령어
| 명령어 | 목적 | 최적 사용처 |
|---------|---------|----------|
| **workflow** | 구현 계획 | 프로젝트 로드맵, 스프린트 계획 |
| **implement** | 기능 개발 | 풀스택 기능, API 개발 |
| **build** | 프로젝트 컴파일 | CI/CD, 프로덕션 빌드 |
| **design** | 시스템 아키텍처 | API 스펙, 데이터베이스 스키마 |

### 분석 명령어
| 명령어 | 목적 | 최적 사용처 |
|---------|---------|----------|
| **analyze** | 코드 평가 | 품질 감사, 보안 검토 |
| **research** | 지능형 검색을 통한 웹 연구 | 기술 연구, 최신 정보, 시장 분석 |
| **business-panel** | 전략적 분석 | 비즈니스 결정, 경쟁 평가 |
| **spec-panel** | 사양 검토 | 요구사항 검증, 아키텍처 분석 |
| **troubleshoot** | 문제 진단 | 버그 조사, 성능 문제 |
| **explain** | 코드 설명 | 학습, 코드 검토 |

### 품질 명령어
| 명령어 | 목적 | 최적 사용처 |
|---------|---------|----------|
| **improve** | 코드 향상 | 성능 최적화, 리팩토링 |
| **cleanup** | 기술 부채 | 데드 코드 제거, 정리 |
| **test** | 품질 보증 | 테스트 자동화, 커버리지 분석 |
| **document** | 문서화 | API 문서, 사용자 가이드 |

### 프로젝트 관리
| 명령어 | 목적 | 최적 사용처 |
|---------|---------|----------|
| **estimate** | 프로젝트 추정 | 타임라인 계획, 리소스 할당 |
| **task** | 작업 관리 | 복잡한 워크플로우, 작업 추적 |
| **spawn** | 메타 오케스트레이션 | 대규모 프로젝트, 병렬 실행 |

### 유틸리티 명령어
| 명령어 | 목적 | 최적 사용처 |
|---------|---------|----------|
| **help** | 모든 명령어 나열 | 사용 가능한 명령어 발견 |
| **git** | 버전 제어 | 커밋 관리, 브랜치 전략 |
| **index** | 명령어 발견 | 기능 탐색, 명령어 찾기 |

### 세션 명령어
| 명령어 | 목적 | 최적 사용처 |
|---------|---------|----------|
| **load** | 컨텍스트 로딩 | 세션 초기화, 프로젝트 온보딩 |
| **save** | 세션 지속성 | 체크포인팅, 컨텍스트 보존 |
| **reflect** | 작업 검증 | 진행 상황 평가, 완료 검증 |
| **select-tool** | 도구 최적화 | 성능 최적화, 도구 선택 |

---

## 명령어 인덱스

**기능별:**
- **계획**: brainstorm, design, workflow, estimate
- **개발**: implement, build, git
- **분석**: analyze, business-panel, spec-panel, troubleshoot, explain
- **품질**: improve, cleanup, test, document
- **관리**: task, spawn, load, save, reflect
- **유틸리티**: help, index, select-tool

**복잡성별:**
- **초급**: brainstorm, implement, analyze, test, help
- **중급**: workflow, design, business-panel, spec-panel, improve, document
- **고급**: spawn, task, select-tool, reflect

## 문제 해결

**명령어 문제:**
- **명령어를 찾을 수 없음**: 설치 확인: `python3 -m SuperClaude --version`
- **응답 없음**: Claude Code 세션 재시작
- **처리 지연**: MCP 서버 없이 테스트하려면 `--no-mcp` 사용

**빠른 수정:**
- 세션 재설정: `/sc:load`로 다시 초기화
- 상태 확인: `SuperClaude install --list-components`
- 도움말 받기: [문제 해결 가이드](../Reference/troubleshooting.md)

## 다음 단계

- [플래그 가이드](flags.md) - 명령어 동작 제어
- [에이전트 가이드](agents.md) - 전문가 활성화
- [예제 모음](../Reference/examples-cookbook.md) - 실제 사용 패턴

