import streamlit as st
import streamlit.components.v1 as components
import random
import math
import zipfile
import io
import time
import itertools

# ==========================================
# ⚙️ ตรวจสอบไลบรารี pdfkit
# ==========================================
try:
    import pdfkit
    HAS_PDFKIT = True
except ImportError:
    HAS_PDFKIT = False

# ==========================================
# 🎨 ตั้งค่าหน้าเพจ Web App & Professional CSS (ธีม ป.5 โทนส้ม-แดง ท้าทายขึ้น)
# ==========================================
st.set_page_config(page_title="Math Generator - Primary 5 (Gifted)", page_icon="🏆", layout="wide")

st.markdown("""
<style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1200px; }
    div[data-testid="stSidebar"] div.stButton > button { background-color: #d35400; color: white; border-radius: 8px; height: 3.5rem; font-size: 18px; font-weight: bold; border: none; box-shadow: 0 4px 6px rgba(211,84,0,0.3); }
    div[data-testid="stSidebar"] div.stButton > button:hover { background-color: #e67e22; box-shadow: 0 6px 12px rgba(211,84,0,0.4); }
    .main-header { background: linear-gradient(135deg, #c0392b, #e67e22); padding: 2rem; border-radius: 15px; color: white; margin-bottom: 2rem; box-shadow: 0 10px 20px rgba(0,0,0,0.15); }
    .main-header h1 { margin: 0; font-size: 2.8rem; font-weight: 800; text-shadow: 2px 2px 4px rgba(0,0,0,0.2); }
    .main-header p { margin: 10px 0 0 0; font-size: 1.2rem; opacity: 0.9; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>🏆 Math Worksheet Pro <span style="font-size: 20px; background: #f1c40f; color: #333; padding: 5px 15px; border-radius: 20px; vertical-align: middle;">ป.5 & เตรียมสอบเข้า ม.1</span></h1>
    <p>ระบบสร้างโจทย์คณิตศาสตร์ประยุกต์ สถิติ และเรขาคณิตขั้นสูง</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 📚 ฐานข้อมูลหลักสูตร (Master Database ป.5)
# ==========================================
curriculum_db = {
    "ป.5": {
        "เศษส่วน": ["การบวกเศษส่วน", "การลบเศษส่วน", "การคูณเศษส่วน", "การหารเศษส่วน"],
        "ทศนิยม": ["การบวกและการลบทศนิยม", "การคูณและการหารทศนิยม"],
        "สถิติและความน่าจะเป็น": ["การหาค่าเฉลี่ย (Average)", "ความน่าจะเป็นเบื้องต้น (สุ่มหยิบของ)"],
        "เรขาคณิต 2 มิติและ 3 มิติ": ["โจทย์ปัญหาพื้นที่และความยาวรอบรูป", "เส้นขนานและมุมแย้ง", "ปริมาตรและความจุทรงสี่เหลี่ยมมุมฉาก"],
        "ร้อยละและเปอร์เซ็นต์": ["การเขียนเศษส่วนในรูปร้อยละ"],
        "สมการ": ["การแก้สมการ (คูณ/หาร)"],
        "เตรียมสอบเข้า ม.1 (Gifted)": ["โจทย์ปัญหา ห.ร.ม. และ ค.ร.น.", "โจทย์ปัญหาคลาสสิก (สมการประยุกต์)", "แบบรูปและอนุกรม (Number Patterns)", "มาตราส่วนและทิศทาง", "เรขาคณิตประยุกต์ (หาพื้นที่แรเงา)"]
    }
}

# ==========================================
# 1. คลังคำศัพท์และฟังก์ชันตัวช่วย (Helpers)
# ==========================================
NAMES = ["อคิณ", "นาวิน", "ภูผา", "สายฟ้า", "เจ้านาย", "ข้าวหอม", "ใบบัว", "มะลิ", "น้ำใส", "ญาญ่า", "ปลื้ม", "พายุ", "ธาม", "คิน", "พริม"]
PLACE_EMOJIS = {"บ้าน": "🏠", "โรงเรียน": "🏫", "ตลาด": "🛒", "วัด": "🛕", "สวนสาธารณะ": "🌳", "โรงพยาบาล": "🏥"}

def f_html(n, d, c="#2c3e50", b=True):
    w = "bold" if b else "normal"
    return f"<span style='display:inline-flex; flex-direction:column; vertical-align:middle; text-align:center; line-height:1.4; margin:0 4px;'><span style='border-bottom:2px solid {c}; padding:0 4px; font-weight:{w}; color:{c};'>{n}</span><span style='padding:0 4px; font-weight:{w}; color:{c};'>{d}</span></span>"

def generate_vertical_table_html(a, b, op, result="", is_key=False):
    a_str, b_str = f"{a:,}", f"{b:,}"
    ans_val = f"{result:,}" if is_key and result != "" else ""
    border_ans = "border-bottom: 4px double #000;" if is_key else ""
    return f"""<div style='margin-left: 60px; display: block; font-family: "Sarabun", sans-serif; font-size: 26px; margin-top: 15px; margin-bottom: 15px;'>
        <table style='border-collapse: collapse; text-align: right;'>
            <tr><td style='padding: 0 10px 0 0; border: none;'>{a_str}</td><td rowspan='2' style='vertical-align: middle; text-align: left; padding: 0 0 0 15px; font-size: 28px; font-weight: bold; border: none;'>{op}</td></tr>
            <tr><td style='padding: 5px 10px 5px 0; border: none; border-bottom: 2px solid #000;'>{b_str}</td></tr>
            <tr><td style='padding: 5px 10px 0 0; border: none; {border_ans} height: 35px;'>{ans_val}</td><td style='border: none;'></td></tr>
        </table></div>"""

def generate_decimal_vertical_html(a, b, op, is_key=False):
    str_a, str_b = f"{a:.2f}", f"{b:.2f}"
    ans = a + b if op == '+' else round(a - b, 2)
    str_ans = f"{ans:.2f}"
    max_len = max(len(str_a), len(str_b), len(str_ans)) + 1 
    str_a, str_b, str_ans = str_a.rjust(max_len, " "), str_b.rjust(max_len, " "), str_ans.rjust(max_len, " ")
    strike, top_marks = [False] * max_len, [""] * max_len
    
    if is_key:
        if op == '+':
            carry = 0
            for i in range(max_len - 1, -1, -1):
                if str_a[i] == '.': continue
                da = int(str_a[i]) if str_a[i].strip() else 0
                db = int(str_b[i]) if str_b[i].strip() else 0
                s = da + db + carry
                carry = s // 10
                if carry > 0 and i > 0:
                    next_i = i - 1
                    if str_a[next_i] == '.': next_i -= 1
                    if next_i >= 0: top_marks[next_i] = str(carry)
        elif op == '-':
            a_digits = [int(c) if c.strip() and c != '.' else 0 for c in list(str_a)]
            b_digits = [int(c) if c.strip() and c != '.' else 0 for c in list(str_b)]
            for i in range(max_len - 1, -1, -1):
                if str_a[i] == '.': continue
                if a_digits[i] < b_digits[i]:
                    for j in range(i-1, -1, -1):
                        if str_a[j] == '.': continue
                        if a_digits[j] > 0 and str_a[j].strip() != "":
                            strike[j] = True
                            a_digits[j] -= 1
                            top_marks[j] = str(a_digits[j])
                            for k in range(j+1, i):
                                if str_a[k] == '.': continue
                                strike[k] = True
                                a_digits[k] = 9
                                top_marks[k] = "9"
                            strike[i] = True
                            a_digits[i] += 10
                            top_marks[i] = str(a_digits[i])
                            break
                            
    a_tds = ""
    for i in range(max_len):
        val = str_a[i].strip() if str_a[i].strip() else ""
        if str_a[i] == '.': val = "."
        td_content = val
        if val and val != '.':
            mark = top_marks[i]
            if strike[i] and is_key: td_content = f'<div style="position: relative;"><span style="position: absolute; top: -25px; left: 50%; transform: translateX(-50%); font-size: 20px; color: red; font-weight: bold;">{mark}</span><span style="text-decoration: line-through; text-decoration-color: red; text-decoration-thickness: 2px;">{val}</span></div>'
            elif mark and is_key: td_content = f'<div style="position: relative;"><span style="position: absolute; top: -25px; left: 50%; transform: translateX(-50%); font-size: 20px; color: red; font-weight: bold;">{mark}</span><span>{val}</span></div>'
        a_tds += f"<td style='width: 35px; text-align: center; height: 50px; vertical-align: bottom;'>{td_content}</td>"
        
    b_tds = "".join([f"<td style='width: 35px; text-align: center; border-bottom: 2px solid #000; height: 40px; vertical-align: bottom;'>{c.strip() if c.strip() else ('.' if c=='.' else '')}</td>" for c in str_b])
    ans_tds = "".join([f"<td style='width: 35px; text-align: center; color: red; font-weight: bold; height: 45px; vertical-align: bottom;'>{c.strip() if c.strip() else ('.' if c=='.' else '')}</td>" for c in str_ans]) if is_key else "".join([f"<td style='width: 35px; height: 45px;'></td>" for _ in str_ans])
    return f"""<div style="display: block; margin-left: 60px; margin-top: 15px; margin-bottom: 15px;"><div style="display: inline-block; font-family: 'Sarabun', sans-serif; font-size: 32px; line-height: 1.2;"><table style="border-collapse: collapse;"><tr><td style="width: 20px;"></td>{a_tds}<td style="width: 50px; text-align: left; padding-left: 15px; vertical-align: middle;" rowspan="2">{op}</td></tr><tr><td></td>{b_tds}</tr><tr><td></td>{ans_tds}<td></td></tr><tr><td></td><td colspan="{max_len}" style="border-bottom: 6px double #000; height: 10px;"></td><td></td></tr></table></div></div>"""

def render_short_div(nums, mode="gcd"):
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    steps, current_nums, divisors = [], list(nums), []
    while True:
        found = False
        for p in primes:
            if all(n % p == 0 for n in current_nums):
                divisors.append(p); steps.append(list(current_nums))
                current_nums = [n // p for n in current_nums]; found = True; break
        if not found: break
    if mode == "lcm":
        while True:
            found = False
            for p in primes:
                if sum(1 for n in current_nums if n % p == 0) >= 2:
                    divisors.append(p); steps.append(list(current_nums))
                    current_nums = [n // p if n % p == 0 else n for n in current_nums]; found = True; break
            if not found: break
    html = "<div style='display:block; text-align:center; margin: 20px 0;'><div style='display:inline-block; text-align:left; font-family:\"Courier New\", Courier, monospace; font-size:20px; background:#f8f9fa; padding:15px 25px; border-radius:8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); border: 1px solid #e0e0e0;'>"
    for i in range(len(divisors)):
        html += f"<div style='display: flex; align-items: baseline;'><div style='width: 35px; text-align: right; color: #c0392b; font-weight: bold; padding-right: 12px;'>{divisors[i]}</div><div style='border-left: 2px solid #2c3e50; border-bottom: 2px solid #2c3e50; padding: 4px 15px; display: flex; gap: 20px;'>"
        for n in steps[i]: html += f"<div style='width: 40px; text-align: center; color: #333;'>{n}</div>"
        html += "</div></div>"
    html += f"<div style='display: flex; align-items: baseline;'><div style='width: 35px; text-align: right; padding-right: 12px;'></div><div style='padding: 6px 15px 0px 15px; display: flex; gap: 20px; color: #2980b9; font-weight: bold; border-bottom: 4px double #2980b9;'>"
    for n in current_nums: html += f"<div style='width: 40px; text-align: center;'>{n}</div>"
    html += "</div></div></div></div>"
    return html, divisors, current_nums

# ==========================================
# 2. ฟังก์ชันวาด SVG สำหรับ ป.5
# ==========================================

# 2.1 ปริมาตรและความจุทรงลูกบาศก์/ทรงสี่เหลี่ยมมุมฉาก
def draw_prism_svg(w_lbl, l_lbl, h_lbl, is_water=False):
    svg = '<div style="text-align:center; margin:15px 0;"><svg width="280" height="220">'
    fill_front, fill_top, fill_right = ("#aed6f1", "#85c1e9", "#5dade2") if is_water else ("#d5f5e3", "#abebc6", "#82e0aa")
    stroke_c = "#2874a6" if is_water else "#27ae60"
    
    if is_water:
        y_offset = 60 
        svg += '<line x1="80" y1="10" x2="80" y2="130" stroke="#bdc3c7" stroke-width="2"/>'
        svg += '<line x1="80" y1="130" x2="220" y2="130" stroke="#bdc3c7" stroke-width="2"/>'
        svg += '<line x1="40" y1="160" x2="80" y2="130" stroke="#bdc3c7" stroke-width="2"/>'
        # ระดับน้ำ
        svg += f'<polygon points="40,{30+y_offset} 80,{10+y_offset} 220,{10+y_offset} 180,{30+y_offset}" fill="{fill_top}" stroke="{stroke_c}" stroke-width="2" opacity="0.85"/>'
        svg += f'<rect x="40" y="{30+y_offset}" width="140" height="{130-y_offset}" fill="{fill_front}" stroke="{stroke_c}" stroke-width="2" opacity="0.85"/>'
        svg += f'<polygon points="180,{30+y_offset} 220,{10+y_offset} 220,130 180,160" fill="{fill_right}" stroke="{stroke_c}" stroke-width="2" opacity="0.85"/>'
        # โครงกระจก
        svg += '<polygon points="40,30 80,10 220,10 180,30" fill="none" stroke="#95a5a6" stroke-width="2"/>'
        svg += '<line x1="40" y1="30" x2="40" y2="160" stroke="#95a5a6" stroke-width="2"/>'
        svg += '<line x1="180" y1="30" x2="180" y2="160" stroke="#95a5a6" stroke-width="2"/>'
        svg += '<line x1="220" y1="10" x2="220" y2="130" stroke="#95a5a6" stroke-width="2"/>'
        svg += '<line x1="40" y1="160" x2="180" y2="160" stroke="#95a5a6" stroke-width="2"/>'
    else:
        # กล่องทึบ
        svg += f'<rect x="40" y="60" width="140" height="100" fill="{fill_front}" stroke="{stroke_c}" stroke-width="3"/>'
        svg += f'<polygon points="40,60 80,20 220,20 180,60" fill="{fill_top}" stroke="{stroke_c}" stroke-width="3"/>'
        svg += f'<polygon points="180,60 220,20 220,120 180,160" fill="{fill_right}" stroke="{stroke_c}" stroke-width="3"/>'
        
    svg += f'<text x="110" y="185" font-family="Sarabun" font-size="16" fill="#2c3e50" font-weight="bold" text-anchor="middle">{l_lbl}</text>'
    svg += f'<text x="210" y="150" font-family="Sarabun" font-size="16" fill="#2c3e50" font-weight="bold">{w_lbl}</text>'
    
    if is_water: 
        svg += f'<text x="5" y="{95+y_offset/2}" font-family="Sarabun" font-size="16" fill="#2980b9" font-weight="bold">{h_lbl}</text>'
    else: 
        svg += f'<text x="5" y="115" font-family="Sarabun" font-size="16" fill="#2c3e50" font-weight="bold">{h_lbl}</text>'
    
    return svg + '</svg></div>'

# 2.2 กล่องลูกแก้ว ความน่าจะเป็น
def draw_marbles_box_svg(color_counts):
    color_map = {"สีแดง": "#e74c3c", "สีฟ้า": "#3498db", "สีเขียว": "#2ecc71", "สีเหลือง": "#f1c40f", "สีดำ": "#2c3e50", "สีขาว": "#fdfefe"}
    total_marbles = sum(color_counts.values())
    cols = 10 if total_marbles > 20 else 8
    rows = (total_marbles + cols - 1) // cols
    marble_r, col_w, row_h = 12, 36, 36
    box_width, box_height = max(320, cols * col_w + 30), max(140, rows * row_h + 60)
    width, height = box_width + 100, box_height + 40
    svg = f'<div style="text-align:center; margin: 15px 0;"><svg width="{width}" height="{height}">'
    box_x, box_y = 50, 20
    
    # วาดกล่องทึบ
    svg += f'<rect x="{box_x}" y="{box_y}" width="{box_width}" height="{box_height}" fill="#ebedef" stroke="#7f8c8d" stroke-width="4" rx="10"/>'
    svg += f'<path d="M {box_x} {box_y + 35} L {box_x + box_width} {box_y + 35}" stroke="#bdc3c7" stroke-width="2" stroke-dasharray="5,5"/>'
    svg += f'<text x="{box_x + box_width/2}" y="{box_y + 25}" font-family="Sarabun" font-size="16" font-weight="bold" fill="#34495e" text-anchor="middle">กล่องทึบ (มองไม่เห็นด้านใน)</text>'
    
    marbles = []
    for c_name, count in color_counts.items():
        for _ in range(count): marbles.append(color_map[c_name])
    random.shuffle(marbles)
    
    start_x, start_y = box_x + 25 + marble_r, box_y + 35 + 15 + marble_r
    for i, color in enumerate(marbles):
        cx, cy = start_x + ((i % cols) * col_w), start_y + ((i // cols) * row_h)
        svg += f'<circle cx="{cx}" cy="{cy}" r="{marble_r}" fill="{color}" stroke="#34495e" stroke-width="2"/>'
        svg += f'<circle cx="{cx-3}" cy="{cy-3}" r="3" fill="#ffffff" opacity="0.4"/>'
    return svg + '</svg></div>'

# 2.3 กล่องแสดงค่าเฉลี่ย
def draw_avg_box(icon, count, label_count, avg_val, label_avg, bg_color="#f1f8ff", border_color="#3498db"):
    box_style = f"border: 2px dashed {border_color}; border-radius: 8px; padding: 10px 15px; display: inline-block; text-align: center; margin: 5px; background-color: {bg_color}; vertical-align: top; min-width: 140px;"
    return f'<div style="{box_style}"><div style="font-size:24px;">{icon} {count} {label_count}</div><div style="font-size: 14px; font-weight: bold; color: #7f8c8d; margin-top: 5px;">ค่าเฉลี่ย</div><div style="font-size: 20px; font-weight: bold; color: #e74c3c;">{avg_val} {label_avg}</div></div>'

# 2.4 วาดเส้นขนาน และมุมแย้ง
def draw_angle_feature(vx, vy, ax, ay, bx, by, r_arc, r_text, label, color_arc, color_text, is_x=False):
    len_a = math.hypot(ax - vx, ay - vy)
    len_b = math.hypot(bx - vx, by - vy)
    if len_a == 0 or len_b == 0: return ""
    sx, sy = vx + (ax - vx) * r_arc / len_a, vy + (ay - vy) * r_arc / len_a
    ex, ey = vx + (bx - vx) * r_arc / len_b, vy + (by - vy) * r_arc / len_b
    sweep = 1 if (sx - vx) * (ey - vy) - (sy - vy) * (ex - vx) > 0 else 0
    arc_svg = f'<path d="M {sx} {sy} A {r_arc} {r_arc} 0 0 {sweep} {ex} {ey}" fill="none" stroke="{color_arc}" stroke-width="3"/>'
    mid_x, mid_y = (sx - vx)/r_arc + (ex - vx)/r_arc, (sy - vy)/r_arc + (ey - vy)/r_arc
    len_mid = math.hypot(mid_x, mid_y)
    tx, ty = (vx, vy - r_text) if len_mid == 0 else (vx + (mid_x / len_mid) * r_text, vy + (mid_y / len_mid) * r_text)
    font_size = "18px" if is_x else "16px"
    return arc_svg + f'<text x="{tx}" y="{ty+6}" font-size="{font_size}" font-weight="bold" font-family="Sarabun" text-anchor="middle" fill="{color_text}">{label}</text>'

def draw_parallel_svg(dir_key, pos1, val1, pos2, val2):
    angle_meta = {
        "dir1": {"bot": (110, 165), "top": (210, 15), "V1": (180, 60), "V2": (140, 120), "acute": ["TR_ext", "BL_int", "TL_int", "BR_ext"]},
        "dir2": {"bot": (220, 165), "top": (120, 15), "V1": (150, 60), "V2": (190, 120), "acute": ["TL_ext", "BR_int", "TR_int", "BL_ext"]}
    }
    def get_arms(pos, V1, V2, bot, top):
        if pos == "TL_ext": return V1, top, (40, V1[1])
        if pos == "TR_ext": return V1, (300, V1[1]), top
        if pos == "BL_int": return V1, (40, V1[1]), V2
        if pos == "BR_int": return V1, V2, (300, V1[1])
        if pos == "TL_int": return V2, V1, (40, V2[1])
        if pos == "TR_int": return V2, (300, V2[1]), V1
        if pos == "BL_ext": return V2, (40, V2[1]), bot
        if pos == "BR_ext": return V2, bot, (300, V2[1])

    svg = '<div style="text-align:center; margin:15px 0;"><svg width="340" height="200">'
    # เส้นขนาน 2 เส้น
    svg += '<line x1="40" y1="60" x2="300" y2="60" stroke="#2980b9" stroke-width="4"/><line x1="40" y1="120" x2="300" y2="120" stroke="#2980b9" stroke-width="4"/>'
    # สัญลักษณ์ลูกศรขนาน
    svg += '<polygon points="275,55 285,60 275,65" fill="#2980b9"/><polygon points="275,115 285,120 275,125" fill="#2980b9"/>'
    
    lbl_style = 'font-family:Sarabun; font-size:16px; font-weight:bold; fill:#2c3e50;'
    meta = angle_meta[dir_key]
    bot, top = meta["bot"], meta["top"]
    # เส้นตัด
    svg += f'<line x1="{bot[0]}" y1="{bot[1]}" x2="{top[0]}" y2="{top[1]}" stroke="#8e44ad" stroke-width="3"/>'
    
    V1, V2 = meta["V1"], meta["V2"]
    def draw_pos(pos, val, is_var):
        vx, arm1, arm2 = get_arms(pos, V1, V2, bot, top)
        return draw_angle_feature(vx[0], vx[1], arm1[0], arm1[1], arm2[0], arm2[1], 25, 45, "x" if is_var else f"{val}°", "#2ecc71", "#c0392b", is_x=is_var)
    
    svg += draw_pos(pos1, val1, is_var=False) + draw_pos(pos2, val2, is_var=True)
    return svg + '</svg></div>'

# 2.5 วาดพื้นที่แรเงาซ้อนทับ (Gifted)
def draw_shaded_svg(scenario, W, H, p1=0):
    svg = '<div style="text-align:center; margin:15px 0;"><svg width="460" height="240">'
    max_w, max_h = 200, 140 
    scale = min(max_w / W, max_h / H)
    draw_w, draw_h = W * scale, H * scale
    ox, oy = (460 - draw_w) / 2, (240 - draw_h) / 2
    lbl_style = 'font-family:Sarabun; font-size:16px; font-weight:bold; fill:#c0392b;'
    lbl_style_sm = 'font-family:Sarabun; font-size:15px; font-weight:bold; fill:#2980b9;'
    
    if scenario == "frame":
        border_scale = p1 * scale
        svg += f'<rect x="{ox}" y="{oy}" width="{draw_w}" height="{draw_h}" fill="#bdc3c7" stroke="#2c3e50" stroke-width="3"/>'
        svg += f'<rect x="{ox+border_scale}" y="{oy+border_scale}" width="{draw_w-2*border_scale}" height="{draw_h-2*border_scale}" fill="#ffffff" stroke="#2c3e50" stroke-width="2"/>'
        svg += f'<text x="{ox + draw_w/2}" y="{oy - 10}" {lbl_style} text-anchor="middle">{W} ม.</text>'
        svg += f'<text x="{ox - 15}" y="{oy + draw_h/2 + 5}" {lbl_style} text-anchor="end">{H} ม.</text>'
        svg += f'<text x="{ox + draw_w/2}" y="{oy + border_scale/2 + 5}" {lbl_style_sm} text-anchor="middle">กว้าง {p1} ม.</text>'
        
    elif scenario == "cross_path":
        p_scale = p1 * scale
        svg += f'<rect x="{ox}" y="{oy}" width="{draw_w}" height="{draw_h}" fill="#ffffff" stroke="none"/>'
        svg += f'<rect x="{ox}" y="{oy + (draw_h - p_scale)/2}" width="{draw_w}" height="{p_scale}" fill="#bdc3c7" stroke="none"/>'
        svg += f'<rect x="{ox + (draw_w - p_scale)/2}" y="{oy}" width="{p_scale}" height="{draw_h}" fill="#bdc3c7" stroke="none"/>'
        svg += f'<rect x="{ox}" y="{oy}" width="{draw_w}" height="{draw_h}" fill="none" stroke="#2c3e50" stroke-width="3"/>'
        svg += f'<text x="{ox + draw_w/2}" y="{oy + draw_h + 20}" {lbl_style} text-anchor="middle">{W} ม.</text>'
        svg += f'<text x="{ox - 15}" y="{oy + draw_h/2 + 5}" {lbl_style} text-anchor="end">{H} ม.</text>'
        svg += f'<text x="{ox + draw_w + 15}" y="{oy + draw_h/2 + 5}" {lbl_style_sm} text-anchor="start">ทางกว้าง {p1} ม.</text>'
        
    elif scenario == "triangle_in_rect":
        svg += f'<rect x="{ox}" y="{oy}" width="{draw_w}" height="{draw_h}" fill="#bdc3c7" stroke="#2c3e50" stroke-width="3"/>'
        svg += f'<polygon points="{ox},{oy+draw_h} {ox+draw_w},{oy+draw_h} {ox+draw_w/2},{oy}" fill="#ffffff" stroke="#2c3e50" stroke-width="2"/>'
        svg += f'<text x="{ox + draw_w/2}" y="{oy + draw_h + 25}" {lbl_style} text-anchor="middle">{W} ซม.</text>'
        svg += f'<text x="{ox - 15}" y="{oy + draw_h/2 + 5}" {lbl_style} text-anchor="end">{H} ซม.</text>'
        
    return svg + '</svg></div>'

# ==========================================
# ฟังก์ชันตัวช่วยสำหรับการตั้งหารยาวทศนิยม (ป.5)
# ==========================================
def get_decimal_long_div_html(divisor, dividend_str, max_dp=3):
    div_chars, ans_chars, steps, curr_val, i, dp_count = list(dividend_str), [], [], 0, 0, 0
    while True:
        if i < len(div_chars): char = div_chars[i]
        else:
            if '.' not in div_chars:
                div_chars.append('.'); ans_chars.append('.'); i += 1
                continue
            char = '0'; div_chars.append('0')
        if char == '.':
            if '.' not in ans_chars: ans_chars.append('.')
            i += 1; continue
        curr_val = curr_val * 10 + int(char)
        q = curr_val // divisor
        ans_chars.append(str(q))
        mul = q * divisor
        rem = curr_val - mul
        if q > 0 or i >= len(dividend_str) - 1:
            steps.append({'col': i, 'curr': curr_val, 'mul': mul, 'rem': rem})
        curr_val = rem
        if '.' in ans_chars: dp_count = len(ans_chars) - ans_chars.index('.') - 1
        i += 1
        if i >= len(dividend_str) and curr_val == 0: break
        if dp_count >= max_dp: break
    first_nonzero = False
    for j in range(len(ans_chars)):
        if ans_chars[j] == '.':
            if not first_nonzero and j > 0: ans_chars[j-1] = '0'
            break
        if ans_chars[j] != '0': first_nonzero = True
        elif not first_nonzero: ans_chars[j] = ''
    
    html = "<div style='margin: 15px 40px; font-family: \"Sarabun\", sans-serif; font-size: 24px;'><table style='border-collapse: collapse; text-align: center;'>"
    html += "<tr><td style='border: none;'></td>"
    for c in ans_chars: html += f"<td style='padding: 2px 10px; color: #c0392b; font-weight: bold;'>{c}</td>"
    html += "<td style='border: none;'></td></tr>" 
    html += f"<tr><td style='padding: 2px 15px; font-weight: bold; text-align: right;'>{divisor}</td>"
    for j, c in enumerate(div_chars):
        html += f"<td style='border-top: 2px solid #333; {'border-left: 2px solid #333;' if j == 0 else ''} padding: 2px 10px; font-weight: bold;'>{c}</td>"
    html += "<td style='border: none;'></td></tr>"
    for idx, step in enumerate(steps):
        if step['mul'] == 0 and step['curr'] == 0 and idx != len(steps)-1: continue
        if idx > 0:
            html += "<tr><td style='border: none;'></td>"
            cv_str, cols, c_ptr = str(step['curr']), [], step['col']
            while len(cols) < len(cv_str):
                if div_chars[c_ptr] != '.': cols.append(c_ptr)
                c_ptr -= 1
            cols.reverse()
            for j in range(len(div_chars) + 1):
                html += f"<td style='padding: 2px 10px;'>{cv_str[cols.index(j)]}</td>" if j in cols else "<td style='border: none;'></td>"
            html += "</tr>"
        html += "<tr><td style='border: none;'></td>"
        mul_str, cols, c_ptr = str(step['mul']), [], step['col']
        while len(cols) < len(mul_str):
            if div_chars[c_ptr] != '.': cols.append(c_ptr)
            c_ptr -= 1
        cols.reverse()
        for j in range(len(div_chars) + 1):
            if j in cols: html += f"<td style='border-bottom: 2px solid #333; padding: 2px 10px;'>{mul_str[cols.index(j)]}</td>"
            elif len(cols) > 0 and j == cols[-1] + 1: html += "<td style='padding: 2px 10px; font-weight: bold; color: #e74c3c;'>-</td>"
            else: html += "<td style='border: none;'></td>"
        html += "</tr>"
    if len(steps) > 0:
        html += "<tr><td style='border: none;'></td>"
        rem_str, cols, c_ptr = str(steps[-1]['rem']), [], steps[-1]['col']
        while len(cols) < len(rem_str):
            if div_chars[c_ptr] != '.': cols.append(c_ptr)
            c_ptr -= 1
        cols.reverse()
        for j in range(len(div_chars) + 1):
            html += f"<td style='border-bottom: 4px double #333; padding: 2px 10px;'>{rem_str[cols.index(j)]}</td>" if j in cols else "<td style='border: none;'></td>"
        html += "</tr>"
    html += "</table></div>"
    return html

def draw_frac(n, d):
    return f"<span style='display:inline-flex; flex-direction:column; vertical-align:middle; text-align:center; margin:0 4px; font-weight:bold; font-size:18px;'><span style='border-bottom:2px solid #2c3e50; padding:0 4px;'>{n}</span><span style='padding:0 4px;'>{d}</span></span>"

# ==========================================
# 3. Logic & Dynamic Difficulty Scaling (ป.5)
# ==========================================
def generate_questions_logic(grade, main_t, sub_t, num_q, is_challenge=False):
    questions, seen = [], set()
    
    for _ in range(num_q):
        q, sol, attempts = "", "", 0
        
        while attempts < 300:
            actual_sub_t = sub_t
            if sub_t == "แบบทดสอบรวมปลายภาค":
                rand_main = random.choice(list(curriculum_db[grade].keys()))
                actual_sub_t = random.choice(curriculum_db[grade][rand_main])

            # ================= หมวดที่ 1: เศษส่วน (ป.5) =================
            if actual_sub_t in ["การบวกเศษส่วน", "การลบเศษส่วน"]:
                op = "+" if actual_sub_t == "การบวกเศษส่วน" else "-"
                
                # ป.5 ตัวส่วนจะไม่เท่ากัน ต้องหา ค.ร.น.
                d1 = random.choice([3, 4, 5, 6, 8, 9, 10, 12])
                d2 = random.choice([x for x in [3, 4, 5, 6, 8, 9, 10, 12, 15] if x != d1])
                lcm = (d1 * d2) // math.gcd(d1, d2)
                
                if is_challenge:
                    n1 = random.randint(d1 + 1, d1 * 3) # เศษเกิน
                    n2 = random.randint(1, d2 * 2)
                else:
                    n1 = random.randint(1, d1 - 1)
                    n2 = random.randint(1, d2 - 1)
                
                # ถ้าเป็นการลบ ต้องแน่ใจว่าตัวตั้งมากกว่าตัวลบ
                if op == "-" and (n1/d1) < (n2/d2):
                    n1, n2 = n2, n1
                    d1, d2 = d2, d1
                
                m1, m2 = lcm // d1, lcm // d2
                new_n1, new_n2 = n1 * m1, n2 * m2
                
                if op == "+":
                    ans_n = new_n1 + new_n2
                else:
                    ans_n = new_n1 - new_n2
                
                gcd_ans = math.gcd(ans_n, lcm)
                final_n, final_d = ans_n // gcd_ans, lcm // gcd_ans
                
                # แปลงเป็นจำนวนคละถ้าจำเป็น
                if final_n > final_d and final_d != 1:
                    whole = final_n // final_d
                    rem = final_n % final_d
                    ans_disp = f"{whole}{draw_frac(rem, final_d)}" if rem != 0 else str(whole)
                else:
                    ans_disp = str(final_n) if final_d == 1 else draw_frac(final_n, final_d)

                q = f"จงหาผลลัพธ์ของ {draw_frac(n1, d1)} <b style='color:#e74c3c;'>{op}</b> {draw_frac(n2, d2)}"
                
                sol = f"""<span style='color:#2c3e50;'>
                <div style='background-color:#fcf3cf; border-left:4px solid #f1c40f; padding:10px; margin-bottom:15px; border-radius:4px;'>
                💡 <b>เทคนิคการ{actual_sub_t.replace('การ','')} (ตัวส่วนไม่เท่ากัน):</b><br>
                ต้องทำ <b>"ตัวส่วน"</b> ให้เท่ากันก่อน โดยการหา ค.ร.น. ของ {d1} และ {d2} ซึ่งก็คือ <b>{lcm}</b>
                </div>
                <b>วิธีทำอย่างละเอียด:</b><br>
                👉 <b>ขั้นที่ 1: ทำส่วนให้เท่ากัน (เป็น {lcm})</b><br>
                &nbsp;&nbsp;&nbsp;&nbsp;• {draw_frac(f"{n1} × <b style='color:#e74c3c;'>{m1}</b>", f"{d1} × <b style='color:#e74c3c;'>{m1}</b>")} = <b style='color:#2980b9;'>{draw_frac(new_n1, lcm)}</b><br>
                &nbsp;&nbsp;&nbsp;&nbsp;• {draw_frac(f"{n2} × <b style='color:#e74c3c;'>{m2}</b>", f"{d2} × <b style='color:#e74c3c;'>{m2}</b>")} = <b style='color:#2980b9;'>{draw_frac(new_n2, lcm)}</b><br><br>
                👉 <b>ขั้นที่ 2: นำเศษมา{op.replace('+','บวก').replace('-','ลบ')}กัน</b><br>
                &nbsp;&nbsp;&nbsp;&nbsp;{draw_frac(new_n1, lcm)} <b style='color:#e74c3c;'>{op}</b> {draw_frac(new_n2, lcm)} = {draw_frac(f"{new_n1} {op} {new_n2}", lcm)} = <b>{draw_frac(ans_n, lcm)}</b><br><br>
                """
                if gcd_ans > 1:
                    sol += f"""👉 <b>ขั้นที่ 3: ตัดทอนเป็นเศษส่วนอย่างต่ำ</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;นำ <b>{gcd_ans}</b> มาหารทั้งเศษและส่วน จะได้ <b>{draw_frac(final_n, final_d)}</b><br><br>"""
                
                if final_n > final_d and final_d != 1:
                    sol += f"👉 <b>ขั้นที่ 4: แปลงเป็นจำนวนคละ</b> ➔ <b>{ans_disp}</b><br><br>"
                    
                sol += f"<b>ตอบ: {ans_disp}</b></span>"



            elif actual_sub_t == "การคูณเศษส่วน":
                d1 = random.randint(3, 15)
                n1 = random.randint(1, d1 * 2) if is_challenge else random.randint(1, d1 - 1)
                
                type_mul = random.choice(["frac", "whole"])
                if type_mul == "whole":
                    n2 = random.randint(2, 20)
                    d2 = 1
                    q = f"จงหาผลลัพธ์ของ {draw_frac(n1, d1)} <b style='color:#e74c3c;'>×</b> <b>{n2}</b>"
                else:
                    d2 = random.randint(3, 15)
                    n2 = random.randint(1, d2 * 2) if is_challenge else random.randint(1, d2 - 1)
                    q = f"จงหาผลลัพธ์ของ {draw_frac(n1, d1)} <b style='color:#e74c3c;'>×</b> {draw_frac(n2, d2)}"
                
                ans_n_raw = n1 * n2
                ans_d_raw = d1 * d2
                gcd_ans = math.gcd(ans_n_raw, ans_d_raw)
                final_n, final_d = ans_n_raw // gcd_ans, ans_d_raw // gcd_ans
                
                ans_disp = str(final_n) if final_d == 1 else f"{final_n//final_d}{draw_frac(final_n%final_d, final_d)}" if final_n > final_d else draw_frac(final_n, final_d)
                
                sol = f"""<span style='color:#2c3e50;'>
                <div style='background-color:#ebf5fb; border-left:4px solid #3498db; padding:10px; margin-bottom:15px; border-radius:4px;'>
                💡 <b>เทคนิคการคูณเศษส่วน:</b><br>
                ไม่ต้องทำส่วนให้เท่ากัน! สามารถนำ <b>(เศษ × เศษ)</b> และ <b>(ส่วน × ส่วน)</b> ได้เลย ถ้ารูปไหนตัดทอนไขว้ได้ให้ตัดก่อนจะคำนวณง่ายขึ้น
                </div>
                <b>วิธีทำอย่างละเอียด:</b><br>
                👉 <b>ขั้นที่ 1: นำบนคูณบน ล่างคูณล่าง</b><br>
                &nbsp;&nbsp;&nbsp;&nbsp;{draw_frac(f"{n1} × {n2}", f"{d1} × {d2 if type_mul=='frac' else '1'}")} = <b>{draw_frac(ans_n_raw, ans_d_raw)}</b><br><br>
                """
                if gcd_ans > 1:
                    sol += f"""👉 <b>ขั้นที่ 2: ตัดทอนเป็นเศษส่วนอย่างต่ำ</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;ใช้แม่ <b>{gcd_ans}</b> หารทั้งบนและล่าง จะได้ <b>{draw_frac(final_n, final_d) if final_d != 1 else final_n}</b><br><br>"""
                
                sol += f"<b>ตอบ: {ans_disp}</b></span>"



            elif actual_sub_t == "การหารเศษส่วน":
                d1 = random.randint(2, 10)
                n1 = random.randint(1, d1 * 2)
                
                type_div = random.choice(["frac", "whole"])
                if type_div == "whole":
                    n2 = random.randint(2, 12)
                    d2 = 1
                    q = f"จงหาผลลัพธ์ของ {draw_frac(n1, d1)} <b style='color:#e74c3c;'>÷</b> <b>{n2}</b>"
                    flip_text = f"{draw_frac(1, n2)}"
                else:
                    d2 = random.randint(2, 10)
                    n2 = random.randint(1, d2 - 1)
                    q = f"จงหาผลลัพธ์ของ {draw_frac(n1, d1)} <b style='color:#e74c3c;'>÷</b> {draw_frac(n2, d2)}"
                    flip_text = f"{draw_frac(d2, n2)}"
                
                ans_n_raw = n1 * d2
                ans_d_raw = d1 * n2
                gcd_ans = math.gcd(ans_n_raw, ans_d_raw)
                final_n, final_d = ans_n_raw // gcd_ans, ans_d_raw // gcd_ans
                
                ans_disp = str(final_n) if final_d == 1 else f"{final_n//final_d}{draw_frac(final_n%final_d, final_d)}" if final_n > final_d else draw_frac(final_n, final_d)
                
                sol = f"""<span style='color:#2c3e50;'>
                <div style='background-color:#fef5e7; border-left:4px solid #e67e22; padding:10px; margin-bottom:15px; border-radius:4px;'>
                💡 <b>คาถาการหารเศษส่วน:</b><br>
                <b>"ตัวหน้าเหมือนเดิม เปลี่ยนหาร(÷) เป็นคูณ(×) และกลับเศษเป็นส่วนที่ตัวหลัง"</b>
                </div>
                <b>วิธีทำอย่างละเอียด:</b><br>
                👉 <b>ขั้นที่ 1: เปลี่ยนเครื่องหมายและกลับตัวหลัง</b><br>
                &nbsp;&nbsp;&nbsp;&nbsp;จากโจทย์ กลายเป็น ➔ {draw_frac(n1, d1)} <b style='color:#27ae60;'>×</b> <b style='color:#8e44ad;'>{flip_text}</b><br><br>
                👉 <b>ขั้นที่ 2: คูณเศษส่วนตามปกติ (บน×บน, ล่าง×ล่าง)</b><br>
                &nbsp;&nbsp;&nbsp;&nbsp;{draw_frac(f"{n1} × {d2}", f"{d1} × {n2}")} = <b>{draw_frac(ans_n_raw, ans_d_raw)}</b><br><br>
                """
                if gcd_ans > 1:
                    sol += f"""👉 <b>ขั้นที่ 3: ทำให้เป็นเศษส่วนอย่างต่ำ/จำนวนคละ</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;จะได้ <b>{ans_disp}</b><br><br>"""
                    
                sol += f"<b>ตอบ: {ans_disp}</b></span>"



            # ================= หมวดที่ 2: ทศนิยม (ป.5) =================
            elif actual_sub_t == "การบวกและการลบทศนิยม":
                op = random.choice(["+", "-"])
                # ป.5 เน้นทศนิยม 2-3 ตำแหน่งที่ไม่เท่ากัน
                dp1, dp2 = random.choice([1, 2, 3]), random.choice([1, 2, 3])
                while dp1 == dp2: dp2 = random.choice([1, 2, 3])
                
                if op == "+": 
                    a = round(random.uniform(10.0, 500.0), dp1)
                    b = round(random.uniform(1.0, 99.0), dp2)
                else: 
                    a = round(random.uniform(100.0, 500.0), dp1)
                    b = round(random.uniform(10.0, a - 10.0), dp2)
                
                q = f"จงตั้งทดเพื่อหาผลลัพธ์ของ <b>{a} {op} {b}</b><br>{generate_decimal_vertical_html(a, b, op, is_key=False)}"
                
                sol = f"""<span style='color:#2c3e50;'>
                <div style='background-color:#fcf3cf; border-left:4px solid #f1c40f; padding:10px; margin-bottom:15px; border-radius:4px;'>
                💡 <b>เทคนิค:</b> เมื่อตำแหน่งทศนิยมไม่เท่ากัน ให้ <b>"เติม 0"</b> ด้านหลังตัวที่ตำแหน่งน้อยกว่า เพื่อให้การตั้งจุดทศนิยมและการยืมเลขไม่ผิดพลาด
                </div>
                {generate_decimal_vertical_html(a, b, op, is_key=True)}</span>"""



            elif actual_sub_t == "การคูณและการหารทศนิยม":
                op = random.choice(["×", "÷"])
                
                if op == "×":
                    # การคูณ: ทศนิยม 1-2 ตำแหน่ง คูณ ทศนิยม 1-2 ตำแหน่ง
                    v1 = round(random.uniform(1.1, 25.5), random.choice([1, 2]))
                    v2 = round(random.uniform(1.1, 9.9), random.choice([1, 2]))
                    ans = round(v1 * v2, 4)
                    
                    dec_p1 = len(str(v1).split('.')[1])
                    dec_p2 = len(str(v2).split('.')[1])
                    total_dec = dec_p1 + dec_p2
                    
                    ans_raw = int(str(v1).replace('.', '')) * int(str(v2).replace('.', ''))
                    
                    q = f"จงหาผลคูณของ <b>{v1} × {v2}</b>"
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    <div style='background-color:#ebf5fb; border-left:4px solid #3498db; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    💡 <b>เทคนิคการคูณทศนิยม:</b><br>
                    1. ถอดจุดออกแล้วนำตัวเลขมาตั้งคูณกันเหมือนจำนวนเต็มปกติ<br>
                    2. นำจำนวนตำแหน่งทศนิยมของตัวตั้งและตัวคูณมา <b>บวกกัน</b> เพื่อกำหนดตำแหน่งทศนิยมของคำตอบ
                    </div>
                    <b>วิธีทำ:</b><br>
                    👉 <b>ขั้นที่ 1:</b> {v1} มี <b>{dec_p1} ตำแหน่ง</b> และ {v2} มี <b>{dec_p2} ตำแหน่ง</b> (รวมเป็น <b style='color:#e74c3c;'>{total_dec} ตำแหน่ง</b>)<br>
                    👉 <b>ขั้นที่ 2:</b> ถอดจุดแล้วตั้งคูณ ➔ {int(str(v1).replace('.', ''))} × {int(str(v2).replace('.', ''))} = <b>{ans_raw:,}</b><br>
                    👉 <b>ขั้นที่ 3:</b> ใส่ทศนิยมกลับไป {total_dec} ตำแหน่ง จะได้ <b>{ans}</b><br><br>
                    <b>ตอบ: {ans}</b></span>"""
                
                else:
                    # การหารทศนิยมด้วยทศนิยม (เนื้อหาหลัก ป.5)
                    ans_raw = random.randint(12, 150)
                    divisor = round(random.choice([0.2, 0.4, 0.5, 1.2, 1.5, 2.5]), 1)
                    
                    dividend = round(ans_raw * divisor, 2)
                    
                    # หาวิธีเลื่อนจุด
                    move_step = 10 if len(str(divisor).split('.')[1]) == 1 else 100
                    new_dividend = dividend * move_step
                    new_divisor = int(divisor * move_step)
                    
                    # เช็คว่าผลคูณเป็น .0 ไหม ถ้าใช่ให้ตัดออก
                    new_dividend_str = str(int(new_dividend)) if new_dividend.is_integer() else str(new_dividend)
                    
                    q_eq = f"<div style='font-size: 24px; margin-bottom: 10px;'><b>{dividend} ÷ {divisor} = ?</b></div>"
                    
                    q = f"จงหาผลหารของทศนิยมต่อไปนี้<br>{q_eq}"
                    
                    long_div_html = get_decimal_long_div_html(new_divisor, new_dividend_str)
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    <div style='background-color:#fcf3cf; border-left:4px solid #f1c40f; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    💡 <b>เทคนิคการหารทศนิยม:</b><br>
                    <b>ห้ามตั้งหารถ้าตัวหารยังติดจุด!</b> ต้องเลื่อนจุดตัวหารให้เป็นจำนวนเต็มก่อน โดยเลื่อนจุดตัวตั้งตามไปเท่าๆ กัน (คือการคูณด้วย 10, 100 หรือ 1000)
                    </div>
                    <b>วิธีทำ:</b><br>
                    👉 <b>ขั้นที่ 1: เลื่อนจุดให้ตัวหารเป็นจำนวนเต็ม</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;• ตัวหารคือ {divisor} เลื่อน 1 จุด (คูณ 10) กลายเป็น <b>{new_divisor}</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;• ตัวตั้งคือ {dividend} ต้องเลื่อน 1 จุดตามกัน กลายเป็น <b>{new_dividend_str}</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;<i>(โจทย์ใหม่คือ: <b>{new_dividend_str} ÷ {new_divisor}</b>)</i><br><br>
                    👉 <b>ขั้นที่ 2: ตั้งหารยาว</b><br>
                    {long_div_html}<br>
                    <b>ตอบ: {ans_raw}</b></span>"""



# ================= หมวดที่ 3: สถิติ, เรขาคณิต, ร้อยละ, สมการ (ป.5) =================
            elif actual_sub_t == "การหาค่าเฉลี่ย (Average)":
                items_count = random.randint(4, 6)
                target_avg = random.randint(20, 100)
                total = target_avg * items_count
                
                # สร้างตัวเลขสุ่มที่รวมกันได้ total พอดี
                nums = []
                current_sum = 0
                for i in range(items_count - 1):
                    n = random.randint(target_avg - 15, target_avg + 15)
                    nums.append(n)
                    current_sum += n
                
                last_num = total - current_sum
                # ถ้าเลขสุดท้ายติดลบ หรือโดดเกินไป ให้จัดใหม่แบบง่ายๆ
                if last_num <= 0 or abs(last_num - target_avg) > 30:
                    nums = [target_avg - 5, target_avg + 10, target_avg - 10, target_avg + 5][:items_count]
                    nums[-1] = total - sum(nums[:-1])
                    
                random.shuffle(nums)
                nums_str = ", ".join(map(str, nums))
                
                q = f"จงหา <b>'ค่าเฉลี่ย'</b> ของชุดข้อมูลต่อไปนี้: <b style='color:#2980b9;'>{nums_str}</b>"
                
                sol = f"""<span style='color:#2c3e50;'>
                <div style='background-color:#e8f8f5; border-left:4px solid #1abc9c; padding:10px; margin-bottom:15px; border-radius:4px;'>
                💡 <b>สูตรการหาค่าเฉลี่ย:</b><br>
                ค่าเฉลี่ย = (ผลรวมของข้อมูลทั้งหมด) ÷ (จำนวนของข้อมูล)
                </div>
                <b>วิธีทำอย่างละเอียด:</b><br>
                👉 <b>ขั้นที่ 1: หาผลรวมของข้อมูลทั้งหมด</b><br>
                &nbsp;&nbsp;&nbsp;&nbsp;นำ {nums_str.replace(', ', ' + ')} = <b>{total}</b><br><br>
                👉 <b>ขั้นที่ 2: นับจำนวนข้อมูล</b><br>
                &nbsp;&nbsp;&nbsp;&nbsp;ข้อมูลชุดนี้มีทั้งหมด <b>{items_count}</b> จำนวน<br><br>
                👉 <b>ขั้นที่ 3: นำผลรวมหารด้วยจำนวนข้อมูล</b><br>
                &nbsp;&nbsp;&nbsp;&nbsp;{total} ÷ {items_count} = <b>{target_avg}</b><br><br>
                <b>ตอบ: ค่าเฉลี่ยของข้อมูลชุดนี้คือ {target_avg}</b></span>"""



            elif actual_sub_t == "ความน่าจะเป็นเบื้องต้น (สุ่มหยิบของ)":
                colors = ["สีแดง", "สีฟ้า", "สีเขียว", "สีเหลือง"]
                selected_colors = random.sample(colors, 3)
                
                c1_qty = random.randint(3, 8)
                c2_qty = random.randint(2, 6)
                c3_qty = random.randint(1, 4)
                
                color_counts = {selected_colors[0]: c1_qty, selected_colors[1]: c2_qty, selected_colors[2]: c3_qty}
                total_marbles = sum(color_counts.values())
                
                target_color = random.choice(selected_colors)
                target_qty = color_counts[target_color]
                
                gcd_val = math.gcd(target_qty, total_marbles)
                ans_n, ans_d = target_qty // gcd_val, total_marbles // gcd_val
                ans_str = f"{ans_n}/{ans_d}"
                
                svg = draw_marbles_box_svg(color_counts)
                
                q = f"ในกล่องทึบใบหนึ่งมีลูกแก้วสีต่างๆ ดังภาพ หากสุ่มหยิบลูกแก้วขึ้นมา 1 ลูก โอกาสที่จะหยิบได้ลูกแก้ว <b><span style='color:#e74c3c;'>{target_color}</span></b> คิดเป็นเศษส่วนเท่าใด?<br>{svg}"
                
                sol = f"""<span style='color:#2c3e50;'>
                <div style='background-color:#fef5e7; border-left:4px solid #e67e22; padding:10px; margin-bottom:15px; border-radius:4px;'>
                💡 <b>หลักความน่าจะเป็นเบื้องต้น:</b><br>
                โอกาส (ความน่าจะเป็น) = (สิ่งที่สนใจ) ÷ (สิ่งที่เป็นไปได้ทั้งหมด)
                </div>
                <b>วิธีทำอย่างละเอียด:</b><br>
                👉 <b>ขั้นที่ 1: หาจำนวนลูกแก้วทั้งหมด (เหตุการณ์ที่เป็นไปได้ทั้งหมด)</b><br>
                &nbsp;&nbsp;&nbsp;&nbsp;ลูกแก้วในกล่องมี {selected_colors[0]} {c1_qty} ลูก, {selected_colors[1]} {c2_qty} ลูก, {selected_colors[2]} {c3_qty} ลูก<br>
                &nbsp;&nbsp;&nbsp;&nbsp;รวมทั้งหมด = <b>{total_marbles}</b> ลูก<br><br>
                👉 <b>ขั้นที่ 2: หาจำนวนลูกแก้วสีที่โจทย์ถาม (เหตุการณ์ที่สนใจ)</b><br>
                &nbsp;&nbsp;&nbsp;&nbsp;โจทย์ถามหา <b>{target_color}</b> ซึ่งมีอยู่ <b>{target_qty}</b> ลูก<br><br>
                👉 <b>ขั้นที่ 3: เขียนเป็นเศษส่วนและตัดทอน</b><br>
                &nbsp;&nbsp;&nbsp;&nbsp;โอกาสที่จะหยิบได้ = {draw_frac(target_qty, total_marbles)}<br>
                """
                if gcd_val > 1:
                    sol += f"&nbsp;&nbsp;&nbsp;&nbsp;ตัดทอนเป็นเศษส่วนอย่างต่ำโดยใช้แม่ {gcd_val} หาร จะได้ = <b>{draw_frac(ans_n, ans_d)}</b><br><br>"
                sol += f"<b>ตอบ: โอกาสที่จะได้{target_color}คือ {ans_str}</b></span>"



            elif actual_sub_t == "โจทย์ปัญหาพื้นที่และความยาวรอบรูป":
                # ป.5 จะเริ่มมีโจทย์พลิกแพลง เช่น ให้เส้นรอบรูปมา ถามหาพื้นที่
                scenario = random.choice([1, 2])
                
                if scenario == 1:
                    # ให้พื้นที่และด้านกว้างมา ถามหาความยาวรอบรูป
                    w = random.randint(5, 15)
                    l = random.randint(w + 2, w + 15)
                    area = w * l
                    peri = 2 * (w + l)
                    
                    q = f"สนามหญ้ารูปสี่เหลี่ยมผืนผ้าแห่งหนึ่งมี <b>พื้นที่ {area} ตารางเมตร</b> ถ้ารู้ว่าสนามหญ้ากว้าง <b>{w} เมตร</b> <br>สนามหญ้าแห่งนี้จะมีความยาวรอบรูปกี่เมตร?"
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    <div style='background-color:#ebf5fb; border-left:4px solid #3498db; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    💡 <b>เทคนิคย้อนกลับ (Reverse Engineering):</b><br>
                    โจทย์ให้พื้นที่มาก่อน เราต้องใช้สูตรพื้นที่ <i>(กว้าง × ยาว = พื้นที่)</i> เพื่อหา <b>"ด้านยาว"</b> ที่หายไป จากนั้นจึงจะไปหาความยาวรอบรูปได้
                    </div>
                    <b>วิธีทำอย่างละเอียด:</b><br>
                    👉 <b>ขั้นที่ 1: หาด้านยาวที่หายไป</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;จากสูตร: กว้าง × ยาว = พื้นที่<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;แทนค่า: {w} × ยาว = {area}<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;จะได้: ยาว = {area} ÷ {w} = <b>{l} เมตร</b><br><br>
                    👉 <b>ขั้นที่ 2: หาความยาวรอบรูป</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;สูตร: (กว้าง + ยาว) × 2<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;แทนค่า: ({w} + {l}) × 2 = {w+l} × 2 = <b>{peri} เมตร</b><br><br>
                    <b>ตอบ: ความยาวรอบรูปของสนามหญ้าคือ {peri} เมตร</b></span>"""
                else:
                    # ให้ความยาวรอบรูปจัตุรัสมา ถามหาพื้นที่
                    side = random.randint(8, 25)
                    peri = side * 4
                    area = side * side
                    
                    q = f"กระเบื้องรูปสี่เหลี่ยมจัตุรัสแผ่นหนึ่งมีความยาวรอบรูป <b>{peri} เซนติเมตร</b> กระเบื้องแผ่นนี้มีพื้นที่กี่ตารางเซนติเมตร?"
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    <div style='background-color:#ebf5fb; border-left:4px solid #3498db; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    💡 <b>เทคนิคย้อนกลับ (Reverse Engineering):</b><br>
                    โจทย์ให้ความยาวรอบรูปของสี่เหลี่ยมจัตุรัสมา (ซึ่งเกิดจาก ด้าน × 4) เราต้องนำไป <b>หาร 4</b> เพื่อหาความยาว 1 ด้านก่อน แล้วจึงนำไปหาพื้นที่
                    </div>
                    <b>วิธีทำอย่างละเอียด:</b><br>
                    👉 <b>ขั้นที่ 1: หาความยาวของ 1 ด้าน</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;สี่เหลี่ยมจัตุรัสมี 4 ด้านที่ยาวเท่ากัน<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;ความยาว 1 ด้าน = {peri} ÷ 4 = <b>{side} เซนติเมตร</b><br><br>
                    👉 <b>ขั้นที่ 2: หาพื้นที่</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;สูตร: ด้าน × ด้าน<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;แทนค่า: {side} × {side} = <b>{area} ตารางเซนติเมตร</b><br><br>
                    <b>ตอบ: กระเบื้องแผ่นนี้มีพื้นที่ {area} ตารางเซนติเมตร</b></span>"""



            elif actual_sub_t == "เส้นขนานและมุมแย้ง":
                # สุ่มมุมและตำแหน่งของเส้นขนาน
                base_angle = random.randint(45, 135)
                dir_key = random.choice(["dir1", "dir2"])
                angle_type = random.choice(["มุมแย้งภายใน", "มุมภายในที่อยู่บนข้างเดียวกันของเส้นตัด", "มุมสมนัย (มุมแย้งภายนอก)"])
                
                if dir_key == "dir1":
                    pos_acute = ["TR_ext", "BL_int", "TL_int", "BR_ext"]
                else:
                    pos_acute = ["TL_ext", "BR_int", "TR_int", "BL_ext"]

                if angle_type == "มุมแย้งภายใน":
                    # มุมแย้งจะเท่ากัน
                    pos1 = "TL_int"
                    pos2 = "BR_int" if dir_key == "dir2" else "BL_int" # ปรับตำแหน่งให้เป็นมุมแย้ง
                    ans_val = base_angle
                    reason = "มุมแย้งจะมีขนาดเท่ากัน"
                    eq_str = f"x = {base_angle}°"
                
                elif angle_type == "มุมภายในที่อยู่บนข้างเดียวกันของเส้นตัด":
                    # มุมภายในรวมกันได้ 180
                    pos1 = "TL_int"
                    pos2 = "BL_int" if dir_key == "dir2" else "TR_int"
                    ans_val = 180 - base_angle
                    reason = "มุมภายในที่อยู่บนข้างเดียวกันของเส้นตัดรวมกันจะได้ 180°"
                    eq_str = f"x = 180° - {base_angle}° = {ans_val}°"
                    
                else:
                    # สมนัย/มุมตรงข้าม
                    pos1 = "TL_ext" if dir_key == "dir2" else "TR_ext"
                    pos2 = "TL_int" if dir_key == "dir2" else "TR_int"
                    ans_val = base_angle
                    reason = "มุมภายนอกและมุมภายในที่อยู่ตรงข้ามกันบนข้างเดียวกันของเส้นตัด (มุมสมนัย) มีขนาดเท่ากัน"
                    eq_str = f"x = {base_angle}°"

                svg = draw_parallel_svg(dir_key, pos1, base_angle, pos2, "x")
                
                q = f"กำหนดให้เส้นตรง AB ขนานกับเส้นตรง CD จากภาพจงหาขนาดของมุม <b>x</b><br>{svg}"
                
                sol = f"""<span style='color:#2c3e50;'>
                <div style='background-color:#fef5e7; border-left:4px solid #e67e22; padding:10px; margin-bottom:15px; border-radius:4px;'>
                💡 <b>สมบัติของเส้นขนาน:</b><br>
                เมื่อมีเส้นตรงเส้นหนึ่งตัดเส้นขนานคู่หนึ่ง <b>{reason}</b>
                </div>
                <b>วิธีทำ:</b><br>
                👉 พิจารณาตำแหน่งของมุม {base_angle}° และมุม x พบว่าเป็นความสัมพันธ์แบบ <b>{angle_type}</b><br>
                👉 ดังนั้น <b>{eq_str}</b><br><br>
                <b>ตอบ: ขนาดของมุม x คือ {ans_val}°</b></span>"""



            elif actual_sub_t == "ปริมาตรและความจุทรงสี่เหลี่ยมมุมฉาก":
                scenario = random.choice(["volume", "water"])
                
                w = random.randint(10, 30)
                l = random.randint(w + 5, 50)
                h = random.randint(15, 40)
                
                if scenario == "volume":
                    vol = w * l * h
                    svg = draw_prism_svg(f"กว้าง {w} ซม.", f"ยาว {l} ซม.", f"สูง {h} ซม.", is_water=False)
                    q = f"กล่องทรงสี่เหลี่ยมมุมฉากใบหนึ่งมีขนาดดังภาพ กล่องใบนี้มีความจุ (ปริมาตร) ทั้งหมดกี่ลูกบาศก์เซนติเมตร?<br>{svg}"
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    <div style='background-color:#e8f8f5; border-left:4px solid #1abc9c; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    💡 <b>สูตรหาปริมาตรทรงสี่เหลี่ยมมุมฉาก:</b><br>
                    ปริมาตร = ความกว้าง × ความยาว × ความสูง
                    </div>
                    <b>วิธีทำอย่างละเอียด:</b><br>
                    👉 <b>ขั้นที่ 1: สกัดข้อมูลจากภาพ</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;ความกว้าง = {w} ซม., ความยาว = {l} ซม., ความสูง = {h} ซม.<br><br>
                    👉 <b>ขั้นที่ 2: แทนค่าในสูตร</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;{w} × {l} × {h} = <b>{vol:,}</b> ลูกบาศก์เซนติเมตร<br><br>
                    <b>ตอบ: ความจุกระดาษของกล่องใบนี้คือ {vol:,} ลูกบาศก์เซนติเมตร</b></span>"""
                else:
                    # ระดับน้ำ
                    h_water = random.randint(5, h - 5)
                    vol_water = w * l * h_water
                    svg = draw_prism_svg(f"กว้าง {w} ซม.", f"ยาว {l} ซม.", f"ระดับน้ำสูง {h_water} ซม.", is_water=True)
                    q = f"ตู้ปลาทรงสี่เหลี่ยมมุมฉาก มีน้ำบรรจุอยู่ตามระดับในภาพ ปริมาตรของน้ำในตู้ปลาคือเท่าใด?<br>{svg}"
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    <div style='background-color:#e8f8f5; border-left:4px solid #1abc9c; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    💡 <b>ข้อควรระวังเรื่องระดับน้ำ:</b><br>
                    การหาปริมาตรน้ำ ให้ใช้ <b>"ความสูงของระดับน้ำ"</b> ไม่ใช่ความสูงของตู้ปลาทั้งหมด! ส่วนความกว้างและความยาวจะเท่ากับขนาดของตู้
                    </div>
                    <b>วิธีทำอย่างละเอียด:</b><br>
                    👉 <b>ขั้นที่ 1: สกัดข้อมูล</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;ความกว้างตู้ = {w} ซม., ความยาวตู้ = {l} ซม., <b>ความสูงของน้ำ = {h_water} ซม.</b><br><br>
                    👉 <b>ขั้นที่ 2: ใช้สูตร กว้าง × ยาว × สูง (ของน้ำ)</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;{w} × {l} × {h_water} = <b>{vol_water:,}</b> ลูกบาศก์เซนติเมตร<br><br>
                    <b>ตอบ: ปริมาตรของน้ำคือ {vol_water:,} ลูกบาศก์เซนติเมตร</b></span>"""



            elif actual_sub_t == "การเขียนเศษส่วนในรูปร้อยละ":
                # ป.5 จะเน้นตัวส่วนที่เป็นพหุคูณของ 100 เช่น 2, 4, 5, 10, 20, 25, 50
                d = random.choice([2, 4, 5, 10, 20, 25, 50])
                n = random.randint(1, d - 1)
                
                multiplier = 100 // d
                percent_val = n * multiplier
                
                q = f"จงเขียนเศษส่วน {draw_frac(n, d)} ให้อยู่ในรูปของ <b>ร้อยละ (เปอร์เซ็นต์)</b>"
                
                sol = f"""<span style='color:#2c3e50;'>
                <div style='background-color:#fcf3cf; border-left:4px solid #f1c40f; padding:10px; margin-bottom:15px; border-radius:4px;'>
                💡 <b>เทคนิคการแปลงร้อยละ:</b><br>
                คำว่า "ร้อยละ" หรือ "%" หมายถึง <b>"ส่วนเป็น 100"</b> ดังนั้นเราต้องหาตัวเลขมาคูณตัวส่วนให้กลายเป็น 100 ให้ได้
                </div>
                <b>วิธีทำอย่างละเอียด:</b><br>
                👉 <b>ขั้นที่ 1: หาตัวเลขมาคูณให้ส่วนเป็น 100</b><br>
                &nbsp;&nbsp;&nbsp;&nbsp;ตัวส่วนคือ <b>{d}</b> นำไปคูณกับอะไรได้ 100? ➔ (100 ÷ {d} = <b style='color:#e74c3c;'>{multiplier}</b>)<br><br>
                👉 <b>ขั้นที่ 2: นำไปคูณทั้งเศษและส่วน</b><br>
                &nbsp;&nbsp;&nbsp;&nbsp;{draw_frac(f"{n} × <b style='color:#e74c3c;'>{multiplier}</b>", f"{d} × <b style='color:#e74c3c;'>{multiplier}</b>")} = <b style='color:#2980b9;'>{draw_frac(percent_val, 100)}</b><br><br>
                👉 <b>ขั้นที่ 3: สรุปผล</b><br>
                &nbsp;&nbsp;&nbsp;&nbsp;เมื่อส่วนเป็น 100 แล้ว สามารถนำตัวเศษมาเขียนเป็นร้อยละได้เลย<br>
                &nbsp;&nbsp;&nbsp;&nbsp;➔ <b>ร้อยละ {percent_val}</b> หรือ <b>{percent_val}%</b><br><br>
                <b>ตอบ: ร้อยละ {percent_val} (หรือ {percent_val}%)</b></span>"""



            elif actual_sub_t == "การแก้สมการ (คูณ/หาร)":
                mode = random.choice(["mul", "div"])
                var = random.choice(["a", "b", "m", "x", "y"])
                
                ans_val = random.randint(12, 60)
                
                if mode == "mul":
                    coef = random.randint(3, 15)
                    res = coef * ans_val
                    q = f"จงแก้สมการเพื่อหาค่าของ <b>{var}</b><br><span style='font-size:24px;'><b>{coef}{var} = {res}</b></span>"
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    <div style='background-color:#fef5e7; border-left:4px solid #e67e22; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    💡 <b>หลักการแก้สมการ:</b><br>
                    ย้ายข้างตัวเลขที่อยู่กับตัวแปรไปอีกฝั่ง โดยต้อง <b>"เปลี่ยนเครื่องหมายให้เป็นตรงข้าม"</b><br>
                    (จาก คูณ เปลี่ยนเป็น หาร / จาก หาร เปลี่ยนเป็น คูณ)
                    </div>
                    <b>วิธีทำอย่างละเอียด:</b><br>
                    👉 <b>ขั้นที่ 1: วิเคราะห์สมการ</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;{coef}{var} หมายถึง {coef} <b>คูณ</b> อยู่กับ {var}<br><br>
                    👉 <b>ขั้นที่ 2: ย้ายข้าง</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;ย้าย {coef} ไปอีกฝั่ง จาก <b>"คูณ"</b> ต้องเปลี่ยนเป็น <b>"หาร"</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;{var} = {res} ÷ {coef}<br><br>
                    👉 <b>ขั้นที่ 3: คำนวณผลลัพธ์</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;{var} = <b>{ans_val}</b><br><br>
                    <b>ตอบ: {var} = {ans_val}</b></span>"""
                else:
                    divisor = random.randint(3, 12)
                    dividend = ans_val
                    res = dividend
                    
                    q = f"จงแก้สมการเพื่อหาค่าของ <b>{var}</b><br><span style='font-size:24px;'><b>{draw_frac(var, divisor)} = {res}</b></span>"
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    <div style='background-color:#fef5e7; border-left:4px solid #e67e22; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    💡 <b>หลักการแก้สมการ:</b><br>
                    ย้ายข้างตัวเลขที่อยู่กับตัวแปรไปอีกฝั่ง โดยต้อง <b>"เปลี่ยนเครื่องหมายให้เป็นตรงข้าม"</b><br>
                    (จาก คูณ เปลี่ยนเป็น หาร / จาก หาร เปลี่ยนเป็น คูณ)
                    </div>
                    <b>วิธีทำอย่างละเอียด:</b><br>
                    👉 <b>ขั้นที่ 1: วิเคราะห์สมการ</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;{draw_frac(var, divisor)} หมายถึง {var} กำลังถูก <b>หาร</b> ด้วย {divisor}<br><br>
                    👉 <b>ขั้นที่ 2: ย้ายข้าง</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;ย้าย {divisor} ไปอีกฝั่ง จาก <b>"หาร"</b> ต้องเปลี่ยนเป็น <b>"คูณ"</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;{var} = {res} × {divisor}<br><br>
                    👉 <b>ขั้นที่ 3: คำนวณผลลัพธ์</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;{var} = <b>{res * divisor}</b><br><br>
                    <b>ตอบ: {var} = {res * divisor}</b></span>"""



# ================= หมวดที่ 4: เตรียมสอบเข้า ม.1 Gifted (ป.5) =================
            elif actual_sub_t == "โจทย์ปัญหา ห.ร.ม. และ ค.ร.น.":
                prob_type = random.choice(["gcd", "lcm"])
                
                if prob_type == "gcd":
                    # โจทย์ปัญหา ห.ร.ม. (แบ่งของให้ได้มากที่สุด)
                    gcd_target = random.choice([4, 5, 6, 8, 10, 12, 15])
                    n1 = gcd_target * random.choice([2, 3, 4])
                    n2 = gcd_target * random.choice([5, 6, 7])
                    n3 = gcd_target * random.choice([8, 9, 11])
                    
                    items = ["ส้ม", "แอปเปิ้ล", "มังคุด"]
                    random.shuffle(items)
                    
                    q = f"แม่ค้ามี{items[0]} <b>{n1}</b> ผล, {items[1]} <b>{n2}</b> ผล และ{items[2]} <b>{n3}</b> ผล ต้องการจัดใส่ถาด ถาดละเท่าๆ กัน โดยไม่ปนกันและไม่มีผลไม้เหลืออยู่เลย<br>แม่ค้าจะจัดผลไม้ได้ <b>มากที่สุด</b> ถาดละกี่ผล?"
                    
                    html_div, divisors, _ = render_short_div([n1, n2, n3], mode="gcd")
                    ans = math.prod(divisors) if divisors else gcd_target
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    <div style='background-color:#fcf3cf; border-left:4px solid #f1c40f; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    💡 <b>วิเคราะห์คีย์เวิร์ด:</b><br>
                    คำว่า <b>"แบ่งเท่าๆ กันให้ได้มากที่สุดโดยไม่เหลือเศษ"</b> เป็นสัญญาณว่าต้องใช้ <b>ห.ร.ม. (หาร่วมมาก)</b>
                    </div>
                    <b>วิธีทำ: ตั้งหารสั้นเพื่อหา ห.ร.ม. ของ {n1}, {n2}, {n3}</b>
                    {html_div}
                    👉 นำตัวหารทั้งหมดมาคูณกัน: {" × ".join(map(str, divisors))} = <b>{ans}</b><br><br>
                    <b>ตอบ: จะจัดผลไม้ได้มากที่สุดถาดละ {ans} ผล</b></span>"""
                
                else:
                    # โจทย์ปัญหา ค.ร.น. (ออกพร้อมกัน)
                    lcm_target = random.choice([60, 120, 180, 240]) # นาที
                    times = []
                    if lcm_target == 60: times = [12, 15, 20]
                    elif lcm_target == 120: times = [15, 24, 40]
                    elif lcm_target == 180: times = [20, 36, 45]
                    else: times = [30, 40, 60]
                    
                    t1, t2, t3 = times[0], times[1], times[2]
                    
                    start_h = random.randint(6, 10)
                    start_m = random.choice([0, 15, 30])
                    
                    # คำนวณเวลาถัดไป
                    total_minutes = start_h * 60 + start_m + lcm_target
                    next_h = (total_minutes // 60) % 24
                    next_m = total_minutes % 60
                    
                    start_str = f"{start_h:02d}.{start_m:02d}"
                    next_str = f"{next_h:02d}.{next_m:02d}"
                    
                    q = f"รถโดยสาร 3 สาย ออกจากสถานีทุกๆ <b>{t1} นาที</b>, <b>{t2} นาที</b> และ <b>{t3} นาที</b> ตามลำดับ ถ้ารถทั้งสามสายออกพร้อมกันครั้งแรกเวลา <b>{start_str} น.</b><br>รถทั้งสามสายจะออกจากสถานีพร้อมกันอีกครั้งในเวลาใด?"
                    
                    html_div, divisors, remainders = render_short_div([t1, t2, t3], mode="lcm")
                    ans_lcm = math.prod(divisors) * math.prod(remainders)
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    <div style='background-color:#ebf5fb; border-left:4px solid #3498db; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    💡 <b>วิเคราะห์คีย์เวิร์ด:</b><br>
                    คำว่า <b>"เหตุการณ์ที่จะเกิดขึ้นพร้อมกันอีกครั้งในอนาคต"</b> เป็นสัญญาณว่าต้องใช้ <b>ค.ร.น. (คูณร่วมน้อย)</b>
                    </div>
                    <b>วิธีทำ: ตั้งหารสั้นเพื่อหา ค.ร.น. ของ {t1}, {t2}, {t3}</b>
                    {html_div}
                    👉 นำตัวหารและเศษมาคูณกัน: {" × ".join(map(str, divisors))} × {" × ".join(map(str, remainders))} = <b>{ans_lcm}</b> นาที<br>
                    👉 แปลง {ans_lcm} นาที เป็นชั่วโมง ➔ {ans_lcm} ÷ 60 = <b>{ans_lcm//60} ชั่วโมง</b><br>
                    👉 นับต่อจากเวลา {start_str} น. ไปอีก {ans_lcm//60} ชั่วโมง จะตรงกับเวลา <b>{next_str} น.</b><br><br>
                    <b>ตอบ: รถจะออกพร้อมกันอีกครั้งเวลา {next_str} น.</b></span>"""



            elif actual_sub_t == "โจทย์ปัญหาคลาสสิก (สมการประยุกต์)":
                # โจทย์หัวขาสัตว์ ยอดฮิตสอบเข้า ม.1
                animals = [("ไก่", 2, "วัว", 4), ("นก", 2, "สุนัข", 4), ("เป็ด", 2, "หมู", 4)]
                a1_name, a1_legs, a2_name, a2_legs = random.choice(animals)
                
                a1_count = random.randint(15, 40)
                a2_count = random.randint(10, 30)
                
                total_heads = a1_count + a2_count
                total_legs = (a1_count * a1_legs) + (a2_count * a2_legs)
                
                q = f"ฟาร์มแห่งหนึ่งมี{a1_name}และ{a2_name}รวมกันอยู่ <b>{total_heads} ตัว</b> ถ้านับขาสัตว์ทั้งสองชนิดรวมกันจะได้ <b>{total_legs} ขา</b><br>จงหาว่าฟาร์มแห่งนี้มี <b>{a2_name}</b> กี่ตัว?"
                
                # วิธีคิดลัดแบบประถม (สมมติให้เป็นสัตว์ขาเตี้ยทั้งหมด)
                assume_legs = total_heads * a1_legs
                diff_legs = total_legs - assume_legs
                leg_diff_per_animal = a2_legs - a1_legs
                ans_a2 = diff_legs // leg_diff_per_animal
                
                sol = f"""<span style='color:#2c3e50;'>
                <div style='background-color:#fcf3cf; border-left:4px solid #f1c40f; padding:10px; margin-bottom:15px; border-radius:4px;'>
                💡 <b>เทคนิคคิดลัด (ไม่ต้องตั้งสมการ X, Y):</b><br>
                ให้ <b>"สมมติว่าเป็นสัตว์ที่มีขาน้อยกว่าทั้งหมด"</b> แล้วดูว่าขาขาดไปเท่าไหร่ ขาที่ขาดไปนั้นคือขาของสัตว์ชนิดที่มีขามากกว่าที่ซ่อนอยู่นั่นเอง!
                </div>
                <b>วิธีทำอย่างละเอียด:</b><br>
                👉 <b>ขั้นที่ 1: สมมติว่าเป็น{a1_name}ทั้งหมด</b><br>
                &nbsp;&nbsp;&nbsp;&nbsp;ถ้ามี{a1_name}ทั้งหมด {total_heads} ตัว จะมีขารวม {total_heads} × {a1_legs} = <b>{assume_legs} ขา</b><br><br>
                👉 <b>ขั้นที่ 2: หาจำนวนขาที่หายไปจากความจริง</b><br>
                &nbsp;&nbsp;&nbsp;&nbsp;แต่ความจริงมี {total_legs} ขา แสดงว่าขาหายไป {total_legs} - {assume_legs} = <b>{diff_legs} ขา</b><br><br>
                👉 <b>ขั้นที่ 3: แลกเปลี่ยนสัตว์เพื่อเพิ่มขา</b><br>
                &nbsp;&nbsp;&nbsp;&nbsp;การเปลี่ยน{a1_name} 1 ตัว เป็น{a2_name} 1 ตัว จะได้ขาเพิ่มขึ้น {a2_legs} - {a1_legs} = <b>{leg_diff_per_animal} ขา</b><br>
                &nbsp;&nbsp;&nbsp;&nbsp;ต้องการขาเพิ่ม {diff_legs} ขา จึงต้องมี{a2_name}ทั้งหมด {diff_legs} ÷ {leg_diff_per_animal} = <b>{ans_a2} ตัว</b><br><br>
                <i>(ตรวจคำตอบ: {a2_name} {ans_a2} ตัว = {ans_a2*a2_legs} ขา, {a1_name} {total_heads-ans_a2} ตัว = {(total_heads-ans_a2)*a1_legs} ขา, รวม = {ans_a2*a2_legs + (total_heads-ans_a2)*a1_legs} ขา ตรงเป๊ะ!)</i><br><br>
                <b>ตอบ: มี{a2_name}ทั้งหมด {ans_a2} ตัว</b></span>"""



            elif actual_sub_t == "แบบรูปและอนุกรม (Number Patterns)":
                pattern_type = random.choice(["arithmetic", "geometric", "quadratic"])
                
                if pattern_type == "arithmetic":
                    start = random.randint(5, 50)
                    diff = random.randint(3, 15)
                    seq = [start + (i * diff) for i in range(5)]
                    q = f"จงหาจำนวนถัดไปของแบบรูปต่อไปนี้: <br><span style='font-size:24px; color:#2980b9; letter-spacing: 2px;'><b>{seq[0]},  {seq[1]},  {seq[2]},  {seq[3]},  {seq[4]},  <span style='color:#e74c3c;'>?</span></b></span>"
                    ans = seq[4] + diff
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b> สังเกตระยะห่างของตัวเลข พบว่าเพิ่มขึ้นทีละ <b>+{diff}</b> เท่าๆ กัน<br>ดังนั้น จำนวนถัดไปคือ {seq[4]} + {diff} = <b>{ans}</b></span>"
                
                elif pattern_type == "geometric":
                    start = random.randint(2, 5)
                    mult = random.choice([2, 3])
                    seq = [start * (mult ** i) for i in range(5)]
                    q = f"จงหาจำนวนถัดไปของแบบรูปต่อไปนี้: <br><span style='font-size:24px; color:#2980b9; letter-spacing: 2px;'><b>{seq[0]},  {seq[1]},  {seq[2]},  {seq[3]},  {seq[4]},  <span style='color:#e74c3c;'>?</span></b></span>"
                    ans = seq[4] * mult
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b> สังเกตระยะห่างของตัวเลข พบว่าเป็นการ <b>คูณด้วย {mult}</b> ต่อเนื่องกันไปเรื่อยๆ ({seq[0]}×{mult}={seq[1]}, {seq[1]}×{mult}={seq[2]}...)<br>ดังนั้น จำนวนถัดไปคือ {seq[4]} × {mult} = <b>{ans}</b></span>"
                
                else: # quadratic (+2, +4, +6...)
                    start = random.randint(2, 10)
                    step_start = random.choice([2, 3])
                    seq = [start]
                    current_step = step_start
                    for _ in range(4):
                        seq.append(seq[-1] + current_step)
                        current_step += step_start # step increases by itself (e.g. +2, +4, +6)
                        
                    q = f"จงหาจำนวนถัดไปของแบบรูปต่อไปนี้: <br><span style='font-size:24px; color:#2980b9; letter-spacing: 2px;'><b>{seq[0]},  {seq[1]},  {seq[2]},  {seq[3]},  {seq[4]},  <span style='color:#e74c3c;'>?</span></b></span>"
                    ans = seq[4] + current_step
                    sol = f"""<span style='color:#2c3e50;'>
                    <div style='background-color:#ebf5fb; border-left:4px solid #3498db; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    💡 <b>เทคนิค: อนุกรมหลายชั้น (ระยะห่างไม่คงที่)</b><br>
                    ให้ลองหา <b>"ส่วนต่าง"</b> ของแต่ละคู่ตัวเลขดูก่อนว่ามีความสัมพันธ์กันอย่างไร
                    </div>
                    <b>วิธีทำ:</b><br>
                    👉 ส่วนต่างของคู่ที่ 1 ({seq[0]} ไป {seq[1]}) คือ <b>+{step_start}</b><br>
                    👉 ส่วนต่างของคู่ที่ 2 ({seq[1]} ไป {seq[2]}) คือ <b>+{step_start*2}</b><br>
                    👉 ส่วนต่างของคู่ที่ 3 ({seq[2]} ไป {seq[3]}) คือ <b>+{step_start*3}</b><br>
                    👉 ส่วนต่างของคู่ที่ 4 ({seq[3]} ไป {seq[4]}) คือ <b>+{step_start*4}</b><br>
                    แสดงว่าส่วนต่างตัวต่อไปจะต้องเป็น <b>+{current_step}</b><br>
                    ดังนั้น จำนวนถัดไปคือ {seq[4]} + {current_step} = <b>{ans}</b></span>"""



            elif actual_sub_t == "มาตราส่วนและทิศทาง":
                scale = random.choice([1000, 50000, 100000, 500000])
                map_dist = round(random.uniform(2.0, 12.5), 1)
                
                # คำนวณระยะทางจริง (ซม. -> กม.)
                real_dist_cm = map_dist * scale
                real_dist_km = real_dist_cm / 100000
                
                scale_str = f"1 : {scale:,}"
                
                q = f"แผนที่ฉบับหนึ่งใช้มาตราส่วน <b>{scale_str}</b> ถ้าวัดระยะทางบนแผนที่จากเมือง A ไปเมือง B ได้ <b>{map_dist} เซนติเมตร</b><br>ระยะทางจริงจากเมือง A ไปเมือง B คิดเป็นกี่<b>กิโลเมตร</b>?"
                
                sol = f"""<span style='color:#2c3e50;'>
                <div style='background-color:#e8f8f5; border-left:4px solid #1abc9c; padding:10px; margin-bottom:15px; border-radius:4px;'>
                💡 <b>ความรู้เรื่องมาตราส่วน:</b><br>
                มาตราส่วน {scale_str} หมายความว่า ระยะทางบนแผนที่ 1 ซม. เท่ากับ ระยะทางจริง {scale:,} ซม.<br>
                <b>(จำไว้ว่า: 100,000 ซม. = 1 กิโลเมตร)</b>
                </div>
                <b>วิธีทำอย่างละเอียด:</b><br>
                👉 <b>ขั้นที่ 1: หาระยะทางจริงในหน่วยเซนติเมตร (ซม.)</b><br>
                &nbsp;&nbsp;&nbsp;&nbsp;บนแผนที่ {map_dist} ซม. นำไปคูณกับมาตราส่วน<br>
                &nbsp;&nbsp;&nbsp;&nbsp;{map_dist} × {scale:,} = <b>{real_dist_cm:,.0f} เซนติเมตร</b><br><br>
                👉 <b>ขั้นที่ 2: แปลงหน่วยจาก เซนติเมตร เป็น กิโลเมตร</b><br>
                &nbsp;&nbsp;&nbsp;&nbsp;เนื่องจาก 1 กม. = 100,000 ซม. จึงต้องนำไป <b>หารด้วย 100,000</b><br>
                &nbsp;&nbsp;&nbsp;&nbsp;{real_dist_cm:,.0f} ÷ 100,000 = <b>{real_dist_km:,.2f} กิโลเมตร</b><br><br>
                <b>ตอบ: ระยะทางจริงคือ {real_dist_km:,.2f} กิโลเมตร</b></span>"""



            elif actual_sub_t == "เรขาคณิตประยุกต์ (หาพื้นที่แรเงา)":
                scenario = random.choice(["frame", "cross_path", "triangle_in_rect"])
                
                if scenario == "frame":
                    w_out = random.randint(20, 40)
                    l_out = random.randint(w_out + 5, 50)
                    border = random.choice([2, 3, 4, 5])
                    
                    w_in = w_out - (2 * border)
                    l_in = l_out - (2 * border)
                    
                    area_out = w_out * l_out
                    area_in = w_in * l_in
                    shaded_area = area_out - area_in
                    
                    svg = draw_shaded_svg("frame", l_out, w_out, border)
                    
                    q = f"จากรูป กรอบรูปสี่เหลี่ยมผืนผ้ามีขนาดภายนอกกว้าง {w_out} ม. ยาว {l_out} ม. มีความกว้างของขอบรอบด้านเท่ากันคือ {border} ม. <br>จงหา <b>พื้นที่ของขอบกรอบรูป (ส่วนที่ระบายสีเทา)</b><br>{svg}"
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    <div style='background-color:#fcf3cf; border-left:4px solid #f1c40f; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    💡 <b>เทคนิคหาพื้นที่แรเงาแบบกรอบ/โดนเจาะ:</b><br>
                    <b>พื้นที่แรเงา = พื้นที่รูปใหญ่ (ด้านนอก) - พื้นที่รูปเล็ก (ด้านใน)</b>
                    </div>
                    <b>วิธีทำอย่างละเอียด:</b><br>
                    👉 <b>ขั้นที่ 1: หาพื้นที่สี่เหลี่ยมรูปใหญ่ (ด้านนอก)</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;กว้าง {w_out} ม. × ยาว {l_out} ม. = <b>{area_out} ตร.ม.</b><br><br>
                    👉 <b>ขั้นที่ 2: หาความยาวด้านของรูปสี่เหลี่ยมเล็ก (ด้านใน)</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;<i>ระวัง! ขอบกินพื้นที่ 2 ฝั่ง (ซ้าย-ขวา / บน-ล่าง) ต้องหักออกฝั่งละ {border} ม.</i><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;กว้างด้านใน = {w_out} - {border} - {border} = <b>{w_in} ม.</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;ยาวด้านใน = {l_out} - {border} - {border} = <b>{l_in} ม.</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;พื้นที่รูปเล็ก = {w_in} × {l_in} = <b>{area_in} ตร.ม.</b><br><br>
                    👉 <b>ขั้นที่ 3: จับมาลบกัน</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;พื้นที่แรเงา = {area_out} - {area_in} = <b>{shaded_area} ตร.ม.</b><br><br>
                    <b>ตอบ: พื้นที่ขอบกรอบรูปคือ {shaded_area} ตารางเมตร</b></span>"""
                    
                elif scenario == "cross_path":
                    w = random.randint(20, 50)
                    l = random.randint(w + 5, 80)
                    path = random.choice([2, 3, 4, 5])
                    
                    area_path_h = l * path
                    area_path_v = w * path
                    area_intersect = path * path
                    shaded_area = area_path_h + area_path_v - area_intersect
                    
                    svg = draw_shaded_svg("cross_path", l, w, path)
                    
                    q = f"ลานจอดรถรูปสี่เหลี่ยมผืนผ้ากว้าง {w} ม. ยาว {l} ม. มีการทำทางเดินกากบาทตัดกันตรงกลางซึ่งมีความกว้าง {path} ม. <br>จงหา <b>พื้นที่ของทางเดินทั้งหมด (ส่วนที่ระบายสีเทา)</b><br>{svg}"
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    <div style='background-color:#fcf3cf; border-left:4px solid #f1c40f; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    💡 <b>เทคนิคหาพื้นที่ทางเดินตัดกัน:</b><br>
                    นำพื้นที่ทางเดินแนวนอน + ทางเดินแนวตั้ง <b>แต่ต้องหัก "พื้นที่สี่เหลี่ยมจัตุรัสตรงกลางที่ซ้อนทับกันออก 1 ครั้ง" ด้วย!</b> (เพราะเราบวกซ้ำไป 2 รอบ)
                    </div>
                    <b>วิธีทำอย่างละเอียด:</b><br>
                    👉 <b>ขั้นที่ 1: หาพื้นที่ทางเดินแนวนอน</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;ยาว {l} ม. × กว้าง {path} ม. = <b>{area_path_h} ตร.ม.</b><br><br>
                    👉 <b>ขั้นที่ 2: หาพื้นที่ทางเดินแนวตั้ง</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;ยาว {w} ม. × กว้าง {path} ม. = <b>{area_path_v} ตร.ม.</b><br><br>
                    👉 <b>ขั้นที่ 3: หักพื้นที่ตรงกลางที่ซ้อนทับกัน</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;ทางตัดกันเป็นสี่เหลี่ยมจัตุรัสขนาด {path} × {path} = <b>{area_intersect} ตร.ม.</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;พื้นที่ทางเดินรวม = {area_path_h} + {area_path_v} - {area_intersect} = <b>{shaded_area} ตร.ม.</b><br><br>
                    <b>ตอบ: พื้นที่ทางเดินทั้งหมดคือ {shaded_area} ตารางเมตร</b></span>"""
                    
                else: # triangle_in_rect
                    w = random.randint(10, 30)
                    l = random.randint(w + 5, 40)
                    rect_area = w * l
                    tri_area = (l * w) // 2
                    
                    svg = draw_shaded_svg("triangle_in_rect", l, w)
                    
                    q = f"กระดาษรูปสี่เหลี่ยมผืนผ้ากว้าง {w} นิ้ว ยาว {l} นิ้ว ถูกตัดเป็นรูปสามเหลี่ยมดังภาพ (ส่วนที่ระบายสีขาว) จงหาว่า<b>พื้นที่ส่วนที่เหลือ (สีเทา)</b> มีขนาดกี่ตารางนิ้ว?<br>{svg}"
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    <div style='background-color:#e8f8f5; border-left:4px solid #1abc9c; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    💡 <b>เทคนิคลับเรขาคณิต:</b><br>
                    ถ้าเรามีรูปสามเหลี่ยมที่วาดแนบพอดีกึ่งกลางสี่เหลี่ยมมุมฉากแบบนี้ <b>พื้นที่ของสามเหลี่ยมจะเท่ากับ "ครึ่งหนึ่ง" ของพื้นที่สี่เหลี่ยมเสมอ!</b> แสดงว่าพื้นที่ส่วนที่เหลือ (สีเทา) ก็จะเท่ากับอีกครึ่งหนึ่งพอดี
                    </div>
                    <b>วิธีทำอย่างละเอียด:</b><br>
                    👉 <b>ขั้นที่ 1: หาพื้นที่สี่เหลี่ยมผืนผ้าทั้งหมด</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;กว้าง {w} นิ้ว × ยาว {l} นิ้ว = <b>{rect_area} ตร.นิ้ว</b><br><br>
                    👉 <b>ขั้นที่ 2: แบ่งครึ่งพื้นที่</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;พื้นที่สีเทา = ครึ่งหนึ่งของสี่เหลี่ยม ➔ {rect_area} ÷ 2 = <b>{tri_area} ตร.นิ้ว</b><br><br>
                    <b>ตอบ: พื้นที่ส่วนที่เหลือ (สีเทา) คือ {tri_area} ตารางนิ้ว</b></span>"""

else:
                q = f"⚠️ [ระบบอยู่ระหว่างการอัปเดต] ไม่พบเงื่อนไขการสร้างโจทย์สำหรับหัวข้อ: <b>{actual_sub_t}</b>"
                sol = "กรุณาเลือกหัวข้ออื่น"

            # ==================================================
            # ระบบเช็คโจทย์ซ้ำ (ยันต์กันค้าง)
            # ==================================================
            if q not in seen: 
                seen.add(q)
                questions.append({"question": q, "solution": sol})
                break 
            elif attempts >= 299:
                questions.append({"question": q, "solution": sol})
                break
                
            attempts += 1  
            
    return questions

# ==========================================
# UI Rendering & Streamlit
# ==========================================
def extract_body(html_str):
    try: return html_str.split('<body>')[1].split('</body>')[0]
    except IndexError: return html_str

def create_page(grade, sub_t, questions, is_key=False, q_margin="20px", ws_height="180px", brand_name=""):
    title = "เฉลยแบบฝึกหัด (Answer Key)" if is_key else "แบบฝึกหัดคณิตศาสตร์"
    student_info = """
        <table style="width: 100%; margin-bottom: 10px; font-size: 18px; border-collapse: collapse;">
            <tr>
                <td style="width: 1%; white-space: nowrap; padding-right: 5px;"><b>ชื่อ-สกุล</b></td>
                <td style="border-bottom: 2px dotted #999; width: 60%;"></td>
                <td style="width: 1%; white-space: nowrap; padding-left: 20px; padding-right: 5px;"><b>ชั้น</b></td>
                <td style="border-bottom: 2px dotted #999; width: 15%;"></td>
                <td style="width: 1%; white-space: nowrap; padding-left: 20px; padding-right: 5px;"><b>เลขที่</b></td>
                <td style="border-bottom: 2px dotted #999; width: 15%;"></td>
            </tr>
        </table>
        """ if not is_key else ""
        
    html = f"""<!DOCTYPE html><html lang="th"><head><meta charset="utf-8">
    <style>
        @page {{ size: A4; margin: 15mm; }}
        body {{ font-family: 'Sarabun', sans-serif; padding: 20px; line-height: 1.6; color: #333; }}
        .header {{ text-align: center; border-bottom: 2px solid #333; margin-bottom: 10px; padding-bottom: 10px; }}
        .q-box {{ margin-bottom: {q_margin}; padding: 10px 15px; page-break-inside: avoid; font-size: 20px; line-height: 1.6; }}
        .workspace {{ height: {ws_height}; border: 2px dashed #bdc3c7; border-radius: 8px; margin: 15px 0; padding: 10px; color: #95a5a6; font-size: 16px; background-color: #fafbfc; }}
        .ans-line {{ margin-top: 10px; border-bottom: 1px dotted #999; width: 80%; height: 30px; font-weight: bold; font-size: 20px; display: flex; align-items: flex-end; padding-bottom: 5px; }}
        .sol-text {{ color: #333; font-size: 18px; display: block; margin-top: 15px; padding: 15px; background-color: #f1f8ff; border-left: 4px solid #3498db; border-radius: 4px; line-height: 1.6; }}
        .page-footer {{ text-align: right; font-size: 14px; color: #95a5a6; margin-top: 20px; border-top: 1px solid #eee; padding-top: 10px; }}
    </style></head><body>
    <div class="header"><h2>{title} - {grade}</h2><p><b>หมวดหมู่:</b> {sub_t}</p></div>
    {student_info}"""
    
    for i, item in enumerate(questions, 1):
        html += f'<div class="q-box"><b>ข้อที่ {i}.</b> '
        
        # 💡 ปรับเงื่อนไขซ่อนพื้นที่ทดเลข ให้ครอบคลุมเนื้อหา ป.5
        hide_ws = False
        if any(keyword in sub_t for keyword in ["(แบบตั้งหลัก)", "หารยาว", "การคูณและการหารทศนิยม", "การบวกและการลบทศนิยม"]):
            hide_ws = True
        elif any(keyword in item["question"] for keyword in ["จงหาผลบวกของ", "จงหาผลลบของ", "จงหาผลคูณของ", "วิธีหารยาว", "ตั้งทด"]):
            hide_ws = True
            
        if is_key:
            if hide_ws: 
                html += f'{item["solution"]}'
            else: 
                html += f'{item["question"]}<div class="sol-text">{item["solution"]}</div>'
        else:
            if hide_ws:
                html += f'{item["question"]}<div class="ans-line">ตอบ: </div>'
            else:
                html += f'{item["question"]}<div class="workspace">พื้นที่สำหรับแสดงวิธีทำอย่างละเอียด...</div><div class="ans-line">ตอบ: </div>'
        html += '</div>'
        
    if brand_name: 
        html += f'<div class="page-footer">&copy; 2026 {brand_name} | สงวนลิขสิทธิ์</div>'
        
    return html + "</body></html>"

# ==========================================
# 4. Streamlit UI (Sidebar & Result Grouping)
# ==========================================
st.sidebar.markdown("## ⚙️ พารามิเตอร์การสร้าง")

# 📚 บังคับเลือกเป็น ป.5
selected_grade = st.sidebar.selectbox("📚 เลือกระดับชั้น:", ["ป.5", "ป.5 (สอบแข่งขัน/สอบเข้า)"])

# ปรับดึง Key จาก curriculum_db ตามตัวเลือก
if selected_grade == "ป.5":
    main_topics_list = list(curriculum_db["ป.5"].keys())
else:
    main_topics_list = list(curriculum_db["ป.5"].keys()) # ถ้ารวมอยู่ใน dict เดียวกันหมด

main_topics_list.append("🌟 โหมดพิเศษ (สุ่มทุกเรื่อง)")

selected_main = st.sidebar.selectbox("📂 เลือกหัวข้อหลัก:", main_topics_list)

if selected_main == "🌟 โหมดพิเศษ (สุ่มทุกเรื่อง)":
    selected_sub = "แบบทดสอบรวมปลายภาค"
    st.sidebar.info("💡 โหมดนี้จะสุ่มดึงโจทย์จากทุกเรื่องในชั้นเรียนนี้มายำรวมกัน")
else:
    selected_sub = st.sidebar.selectbox("📝 เลือกหัวข้อย่อย:", curriculum_db["ป.5"][selected_main])

num_input = st.sidebar.number_input("🔢 จำนวนข้อ:", min_value=1, max_value=100, value=10)

st.sidebar.markdown("---")
is_challenge = st.sidebar.toggle("🔥 โหมดชาเลนจ์ (ท้าทาย)", value=False)
if is_challenge:
    st.sidebar.warning("เปิดโหมดชาเลนจ์แล้ว! ตัวเลขจะยากขึ้นและโจทย์จะท้าทายกว่าเดิม")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📏 ตั้งค่าหน้ากระดาษ")
spacing_level = st.sidebar.select_slider(
    "↕️ ความสูงของพื้นที่ทดเลข:", 
    options=["แคบ", "ปานกลาง", "กว้าง", "กว้างพิเศษ"], 
    value="กว้าง" # ป.5 ปกติใช้พื้นที่ทดเยอะ ปรับ default เป็นกว้าง
)

if spacing_level == "แคบ": q_margin, ws_height = "15px", "100px"
elif spacing_level == "ปานกลาง": q_margin, ws_height = "20px", "180px"
elif spacing_level == "กว้าง": q_margin, ws_height = "30px", "280px"
else: q_margin, ws_height = "40px", "400px"

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎨 ตั้งค่าแบรนด์")
brand_name = st.sidebar.text_input("🏷️ ชื่อแบรนด์ / ผู้สอน:", value="บ้านทีเด็ด")

# เปลี่ยนสีปุ่มให้เข้ากับธีม ป.5 (แดง/ส้ม)
if st.sidebar.button("🚀 สั่งสร้างใบงาน ป.5", type="primary", use_container_width=True):
    with st.spinner("กำลังออกแบบรูปภาพและสร้างเฉลยแบบ Step-by-Step..."):
        
        qs = generate_questions_logic("ป.5", selected_main, selected_sub, num_input, is_challenge)
        
        html_w = create_page("ป.5", selected_sub, qs, is_key=False, q_margin=q_margin, ws_height=ws_height, brand_name=brand_name)
        html_k = create_page("ป.5", selected_sub, qs, is_key=True, q_margin=q_margin, ws_height=ws_height, brand_name=brand_name)
        
        st.session_state['worksheet_html'] = html_w
        st.session_state['answerkey_html'] = html_k
        
        ebook_body = f'\n<div class="a4-wrapper">{extract_body(html_w)}</div>\n<div class="a4-wrapper">{extract_body(html_k)}</div>\n'
        
        full_ebook_html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap" rel="stylesheet"><style>@page {{ size: A4; margin: 15mm; }} @media screen {{ body {{ font-family: 'Sarabun', sans-serif; background-color: #525659; display: flex; flex-direction: column; align-items: center; padding: 40px 0; margin: 0; }} .a4-wrapper {{ width: 210mm; min-height: 297mm; background: white; margin-bottom: 30px; box-shadow: 0 10px 20px rgba(0,0,0,0.3); padding: 15mm; box-sizing: border-box; }} }} @media print {{ body {{ font-family: 'Sarabun', sans-serif; background: transparent; padding: 0; display: block; margin: 0; }} .a4-wrapper {{ width: 100%; min-height: auto; margin: 0; padding: 0; box-shadow: none; page-break-after: always; }} }} .header {{ text-align: center; border-bottom: 2px solid #333; margin-bottom: 10px; padding-bottom: 10px; }} .q-box {{ margin-bottom: {q_margin}; padding: 10px 15px; page-break-inside: avoid; font-size: 20px; line-height: 1.6; }} .workspace {{ height: {ws_height}; border: 2px dashed #bdc3c7; border-radius: 8px; margin: 15px 0; padding: 10px; color: #95a5a6; font-size: 16px; background-color: #fafbfc; }} .ans-line {{ margin-top: 10px; border-bottom: 1px dotted #999; width: 80%; height: 30px; font-weight: bold; font-size: 20px; display: flex; align-items: flex-end; padding-bottom: 5px; }} .sol-text {{ color: #333; font-size: 18px; display: block; margin-top: 15px; padding: 15px; background-color: #f1f8ff; border-left: 4px solid #3498db; border-radius: 4px; line-height: 1.6; }} .page-footer {{ text-align: right; font-size: 14px; color: #95a5a6; margin-top: 20px; border-top: 1px solid #eee; padding-top: 10px; }} </style></head><body>{ebook_body}</body></html>"""

        filename_base = f"BaanTded_P5_Gifted_{int(time.time())}"
        st.session_state['ebook_html'] = full_ebook_html
        st.session_state['filename_base'] = filename_base
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(f"{filename_base}_Full_EBook.html", full_ebook_html.encode('utf-8'))
            zip_file.writestr(f"{filename_base}_Worksheet.html", html_w.encode('utf-8'))
            zip_file.writestr(f"{filename_base}_AnswerKey.html", html_k.encode('utf-8'))
        st.session_state['zip_data'] = zip_buffer.getvalue()

if 'ebook_html' in st.session_state:
    st.success(f"✅ สร้างใบงานสำเร็จ! ลิขสิทธิ์โดย {brand_name}")
    c1, c2 = st.columns(2)
    with c1:
        st.download_button("📄 โหลดเฉพาะโจทย์", data=st.session_state['worksheet_html'], file_name=f"{st.session_state['filename_base']}_Worksheet.html", mime="text/html", use_container_width=True)
        st.download_button("🔑 โหลดเฉพาะเฉลย", data=st.session_state['answerkey_html'], file_name=f"{st.session_state['filename_base']}_AnswerKey.html", mime="text/html", use_container_width=True)
    with c2:
        st.download_button("📚 โหลดรวมเล่ม E-Book", data=st.session_state['ebook_html'], file_name=f"{st.session_state['filename_base']}_Full_EBook.html", mime="text/html", use_container_width=True)
        st.download_button("🗂️ โหลดแพ็กเกจ (.zip)", data=st.session_state['zip_data'], file_name=f"{st.session_state['filename_base']}.zip", mime="application/zip", use_container_width=True)
    st.markdown("---")
    components.html(st.session_state['ebook_html'], height=800, scrolling=True)
