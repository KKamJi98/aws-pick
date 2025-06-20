# AWS Pick – Codex Prompt

> 🛠️ 목적:
> CLI 도구 `awspick` 개발 및 유지보수를 위한 규칙과 요구사항 명세. 사용자는 AWS 프로파일을 빠르게 전환할 수 있어야 한다.

---

## Rules

1. README.md를 기능 변경 시 항상 갱신한다.
2. 이미 추가하거나 수정이 완료된 항목은 CHANGE.log변경된 내용에 대해 Functional Requirement or Non-Functional Requirement에 반영 시킬것
3. 변경 이력은 본 파일 상단 History 섹션에 날짜·작성자·요약을 추가한다.
4. 모든 커밋은 black, isort, pytest 품질 게이트를 통과해야 한다.
5. Conventional Commits 형식을 사용한다.
   * 예: feat(cli): 프로파일 인덱스 선택 기능 추가
6. Poetry + direnv 사용. `.envrc`에 `layout poetry` 선언.
7. `.prompt.md`는 Git에 커밋하지 않는다.
8. boto3, AWS, Python 패키징 공식 Best Practice를 준수한다.
9. 타입 힌트, 순수 함수, 모듈화로 가독성과 확장성을 유지한다.

## Requirement

## Environment
- Python 3.9+
- Poetry for dependency management
- direnv with `layout poetry`
- Formatters: black, isort
- Testing: pytest
