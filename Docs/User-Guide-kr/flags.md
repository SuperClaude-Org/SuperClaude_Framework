# SuperClaude 플래그 가이드 🏁

**대부분의 플래그는 자동으로 활성화됩니다** - Claude Code가 요청의 키워드와 패턴을 기반으로 적절한 컨텍스트를 참여시키는 행동 지침을 읽습니다.

## 필수 자동 활성화 플래그 (사용 사례의 90%)

### 핵심 분석 플래그
| 플래그 | 활성화 시점 | 수행 작업 |
|------|---------------|--------------|
| `--think` | 5개 이상 파일 또는 복잡한 분석 | 표준 구조화된 분석 (~4K 토큰) |
| `--think-hard` | 아키텍처 분석, 시스템 종속성 | 향상된 도구를 사용한 심층 분석 (~10K 토큰) |
| `--ultrathink` | 중요한 시스템 재설계, 레거시 현대화 | 모든 도구를 사용한 최대 깊이 분석 (~32K 토큰) |

### MCP 서버 플래그
| 플래그 | 서버 | 목적 | 자동 트리거 |
|------|---------|---------|---------------|
| `--c7` / `--context7` | Context7 | 공식 문서, 프레임워크 패턴 | 라이브러리 임포트, 프레임워크 질문 |
| `--seq` / `--sequential` | Sequential | 다단계 추론, 디버깅 | 복잡한 디버깅, 시스템 설계 |
| `--magic` | Magic | UI 컴포넌트 생성 | `/ui` 명령어, 프론트엔드 키워드 |
| `--play` / `--playwright` | Playwright | 브라우저 테스팅, E2E 검증 | 테스팅 요청, 시각적 검증 |
| `--morph` / `--morphllm` | Morphllm | 대량 변환, 패턴 편집 | 대량 작업, 스타일 강제 |
| `--serena` | Serena | 프로젝트 메모리, 심볼 작업 | 심볼 작업, 대규모 코드베이스 |

### 행동 모드 플래그
| 플래그 | 활성화 시점 | 수행 작업 |
|------|---------------|--------------|
| `--brainstorm` | 모호한 요청, 탐색 키워드 | 협업 발견 마인드셋 |
| `--introspect` | 자기 분석, 오류 복구 | 투명성을 갖춘 추론 과정 노출 |
| `--task-manage` | >3단계, 복잡한 범위 | 위임을 통한 오케스트레이션 |
| `--orchestrate` | 다중 도구 작업, 성능 필요 | 도구 선택 및 병렬 실행 최적화 |
| `--token-efficient` / `--uc` | 컨텍스트 >75%, 효율성 필요 | 심볼 강화 커뮤니케이션, 30-50% 감소 |

### 실행 제어 플래그
| 플래그 | 활성화 시점 | 수행 작업 |
|------|---------------|--------------|
| `--loop` | "개선", "다듬기", "정제" 키워드 | 반복적 향상 사이클 |
| `--safe-mode` | 프로덕션, >85% 리소스 사용 | 최대 검증, 보수적 실행 |
| `--validate` | 위험 >0.7, 프로덕션 환경 | 실행 전 위험 평가 |
| `--delegate` | >7개 디렉토리 또는 >50개 파일 | 하위 에이전트 병렬 처리 |

## 명령어별 플래그

### 분석 명령어 플래그 (`/sc:analyze`)
| 플래그 | 목적 | 값 |
|------|---------|--------|
| `--focus` | 특정 도메인 대상 | `security`, `performance`, `quality`, `architecture` |
| `--depth` | 분석 철저함 | `quick`, `deep` |
| `--format` | 출력 형식 | `text`, `json`, `report` |

### 빌드 명령어 플래그 (`/sc:build`)
| 플래그 | 목적 | 값 |
|------|---------|--------|
| `--type` | 빌드 구성 | `dev`, `prod`, `test` |
| `--clean` | 빌드 전 정리 | 불린 |
| `--optimize` | 최적화 활성화 | 불린 |
| `--verbose` | 상세 출력 | 불린 |

### 디자인 명령어 플래그 (`/sc:design`)
| 플래그 | 목적 | 값 |
|------|---------|--------|
| `--type` | 디자인 대상 | `architecture`, `api`, `component`, `database` |
| `--format` | 출력 형식 | `diagram`, `spec`, `code` |

### 설명 명령어 플래그 (`/sc:explain`)
| 플래그 | 목적 | 값 |
|------|---------|--------|
| `--level` | 복잡성 수준 | `basic`, `intermediate`, `advanced` |
| `--format` | 설명 스타일 | `text`, `examples`, `interactive` |
| `--context` | 도메인 컨텍스트 | 모든 도메인 (예: `react`, `security`) |

### 개선 명령어 플래그 (`/sc:improve`)
| 플래그 | 목적 | 값 |
|------|---------|--------|
| `--type` | 개선 초점 | `quality`, `performance`, `maintainability`, `style`, `security` |
| `--safe` | 보수적 접근 | 불린 |
| `--interactive` | 사용자 안내 | 불린 |
| `--preview` | 실행 없이 표시 | 불린 |

### 작업 명령어 플래그 (`/sc:task`)
| 플래그 | 목적 | 값 |
|------|---------|--------|
| `--strategy` | 작업 접근법 | `systematic`, `agile`, `enterprise` |
| `--parallel` | 병렬 실행 | 불린 |
| `--delegate` | 하위 에이전트 조정 | 불린 |

### 워크플로우 명령어 플래그 (`/sc:workflow`)
| 플래그 | 목적 | 값 |
|------|---------|--------|
| `--strategy` | 워크플로우 접근법 | `systematic`, `agile`, `enterprise` |
| `--depth` | 분석 깊이 | `shallow`, `normal`, `deep` |
| `--parallel` | 병렬 조정 | 불린 |

### 문제 해결 명령어 플래그 (`/sc:troubleshoot`)
| 플래그 | 목적 | 값 |
|------|---------|--------|
| `--type` | 문제 카테고리 | `bug`, `build`, `performance`, `deployment` |
| `--trace` | 추적 분석 포함 | 불린 |
| `--fix` | 수정 적용 | 불린 |

### 정리 명령어 플래그 (`/sc:cleanup`)
| 플래그 | 목적 | 값 |
|------|---------|--------|
| `--type` | 정리 대상 | `code`, `imports`, `files`, `all` |
| `--safe` / `--aggressive` | 정리 강도 | 불린 |
| `--interactive` | 사용자 안내 | 불린 |
| `--preview` | 실행 없이 표시 | 불린 |

### 추정 명령어 플래그 (`/sc:estimate`)
| 플래그 | 목적 | 값 |
|------|---------|--------|
| `--type` | 추정 초점 | `time`, `effort`, `complexity` |
| `--unit` | 시간 단위 | `hours`, `days`, `weeks` |
| `--breakdown` | 상세 분해 | 불린 |

### 인덱스 명령어 플래그 (`/sc:index`)
| 플래그 | 목적 | 값 |
|------|---------|--------|
| `--type` | 인덱스 대상 | `docs`, `api`, `structure`, `readme` |
| `--format` | 출력 형식 | `md`, `json`, `yaml` |

### 성찰 명령어 플래그 (`/sc:reflect`)
| 플래그 | 목적 | 값 |
|------|---------|--------|
| `--type` | 성찰 범위 | `task`, `session`, `completion` |
| `--analyze` | 분석 포함 | 불린 |
| `--validate` | 완전성 검증 | 불린 |

### 스폰 명령어 플래그 (`/sc:spawn`)
| 플래그 | 목적 | 값 |
|------|---------|--------|
| `--strategy` | 조정 접근법 | `sequential`, `parallel`, `adaptive` |
| `--depth` | 분석 깊이 | `normal`, `deep` |

### Git 명령어 플래그 (`/sc:git`)
| 플래그 | 목적 | 값 |
|------|---------|--------|
| `--smart-commit` | 커밋 메시지 생성 | 불린 |
| `--interactive` | 안내 작업 | 불린 |

### 도구 선택 명령어 플래그 (`/sc:select-tool`)
| 플래그 | 목적 | 값 |
|------|---------|--------|
| `--analyze` | 도구 분석 | 불린 |
| `--explain` | 선택 설명 | 불린 |

### 테스트 명령어 플래그 (`/sc:test`)
| 플래그 | 목적 | 값 |
|------|---------|--------|
| `--coverage` | 커버리지 포함 | 불린 |
| `--type` | 테스트 유형 | `unit`, `integration`, `e2e` |
| `--watch` | 감시 모드 | 불린 |

## 고급 제어 플래그

### 범위 및 초점
| 플래그 | 목적 | 값 |
|------|---------|--------|
| `--scope` | 분석 경계 | `file`, `module`, `project`, `system` |
| `--focus` | 도메인 타겟팅 | `performance`, `security`, `quality`, `architecture`, `accessibility`, `testing` |

### 실행 제어
| 플래그 | 목적 | 값 |
|------|---------|--------|
| `--concurrency [n]` | 병렬 작업 제어 | 1-15 |
| `--iterations [n]` | 개선 사이클 | 1-10 |
| `--all-mcp` | 모든 MCP 서버 활성화 | 불린 |
| `--no-mcp` | 네이티브 도구만 | 불린 |

### 시스템 플래그 (SuperClaude 설치)
| 플래그 | 목적 | 값 |
|------|---------|--------|
| `--verbose` / `-v` | 상세 로깅 | 불린 |
| `--quiet` / `-q` | 출력 억제 | 불린 |
| `--dry-run` | 작업 시뮬레이션 | 불린 |
| `--force` | 검사 건너뛰기 | 불린 |
| `--yes` / `-y` | 자동 확인 | 불린 |
| `--install-dir` | 대상 디렉토리 | 경로 |
| `--legacy` | 레거시 스크립트 사용 | 불린 |
| `--version` | 버전 표시 | 불린 |
| `--help` | 도움말 표시 | 불린 |

## 일반적인 사용 패턴

### 프론트엔드 개발
```bash
/sc:implement "반응형 대시보드" --magic --c7
/sc:design component-library --type component --format code
/sc:test ui-components/ --magic --play
/sc:improve legacy-ui/ --magic --morph --validate
```

### 백엔드 개발
```bash
/sc:analyze api/ --focus performance --seq --think
/sc:design payment-api --type api --format spec
/sc:troubleshoot "API 타임아웃" --type performance --trace
/sc:improve auth-service --type security --validate
```

### 대규모 프로젝트
```bash
/sc:analyze . --ultrathink --all-mcp --safe-mode
/sc:workflow enterprise-system --strategy enterprise --depth deep
/sc:cleanup . --type all --safe --interactive
/sc:estimate "마이크로서비스로 마이그레이션" --type complexity --breakdown
```

### 품질 및 유지보수
```bash
/sc:improve src/ --type quality --safe --interactive
/sc:cleanup imports --type imports --preview
/sc:reflect --type completion --validate
/sc:git commit --smart-commit
```

## 플래그 상호작용

### 호환 가능한 조합
- `--think` + `--c7`: 문서를 사용한 분석
- `--magic` + `--play`: 테스팅을 사용한 UI 생성
- `--serena` + `--morph`: 변환을 사용한 프로젝트 메모리
- `--safe-mode` + `--validate`: 최대 안전성
- `--loop` + `--validate`: 검증을 통한 반복적 개선

### 충돌하는 플래그
- `--all-mcp` vs 개별 MCP 플래그 (하나만 사용)
- `--no-mcp` vs 모든 MCP 플래그 (--no-mcp 우선)
- `--safe` vs `--aggressive` (정리 강도)
- `--quiet` vs `--verbose` (출력 수준)

### 자동 활성화 관계
- `--safe-mode`는 `--uc` 및 `--validate` 자동 활성화
- `--ultrathink`는 모든 MCP 서버 자동 활성화
- `--think-hard`는 `--seq` + `--c7` 자동 활성화
- `--magic`는 UI 중심 에이전트 트리거

## 플래그 문제 해결

### 일반적인 문제
- **너무 많은 도구**: 네이티브 도구만 테스트하려면 `--no-mcp` 사용
- **작업이 너무 느림**: 출력 압축을 위해 `--uc` 추가
- **검증 차단**: 개발 중에는 `--safe-mode` 대신 `--validate` 사용
- **컨텍스트 압박**: >75% 사용 시 `--token-efficient` 자동 활성화

### 디버그 플래그
```bash
/sc:analyze . --verbose                      # 결정 로직 및 플래그 활성화 표시
/sc:select-tool "작업" --explain              # 도구 선택 과정 설명
/sc:reflect --type session --analyze         # 현재 세션 결정 검토
```

### 빠른 수정
```bash
/sc:analyze . --help                         # 명령어에 사용 가능한 플래그 표시
/sc:analyze . --no-mcp                       # 네이티브 실행만
/sc:cleanup . --preview                      # 정리될 내용 표시
```

## 플래그 우선순위 규칙

1. **안전 우선**: `--safe-mode` > `--validate` > 최적화 플래그
2. **명시적 재정의**: 사용자 플래그 > 자동 감지
3. **깊이 계층**: `--ultrathink` > `--think-hard` > `--think`
4. **MCP 제어**: `--no-mcp`가 모든 개별 MCP 플래그 재정의
5. **범위 우선순위**: system > project > module > file

## 관련 리소스
- [명령어 가이드](commands.md) - 이러한 플래그를 사용하는 명령어
- [MCP 서버 가이드](mcp-servers.md) - MCP 플래그 활성화 이해
- [세션 관리](session-management.md) - 영구 세션에서 플래그 사용

