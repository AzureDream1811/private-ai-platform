# Private AI Platform

A self-hosted personal AI platform that provides multiple AI services through a unified API.

## 1. Overview

Private AI Platform là nền tảng AI cá nhân, cho phép người dùng sử dụng nhiều dịch vụ AI thông qua một hệ thống thống nhất.

Thay vì triển khai từng AI model thành những ứng dụng độc lập, nền tảng cung cấp một hệ thống quản lý tập trung:

- User authentication and authorization.
- AI service management.
- Asynchronous inference job processing.
- File storage and management.
- Inference result management.
- Job history and tracking.

**AI service đầu tiên:** Speech-to-Text sử dụng faster-whisper.

### Main objectives

- Xây dựng Backend có kiến trúc rõ ràng, dễ mở rộng.
- Tách biệt API processing và AI inference processing.
- Hỗ trợ xử lý các tác vụ AI bất đồng bộ.
- Quản lý tập trung người dùng, file, job và kết quả.
- Có thể tích hợp thêm các AI service trong tương lai.

---

## 2. Technology Stack

| Component        | Technology             |
| ---------------- | ---------------------- |
| Frontend         | React, TypeScript      |
| Backend API      | Python, FastAPI        |
| ORM              | SQLAlchemy 2.0         |
| Database         | PostgreSQL 17          |
| Migration        | Alembic                |
| Validation       | Pydantic v2            |
| Authentication   | JWT, PyJWT, bcrypt     |
| Message Broker   | Redis                  |
| Task Queue       | Celery                 |
| Object Storage   | MinIO                  |
| AI Model         | faster-whisper         |
| AI Runtime       | CPU                    |
| Testing          | Pytest, HTTPX          |
| Containerization | Docker, Docker Compose |

---

## 3. System Architecture

Hệ thống sử dụng kiến trúc Modular Monolith cho Backend API và triển khai Inference Worker thành một service riêng.

```text
                     CLIENT
                       |
                       v
                React + TypeScript
                       |
                       v
                 FastAPI Backend
                       |
          +------------+------------+
          |            |            |
          v            v            v
       Auth Module  Jobs Module  AI Service Module
          |            |            |
          +------------+------------+
                       |
                       v
                   PostgreSQL
                       |
                       |
                 Redis Broker
                       |
                       v
                Celery Worker
                       |
                       v
                faster-whisper
                       |
                       v
                  MinIO Storage
```

### Component responsibilities

**Frontend**

- User interface.
- Authentication.
- Upload input files.
- Submit AI jobs.
- Display job status and results.

**FastAPI Backend**

- Authentication and authorization.
- Validate API requests.
- Manage AI services.
- Create and manage inference jobs.
- Manage job history and results.
- Upload and retrieve files.
- Dispatch inference tasks to Celery.

**PostgreSQL**

- Store users and refresh tokens.
- Store available AI services.
- Store inference job metadata.
- Store inference results.
- Maintain job status.

**Redis**

- Act as Celery message broker.
- Handle task queues.

**Celery Worker**

- Consume inference tasks.
- Retrieve input files from MinIO.
- Execute AI inference.
- Update job status.
- Save inference results.

**MinIO**

- Store uploaded input files.
- Store generated output files when necessary.
- Keep large files outside PostgreSQL.

---

## 4. Project Structure

### Backend

```text
backend/
├── app/
│   ├── main.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── dependencies.py
│   │
│   ├── database/
│   │   ├── base.py
│   │   ├── session.py
│   │   └── models/
│   │       ├── __init__.py
│   │       ├── user.py
│   │       ├── refresh_token.py
│   │       ├── ai_service.py
│   │       ├── inference_job.py
│   │       ├── inference_result.py
│   │       └── enum.py
│   │
│   ├── modules/
│   │   ├── auth/
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── repository.py
│   │   │   └── schemas.py
│   │   │
│   │   ├── ai_services/
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── repository.py
│   │   │   └── schemas.py
│   │   │
│   │   └── jobs/
│   │       ├── router.py
│   │       ├── service.py
│   │       ├── repository.py
│   │       └── schemas.py
│   │
│   └── storage/
│       └── ...
│
├── migrations/
├── tests/
├── requirements.txt
├── requirements-dev.txt
└── alembic.ini
```

### Inference Worker

```text
worker/
├── main.py
├── celery_app.py
├── tasks/
│   └── inference_tasks.py
├── services/
│   └── speech_to_text.py
├── models/
│   └── whisper_model.py
└── storage/
    └── minio_client.py
```

Worker được triển khai độc lập với FastAPI. Model được load một lần khi worker khởi động, tránh load lại model cho mỗi task.

### Frontend

```text
frontend/
├── src/
│   ├── api/
│   ├── components/
│   ├── features/
│   │   ├── auth/
│   │   ├── services/
│   │   └── jobs/
│   ├── hooks/
│   ├── layouts/
│   ├── pages/
│   ├── routes/
│   ├── store/
│   └── types/
└── package.json
```

---

## 5. Database Design

### 5.1. User

Lưu thông tin tài khoản người dùng.

| Column        | Type        | Description     |
| ------------- | ----------- | --------------- |
| id            | Integer     | Primary key     |
| username      | String(50)  | Unique username |
| email         | String(100) | Unique email    |
| password_hash | String(255) | Hashed password |
| created_at    | Timestamp   | Creation time   |
| updated_at    | Timestamp   | Last update     |

### 5.2. RefreshToken

Quản lý vòng đời Refresh Token.

| Column     | Type        | Description     |
| ---------- | ----------- | --------------- |
| id         | Integer     | Primary key     |
| user_id    | FK          | Token owner     |
| token_hash | String(255) | SHA-256 hash    |
| expires_at | Timestamp   | Expiration time |
| revoked_at | Timestamp   | Revocation time |
| created_at | Timestamp   | Creation time   |

Không lưu raw Refresh Token vào database.

### 5.3. AIService

Quản lý các AI service được hệ thống hỗ trợ.

| Column      | Type        | Description               |
| ----------- | ----------- | ------------------------- |
| id          | Integer     | Primary key               |
| name        | String(100) | Service name              |
| service_key | String(255) | Unique service identifier |
| description | String(500) | Service description       |
| is_active   | Boolean     | Service availability      |

Ví dụ:

| name           | service_key    |
| -------------- | -------------- |
| Speech To Text | speech-to-text |

### 5.4. InferenceJob

Quản lý từng tác vụ AI do người dùng tạo.

| Column       | Type        | Description           |
| ------------ | ----------- | --------------------- |
| id           | Integer     | Primary key           |
| user_id      | FK          | Job owner             |
| service_id   | FK          | AI service            |
| status       | Enum        | Job status            |
| input_file   | String(500) | Storage object key    |
| parameters   | JSONB       | Inference parameters  |
| created_at   | Timestamp   | Creation time         |
| started_at   | Timestamp   | Processing start time |
| completed_at | Timestamp   | Completion time       |

Job status:

- `PENDING`
- `PROCESSING`
- `COMPLETED`
- `FAILED`

### 5.5. InferenceResult

Lưu kết quả xử lý của inference job.

| Column        | Type       | Description      |
| ------------- | ---------- | ---------------- |
| id            | Integer    | Primary key      |
| job_id        | FK, Unique | Related job      |
| result        | JSONB      | Inference output |
| error_message | Text       | Error details    |
| created_at    | Timestamp  | Creation time    |

### Relationships

```text
User
  |
  | 1:N
  v
RefreshToken

User
  |
  | 1:N
  v
InferenceJob
  |
  | N:1
  v
AIService

InferenceJob
  |
  | 1:0..1
  v
InferenceResult
```

---

## 6. Authentication Design

### API Endpoints

| Method | Endpoint              | Description          |
| ------ | --------------------- | -------------------- |
| POST   | /api/v1/auth/register | Register             |
| POST   | /api/v1/auth/login    | Login                |
| POST   | /api/v1/auth/refresh  | Refresh tokens       |
| POST   | /api/v1/auth/logout   | Revoke refresh token |
| GET    | /api/v1/auth/me       | Get current user     |

### Token configuration

| Token         | Expiration | Purpose               |
| ------------- | ---------- | --------------------- |
| Access Token  | 15 minutes | API authentication    |
| Refresh Token | 7 days     | Obtain new token pair |

### Login flow

1. Client sends email and password.
2. Backend verifies password using bcrypt.
3. Backend generates Access Token and Refresh Token.
4. Backend hashes Refresh Token using SHA-256.
5. Backend stores token hash in PostgreSQL.
6. Backend returns raw tokens to client.

### Refresh flow

1. Client sends Refresh Token.
2. Backend verifies JWT signature, expiration and token type.
3. Backend hashes the submitted token.
4. Backend finds its database record.
5. Backend checks whether the token is revoked or expired.
6. Backend revokes the old token.
7. Backend generates a new token pair.
8. Backend stores the new Refresh Token hash.
9. Backend commits the transaction.

### Security requirements

- Passwords must never be stored in plaintext.
- Refresh tokens must be stored as hashes.
- Access Token and Refresh Token must have different token types.
- Protected APIs must validate Access Token.
- Users can only access their own inference jobs.
- Sensitive configuration must be stored in environment variables.

---

## 7. AI Service Management

AI Service là danh mục các dịch vụ AI được nền tảng hỗ trợ.

### API Endpoints

| Method | Endpoint                      | Description          |
| ------ | ----------------------------- | -------------------- |
| GET    | /api/v1/services              | List active services |
| GET    | /api/v1/services/{service_id} | Get service details  |
| POST   | /api/v1/services              | Create service       |
| PATCH  | /api/v1/services/{service_id} | Update service       |
| DELETE | /api/v1/services/{service_id} | Deactivate service   |

Các API tạo, chỉnh sửa và deactivate service chỉ dành cho quản trị viên.

Ở giai đoạn đầu, có thể quản lý service bằng dữ liệu seed hoặc thao tác quản trị nội bộ.

---

## 8. Inference Job Management

Đây là module trung tâm của nền tảng.

### API Endpoints

| Method | Endpoint                     | Description            |
| ------ | ---------------------------- | ---------------------- |
| POST   | /api/v1/jobs                 | Create inference job   |
| GET    | /api/v1/jobs                 | Get user's job history |
| GET    | /api/v1/jobs/{job_id}        | Get job details        |
| GET    | /api/v1/jobs/{job_id}/result | Get inference result   |
| POST   | /api/v1/jobs/{job_id}/retry  | Retry failed job       |

### Create Job Flow

```text
Client
  |
  | Upload audio + service_key + parameters
  v
FastAPI
  |
  | 1. Authenticate user
  | 2. Validate AI service
  | 3. Validate input file
  v
MinIO
  |
  | Store uploaded audio
  | Return object key
  v
PostgreSQL
  |
  | Create InferenceJob
  | status = PENDING
  v
Redis / Celery
  |
  | Enqueue inference task
  v
Worker
```

### Processing Flow

```text
Celery Worker
      |
      v
Update status = PROCESSING
      |
      v
Retrieve audio from MinIO
      |
      v
Load faster-whisper model
      |
      v
Run Speech-to-Text
      |
      +--------------------+
      |                    |
      v                    v
    Success               Failure
      |                    |
      v                    v
Save Result          Save Error Details
      |                    |
      v                    v
COMPLETED               FAILED
```

### Important business rules

- A user can only access their own jobs.
- Inactive services cannot receive new jobs.
- A job must be persisted before it is dispatched to the worker.
- Worker must update job status during processing.
- A completed job must have an inference result.
- A failed job must retain useful error information.
- Job history must support pagination, filtering and sorting.

### Retry behavior

Chỉ cho phép retry các job ở trạng thái `FAILED`.

Retry phải tạo một lần xử lý mới có thể theo dõi được. Ở phiên bản đầu, có thể tái sử dụng job cũ với cơ chế reset trạng thái, nhưng cần đảm bảo không tạo nhiều worker task xử lý đồng thời cùng một job. Khi cần lưu lịch sử từng lần chạy, nên bổ sung bảng `InferenceAttempt`.

---

## 9. Speech-to-Text Service

### Technology

- Model: faster-whisper.
- Runtime: CPU.
- Language: Multilingual.
- Inference: Asynchronous through Celery.

### Input

Audio file và các tham số tùy chọn.

Ví dụ parameters:

```json
{
  "language": "en",
  "task": "transcribe",
  "beam_size": 5
}
```

### Output

```json
{
  "text": "Hello, how are you?",
  "language": "en",
  "duration": 3.5,
  "segments": [
    {
      "start": 0.0,
      "end": 1.5,
      "text": "Hello, how are you?"
    }
  ]
}
```

### Processing requirements

- Validate audio format and file size.
- Store audio in MinIO.
- Retrieve audio in the worker.
- Load model once at worker startup.
- Process audio asynchronously.
- Save transcription result in PostgreSQL.
- Handle invalid files and inference errors.
- Clean up temporary local files after processing.

---

## 10. File Storage Design

MinIO được sử dụng để lưu trữ file, PostgreSQL chỉ lưu metadata hoặc object key.

Ví dụ object key:

```text
users/{user_id}/jobs/{job_id}/input/audio.wav
users/{user_id}/jobs/{job_id}/output/result.json
```

File upload flow:

1. Client uploads file to FastAPI.
2. FastAPI validates file.
3. FastAPI uploads file to MinIO.
4. MinIO returns object key.
5. Backend stores object key in `InferenceJob.input_file`.
6. Worker retrieves file using object key.

Không nên lưu nội dung audio trực tiếp vào PostgreSQL.

---

## 11. Error Handling

Các lỗi cần xử lý thống nhất:

| HTTP Status | Situation                |
| ----------- | ------------------------ |
| 400         | Invalid business request |
| 401         | Unauthenticated          |
| 403         | Insufficient permission  |
| 404         | Resource not found       |
| 409         | Resource conflict        |
| 413         | File too large           |
| 422         | Request validation error |
| 500         | Internal server error    |

Đối với job đã được tạo thành công nhưng inference thất bại, API vẫn có thể trả về thông tin job với trạng thái `FAILED`. Đây không phải HTTP 500 của request tạo job.

---

## 12. Implementation Roadmap

### Phase 1 — Foundation

- [x] FastAPI project setup.
- [x] PostgreSQL Docker setup.
- [x] SQLAlchemy models.
- [x] Alembic migration.
- [x] Pydantic Settings.
- [x] Database session management.

### Phase 2 — Authentication

- [x] Password hashing.
- [x] JWT Access Token.
- [x] JWT Refresh Token.
- [x] Register API.
- [x] Login API.
- [x] Refresh API.
- [x] Logout API.
- [x] Current user dependency.
- [x] Protected `/me` endpoint.

### Phase 3 — AI Service Management

- [ ] AI Service Repository.
- [ ] AI Service Schemas.
- [ ] AI Service Service.
- [ ] AI Service Router.
- [ ] Seed initial AI services.
- [ ] Admin authorization.

### Phase 4 — Inference Job Management

- [ ] Job Repository.
- [ ] Job Schemas.
- [ ] Job Service.
- [ ] Job Router.
- [ ] Create Job API.
- [ ] Get Job Details API.
- [ ] Job History API.
- [ ] Pagination, Filtering and Sorting.
- [ ] Ownership validation.

### Phase 5 — Storage and Background Processing

- [ ] MinIO setup.
- [ ] File upload and download.
- [ ] Redis setup.
- [ ] Celery setup.
- [ ] Separate Worker deployment.
- [ ] Job dispatching.
- [ ] Job status updates.
- [ ] Inference Result management.
- [ ] Retry mechanism.
- [ ] Worker error handling.

### Phase 6 — Speech-to-Text

- [ ] Install faster-whisper.
- [ ] Implement model initialization.
- [ ] Load model at worker startup.
- [ ] Implement transcription service.
- [ ] Integrate transcription with Celery.
- [ ] Save transcription result.
- [ ] Handle unsupported or invalid audio.

### Phase 7 — Frontend

- [ ] React + TypeScript setup.
- [ ] Login and Register pages.
- [ ] Authentication state management.
- [ ] AI Service listing.
- [ ] Audio upload interface.
- [ ] Job history.
- [ ] Job status tracking.
- [ ] Transcription result display.

### Phase 8 — Quality and Deployment

- [ ] Unit tests.
- [ ] Integration tests.
- [ ] API tests.
- [ ] Authentication security review.
- [ ] Docker Compose deployment.
- [ ] Environment configuration.
- [ ] Logging and monitoring.
- [ ] Documentation.

---

## 13. Development Principles

Các nguyên tắc cần tuân thủ trong quá trình phát triển:

1. **Separation of Concerns:** Mỗi layer chỉ đảm nhận một trách nhiệm.
2. **Repository Pattern:** Repository chịu trách nhiệm giao tiếp với database.
3. **Service Layer:** Service xử lý business logic, không để business logic trong Router.
4. **Schema Separation:** Không trả trực tiếp SQLAlchemy Entity từ API.
5. **Transaction Management:** Xác định rõ nơi quản lý commit và rollback.
6. **Authentication and Authorization:** Xác thực người dùng và kiểm tra quyền sở hữu tài nguyên.
7. **Asynchronous Processing:** Các tác vụ AI nặng không chạy trực tiếp trong HTTP request.
8. **Scalability:** Có thể mở rộng worker độc lập mà không cần mở rộng API cùng tỷ lệ.
9. **Maintainability:** Ưu tiên code dễ đọc, dễ kiểm thử và dễ thay đổi.

---

## 14. Future Improvements

Các tính năng có thể phát triển sau khi hoàn thành phiên bản đầu:

- Redis caching.
- Access Token revocation.
- Rate limiting.
- WebSocket hoặc Server-Sent Events để cập nhật job status.
- Multiple AI workers.
- GPU inference.
- Additional AI services.
- Job priority and scheduling.
- Inference performance metrics.
- Usage statistics and quotas.
- InferenceAttempt history.
- Audit logging.

---

## 15. Project Goal

Hoàn thành một nền tảng AI cá nhân có khả năng:

- Quản lý tài khoản và xác thực an toàn.
- Cung cấp nhiều AI services thông qua một API thống nhất.
- Tiếp nhận và quản lý các inference jobs.
- Xử lý AI bất đồng bộ bằng worker riêng.
- Lưu trữ file và kết quả.
- Theo dõi lịch sử và trạng thái xử lý.
- Dễ dàng mở rộng thêm AI models và services.

**First milestone:** Hoàn thiện hệ thống Speech-to-Text end-to-end, từ upload audio đến nhận kết quả transcription thông qua nền tảng.
