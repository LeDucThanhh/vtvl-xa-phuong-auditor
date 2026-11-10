# -*- coding: utf-8 -*-
"""
Ứng dụng Web Dashboard & API Rà soát Chuyên môn Giờ làm việc và Phân bổ Nhân sự VTVL.

Chạy trên máy:   python app.py          (mở http://127.0.0.1:8050)
Chạy trên Vercel: xem vercel.json + api/index.py

Trình duyệt đọc file Excel bằng SheetJS, chỉ trích các biểu cần thiết (C1, A2, B1, C3, D1, D2), nén gzip
rồi gửi lên /api/audit-sheets. File Excel gốc không được tải lên và máy chủ không lưu gì.
Endpoint đọc theo đường dẫn file (/api/audit-path, /api/export-excel) chỉ bật khi chạy trên máy cá nhân.
"""

import json
import os
import tempfile
import zlib
from pathlib import Path
from urllib.parse import quote

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, Response
from pydantic import BaseModel

from core.audit_pipeline import run_full_audit, run_full_audit_sheets
from exporters.excel_report_builder import build_excel_audit_report

BASE_DIR = Path(__file__).resolve().parent
XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
MAX_PAYLOAD_BYTES = 300 * 1024 * 1024  # giới hạn dữ liệu sau giải nén (chống gzip bomb)

# Đọc file theo đường dẫn trên máy chủ: chỉ dành cho chạy cá nhân. Tắt trên Vercel hoặc khi đặt VTVL_DISABLE_PATH=1.
PATH_MODE = not os.environ.get("VERCEL") and os.environ.get("VTVL_DISABLE_PATH", "") not in ("1", "true", "yes")

app = FastAPI(title="VTVL Workload & Headcount Auditor")
app.add_middleware(GZipMiddleware, minimum_size=1000)


class AuditPathRequest(BaseModel):
    file_path: str


def _report_name(file_name: str) -> str:
    stem = Path(file_name).stem or "VTVL"
    return f"Bao_cao_Ra_soat_Chuyen_mon_Gio_VTVL_{stem}.xlsx"


def _xlsx_response(data: bytes, name: str) -> Response:
    ascii_name = name.encode("ascii", "ignore").decode() or "Bao_cao_VTVL.xlsx"
    disp = f"attachment; filename=\"{ascii_name}\"; filename*=UTF-8''{quote(name)}"
    return Response(content=data, media_type=XLSX_MIME, headers={"Content-Disposition": disp})


def _build_report_bytes(result) -> bytes:
    fd, tmp = tempfile.mkstemp(suffix=".xlsx")
    os.close(fd)
    try:
        build_excel_audit_report(result, tmp)
        return Path(tmp).read_bytes()
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass


async def _read_payload(request: Request):
    body = await request.body()
    if not body:
        raise HTTPException(status_code=400, detail="Không nhận được dữ liệu.")
    if body[:2] == b"\x1f\x8b":
        d = zlib.decompressobj(16 + zlib.MAX_WBITS)
        body = d.decompress(body, MAX_PAYLOAD_BYTES)
        if d.unconsumed_tail:
            raise HTTPException(status_code=413, detail="Dữ liệu quá lớn.")
    try:
        payload = json.loads(body.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="Dữ liệu gửi lên không đúng định dạng.")
    if not isinstance(payload, dict) or not isinstance(payload.get("sheets"), dict):
        raise HTTPException(status_code=400, detail="Thiếu dữ liệu các biểu.")
    return payload


@app.get("/", response_class=HTMLResponse)
async def index():
    html_path = BASE_DIR / "templates" / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


@app.get("/api/config")
async def config():
    # Vercel giới hạn thân request khoảng 4,5 MB: trình duyệt kiểm tra trước để báo lỗi rõ ràng
    return {"path_mode": PATH_MODE, "max_payload_bytes": int(4.3 * 1024 * 1024) if os.environ.get("VERCEL") else None}


@app.post("/api/audit-sheets")
async def audit_sheets(request: Request):
    payload = await _read_payload(request)
    try:
        return JSONResponse(content=run_full_audit_sheets(payload))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/export-excel-sheets")
async def export_excel_sheets(request: Request):
    payload = await _read_payload(request)
    try:
        result = run_full_audit_sheets(payload)
        data = _build_report_bytes(result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _xlsx_response(data, _report_name(result["file_name"]))


if PATH_MODE:
    @app.post("/api/audit-path")
    async def audit_by_path(req: AuditPathRequest):
        try:
            return JSONResponse(content=run_full_audit(req.file_path))
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.get("/api/export-excel")
    async def export_excel(file_path: str = Query(...)):
        try:
            result = run_full_audit(file_path)
            data = _build_report_bytes(result)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
        return _xlsx_response(data, _report_name(file_path))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=os.environ.get("HOST", "127.0.0.1"), port=int(os.environ.get("PORT", "8050")))
