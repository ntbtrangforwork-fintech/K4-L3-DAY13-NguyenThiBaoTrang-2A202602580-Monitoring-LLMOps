# Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert 1

- Tên: `HighLatencyP95`
- Severity: `warning`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: P95 của `response_sent.latency_ms`; SLO request tốt khi latency không quá 3000 ms.
- Điều kiện và thời gian duy trì: `p95(response_sent.latency_ms) > 3000` liên tục 5 phút.
- Ảnh hưởng tới người dùng: phần request chậm nhất khiến người dùng chờ quá ngưỡng phản hồi đã cam kết.
- Ba bước kiểm tra đầu tiên:
  1. Mở panel Latency, xác nhận P95/P99 và thời điểm bắt đầu vượt 3000 ms.
  2. Lọc `response_sent` trong khoảng đó, chọn log có `latency_ms` cao và lấy `correlation_id`.
  3. Mở trace cùng correlation ID, so sánh thời lượng `retrieval` và `generation` để khoanh vùng bước chậm.
- Mitigation tạm thời: tắt practice scenario nếu đang chạy; rollback prompt mới nếu generation tăng token/latency; giảm tải hoặc khôi phục retrieval config theo evidence.
- Owner: `student-2A202602580`

## Alert 2

- Tên: `HighErrorRate`
- Severity: `critical`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: tỷ lệ `request_failed / request_received`; guardrail tối đa 2%.
- Điều kiện và thời gian duy trì: `error_rate_pct > 2` liên tục 5 phút.
- Ảnh hưởng tới người dùng: nhiều request không trả được câu trả lời thành công.
- Ba bước kiểm tra đầu tiên:
  1. Mở panel Errors, xác nhận error rate, loại lỗi và retrieval success.
  2. Lọc `request_failed`, nhóm theo `error_type`, rồi chọn một correlation ID đại diện.
  3. Mở trace tương ứng, kiểm tra span lỗi và `status_message` để xác định dependency hoặc bước thất bại.
- Mitigation tạm thời: vô hiệu hóa scenario/dependency lỗi, chuyển sang fallback an toàn hoặc rollback cấu hình/prompt liên quan; xác nhận error rate phục hồi trước khi đóng alert.
- Owner: `student-2A202602580`

## Alert 3

- Tên: `LowQualityScore`
- Severity: `warning`
- Duration: `10m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: trung bình `response_sent.quality_score`; guardrail tối thiểu 0.75.
- Điều kiện và thời gian duy trì: `mean(response_sent.quality_score) < 0.75` liên tục 10 phút.
- Ảnh hưởng tới người dùng: hệ thống vẫn trả lời nhưng câu trả lời có dấu hiệu thiếu context hoặc không đạt chất lượng mong đợi.
- Ba bước kiểm tra đầu tiên:
  1. Mở panel Quality, xác nhận thời điểm và phạm vi score giảm.
  2. Lọc log có `quality_score` thấp, so sánh feature/model/prompt version và lấy correlation ID.
  3. Mở trace tương ứng, kiểm tra retrieval output, prompt metadata và generation token/output preview đã scrub.
- Mitigation tạm thời: rollback label `production` về prompt baseline nếu regression trùng version mới; kiểm tra retrieval corpus và bật fallback đã kiểm chứng.
- Owner: `student-2A202602580`
