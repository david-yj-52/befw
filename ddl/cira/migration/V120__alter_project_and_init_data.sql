-- Flyway Migration: V120__alter_project_and_init_data
-- Source: Phase 1 Issue CRUD Requirements
-- Generated: 2026-05-25

-- 1. Alter SN_CIRA_PROJECT to add ISSUE_SEQUENCE and DELETED_AT
ALTER TABLE SN_CIRA_PROJECT ADD COLUMN ISSUE_SEQUENCE INT NOT NULL DEFAULT 0;
ALTER TABLE SN_CIRA_PROJECT ADD COLUMN DELETED_AT TIMESTAMP;

COMMENT ON COLUMN SN_CIRA_PROJECT.ISSUE_SEQUENCE IS '이슈 번호 채번용 시퀀스';
COMMENT ON COLUMN SN_CIRA_PROJECT.DELETED_AT IS '삭제 일시 (Soft Delete)';

-- 2. Alter SN_CIRA_ISSUE to add DELETED_AT
ALTER TABLE SN_CIRA_ISSUE ADD COLUMN DELETED_AT TIMESTAMP;
COMMENT ON COLUMN SN_CIRA_ISSUE.DELETED_AT IS '삭제 일시 (Soft Delete)';

-- 3. Initial Issue Types
INSERT INTO SN_CIRA_CIRA_ISSUE_TYPE (OBJ_ID, TYPE_NM, ICON, COLOR_CD, DESCR, SRV_ID, TENANT, TRACE_ID, USE_STAT_CD, EVNT_NM, PREV_EVNT_NM, CREATED_BY, CREATED_AT, MODIFIED_BY, MODIFIED_AT)
VALUES 
(gen_random_uuid(), 'Epic', 'epic-icon', '#904EE2', 'Large body of work', 'CIRA', 'TAS', 'INIT', 'Usable', 'Initialize', 'None', 'system', NOW(), 'system', NOW()),
(gen_random_uuid(), 'Story', 'story-icon', '#63BA3C', 'User requirement', 'CIRA', 'TAS', 'INIT', 'Usable', 'Initialize', 'None', 'system', NOW(), 'system', NOW()),
(gen_random_uuid(), 'Task', 'task-icon', '#4BADE8', 'Technical work', 'CIRA', 'TAS', 'INIT', 'Usable', 'Initialize', 'None', 'system', NOW(), 'system', NOW()),
(gen_random_uuid(), 'Bug', 'bug-icon', '#E5493A', 'Defect in system', 'CIRA', 'TAS', 'INIT', 'Usable', 'Initialize', 'None', 'system', NOW(), 'system', NOW()),
(gen_random_uuid(), 'Sub-task', 'subtask-icon', '#4BADE8', 'Part of a story/task', 'CIRA', 'TAS', 'INIT', 'Usable', 'Initialize', 'None', 'system', NOW(), 'system', NOW());
