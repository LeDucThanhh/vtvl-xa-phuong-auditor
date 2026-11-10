# -*- coding: utf-8 -*-
"""
Module 4: Đối chiếu số người D1 (hiện có) và C3 (đề xuất) với biên chế giao năm 2026 theo QĐ 2398/QĐ-UBND
cho khối chính quyền và đơn vị sự nghiệp cấp xã, phường (công chức, hợp đồng 111, TT Dịch vụ tổng hợp,
Trạm Y tế, Mầm non, Tiểu học, THCS).

Chỉ đối chiếu các cấu phần CÓ vị trí việc làm trong file; khối Đảng/MTTQ không thuộc phạm vi QĐ này nên bị bỏ qua.
"""

from typing import Any, Dict, List, Optional

from .qd2398_data import QD_NGAY, QD_SO_HIEU

MODULE_NAME = "4. Đối chiếu biên chế giao (QĐ 2398)"


def _is_contract(pos: Dict[str, Any]) -> bool:
    t = (pos.get("loai_nhan_luc") or "").lower()
    return "hợp đồng" in t or "hđ" in t.split()


def _is_vien_chuc(pos: Dict[str, Any]) -> bool:
    return "viên chức" in (pos.get("loai_nhan_luc") or "").lower()


def _giao(unit: Dict[str, Any], section: str) -> Dict[str, int]:
    s = unit.get(section) or {}
    tong = int(s.get("tong", 0))
    return {"tong": tong, "chinh_thuc": int(s.get("chinh_thuc", tong)), "doi_du": int(s.get("doi_du", 0))}


def _giao_truong(unit: Dict[str, Any], section: str) -> Dict[str, int]:
    s = unit.get(section) or {}
    tong = int(s.get("tong", 0))
    dd = int(s.get("gv_doi_du", 0))
    return {"tong": tong, "chinh_thuc": tong - dd, "doi_du": dd}


def _components_tinh(unit: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Sở/ngành cấp tỉnh: Phụ lục 1 mục I - biên chế cán bộ, công chức và hợp đồng Nghị định 111."""
    hd111 = int(unit["cong_chuc"]["hd111"])
    return [
        {"code": "CONG_CHUC", "label": "Cán bộ, công chức cơ quan cấp tỉnh",
         "pred": lambda p: p["khoi"] == "CAP_TINH" and not _is_contract(p),
         "giao": _giao(unit, "cong_chuc"), "src": "Phụ lục 1 (mục I - cấp tỉnh)"},
        {"code": "HD111", "label": "Hợp đồng theo Nghị định 111/2022/NĐ-CP",
         "pred": lambda p: p["khoi"] == "CAP_TINH" and _is_contract(p),
         "giao": {"tong": hd111, "chinh_thuc": hd111, "doi_du": 0}, "src": "Phụ lục 1 (mục I - cấp tỉnh)"},
    ]


def _components(unit: Dict[str, Any]) -> List[Dict[str, Any]]:
    if unit.get("cap") == "tinh":
        return _components_tinh(unit)
    def is_cc(p):  # cán bộ, công chức khối chính quyền (không tính hợp đồng, không tính viên chức của TT HCC)
        return (p["khoi"] == "CHINH_QUYEN" and not _is_contract(p)
                and not (p["dept_code"] == "TTHCC" and _is_vien_chuc(p)))

    hd111 = int(unit["cong_chuc"]["hd111"])
    return [
        {"code": "CONG_CHUC", "label": "Cán bộ, công chức khối chính quyền (HĐND-UBND)", "pred": is_cc,
         "giao": _giao(unit, "cong_chuc"), "src": "Phụ lục 1"},
        {"code": "HD111", "label": "Hợp đồng theo Nghị định 111/2022/NĐ-CP",
         "pred": lambda p: p["khoi"] == "CHINH_QUYEN" and _is_contract(p),
         "giao": {"tong": hd111, "chinh_thuc": hd111, "doi_du": 0}, "src": "Phụ lục 1"},
        {"code": "TTDVTH", "label": "Viên chức Trung tâm Dịch vụ tổng hợp",
         "pred": lambda p: not _is_contract(p) and (p.get("unit_profile") == "TTDVTH" or (p["dept_code"] == "TTHCC" and _is_vien_chuc(p))),
         "giao": _giao(unit, "ttdvth"), "src": "Phụ lục 2"},
        {"code": "TYT", "label": "Viên chức Trạm Y tế",
         "pred": lambda p: p.get("unit_profile") == "TYT" and not _is_contract(p),
         "giao": _giao(unit, "tram_y_te"), "src": "Phụ lục 2"},
        {"code": "GDMN", "label": "Người làm việc Trường Mầm non (2026-2027)",
         "pred": lambda p: p.get("unit_profile") == "GDMN", "giao": _giao_truong(unit, "mam_non"), "src": "Phụ lục 4A",
         "partial": True},
        {"code": "GDTH", "label": "Người làm việc Trường Tiểu học (2026-2027)",
         "pred": lambda p: p.get("unit_profile") == "GDTH", "giao": _giao_truong(unit, "tieu_hoc"), "src": "Phụ lục 4B",
         "partial": True},
        {"code": "GDTHCS", "label": "Người làm việc Trường THCS (2026-2027)",
         "pred": lambda p: p.get("unit_profile") == "GDTHCS", "giao": _giao_truong(unit, "thcs"), "src": "Phụ lục 4C",
         "partial": True},
        {"code": "GD_TH_THCS", "label": "Người làm việc Trường TH&THCS liên cấp (2026-2027) - so với Tiểu học + THCS của xã",
         "pred": lambda p: p.get("unit_profile") == "GD_LIENCAP",
         "giao": {k: _giao_truong(unit, "tieu_hoc")[k] + _giao_truong(unit, "thcs")[k] for k in ("tong", "chinh_thuc", "doi_du")},
         "src": "Phụ lục 4B+4C", "partial": True},
    ]


def analyze_bien_che_giao(data: Dict[str, Any], unit: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    positions: List[Dict[str, Any]] = data["positions"]
    comparisons: List[Dict[str, Any]] = []
    findings: List[Dict[str, Any]] = []
    notes: List[str] = []

    if unit is None:
        return {
            "comparisons": [],
            "findings": [],
            "notes": ["Chưa nhận diện được xã/phường hoặc Sở/ngành từ tên file nên chưa đối chiếu biên chế giao."],
        }

    if unit.get("tong_ca_so"):
        notes.append(
            f"{unit['ten']}: số giao dùng để đối chiếu là phần Cơ quan/Văn phòng Sở ({unit['cong_chuc']['tong']} biên chế); "
            f"tổng cả Sở gồm các chi cục/đơn vị trực thuộc là {unit['tong_ca_so']['tong']} biên chế (mỗi chi cục có số giao riêng)."
        )
    covered = set()
    for comp in _components(unit):
        code, label, src, giao = comp["code"], comp["label"], comp["src"], comp["giao"]
        group = [p for p in positions if comp["pred"](p)]
        if not group:
            continue
        covered.update(p["ma_vtvl"] for p in group)
        if comp.get("partial"):
            notes.append(
                f"'{label}': số giao là của CẢ xã {unit['ten']} (có thể gồm nhiều trường); file này chỉ là một đơn vị, "
                f"cần cộng số D1/C3 của tất cả các file trường cùng xã trước khi kết luận vượt/không vượt."
            )
        d1 = sum(p["n_d1"] for p in group)
        c3 = sum(p["n_c3"] for p in group)
        tong, ct, dd = giao["tong"], giao["chinh_thuc"], giao["doi_du"]

        if tong == 0:
            status, sev = "QĐ KHÔNG GIAO", "CANH_BAO"
        elif c3 > tong + 1e-9:
            status, sev = "ĐỀ XUẤT VƯỢT TỔNG GIAO", "NGHIEM_TRONG"
        elif dd > 0 and c3 > ct + 1e-9:
            status, sev = "DÙNG CẢ PHẦN DÔI DƯ", "CANH_BAO"
        elif d1 > tong:
            status, sev = "HIỆN CÓ VƯỢT GIAO", "CANH_BAO"
        else:
            status, sev = "TRONG CHỈ TIÊU", "HOP_LY"

        comparisons.append({
            "code": code, "label": label, "nguon": src,
            "so_vtvl": len(group), "giao_tong": tong, "giao_chinh_thuc": ct, "giao_doi_du": dd,
            "n_d1": d1, "n_c3": c3, "con_lai_c3": tong - c3, "status": status, "severity": sev,
        })
        if sev == "HOP_LY":
            continue

        pos_list = "; ".join(f"{p['ma_vtvl']} ({p['n_c3']:g})" for p in group[:12]) + (" ..." if len(group) > 12 else "")
        if status == "QĐ KHÔNG GIAO":
            detail = (f"{unit['ten']} có {len(group)} vị trí thuộc '{label}' (D1={d1}, C3={c3:g}) "
                      f"nhưng QĐ {QD_SO_HIEU} không giao chỉ tiêu cho cấu phần này.")
            reco = "Kiểm tra lại việc xếp vị trí vào cấu phần hoặc đề nghị Sở Nội vụ xác nhận chỉ tiêu."
        elif status == "ĐỀ XUẤT VƯỢT TỔNG GIAO":
            detail = (f"Tổng đề xuất C3 của '{label}' là {c3:g} người, vượt tổng giao {tong} người "
                      f"(chính thức {ct} + dôi dư {dd}) theo {src} QĐ {QD_SO_HIEU}, vượt {c3 - tong:g} người. Các vị trí: {pos_list}.")
            reco = "Giảm đề xuất C3 về trong tổng giao hoặc giải trình/điều chỉnh vị trí; không đề xuất vượt chỉ tiêu được giao."
        elif status == "DÙNG CẢ PHẦN DÔI DƯ":
            detail = (f"Đề xuất C3 của '{label}' là {c3:g} người, lớn hơn phần giao chính thức {ct} "
                      f"(còn {dd} dôi dư chờ xử lý theo Điều 2 QĐ {QD_SO_HIEU}). Các vị trí: {pos_list}.")
            reco = "Không bố trí phần dôi dư thành định biên lâu dài; giữ ở mức chính thức, phần dôi dư xử lý theo lộ trình."
        else:
            detail = f"Nhân lực hiện có D1 của '{label}' là {d1} người, vượt tổng giao {tong} người ({src} QĐ {QD_SO_HIEU})."
            reco = "Rà soát D1 (trùng người, người đã chuyển/nghỉ) và xây dựng phương án xử lý số vượt."
        findings.append({
            "severity": sev,
            "category": f"{status.capitalize()} - {label}",
            "dept_name": label,
            "ma_vtvl": f"BIENCHE_{code}",
            "ten_vtvl": label,
            "cell_ref": "8. C3_NhuCau & 9. D1_NhanLuc (tổng theo cấu phần)",
            "current_value": f"D1 = {d1} | C3 = {c3:g} | Giao: tổng {tong} (chính thức {ct}, dôi dư {dd})",
            "benchmark": f"C3 ≤ tổng giao {tong} theo {src} - QĐ {QD_SO_HIEU} ngày {QD_NGAY}",
            "detail": detail,
            "recommendation": reco,
        })

    uncovered = [p for p in positions if p["ma_vtvl"] not in covered and p["khoi"] in ("CHINH_QUYEN", "SU_NGHIEP", "CAP_TINH")]
    if uncovered:
        notes.append(
            f"{len(uncovered)} vị trí khối chính quyền/sự nghiệp chưa gán được cấu phần để đối chiếu "
            f"(ví dụ: {uncovered[0]['ma_vtvl']} - {uncovered[0]['ten_vtvl']})."
        )
    if not comparisons:
        notes.append(
            "File không có vị trí thuộc khối chính quyền/sự nghiệp/cơ quan cấp tỉnh nên chưa có cấu phần nào để đối chiếu "
            "với QĐ 2398 (khối Đảng, MTTQ nằm ngoài phạm vi)."
        )
    return {"comparisons": comparisons, "findings": findings, "notes": notes}
