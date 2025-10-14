# SuperClaude 에이전트 가이드 🤖

SuperClaude는 Claude Code가 전문 지식을 위해 호출할 수 있는 15개의 도메인 전문 에이전트를 제공합니다.

## 🧪 에이전트 활성화 테스트

이 가이드를 사용하기 전에 에이전트 선택이 작동하는지 확인하세요:

```bash
# 수동 에이전트 호출 테스트
@agent-python-expert "데코레이터 설명해줘"
# 예상 동작: Python 전문가가 자세한 설명으로 응답

# 보안 에이전트 자동 활성화 테스트
/sc:implement "JWT 인증"
# 예상 동작: 보안 엔지니어가 자동으로 활성화되어야 함

# 프론트엔드 에이전트 자동 활성화 테스트
/sc:implement "반응형 네비게이션 컴포넌트"
# 예상 동작: 프론트엔드 아키텍트 + Magic MCP가 활성화되어야 함

# 체계적 분석 테스트
/sc:troubleshoot "느린 API 성능"
# 예상 동작: 근본 원인 분석가 + 성능 엔지니어 활성화

# 수동 및 자동 결합 테스트
/sc:analyze src/
@agent-refactoring-expert "개선 사항 제안해줘"
# 예상 동작: 분석 후 리팩토링 제안
```

**테스트가 실패하면**: `~/.claude/agents/`에 에이전트 파일이 있는지 확인하거나 Claude Code 세션을 재시작하세요

## 핵심 개념

### SuperClaude 에이전트란?

**에이전트**는 Claude Code의 동작을 수정하는 컨텍스트 지시문으로 구현된 전문 AI 도메인 전문가입니다. 각 에이전트는 `superclaude/Agents/` 디렉토리에 있는 신중하게 작성된 `.md` 파일로, 도메인별 전문 지식, 행동 패턴, 문제 해결 접근 방식을 포함합니다.

**중요**: 에이전트는 별도의 AI 모델이나 소프트웨어가 아닙니다 - Claude Code가 읽어 전문화된 행동을 채택하는 컨텍스트 구성입니다.

### 에이전트 사용 방법 2가지

#### 1. @agent- 접두사를 사용한 수동 호출
```bash
# 특정 에이전트를 직접 호출
@agent-security "인증 구현 검토해줘"
@agent-frontend "반응형 네비게이션 디자인해줘"
@agent-architect "마이크로서비스 마이그레이션 계획해줘"
```

#### 2. 자동 활성화 (행동 라우팅)
"자동 활성화"는 Claude Code가 요청의 키워드와 패턴에 따라 적절한 컨텍스트를 참여시키기 위해 행동 지침을 읽는 것을 의미합니다. SuperClaude는 Claude가 가장 적절한 전문가에게 라우팅하기 위해 따르는 행동 가이드라인을 제공합니다.

> **📝 에이전트 "자동 활성화" 작동 방식**: 
> 에이전트 활성화는 자동 시스템 로직이 아닙니다 - 컨텍스트 파일의 행동 지침입니다.
> 문서에서 에이전트가 "자동 활성화"된다고 할 때, Claude Code가 요청의 키워드와 패턴을 기반으로 
> 특정 도메인 전문 지식을 참여시키는 지침을 읽는다는 의미입니다. 이는 기본 메커니즘에 대해 
> 투명하면서도 지능적인 라우팅 경험을 만듭니다.

```bash
# 이러한 명령은 관련 에이전트를 자동 활성화합니다
/sc:implement "JWT 인증"          # → security-engineer 자동 활성화
/sc:design "React 대시보드"        # → frontend-architect 자동 활성화
/sc:troubleshoot "메모리 누수"     # → performance-engineer 자동 활성화
```

**MCP 서버**는 Context7(문서), Sequential(분석), Magic(UI), Playwright(테스팅), Morphllm(코드 변환)과 같은 전문 도구를 통해 향상된 기능을 제공합니다.

**도메인 전문가**는 일반적인 접근 방식보다 더 깊고 정확한 솔루션을 제공하기 위해 좁은 전문 영역에 집중합니다.

### 에이전트 선택 규칙

**우선순위 계층:**
1. **수동 재정의** - @agent-[name]이 자동 활성화보다 우선합니다
2. **키워드** - 직접적인 도메인 용어가 주요 에이전트를 트리거합니다
3. **파일 유형** - 확장자가 언어/프레임워크 전문가를 활성화합니다
4. **복잡성** - 다단계 작업이 조정 에이전트를 참여시킵니다
5. **컨텍스트** - 관련 개념이 보완 에이전트를 트리거합니다

**충돌 해결:**
- 수동 호출 → 지정된 에이전트가 우선합니다
- 여러 일치 → 다중 에이전트 조정
- 불명확한 컨텍스트 → 요구사항 분석가 활성화
- 높은 복잡성 → 시스템 아키텍트 감독
- 품질 우려 → 자동 QA 에이전트 포함

**선택 결정 트리:**
```
작업 분석 →
├─ 수동 @agent-? → 지정된 에이전트 사용
├─ 단일 도메인? → 주요 에이전트 활성화
├─ 다중 도메인? → 전문 에이전트 조정
├─ 복잡한 시스템? → system-architect 감독 추가
├─ 품질 중요? → security + performance + quality 에이전트 포함
└─ 학습 중심? → learning-guide + technical-writer 추가
```

## 빠른 시작 예제

### 수동 에이전트 호출
```bash
# @agent- 접두사로 특정 에이전트를 명시적으로 호출
@agent-python-expert "이 데이터 처리 파이프라인 최적화해줘"
@agent-quality-engineer "포괄적인 테스트 스위트 만들어줘"
@agent-technical-writer "이 API를 예제와 함께 문서화해줘"
@agent-socratic-mentor "이 디자인 패턴 설명해줘"
```

### 자동 에이전트 조정
```bash
# 자동 활성화를 트리거하는 명령
/sc:implement "속도 제한이 있는 JWT 인증"
# → 트리거: security-engineer + backend-architect + quality-engineer

/sc:design "접근 가능한 React 대시보드와 문서"
# → 트리거: frontend-architect + learning-guide + technical-writer

/sc:troubleshoot "간헐적 실패가 있는 느린 배포 파이프라인"
# → 트리거: devops-architect + performance-engineer + root-cause-analyst

/sc:audit "결제 처리 보안 취약점"
# → 트리거: security-engineer + quality-engineer + refactoring-expert
```

### 수동 및 자동 접근 방식 결합
```bash
# 명령으로 시작 (자동 활성화)
/sc:implement "사용자 프로필 시스템"

# 그런 다음 전문가 검토를 명시적으로 추가
@agent-security "프로필 시스템의 OWASP 규정 준수 검토해줘"
@agent-performance-engineer "데이터베이스 쿼리 최적화해줘"
```

---

## SuperClaude 에이전트 팀 👥

### 아키텍처 및 시스템 설계 에이전트 🏗️

### system-architect 🏢
**전문 분야**: 확장성과 서비스 아키텍처에 중점을 둔 대규모 분산 시스템 설계

**자동 활성화**:
- 키워드: "architecture", "microservices", "scalability", "system design", "distributed"
- 컨텍스트: 다중 서비스 시스템, 아키텍처 결정, 기술 선택
- 복잡성: >5개 컴포넌트 또는 교차 도메인 통합 요구사항

**역량**:
- 서비스 경계 정의 및 마이크로서비스 분해
- 기술 스택 선택 및 통합 전략
- 확장성 계획 및 성능 아키텍처
- 이벤트 기반 아키텍처 및 메시징 패턴
- 데이터 흐름 설계 및 시스템 통합

**예제**:
1. **전자상거래 플랫폼**: 이벤트 소싱을 사용한 사용자, 제품, 결제, 알림 서비스를 위한 마이크로서비스 설계
2. **실시간 분석**: 스트림 처리 및 시계열 저장소를 갖춘 고처리량 데이터 수집 아키텍처
3. **다중 테넌트 SaaS**: 테넌트 격리, 공유 인프라, 수평 확장 전략을 갖춘 시스템 설계

### 성공 기준
- [ ] 응답에서 시스템 수준 사고가 명확함
- [ ] 서비스 경계 및 통합 패턴 언급
- [ ] 확장성 및 신뢰성 고려사항 포함
- [ ] 기술 스택 권장사항 제공

**검증:** `/sc:design "마이크로서비스 플랫폼"`은 system-architect를 활성화해야 함
**테스트:** 출력에 서비스 분해 및 통합 패턴이 포함되어야 함
**확인:** 인프라 문제에 대해 devops-architect와 조정해야 함

**최적의 협업 대상**: devops-architect(인프라), performance-engineer(최적화), security-engineer(규정 준수)

---

### backend-architect ⚙️
**전문 분야**: API 신뢰성과 데이터 무결성을 강조하는 견고한 서버 측 시스템 설계

**자동 활성화**:
- 키워드: "API", "backend", "server", "database", "REST", "GraphQL", "endpoint"
- 파일 유형: API 스펙, 서버 설정, 데이터베이스 스키마
- 컨텍스트: 서버 측 로직, 데이터 지속성, API 개발

**역량**:
- RESTful 및 GraphQL API 아키텍처 및 디자인 패턴
- 데이터베이스 스키마 설계 및 쿼리 최적화 전략
- 인증, 권한 부여 및 보안 구현
- 오류 처리, 로깅 및 모니터링 통합
- 캐싱 전략 및 성능 최적화

**예제**:
1. **사용자 관리 API**: JWT 인증, 역할 기반 액세스 제어 및 속도 제한
2. **결제 처리**: PCI 규정 준수 트랜잭션 처리, 멱등성 및 감사 추적
3. **콘텐츠 관리**: 캐싱, 페이지네이션, 실시간 알림을 갖춘 RESTful API

**최적의 협업 대상**: security-engineer(인증/보안), performance-engineer(최적화), quality-engineer(테스팅)

---

### frontend-architect 🎨
**전문 분야**: 접근성과 사용자 경험에 중점을 둔 현대적인 웹 애플리케이션 아키텍처

**자동 활성화**:
- 키워드: "UI", "frontend", "React", "Vue", "Angular", "component", "accessibility", "responsive"
- 파일 유형: .jsx, .vue, .ts(프론트엔드), .css, .scss
- 컨텍스트: 사용자 인터페이스 개발, 컴포넌트 설계, 클라이언트 측 아키텍처

**역량**:
- 컴포넌트 아키텍처 및 디자인 시스템 구현
- 상태 관리 패턴(Redux, Zustand, Pinia)
- 접근성 규정 준수(WCAG 2.1) 및 포용적 디자인
- 성능 최적화 및 번들 분석
- 프로그레시브 웹 앱 및 모바일 우선 개발

**예제**:
1. **대시보드 인터페이스**: 실시간 업데이트 및 반응형 그리드 레이아웃을 갖춘 접근 가능한 데이터 시각화
2. **폼 시스템**: 검증, 오류 처리, 접근성 기능을 갖춘 복잡한 다단계 폼
3. **디자인 시스템**: 일관된 스타일링 및 상호작용 패턴을 갖춘 재사용 가능한 컴포넌트 라이브러리

**최적의 협업 대상**: learning-guide(사용자 안내), performance-engineer(최적화), quality-engineer(테스팅)

---

### devops-architect 🚀
**전문 분야**: 안정적인 소프트웨어 전달을 위한 인프라 자동화 및 배포 파이프라인 설계

**자동 활성화**:
- 키워드: "deploy", "CI/CD", "Docker", "Kubernetes", "infrastructure", "monitoring", "pipeline"
- 파일 유형: Dockerfile, docker-compose.yml, k8s 매니페스트, CI 설정
- 컨텍스트: 배포 프로세스, 인프라 관리, 자동화

**역량**:
- 자동화된 테스팅 및 배포를 갖춘 CI/CD 파이프라인 설계
- 컨테이너 오케스트레이션 및 Kubernetes 클러스터 관리
- Terraform 및 클라우드 플랫폼을 사용한 Infrastructure as Code
- 메트릭, 로그, 추적을 위한 모니터링, 로깅, 관찰성 스택 구현
- 보안 스캔 및 규정 준수 자동화

**예제**:
1. **마이크로서비스 배포**: 서비스 메시, 자동 확장, blue-green 릴리스를 갖춘 Kubernetes 배포
2. **다중 환경 파이프라인**: 자동화된 테스팅, 보안 스캔, 단계별 배포를 갖춘 GitOps 워크플로우
3. **모니터링 스택**: 메트릭, 로그, 추적, 알림 시스템을 갖춘 포괄적인 관찰성

**최적의 협업 대상**: system-architect(인프라 계획), security-engineer(규정 준수), performance-engineer(모니터링)

---

### deep-research-agent 🔬
**전문 분야**: 적응형 전략과 다중 홉 추론을 사용한 포괄적인 연구

**자동 활성화**:
- 키워드: "research", "investigate", "discover", "explore", "find out", "search for", "latest", "current"
- 명령어: `/sc:research`가 자동으로 이 에이전트를 활성화
- 컨텍스트: 철저한 조사가 필요한 복잡한 쿼리, 최신 정보 필요, 사실 확인
- 복잡성: 여러 도메인에 걸쳐 있거나 반복적 탐색이 필요한 질문

**역량**:
- **적응형 계획 전략**: Planning(직접), Intent(먼저 명확화), Unified(협업)
- **다중 홉 추론**: 최대 5단계 - 엔티티 확장, 시간적 진행, 개념적 심화, 인과 관계 체인
- **자기 성찰 메커니즘**: 각 주요 단계 후 진행 상황 평가 및 재계획 트리거
- **증거 관리**: 명확한 인용, 관련성 점수, 불확실성 인정
- **도구 오케스트레이션**: Tavily(검색), Playwright(JavaScript 콘텐츠), Sequential(추론)을 사용한 병렬 우선 실행
- **학습 통합**: Serena 메모리를 통한 패턴 인식 및 전략 재사용

**연구 깊이 수준**:
- **Quick**: 기본 검색, 1홉, 요약 출력
- **Standard**: 확장 검색, 2-3홉, 구조화된 보고서(기본값)
- **Deep**: 포괄적 검색, 3-4홉, 상세 분석
- **Exhaustive**: 최대 깊이, 5홉, 완전한 조사

**예제**:
1. **기술 연구**: `/sc:research "최신 React Server Components 패턴"` → 구현 예제를 포함한 포괄적인 기술 연구
2. **시장 분석**: `/sc:research "2024년 AI 코딩 어시스턴트 현황" --strategy unified` → 사용자 입력을 포함한 협업 분석
3. **학술 조사**: `/sc:research "양자 컴퓨팅 돌파구" --depth exhaustive` → 증거 체인을 포함한 포괄적인 문헌 검토

**워크플로우 패턴** (6단계):
1. **이해** (5-10%): 쿼리 복잡성 평가
2. **계획** (10-15%): 전략 선택 및 병렬 기회 식별
3. **TodoWrite** (5%): 적응형 작업 계층 구조 생성(3-15개 작업)
4. **실행** (50-60%): 병렬 검색 및 추출
5. **추적** (지속적): 진행 상황 및 신뢰도 모니터링
6. **검증** (10-15%): 증거 체인 확인

**출력**: 보고서는 `claudedocs/research_[topic]_[timestamp].md`에 저장됨

**최적의 협업 대상**: system-architect(기술 연구), learning-guide(교육 연구), requirements-analyst(시장 연구)

### 품질 및 분석 에이전트 🔍

### security-engineer 🔒
**전문 분야**: 위협 모델링 및 취약점 예방에 중점을 둔 애플리케이션 보안 아키텍처

**자동 활성화**:
- 키워드: "security", "auth", "authentication", "vulnerability", "encryption", "compliance", "OWASP"
- 컨텍스트: 보안 검토, 인증 흐름, 데이터 보호 요구사항
- 위험 지표: 결제 처리, 사용자 데이터, API 액세스, 규정 준수 필요

**역량**:
- 위협 모델링 및 공격 표면 분석
- 안전한 인증 및 권한 부여 설계(OAuth, JWT, SAML)
- 데이터 암호화 전략 및 키 관리
- 취약점 평가 및 침투 테스트 지침
- 보안 규정 준수(GDPR, HIPAA, PCI-DSS) 구현

**예제**:
1. **OAuth 구현**: 토큰 새로 고침 및 역할 기반 액세스를 갖춘 안전한 다중 테넌트 인증
2. **API 보안**: 속도 제한, 입력 검증, SQL 인젝션 방지, 보안 헤더
3. **데이터 보호**: 저장/전송 중 암호화, 키 순환, 프라이버시 바이 디자인 아키텍처

**최적의 협업 대상**: backend-architect(API 보안), quality-engineer(보안 테스팅), root-cause-analyst(사고 대응)

---

### performance-engineer ⚡
**전문 분야**: 확장성과 리소스 효율성에 중점을 둔 시스템 성능 최적화

**자동 활성화**:
- 키워드: "performance", "slow", "optimization", "bottleneck", "latency", "memory", "CPU"
- 컨텍스트: 성능 문제, 확장성 우려, 리소스 제약
- 메트릭: 응답 시간 >500ms, 높은 메모리 사용량, 낮은 처리량

**역량**:
- 성능 프로파일링 및 병목 현상 식별
- 데이터베이스 쿼리 최적화 및 인덱싱 전략
- 캐싱 구현(Redis, CDN, 애플리케이션 레벨)
- 부하 테스트 및 용량 계획
- 메모리 관리 및 리소스 최적화

**예제**:
1. **API 최적화**: 캐싱 및 쿼리 최적화를 통해 응답 시간을 2초에서 200ms로 단축
2. **데이터베이스 확장**: 읽기 복제본, 연결 풀링, 쿼리 결과 캐싱 구현
3. **프론트엔드 성능**: 번들 최적화, 지연 로딩, CDN 구현으로 <3초 로드 시간 달성

**최적의 협업 대상**: system-architect(확장성), devops-architect(인프라), root-cause-analyst(디버깅)

---

### root-cause-analyst 🔍
**전문 분야**: 증거 기반 분석 및 가설 테스트를 사용한 체계적인 문제 조사

**자동 활성화**:
- 키워드: "bug", "issue", "problem", "debugging", "investigation", "troubleshoot", "error"
- 컨텍스트: 시스템 장애, 예상치 못한 동작, 복잡한 다중 컴포넌트 문제
- 복잡성: 체계적인 조사가 필요한 교차 시스템 문제

**역량**:
- 체계적인 디버깅 방법론 및 근본 원인 분석
- 시스템 전반의 오류 상관 관계 및 종속성 매핑
- 실패 조사를 위한 로그 분석 및 패턴 인식
- 복잡한 문제에 대한 가설 형성 및 테스트
- 사고 대응 및 사후 분석 절차

**예제**:
1. **데이터베이스 연결 실패**: 연결 풀, 네트워크 타임아웃, 리소스 제한 전반의 간헐적 실패 추적
2. **결제 처리 오류**: API 로그, 데이터베이스 상태, 외부 서비스 응답을 통한 트랜잭션 실패 조사
3. **성능 저하**: 메트릭 상관 관계, 리소스 사용량, 코드 변경을 통한 점진적인 둔화 분석

**최적의 협업 대상**: performance-engineer(성능 문제), security-engineer(보안 사고), quality-engineer(테스트 실패)

---

### quality-engineer ✅
**전문 분야**: 자동화 및 커버리지에 중점을 둔 포괄적인 테스팅 전략 및 품질 보증

**자동 활성화**:
- 키워드: "test", "testing", "quality", "QA", "validation", "coverage", "automation"
- 컨텍스트: 테스트 계획, 품질 게이트, 검증 요구사항
- 품질 우려: 코드 커버리지 <80%, 테스트 자동화 부족, 품질 문제

**역량**:
- 테스트 전략 설계(단위, 통합, e2e, 성능 테스팅)
- 테스트 자동화 프레임워크 구현 및 CI/CD 통합
- 품질 메트릭 정의 및 모니터링(커버리지, 결함률)
- 엣지 케이스 식별 및 경계 테스팅 시나리오
- 접근성 테스팅 및 규정 준수 검증

**예제**:
1. **전자상거래 테스팅**: 사용자 흐름, 결제 처리, 재고 관리를 다루는 포괄적인 테스트 스위트
2. **API 테스팅**: REST/GraphQL API에 대한 자동화된 계약 테스팅, 부하 테스팅, 보안 테스팅
3. **접근성 검증**: 자동화 및 수동 접근성 감사를 통한 WCAG 2.1 규정 준수 테스팅

**최적의 협업 대상**: security-engineer(보안 테스팅), performance-engineer(부하 테스팅), frontend-architect(UI 테스팅)

---

### refactoring-expert 🔧
**전문 분야**: 체계적인 리팩토링 및 기술 부채 관리를 통한 코드 품질 개선

**자동 활성화**:
- 키워드: "refactor", "clean code", "technical debt", "SOLID", "maintainability", "code smell"
- 컨텍스트: 레거시 코드 개선, 아키텍처 업데이트, 코드 품질 문제
- 품질 지표: 높은 복잡성, 중복 코드, 낮은 테스트 커버리지

**역량**:
- SOLID 원칙 적용 및 디자인 패턴 구현
- 코드 냄새 식별 및 체계적인 제거
- 레거시 코드 현대화 전략 및 마이그레이션 계획
- 기술 부채 평가 및 우선순위 프레임워크
- 코드 구조 개선 및 아키텍처 리팩토링

**예제**:
1. **레거시 현대화**: 모놀리식 애플리케이션을 테스트 가능성이 향상된 모듈형 아키텍처로 변환
2. **디자인 패턴**: 결제 처리에 Strategy 패턴 구현으로 결합도 감소 및 확장성 향상
3. **코드 정리**: 중복 코드 제거, 명명 규칙 개선, 재사용 가능한 컴포넌트 추출

**최적의 협업 대상**: system-architect(아키텍처 개선), quality-engineer(테스팅 전략), python-expert(언어별 패턴)

### 전문 개발 에이전트 🎯

### python-expert 🐍
**전문 분야**: 현대적인 프레임워크와 성능을 강조하는 프로덕션급 Python 개발

**자동 활성화**:
- 키워드: "Python", "Django", "FastAPI", "Flask", "asyncio", "pandas", "pytest"
- 파일 유형: .py, requirements.txt, pyproject.toml, Pipfile
- 컨텍스트: Python 개발 작업, API 개발, 데이터 처리, 테스팅

**역량**:
- 현대적인 Python 아키텍처 패턴 및 프레임워크 선택
- asyncio 및 concurrent futures를 사용한 비동기 프로그래밍
- 프로파일링 및 알고리즘 개선을 통한 성능 최적화
- pytest, 픽스처, 테스트 자동화를 사용한 테스팅 전략
- pip, poetry, Docker를 사용한 패키지 관리 및 배포

**예제**:
1. **FastAPI 마이크로서비스**: Pydantic 검증, 의존성 주입, OpenAPI 문서를 갖춘 고성능 비동기 API
2. **데이터 파이프라인**: 대규모 데이터셋에 대한 오류 처리, 로깅, 병렬 처리를 갖춘 Pandas 기반 ETL
3. **Django 애플리케이션**: 사용자 정의 사용자 모델, API 엔드포인트, 포괄적인 테스트 커버리지를 갖춘 풀스택 웹 앱

**최적의 협업 대상**: backend-architect(API 설계), quality-engineer(테스팅), performance-engineer(최적화)

---

### requirements-analyst 📝
**전문 분야**: 체계적인 이해관계자 분석을 통한 요구사항 발견 및 사양 개발

**자동 활성화**:
- 키워드: "requirements", "specification", "PRD", "user story", "functional", "scope", "stakeholder"
- 컨텍스트: 프로젝트 시작, 불명확한 요구사항, 범위 정의 필요
- 복잡성: 다중 이해관계자 프로젝트, 불명확한 목표, 상충하는 요구사항

**역량**:
- 이해관계자 인터뷰 및 워크숍을 통한 요구사항 도출
- 승인 기준 및 완료 정의를 갖춘 사용자 스토리 작성
- 기능 및 비기능 사양 문서화
- 이해관계자 분석 및 요구사항 우선순위 프레임워크
- 범위 관리 및 변경 제어 프로세스

**예제**:
1. **제품 요구사항 문서**: 사용자 페르소나, 기능 사양, 성공 메트릭을 포함한 핀테크 모바일 앱 포괄적 PRD
2. **API 사양**: 오류 처리, 보안, 성능 기준을 갖춘 결제 처리 API에 대한 상세 요구사항
3. **마이그레이션 요구사항**: 데이터 마이그레이션, 사용자 교육, 롤백 절차를 갖춘 레거시 시스템 현대화 요구사항

**최적의 협업 대상**: system-architect(기술적 실현 가능성), technical-writer(문서화), learning-guide(사용자 안내)

### 커뮤니케이션 및 학습 에이전트 📚

### technical-writer 📚
**전문 분야**: 대상 분석 및 명확성에 중점을 둔 기술 문서화 및 커뮤니케이션

**자동 활성화**:
- 키워드: "documentation", "readme", "API docs", "user guide", "technical writing", "manual"
- 컨텍스트: 문서화 요청, API 문서화, 사용자 가이드, 기술 설명
- 파일 유형: .md, .rst, API 스펙, 문서 파일

**역량**:
- 기술 문서화 아키텍처 및 정보 설계
- 다양한 기술 수준에 대한 대상 분석 및 콘텐츠 타겟팅
- 작동 예제 및 통합 지침을 포함한 API 문서화
- 단계별 절차 및 문제 해결을 포함한 사용자 가이드 작성
- 접근성 표준 적용 및 포용적 언어 사용

**예제**:
1. **API 문서화**: 인증, 엔드포인트, 예제, SDK 통합 가이드를 포함한 포괄적인 REST API 문서
2. **사용자 매뉴얼**: 스크린샷, 문제 해결, FAQ 섹션을 포함한 단계별 설치 및 구성 가이드
3. **기술 사양**: 다이어그램, 데이터 흐름, 구현 세부사항을 포함한 시스템 아키텍처 문서

**최적의 협업 대상**: requirements-analyst(사양 명확성), learning-guide(교육 콘텐츠), frontend-architect(UI 문서화)

---

### learning-guide 🎓
**전문 분야**: 기술 개발 및 멘토십에 중점을 둔 교육 콘텐츠 설계 및 점진적 학습

**자동 활성화**:
- 키워드: "explain", "learn", "tutorial", "beginner", "teaching", "education", "training"
- 컨텍스트: 교육 요청, 개념 설명, 기술 개발, 학습 경로
- 복잡성: 단계별 분해 및 점진적 이해가 필요한 복잡한 주제

**역량**:
- 점진적 기술 개발을 갖춘 학습 경로 설계
- 유추 및 예제를 통한 복잡한 개념 설명
- 실습 연습을 포함한 대화형 튜토리얼 생성
- 기술 평가 및 역량 평가 프레임워크
- 멘토십 전략 및 개인화된 학습 접근법

**예제**:
1. **프로그래밍 튜토리얼**: 실습 연습, 코드 예제, 점진적 복잡성을 포함한 대화형 React 튜토리얼
2. **개념 설명**: 시각적 다이어그램 및 연습 문제를 포함한 실제 예제를 통한 데이터베이스 정규화 설명
3. **기술 평가**: 실제 프로젝트 및 피드백을 포함한 풀스택 개발을 위한 포괄적인 평가 프레임워크

**최적의 협업 대상**: technical-writer(교육 문서화), frontend-architect(대화형 학습), requirements-analyst(학습 목표)

---

## 에이전트 조정 및 통합 🤝

### 조정 패턴

**아키텍처 팀**:
- **풀스택 개발**: frontend-architect + backend-architect + security-engineer + quality-engineer
- **시스템 설계**: system-architect + devops-architect + performance-engineer + security-engineer
- **레거시 현대화**: refactoring-expert + system-architect + quality-engineer + technical-writer

**품질 팀**:
- **보안 감사**: security-engineer + quality-engineer + root-cause-analyst + requirements-analyst
- **성능 최적화**: performance-engineer + system-architect + devops-architect + root-cause-analyst
- **테스팅 전략**: quality-engineer + security-engineer + performance-engineer + frontend-architect

**커뮤니케이션 팀**:
- **문서화 프로젝트**: technical-writer + requirements-analyst + learning-guide + 도메인 전문가
- **학습 플랫폼**: learning-guide + frontend-architect + technical-writer + quality-engineer
- **API 문서화**: backend-architect + technical-writer + security-engineer + quality-engineer

### MCP 서버 통합

**MCP 서버를 통한 향상된 기능**:
- **Context7**: 모든 아키텍트 및 전문가를 위한 공식 문서화 패턴
- **Sequential**: root-cause-analyst, system-architect, performance-engineer를 위한 다단계 분석
- **Magic**: frontend-architect, learning-guide 대화형 콘텐츠를 위한 UI 생성
- **Playwright**: quality-engineer를 위한 브라우저 테스팅, frontend-architect를 위한 접근성 검증
- **Morphllm**: refactoring-expert를 위한 코드 변환, python-expert를 위한 대량 변경
- **Serena**: 모든 에이전트를 위한 프로젝트 메모리, 세션 전반의 컨텍스트 보존

### 에이전트 활성화 문제 해결

## 문제 해결

문제 해결 도움말은 다음을 참조하세요:
- [일반적인 문제](../Reference/common-issues.md) - 자주 발생하는 문제에 대한 빠른 수정
- [문제 해결 가이드](../Reference/troubleshooting.md) - 포괄적인 문제 해결

### 일반적인 문제
- **에이전트 활성화 없음**: 도메인 키워드 사용: "security", "performance", "frontend"
- **잘못된 에이전트 선택**: 에이전트 문서의 트리거 키워드 확인
- **너무 많은 에이전트**: 주요 도메인에 키워드 집중 또는 `/sc:focus [domain]` 사용
- **에이전트가 조정하지 않음**: 작업 복잡성 증가 또는 다중 도메인 키워드 사용
- **에이전트 전문 지식 불일치**: 더 구체적인 기술 용어 사용

### 즉각적인 수정
- **에이전트 활성화 강제**: 요청에 명시적 도메인 키워드 사용
- **에이전트 선택 재설정**: Claude Code 세션을 재시작하여 에이전트 상태 재설정
- **에이전트 패턴 확인**: 에이전트 문서의 트리거 키워드 검토
- **기본 활성화 테스트**: `/sc:implement "security auth"`로 security-engineer 테스트

### 에이전트별 문제 해결

**보안 에이전트 없음:**
```bash
# 문제: 보안 우려가 security-engineer를 트리거하지 않음
# 빠른 수정: 명시적 보안 키워드 사용
"implement authentication"              # 일반적 - 트리거하지 않을 수 있음
"implement JWT authentication security" # 명시적 - security-engineer 트리거
"secure user login with encryption"    # 보안 중심 - security-engineer 트리거
```

**성능 에이전트 없음:**
```bash
# 문제: 성능 문제가 performance-engineer를 트리거하지 않음
# 빠른 수정: 성능별 용어 사용
"make it faster"                       # 모호함 - 트리거하지 않을 수 있음
"optimize slow database queries"       # 구체적 - performance-engineer 트리거
"reduce API latency and bottlenecks"   # 성능 중심 - performance-engineer 트리거
```

**아키텍처 에이전트 없음:**
```bash
# 문제: 시스템 설계가 아키텍처 에이전트를 트리거하지 않음
# 빠른 수정: 아키텍처 키워드 사용
"build an app"                         # 일반적 - 기본 에이전트 트리거
"design microservices architecture"    # 구체적 - system-architect 트리거
"scalable distributed system design"   # 아키텍처 중심 - system-architect 트리거
```

**잘못된 에이전트 조합:**
```bash
# 문제: 백엔드 작업에 프론트엔드 에이전트 활성화
# 빠른 수정: 도메인별 용어 사용
"create user interface"                # frontend-architect를 트리거할 수 있음
"create REST API endpoints"            # 구체적 - backend-architect 트리거
"implement server-side authentication" # 백엔드 중심 - backend-architect 트리거
```

### 지원 수준

**빠른 수정:**
- 에이전트 트리거 테이블의 명시적 도메인 키워드 사용
- Claude Code 세션 재시작 시도
- 혼란을 피하기 위해 단일 도메인에 집중

**상세 도움말:**
- 에이전트 설치 문제는 [일반적인 문제 가이드](../Reference/common-issues.md) 참조
- 대상 에이전트의 트리거 키워드 검토

**전문가 지원:**
- `SuperClaude install --diagnose` 사용
- 조정 분석은 [진단 참조 가이드](../Reference/diagnostic-reference.md) 참조

**커뮤니티 지원:**
- [GitHub Issues](https://github.com/SuperClaude-Org/SuperClaude_Framework/issues)에서 문제 보고
- 예상 대비 실제 에이전트 활성화 예제 포함

### 성공 검증

에이전트 수정 적용 후 테스트:
- [ ] 도메인별 요청이 올바른 에이전트 활성화 (security → security-engineer)
- [ ] 복잡한 작업이 다중 에이전트 조정 트리거 (3개 이상 에이전트)
- [ ] 에이전트 전문 지식이 작업 요구사항과 일치 (API → backend-architect)
- [ ] 적절한 경우 품질 에이전트 자동 포함 (security, performance, testing)
- [ ] 응답에 도메인 전문 지식 및 전문 지식 표시

## 빠른 문제 해결 (레거시)
- **에이전트 활성화 없음** → 도메인 키워드 사용: "security", "performance", "frontend"
- **잘못된 에이전트** → 에이전트 문서의 트리거 키워드 확인
- **너무 많은 에이전트** → 주요 도메인에 키워드 집중
- **에이전트가 조정하지 않음** → 작업 복잡성 증가 또는 다중 도메인 키워드 사용

**에이전트가 활성화되지 않나요?**
1. **키워드 확인**: 도메인별 용어 사용 (예: security-engineer의 경우 "login"이 아닌 "authentication")
2. **컨텍스트 추가**: 파일 유형, 프레임워크 또는 특정 기술 포함
3. **복잡성 증가**: 다중 도메인 문제가 더 많은 에이전트 트리거
4. **예제 사용**: 에이전트 전문 지식과 일치하는 구체적인 시나리오 참조

**너무 많은 에이전트?**
- 주요 도메인 필요에 키워드 집중
- `/sc:focus [domain]`을 사용하여 범위 제한
- 특정 에이전트로 시작하고 필요에 따라 확장

**잘못된 에이전트?**
- 에이전트 문서의 트리거 키워드 검토
- 대상 도메인에 더 구체적인 용어 사용
- 명시적 요구사항 또는 제약조건 추가

## 빠른 참조 📋

### 에이전트 트리거 조회

| 트리거 유형 | 키워드/패턴 | 활성화된 에이전트 |
|-------------|-------------------|------------------|
| **보안** | "auth", "security", "vulnerability", "encryption" | security-engineer |
| **성능** | "slow", "optimization", "bottleneck", "latency" | performance-engineer |
| **프론트엔드** | "UI", "React", "Vue", "component", "responsive" | frontend-architect |
| **백엔드** | "API", "server", "database", "REST", "GraphQL" | backend-architect |
| **테스팅** | "test", "QA", "validation", "coverage" | quality-engineer |
| **DevOps** | "deploy", "CI/CD", "Docker", "Kubernetes" | devops-architect |
| **아키텍처** | "architecture", "microservices", "scalability" | system-architect |
| **Python** | ".py", "Django", "FastAPI", "asyncio" | python-expert |
| **문제** | "bug", "issue", "debugging", "troubleshoot" | root-cause-analyst |
| **코드 품질** | "refactor", "clean code", "technical debt" | refactoring-expert |
| **문서화** | "documentation", "readme", "API docs" | technical-writer |
| **학습** | "explain", "tutorial", "beginner", "teaching" | learning-guide |
| **요구사항** | "requirements", "PRD", "specification" | requirements-analyst |
| **연구** | "research", "investigate", "latest", "current" | deep-research-agent |

### 명령어-에이전트 매핑

| 명령어 | 주요 에이전트 | 지원 에이전트 |
|---------|----------------|-------------------|
| `/sc:implement` | 도메인 아키텍트 (frontend, backend) | security-engineer, quality-engineer |
| `/sc:analyze` | quality-engineer, security-engineer | performance-engineer, root-cause-analyst |
| `/sc:troubleshoot` | root-cause-analyst | 도메인 전문가, performance-engineer |
| `/sc:improve` | refactoring-expert | quality-engineer, performance-engineer |
| `/sc:document` | technical-writer | 도메인 전문가, learning-guide |
| `/sc:design` | system-architect | 도메인 아키텍트, requirements-analyst |
| `/sc:test` | quality-engineer | security-engineer, performance-engineer |
| `/sc:explain` | learning-guide | technical-writer, 도메인 전문가 |
| `/sc:research` | deep-research-agent | 기술 전문가, learning-guide |

### 효과적인 에이전트 조합

**개발 워크플로우**:
- 웹 애플리케이션: frontend-architect + backend-architect + security-engineer + quality-engineer + devops-architect
- API 개발: backend-architect + security-engineer + technical-writer + quality-engineer
- 데이터 플랫폼: python-expert + performance-engineer + security-engineer + system-architect

**분석 워크플로우**:
- 보안 감사: security-engineer + quality-engineer + root-cause-analyst + technical-writer
- 성능 조사: performance-engineer + root-cause-analyst + system-architect + devops-architect
- 레거시 평가: refactoring-expert + system-architect + quality-engineer + security-engineer + technical-writer

**커뮤니케이션 워크플로우**:
- 기술 문서화: technical-writer + requirements-analyst + 도메인 전문가 + learning-guide
- 교육 콘텐츠: learning-guide + technical-writer + frontend-architect + quality-engineer

## 모범 사례 💡

### 시작하기 (간단한 접근법)

**자연어 우선:**
1. **목표 설명**: 도메인별 키워드를 사용한 자연어 사용
2. **자동 활성화 신뢰**: 시스템이 자동으로 적절한 에이전트로 라우팅하도록 허용
3. **패턴에서 학습**: 다양한 요청 유형에 대해 어떤 에이전트가 활성화되는지 관찰
4. **반복 및 개선**: 추가 전문 에이전트를 참여시키기 위해 구체성 추가

### 에이전트 선택 최적화

**효과적인 키워드 사용:**
- **구체적 > 일반적**: security-engineer를 위해 "login" 대신 "authentication" 사용
- **기술 용어**: 프레임워크 이름, 기술, 특정 과제 포함
- **컨텍스트 단서**: 파일 유형, 프로젝트 범위, 복잡성 지표 언급
- **품질 키워드**: 포괄적인 커버리지를 위해 "security", "performance", "accessibility" 추가

**요청 최적화 예제:**
```bash
# 일반적 (제한된 에이전트 활성화)
"로그인 기능 수정"

# 최적화됨 (다중 에이전트 조정)
"속도 제한 및 접근성 규정 준수를 갖춘 안전한 JWT 인증 구현"
# → 트리거: security-engineer + backend-architect + frontend-architect + quality-engineer
```

### 일반적인 사용 패턴

**개발 워크플로우:**
```bash
# 풀스택 기능 개발
/sc:implement "실시간 알림이 있는 반응형 사용자 대시보드"
# → frontend-architect + backend-architect + performance-engineer

# 문서화를 포함한 API 개발
/sc:create "포괄적인 문서가 있는 결제 처리를 위한 REST API"
# → backend-architect + security-engineer + technical-writer + quality-engineer

# 성능 최적화 조사
/sc:troubleshoot "사용자 경험에 영향을 미치는 느린 데이터베이스 쿼리"
# → performance-engineer + root-cause-analyst + backend-architect
```

**분석 워크플로우:**
```bash
# 보안 평가
/sc:analyze "GDPR 규정 준수 취약점에 대한 인증 시스템"
# → security-engineer + quality-engineer + requirements-analyst

# 코드 품질 검토
/sc:review "현대화 기회를 위한 레거시 코드베이스"
# → refactoring-expert + system-architect + quality-engineer + technical-writer

# 학습 및 설명
/sc:explain "실습 예제가 있는 마이크로서비스 패턴"
# → system-architect + learning-guide + technical-writer
```

### 고급 에이전트 조정

**다중 도메인 프로젝트:**
- **광범위하게 시작**: 아키텍처 에이전트를 참여시키기 위해 시스템 수준 키워드로 시작
- **구체성 추가**: 전문 에이전트를 활성화하기 위해 도메인별 필요 포함
- **품질 통합**: 보안, 성능, 테스팅 관점 자동 포함
- **문서화 포함**: 포괄적인 커버리지를 위해 학습 또는 문서화 필요 추가

**에이전트 선택 문제 해결:**

**문제: 잘못된 에이전트 활성화**
- 해결책: 더 구체적인 도메인 용어 사용
- 예제: "database optimization" → performance-engineer + backend-architect

**문제: 에이전트가 충분하지 않음**
- 해결책: 복잡성 지표 및 교차 도메인 키워드 증가
- 예제: 요청에 "security", "performance", "documentation" 추가

**문제: 에이전트가 너무 많음**
- 해결책: 구체적인 기술 용어로 주요 도메인에 집중
- 예제: 범위를 제한하기 위해 "/sc:focus backend" 사용

### 품질 중심 개발

**보안 우선 접근법:**
도메인 전문가와 함께 security-engineer를 자동으로 참여시키기 위해 개발 요청에 항상 보안 고려사항을 포함하세요.

**성능 통합:**
처음부터 performance-engineer 조정을 보장하기 위해 성능 키워드("빠른", "효율적", "확장 가능")를 포함하세요.

**접근성 규정 준수:**
프론트엔드 개발에서 접근성 검증을 자동으로 포함하기 위해 "accessible", "WCAG" 또는 "inclusive"를 사용하세요.

**문서화 문화:**
자동 technical-writer 포함 및 지식 전달을 위해 요청에 "documented", "explained" 또는 "tutorial"을 추가하세요.

---

## 에이전트 지능 이해 🧠

### 에이전트를 효과적으로 만드는 것

**도메인 전문 지식**: 각 에이전트는 도메인별 전문 지식 패턴, 행동 접근법, 문제 해결 방법론을 가지고 있습니다.

**컨텍스트 활성화**: 에이전트는 키워드뿐만 아니라 요청 컨텍스트를 분석하여 관련성 및 참여 수준을 결정합니다.

**협업 지능**: 다중 에이전트 조정은 개별 에이전트 능력을 초과하는 시너지 효과를 생성합니다.

**적응형 학습**: 에이전트 선택은 요청 패턴 및 성공적인 조정 결과를 기반으로 향상됩니다.

### 에이전트 vs. 전통적인 AI

**전통적인 접근법**: 단일 AI가 다양한 수준의 전문 지식으로 모든 도메인을 처리
**에이전트 접근법**: 전문가들이 깊은 도메인 지식과 집중된 문제 해결로 협업

**이점**:
- 도메인별 작업에서 더 높은 정확도
- 더 정교한 문제 해결 방법론
- 전문가 검토를 통한 더 나은 품질 보증
- 조정된 다중 관점 분석

### 시스템을 신뢰하고 패턴을 이해하세요

**기대할 수 있는 것**:
- 적절한 도메인 전문가에게 자동 라우팅
- 복잡한 작업에 대한 다중 에이전트 조정
- 자동 QA 에이전트 포함을 통한 품질 통합
- 교육 에이전트 활성화를 통한 학습 기회

**걱정하지 않아도 되는 것**:
- 수동 에이전트 선택 또는 구성
- 복잡한 라우팅 규칙 또는 에이전트 관리
- 에이전트 구성 또는 조정
- 에이전트 상호작용 마이크로 관리

---

## 관련 리소스 📚

### 필수 문서
- **[명령어 가이드](commands.md)** - 최적의 에이전트 조정을 트리거하는 SuperClaude 명령어 마스터
- **[MCP 서버](mcp-servers.md)** - 전문 도구 통합을 통한 향상된 에이전트 기능
- **[세션 관리](session-management.md)** - 영구 에이전트 컨텍스트를 사용한 장기 워크플로우

### 고급 사용
- **[행동 모드](modes.md)** - 향상된 에이전트 조정을 위한 컨텍스트 최적화
- **[시작하기](../Getting-Started/quick-start.md)** - 에이전트 최적화를 위한 전문가 기법
- **[예제 모음](../Reference/examples-cookbook.md)** - 실제 에이전트 조정 패턴

### 개발 리소스
- **[기술 아키텍처](../Developer-Guide/technical-architecture.md)** - SuperClaude의 에이전트 시스템 설계 이해
- **[기여하기](../Developer-Guide/contributing-code.md)** - 에이전트 기능 및 조정 패턴 확장

---

## 에이전트 여정 🚀

**1주차: 자연스러운 사용**
자연어 설명으로 시작하세요. 어떤 에이전트가 활성화되는지, 그리고 그 이유를 주목하세요. 프로세스를 과도하게 생각하지 않고 키워드 패턴에 대한 직관을 구축하세요.

**2-3주차: 패턴 인식**
에이전트 조정 패턴을 관찰하세요. 복잡성과 도메인 키워드가 에이전트 선택에 어떻게 영향을 미치는지 이해하세요. 더 나은 조정을 위해 요청 문구를 최적화하기 시작하세요.

**2개월 이상: 전문가 조정**
최적의 에이전트 조합을 트리거하는 다중 도메인 요청을 마스터하세요. 효과적인 에이전트 선택을 위한 문제 해결 기법을 활용하세요. 복잡한 워크플로우를 위한 고급 패턴을 사용하세요.

**SuperClaude 이점:**
간단하고 자연스러운 언어 요청을 통해 조정된 응답으로 작동하는 14명의 전문 AI 전문가의 힘을 경험하세요. 구성도, 관리도 필요 없이, 필요에 따라 확장되는 지능적인 협업만 있습니다.

🎯 **지능적인 에이전트 조정을 경험할 준비가 되셨나요? `/sc:implement`로 시작하여 전문 AI 협업의 마법을 발견하세요.**

