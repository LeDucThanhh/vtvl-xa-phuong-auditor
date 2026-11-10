# -*- coding: utf-8 -*-
"""Kiểm tra phân loại chức danh khối xã/phường và tra biên chế giao theo QĐ 2398. Chạy: python -m pytest tests"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.analyzer_bienche import analyze_bien_che_giao
from core.bien_che_giao import lookup_bien_che_giao
from core.dept_parser import classify_role_level, get_khoi, parse_department
from core.qd2398_data import BIEN_CHE_CAP_XA


# ---------- phân loại chức danh ----------
def test_dang_mttq_codes_unchanged():
    assert parse_department("A27.118_TT01", "Bí thư Đảng ủy phường")[0] == "TT"
    assert parse_department("A27.118_XDĐ_TB", "Trưởng Ban Xây dựng Đảng")[0] == "XDĐ"
    assert parse_department("A27.118_KT_KTV", "Kiểm tra viên")[0] == "UBKT"
    assert parse_department("A27.118_VP_CV05", "Văn thư, lưu trữ")[0] == "VP"
    assert parse_department("I27.118_CTUBMTTQ", "Chủ tịch Ủy ban MTTQ Việt Nam phường")[0] == "MTTQ"
    assert parse_department("A27.118_TTCT_GĐ", "Giám đốc")[0] == "TTCT"


def test_chinh_quyen_by_title_when_code_unknown():
    cases = {
        "Chủ tịch Hội đồng nhân dân xã": "HĐND",
        "Phó Chủ tịch Hội đồng nhân dân phường": "HĐND",
        "Trưởng Ban Pháp chế HĐND": "HĐND",
        "Chủ tịch Ủy ban nhân dân xã": "UBND",
        "Phó Chủ tịch Ủy ban nhân dân phường": "UBND",
        "Chánh Văn phòng HĐND và UBND": "VPHĐND-UBND",
        "Công chức Tư pháp - Hộ tịch": "VPHĐND-UBND",
        "Chuyên viên Văn thư, lưu trữ": "VPHĐND-UBND",
        "Công chức Văn hóa - Xã hội": "VHXH",
        "Chuyên viên Lao động - Thương binh và Xã hội": "VHXH",
        "Công chức Địa chính - Xây dựng": "KTHT",
        "Chuyên viên Nông nghiệp và Môi trường": "KTHT",
        "Công chức Tài chính - Kế toán": "KTHT",
        "Chỉ huy trưởng Ban Chỉ huy quân sự xã": "QSCA",
        "Giám đốc Trung tâm Dịch vụ tổng hợp": "TTDVTH",
        "Chuyên viên Trung tâm Phục vụ Hành chính công": "TTHCC",
        "Bác sĩ Trạm Y tế xã": "TYT",
        "Điều dưỡng": "TYT",
        "Hiệu trưởng Trường Mầm non": "GDMN",
        "Giáo viên Trường Tiểu học": "GDTH",
        "Phó Hiệu trưởng Trường THCS": "GDTHCS",
    }
    for title, expected in cases.items():
        got = parse_department("B27.101_ZZ_01", title, chinh_quyen=True)[0]
        assert got == expected, (title, got, expected)


def test_chinh_quyen_by_code_token():
    assert parse_department("B27.101_HĐND_CT", "x", chinh_quyen=True)[0] == "HĐND"
    assert parse_department("B27.101_UBND_CT", "x", chinh_quyen=True)[0] == "UBND"
    assert parse_department("B27.101_VPHĐND-UBND_CV01", "x", chinh_quyen=True)[0] == "VPHĐND-UBND"
    assert parse_department("B27.101_VHXH_CV01", "x", chinh_quyen=True)[0] == "VHXH"
    assert parse_department("B27.101_KTHT_CV01", "x", chinh_quyen=True)[0] == "KTHT"
    assert parse_department("B27.101_TTHCC_CV01", "x", chinh_quyen=True)[0] == "TTHCC"
    assert parse_department("B27.101_TYT_BS", "x", chinh_quyen=True)[0] == "TYT"


def test_khoi():
    assert get_khoi("XDĐ") == "DANG"
    assert get_khoi("MTTQ") == "MTTQ"
    assert get_khoi("UBND") == "CHINH_QUYEN"
    assert get_khoi("TYT") == "SU_NGHIEP"


def test_role_levels():
    assert classify_role_level("", "Chủ tịch Ủy ban nhân dân xã")[0].startswith("Lãnh đạo cấp trưởng")
    assert classify_role_level("", "Phó Chủ tịch Ủy ban nhân dân xã")[0] == "Lãnh đạo cấp phó"
    assert classify_role_level("", "Hiệu trưởng")[0].startswith("Lãnh đạo cấp trưởng")
    assert classify_role_level("", "Phó Hiệu trưởng")[0] == "Lãnh đạo cấp phó"


# ---------- tra biên chế giao ----------
def test_totals_match_decision():
    assert len(BIEN_CHE_CAP_XA) == 69
    assert sum(u["cong_chuc"]["tong"] for u in BIEN_CHE_CAP_XA) == 2579
    assert sum(u["cong_chuc"]["doi_du"] for u in BIEN_CHE_CAP_XA) == 120


def test_lookup_real_file_names():
    names = {
        "10.  Kỳ Lạc 08.11.2026.xlsx": "Xã Kỳ Lạc",
        "A27.106_KYHOA_09.11.2026(22h).xlsx": "Xã Kỳ Hoa",
        "A2.151. SƠN KIM 1. 09.11.xlsx": "Xã Sơn Kim 1",
        "9.11. Xã Sơn Kim 2.xlsx": "Xã Sơn Kim 2",
        "42. NGHI XUAN (BẢN CUỐI 9.11.2026) 21H.xlsx": "Xã Nghi Xuân",
        "VUNG ANG 10.11 SOAT LOI.xlsx": "Phường Vũng Áng",
        "A27.101_PHUONG HAI NINH_09.11.2026.xlsx": "Phường Hải Ninh",
        "19. THÀNH SEN 09.11.2026 20H40 BẢN 30000 DÒNG.xlsx": "Phường Thành Sen",
        "09.11. (Cẩm Bình) Biểu VTVL.xlsx": "Xã Cẩm Bình",
        "9.11 Sơn Tây (1).xlsx": "Xã Sơn Tây",
    }
    for fname, expected in names.items():
        got = lookup_bien_che_giao(fname)
        assert got and got["ten"] == expected, (fname, got and got["ten"])


def test_lookup_unknown():
    assert lookup_bien_che_giao("bieu_mau_trong.xlsx") is None


# ---------- đối chiếu biên chế ----------
def _pos(code, name, loai, n_d1, n_c3, profile=""):
    dept, _ = parse_department(code, name, chinh_quyen=True)
    return {"ma_vtvl": code, "ten_vtvl": name, "loai_nhan_luc": loai, "dept_code": dept,
            "khoi": "SU_NGHIEP" if profile else get_khoi(dept), "unit_profile": profile, "n_d1": n_d1, "n_c3": n_c3}


def test_analyzer_flags_over_allocation():
    unit = lookup_bien_che_giao("Kỳ Lạc.xlsx")  # công chức giao 33 (chính thức 33)
    tong = unit["cong_chuc"]["tong"]
    data = {"positions": [
        _pos("B1_UBND_CT", "Chủ tịch Ủy ban nhân dân xã", "Cán bộ", 1, 1),
        _pos("B1_VHXH_CV", "Công chức Văn hóa - Xã hội", "Công chức", 3, tong + 5),
        _pos("B1_TYT_BS", "Bác sĩ Trạm Y tế xã", "Viên chức", 2, 2, profile="TYT"),
        _pos("A1_XDĐ_TB", "Trưởng Ban Xây dựng Đảng", "Công chức", 1, 1),  # khối Đảng: bỏ qua
    ]}
    res = analyze_bien_che_giao(data, unit)
    by_code = {c["code"]: c for c in res["comparisons"]}
    assert set(by_code) == {"CONG_CHUC", "TYT"}
    assert by_code["CONG_CHUC"]["status"] == "ĐỀ XUẤT VƯỢT TỔNG GIAO"
    assert by_code["CONG_CHUC"]["n_c3"] == tong + 6
    assert by_code["TYT"]["status"] == "TRONG CHỈ TIÊU"
    assert [f["severity"] for f in res["findings"]] == ["NGHIEM_TRONG"]


def test_analyzer_dang_only_file_has_note():
    unit = lookup_bien_che_giao("Kỳ Lạc.xlsx")
    data = {"positions": [_pos("A1_TT01", "Bí thư Đảng ủy xã", "Cán bộ", 1, 1)]}
    res = analyze_bien_che_giao(data, unit)
    assert res["comparisons"] == [] and res["notes"]


def test_unit_profile_detection():
    from core.xa_titles import classify_in_profile, detect_unit_profile as d
    assert d("Kỳ Văn_TYT.xlsx", []) == "TYT"
    assert d("x.xlsx", ["Trạm Y tế xã Kỳ Văn"]) == "TYT"
    assert d("Kỳ Văn_TTDVTH.xlsx", []) == "TTDVTH"
    assert d("MN Kỳ Văn.xlsx", []) == "GDMN"
    assert d("Kỳ Văn_TH&THCS Kỳ Tây.xlsx", []) == "GD_LIENCAP"
    assert d("10. Kỳ Lạc.xlsx", ["Đảng ủy xã Kỳ Lạc"]) == ""
    assert d("K-Van_HDND-UBND.xlsx", ["UBND xã Kỳ Văn"]) == ""
    assert classify_in_profile("TYT", "Y tế công cộng")[0] == "TYT_CM"
    assert classify_in_profile("TYT", "Kế toán viên")[0] == "TYT_HC"
    assert classify_in_profile("TYT", "Giám đốc")[0] == "TYT_LD"


def test_dang_file_not_affected_without_context():
    # file khối Đảng (không bật chinh_quyen): chức danh chung chung KHÔNG bị chuyển sang nhóm chính quyền
    assert parse_department("A27.02_VT15", "Văn thư, lưu trữ")[0] == "VP"
    assert parse_department("A27.02_VT14", "Kế toán viên")[0] == "VT14"
    assert parse_department("A27.02_VT12", "Chuyên viên về hành chính, tổng hợp")[0] == "VT12"


def test_context_detection():
    from core.xa_titles import is_chinh_quyen_context as c
    assert c("K-Van_HDND-UBND.xlsx", [])
    assert c("x.xlsx", ["UBND xã Kỳ Văn"])
    assert not c("10. Kỳ Lạc 08.11.2026.xlsx", ["Đảng ủy xã Kỳ Lạc"])
    assert not c("9.11.2026. Biểu Ban Tổ chức.xlsx", [])


# ---------- Sở/ngành cấp tỉnh ----------
def test_cap_tinh_lookup():
    from core.bien_che_giao import lookup_cap_tinh
    u = lookup_cap_tinh("7.11 chốt Phieu_so_ngoai_vu_FN.xlsx", [])
    assert u and u["ten"] == "Sở Ngoại vụ" and u["cong_chuc"] == {"tong": 20, "chinh_thuc": 20, "doi_du": 0, "hd111": 2}
    assert lookup_cap_tinh("x.xlsx", ["Sở Ngoại vụ"])["ten"] == "Sở Ngoại vụ"
    assert lookup_cap_tinh("Phieu so van hoa.xlsx", [])["ten"] == "Sở Văn hóa, Thể thao và Du lịch"
    assert lookup_cap_tinh("Chi cuc Kiem lam.xlsx", [])["cong_chuc"]["tong"] == 181
    assert lookup_cap_tinh("Thanh tra tinh.xlsx", [])["cong_chuc"]["tong"] == 107
    # xã/phường, Trạm Y tế, Đảng không bị nhận nhầm là Sở
    assert lookup_cap_tinh("10.  Kỳ Lạc 08.11.2026.xlsx", ["Đảng ủy xã Kỳ Lạc"]) is None
    assert lookup_cap_tinh("Kỳ Văn_TYT.xlsx", ["Trạm Y tế xã Kỳ Văn"]) is None


def test_lookup_prefers_cap_tinh_and_marks_cap():
    from core.bien_che_giao import lookup_bien_che_giao
    assert lookup_bien_che_giao("Phieu_so_ngoai_vu.xlsx")["cap"] == "tinh"
    assert lookup_bien_che_giao("Kỳ Lạc.xlsx")["cap"] == "xa"


def test_so_nganh_role_groups():
    from core.xa_titles import classify_in_profile as c
    assert c("SO_NGANH", "Giám đốc Sở")[0] == "SO_NGANH_LD"
    assert c("SO_NGANH", "Trưởng phòng thuộc Sở")[0] == "SO_NGANH_LDP"
    assert c("SO_NGANH", "Chánh Văn phòng Sở")[0] == "SO_NGANH_LD"
    assert c("SO_NGANH", "Chuyên viên về tổ chức - biên chế")[0] == "SO_NGANH_VP"
    assert c("SO_NGANH", "Văn thư viên")[0] == "SO_NGANH_VP"
    assert c("SO_NGANH", "Nhân viên lái xe")[0] == "SO_NGANH_HDLD"
    assert c("SO_NGANH", "Chuyên viên chính về lãnh sự")[0] == "SO_NGANH_CM"


def test_analyzer_cap_tinh():
    from core.bien_che_giao import lookup_cap_tinh
    unit = dict(lookup_cap_tinh("Phieu_so_ngoai_vu.xlsx", [])); unit["cap"] = "tinh"
    def pos(code, name, loai, d1, c3):
        return {"ma_vtvl": code, "ten_vtvl": name, "loai_nhan_luc": loai, "dept_code": "SO_NGANH_CM",
                "khoi": "CAP_TINH", "unit_profile": "SO_NGANH", "n_d1": d1, "n_c3": c3}
    data = {"positions": [pos("a", "Chuyên viên", "Công chức", 10, 22), pos("b", "Lái xe", "Hợp đồng lao động", 2, 0)]}
    r = analyze_bien_che_giao(data, unit)
    by = {c["code"]: c for c in r["comparisons"]}
    assert by["CONG_CHUC"]["status"] == "ĐỀ XUẤT VƯỢT TỔNG GIAO" and by["CONG_CHUC"]["giao_tong"] == 20
    assert by["HD111"]["giao_tong"] == 2 and by["HD111"]["n_d1"] == 2 and by["HD111"]["n_c3"] == 0
