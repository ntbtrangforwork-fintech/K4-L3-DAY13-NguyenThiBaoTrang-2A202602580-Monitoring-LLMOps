# Báo cáo cá nhân — K4-L3B Day 13 Monitoring & LLMOps

> Mỗi học viên hoàn thiện một file duy nhất này. Khi dẫn evidence, dùng đường dẫn tương đối, ví dụ `evidence/07-trace-waterfall.png`.

## 1. Thông tin học viên

- **Họ và tên:** Nguyễn Thị Bảo Trang
- **MSSV:** 2A202602580
- **Lớp:** K4-L3B
- **Repository URL:** https://github.com/ntbtrangforwork-fintech/K4-L3-DAY13-NguyenThiBaoTrang-2A202602580-Monitoring-LLMOps
- **Commit SHA cuối:**
- **Challenge ID:**
- **Tên project Langfuse cá nhân:** `day13-k4-l3b-2A202602580`

## 2. Evidence index

Điền đúng đường dẫn tới evidence thực tế. Có thể đổi tên hoặc dùng nhiều ảnh nếu cần.

| Evidence | Đường dẫn |
|---|---|
| Pytest cuối | `evidence/01-pytest.png` |
| Log validator | `evidence/02-log-validator.png` |
| Dashboard validator | `evidence/03-dashboard-validator.png` |
| Structured log | `evidence/04-structured-log.png` |
| PII redaction | `evidence/05-pii-redaction.png` |
| Trace list | `evidence/06-trace-list.png` |
| Trace waterfall | `evidence/07-trace-waterfall.png` |
| Trace metadata | `evidence/08-trace-metadata.png` |
| Prompt versions | `evidence/09-prompt-versions.png` |
| Prompt rollback | `evidence/10-prompt-rollback.png` |
| Dashboard runtime | `evidence/11-dashboard-overview.png` |
| Incident metric | `evidence/12-incident-metric.png` |
| Incident log | `evidence/13-incident-log.png` |
| Incident trace | `evidence/14-incident-trace.png` |
| CP0 health check | `evidence/cp0-health.txt` |
| CP0 load test | `evidence/cp0-load-test.txt` |
| CP0 log validator baseline | `evidence/cp0-validate-logs.txt` |
| CP0 dashboard validator baseline | `evidence/cp0-validate-dashboard.txt` |
| CP0 pytest baseline | `evidence/cp0-pytest.txt` |
| CP0 Langfuse verification | `evidence/cp0-langfuse-traces.txt` |

## 3. Kết quả kỹ thuật

| Nội dung | Baseline | Kết quả cuối | Nhận xét |
|---|---|---|---|
| `validate_logs.py` | 30/100 | | Baseline CP0 chưa đạt là dự kiến; correlation ID và enrichment thuộc CP1. |
| `validate_dashboard.py` | HỢP LỆ: 6/6 panel | | Contract dashboard mặc định hợp lệ. |
| `pytest` | 22 passed in 3.61s | | Chạy bằng Python 3.11.16 trong `.venv`. |
| Số traces hợp lệ | 10 trace mới | | 10 root observations/10 trace ID trong project Langfuse cá nhân. |
| Số PII leak | 0 | | Kết quả baseline từ `validate_logs.py`. |
| Latency P95 / TTFT P95 | | | |
| Retrieval success rate | | | |

### CP0 — Setup và baseline

- **Thời điểm chạy:** 2026-09-30 11:45 (Asia/Bangkok, UTC+07:00)
- **Commit dùng làm baseline:** `61a34f827748393ced851ea7c9b412dd53dced23`
- **Môi trường:** Python 3.11.16, dependencies cài từ `requirements.txt` trong `.venv`.
- **Health:** `/health` trả `ok: true` và `tracing_enabled: true`.
- **Load test:** 10/10 request trả HTTP 200.
- **Langfuse:** xác thực thành công; project `day13-k4-l3b-2A202602580`; 10 root observations thuộc 10 trace ID mới trong cửa sổ kiểm tra 10 phút.
- **Ghi chú:** `correlation_id=MISSING` và log validator 30/100 là baseline trước CP1, không được sửa giả tại CP0.

## 4. Logging và PII

- **Cách tạo/nhận và truyền correlation ID:**
- **Các metadata được ghi vào structured log:**
- **Cách bảo đảm PII được scrub trước khi ghi:**
- **Cách kiểm chứng kết quả:**

## 5. Tracing và prompt versioning

- **Cách xác nhận traces do chính tôi tạo trong project cá nhân:**
- **Cấu trúc root/retrieval/generation observations:**
- **Cách nối trace với log:**
- **Prompt name:**
- **Version/label baseline:**
- **Version/label candidate:**
- **Trace ID của mỗi version:**
- **Cách promote và rollback `production`:**

## 6. Dashboard, SLO và alerts

- **Dashboard và sáu panel:**
- **SLO và lý do chọn:**
- **Cách tính error budget:**
- **Ba alert và runbook tương ứng:**

> Ví dụ cách viết error budget: "SLO 99.5% trong 28 ngày nghĩa là error budget 0.5%. Nếu workload có 10,000 request thì tối đa 50 request được phép lỗi hoặc chậm hơn ngưỡng SLO."

## 7. Điều tra challenge

- **Challenge ID:**
- **Khoảng thời gian điều tra:**
- **Triệu chứng từ metrics:**
- **Log line và correlation ID liên quan:**
- **Trace ID và span gây ảnh hưởng:**
- **Root cause:**
- **Fix action:**
- **Preventive measure:**

> Gợi ý cách viết ngắn, không thay cho evidence thực tế: "Metric cho thấy `[latency/error/cost/quality]` bất thường trong `[khoảng thời gian]`. Log line `[event]` có `correlation_id=[...]` đại diện cho request bị ảnh hưởng. Trace cùng `correlation_id` cho thấy span `[retrieval/generation/prompt/tool]` có dấu hiệu `[chậm/lỗi/token tăng]`. Root cause là `[nguyên nhân suy ra từ evidence]`. Fix action là `[hành động khôi phục]`; preventive measure là `[alert/runbook/test/guardrail để ngăn tái diễn]`."

## 8. Giải thích và tự đánh giá

- **Một quyết định kỹ thuật quan trọng và lý do:**
- **Một lỗi/blocker đã gặp:**
- **Cách tìm nguyên nhân và xử lý:**
- **Cách hiểu luồng Metrics → Logs → Traces:**
- **Vai trò của prompt version, token/cost, SLO hoặc rollback trong vận hành LLM:**
- **Điều quan trọng nhất đã học:**
- **Hạn chế hoặc phần chưa hoàn thành, nếu có:**

## 9. Checklist trước khi nộp

- [ ] Kết quả và evidence thuộc commit SHA cuối.
- [ ] Tất cả ảnh/output mở được bằng đường dẫn tương đối.
- [ ] Incident evidence nối đúng metric → log → trace.
- [ ] Trace/prompt evidence thuộc project Langfuse cá nhân và ảnh không lộ key/secret.
- [ ] Repository chạy lại được theo README.
- [ ] Không có secret, API key, PII thô hoặc evidence của người khác/lớp khác.
- [ ] URL repo và commit SHA cuối đã được nộp trên LMS/Codelabs.
