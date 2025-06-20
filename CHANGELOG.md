# Changelog
## [1.3.5] - 2025-06-21
### Added
- Document shell function to use `aws_pick.py` directly in README.
## [1.3.4] - 2025-06-21
### Changed
- CLI now prints menus and logs to stderr, leaving only the export command on stdout.
### Added
- Graceful exit when no selection is made.
## [1.3.3] - 2025-06-20
### Fixed
- Run tests in CI using uv virtual environment
## [1.3.2] - 2025-06-20
### Fixed
- CI workflow uses virtual environment binaries explicitly

## [1.3.1] - 2025-06-13
### Added
- Example shell wrapper function to apply profiles immediately
### Fixed
- CI test workflow activates uv virtual environment

## [1.3.0] - 2025-06-12
### Added
- GitHub Actions workflows for testing and automated releases
### Changed
- Migrate package management from Poetry to uv, update docs and environment


## [1.2.1] - 2025-06-11
### Changed
- CLI prints the export command by default; `--export-command` is no longer required

## [1.2.0] - 2025-06-11
### Added
- `--export-command` option prints the shell command to apply the profile
### Changed
- README instructions updated; shell configs are no longer sourced automatically

## [1.1.0] - 2025-06-10
### Added
- Automatically source the appropriate shell rc file after profile update.
- Limit rc file backups to the five most recent copies.

## [1.0.1] - 2025-06-09
### Added
- Support for multiple shells (bash, zsh, fish)
- Enhanced error handling and documentation

## [1.0.0] - 2025-06-05
### Functional Requirements
- `~/.aws/config` 파일에서 프로파일 목록을 읽어 번호와 이름으로 출력한다.
- 번호 또는 이름 입력을 모두 허용한다.
- 잘못된 입력은 재입력을 요구한다.
- 선택된 프로파일을 쉘 설정 파일에서 `export AWS_PROFILE` 줄로 치환하거나 추가한다.
- 원본 설정 파일을 `.bak-YYYYMMDDHHMMSS` 형식으로 백업한다.
- 같은 프로파일을 선택할 경우 파일을 수정하지 않는다.

### Non-Functional Requirements
- Python 3.9 이상.
- 외부 의존성으로 `boto3`, `tabulate` 사용.
- 입력 검증과 파일 패치 로직에 대한 100% 단위 테스트 커버리지.
- `logging` 모듈을 사용하여 INFO/ERROR 단계 로깅.
- Poetry `scripts`에 `awspick` CLI 엔트리포인트 정의.
- 프로젝트 루트에 단일 파일 런처 `aws_pick.py` 제공.

### History
- 2025-06-07 – kkamji – 에러 처리 강화 및 주석 개선
- 2025-06-06 – kkamji – `.prompt.md` GitHub 제외 명확화
- 2025-06-05 – kkamji – 단일 파일 런처 추가 및 임포트 경로 수정
- 2025-06-05 – kkamji – 프로젝트 및 CLI 이름 변경
- 2025-06-05 – kkamji – 초기 규칙/요구사항/히스토리 작성
