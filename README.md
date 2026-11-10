# VTVL xã, phường Auditor

Công cụ rà soát chuyên môn bộ biểu Vị trí việc làm (VTVL): giờ làm việc so với chuẩn 1.904 giờ/người/năm,
đề xuất thêm/bớt người, cân đối giữa các ban/bộ phận và đối chiếu biên chế giao năm 2026.

Hỗ trợ file Excel của: khối Đảng/MTTQ, chính quyền xã/phường (HĐND-UBND), đơn vị sự nghiệp cấp xã
(Trạm Y tế, Trung tâm Dịch vụ tổng hợp, trường học) và Sở/ngành cấp tỉnh.

Biên chế giao lấy từ Quyết định số 2398/QĐ-UBND ngày 04/10/2026 của UBND tỉnh Hà Tĩnh (`core/qd2398_data.py`).

## Chạy trên máy

```bash
pip install -r requirements.txt
python app.py            # mở http://127.0.0.1:8050, nhập đường dẫn hoặc chọn file .xlsx
python run_audit_cli.py "<đường dẫn file Excel>"   # xuất báo cáo Excel vào ket_qua_ra_soat/
```

## Deploy lên Vercel (miễn phí)

1. Vào vercel.com, đăng nhập bằng GitHub, chọn **Add New → Project**, chọn repo này, bấm **Deploy** (không cần chỉnh gì,
   cấu hình nằm trong `vercel.json` và `api/index.py`).
2. Mở link Vercel cấp, bấm "Chọn file khác (.xlsx)".

Cách hoạt động: trình duyệt đọc file Excel bằng SheetJS, chỉ trích 6 biểu cần (C1, A2, B1, C3, D1, D2), nén gzip rồi gửi lên
(file 40 MB thường chỉ còn vài chục KB), nên không vướng giới hạn 4,5 MB của Vercel. File gốc không rời máy người dùng;
máy chủ phân tích trong bộ nhớ và không lưu gì. Trên Vercel, chức năng nhập đường dẫn file bị tắt.

## Cấu trúc

- `core/` - đọc Excel, phân loại ban/bộ phận (`dept_parser.py`, `xa_titles.py`), các bộ phân tích, đối chiếu biên chế (`analyzer_bienche.py`)
- `core/qd2398_data.py` - dữ liệu biên chế giao, sinh bằng `tools/build_qd2398_data.py` từ các phụ lục .docx
- `exporters/` - xuất báo cáo Excel; `templates/` - giao diện web; `tests/` - kiểm tra phân loại và đối chiếu

## Lưu ý dữ liệu

File Excel nhân sự (`uploads/`, `ket_qua_ra_soat/`, `*.xlsx`) bị `.gitignore` chặn, không đưa lên repo.
