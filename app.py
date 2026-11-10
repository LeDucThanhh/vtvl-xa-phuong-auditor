# -*- coding: utf-8 -*-
"""
Ứng dụng Web Dashboard & API Rà soát Chuyên môn Giờ làm việc và Phân bổ Nhân sự VTVL.
Chạy lệnh:
  python app.py
Mặc định mở tại: http://127.0.0.1:8050
"""

from pathlib import Path
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

from core.audit_pipeline import run_full_audit
from exporters.excel_report_builder import build_excel_audit_report

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
EXPORT_DIR = BASE_DIR / "ket_qua_ra_soat"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="VTVL Workload & Headcount Auditor")


class AuditPathRequest(BaseModel):
    file_path: str


@app.get("/", response_class=HTMLResponse)
async def index():
    html_path = BASE_DIR / "templates" / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


@app.post("/api/audit-path")
async def audit_by_path(req: AuditPathRequest):
    try:
        result = run_full_audit(req.file_path)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/audit-upload")
async def audit_upload(request: Request, filename: str = Query("uploaded_vtvl.xlsx")):
    try:
        body = await request.body()
        safe_name = Path(filename).name
        saved_path = UPLOAD_DIR / safe_name
        saved_path.write_bytes(body)
        result = run_full_audit(str(saved_path))
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/export-excel")
async def export_excel(file_path: str = Query(...)):
    try:
        result = run_full_audit(file_path)
        stem = Path(file_path).stem
        out_file = EXPORT_DIR / f"Bao_cao_Ra_soat_Chuyen_mon_Gio_VTVL_{stem}.xlsx"
        build_excel_audit_report(result, str(out_file))
        return FileResponse(
            path=str(out_file),
            filename=out_file.name,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8050)
