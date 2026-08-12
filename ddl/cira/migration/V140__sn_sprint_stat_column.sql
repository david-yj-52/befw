-- Flyway Migration: V140__sn_sprint_stat_column
-- SN_CIRA_SPRINT 테이블에 스프린트 상태(SPRINT_STAT) 컬럼 추가
-- Generated: 2026-05-26

-- SN_CIRA_SPRINT: 스프린트 상태 컬럼 추가 (Planned | Active | Completed)
ALTER TABLE SN_CIRA_SPRINT
    ADD COLUMN IF NOT EXISTS SPRINT_STAT VARCHAR (20) NOT NULL DEFAULT 'Planned';

COMMENT
ON COLUMN SN_CIRA_SPRINT.SPRINT_STAT IS '스프린트 상태 (Planned | Active | Completed)';

-- 스프린트 상태 기반 조회 최적화 인덱스
CREATE INDEX IF NOT EXISTS IDX_SN_CIRA_SPRINT_STAT
    ON SN_CIRA_SPRINT (PROJECT_ID, SPRINT_STAT);
