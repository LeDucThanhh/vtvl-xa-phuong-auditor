# -*- coding: utf-8 -*-
"""
Nhận diện xã/phường từ tên file Excel (hoặc nội dung biểu D1/C1) và tra biên chế giao năm 2026
theo Quyết định số 2398/QĐ-UBND ngày 04/10/2026 của UBND tỉnh Hà Tĩnh (dữ liệu ở core/qd2398_data.py).
"""

import re
import unicodedata
from typing import Any, Dict, List, Optional

from .qd2398_data import BIEN_CHE_CAP_TINH, BIEN_CHE_CAP_XA, QD_NGAY, QD_SO_HIEU


def remove_accents(text: str) -> str:
    if not text:
        return ""
    text = text.replace("đ", "d").replace("Đ", "D")
    norm = unicodedata.normalize("NFD", text)
    return "".join(c for c in norm if unicodedata.category(c) != "Mn")


def normalize_key(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", remove_accents(text).lower()).strip()


# Từ khóa dài trước (vd 'bac hong linh', 'son kim 1') để tránh khớp nhầm từ khóa ngắn.
_SORTED_UNITS = sorted(BIEN_CHE_CAP_XA, key=lambda u: max(len(k) for k in u["keywords"]), reverse=True)


def _build_tinh_units() -> List[Dict[str, Any]]:
    """Cấp tỉnh: từ khóa dài trước; thêm dạng rút gọn 'so + 2 từ' (vd 'so nong nghiep', 'so van hoa') cho Sở có tên dài."""
    units = []
    for u in BIEN_CHE_CAP_TINH:
        u = dict(u)
        kws = list(u["keywords"])
        for k in list(kws):
            parts = k.split()
            if parts[0] == "so" and len(parts) > 4:
                kws.append(" ".join(parts[:3]))
        u["keywords"] = list(dict.fromkeys(kws))
        units.append(u)
    return sorted(units, key=lambda u: max(len(k) for k in u["keywords"]), reverse=True)


_SORTED_TINH = _build_tinh_units()


def _match_text(norm_text: str, units=None) -> Optional[Dict[str, Any]]:
    if not norm_text:
        return None
    tokens = norm_text.split()
    for unit in (units if units is not None else _SORTED_UNITS):
        for kw in unit["keywords"]:
            if " " in kw:
                if re.search(r"\b" + re.escape(kw) + r"\b", norm_text):
                    return unit
            elif kw in tokens:
                # dạng viết liền (KYHOA, XUANLOC, SONKIM1): phải trùng nguyên một token của tên file
                return unit
    return None


def lookup_cap_tinh(file_name: str, unit_texts: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
    """Nhận diện Sở/ngành cấp tỉnh từ 'Nơi tính BC' (D1) rồi tên file. Chỉ khớp tên đầy đủ (có 'Sở ...', 'Thanh tra tỉnh'...)."""
    for t in list(unit_texts or [])[:50] + [file_name or ""]:
        unit = _match_text(normalize_key(t), _SORTED_TINH)
        if unit is not None:
            return unit
    return None


def lookup_bien_che_giao(
    file_name: str,
    positions: Optional[List[Dict[str, Any]]] = None,
    d1_rows: Optional[List[Dict[str, Any]]] = None,
) -> Optional[Dict[str, Any]]:
    """
    Ưu tiên tên file / 'Nơi tính BC': Sở-ngành cấp tỉnh trước, rồi xã/phường. Nếu không có thì quét nguồn D1 và tên VTVL (chỉ xã/phường).
    Trả về bản sao dữ liệu giao + thông tin văn bản, hoặc None nếu không nhận diện được.
    """
    d1_names = [r.get("noi_tinh_bc") or "" for r in (d1_rows or [])[:50]]
    unit = lookup_cap_tinh(file_name, d1_names)
    nguon = "tên file / nơi tính BC"
    if unit is None:
        unit = _match_text(normalize_key(file_name))
        nguon = "tên file"
    if unit is None:
        extra: List[str] = []
        for r in (d1_rows or [])[:10]:
            extra += [r.get("noi_tinh_bc") or "", r.get("nguon") or ""]
        for p in (positions or [])[:10]:
            extra.append(p.get("ten_vtvl") or "")
        unit = _match_text(normalize_key(" ".join(extra)))
        nguon = "nội dung biểu (D1/C1)"
    if unit is None:
        return None
    res = {k: (dict(v) if isinstance(v, dict) else v) for k, v in unit.items()}
    res.setdefault("cap", "xa")
    res["van_ban"] = f"QĐ {QD_SO_HIEU} ngày {QD_NGAY}"
    res["nhan_dien_tu"] = nguon
    return res
