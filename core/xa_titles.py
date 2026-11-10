# -*- coding: utf-8 -*-
"""
Danh mục chức danh / bộ phận của chính quyền cấp xã, phường (mô hình 2 cấp: Luật Tổ chức chính quyền địa phương 2025).
Dùng để gán mỗi vị trí việc làm (VTVL) trong file Excel vào đúng Ban / Bộ phận, phục vụ bộ lọc và cân đối giữa các bộ phận.

SỬA TẠI ĐÂY khi cần thêm chức danh: chỉ cần thêm từ khóa (viết thường, có dấu) vào danh sách của bộ phận tương ứng.
Thứ tự trong XA_GROUPS là thứ tự ưu tiên khi một tên chức danh khớp nhiều bộ phận (bộ phận đứng trước thắng).
"""

from typing import Dict, List, Tuple

# Khối
KHOI_DANG = "DANG"
KHOI_MTTQ = "MTTQ"
KHOI_CHINH_QUYEN = "CHINH_QUYEN"
KHOI_SU_NGHIEP = "SU_NGHIEP"
KHOI_CAP_TINH = "CAP_TINH"
KHOI_KHAC = "KHAC"

KHOI_NAMES: Dict[str, str] = {
    KHOI_DANG: "Khối Đảng",
    KHOI_MTTQ: "Khối Mặt trận - Đoàn thể",
    KHOI_CHINH_QUYEN: "Khối Chính quyền (HĐND - UBND)",
    KHOI_SU_NGHIEP: "Đơn vị sự nghiệp cấp xã",
    KHOI_CAP_TINH: "Cơ quan hành chính cấp tỉnh (Sở, ngành)",
    KHOI_KHAC: "Khác",
}

# (mã bộ phận, tên hiển thị, khối, từ khóa trong TÊN chức danh)
XA_GROUPS: List[Tuple[str, str, str, List[str]]] = [
    # ---- Đơn vị sự nghiệp (đặt trước để "kế toán/văn thư" của trường, trạm không rơi vào khối chính quyền)
    ("TYT", "Trạm Y tế xã, phường", KHOI_SU_NGHIEP,
     ["trạm y tế", "trạm trưởng", "bác sĩ", "y sĩ", "điều dưỡng", "hộ sinh", "dược sĩ", "kỹ thuật y", "y tế xã", "y tế phường", "nhân viên y tế"]),
    ("GDMN", "Trường Mầm non", KHOI_SU_NGHIEP, ["mầm non"]),
    ("GDTH", "Trường Tiểu học", KHOI_SU_NGHIEP, ["tiểu học"]),
    ("GDTHCS", "Trường THCS", KHOI_SU_NGHIEP, ["trung học cơ sở", "thcs"]),
    ("GD", "Giáo dục (trường học - chưa rõ cấp)", KHOI_SU_NGHIEP,
     ["hiệu trưởng", "phó hiệu trưởng", "giáo viên", "giảng viên"]),
    ("TTDVTH", "Trung tâm Dịch vụ tổng hợp", KHOI_SU_NGHIEP,
     ["dịch vụ tổng hợp", "trung tâm dịch vụ"]),
    ("TTHCC", "Trung tâm Phục vụ Hành chính công", KHOI_CHINH_QUYEN,
     ["hành chính công", "một cửa", "tiếp nhận và trả kết quả", "tiếp nhận, giải quyết"]),

    # ---- Văn phòng HĐND & UBND (đứng trước HĐND để 'Chánh Văn phòng HĐND và UBND' không bị tính vào HĐND)
    ("VPHĐND-UBND", "Văn phòng HĐND & UBND", KHOI_CHINH_QUYEN,
     ["văn phòng hđnd", "văn phòng hội đồng", "chánh văn phòng hđnd", "văn phòng ubnd", "văn phòng hđnd và ubnd",
      "văn thư", "lưu trữ", "thống kê", "tổng hợp", "nội vụ", "tổ chức - biên chế", "thi đua", "khen thưởng",
      "cải cách hành chính", "tư pháp", "hộ tịch", "chứng thực", "tiếp công dân", "thanh tra",
      "chuyển đổi số", "công nghệ thông tin", "hành chính - tổng hợp", "cơ yếu"]),

    # ---- Hội đồng nhân dân
    ("HĐND", "Thường trực & các Ban HĐND", KHOI_CHINH_QUYEN,
     ["hội đồng nhân dân", "hđnd", "ban pháp chế", "ban kinh tế - xã hội", "ban kinh tế xã hội", "đại biểu hđnd"]),

    # ---- Ủy ban nhân dân
    ("UBND", "Lãnh đạo UBND", KHOI_CHINH_QUYEN,
     ["chủ tịch ủy ban nhân dân", "phó chủ tịch ủy ban nhân dân", "chủ tịch ubnd", "phó chủ tịch ubnd",
      "chủ tịch ủy ban nhân dân xã", "chủ tịch ủy ban nhân dân phường"]),

    # ---- Quân sự, công an
    ("QSCA", "Quân sự - Công an xã", KHOI_CHINH_QUYEN,
     ["chỉ huy trưởng", "chỉ huy phó", "quân sự", "trưởng công an", "phó trưởng công an", "công an xã", "công an phường"]),

    # ---- Phòng Văn hóa - Xã hội
    ("VHXH", "Phòng Văn hóa - Xã hội", KHOI_CHINH_QUYEN,
     ["văn hóa", "thể thao", "du lịch", "giáo dục", "y tế", "dân số", "lao động", "thương binh", "người có công",
      "bảo trợ xã hội", "xã hội", "dân tộc", "tôn giáo", "thông tin", "truyền thông", "gia đình", "trẻ em", "việc làm"]),

    # ---- Phòng Kinh tế / Kinh tế - Hạ tầng - Đô thị
    ("KTHT", "Phòng Kinh tế, Hạ tầng & Đô thị", KHOI_CHINH_QUYEN,
     ["kinh tế", "hạ tầng", "đô thị", "nông nghiệp", "nông thôn", "lâm nghiệp", "thủy lợi", "thủy sản", "chăn nuôi", "trồng trọt",
      "môi trường", "tài nguyên", "địa chính", "đất đai", "xây dựng", "giao thông", "công thương", "thương mại", "công nghiệp",
      "tài chính", "ngân sách", "kế toán", "kế hoạch", "đầu tư", "phòng chống thiên tai", "quản lý trật tự"]),
]

# Từ viết tắt / token trong MÃ VTVL (phần giữa hai dấu '_') -> mã bộ phận. So khớp không phân biệt dấu & hoa thường.
CODE_TOKENS: Dict[str, str] = {
    "HĐND": "HĐND", "HDND": "HĐND", "CTHĐND": "HĐND", "PCTHĐND": "HĐND", "TBHĐND": "HĐND", "PTBHĐND": "HĐND",
    "UBND": "UBND", "CTUBND": "UBND", "PCTUBND": "UBND", "LĐUBND": "UBND",
    "VPHĐND": "VPHĐND-UBND", "VPUBND": "VPHĐND-UBND", "VPHĐNDUBND": "VPHĐND-UBND", "VPHDNDUBND": "VPHĐND-UBND",
    "VPHĐNDVAUBND": "VPHĐND-UBND", "VPHĐNDUB": "VPHĐND-UBND",
    "VHXH": "VHXH", "VHTT": "VHXH", "VX": "VHXH",
    "KTHT": "KTHT", "KT-HT": "KTHT", "KTHTĐT": "KTHT", "KTHTDT": "KTHT", "KTE": "KTHT",
    "TTHCC": "TTHCC", "PVHCC": "TTHCC", "HCC": "TTHCC",
    "TTDVTH": "TTDVTH", "DVTH": "TTDVTH", "TTDV": "TTDVTH",
    "TYT": "TYT", "YTE": "TYT",
    "MN": "GDMN", "TH": "GDTH", "THCS": "GDTHCS",
    "QS": "QSCA", "BCHQS": "QSCA", "CA": "QSCA",
}

GROUP_INDEX: Dict[str, Tuple[str, str, str]] = {g[0]: (g[1], g[2], g[0]) for g in XA_GROUPS}


def group_name(code: str) -> str:
    return GROUP_INDEX[code][0] if code in GROUP_INDEX else ""


def group_khoi(code: str) -> str:
    return GROUP_INDEX[code][1] if code in GROUP_INDEX else ""


def classify_by_title(ten_vtvl: str) -> str:
    """Trả về mã bộ phận khối chính quyền/sự nghiệp theo TÊN chức danh, hoặc '' nếu không khớp."""
    name = (ten_vtvl or "").lower()
    if not name:
        return ""
    for code, _label, _khoi, kws in XA_GROUPS:
        for kw in kws:
            if kw in name:
                return code
    return ""


# ---------------------------------------------------------------------------------------------
# NHẬN DIỆN LOẠI ĐƠN VỊ CỦA CẢ FILE (Trạm Y tế, TT Dịch vụ tổng hợp, trường học...)
# Một file Excel của đơn vị sự nghiệp có mã VTVL tuần tự (vd H27.107.06_VT1..VT17) nên không dựa vào mã/tên từng
# chức danh được; phải xác định đơn vị từ tên file, 'Nơi tính BC' (D1) hoặc cột 'Cơ quan' (A1).
# ---------------------------------------------------------------------------------------------
import re as _re
import unicodedata as _ud


def _plain(text: str) -> str:
    t = (text or "").replace("đ", "d").replace("Đ", "D")
    t = "".join(c for c in _ud.normalize("NFD", t) if _ud.category(c) != "Mn")
    return _re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()


# (mã profile, tên, từ khóa đã bỏ dấu). Thứ tự = ưu tiên.
UNIT_PROFILES = [
    ("GD_LIENCAP", "Trường Tiểu học và THCS", ["tieu hoc va trung hoc co so", "tieu hoc va thcs", "th thcs", "th va thcs", "th thcs", "thcs va tieu hoc"]),
    ("TYT", "Trạm Y tế", ["tram y te", "tyt"]),
    ("TTDVTH", "Trung tâm Dịch vụ tổng hợp", ["dich vu tong hop", "ttdvth"]),
    ("GDMN", "Trường Mầm non", ["mam non", "truong mn", "mn "]),
    ("GDTHCS", "Trường THCS", ["trung hoc co so", "truong thcs", "thcs"]),
    ("GDTH", "Trường Tiểu học", ["tieu hoc", "truong th ", "truong th"]),
]
PROFILE_NAMES = {p[0]: p[1] for p in UNIT_PROFILES}
PROFILE_NAMES["SO_NGANH"] = "Sở/ngành"  # xác định bằng core.bien_che_giao.lookup_cap_tinh (không nằm trong UNIT_PROFILES)

# Nhóm chức danh bên trong từng loại đơn vị (dùng làm "Ban / Bộ phận" cho bộ lọc và cân đối)
_ROLE_RULES = {
    "TYT": [
        ("LD", "Lãnh đạo Trạm", ["giám đốc", "phó giám đốc", "trạm trưởng", "phó trạm trưởng"]),
        ("HC", "Hành chính - Kế toán", ["văn thư", "kế toán", "thủ quỹ", "hành chính", "văn phòng", "lưu trữ", "bảo vệ", "lái xe"]),
        ("CM", "Chuyên môn y tế", ["bác s", "y s", "điều dưỡng", "hộ sinh", "dược", "kỹ thuật y", "dinh dưỡng", "y tế", "y học", "dân số", "xét nghiệm"]),
    ],
    "TTDVTH": [
        ("LD", "Lãnh đạo Trung tâm", ["giám đốc", "phó giám đốc"]),
        ("HC", "Hành chính - Kế toán", ["văn thư", "kế toán", "thủ quỹ", "hành chính", "văn phòng", "lưu trữ"]),
    ],
    "GD": [
        ("LD", "Ban giám hiệu", ["hiệu trưởng", "phó hiệu trưởng"]),
        ("GV", "Giáo viên", ["giáo viên", "giảng viên"]),
        ("NV", "Nhân viên hỗ trợ", ["kế toán", "văn thư", "thư viện", "thiết bị", "y tế", "bảo vệ", "thủ quỹ", "hành chính", "văn phòng", "công nghệ thông tin", "nhân viên", "cmdc"]),
    ],
}
_ROLE_RULES["SO_NGANH"] = [
    ("HDLD", "Hợp đồng hỗ trợ, phục vụ", ["lái xe", "bảo vệ", "phục vụ", "tạp vụ", "nấu ăn", "bảo trì"]),
    ("LD", "Lãnh đạo Sở/đơn vị", ["giám đốc", "chi cục trưởng", "phó chi cục trưởng", "chánh thanh tra", "phó chánh thanh tra",
                                  "trưởng ban", "phó trưởng ban", "chủ nhiệm", "phó chủ nhiệm", "chánh văn phòng sở", "chánh văn phòng"]),
    ("LDP", "Lãnh đạo phòng", ["trưởng phòng", "phó trưởng phòng", "đội trưởng", "phó đội trưởng", "trưởng chi nhánh"]),
    ("VP", "Văn phòng - Tổng hợp", ["văn phòng", "hành chính", "tổng hợp", "kế toán", "văn thư", "thủ quỹ", "lưu trữ", "tổ chức - biên chế",
                                    "tổ chức, biên chế", "cải cách hành chính", "ứng dụng công nghệ", "công nghệ thông tin", "chuyển đổi số",
                                    "thi đua", "pháp chế", "phòng, chống tham nhũng", "phòng chống tham nhũng", "quản trị"]),
]
_DEFAULT_ROLE = {
    "SO_NGANH": ("CM", "Chuyên môn nghiệp vụ"),
    "TYT": ("CM", "Chuyên môn y tế"),
    "TTDVTH": ("CMDV", "Chuyên môn, dịch vụ"),
    "GD": ("NV", "Nhân viên hỗ trợ"),
}


def detect_unit_profile(file_name: str, unit_texts):
    """Trả về mã loại đơn vị sự nghiệp của file (TYT/TTDVTH/GDMN/GDTH/GDTHCS/GD_LIENCAP) hoặc ''.
    Ưu tiên 'Nơi tính BC'/'Cơ quan' (nội dung biểu), sau đó tên file."""
    sources = []
    seen = set()
    for t in list(unit_texts or []):
        if t and t not in seen:
            seen.add(t)
            sources.append(t)
    sources.append(file_name or "")
    for src in sources:
        text = " " + _plain(src) + " "
        for code, _name, kws in UNIT_PROFILES:
            for kw in kws:
                if (" " + kw.strip() + " ") in text:
                    return code
    return ""


def classify_in_profile(profile: str, ten_vtvl: str):
    """Nhóm chức danh bên trong đơn vị sự nghiệp -> (mã bộ phận, tên bộ phận). Mã gắn tiền tố loại đơn vị."""
    key = "GD" if profile.startswith("GD") else profile
    name = (ten_vtvl or "").lower()
    for code, label, kws in _ROLE_RULES.get(key, []):
        if any(k in name for k in kws):
            return f"{profile}_{code}", f"{PROFILE_NAMES[profile]} - {label}"
    code, label = _DEFAULT_ROLE.get(key, ("KHAC", "Khác"))
    return f"{profile}_{code}", f"{PROFILE_NAMES[profile]} - {label}"


def is_chinh_quyen_context(file_name: str, unit_texts) -> bool:
    """File thuộc khối chính quyền xã/phường (UBND/HĐND)? Xét tên file và ô 'Nơi tính BC' (D1).
    Chỉ khi đúng mới áp dụng danh mục chức danh chính quyền; file khối Đảng/MTTQ giữ nguyên cách phân loại gốc."""
    texts = [file_name or ""] + [t for t in (unit_texts or []) if t][:50]
    for t in texts:
        p = " " + _plain(t) + " "
        if any(k in p for k in (" dang uy ", " tinh uy ", " mttq ", " mat tran ", " cap uy ")):
            continue
        if any(k in p for k in (" hdnd ", " ubnd ", " uy ban nhan dan ", " hoi dong nhan dan ", " chinh quyen ")):
            return True
    return False
