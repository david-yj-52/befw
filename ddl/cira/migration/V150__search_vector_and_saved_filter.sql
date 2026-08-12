-- Flyway Migration: V150__search_vector_and_saved_filter
-- SN_CIRA_ISSUE FTS 검색 벡터 추가 + GIN 인덱스 + 트리거
-- Generated: 2026-05-27

-- SN_CIRA_ISSUE: tsvector 검색 컬럼 추가
ALTER TABLE SN_CIRA_ISSUE
    ADD COLUMN IF NOT EXISTS SEARCH_VECTOR TSVECTOR;

-- GIN 인덱스 (FTS 고속 검색)
CREATE INDEX IF NOT EXISTS idx_sn_cira_issue_search
    ON SN_CIRA_ISSUE USING GIN(SEARCH_VECTOR);

-- 검색 벡터 자동 갱신 함수
CREATE
OR REPLACE FUNCTION update_issue_search_vector()
RETURNS TRIGGER AS $$
BEGIN
  NEW.SEARCH_VECTOR
:= to_tsvector('simple',
    COALESCE(NEW.TITLE, '') || ' ' || COALESCE(NEW.CONTENT, ''));
RETURN NEW;
END;
$$
LANGUAGE plpgsql;

-- 트리거 (INSERT/UPDATE 시 자동 갱신)
DROP TRIGGER IF EXISTS issue_search_vector_update ON SN_CIRA_ISSUE;
CREATE TRIGGER issue_search_vector_update
    BEFORE INSERT OR
UPDATE ON SN_CIRA_ISSUE
    FOR EACH ROW EXECUTE FUNCTION update_issue_search_vector();

-- 기존 데이터 벡터 초기화
UPDATE SN_CIRA_ISSUE
SET SEARCH_VECTOR = to_tsvector('simple', COALESCE(TITLE, '') || ' ' || COALESCE(CONTENT, ''))
WHERE SEARCH_VECTOR IS NULL;

-- SN_CIRA_SAVED_FILTER 빠른 조회 인덱스
CREATE INDEX IF NOT EXISTS idx_sn_cira_saved_filter_user
    ON SN_CIRA_SAVED_FILTER (USER_ID);
