-- ============================================================
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
\ir
01_users_and_permissions.sql    -- GS_USER, GS_ROLE, GS_USER_ROLE, GS_PERMISSION, GS_ROLE_PERMISSION, GS_GROUP, GS_GROUP_MEMBER
\ir 02_projects_and_sprints.sql     -- SN_CIRA_PROJECT, SN_CIRA_PROJECT_MEMBER, SN_CIRA_SPRINT, SN_CIRA_SPRINT_METRICS
\ir 03_issues_and_workflow.sql      -- SN_CIRA_ISSUE_TYPE, SN_CIRA_ISSUE_STATUS, SN_CIRA_ISSUE, ...
\ir 04_issue_relations.sql          -- SN_CIRA_ISSUE_LINK, SN_CIRA_ISSUE_SUBTASK
\ir 05_comments_and_collaboration.sql -- SN_CIRA_COMMENT, SN_CIRA_COMMENT_REACTION, SN_CIRA_ATTACHMENT
\ir 06_kanban_board.sql             -- SN_CIRA_BOARD, SN_CIRA_BOARD_COLUMN, SN_CIRA_ISSUE_POSITION

-- [ Phase 2 : 확장 기능 ]
\ir 07_custom_fields.sql            -- SN_CIRA_CUSTOM_FIELD, SN_CIRA_ISSUE_CF_VALUE
\ir 08_budget_and_time.sql          -- SN_CIRA_PROJECT_BUDGET, SN_CIRA_HOURLY_RATE, SN_CIRA_TIME_LOG, SN_CIRA_EXPENSE
\ir 09_automation.sql               -- SN_CIRA_AUTO_RULE, SN_CIRA_AUTO_EXECUTION
\ir 10_notifications.sql            -- SN_CIRA_NOTIFICATION, SN_CIRA_NOTIF_PREF, SN_CIRA_AUDIT_LOG
\ir 11_git_integration.sql          -- SN_CIRA_GIT_REPO, SN_CIRA_GIT_COMMIT, SN_CIRA_GIT_PR
\ir 12_versions_and_milestones.sql  -- SN_CIRA_VERSION, SN_CIRA_ISSUE_VERSION, SN_CIRA_MILESTONE, SN_CIRA_MILESTONE_ISSUE
\ir 13_search.sql                   -- SN_CIRA_SAVED_FILTER, SN_CIRA_ISSUE_SEARCH_IDX
