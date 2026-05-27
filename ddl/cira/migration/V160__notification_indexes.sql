-- Flyway Migration: V160__notification_indexes
-- SN_CIRA_NOTIFICATION, SN_CIRA_NOTIF_PREF 조회 최적화 인덱스
-- Generated: 2026-05-27

-- 알림 목록 조회 (userId + 최신순)
CREATE INDEX IF NOT EXISTS idx_sn_cira_notification_user
    ON SN_CIRA_NOTIFICATION (USER_ID);

-- 읽지 않은 알림 빠른 카운트
CREATE INDEX IF NOT EXISTS idx_sn_cira_notification_unread
    ON SN_CIRA_NOTIFICATION (USER_ID, READ_YN);

-- 알림 설정 조회
CREATE INDEX IF NOT EXISTS idx_sn_cira_notif_pref_user
    ON SN_CIRA_NOTIF_PREF (USER_ID);
