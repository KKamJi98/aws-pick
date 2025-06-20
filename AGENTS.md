# AWS Pick – Codex Prompt

> 🛠️ 목적:
> CLI 도구 `awspick` 개발 및 유지보수를 위한 규칙과 요구사항 명세. 사용자는 AWS 프로파일을 빠르게 전환할 수 있어야 한다.

---

## Rules

1. README.md를 기능 변경 시 항상 갱신
2. 기능 개발이나 수정이 완료된 항목과 같은 변경 이력은 CHANGELOG.md 파일에 추가할 것  
3. 모든 커밋은 black, isort, pytest 테스트를 통과해야 함
4. Conventional Commits 형식을 사용  
   - ex: `docs: update README.md`
5. uv + direnv 사용. `.envrc`에 uv 가상환경의 venv를 activate 시키도록 추가
6. boto3, AWS, Python 등의 패키징 공식 Best Practice를 준수한다.
7. 타입 힌트, 순수 함수, 모듈화로 가독성과 확장성을 유지한다.

## Requirement

## Environment

- Python 3.9+
- uv for dependency management
- direnv with `layout poetry`
- Formatters: black, isort
- Testing: pytest
