#### 프로그램 구조(변경)

Route <-> Service <-> Repository <-> Crawler, DAO

Route 역할: 클라이언트의 Request를 받고 Response를 보냄
Repository 역할: 필요한 데이터에 접근 (db, crawler 접근)
Service 역할: Fucntion에대한 로직구현(Task동작 제어 포함)
DAO 역할: 데이터 베이스 접근을 하는 역할
DTO 역할: 계층간 데이터 교환이 이루어 질 수 있도록 하는 객체