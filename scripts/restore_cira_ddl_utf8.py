#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Restore cira DDL files: UTF-8 Korean comments + BaseModel column names."""
from __future__ import annotations

import re
from pathlib import Path

DDL_DIR = Path(__file__).resolve().parents[1] / "ddl" / "cira"

COMMON_COL = {
    "OBJ_ID": "오브젝트 ID (PK, UUID)",
    "SRV_ID": "서비스명",
    "TENANT": "테넌트",
    "TRACE_ID": "트레이스 ID",
    "USE_STAT_CD": "사용 상태",
    "EVNT_NM": "이벤트명",
    "PREV_EVNT_NM": "이전 이벤트명",
    "ACT_CD": "액션 사유 코드",
    "ACT_CM": "액션 코멘트",
    "CREATED_BY": "생성자",
    "CREATED_AT": "생성일시",
    "MODIFIED_BY": "수정자",
    "MODIFIED_AT": "수정일시",
}

# Per-table: (table_comment, {column: comment}) — domain columns only
TABLE_META: dict[str, dict[str, tuple[str, dict[str, str]]]] = {
    "01_users_and_permissions.sql": {
        "GS_USER": ("사용자 기본 정보", {
            "EMAIL": "이메일 (UK)",
            "USER_NM": "사용자명",
            "AVATAR_URL": "프로필 이미지 URL",
            "PWD_HASH": "비밀번호 해시",
        }),
        "GS_ROLE": ("역할 정의", {
            "ROLE_NM": "역할명 (Admin | Developer | Reporter | Viewer)",
            "DESCR": "역할 설명",
        }),
        "GS_USER_ROLE": ("사용자-역할 매핑", {
            "USER_ID": "사용자 ID (FK → GS_USER)",
            "ROLE_ID": "역할 ID (FK → GS_ROLE)",
        }),
        "GS_PERMISSION": ("권한 정의", {
            "PERM_NM": "권한명 (UK)",
            "DESCR": "권한 설명",
            "RESOURCE": "대상 리소스 (issue | project | sprint | board …)",
            "ACTION": "허용 액션 (create | read | update | delete)",
        }),
        "GS_ROLE_PERMISSION": ("역할-권한 매핑", {
            "ROLE_ID": "역할 ID (FK → GS_ROLE)",
            "PERMISSION_ID": "권한 ID (FK → GS_PERMISSION)",
        }),
        "GS_GROUP": ("사용자 그룹", {
            "GROUP_NM": "그룹명 (UK)",
            "DESCR": "그룹 설명",
        }),
        "GS_GROUP_MEMBER": ("그룹 멤버십", {
            "GROUP_ID": "그룹 ID (FK → GS_GROUP)",
            "USER_ID": "사용자 ID (FK → GS_USER)",
        }),
    },
    "02_projects_and_sprints.sql": {
        "SN_CIRA_PROJECT": ("프로젝트 기본 정보", {
            "PROJECT_KEY": "프로젝트 키 (UK, 예: CRA)",
            "PROJECT_NM": "프로젝트명",
            "DESCR": "프로젝트 설명",
            "PROJECT_TYPE": "프로젝트 유형 (SCRUM | KANBAN)",
            "OWNER_ID": "프로젝트 소유자 ID (FK → GS_USER)",
        }),
        "SN_CIRA_PROJECT_MEMBER": ("프로젝트 멤버", {
            "PROJECT_ID": "프로젝트 ID (FK → SN_CIRA_PROJECT)",
            "USER_ID": "사용자 ID (FK → GS_USER)",
            "ROLE": "프로젝트 내 역할 (ADMIN | DEVELOPER | REPORTER | VIEWER)",
        }),
        "SN_CIRA_SPRINT": ("스프린트", {
            "PROJECT_ID": "프로젝트 ID (FK → SN_CIRA_PROJECT)",
            "SPRINT_NM": "스프린트명",
            "GOAL": "스프린트 목표",
            "START_DT": "시작일",
            "END_DT": "종료일",
        }),
        "SN_CIRA_SPRINT_METRICS": ("스프린트 메트릭", {
            "SPRINT_ID": "스프린트 ID (FK → SN_CIRA_SPRINT)",
            "VELOCITY": "완료 스토리 포인트 (Velocity)",
            "TEAM_CAPACITY": "팀 가용 공수 (시간)",
            "PLAN_STORY_PNT": "계획 스토리 포인트",
            "COMPL_STORY_PNT": "완료 스토리 포인트",
        }),
    },
}

FILE_HEADERS = {
    "01_users_and_permissions.sql": (
        "Cira : 사용자 및 권한 관리 (Phase 1)",
        "GS_ (Global — befw-lib-core 소속)",
    ),
    "02_projects_and_sprints.sql": (
        "Cira : 프로젝트 및 스프린트 (Phase 1)",
        "SN_ (Single App — Cira 전용)",
    ),
    "03_issues_and_workflow.sql": (
        "Cira : 이슈 및 워크플로우 (Phase 1)",
        "SN_CIRA_ (Single App — Cira 전용)",
    ),
    "04_issue_relations.sql": (
        "Cira : 이슈 관계 및 의존성 (Phase 1)",
        "SN_CIRA_ (Single App — Cira 전용)",
    ),
    "05_comments_and_collaboration.sql": (
        "Cira : 댓글 및 협업 (Phase 1)",
        "SN_CIRA_ (Single App — Cira 전용)",
    ),
    "06_kanban_board.sql": (
        "Cira : 칸반 보드 (Phase 1)",
        "SN_CIRA_ (Single App — Cira 전용)",
    ),
    "07_custom_fields.sql": (
        "Cira : 커스텀 필드 — EAV 패턴 (Phase 2)",
        "SN_CIRA_ (Single App — Cira 전용)",
    ),
    "08_budget_and_time.sql": (
        "Cira : 예산 및 시간 추적 (Phase 2)",
        "SN_CIRA_ (Single App — Cira 전용)",
    ),
    "09_automation.sql": (
        "Cira : 워크플로우 자동화 엔진 (Phase 2)",
        "SN_CIRA_ (Single App — Cira 전용)",
    ),
    "10_notifications.sql": (
        "Cira : 알림 및 감사 이력 (Phase 2)",
        "SN_CIRA_ (Single App — Cira 전용)",
    ),
    "11_git_integration.sql": (
        "Cira : Git 연동 (Phase 2)",
        "SN_CIRA_ (Single App — Cira 전용)",
    ),
    "12_versions_and_milestones.sql": (
        "Cira : 버전 및 마일스톤 (Phase 2)",
        "SN_CIRA_ (Single App — Cira 전용)",
    ),
    "13_search.sql": (
        "Cira : 검색 및 저장 필터 (Phase 2)",
        "SN_CIRA_ (Single App — Cira 전용)",
    ),
}

# Extended metadata for 03-13 (loaded from original DDL semantics)
def _load_extended_meta():
    m = TABLE_META.copy()
    m["03_issues_and_workflow.sql"] = {
        "SN_CIRA_CIRA_ISSUE_TYPE": ("이슈 타입 정의", {
            "TYPE_NM": "타입명 (Epic | Story | Task | Bug | Sub-task)",
            "ICON": "아이콘 URL/클래스",
            "COLOR_CD": "색상 코드 (HEX)",
            "DESCR": "타입 설명",
        }),
        "SN_CIRA_ISSUE_STATUS": ("이슈 상태 정의", {
            "PROJECT_ID": "프로젝트 ID (NULL=전역, FK → SN_CIRA_PROJECT)",
            "STATUS_NM": "상태명 (To Do | In Progress | In Review | Done)",
            "CATEGORY": "상태 카테고리 (TODO | IN_PROGRESS | DONE)",
            "COLOR_CD": "색상 코드 (HEX)",
            "SORT_ORD": "정렬 순서",
        }),
        "SN_CIRA_ISSUE": ("이슈 기본 정보", {
            "PROJECT_ID": "프로젝트 ID (FK → SN_CIRA_PROJECT)",
            "SPRINT_ID": "스프린트 ID (FK → SN_CIRA_SPRINT)",
            "ISSUE_KEY": "이슈 키 (UK, 예: CRA-42)",
            "TITLE": "이슈 제목",
            "CONTENT": "이슈 본문",
            "ISSUE_TYPE_ID": "이슈 타입 ID (FK → SN_CIRA_CIRA_ISSUE_TYPE)",
            "STATUS_ID": "이슈 상태 ID (FK → SN_CIRA_ISSUE_STATUS)",
            "PRIORITY": "우선순위 (HIGHEST | HIGH | MEDIUM | LOW | LOWEST)",
            "STORY_PNT": "스토리 포인트",
            "ASSIGNEE_ID": "담당자 ID (FK → GS_USER)",
            "REPORTER_ID": "보고자 ID (FK → GS_USER)",
            "DUE_DT": "마감일",
            "STARTED_AT": "작업 시작일시",
            "RESOLVED_AT": "해결일시",
        }),
        "SN_CIRA_ISSUE_TRANSITION": ("이슈 상태 전이 규칙", {
            "PROJECT_ID": "프로젝트 ID (NULL=전역, FK → SN_CIRA_PROJECT)",
            "FROM_STATUS_ID": "출발 상태 ID (NULL=모든 상태, FK → SN_CIRA_ISSUE_STATUS)",
            "TO_STATUS_ID": "도착 상태 ID (FK → SN_CIRA_ISSUE_STATUS)",
            "ALLOW_YN": "전이 허용 여부 (Y | N)",
            "REQUIRED_ROLE": "전이 가능 역할 제한",
        }),
        "SN_CIRA_ISSUE_LOG": ("이슈 변경 이력", {
            "ISSUE_ID": "이슈 ID (FK → SN_CIRA_ISSUE)",
            "FIELD_NM": "변경 필드명",
            "OLD_VAL": "변경 전 값",
            "NEW_VAL": "변경 후 값",
            "CHANGED_BY": "변경자 ID (FK → GS_USER)",
            "CHANGED_AT": "변경일시",
        }),
        "SN_CIRA_ISSUE_WATCHER": ("이슈 감시자", {
            "ISSUE_ID": "이슈 ID (FK → SN_CIRA_ISSUE)",
            "USER_ID": "감시자 ID (FK → GS_USER)",
        }),
    }
    m["04_issue_relations.sql"] = {
        "SN_CIRA_ISSUE_LINK": ("이슈 간 관계", {
            "SRC_ISSUE_ID": "출발 이슈 ID (FK → SN_CIRA_ISSUE)",
            "TGT_ISSUE_ID": "도착 이슈 ID (FK → SN_CIRA_ISSUE)",
            "LINK_TYPE": "관계 유형 (BLOCKS | IS_BLOCKED_BY | RELATES_TO | DUPLICATES …)",
        }),
        "SN_CIRA_ISSUE_SUBTASK": ("부모-자식 이슈 관계", {
            "PARENT_ISSUE_ID": "부모 이슈 ID (FK → SN_CIRA_ISSUE)",
            "CHILD_ISSUE_ID": "자식 이슈 ID (FK → SN_CIRA_ISSUE)",
            "SORT_ORD": "자식 이슈 정렬 순서",
        }),
    }
    m["05_comments_and_collaboration.sql"] = {
        "SN_CIRA_COMMENT": ("이슈 댓글", {
            "ISSUE_ID": "이슈 ID (FK → SN_CIRA_ISSUE)",
            "AUTHOR_ID": "작성자 ID (FK → GS_USER)",
            "PARENT_ID": "부모 댓글 ID (대댓글, FK → SN_CIRA_COMMENT)",
            "CONTENT": "댓글 본문",
        }),
        "SN_CIRA_COMMENT_REACTION": ("댓글 반응 (이모지)", {
            "COMMENT_ID": "댓글 ID (FK → SN_CIRA_COMMENT)",
            "USER_ID": "사용자 ID (FK → GS_USER)",
            "REACTION_TYPE": "반응 유형 (THUMBS_UP | HEART | ROCKET …)",
        }),
        "SN_CIRA_ATTACHMENT": ("이슈 첨부 파일", {
            "ISSUE_ID": "이슈 ID (FK → SN_CIRA_ISSUE)",
            "COMMENT_ID": "댓글 ID (FK → SN_CIRA_COMMENT, 댓글 첨부 시)",
            "FILE_NM": "파일명",
            "FILE_PATH": "파일 저장 경로",
            "FILE_SIZE": "파일 크기 (bytes)",
            "MIME_TYPE": "MIME 타입",
        }),
    }
    m["06_kanban_board.sql"] = {
        "SN_CIRA_BOARD": ("칸반/스크럼 보드", {
            "PROJECT_ID": "프로젝트 ID (FK → SN_CIRA_PROJECT)",
            "BOARD_NM": "보드명",
            "BOARD_TYPE": "보드 유형 (KANBAN | SCRUM)",
        }),
        "SN_CIRA_BOARD_COLUMN": ("보드 컬럼", {
            "BOARD_ID": "보드 ID (FK → SN_CIRA_BOARD)",
            "STATUS_ID": "연결 이슈 상태 ID (FK → SN_CIRA_ISSUE_STATUS)",
            "COLUMN_NM": "컬럼명",
            "WIP_LIMIT": "WIP 제한 (NULL=제한 없음)",
            "SORT_ORD": "컬럼 정렬 순서",
        }),
        "SN_CIRA_ISSUE_POSITION": ("보드 내 이슈 위치 (Lexorank)", {
            "ISSUE_ID": "이슈 ID (FK → SN_CIRA_ISSUE)",
            "COLUMN_ID": "보드 컬럼 ID (FK → SN_CIRA_BOARD_COLUMN)",
            "RANK_STR": "Lexorank 정렬 문자열",
        }),
    }
    m["07_custom_fields.sql"] = {
        "SN_CIRA_CUSTOM_FIELD": ("커스텀 필드 정의", {
            "PROJECT_ID": "프로젝트 ID (NULL=전역, FK → SN_CIRA_PROJECT)",
            "FIELD_NM": "필드명",
            "FIELD_TYPE": "필드 유형 (TEXT | NUMBER | DATE | SELECT …)",
            "REQUIRED_YN": "필수 여부 (Y | N)",
            "OPTIONS": "SELECT/MULTI_SELECT 선택지 목록 (JSONB)",
            "SORT_ORD": "정렬 순서",
        }),
        "SN_CIRA_ISSUE_CF_VALUE": ("이슈별 커스텀 필드 값", {
            "ISSUE_ID": "이슈 ID (FK → SN_CIRA_ISSUE)",
            "CUSTOM_FIELD_ID": "커스텀 필드 ID (FK → SN_CIRA_CUSTOM_FIELD)",
            "VAL_TEXT": "텍스트 값",
            "VAL_NUMBER": "숫자 값",
            "VAL_DT": "날짜 값",
            "VAL_JSON": "복합 값 (JSONB)",
        }),
    }
    m["08_budget_and_time.sql"] = {
        "SN_CIRA_PROJECT_BUDGET": ("프로젝트 예산", {
            "PROJECT_ID": "프로젝트 ID (FK → SN_CIRA_PROJECT)",
            "TOTAL_BUDGET": "총 예산",
            "BUDGET_CATEGORY": "예산 카테고리 (TOTAL | DEVELOPMENT | DESIGN | QA | OTHER)",
            "CURRENCY": "통화 코드 (KRW | USD …)",
            "FISCAL_YEAR": "회계 연도",
        }),
        "SN_CIRA_HOURLY_RATE": ("사용자별 시급", {
            "USER_ID": "사용자 ID (FK → GS_USER)",
            "HOURLY_RATE": "시급",
            "CURRENCY": "통화 코드",
            "EFF_FROM_DT": "적용 시작일",
            "EFF_TO_DT": "적용 종료일 (NULL=현재 적용 중)",
        }),
        "SN_CIRA_TIME_LOG": ("시간 기록", {
            "ISSUE_ID": "이슈 ID (FK → SN_CIRA_ISSUE)",
            "USER_ID": "사용자 ID (FK → GS_USER)",
            "LOG_HRS": "기록 시간 (시간 단위, 0 < LOG_HRS ≤ 24)",
            "LOG_DT": "작업 날짜",
            "DESCR": "작업 설명",
        }),
        "SN_CIRA_EXPENSE": ("지출 기록", {
            "PROJECT_ID": "프로젝트 ID (FK → SN_CIRA_PROJECT)",
            "ISSUE_ID": "이슈 ID (FK → SN_CIRA_ISSUE, 선택)",
            "AMOUNT": "지출 금액",
            "CURRENCY": "통화 코드",
            "CATEGORY": "지출 카테고리 (LABOR | SOFTWARE | INFRA | EQUIPMENT | OTHER)",
            "EXPENSE_DT": "지출 날짜",
            "DESCR": "지출 설명",
        }),
    }
    m["09_automation.sql"] = {
        "SN_CIRA_AUTO_RULE": ("워크플로우 자동화 규칙", {
            "PROJECT_ID": "프로젝트 ID (NULL=전역, FK → SN_CIRA_PROJECT)",
            "RULE_NM": "규칙명",
            "DESCR": "규칙 설명",
            "TRIGGER_TYPE": "트리거 유형 (ISSUE_CREATED | STATUS_CHANGED …)",
            "COND": "트리거 조건 (JSONB)",
            "ACTION": "실행 액션 (JSONB)",
        }),
        "SN_CIRA_AUTO_EXECUTION": ("자동화 실행 기록", {
            "RULE_ID": "자동화 규칙 ID (FK → SN_CIRA_AUTO_RULE)",
            "ISSUE_ID": "연관 이슈 ID (FK → SN_CIRA_ISSUE, 선택)",
            "EXEC_STAT": "실행 결과 (SUCCESS | FAILED | SKIPPED)",
            "ERR_MSG": "오류 메시지",
            "EXECUTED_AT": "실행일시",
        }),
    }
    m["10_notifications.sql"] = {
        "SN_CIRA_NOTIFICATION": ("알림", {
            "USER_ID": "수신자 ID (FK → GS_USER)",
            "NOTIF_TYPE": "알림 유형 (ISSUE_ASSIGNED | COMMENT_ADDED …)",
            "TITLE": "알림 제목",
            "MSG": "알림 내용",
            "RESOURCE_TYPE": "연관 리소스 유형 (ISSUE | PROJECT | SPRINT | COMMENT)",
            "RESOURCE_ID": "연관 리소스 ID",
            "READ_YN": "읽음 여부 (Y | N)",
        }),
        "SN_CIRA_NOTIF_PREF": ("알림 수신 설정", {
            "USER_ID": "사용자 ID (FK → GS_USER)",
            "CHANNEL": "알림 채널 (EMAIL | IN_APP | SLACK | WEBHOOK)",
            "EVENT_TYPE": "이벤트 유형 (ISSUE_ASSIGNED | ALL …)",
            "ENABLED_YN": "알림 활성 여부 (Y | N)",
        }),
        "SN_CIRA_AUDIT_LOG": ("감사 로그 (월별 파티셔닝)", {
            "ACTION_TYPE": "액션 유형 (CREATE | UPDATE | DELETE | LOGIN | LOGOUT)",
            "ACTOR_ID": "행위자 ID (FK → GS_USER)",
            "RESOURCE_TYPE": "리소스 유형 (ISSUE | PROJECT | USER …)",
            "RESOURCE_ID": "리소스 ID",
            "OLD_SNAPSHOT": "변경 전 데이터 스냅샷 (JSONB)",
            "NEW_SNAPSHOT": "변경 후 데이터 스냅샷 (JSONB)",
            "IP_ADDR": "요청 IP 주소",
            "USER_AGENT": "요청 User-Agent",
        }),
    }
    m["11_git_integration.sql"] = {
        "SN_CIRA_GIT_REPO": ("Git 저장소 정보", {
            "PROJECT_ID": "프로젝트 ID (FK → SN_CIRA_PROJECT)",
            "PROVIDER": "Git 공급자 (GITHUB | GITLAB | BITBUCKET)",
            "REPO_URL": "저장소 URL",
            "ACCESS_TOKEN_ENC": "암호화된 액세스 토큰",
            "DEFAULT_BRANCH": "기본 브랜치명",
        }),
        "SN_CIRA_GIT_COMMIT": ("Git 커밋 정보", {
            "REPO_ID": "저장소 ID (FK → SN_CIRA_GIT_REPO)",
            "ISSUE_ID": "연관 이슈 ID (FK → SN_CIRA_ISSUE, 선택)",
            "COMMIT_HASH": "커밋 해시 (40자)",
            "MSG": "커밋 메시지",
            "AUTHOR_NM": "커밋 작성자명",
            "AUTHOR_EMAIL": "커밋 작성자 이메일",
            "COMMIT_DT": "커밋 일시",
        }),
        "SN_CIRA_GIT_PR": ("Git Pull Request 정보", {
            "REPO_ID": "저장소 ID (FK → SN_CIRA_GIT_REPO)",
            "ISSUE_ID": "연관 이슈 ID (FK → SN_CIRA_ISSUE, 선택)",
            "PR_NO": "PR 번호 (저장소 내 고유)",
            "TITLE": "PR 제목",
            "DESCR": "PR 설명",
            "PR_STAT": "PR 상태 (OPEN | MERGED | CLOSED | DRAFT)",
            "SRC_BRANCH": "소스 브랜치",
            "TGT_BRANCH": "대상 브랜치",
            "AUTHOR_NM": "PR 작성자명",
            "AUTHOR_EMAIL": "PR 작성자 이메일",
            "MERGED_AT": "병합일시",
            "CLOSED_AT": "닫힌 일시",
        }),
    }
    m["12_versions_and_milestones.sql"] = {
        "SN_CIRA_VERSION": ("릴리스 버전", {
            "PROJECT_ID": "프로젝트 ID (FK → SN_CIRA_PROJECT)",
            "VERSION_NM": "버전명 (UK per project)",
            "DESCR": "버전 설명",
            "PLAN_REL_DT": "릴리스 예정일",
            "RELEASED_DT": "실제 릴리스일",
        }),
        "SN_CIRA_ISSUE_VERSION": ("이슈-버전 매핑", {
            "ISSUE_ID": "이슈 ID (FK → SN_CIRA_ISSUE)",
            "VERSION_ID": "버전 ID (FK → SN_CIRA_VERSION)",
            "REL_TYPE": "관계 유형 (FIX_VERSION | AFFECTS_VERSION)",
        }),
        "SN_CIRA_MILESTONE": ("마일스톤", {
            "PROJECT_ID": "프로젝트 ID (FK → SN_CIRA_PROJECT)",
            "MILESTONE_NM": "마일스톤명",
            "DESCR": "마일스톤 설명",
            "DUE_DT": "목표 완료일",
        }),
        "SN_CIRA_MILESTONE_ISSUE": ("마일스톤-이슈 매핑", {
            "MILESTONE_ID": "마일스톤 ID (FK → SN_CIRA_MILESTONE)",
            "ISSUE_ID": "이슈 ID (FK → SN_CIRA_ISSUE)",
        }),
    }
    m["13_search.sql"] = {
        "SN_CIRA_SAVED_FILTER": ("저장된 검색 필터", {
            "USER_ID": "소유자 ID (FK → GS_USER)",
            "PROJECT_ID": "프로젝트 ID (NULL=전역, FK → SN_CIRA_PROJECT)",
            "FILTER_NM": "필터명",
            "JQL_QUERY": "JQL 쿼리 문자열",
            "SHARED_YN": "공유 여부 (Y | N)",
        }),
        "SN_CIRA_ISSUE_SEARCH_IDX": ("이슈 Full-Text Search 인덱스", {
            "ISSUE_ID": "이슈 ID (UK, FK → SN_CIRA_ISSUE)",
            "SEARCH_VEC": "PostgreSQL TSVECTOR (GIN 인덱스 대상)",
        }),
    }
    return m


TABLE_META = _load_extended_meta()


def structural_fix(text: str) -> str:
    text = text.replace("PRV_EVNT_NM", "PREV_EVNT_NM")
    text = text.replace("ACT_RSN_CIRA_CD", "ACT_CD")
    text = text.replace("ACT_RSN_CD", "ACT_CD")
    text = text.replace("SN_CIRA_CIRA_PROJECT (OBJ_ID)", "SN_CIRA_PROJECT (OBJ_ID)")
    text = text.replace("REFERENCES SN_CIRA_CIRA_PROJECT", "REFERENCES SN_CIRA_PROJECT")
    text = text.replace("FK → SN_CIRA_CIRA_PROJECT", "FK → SN_CIRA_PROJECT")
    text = text.replace("â€¦", "…")
    text = re.sub(
        r"RESOURCE\s+VARCHAR\(50\)\s+NOT NULL,\s*--[^\n]*ACTION\s+VARCHAR",
        "RESOURCE     VARCHAR(50)  NOT NULL,  -- issue | project | sprint | board …\n    ACTION       VARCHAR",
        text,
    )
    return text


def strip_duplicate_headers(text: str) -> str:
    return re.sub(
        r"\n-- ={20,}\n-- DB\s+: PostgreSQL\n-- ={20,}\n",
        "\n",
        text,
    ).strip()


def fix_section_headers(text: str, meta: dict) -> str:
    for tname, (tkr, _) in meta.items():
        text = re.sub(
            rf"^(-- \d+\. {re.escape(tname)})([^\n]*)",
            rf"\1 ({tkr})",
            text,
            flags=re.MULTILINE,
        )
    return text


def polish_body(text: str, filename: str) -> str:
    """Fix corrupted inline comments and lines merged by encoding damage."""
    pairs: list[tuple[str, str]] = [
        (r"-- \?\? CRA, TAS", "-- 예: CRA, TAS"),
        (r"-- \?\? CRA-42", "-- 예: CRA-42"),
        (r"PROJECT_ID\s+VARCHAR\(100\),\s*-- NULL = [^\n]+\n\s+STATUS_NM",
         "PROJECT_ID      VARCHAR(100),                                -- NULL = 전역 상태\n    STATUS_NM"),
        (r"PROJECT_ID\s+VARCHAR\(100\), -- NULL = [^\n]+\n\s+FROM_STATUS",
         "PROJECT_ID      VARCHAR(100), -- NULL = 전역 규칙\n    FROM_STATUS"),
        (r"FROM_STATUS_ID\s+VARCHAR\(100\), -- NULL = [^\n]+\n\s+TO_STATUS",
         "FROM_STATUS_ID  VARCHAR(100), -- NULL = 모든 상태\n    TO_STATUS"),
        (r"PROJECT_ID\s+VARCHAR\(100\),\s*-- NULL = [^\n]+\n\s+FIELD_NM",
         "PROJECT_ID      VARCHAR(100),          -- NULL = 전역 필드\n    FIELD_NM"),
        (r"OPTIONS\s+JSONB,\s*-- SELECT / MULTI_SELECT [^\n]+\n\s+SORT_ORD",
         "OPTIONS         JSONB,                 -- SELECT / MULTI_SELECT 선택지 목록\n    SORT_ORD"),
        (r"VAL_JSON\s+JSONB, -- SELECT[^\n]*-- BaseModel",
         "VAL_JSON        JSONB, -- SELECT | MULTI_SELECT | USER 등 복합 값\n    -- BaseModel"),
        (r"PARENT_ID\s+VARCHAR\(100\),\s*-- [^\n]+\n\s+CONTENT",
         "PARENT_ID       VARCHAR(100),                           -- 부모 댓글 ID (대댓글)\n    CONTENT"),
        (r"WIP_LIMIT\s+SMALLINT, -- NULL = [^\n]+\n\s+SORT_ORD",
         "WIP_LIMIT       SMALLINT, -- NULL = 제한 없음\n    SORT_ORD"),
        (r"RANK_STR\s+VARCHAR\(100\) NOT NULL, -- Lexorank[^\n]*-- BaseModel",
         "RANK_STR        VARCHAR(100) NOT NULL, -- Lexorank 정렬 문자열\n    -- BaseModel"),
        (r"NOTIF_TYPE\s+VARCHAR\(50\)\s+NOT NULL, -- ISSUE_ASSIGNED[^\n]*TITLE\s+VARCHAR\(300\)",
         "NOTIF_TYPE      VARCHAR(50)  NOT NULL, -- ISSUE_ASSIGNED | COMMENT_ADDED | STATUS_CHANGED | MENTIONED | SPRINT_STARTED …\n    TITLE           VARCHAR(300)"),
        (r"RESOURCE_TYPE\s+VARCHAR\(50\)\s+NOT NULL, -- ISSUE[^\n]*RESOURCE_ID\s+VARCHAR\(100\)",
         "RESOURCE_TYPE   VARCHAR(50)  NOT NULL, -- ISSUE | PROJECT | USER | ROLE …\n    RESOURCE_ID     VARCHAR(100)"),
        (r"EVENT_TYPE\s+VARCHAR\(50\)\s+NOT NULL, -- ISSUE_ASSIGNED[^\n]*\| ALL",
         "EVENT_TYPE      VARCHAR(50)  NOT NULL, -- ISSUE_ASSIGNED | COMMENT_ADDED | … | ALL"),
        (r"PROJECT_ID\s+VARCHAR\(100\),\s*-- NULL = [^\n]+\n\s+RULE_NM",
         "PROJECT_ID      VARCHAR(100),                           -- NULL = 전역 규칙\n    RULE_NM"),
        (r"COND\s+JSONB,\s*-- [^\n]+\n\s+ACTION",
         'COND            JSONB,                                  -- 트리거 조건 (예: {"status":"In Review"})\n    ACTION'),
        (r"ACTION\s+JSONB\s+NOT NULL,\s*-- [^\n]+\n\s+-- BaseModel \(USE_STAT_CD",
         'ACTION          JSONB        NOT NULL,                  -- 실행 액션 (예: {"type":"ASSIGN"})\n    -- BaseModel (USE_STAT_CD로 활성/비활성 관리)'),
        (r"USE_STAT_CD\s+VARCHAR\(40\)\s+NOT NULL DEFAULT 'Usable', -- Usable\([^\n]+\n\s+EVNT_NM",
         "USE_STAT_CD     VARCHAR(40)  NOT NULL DEFAULT 'Usable', -- Usable(활성) | Disabled(비활성)\n    EVNT_NM"),
        (r"ACCESS_TOKEN_ENC TEXT,\s*-- [^\n]+\n\s+DEFAULT_BRANCH",
         "ACCESS_TOKEN_ENC TEXT,                                   -- 암호화된 액세스 토큰\n    DEFAULT_BRANCH"),
        (r"-- BaseModel \(USE_STAT_CD [^\n]+\n\s+SRV_ID\s+VARCHAR\(50\)\s+NOT NULL DEFAULT 'CIRA',\n\s+TENANT\s+VARCHAR\(50\)\s+NOT NULL DEFAULT 'TAS',\n\s+TRACE_ID\s+VARCHAR\(100\) NOT NULL,\n\s+USE_STAT_CD\s+VARCHAR\(40\)\s+NOT NULL DEFAULT 'Usable',\n\s+EVNT_NM",
         "-- BaseModel (USE_STAT_CD로 활성/비활성 관리)\n    SRV_ID           VARCHAR(50)  NOT NULL DEFAULT 'CIRA',\n    TENANT           VARCHAR(50)  NOT NULL DEFAULT 'TAS',\n    TRACE_ID         VARCHAR(100) NOT NULL,\n    USE_STAT_CD      VARCHAR(40)  NOT NULL DEFAULT 'Usable',\n    EVNT_NM"),
        (r"PROJECT_ID\s+VARCHAR\(100\), -- NULL = [^\n]+\n\s+FILTER_NM",
         "PROJECT_ID      VARCHAR(100), -- NULL = 전역 필터\n    FILTER_NM"),
        (r"PREV_EVNT_NM\s+VARCHAR\(100\),\n\s+ACT_CD VARCHAR",
         "PREV_EVNT_NM     VARCHAR(100),\n    ACT_CD       VARCHAR"),
        (r"PREV_EVNT_NM VARCHAR\(100\),\n\s+ACT_CD VARCHAR",
         "PREV_EVNT_NM VARCHAR(100),\n    ACT_CD       VARCHAR"),
        (r"PREV_EVNT_NM\s+VARCHAR\(100\),\n\s+ACT_CD\s+VARCHAR",
         "PREV_EVNT_NM     VARCHAR(100),\n    ACT_CD       VARCHAR"),
    ]
    for pat, repl in pairs:
        text = re.sub(pat, repl, text)

    if filename == "10_notifications.sql":
        text = re.sub(
            r"^-- [^\n]*파티션[^\n]*\n",
            "-- 파티션 예시 (월별 분리)\n",
            text,
            count=1,
            flags=re.MULTILINE,
        )
        text = re.sub(
            r"^-- [^\n]*\n(?=CREATE TABLE SN_CIRA_AUDIT_LOG_2026)",
            "-- 파티션 예시 (월별 분리)\n",
            text,
            count=1,
            flags=re.MULTILINE,
        )

    if filename == "13_search.sql":
        text = re.sub(
            r"-- 2\. SN_CIRA_ISSUE_SEARCH_IDX[^\n]*\n--[^\n]*\n",
            "-- 2. SN_CIRA_ISSUE_SEARCH_IDX (PostgreSQL FTS 인덱스)\n"
            "--    Elasticsearch 도입 시 대체 / 병행 사용 가능\n",
            text,
            count=1,
        )
        text = re.sub(
            r"-- GIN [^\n]+\n",
            "-- GIN 인덱스 (Full-Text Search 최적화)\n",
            text,
            count=1,
        )
        text = re.sub(
            r"-- 3\. FTS [^\n]+\n",
            "-- 3. FTS 자동 갱신 트리거\n",
            text,
            count=1,
        )
        text = re.sub(
            r"-- \d+\. 파티션 [^\n]+\n",
            "-- 파티션 예시 (월별 분리)\n",
            text,
            count=1,
        )

    return text


def extract_body(path: Path) -> str:
    lines = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        s = line.strip()
        if s.startswith("COMMENT ON"):
            continue
        if re.match(r"^-- Cira\s*:", line) or line.strip().startswith("-- Prefix:"):
            continue
        if re.match(r"^-- =+$", line.strip()):
            continue
        if line.strip() == "-- DB    : PostgreSQL":
            continue
        if "BaseModel 공통" in line or "테이블 Prefix" in line or "전체 실행" in line:
            continue
        lines.append(line)
    body = structural_fix("\n".join(lines))
    return strip_duplicate_headers(body)


def emit_comments(table: str, table_kr: str, cols: dict[str, str]) -> list[str]:
    out = [f"COMMENT ON TABLE {table} IS '{table_kr}';"]
    for col, desc in cols.items():
        out.append(f"COMMENT ON COLUMN {table}.{col} IS '{desc}';")
    for col, desc in COMMON_COL.items():
        out.append(f"COMMENT ON COLUMN {table}.{col} IS '{desc}';")
    return out


def rebuild_file(filename: str) -> None:
    path = DDL_DIR / filename
    body = extract_body(path)
    meta = TABLE_META.get(filename, {})
    body = polish_body(body, filename)
    body = fix_section_headers(body, meta)
    path.write_text(rebuild_with_comments(body, filename), encoding="utf-8")
    print(f"Restored {filename}")


def rebuild_with_comments(body: str, filename: str) -> str:
    header = FILE_HEADERS.get(filename, ("Cira DDL", "SN_CIRA_"))
    meta = TABLE_META.get(filename, {})
    lines_out = [
        "-- ============================================================",
        f"-- {header[0]}",
        f"-- Prefix: {header[1]}",
        "-- DB    : PostgreSQL",
        "-- ============================================================",
        "",
    ]

    parts = re.split(r"(?=-- -{10,})", body)
    for part in parts:
        part = part.strip()
        if not part:
            continue
        lines_out.append(part)
        m = re.search(r"CREATE TABLE (\w+)", part)
        if m and m.group(1) in meta:
            tname = m.group(1)
            tkr, cols = meta[tname]
            lines_out.append("")
            lines_out.extend(emit_comments(tname, tkr, cols))
        lines_out.append("")

    return "\n".join(lines_out).rstrip() + "\n"


def write_00_run_all():
    content = """-- ============================================================
-- Cira DDL 전체 실행 스크립트
-- DB   : PostgreSQL
-- 실행  : psql -U <user> -d <database> -f 00_run_all.sql
--
-- 테이블 Prefix 규칙
--   GS_ : Global 전역 테이블 (befw-lib-core 소속, 서비스 공통)
--   SN_ : Single App 전용 테이블 (Cira 앱 전용)
--
-- BaseModel 공통 컬럼 (전 테이블 적용)
--   OBJ_ID, SRV_ID, TENANT, TRACE_ID, USE_STAT_CD,
--   EVNT_NM, PREV_EVNT_NM, ACT_CD, ACT_CM,
--   CREATED_BY, CREATED_AT, MODIFIED_BY, MODIFIED_AT
-- ============================================================

-- [ Phase 1 : 핵심 구조 ]
\\ir 01_users_and_permissions.sql    -- GS_USER, GS_ROLE, GS_USER_ROLE, GS_PERMISSION, GS_ROLE_PERMISSION, GS_GROUP, GS_GROUP_MEMBER
\\ir 02_projects_and_sprints.sql     -- SN_CIRA_PROJECT, SN_CIRA_PROJECT_MEMBER, SN_CIRA_SPRINT, SN_CIRA_SPRINT_METRICS
\\ir 03_issues_and_workflow.sql      -- SN_CIRA_ISSUE_TYPE, SN_CIRA_ISSUE_STATUS, SN_CIRA_ISSUE, ...
\\ir 04_issue_relations.sql          -- SN_CIRA_ISSUE_LINK, SN_CIRA_ISSUE_SUBTASK
\\ir 05_comments_and_collaboration.sql -- SN_CIRA_COMMENT, SN_CIRA_COMMENT_REACTION, SN_CIRA_ATTACHMENT
\\ir 06_kanban_board.sql             -- SN_CIRA_BOARD, SN_CIRA_BOARD_COLUMN, SN_CIRA_ISSUE_POSITION

-- [ Phase 2 : 확장 기능 ]
\\ir 07_custom_fields.sql            -- SN_CIRA_CUSTOM_FIELD, SN_CIRA_ISSUE_CF_VALUE
\\ir 08_budget_and_time.sql          -- SN_CIRA_PROJECT_BUDGET, SN_CIRA_HOURLY_RATE, SN_CIRA_TIME_LOG, SN_CIRA_EXPENSE
\\ir 09_automation.sql               -- SN_CIRA_AUTO_RULE, SN_CIRA_AUTO_EXECUTION
\\ir 10_notifications.sql            -- SN_CIRA_NOTIFICATION, SN_CIRA_NOTIF_PREF, SN_CIRA_AUDIT_LOG
\\ir 11_git_integration.sql          -- SN_CIRA_GIT_REPO, SN_CIRA_GIT_COMMIT, SN_CIRA_GIT_PR
\\ir 12_versions_and_milestones.sql  -- SN_CIRA_VERSION, SN_CIRA_ISSUE_VERSION, SN_CIRA_MILESTONE, SN_CIRA_MILESTONE_ISSUE
\\ir 13_search.sql                   -- SN_CIRA_SAVED_FILTER, SN_CIRA_ISSUE_SEARCH_IDX
"""
    (DDL_DIR / "00_run_all.sql").write_text(content, encoding="utf-8")
    print("Restored 00_run_all.sql")


def main():
    write_00_run_all()
    for fn in sorted(TABLE_META.keys()):
        rebuild_file(fn)
    print("Done.")


if __name__ == "__main__":
    main()
