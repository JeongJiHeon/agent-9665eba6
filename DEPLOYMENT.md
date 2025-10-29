# 배포 가이드

## 로컬 개발 환경

### 1. 사전 준비

```bash
# Git clone
git clone <repository-url>
cd workspace

# 환경 변수 설정
cp .env.example .env
# .env 파일을 편집하여 필요한 API 키 입력
```

### 2. Docker로 실행

```bash
# 모든 서비스 빌드 및 시작
docker-compose up --build

# 백그라운드 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 특정 서비스 재시작
docker-compose restart backend

# 중지
docker-compose down

# 볼륨까지 삭제
docker-compose down -v
```

### 3. 로컬 개발 (Docker 없이)

#### 백엔드

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Redis 실행 (별도 터미널)
redis-server

# 개발 서버
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 프론트엔드

```bash
cd frontend
npm install
npm start
```

## 프로덕션 배포

### 환경 변수 설정

프로덕션 환경에서는 다음 변수들을 안전하게 설정:

```env
# 프로덕션 설정
DEBUG=False
API_WORKERS=4
LOG_LEVEL=INFO

# HTTPS 사용 시
GOOGLE_REDIRECT_URI=https://yourdomain.com/auth/callback
CORS_ORIGINS=["https://yourdomain.com"]

# Redis 보안
REDIS_PASSWORD=strong_password_here
```

### Docker Compose 프로덕션

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    environment:
      - DEBUG=False
      - API_WORKERS=4
    restart: always
    
  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    restart: always
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    restart: always
```

### AWS 배포

#### EC2 배포

```bash
# EC2 인스턴스에 접속
ssh -i your-key.pem ec2-user@your-instance

# Docker 설치
sudo yum update -y
sudo yum install docker -y
sudo systemctl start docker
sudo usermod -a -G docker ec2-user

# Docker Compose 설치
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 애플리케이션 배포
git clone <repo>
cd workspace
cp .env.example .env
# .env 편집
docker-compose up -d
```

#### ECS/Fargate 배포

```bash
# ECR에 이미지 푸시
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

docker build -t calendar-agent-backend -f Dockerfile.backend .
docker tag calendar-agent-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/calendar-agent-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/calendar-agent-backend:latest

# ECS 태스크 정의 및 서비스 생성
aws ecs create-task-definition --cli-input-json file://task-definition.json
aws ecs create-service --cli-input-json file://service-definition.json
```

### Kubernetes 배포

```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: calendar-agent-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: calendar-agent-backend
  template:
    metadata:
      labels:
        app: calendar-agent-backend
    spec:
      containers:
      - name: backend
        image: your-registry/calendar-agent-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: openai-api-key
---
apiVersion: v1
kind: Service
metadata:
  name: calendar-agent-backend
spec:
  selector:
    app: calendar-agent-backend
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

```bash
# 배포
kubectl apply -f kubernetes/
```

### Google Cloud Run 배포

```bash
# 빌드 및 푸시
gcloud builds submit --tag gcr.io/PROJECT-ID/calendar-agent-backend

# 배포
gcloud run deploy calendar-agent-backend \
  --image gcr.io/PROJECT-ID/calendar-agent-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=$OPENAI_API_KEY
```

## CI/CD 설정

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Build and push Docker image
      env:
        DOCKER_USERNAME: ${{ secrets.DOCKER_USERNAME }}
        DOCKER_PASSWORD: ${{ secrets.DOCKER_PASSWORD }}
      run: |
        docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD
        docker build -t $DOCKER_USERNAME/calendar-agent-backend -f Dockerfile.backend .
        docker push $DOCKER_USERNAME/calendar-agent-backend:latest
    
    - name: Deploy to server
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.HOST }}
        username: ${{ secrets.USERNAME }}
        key: ${{ secrets.SSH_KEY }}
        script: |
          cd /app/workspace
          git pull
          docker-compose pull
          docker-compose up -d
```

## 모니터링 및 로깅

### Prometheus + Grafana

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      
  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

### ELK Stack

```yaml
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      
  logstash:
    image: docker.elastic.co/logstash/logstash:8.11.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
      
  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    ports:
      - "5601:5601"
```

## 백업 및 복구

### Redis 백업

```bash
# 수동 백업
docker exec calendar-agent-redis redis-cli SAVE

# 백업 파일 복사
docker cp calendar-agent-redis:/data/dump.rdb ./backup/

# 복구
docker cp ./backup/dump.rdb calendar-agent-redis:/data/
docker restart calendar-agent-redis
```

### ChromaDB 백업

```bash
# 데이터 디렉토리 백업
tar -czf chroma-backup-$(date +%Y%m%d).tar.gz data/chroma/

# 복구
tar -xzf chroma-backup-20231201.tar.gz
```

## 보안 체크리스트

- [ ] 모든 API 키를 환경 변수로 관리
- [ ] HTTPS 설정 (Let's Encrypt)
- [ ] CORS 올바르게 설정
- [ ] Redis 비밀번호 설정
- [ ] 방화벽 규칙 설정
- [ ] 정기적인 보안 업데이트
- [ ] 로그 모니터링
- [ ] 백업 자동화

## 성능 튜닝

### Uvicorn Workers

```python
# 프로덕션에서 worker 수 증가
uvicorn app.main:app --workers 4 --host 0.0.0.0 --port 8000
```

### Redis 최적화

```conf
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

### ChromaDB 최적화

```python
# 임베딩 배치 처리
await vector_store_service.add_events_batch(events)
```

## 문제 해결

### 컨테이너가 시작되지 않음

```bash
docker-compose logs backend
docker-compose ps
docker inspect calendar-agent-backend
```

### Redis 연결 오류

```bash
docker-compose exec redis redis-cli ping
docker-compose restart redis
```

### 메모리 부족

```bash
# Docker 메모리 제한 확인
docker stats

# 컨테이너 메모리 제한 설정
docker-compose.yml에서:
services:
  backend:
    mem_limit: 2g
```

## 스케일링

### 수평 스케일링

```yaml
# docker-compose.yml
services:
  backend:
    deploy:
      replicas: 3
```

### 로드 밸런싱

```nginx
# nginx.conf
upstream backend {
    least_conn;
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://backend;
    }
}
```
