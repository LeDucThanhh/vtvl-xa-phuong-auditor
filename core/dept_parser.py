# -*- coding: utf-8 -*-
"""
Bộ phân tích và nhận diện Ban / Bộ phận / Khối từ Mã VTVL và Tên VTVL.
Hỗ trợ cả mô hình chính quyền địa phương 2 cấp (Đảng ủy, MTTQ, HĐND, UBND) và Sở/Ngành, Đơn vị sự nghiệp.
"""

import re
import unicodedata
from typing import Dict, Tuple

from .xa_titles import (
    CODE_TOKENS,
    GROUP_INDEX,
    KHOI_CHINH_QUYEN,
    KHOI_DANG,
    KHOI_KHAC,
    KHOI_MTTQ,
    KHOI_NAMES,
    KHOI_SU_NGHIEP,
    classify_by_title,
)


def _norm_token(text: str) -> str:
    t = (text or "").replace("đ", "d").replace("Đ", "D")
    t = "".join(c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn")
    return re.sub(r"[^A-Za-z0-9]+", "", t).upper()


_NORM_CODE_TOKENS: Dict[str, str] = {_norm_token(k): v for k, v in CODE_TOKENS.items()}

DEPT_MAPPING: Dict[str, str] = {
    "TT": "Thường trực Đảng ủy",
    "XDĐ": "Ban Xây dựng Đảng",
    "XDD": "Ban Xây dựng Đảng",
    "TC": "Ban Tổ chức",
    "TG": "Ban Tuyên giáo và Dân vận",
    "DV": "Ban Dân vận",
    "NC": "Ban Nội chính",
    "UBKT": "Cơ quan Ủy ban Kiểm tra",
    "KT": "Cơ quan Ủy ban Kiểm tra",
    "VP": "Văn phòng Đảng ủy",
    "VPĐU": "Văn phòng Đảng ủy",
    "CTUBMTTQ": "Cơ quan Ủy ban MTTQ & Đoàn thể",
    "PCTUBMTTQ": "Cơ quan Ủy ban MTTQ & Đoàn thể",
    "UBMTTQ": "Cơ quan Ủy ban MTTQ & Đoàn thể",
    "MTTQ": "Cơ quan Ủy ban MTTQ & Đoàn thể",
    "TTCT": "Trung tâm Chính trị",
    "HĐND": "Thường trực & các Ban HĐND",
    "HDND": "Thường trực & các Ban HĐND",
    "UBND": "Lãnh đạo UBND",
    "VPHĐND": "Văn phòng HĐND & UBND",
    "VPUBND": "Văn phòng HĐND & UBND",
    "VHXH": "Phòng Văn hóa - Xã hội",
    "KTHT": "Phòng Kinh tế, Hạ tầng & Đô thị",
    "TTHCC": "Trung tâm Phục vụ Hành chính công",
}
# Bộ phận khối chính quyền & sự nghiệp cấp xã (lấy từ core/xa_titles.py)
# DEPT_MAPPING (bản gốc) KHÔNG bị thay đổi để khối Đảng/MTTQ cho kết quả y hệt trước; tên hiển thị mở rộng đặt riêng:
DEPT_NAMES_EXT: Dict[str, str] = dict(DEPT_MAPPING)
for _code, (_label, _khoi, _c) in GROUP_INDEX.items():
    DEPT_NAMES_EXT[_code] = _label

# Khối của từng bộ phận Đảng / MTTQ
_DANG_CODES = {"TT", "XDĐ", "XDD", "TC", "TG", "DV", "NC", "UBKT", "KT", "VP", "VPĐU", "TTCT"}


def get_khoi(dept_code: str) -> str:
    """Khối của bộ phận: DANG / MTTQ / CHINH_QUYEN / SU_NGHIEP / KHAC."""
    if dept_code in GROUP_INDEX:
        return GROUP_INDEX[dept_code][1]
    if dept_code == "MTTQ":
        return KHOI_MTTQ
    if dept_code in _DANG_CODES:
        return KHOI_DANG
    return KHOI_KHAC


def get_khoi_name(khoi: str) -> str:
    return KHOI_NAMES.get(khoi, KHOI_NAMES[KHOI_KHAC])


def parse_department(ma_vtvl: str, ten_vtvl: str = "", chinh_quyen: bool = False) -> Tuple[str, str]:
    """
    Trả về (ma_ban_chuan, ten_ban_hien_thi) từ mã VTVL và tên VTVL.
    Ví dụ:
      'A27.103_XDĐ_CV01' -> ('XDĐ', 'Ban Xây dựng Đảng')
      'A27.103_KT_KTV'   -> ('UBKT', 'Cơ quan Ủy ban Kiểm tra')
      'I27.103_CTUBMTTQ' -> ('MTTQ', 'Cơ quan Ủy ban MTTQ & Đoàn thể')

    chinh_quyen=True (file thuộc khối chính quyền xã/phường) mới bật thêm nhận diện ký hiệu và chức danh chính quyền;
    mặc định False để file khối Đảng/MTTQ phân loại y hệt logic gốc.
    """
    if not ma_vtvl:
        return ("KHAC", "Bộ phận khác")

    code = str(ma_vtvl).strip()
    parts = code.split("_")
    unit_prefix = parts[0] if parts else ""

    if len(parts) >= 2:
        token = parts[1].upper()
        # Gom nhóm TT01, TT02 -> TT
        if re.match(r"^TT\d*$", token):
            return ("TT", DEPT_MAPPING["TT"])
        # Gom nhóm KT (Kiểm tra viên) vào UBKT
        if token in ("UBKT", "KT"):
            return ("UBKT", DEPT_MAPPING["UBKT"])
        # Gom nhóm MTTQ
        if "MTTQ" in token or unit_prefix.startswith("I"):
            return ("MTTQ", DEPT_MAPPING["MTTQ"])
        if token in DEPT_MAPPING:
            norm_code = "XDĐ" if token == "XDD" else token
            return (norm_code, DEPT_MAPPING[token])
        # Token khối chính quyền xã/phường (HĐND, UBND, VHXH, KTHT, TYT, MN...)
        ntok = _norm_token(token)
        if chinh_quyen:
            if ntok in _NORM_CODE_TOKENS:
                c = _NORM_CODE_TOKENS[ntok]
                return (c, DEPT_NAMES_EXT[c])
            if ntok.startswith("VP") and ("HDND" in ntok or "UBND" in ntok):
                return ("VPHĐND-UBND", DEPT_NAMES_EXT["VPHĐND-UBND"])
            if "HDND" in ntok:
                return ("HĐND", DEPT_NAMES_EXT["HĐND"])
            if "UBND" in ntok:
                return ("UBND", DEPT_NAMES_EXT["UBND"])

    # Fallback dựa trên tên VTVL
    name_lower = (ten_vtvl or "").lower()
    if "bí thư" in name_lower:
        return ("TT", DEPT_MAPPING["TT"])
    # Chức danh khối chính quyền / sự nghiệp cấp xã (chỉ xét khi tên không mang dấu hiệu của khối Đảng/MTTQ)
    is_dang_mttq = any(k in name_lower for k in ("đảng", "cấp ủy", "mttq", "mặt trận", "ủy ban kiểm tra", "kiểm tra viên"))
    if chinh_quyen and not is_dang_mttq:
        grp = classify_by_title(ten_vtvl)
        if grp:
            return (grp, DEPT_NAMES_EXT[grp])
    if "xây dựng đảng" in name_lower or "tổ chức" in name_lower or "tuyên giáo" in name_lower or "dân vận" in name_lower:
        return ("XDĐ", DEPT_MAPPING["XDĐ"])
    if "kiểm tra" in name_lower:
        return ("UBKT", DEPT_MAPPING["UBKT"])
    if "văn phòng" in name_lower or "cơ yếu" in name_lower or "văn thư" in name_lower or "thủ quỹ" in name_lower:
        return ("VP", DEPT_MAPPING["VP"])
    if "mặt trận" in name_lower or "mttq" in name_lower or "chính trị - xã hội" in name_lower:
        return ("MTTQ", DEPT_MAPPING["MTTQ"])

    if len(parts) >= 2:
        return (parts[1].upper(), f"Bộ phận {parts[1].upper()}")
    return ("KHAC", "Bộ phận khác")


def classify_role_level(ma_vtvl: str, ten_vtvl: str = "") -> Tuple[str, str]:
    """
    Phân loại nhóm chức danh để kiểm tra phương pháp định biên (PP1, PP1+PP2, PP2).
    Trả về (loai_vi_tri, phuong_phap_chuan_goi_y)
    """
    name = (ten_vtvl or "").lower().strip()
    code = (ma_vtvl or "").upper().strip()

    # Cấp trưởng / Thường trực
    if any(
        kw in name
        for kw in [
            "bí thư",
            "trưởng ban",
            "chủ nhiệm ủy ban kiểm tra",
            "chánh văn phòng",
            "chủ tịch ủy ban mttq",
            "chủ tịch hđnd",
            "chủ tịch ubnd",
            "chủ tịch hội đồng nhân dân",
            "chủ tịch ủy ban nhân dân",
            "giám đốc",
            "trưởng phòng",
            "chỉ huy trưởng",
            "hiệu trưởng",
            "trạm trưởng",
        ]
    ) and not any(p in name for p in ["phó trưởng", "phó chủ nhiệm", "phó chánh", "phó chủ tịch", "phó giám đốc", "phó hiệu trưởng", "phó trạm trưởng", "phó chỉ huy"]):
        if "phó bí thư" in name:
            return ("Thường trực (Cấp phó)", "PP1")
        return ("Lãnh đạo cấp trưởng / Thường trực", "PP1")

    # Cấp phó
    if any(
        kw in name
        for kw in [
            "phó trưởng ban",
            "phó chủ nhiệm",
            "phó chánh văn phòng",
            "phó chủ tịch",
            "cấp phó",
            "phó giám đốc",
            "phó trưởng phòng",
            "phó hiệu trưởng",
            "phó trạm trưởng",
            "phó chỉ huy trưởng",
            "phó chủ tịch hội đồng nhân dân",
            "phó chủ tịch ủy ban nhân dân",
        ]
    ):
        return ("Lãnh đạo cấp phó", "PP1 hoặc PP1+PP2")

    # Ủy viên UBKT chuyên trách
    if "ủy viên ủy ban kiểm tra" in name or code.endswith("_UV"):
        return ("Ủy viên chuyên trách", "PP2 (hoặc PP1 theo cơ cấu)")

    # Chuyên viên, kiểm tra viên, kế toán, văn thư, cơ yếu...
    return ("Chuyên môn, nghiệp vụ / Hỗ trợ", "PP2")
