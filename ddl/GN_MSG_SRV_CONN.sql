-- ============================================================
-- Table Name : GN_MSG_SRV_CONN
-- DB Type    : Server - PostgreSQL
-- Description: Global 서비스 Messaging 서버 연결 기준정보
-- Created By : 김연준
-- Created At : 2026-04-05
-- ============================================================

CREATE TABLE GN_MSG_SRV_CONN
(
    OBJ_ID      VARCHAR(100) NOT NULL,               -- PK
    SRV_ID      VARCHAR(50)  NOT NULL DEFAULT 'BEFW',-- UK, 서비스 이름
    TENANT      VARCHAR(50)  NOT NULL DEFAULT 'TAS', -- UK, 테넌트
    ENV         VARCHAR(50)  NOT NULL,               -- UK, 서비스 환경 (PROD, DEV)
    SOL_NM      VARCHAR(50)  NOT NULL,               -- UK, Messaging 서비스 이름 (Kafka, Solace)
    HOST        VARCHAR(100) NOT NULL,               -- UK, 서버 IP
    PORT        NUMERIC,                             -- 서버 포트
    "USER"      VARCHAR(100),                        -- 접속 아이디
    PWD         VARCHAR(100),                        -- 접속 비밀번호
    DOMAIN      VARCHAR(50),
    EVNT_NM     VARCHAR(100) NOT NULL,               -- Null = N
    PRV_EVNT_NM VARCHAR(100),
    ACT_RSN_CD  VARCHAR(100),
    ACT_CM      TEXT,
    USE_STAT_CD VARCHAR(40)  NOT NULL DEFAULT 'Usable',
    TRACE_ID    VARCHAR(100) NOT NULL,
    CREATED_BY  VARCHAR(40),
    CREATED_AT  TIMESTAMP    NOT NULL DEFAULT NOW(),
    MODIFIED_BY VARCHAR(40),
    MODIFIED_AT TIMESTAMP    NOT NULL DEFAULT NOW(),

    -- Primary Key
    CONSTRAINT PK_GN_MSG_SRV_CONN PRIMARY KEY (OBJ_ID),

    -- Unique Key
    CONSTRAINT UK_GN_MSG_SRV_CONN UNIQUE (TENANT, ENV, SOL_NM, HOST)
);

-- ============================================================
-- Comments
-- ============================================================
COMMENT ON TABLE GN_MSG_SRV_CONN IS 'Global 서비스 Messaging 서버 연결 기준정보';
COMMENT ON COLUMN GN_MSG_SRV_CONN.OBJ_ID IS '오브젝트 ID (PK)';
COMMENT ON COLUMN GN_MSG_SRV_CONN.SRV_ID IS '서비스 명 (Default: BEFW)';
COMMENT ON COLUMN GN_MSG_SRV_CONN.TENANT IS '테넌트 (Default: TSH)';
COMMENT ON COLUMN GN_MSG_SRV_CONN.ENV IS '서비스 환경 (PROD, DEV)';
COMMENT ON COLUMN GN_MSG_SRV_CONN.SOL_NM IS 'Messaging 서비스 이름 (Kafka, Solace)';
COMMENT ON COLUMN GN_MSG_SRV_CONN.HOST IS '서버 IP';
COMMENT ON COLUMN GN_MSG_SRV_CONN.PORT IS '서버 포트';
COMMENT ON COLUMN GN_MSG_SRV_CONN."USER" IS '접속 아이디';
COMMENT ON COLUMN GN_MSG_SRV_CONN.PWD IS '접속 비밀번호';
COMMENT ON COLUMN GN_MSG_SRV_CONN.DOMAIN IS '도메인';
COMMENT ON COLUMN GN_MSG_SRV_CONN.EVNT_NM IS '이벤트 이름';
COMMENT ON COLUMN GN_MSG_SRV_CONN.PRV_EVNT_NM IS '이전 이벤트 이름';
COMMENT ON COLUMN GN_MSG_SRV_CONN.ACT_RSN_CD IS '액션 사유 코드';
COMMENT ON COLUMN GN_MSG_SRV_CONN.ACT_CM IS '액션 코멘트';
COMMENT ON COLUMN GN_MSG_SRV_CONN.USE_STAT_CD IS '사용 상태 코드 (Default: Usable)';
COMMENT ON COLUMN GN_MSG_SRV_CONN.TRACE_ID IS '트레이스 ID';
COMMENT ON COLUMN GN_MSG_SRV_CONN.CREATED_BY IS '생성자';
COMMENT ON COLUMN GN_MSG_SRV_CONN.CREATED_AT IS '생성일시';
COMMENT ON COLUMN GN_MSG_SRV_CONN.MODIFIED_BY IS '수정자';
COMMENT ON COLUMN GN_MSG_SRV_CONN.MODIFIED_AT IS '수정일시';