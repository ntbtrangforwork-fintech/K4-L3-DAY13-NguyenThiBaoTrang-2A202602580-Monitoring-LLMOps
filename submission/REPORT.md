# Báo cáo cá nhân — K4-L3B Day 13 Monitoring & LLMOps

> Mỗi học viên hoàn thiện một file duy nhất này. Khi dẫn evidence, dùng đường dẫn tương đối, ví dụ `evidence/07-trace-waterfall.png`.

## 1. Thông tin học viên

- **Họ và tên:** Nguyễn Thị Bảo Trang
- **MSSV:** 2A202602580
- **Lớp:** K4-L3B
- **Repository URL:** https://github.com/ntbtrangforwork-fintech/K4-L3-DAY13-NguyenThiBaoTrang-2A202602580-Monitoring-LLMOps
- **Commit SHA cuối:** `bb224745caa9688b5e600dfd541cc1cd2e96fdbe`
- **Challenge ID:** `day13-k4-l3b-monitoring-llmops-v1`
- **Tên project Langfuse cá nhân:** `day13-k4-l3b-2A202602580`

## 2. Evidence index

Điền đúng đường dẫn tới evidence thực tế. Có thể đổi tên hoặc dùng nhiều ảnh nếu cần.

| Evidence | Đường dẫn |
|---|---|
| Pytest cuối | `evidence/01-pytest.txt` |
| Log validator | `evidence/02-log-validator.png` |
| Dashboard validator | `evidence/03-dashboard-validator.png` |
| Structured log | `evidence/04-structured-log.png` |
| PII redaction | `evidence/05a-pii-test-input.png`, `evidence/05b-pii-redacted-log.png` |
| Trace list | `evidence/06-trace-list.png` |
| Trace waterfall | `evidence/07-trace-waterfall.png` |
| Trace metadata | `evidence/08a-trace-metadata.png`, `evidence/08b-generation-usage.png` |
| Prompt versions | `evidence/09-prompt-versions.png` |
| Prompt rollback | `evidence/10-prompt-rollback.png` |
| Dashboard runtime | `evidence/11a-dashboard-latency-traffic.png`, `evidence/11b-dashboard-error-cost-token-quality.png` |
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
| `validate_logs.py` | 30/100 | 100/100 | CP1 bổ sung correlation ID, enrichment và PII processor. |
| `validate_dashboard.py` | HỢP LỆ: 6/6 panel | HỢP LỆ: 6/6 panel | Dashboard runtime đọc trực tiếp `data/logs.jsonl`. |
| `pytest` | 22 passed in 3.61s | 29 passed | Chạy bằng Python 3.11.16 trong `.venv`. |
| Số traces hợp lệ | 10 trace mới | 11 trace CP2 gần nhất | Mỗi trace CP2 có root, retrieval và generation. |
| Số PII leak | 0 | 0 | Kiểm tra runtime với email, điện thoại, CCCD và thẻ giả. |
| Latency P95 / TTFT P95 | | 1729 ms / 50 ms | Cửa sổ dashboard 60 phút sau workload CP2. |
| Retrieval success rate | | 100% | Tính từ `response_sent.tool_success`. |

### CP0 — Setup và baseline

- **Thời điểm chạy:** 2026-09-30 11:45 (Asia/Bangkok, UTC+07:00)
- **Commit dùng làm baseline:** `61a34f827748393ced851ea7c9b412dd53dced23`
- **Môi trường:** Python 3.11.16, dependencies cài từ `requirements.txt` trong `.venv`.
- **Health:** `/health` trả `ok: true` và `tracing_enabled: true`.
- **Load test:** 10/10 request trả HTTP 200.
- **Langfuse:** xác thực thành công; project `day13-k4-l3b-2A202602580`; 10 root observations thuộc 10 trace ID mới trong cửa sổ kiểm tra 10 phút.
- **Ghi chú:** `correlation_id=MISSING` và log validator 30/100 là baseline trước CP1, không được sửa giả tại CP0.

## 4. Logging và PII

- **Cách tạo/nhận và truyền correlation ID:** Middleware xóa contextvars đầu mỗi request, nhận `x-request-id` nếu khớp `req-<8-hex>` hoặc sinh ID mới bằng UUID, bind ID vào structlog context, lưu trong `request.state`, rồi trả lại qua response body/header `x-request-id`. Header `x-response-time-ms` ghi tổng thời gian xử lý HTTP.
- **Các metadata được ghi vào structured log:** `correlation_id`, `user_id_hash`, `session_id`, `feature`, `model`, `env`, cùng timestamp, level, event và các trường latency/TTFT/token/cost/quality khi đã có kết quả.
- **Cách bảo đảm PII được scrub trước khi ghi:** `scrub_event` duyệt đệ quy các chuỗi trong event dictionary và chạy sau bước bổ sung exception/stack metadata nhưng trước `JsonlFileProcessor` và `JSONRenderer`. User ID chỉ được ghi dưới dạng SHA-256 rút gọn.
- **Cách kiểm chứng kết quả:** Workload tạo 12 correlation ID duy nhất. `validate_logs.py` đạt 100/100, không thiếu schema/enrichment và phát hiện 0 PII leak. Request kiểm thử `req-deadbeef` chứa email, điện thoại Việt Nam, CCCD và thẻ giả; log chỉ còn các marker `[REDACTED_*]`. Public tests đạt 26/26.

## 5. Tracing và prompt versioning

- **Cách xác nhận traces do chính tôi tạo trong project cá nhân:** Xác thực bằng Langfuse Projects API rằng key thuộc project `day13-k4-l3b-2A202602580`, sau đó chạy workload từ repo cá nhân. Observations v2 API ghi nhận 11 trace gần nhất, mỗi trace có đủ ba observation CP2.
- **Cấu trúc root/retrieval/generation observations:** `lab-agent-run` (`AGENT`) là root; `retrieval` (`RETRIEVER`) và `generation` (`GENERATION`) là hai child cùng trỏ `parent_observation_id` của root. Retrieval chỉ lưu query/document preview đã scrub. Generation có model, managed prompt link, input/output token, TTFT và cost.
- **Cách nối trace với log:** `correlation_id` được bind từ middleware vào log và đồng thời ghi trong metadata của root, retrieval và generation. Ví dụ baseline dùng `req-bae10001`; candidate dùng `req-cad20002`.
- **Prompt name:** `day13-chat`.
- **Version/label baseline:** Version 1, labels `baseline` và `production` sau rollback.
- **Version/label candidate:** Version 2, labels `candidate` và `latest`.
- **Trace ID của mỗi version:** baseline v1 `db6141ff46bcefaee81d880be66fc315`; candidate v2 `c78bab9e839a6f55cfec54cefa6ec8d9`; production-v2 trước rollback `4c0a933a8787232fde4a727d79983ad9`.
- **Cách promote và rollback `production`:** Dùng Langfuse prompt label, không sửa code: chuyển `production` sang version 2, chạy request `req-face2002` và xác nhận trace metadata `prompt_label=production`, `prompt_version=2`; sau đó chuyển `production` về version 1. Trạng thái cuối là v1=`baseline, production`, v2=`candidate, latest`.

## 6. Dashboard, SLO và alerts

- **Dashboard và sáu panel:** Dashboard runtime tại `/dashboard` đọc `data/logs.jsonl`, dùng time range 60 phút và refresh 30 giây. Sáu panel gồm latency P50/P95/P99 + TTFT P95, traffic, error rate + retrieval success, cost, input/output token và quality proxy; mỗi panel hiển thị đơn vị cùng threshold từ `config/dashboard.yaml`.
- **SLO và lý do chọn:** Trong cửa sổ 28 ngày, 99.5% request phải có `response_sent` và `latency_ms <= 3000`. Baseline CP2 có P95 1729 ms nên ngưỡng 3000 ms bảo vệ tail latency nhưng vẫn chừa biên cho dao động fake LLM/retrieval. Guardrails bổ sung: error rate <=2%, cost <=2.5 USD/ngày, quality trung bình >=0.75 và retrieval success >=90%.
- **Cách tính error budget:** Target 99.5% cho phép 0.5% request không đạt. Với 10,000 request, error budget là `10,000 × (1 - 0.995) = 50` request lỗi hoặc chậm hơn 3000 ms.
- **Ba alert và runbook tương ứng:** `HighLatencyP95` (>3000 ms trong 5m, warning), `HighErrorRate` (>2% trong 5m, critical) và `LowQualityScore` (<0.75 trong 10m, warning). Cả ba gửi Slack `#k4-l3b-alerts`, owner `student-2A202602580`, và có quy trình Metrics → Logs → Traces cùng mitigation tại `docs/alerts.md`.

> Ví dụ cách viết error budget: "SLO 99.5% trong 28 ngày nghĩa là error budget 0.5%. Nếu workload có 10,000 request thì tối đa 50 request được phép lỗi hoặc chậm hơn ngưỡng SLO."

## 7. Điều tra challenge

- **Challenge ID:** `day13-k4-l3b-monitoring-llmops-v1`.
- **Khoảng thời gian điều tra:** workload challenge chạy từ 14:28:04 đến 14:28:18 ngày 30/09/2026 (Asia/Bangkok, UTC+07:00); incident được tắt lúc 14:35:12 cùng ngày.
- **Triệu chứng từ metrics:** 5/5 request trả HTTP 200 nhưng latency ứng dụng lần lượt là 2653, 2653, 2654, 2655 và 2655 ms; P50=2654 ms, P95=2655 ms, vượt ngưỡng challenge 2000 ms. TTFT P95 vẫn là 50 ms, retrieval success 100% và error count bằng 0, nên đây là suy giảm latency chứ không phải lỗi request.
- **Log line và correlation ID liên quan:** dòng 63–64 trong `data/logs.jsonl` ghi `request_received` rồi `response_sent` của `correlation_id=req-62cdec8c`; request có `latency_ms=2655`, `ttft_ms=50`, `tool_name=retrieval`, `tool_success=true`, `tokens_in=36`, `tokens_out=81`, `cost_usd=0.001323` và `quality_score=0.9`.
- **Trace ID và span gây ảnh hưởng:** trace `deaebe6b65ce78307a8cd655879d29e1` có cùng `correlation_id=req-62cdec8c`. Root `lab-agent-run` mất khoảng 2658 ms; child span `retrieval` mất 2501 ms, trong khi `generation` chỉ mất 154 ms.
- **Root cause:** retrieval bị tăng độ trễ khoảng 2.5 giây. Bằng chứng là retrieval chiếm gần toàn bộ thời gian của root span, còn generation, TTFT, token, cost, quality và tỉ lệ thành công vẫn bình thường; vì vậy prompt/model không phải nguồn regression.
- **Fix action:** tắt incident `rag_slow` bằng `python scripts/inject_incident.py --disable` để khôi phục retrieval. Trong môi trường production, hành động tương đương là rollback cấu hình/deployment retrieval gây chậm, kiểm tra vector store và áp dụng timeout/fallback trước khi mở lại traffic đầy đủ.
- **Preventive measure:** cảnh báo theo cả latency P95 toàn request và latency riêng của retrieval; thêm timeout, circuit breaker/cache fallback cho retrieval; duy trì runbook Metrics → Logs → Traces và chạy load test có regression threshold trước khi deploy thay đổi retrieval.

> Gợi ý cách viết ngắn, không thay cho evidence thực tế: "Metric cho thấy `[latency/error/cost/quality]` bất thường trong `[khoảng thời gian]`. Log line `[event]` có `correlation_id=[...]` đại diện cho request bị ảnh hưởng. Trace cùng `correlation_id` cho thấy span `[retrieval/generation/prompt/tool]` có dấu hiệu `[chậm/lỗi/token tăng]`. Root cause là `[nguyên nhân suy ra từ evidence]`. Fix action là `[hành động khôi phục]`; preventive measure là `[alert/runbook/test/guardrail để ngăn tái diễn]`."

## 8. Giải thích và tự đánh giá

- **Một quyết định kỹ thuật quan trọng và lý do:** Dùng `contextvars` kết hợp middleware để tạo hoặc nhận `x-request-id` một lần ở biên HTTP, sau đó bind cùng `correlation_id` vào structured log và metadata của mọi observation. Cách này giữ được quan hệ giữa các nguồn quan sát mà không phải truyền ID thủ công qua từng hàm, đồng thời xóa context ở đầu request để tránh rò dữ liệu giữa các request đồng thời.
- **Một lỗi/blocker đã gặp:** Môi trường `.venv` hiện có đầy đủ Python và dependencies nhưng thiếu `Scripts/Activate.ps1`, nên PowerShell không thể kích hoạt bằng lệnh thông thường. Trong lúc kiểm tra CP3, kết nối Langfuse API cũng từng gián đoạn tạm thời.
- **Cách tìm nguyên nhân và xử lý:** Kiểm tra trực tiếp `.venv/Scripts` xác nhận `python.exe` tồn tại nhưng `Activate.ps1` không có; thay vì tạo lại môi trường và có nguy cơ làm thay đổi dependencies, mọi lệnh được chạy bằng `./.venv/Scripts/python.exe`. Với Langfuse, giữ nguyên dữ liệu local, thử lại API sau khi kết nối phục hồi và chỉ lấy các trường cần thiết để đối chiếu trace.
- **Cách hiểu luồng Metrics → Logs → Traces:** Metrics cho biết triệu chứng và cửa sổ thời gian, ví dụ P95 tăng lên 2655 ms. Từ cửa sổ đó, structured log cung cấp một request cụ thể qua `correlation_id=req-62cdec8c`. Tìm cùng ID trong Langfuse dẫn đến trace `deaebe6b65ce78307a8cd655879d29e1`; so sánh child spans cho thấy retrieval 2501 ms trong khi generation 154 ms, từ đó kết luận retrieval là bước gây chậm.
- **Vai trò của prompt version, token/cost, SLO hoặc rollback trong vận hành LLM:** Prompt version và label cho phép truy ra chính xác cấu hình prompt của từng request và rollback `production` mà không sửa code. Token và cost giúp phát hiện output phình hoặc chi phí tăng dù request vẫn thành công. SLO biến kỳ vọng vận hành thành ngưỡng đo được, còn error budget cho biết mức vi phạm có thể chấp nhận trước khi phải ưu tiên độ ổn định hơn thay đổi mới.
- **Điều quan trọng nhất đã học:** Một dashboard chỉ phát hiện được triệu chứng; kết luận root cause cần chuỗi bằng chứng nhất quán từ metric đến log có correlation ID rồi đến trace/span. Observability có giá trị khi các tín hiệu liên kết được với nhau và hỗ trợ một hành động khôi phục có thể kiểm chứng.
- **Hạn chế hoặc phần chưa hoàn thành, nếu có:** Logic LLM và retrieval trong lab là mô phỏng nên latency, token, cost và quality proxy không đại diện cho production thật. Dashboard được tách thành hai ảnh để giữ đủ độ rõ của cả sáu panel; đây chỉ là giới hạn trình bày evidence, không ảnh hưởng dữ liệu hoặc validator.

## 9. Checklist trước khi nộp

- [x] Kết quả và evidence thuộc commit SHA cuối.
- [x] Tất cả ảnh/output mở được bằng đường dẫn tương đối.
- [x] Incident evidence nối đúng metric → log → trace.
- [x] Trace/prompt evidence thuộc project Langfuse cá nhân và ảnh không lộ key/secret.
- [x] Repository chạy lại được theo README.
- [x] Không có secret, API key, PII thô hoặc evidence của người khác/lớp khác.
- [ ] URL repo và commit SHA cuối đã được nộp trên LMS/Codelabs.
