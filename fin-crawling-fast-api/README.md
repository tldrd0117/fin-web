#### 프로그램 구조

Route <-> Event <-> Service <-> Repository <-> Crawler, DAO

Route 역할: 소켓 제어
Event 역할: 클라이언트와 송수신 각 이벤트 키에대한 Function을 수행
Service 역할: Function에대한 로직구현
Repository 역할: 필요한 데이터를 구조화하여 가지고 있거나 가져옴
Crawler 역할: webdriver를 통해 데이터를 가져옴
DAO 역할: 데이터 베이스 접근을 하는 역할
DTO 역할: 계층간 데이터 교환이 이루어 질 수 있도록 하는 객체