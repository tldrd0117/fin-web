#### 프로그램 구조(변경)

Route <-> Service <-> Repository <-> Crawler, DAO

Route 역할: 클라이언트의 Request를 받고 Response를 보냄
Repository 역할: 필요한 데이터에 접근 (db, crawler 접근)
Service 역할: Fucntion에대한 로직구현(Task동작 제어 포함)
DAO 역할: 데이터 베이스 접근을 하는 역할
DTO 역할: 계층간 데이터 교환이 이루어 질 수 있도록 하는 객체

### 에러날떄 yaml에 추가
    command: ["/bin/sh"]    
    args: ["-c", "sleep 100 && echo Sleep expired > /dev/termination-log"]

#### 프로그램 구조 개선해야할 점

1. 키밸류 이벤트는 너무 헷갈린다
2. 서비스 로케이터 패턴은 안티패턴인 것 같다.
3. 복잡한 구조는 프로그래밍 이해하는 시간을 너무 많이 쓰게한다.
4. 하나의 소켓으로 모든 통신을 다루는 것이 아닌 주소에 따른 웹소켓 구현이 나은 방법인지 생각할 필요가 있다.