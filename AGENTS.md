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

---

## Current Requirement

---

## Functional Requirement (Finished)

* `~/.aws/config` 파일에서 프로파일 목록을 읽어 번호와 이름으로 출력한다.
* 번호 또는 이름 입력을 모두 허용한다.
* 잘못된 입력(범위 밖 숫자, 존재하지 않는 이름, 빈 문자열)은 재입력을 요구한다.
* 선택된 프로파일을 `~/.zshrc` 파일의 `export AWS_PROFILE=<선택>` 줄로 치환(없으면 추가)한다.
* 원본 `~/.zshrc`는 `.bak-YYYYMMDDHHMMSS` 형식으로 백업한다.
* 같은 프로파일을 선택할 경우 파일을 수정하지 않는다(멱등성).

---

## Non-Functional Requirement (Finished)

* Python 3.9 이상.
* 외부 의존성은 `boto3`, `tabulate` 사용.
* 입력 검증과 파일 패치 로직에 대해 100% 단위 테스트 커버리지를 확보한다.
* `logging` 모듈을 사용해 INFO 단계, ERROR 단계 로깅한다.
* Poetry `scripts`에 `awspick` CLI 엔트리포인트를 정의한다.
* 프로젝트 루트에 `aws_pick.py` 단일 파일 런처를 제공한다.

---

## History

* 2025-06-07 – kkamji – 에러 처리 강화 및 주석 개선
* 2025-06-06 – kkamji – `.prompt.md` GitHub 제외 명확화
* 2025-06-05 – kkamji – 단일 파일 런처 추가 및 임포트 경로 수정
* 2025-06-05 – kkamji – 프로젝트 및 CLI 이름 변경
* 2025-06-05 – kkamji – 초기 규칙/요구사항/히스토리 작성
