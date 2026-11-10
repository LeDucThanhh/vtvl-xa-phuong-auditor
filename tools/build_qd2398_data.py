# -*- coding: utf-8 -*-
"""
Sinh file core/qd2398_data.py từ các phụ lục .docx kèm Quyết định số 2398/QĐ-UBND ngày 04/10/2026
của UBND tỉnh Hà Tĩnh (file tên "Quyet-dinh-giao-bien-che-554...").

Chạy:  python tools/build_qd2398_data.py "<thư mục chứa các Phu-luc-*.docx>"
Cần: pip install python-docx
"""

import pprint
import re
import sys
import unicodedata
from pathlib import Path

import docx

PL1 = "Phu-luc-1-Cong-chuc-541.docx"
PL2 = "Phu-luc-2-Vien-chuc-nhom-3.4-963.docx"
PL4 = "Phu-luc-4-bien-che-giao-duc-nam-hoc-26-27.docx"


def strip_accents(s: str) -> str:
    s = s.replace("đ", "d").replace("Đ", "D")
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def key_of(name: str) -> str:
    """Khóa so khớp tên đơn vị: bỏ 'Xã/Phường', bỏ dấu, chữ thường."""
    k = strip_accents(name).lower().strip()
    k = re.sub(r"^(xa|phuong)\s+", "", k)
    return re.sub(r"[^a-z0-9]+", " ", k).strip()


def num(x: str) -> int:
    x = (x or "").strip().replace(".", "")
    return int(x) if x.isdigit() else 0


def table_rows(path: Path):
    d = docx.Document(str(path))
    return [[[c.text.strip() for c in r.cells] for r in t.rows] for t in d.tables]


def main(folder: str):
    base = Path(folder)
    t1 = table_rows(base / PL1)[1]
    i = next(k for k, r in enumerate(t1) if r[0] == "II")
    cap_xa = [r for r in t1[i + 1:] if r[0].isdigit()]
    assert len(cap_xa) == 69, len(cap_xa)

    units = {}
    for r in cap_xa:
        ten = r[1].strip()
        if not re.match(r"^(Xã|Phường)\s", ten):
            ten = "Xã " + ten
        k = key_of(ten)
        units[k] = {
            "tt": int(r[0]),
            "ten": ten,
            "loai": "Phường" if ten.startswith("Phường") else "Xã",
            "cong_chuc": {"tong": num(r[2]), "chinh_thuc": num(r[3]), "doi_du": num(r[4]), "hd111": num(r[5])},
        }

    # --- Phụ lục 2: Trạm y tế & Trung tâm dịch vụ tổng hợp cấp xã
    t2 = table_rows(base / PL2)[1]
    marks = [(k, r[0], r[1]) for k, r in enumerate(t2) if r[0] in ("VI", "B")]
    assert [m[2] for m in marks][0].startswith("Trạm Y tế"), marks
    a, b, c = (m[0] for m in marks[:3])

    def pl2_row(r):
        note = r[7] if len(r) > 7 else ""
        m = re.search(r"(\d+)\s*H[ĐD]\s*3604", note, re.I)
        return {
            "tong": num(r[2]), "chinh_thuc": num(r[3]), "doi_du": num(r[4]),
            "hd235": num(r[5]), "tu_dam_bao": num(r[6]),
            "hd3604": int(m.group(1)) if m else 0,
        }

    for r in t2[a + 1:b]:
        if r[0].isdigit():
            units[key_of(r[1])]["tram_y_te"] = pl2_row(r)
    for r in t2[b + 1:c]:
        if r[0].isdigit():
            units[key_of(r[1])]["ttdvth"] = pl2_row(r)

    # --- Phụ lục 4A/4B/4C: Mầm non / Tiểu học / THCS (năm học 2026-2027)
    t4 = table_rows(base / PL4)
    for tbl_idx, field, has_doi in ((1, "mam_non", False), (3, "tieu_hoc", True), (5, "thcs", True)):
        for r in t4[tbl_idx]:
            if not r[0].isdigit():
                continue
            o = 1 if has_doi else 0  # cột 'Đội' chỉ có ở TH và THCS
            gv_tong = num(r[4 + o]); gv_ct = num(r[5 + o]); gv_dd = num(r[6 + o])
            units[key_of(r[1])][field] = {
                "so_truong": num(r[2]), "quan_ly": num(r[3]),
                "giao_vien": gv_tong, "gv_chinh_thuc": gv_ct, "gv_doi_du": gv_dd,
                "cmdc": num(r[7 + o]), "tong": num(r[8 + o]),
            }

    empty = {"tong": 0, "chinh_thuc": 0, "doi_du": 0, "hd235": 0, "tu_dam_bao": 0, "hd3604": 0}
    empty_gd = {"so_truong": 0, "quan_ly": 0, "giao_vien": 0, "gv_chinh_thuc": 0, "gv_doi_du": 0, "cmdc": 0, "tong": 0}
    out = []
    for k, u in sorted(units.items(), key=lambda kv: kv[1]["tt"]):
        for f in ("tram_y_te", "ttdvth"):
            u.setdefault(f, dict(empty))
        for f in ("mam_non", "tieu_hoc", "thcs"):
            u.setdefault(f, dict(empty_gd))
        base_kw = k
        kws = [base_kw]
        if u["ten"] == "Phường Trần Phú":
            kws.append("phuong tran phu")
        kws.append(base_kw.replace(" ", ""))  # dạng viết liền: KYHOA, XUANLOC...
        u["keywords"] = list(dict.fromkeys(kws))
        out.append(u)

    # --- Phụ lục 1 mục I: cơ quan hành chính cấp tỉnh (Sở, ngành) + hợp đồng Nghị định 111
    i1 = next(k for k, r in enumerate(t1) if r[0] == "I")
    i2 = next(k for k, r in enumerate(t1) if r[0] == "II")
    tinh_rows = t1[i1 + 1:i2]
    assert sum(num(r[2]) for r in tinh_rows if r[0].isdigit()) == 1227
    tinh = []
    parent = None
    pending_subs = []

    def giao_of(r):
        return {"tong": num(r[2]), "chinh_thuc": num(r[3]), "doi_du": num(r[4]), "hd111": num(r[5])}

    def short(n):
        n = re.sub(r"\s+tỉnh Hà Tĩnh$", "", n.strip())
        return n

    def flush():
        """Sở có chi cục/đơn vị con: mục cha lấy phần 'Cơ quan Sở/Văn phòng Sở'; các chi cục là đơn vị riêng."""
        nonlocal parent
        if parent is None:
            return
        pr, subs = parent
        main = next((x for x in subs if re.match(r"^(Cơ quan Sở|Văn phòng Sở)", x[1])), None)
        entry = {"tt": int(pr[0]), "ten": pr[1].strip(), "cap": "tinh", "loai": "Sở/ngành cấp tỉnh",
                 "cong_chuc": giao_of(main if main else pr)}
        if subs:
            entry["tong_ca_so"] = giao_of(pr)
            entry["gom_don_vi"] = [x[1] for x in subs]
        entry["keywords"] = [key_of(short(pr[1])).replace("xa ", "xa ")]
        tinh.append(entry)
        for x in subs:
            if x is main:
                continue
            tinh.append({"tt": int(pr[0]), "ten": f"{short(x[1])} ({pr[1].strip()})", "cap": "tinh",
                         "loai": "Đơn vị trực thuộc Sở", "cong_chuc": giao_of(x),
                         "keywords": [key_of(short(x[1]))]})
        parent = None

    for r in tinh_rows:
        if r[0].isdigit():
            flush()
            parent = (r, [])
        elif re.match(r"^\d+\.\d+$", r[0]) and parent is not None:
            parent[1].append(r)
    flush()
    assert sum(u["cong_chuc"]["tong"] for u in tinh if "tong_ca_so" not in u) > 0
    for u in tinh:
        u["keywords"] = list(dict.fromkeys(u["keywords"] + [k.replace(" ", "") for k in u["keywords"] if len(k) > 14]))

    # kiểm tra đối chiếu tổng với văn bản
    assert sum(u["cong_chuc"]["tong"] for u in out) == 2579
    assert sum(u["tram_y_te"]["tong"] for u in out) == 1823
    assert sum(u["ttdvth"]["tong"] for u in out) == 591
    assert sum(u["mam_non"]["tong"] for u in out) == 5638
    assert sum(u["tieu_hoc"]["tong"] for u in out) == 6873
    assert sum(u["thcs"]["tong"] for u in out) == 5721

    header = '''# -*- coding: utf-8 -*-
"""
Biên chế giao năm 2026 cho 69 xã, phường tỉnh Hà Tĩnh theo
Quyết định số 2398/QĐ-UBND ngày 04/10/2026 của UBND tỉnh (thay thế QĐ 434-QĐ/TU trong tool này).

FILE NÀY ĐƯỢC SINH TỰ ĐỘNG bởi tools/build_qd2398_data.py từ các phụ lục .docx - không sửa tay.
  - Phụ lục 1: biên chế cán bộ, công chức (HĐND-UBND cấp xã) + hợp đồng Nghị định 111  -> cong_chuc
  - Phụ lục 2: viên chức Trạm y tế xã -> tram_y_te; Trung tâm Dịch vụ tổng hợp cấp xã -> ttdvth
  - Phụ lục 4A/4B/4C: người làm việc Mầm non / Tiểu học / THCS năm học 2026-2027
Cấp tỉnh (Phụ lục 1 mục I): 1.227 công chức, HĐ 111 = 122 (xem BIEN_CHE_CAP_TINH ở cuối file).
Tổng cấp xã: công chức 2.579 (chính thức 2.459 + dôi dư 120; HĐ 111 = 29); Trạm y tế 1.823; TT DVTH 591;
Mầm non 5.638; Tiểu học 6.873; THCS 5.721.
"""

from typing import Any, Dict, List

QD_SO_HIEU = "2398/QĐ-UBND"
QD_NGAY = "04/10/2026"

BIEN_CHE_CAP_XA: List[Dict[str, Any]] = '''
    body = pprint.pformat(out, width=140, sort_dicts=False)
    body_tinh = pprint.pformat(tinh, width=140, sort_dicts=False)
    dst = Path(__file__).resolve().parent.parent / "core" / "qd2398_data.py"
    dst.write_text(
        header + body
        + "\n\n# Phụ lục 1 mục I: cơ quan hành chính cấp tỉnh (Sở, ngành). Sở có chi cục: mục cha lấy phần 'Cơ quan Sở/Văn phòng Sở',\n"
        + "# 'tong_ca_so' là tổng cả Sở (gồm chi cục), các chi cục là đơn vị riêng.\n"
        + "BIEN_CHE_CAP_TINH: List[Dict[str, Any]] = " + body_tinh + "\n",
        encoding="utf-8",
    )
    print("Đã ghi", dst, "-", len(out), "xã/phường,", len(tinh), "đơn vị cấp tỉnh")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Cách dùng: python tools/build_qd2398_data.py <thư mục chứa các Phu-luc-*.docx>")
        sys.exit(1)
    main(sys.argv[1])
