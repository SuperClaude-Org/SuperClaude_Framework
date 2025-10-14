# SuperClaude MCP 서버 가이드 🔌

## 개요

MCP (Model Context Protocol) 서버는 전문 도구를 통해 Claude Code의 기능을 확장합니다. SuperClaude는 8개의 MCP 서버를 통합하고 작업에 따라 언제 활성화할지에 대한 지침을 Claude에 제공합니다.

### 🔍 현실 확인
- **MCP 서버란**: 추가 도구를 제공하는 외부 Node.js 프로세스
- **MCP 서버가 아닌 것**: 내장된 SuperClaude 기능
- **활성화 방식**: Claude가 컨텍스트에 따라 적절한 서버를 사용하도록 지침을 읽음
- **제공하는 것**: Claude Code의 네이티브 기능을 확장하는 실제 도구

**핵심 서버:**
- **context7**: 공식 라이브러리 문서 및 패턴
- **sequential-thinking**: 다단계 추론 및 분석
- **magic**: 현대적인 UI 컴포넌트 생성
- **playwright**: 브라우저 자동화 및 E2E 테스팅
- **morphllm-fast-apply**: 패턴 기반 코드 변환
- **serena**: 의미론적 코드 이해 및 프로젝트 메모리
- **tavily**: 웹 검색 및 실시간 정보 검색
- **chrome-devtools**: 성능 분석 및 디버깅

## 빠른 시작

**설정 확인**: MCP 서버는 자동으로 활성화됩니다. 설치 및 문제 해결은 [설치 가이드](../Getting-Started/installation.md) 및 [문제 해결](../Reference/troubleshooting.md)을 참조하세요.

**자동 활성화 로직:**

| 요청 포함 | 활성화되는 서버 |
|-----------------|------------------|
| 라이브러리 임포트, API 이름 | **context7** |
| `--think`, 디버깅 | **sequential-thinking** |
| `component`, `UI`, frontend | **magic** |
| `test`, `e2e`, `browser` | **playwright** |
| 다중 파일 편집, 리팩토링 | **morphllm-fast-apply** |
| 대규모 프로젝트, 세션 | **serena** |
| `/sc:research`, `latest`, `current` | **tavily** |
| `performance`, `debug`, `LCP` | **chrome-devtools** |

## 서버 세부정보

### context7 📚
**목적**: 공식 라이브러리 문서 액세스
**트리거**: Import 문, 프레임워크 키워드, 문서 요청
**요구사항**: Node.js 16+, API 키 불필요

```bash
# 자동 활성화
/sc:implement "React 인증 시스템"
# → 공식 React 패턴 제공

# 수동 활성화
/sc:analyze auth-system/ --c7
```

### sequential-thinking 🧠
**목적**: 구조화된 다단계 추론 및 체계적 분석
**트리거**: 복잡한 디버깅, `--think` 플래그, 아키텍처 분석
**요구사항**: Node.js 16+, API 키 불필요

```bash
# 자동 활성화
/sc:troubleshoot "API 성능 문제"
# → 체계적인 근본 원인 분석 활성화

# 수동 활성화
/sc:analyze --think-hard architecture/
```

### magic ✨
**목적**: 21st.dev 패턴에서 현대적인 UI 컴포넌트 생성
**트리거**: UI 요청, `/ui` 명령어, 컴포넌트 개발
**요구사항**: Node.js 16+, TWENTYFIRST_API_KEY ()

```bash
# 자동 활성화
/sc:implement "반응형 대시보드 컴포넌트"
# → 현대적인 패턴으로 접근 가능한 UI 생성

# API 키 설정
export TWENTYFIRST_API_KEY="your_key_here"
```

### playwright 🎭
**목적**: 실제 브라우저 자동화 및 E2E 테스팅
**트리거**: 브라우저 테스팅, E2E 시나리오, 시각적 검증
**요구사항**: Node.js 16+, API 키 불필요

```bash
# 자동 활성화
/sc:test --type e2e "사용자 로그인 흐름"
# → 브라우저 자동화 테스팅 활성화

# 수동 활성화
/sc:validate "접근성 규정 준수" --play
```

### morphllm-fast-apply 🔄
**목적**: 효율적인 패턴 기반 코드 변환
**트리거**: 다중 파일 편집, 리팩토링, 프레임워크 마이그레이션
**요구사항**: Node.js 16+, MORPH_API_KEY

```bash
# 자동 활성화
/sc:improve legacy-codebase/ --focus maintainability
# → 파일 전반에 일관된 패턴 적용

# API 키 설정
export MORPH_API_KEY="your_key_here"
```

### serena 🧭
**목적**: 프로젝트 메모리를 갖춘 의미론적 코드 이해
**트리거**: 심볼 작업, 대규모 코드베이스, 세션 관리
**요구사항**: Python 3.9+, uv 패키지 매니저, API 키 불필요

```bash
# 자동 활성화
/sc:load existing-project/
# → 프로젝트 이해 및 메모리 구축

# 수동 활성화
/sc:refactor "UserService 추출" --serena
```

### tavily 🔍
**목적**: 연구를 위한 웹 검색 및 실시간 정보 검색
**트리거**: `/sc:research` 명령어, "최신" 정보 요청, 최신 이벤트, 사실 확인
**요구사항**: Node.js 16+, TAVILY_API_KEY (https://app.tavily.com에서 무료 티어 사용 가능)

```bash
# 자동 활성화
/sc:research "2024년 최신 AI 개발"
# → 지능형 웹 연구 수행

# 수동 활성화
/sc:analyze "시장 트렌드" --tavily

# API 키 설정 (https://app.tavily.com에서 무료 키 받기)
export TAVILY_API_KEY="tvly-your_api_key_here"
```

### chrome-devtools 📊
**목적**: 성능 분석, 디버깅, 실시간 브라우저 검사
**트리거**: 성능 감사, 레이아웃 문제 디버깅 (예: CLS), 느린 로딩 시간 (LCP), 콘솔 오류, 네트워크 요청
**요구사항**: Node.js 16+, API 키 불필요

```bash
# 자동 활성화
/sc:debug "페이지 로딩이 느림"
# → Chrome DevTools로 성능 분석 활성화

# 수동 활성화
/sc:analyze --performance "홈페이지"
```

**기능:**
- **웹 검색**: 랭킹 및 필터링을 통한 포괄적인 검색
- **뉴스 검색**: 시간 필터링된 최신 이벤트 및 업데이트
- **콘텐츠 추출**: 검색 결과에서 전체 텍스트 추출
- **도메인 필터링**: 특정 도메인 포함/제외
- **다중 홉 연구**: 발견에 기반한 반복적 검색 (최대 5홉)

**연구 깊이 제어:**
- `--depth quick`: 5-10개 소스, 기본 종합
- `--depth standard`: 10-20개 소스, 구조화된 보고서 (기본값)
- `--depth deep`: 20-40개 소스, 포괄적 분석
- `--depth exhaustive`: 40개 이상 소스, 학술 수준 연구

## 구성

**MCP 구성 파일 (`~/.claude.json`):**
```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"]
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    },
    "magic": {
      "command": "npx",
      "args": ["@21st-dev/magic"],
      "env": {"TWENTYFIRST_API_KEY": "${TWENTYFIRST_API_KEY}"}
    },
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    },
    "morphllm-fast-apply": {
      "command": "npx",
      "args": ["@morph-llm/morph-fast-apply"],
      "env": {"MORPH_API_KEY": "${MORPH_API_KEY}"}
    },
    "serena": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/oraios/serena", "serena", "start-mcp-server", "--context", "ide-assistant"]
    },
    "tavily": {
      "command": "npx",
      "args": ["-y", "tavily-mcp@latest"],
      "env": {"TAVILY_API_KEY": "${TAVILY_API_KEY}"}
    },
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest"]
    }
  }
}
```

## 사용 패턴

**서버 제어:**
```bash
# 특정 서버 활성화
/sc:analyze codebase/ --c7 --seq

# 모든 MCP 서버 비활성화
/sc:implement "간단한 함수" --no-mcp

# 모든 서버 활성화
/sc:design "복잡한 아키텍처" --all-mcp
```

**다중 서버 조정:**
```bash
# 풀스택 개발
/sc:implement "전자상거래 체크아웃"
# → Sequential: 워크플로우 분석
# → Context7: 결제 패턴
# → Magic: UI 컴포넌트
# → Serena: 코드 조직
# → Playwright: E2E 테스팅
```

## 문제 해결

**일반적인 문제:**
- **서버 연결 없음**: Node.js 확인: `node --version` (v16+ 필요)
- **Context7 실패**: 캐시 정리: `npm cache clean --force`
- **Magic/Morphllm 오류**: API 키 없이 예상됨 (유료 서비스)
- **서버 타임아웃**: Claude Code 세션 재시작

**빠른 수정:**
```bash
# 연결 재설정
# Claude Code 세션 재시작

# 종속성 확인
node --version  # v16+ 표시되어야 함

# MCP 없이 테스트
/sc:command --no-mcp

# 구성 확인
ls ~/.claude.json
```

**API 키 구성:**
```bash
# Magic 서버용 (UI 생성에 필요)
export TWENTYFIRST_API_KEY="your_key_here"

# Morphllm 서버용 (대량 변환에 필요)
export MORPH_API_KEY="your_key_here"

# Tavily 서버용 (웹 검색에 필요 - 무료 티어 사용 가능)
export TAVILY_API_KEY="tvly-your_key_here"

# 지속성을 위해 셸 프로필에 추가
echo 'export TWENTYFIRST_API_KEY="your_key"' >> ~/.bashrc
echo 'export MORPH_API_KEY="your_key"' >> ~/.bashrc
echo 'export TAVILY_API_KEY="your_key"' >> ~/.bashrc
```

**환경 변수 사용:**
- ✅ `TWENTYFIRST_API_KEY` - Magic MCP 서버 기능에 필요
- ✅ `MORPH_API_KEY` - Morphllm MCP 서버 기능에 필요
- ✅ `TAVILY_API_KEY` - Tavily MCP 서버 기능에 필요 (무료 티어 사용 가능)
- ❌ 문서의 다른 환경 변수 - 예제용, 프레임워크에서 사용하지 않음
- 📝 Magic과 Morphllm은 유료 서비스, Tavily는 무료 티어 있음, 프레임워크는 이들 없이도 작동

## 서버 조합

**API 키 없음 (무료)**:
- context7 + sequential-thinking + playwright + serena

**API 키 1개**:
- 전문 UI 개발을 위해 magic 추가

**API 키 2개**:
- 대규모 리팩토링을 위해 morphllm-fast-apply 추가

**일반적인 워크플로우:**
- **학습**: context7 + sequential-thinking
- **웹 개발**: magic + context7 + playwright
- **엔터프라이즈 리팩토링**: serena + morphllm + sequential-thinking
- **복잡한 분석**: sequential-thinking + context7 + serena
- **심층 연구**: tavily + sequential-thinking + serena + playwright
- **최신 이벤트**: tavily + context7 + sequential-thinking
- **성능 튜닝**: chrome-devtools + sequential-thinking + playwright

## 통합

**SuperClaude 명령어와 함께:**
- 분석 명령어는 자동으로 Sequential + Serena 사용
- 구현 명령어는 Magic + Context7 사용
- 테스팅 명령어는 Playwright + Sequential 사용
- 연구 명령어는 Tavily + Sequential + Playwright 사용

**행동 모드와 함께:**
- 브레인스토밍 모드: 발견을 위한 Sequential
- 작업 관리: 지속성을 위한 Serena
- 오케스트레이션 모드: 최적의 서버 선택
- 심층 연구 모드: Tavily + Sequential + Playwright 조정

**성능 제어:**
- 시스템 부하에 따른 자동 리소스 관리
- 동시성 제어: `--concurrency N` (1-15)
- 제약 조건 하에서 우선순위 기반 서버 선택

## 관련 리소스

**필수 읽기:**
- [명령어 가이드](commands.md) - MCP 서버를 활성화하는 명령어
- [빠른 시작 가이드](../Getting-Started/quick-start.md) - MCP 설정 가이드

**고급 사용:**
- [행동 모드](modes.md) - 모드-MCP 조정
- [에이전트 가이드](agents.md) - 에이전트-MCP 통합
- [세션 관리](session-management.md) - Serena 워크플로우

**기술 참조:**
- [예제 모음](../Reference/examples-cookbook.md) - MCP 워크플로우 패턴
- [기술 아키텍처](../Developer-Guide/technical-architecture.md) - 통합 세부사항

