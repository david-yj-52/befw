# befw — 멀티모듈 Parent POM

## 프로젝트 개요

| 항목              | 내용                                         |
|-----------------|--------------------------------------------|
| **역할**          | Backend Framework 멀티모듈 Parent POM (BOM 겸용) |
| **GroupId**     | `com.tsh.starter.befw`                     |
| **ArtifactId**  | `befw`                                     |
| **Version**     | `1.0-SNAPSHOT`                             |
| **Java**        | 21 (Preview 기능 활성화)                        |
| **Spring Boot** | 3.4.1                                      |
| **Packaging**   | `pom`                                      |

## 모듈 구조

```
befw/                          ← Parent POM (이 프로젝트)
├── befw-lib-core/             ← 공통 라이브러리 (Nexus 배포 대상)
└── befw-app-server/           ← 실행 가능한 앱 서버 (Spring Boot 실행 단위)
```

## 공통 의존성 (모든 하위 모듈에 상속)

| 카테고리           | 라이브러리                                                   | 비고                         |
|----------------|---------------------------------------------------------|----------------------------|
| **메시징**        | `sol-jcsmp:10.25.0`                                     | Solace PubSub+ JCSMP 클라이언트 |
| **Web**        | `spring-boot-starter-web`                               | REST API                   |
| **Actuator**   | `spring-boot-starter-actuator`                          | 헬스체크·메트릭                   |
| **JPA**        | `spring-boot-starter-data-jpa`                          | ORM                        |
| **Mail**       | `spring-boot-starter-mail`                              | 메일 발송                      |
| **Scheduler**  | `spring-boot-starter-quartz`                            | 배치/스케줄러                    |
| **로깅**         | `spring-boot-starter-log4j2`                            | Logback 제거 후 Log4j2 사용     |
| **API 문서**     | `springdoc-openapi-starter-webmvc-ui:2.7.0`             | Swagger UI                 |
| **Kotlin**     | `kotlin-reflect`, `kotlin-logging-jvm:3.0.5`            | Kotlin 지원                  |
| **ORM**        | `mybatis-spring-boot-starter:3.0.4`, `hibernate-envers` | MyBatis + Envers 이력관리      |
| **DB**         | `postgresql` (runtime)                                  | PostgreSQL                 |
| **모니터링**       | `micrometer-registry-prometheus` (runtime)              | Prometheus 메트릭             |
| **인증**         | `google-api-client:2.2.0`                               | Google 토큰 검증               |
| **유틸**         | `lombok`, `jackson-module-kotlin:2.15.0`                | 보일러플레이트·JSON               |
| **환경변수**       | `spring-dotenv:4.0.0`                                   | `.env` 파일 지원               |
| **Validation** | `spring-boot-starter-validation`                        | Bean Validation            |
| **내부 스키마**     | `com.tsh:tsh-schema:1.0.6-SNAPSHOT`                     | 공통 스키마 라이브러리               |
| **테스트**        | `spring-boot-starter-test`, `spring-restdocs-mockmvc`   | 통합테스트·REST Docs            |

## Maven Repository 설정

| Repository      | URL                                                         | 용도               |
|-----------------|-------------------------------------------------------------|------------------|
| nexus-snapshots | `http://localhost:8081/repository/maven-snapshots/`         | 내부 SNAPSHOT      |
| nexus-releases  | `http://localhost:8081/repository/maven-releases/`          | 내부 Release       |
| github          | `https://maven.pkg.github.com/david-yj-52/befw-schema-repo` | `tsh-schema` 패키지 |

## DDL

- DB 설정에 대한 정의와 관리는 befw 모듈에서 진행
- 추가되는 테이블은 ddl 파일에서 관리
  | 파일 | 설명 |
  |---------------------------|-------------------------------------|
  | `ddl/GS_MSG_SRV_CONN.sql` | 메시징 서버 연결 기준정보 테이블 DDL (PostgreSQL) |

## 로그

- 경로: `logs/`
- 파일 패턴: `befw-app-server.log`, `befw-app-server-error.log`
- 롤오버: 일별 GZ 압축 (`befw-app-server-YYYY-MM-DD-N.log.gz`)

---

## tsh-schema

- 전체 시스템 (UI, BackEnd, Agent 등) 에서 사용하는 공통 스키마 정보
- 2026년 5월 25일 현재, tsh-schema는 개발 효율성 이슈로 사용하고 있지 않음
    - 추후 다시 사용 예정

## Kafka 설정

- messaging 처리 시, 사용하는 솔루션 중 하나
- 현재는 Solace 만 사용하고 있음
- 2026년 5월 25일 기준, Solace 만을 통한 서비스 진행, 필요 시 추후 설정

## Quartz Job

- 배치 업무를 위한 서비스
- 2026년 5월 25일 기준, 사용할 필요가 없어 구현 대상 제외

## Google 인증

- 서비스 로그인이나 유저 세션 관리등을 위한 사용
- 2026년 5월 25일 기준, 실체적인 구현이 필요한 상황

## 운영 Nexus

- 현재 운영을 위한 Nexus는 없음 (서버 리소스 부족)
- 개발에 필요한 부분은 GitHub Package 통해서 사용

## DB 테이블 네이밍

- DB 테이블 네이밍 규칙
    - GS (Global Server)
        - Global 테이블 네이밍으로 서비스 공통에서 사용하는 테이블에 사용 (befw-lib-core)
        - entity, repository 는 befw-lib-core에 구현하고
        - 사용하는 app에서는 이를 상속 받아서 처리
    - SN (Server Normal)
        - 단위 App 에서 사용하는 테이블 네이밍으로 주로 app 모듈에서 개발하고 사용된다. (ex, befw-app-server)
        - 주로 상세 기능 구현, 데이터 저장 등에 사용됨