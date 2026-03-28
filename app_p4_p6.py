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
# ตั้งค่าหน้าเพจ Web App & Professional CSS
# ==========================================
st.set_page_config(page_title="Math Generator - Primary 4-5", page_icon="🎓", layout="wide")

st.markdown("""
<style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1200px; }
    div[data-testid="stSidebar"] div.stButton > button { background-color: #27ae60; color: white; border-radius: 8px; height: 3.5rem; font-size: 18px; font-weight: bold; border: none; box-shadow: 0 4px 6px rgba(39,174,96,0.3); }
    div[data-testid="stSidebar"] div.stButton > button:hover { background-color: #219653; box-shadow: 0 6px 12px rgba(39,174,96,0.4); }
    .main-header { background: linear-gradient(135deg, #8e44ad, #2980b9); padding: 2rem; border-radius: 15px; color: white; margin-bottom: 2rem; box-shadow: 0 10px 20px rgba(0,0,0,0.15); }
    .main-header h1 { margin: 0; font-size: 2.8rem; font-weight: 800; text-shadow: 2px 2px 4px rgba(0,0,0,0.2); }
    .main-header p { margin: 10px 0 0 0; font-size: 1.2rem; opacity: 0.9; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>🎓 Math Worksheet Pro <span style="font-size: 20px; background: #e74c3c; color: #fff; padding: 5px 15px; border-radius: 20px; vertical-align: middle;">ประถมปลาย ป.4 - ป.5</span></h1>
    <p>ระบบสร้างโจทย์คณิตศาสตร์และสมการ (ฉบับปรับปรุงเฉพาะ ป.4-ป.5)</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 1. คลังคำศัพท์และฟังก์ชันตัวช่วย (Helpers)
# ==========================================
NAMES = ["อคิณ", "นาวิน", "ภูผา", "สายฟ้า", "เจ้านาย", "ข้าวหอม", "ใบบัว", "มะลิ", "น้ำใส", "ญาญ่า", "ปลื้ม", "พายุ"]
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


# ==========================================
# ส่วนของ Helpers (ฟังก์ชันวาดรูป SVG)
# ==========================================


import math
import random

def draw_p4_kite_svg(sides, unit="ซม."):
    svg_w, svg_h = 450, 250
    cx, cy = 225, 125
    svg = f'<svg width="{svg_w}" height="{svg_h}">'
    
    # 📐 ไดนามิก: สุ่มสัดส่วนของรูปว่าวให้แต่ละข้อดูไม่ซ้ำกัน
    half_w = random.randint(60, 100)   # ครึ่งความกว้าง (สุ่มความอ้วน/ผอม)
    top_h = random.randint(30, 55)     # ความสูงส่วนบน (คู่สั้น)
    bottom_h = random.randint(70, 110) # ความสูงส่วนล่าง (คู่ยาว)
    
    # พิกัด 4 มุม (บน, ขวา, ล่าง, ซ้าย) ขยับพิกัด Y ขึ้นนิดหน่อยให้อยู่กึ่งกลางกรอบ
    offset_y = 10
    top = (cx, cy - top_h - offset_y)
    right = (cx + half_w, cy - offset_y)
    bottom = (cx, cy + bottom_h - offset_y)
    left = (cx - half_w, cy - offset_y)
    
    pts = f"{top[0]},{top[1]} {right[0]},{right[1]} {bottom[0]},{bottom[1]} {left[0]},{left[1]}"
    
    # วาดตัวรูป
    svg += f'<polygon points="{pts}" fill="#fcfcfc" stroke="#2c3e50" stroke-width="2.5"/>'
    
    # ฟังก์ชันช่วยคำนวณองศาให้เส้น "ตั้งฉาก" กับด้านเอียงแบบ 100%
    def get_tick_angle(p1, p2):
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        return math.degrees(math.atan2(dy, dx)) + 90

    # 🎯 สัญลักษณ์ 1 ขีด สำหรับคู่ประชิดด้านบน (ด้านสั้น)
    for p1, p2 in [(left, top), (top, right)]:
        mx, my = (p1[0]+p2[0])/2, (p1[1]+p2[1])/2
        angle = get_tick_angle(p1, p2)
        svg += f'<line x1="{mx}" y1="{my-7}" x2="{mx}" y2="{my+7}" stroke="#3498db" stroke-width="2.5" stroke-linecap="round" transform="rotate({angle}, {mx}, {my})"/>'
        
    # 🎯 สัญลักษณ์ 2 ขีด สำหรับคู่ประชิดด้านล่าง (ด้านยาว)
    for p1, p2 in [(left, bottom), (right, bottom)]:
        mx, my = (p1[0]+p2[0])/2, (p1[1]+p2[1])/2
        angle = get_tick_angle(p1, p2)
        svg += f'<line x1="{mx-3}" y1="{my-7}" x2="{mx-3}" y2="{my+7}" stroke="#e74c3c" stroke-width="2.5" stroke-linecap="round" transform="rotate({angle}, {mx}, {my})"/>'
        svg += f'<line x1="{mx+3}" y1="{my-7}" x2="{mx+3}" y2="{my+7}" stroke="#e74c3c" stroke-width="2.5" stroke-linecap="round" transform="rotate({angle}, {mx}, {my})"/>'

    # 🎯 วางตัวเลขให้เยื้องออกจากเส้นเอียง ไม่ให้ทับซ้อนกัน
    # ตัวเลขด้านบนขวา
    mid_tr_x, mid_tr_y = (top[0]+right[0])/2, (top[1]+right[1])/2
    svg += f'<text x="{mid_tr_x + 15}" y="{mid_tr_y - 10}" font-family="Sarabun" font-size="18" font-weight="bold" text-anchor="start" fill="#2980b9">{sides[0]} {unit}</text>'
    
    # ตัวเลขด้านล่างขวา
    mid_br_x, mid_br_y = (right[0]+bottom[0])/2, (right[1]+bottom[1])/2
    svg += f'<text x="{mid_br_x + 15}" y="{mid_br_y + 15}" font-family="Sarabun" font-size="18" font-weight="bold" text-anchor="start" fill="#2980b9">{sides[1]} {unit}</text>'

    svg += '</svg>'
    return f'''<div style="display:flex; justify-content:center; margin: 20px 0;">
        <div style="border: 1px solid #bdc3c7; border-radius: 12px; padding: 25px; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            {svg}
        </div></div>'''




def draw_p4_parallelogram_rhombus_svg(shape_type, sides, unit="วา"):
    svg_w, svg_h = 450, 250
    cx, cy = 225, 125
    svg = f'<svg width="{svg_w}" height="{svg_h}">'
    
    if shape_type == "rhombus":
        # 📐 สี่เหลี่ยมขนมเปียกปูน: ปรับสูตรคำนวณพิกัดใหม่ให้ด้านทั้ง 4 ยาว 120 pixels เท่ากันเป๊ะ!
        tl, tr = (cx - 30, cy - 52), (cx + 90, cy - 52)
        bl, br = (cx - 90, cy + 52), (cx + 30, cy + 52)
        
        pts = f"{tl[0]},{tl[1]} {tr[0]},{tr[1]} {br[0]},{br[1]} {bl[0]},{bl[1]}"
        svg += f'<polygon points="{pts}" fill="#fcfcfc" stroke="#2c3e50" stroke-width="2.5"/>'
        
        # 🎯 ขีด 1 ขีดทุกด้านให้ "ตั้งฉาก" กับเส้นขอบพอดี
        # ด้านบน-ล่างเป็นแนวนอน (0 องศา) / ด้านข้างเอียง (-60 องศา)
        sides_to_tick = [(tl, tr, 0), (tr, br, -60), (br, bl, 0), (bl, tl, -60)]
        for p1, p2, angle in sides_to_tick:
            mx, my = (p1[0]+p2[0])/2, (p1[1]+p2[1])/2
            svg += f'<line x1="{mx}" y1="{my-8}" x2="{mx}" y2="{my+8}" stroke="#e74c3c" stroke-width="2.5" stroke-linecap="round" transform="rotate({angle}, {mx}, {my})"/>'
        
        # วางตัวเลขให้ตรงกึ่งกลางของฐานด้านล่างพอดีเป๊ะ
        svg += f'<text x="{cx - 30}" y="{cy + 85}" font-family="Sarabun" font-size="18" font-weight="bold" text-anchor="middle" fill="#2980b9">{sides[0]} {unit}</text>'

    else: 
        # 📐 สี่เหลี่ยมด้านขนาน: ฐานยาว 160 pixels, ด้านเอียงยาว 90 pixels
        tl, tr = (cx - 57.5, cy - 39), (cx + 102.5, cy - 39)
        bl, br = (cx - 102.5, cy + 39), (cx + 57.5, cy + 39)
        
        pts = f"{tl[0]},{tl[1]} {tr[0]},{tr[1]} {br[0]},{br[1]} {bl[0]},{bl[1]}"
        svg += f'<polygon points="{pts}" fill="#fcfcfc" stroke="#2c3e50" stroke-width="2.5"/>'
        
        # คู่บน-ล่าง (แนวนอน, 2 ขีด)
        for p1, p2 in [(tl, tr), (br, bl)]:
            mx, my = (p1[0]+p2[0])/2, (p1[1]+p2[1])/2
            svg += f'<line x1="{mx-3}" y1="{my-8}" x2="{mx-3}" y2="{my+8}" stroke="#e74c3c" stroke-width="2.5" stroke-linecap="round"/>'
            svg += f'<line x1="{mx+3}" y1="{my-8}" x2="{mx+3}" y2="{my+8}" stroke="#e74c3c" stroke-width="2.5" stroke-linecap="round"/>'
        
        # คู่ซ้าย-ขวา (เอียง, 1 ขีด) ปรับมุมขีดให้ตั้งฉากกับเส้นเอียง (-60 องศา)
        for p1, p2 in [(tr, br), (bl, tl)]:
            mx, my = (p1[0]+p2[0])/2, (p1[1]+p2[1])/2
            svg += f'<line x1="{mx}" y1="{my-8}" x2="{mx}" y2="{my+8}" stroke="#3498db" stroke-width="2.5" stroke-linecap="round" transform="rotate(-60, {mx}, {my})"/>'

        # 🎯 ขยับตัวเลขให้อ่านง่าย: ตัวเลขด้านล่างอยู่กึ่งกลางฐาน / ตัวเลขด้านข้างขยับออกไปพ้นแนวเส้น
        svg += f'<text x="{cx - 22.5}" y="{cy + 75}" font-family="Sarabun" font-size="18" font-weight="bold" text-anchor="middle" fill="#2980b9">{sides[0]} {unit}</text>'
        svg += f'<text x="{cx + 100}" y="{cy + 5}" font-family="Sarabun" font-size="18" font-weight="bold" text-anchor="start" fill="#2980b9">{sides[1]} {unit}</text>'

    svg += '</svg>'
    return f'''<div style="display:flex; justify-content:center; margin: 20px 0;">
        <div style="border: 1px solid #bdc3c7; border-radius: 12px; padding: 25px; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            {svg}
        </div></div>'''


def draw_angle_svg(angle_type, degree):
    # ... โค้ดเดิมของคุณ ...
    pass

def draw_p4_triangle_perimeter_svg(triangle_type, sides, unit="ซม."):
    # --- วางฟังก์ชันใหม่ตรงนี้ ---
    svg_w, svg_h = 450, 250
    # ... (โค้ดที่ผมให้ไปด้านบน) ...
    return f'''<div style="...">...</div>'''

def draw_grid_counting_svg(grid_data):
    # ... ฟังก์ชันอื่นๆ ...
    pass




import math # อย่าลืม import math ที่บรรทัดบนสุดของไฟล์นะครับ!

def draw_p4_triangle_perimeter_svg(triangle_type, sides, unit="ซม."):
    svg_w, svg_h = 450, 250
    cx, cy = 225, 125 
    svg = f'<svg width="{svg_w}" height="{svg_h}">'
    
    if triangle_type == "right_angled":
        # 📐 สามเหลี่ยมมุมฉาก (จัดกึ่งกลางสมมาตร)
        # มุมฉากอยู่ที่ (160, 190), ยอดอยู่ที่ (160, 70), ปลายฐานอยู่ที่ (300, 190)
        p_right, p_top, p_base = (160, 190), (160, 70), (300, 190)
        pts = f"{p_right[0]},{p_right[1]} {p_top[0]},{p_top[1]} {p_base[0]},{p_base[1]}"
        svg += f'<polygon points="{pts}" fill="#fcfcfc" stroke="#2c3e50" stroke-width="2.5"/>'
        # วาดสัญลักษณ์มุมฉาก
        s = 15
        svg += f'<polyline points="{p_right[0]},{p_right[1]-s} {p_right[0]+s},{p_right[1]-s} {p_right[0]+s},{p_right[1]}" fill="none" stroke="#2c3e50" stroke-width="1.5"/>'
        # ตัวเลขกำกับ 3 ด้าน
        svg += f'<text x="150" y="130" font-family="Sarabun" font-size="18" font-weight="bold" text-anchor="end" fill="#2980b9">{sides[0]} {unit}</text>' # ด้านสูง
        svg += f'<text x="230" y="215" font-family="Sarabun" font-size="18" font-weight="bold" text-anchor="middle" fill="#2980b9">{sides[1]} {unit}</text>' # ฐาน
        svg += f'<text x="245" y="120" font-family="Sarabun" font-size="18" font-weight="bold" text-anchor="start" fill="#2980b9">{sides[2]} {unit}</text>' # ด้านเอียง
    else:
        # --- สามเหลี่ยมแบบเดิม (หน้าจั่ว/ด้านเท่า/ด้านไม่เท่า) ---
        t, l, r = (cx, cy - 80), (cx - 100, cy + 70), (cx + 100, cy + 70)
        pts = f"{t[0]},{t[1]} {l[0]},{l[1]} {r[0]},{r[1]}"
        svg += f'<polygon points="{pts}" fill="#fcfcfc" stroke="#2c3e50" stroke-width="2.5"/>'

        if triangle_type == "equilateral":
            lines_data = [(t, l, -60), (t, r, 60), (l, r, 0)]
            for p1, p2, angle in lines_data:
                mx, my = (p1[0]+p2[0])/2, (p1[1]+p2[1])/2
                svg += f'<line x1="{mx}" y1="{my-6}" x2="{mx}" y2="{my+6}" stroke="#e74c3c" stroke-width="2" stroke-linecap="round" transform="rotate({angle}, {mx}, {my})"/>'
            svg += f'<text x="{cx}" y="{cy + 100}" font-family="Sarabun" font-size="18" font-weight="bold" text-anchor="middle" fill="#2980b9">{sides[0]} {unit}</text>'
        elif triangle_type == "isosceles":
            lines_data = [(t, l, -60), (t, r, 60)]
            for p1, p2, angle in lines_data:
                mx, my = (p1[0]+p2[0])/2, (p1[1]+p2[1])/2
                svg += f'<line x1="{mx}" y1="{my-6}" x2="{mx}" y2="{my+6}" stroke="#e74c3c" stroke-width="2" stroke-linecap="round" transform="rotate({angle}, {mx}, {my})"/>'
            svg += f'<text x="{cx}" y="{cy + 100}" font-family="Sarabun" font-size="18" font-weight="bold" text-anchor="middle" fill="#2980b9">{sides[0]} {unit}</text>'
            svg += f'<text x="{cx - 105}" y="{cy + 25}" font-family="Sarabun" font-size="18" font-weight="bold" text-anchor="end" fill="#2980b9">{sides[1]} {unit}</text>'
        else: # scalene
            svg += f'<text x="{cx}" y="{cy + 100}" font-family="Sarabun" font-size="18" font-weight="bold" text-anchor="middle" fill="#2980b9">{sides[0]} {unit}</text>'
            svg += f'<text x="{cx - 105}" y="{cy + 25}" font-family="Sarabun" font-size="18" font-weight="bold" text-anchor="end" fill="#2980b9">{sides[1]} {unit}</text>'
            svg += f'<text x="{cx + 105}" y="{cy + 25}" font-family="Sarabun" font-size="18" font-weight="bold" text-anchor="start" fill="#2980b9">{sides[2]} {unit}</text>'

    svg += '</svg>'
    return f'''<div style="display:flex; justify-content:center; margin: 20px 0;">
        <div style="border: 1px solid #bdc3c7; border-radius: 12px; padding: 25px; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            {svg}
        </div></div>'''




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

def generate_long_division_step_by_step_html(divisor, dividend, equation_html, is_key=False):
    div_str = str(dividend)
    div_len = len(div_str)
    if not is_key:
        ans_tds_list = [f'<td style="width: 35px; height: 45px;"></td>' for _ in div_str] + ['<td style="width: 35px;"></td>']
        div_tds_list = []
        for i, c in enumerate(div_str):
            left_border = "border-left: 3px solid #000;" if i == 0 else ""
            div_tds_list.append(f'<td style="width: 35px; text-align: center; border-top: 3px solid #000; {left_border} font-size: 38px; height: 50px; vertical-align: bottom;">{c}</td>')
        div_tds_list.append('<td style="width: 35px;"></td>')
        empty_rows = ""
        for _ in range(div_len + 1): 
            empty_rows += f"<tr><td style='border: none;'></td>"
            for _ in range(div_len + 1): empty_rows += f"<td style='width: 35px; height: 45px;'></td>"
            empty_rows += "</tr>"
        return f"{equation_html}<div style=\"display: block; margin-left: 60px; margin-top: 15px; margin-bottom: 15px;\"><div style=\"display: inline-block; font-family: 'Sarabun', sans-serif; line-height: 1.2;\"><table style=\"border-collapse: collapse;\"><tr><td style=\"border: none;\"></td>{''.join(ans_tds_list)}</tr><tr><td style=\"border: none; text-align: right; padding-right: 12px; vertical-align: bottom; font-size: 38px;\">{divisor}</td>{''.join(div_tds_list)}</tr>{empty_rows}</table></div></div>"
    
    steps, current_val_str, ans_str, has_started = [], "", "", False
    for i, digit in enumerate(div_str):
        current_val_str += digit
        current_val = int(current_val_str)
        q = current_val // divisor
        mul_res = q * divisor
        rem = current_val - mul_res
        if not has_started and q == 0 and i < len(div_str) - 1:
             current_val_str = str(rem) if rem != 0 else ""
             continue
        has_started = True
        ans_str += str(q)
        steps.append({'mul_res': mul_res, 'rem': rem, 'col_index': i})
        current_val_str = str(rem) if rem != 0 else ""
        
    ans_padded = ans_str.rjust(div_len, " ")
    ans_tds_list = [f'<td style="width: 35px; text-align: center; color: red; font-weight: bold; font-size: 38px;">{c.strip()}</td>' for c in ans_padded] + ['<td style="width: 35px;"></td>']
    div_tds_list = [f'<td style="width: 35px; height: 50px; vertical-align: bottom; text-align: center; border-top: 3px solid #000; {"border-left: 3px solid #000;" if i == 0 else ""} font-size: 38px;">{c}</td>' for i, c in enumerate(div_str)] + ['<td style="width: 35px;"></td>']
    
    html = f"{equation_html}<div style=\"display: block; margin-left: 60px; margin-top: 15px; margin-bottom: 15px;\"><div style=\"display: inline-block; font-family: 'Sarabun', sans-serif; line-height: 1.2;\"><table style=\"border-collapse: collapse;\"><tr><td style=\"border: none;\"></td>{''.join(ans_tds_list)}</tr><tr><td style=\"border: none; text-align: right; padding-right: 12px; vertical-align: bottom; font-size: 38px;\">{divisor}</td>{''.join(div_tds_list)}</tr>"
    
    for idx, step in enumerate(steps):
        mul_res_str = str(step['mul_res'])
        pad_len = step['col_index'] + 1 - len(mul_res_str)
        mul_tds = ""
        for i in range(div_len + 1):
            if i >= pad_len and i <= step['col_index']:
                border_b = "border-bottom: 2px solid #000;" if i <= step['col_index'] else ""
                mul_tds += f'<td style="width: 35px; height: 50px; vertical-align: bottom; text-align: center; font-size: 38px; {border_b}">{mul_res_str[i - pad_len]}</td>'
            elif i == step['col_index'] + 1: mul_tds += '<td style="width: 35px; text-align: center; font-size: 38px; color: #333; position: relative; top: -24px;">-</td>'
            else: mul_tds += '<td style="width: 35px;"></td>'
        html += f"<tr><td style='border: none;'></td>{mul_tds}</tr>"
        
        is_last_step = (idx == len(steps) - 1)
        display_str = str(step['rem']) if str(step['rem']) != "0" or is_last_step else ""
        next_digit = div_str[step['col_index'] + 1] if not is_last_step else ""
        if not is_last_step and display_str != "": display_str += next_digit
        elif display_str == "": display_str = next_digit
        
        pad_len_rem = step['col_index'] + 1 - len(display_str) + (1 if not is_last_step else 0)
        rem_tds = ""
        for i in range(div_len + 1):
            if i >= pad_len_rem and i <= step['col_index'] + (1 if not is_last_step else 0):
                border_b2 = "border-bottom: 6px double #000;" if is_last_step else ""
                rem_tds += f'<td style="width: 35px; height: 50px; vertical-align: bottom; text-align: center; font-size: 38px; {border_b2}">{display_str[i - pad_len_rem]}</td>'
            else: rem_tds += '<td style="width: 35px;"></td>'
        html += f"<tr><td style='border: none;'></td>{rem_tds}</tr>"
    html += "</table></div></div>"
    return html

def get_decimal_long_div_html(divisor, dividend_str, max_dp=2):
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
    final_quotient = "".join(ans_chars).strip()
    if final_quotient.startswith('.'): final_quotient = '0' + final_quotient
    if final_quotient.endswith('.'): final_quotient = final_quotient[:-1]
    
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

def generate_thai_number_text(num_str):
    thai_nums = ["ศูนย์", "หนึ่ง", "สอง", "สาม", "สี่", "ห้า", "หก", "เจ็ด", "แปด", "เก้า"]
    positions = ["", "สิบ", "ร้อย", "พัน", "หมื่น", "แสน", "ล้าน"]
    def read_int(s):
        if s == "0" or s == "": return "ศูนย์"
        if len(s) > 6:
            mil_part, rest_part = s[:-6], s[-6:]
            res = read_int(mil_part) + "ล้าน"
            if int(rest_part) > 0: res += read_int(rest_part)
            return res
        res, length = "", len(s)
        for i, digit in enumerate(s):
            d = int(digit)
            if d == 0: continue
            pos = length - i - 1
            if pos == 1 and d == 2: res += "ยี่สิบ"
            elif pos == 1 and d == 1: res += "สิบ"
            elif pos == 0 and d == 1 and length > 1: res += "เอ็ด"
            else: res += thai_nums[d] + positions[pos]
        return res
    parts = str(num_str).replace(",", "").split(".")
    int_text = read_int(parts[0])
    dec_text = ("จุด" + "".join([thai_nums[int(d)] for d in parts[1]])) if len(parts) > 1 else ""
    return int_text + dec_text
    # ==========================================
# 🌟 ฟังก์ชันวาดรูปภาพ SVG สำหรับเรขาคณิต & สมการ 🌟
# ==========================================
def draw_rect_svg(w_val, h_val, w_lbl, h_lbl, fill_color="#eaf2f8"):
    scale = 140 / max(w_val, h_val)
    dw, dh = w_val * scale, h_val * scale
    svg = f'<div style="text-align:center; margin: 15px 0;"><svg width="300" height="200">'
    svg += f'<rect x="{150 - dw/2}" y="{100 - dh/2}" width="{dw}" height="{dh}" fill="{fill_color}" stroke="#2980b9" stroke-width="3"/>'
    svg += f'<text x="150" y="{100 - dh/2 - 10}" font-family="Sarabun" font-size="16" font-weight="bold" fill="#c0392b" text-anchor="middle">{w_lbl}</text>'
    svg += f'<text x="{150 + dw/2 + 10}" y="100" font-family="Sarabun" font-size="16" font-weight="bold" fill="#c0392b" text-anchor="start" dominant-baseline="middle">{h_lbl}</text>'
    return svg + '</svg></div>'

def draw_shaded_svg(scenario, W, H, p1=0):
    svg = '<div style="text-align:center; margin:15px 0;"><svg width="460" height="240">'
    max_w, max_h = 200, 140 
    scale = min(max_w / W, max_h / H)
    draw_w, draw_h = W * scale, H * scale
    ox, oy = (460 - draw_w) / 2, (240 - draw_h) / 2
    lbl_style = 'font-family:Sarabun; font-size:15px; font-weight:bold; fill:#c0392b;'
    lbl_style_sm = 'font-family:Sarabun; font-size:14px; font-weight:bold; fill:#2980b9;'
    
    if scenario == "frame":
        border_scale = p1 * scale
        svg += f'<rect x="{ox}" y="{oy}" width="{draw_w}" height="{draw_h}" fill="#bdc3c7" stroke="#2c3e50" stroke-width="3"/>'
        svg += f'<rect x="{ox+border_scale}" y="{oy+border_scale}" width="{draw_w-2*border_scale}" height="{draw_h-2*border_scale}" fill="#ffffff" stroke="#2c3e50" stroke-width="2"/>'
        svg += f'<text x="{ox + draw_w/2}" y="{oy - 10}" {lbl_style} text-anchor="middle">{W} ม.</text>'
        svg += f'<text x="{ox - 10}" y="{oy + draw_h/2 + 5}" {lbl_style} text-anchor="end">{H} ม.</text>'
        svg += f'<text x="{ox + draw_w/2}" y="{oy + border_scale/2 + 5}" {lbl_style_sm} text-anchor="middle">กว้าง {p1} ม.</text>'
    elif scenario == "corner_cut":
        cut_scale = p1 * scale
        pts = f"{ox},{oy} {ox+draw_w-cut_scale},{oy} {ox+draw_w-cut_scale},{oy+cut_scale} {ox+draw_w},{oy+cut_scale} {ox+draw_w},{oy+draw_h} {ox},{oy+draw_h}"
        svg += f'<polygon points="{pts}" fill="#bdc3c7" stroke="#2c3e50" stroke-width="3"/>'
        svg += f'<rect x="{ox}" y="{oy}" width="{draw_w}" height="{draw_h}" fill="none" stroke="#7f8c8d" stroke-width="2" stroke-dasharray="5,5"/>'
        svg += f'<text x="{ox + draw_w/2}" y="{oy + draw_h + 20}" {lbl_style} text-anchor="middle">{W} ซม.</text>'
        svg += f'<text x="{ox - 10}" y="{oy + draw_h/2 + 5}" {lbl_style} text-anchor="end">{H} ซม.</text>'
        svg += f'<text x="{ox + draw_w - cut_scale/2}" y="{oy - 10}" {lbl_style_sm} text-anchor="middle">ตัด {p1}x{p1}</text>'
    elif scenario == "triangle_in_rect":
        svg += f'<rect x="{ox}" y="{oy}" width="{draw_w}" height="{draw_h}" fill="#bdc3c7" stroke="#2c3e50" stroke-width="3"/>'
        svg += f'<polygon points="{ox},{oy+draw_h} {ox+draw_w},{oy+draw_h} {ox+draw_w/2},{oy}" fill="#ffffff" stroke="#2c3e50" stroke-width="2"/>'
        svg += f'<text x="{ox + draw_w/2}" y="{oy + draw_h + 20}" {lbl_style} text-anchor="middle">{W} นิ้ว</text>'
        svg += f'<text x="{ox - 10}" y="{oy + draw_h/2 + 5}" {lbl_style} text-anchor="end">{H} นิ้ว</text>'
    elif scenario == "cross_path":
        p_scale = p1 * scale
        svg += f'<rect x="{ox}" y="{oy}" width="{draw_w}" height="{draw_h}" fill="#ffffff" stroke="none"/>'
        svg += f'<rect x="{ox}" y="{oy + (draw_h - p_scale)/2}" width="{draw_w}" height="{p_scale}" fill="#bdc3c7" stroke="none"/>'
        svg += f'<rect x="{ox + (draw_w - p_scale)/2}" y="{oy}" width="{p_scale}" height="{draw_h}" fill="#bdc3c7" stroke="none"/>'
        svg += f'<rect x="{ox}" y="{oy}" width="{draw_w}" height="{draw_h}" fill="none" stroke="#2c3e50" stroke-width="3"/>'
        svg += f'<text x="{ox + draw_w/2}" y="{oy + draw_h + 20}" {lbl_style} text-anchor="middle">{W} ม.</text>'
        svg += f'<text x="{ox - 10}" y="{oy + draw_h/2 + 5}" {lbl_style} text-anchor="end">{H} ม.</text>'
        svg += f'<text x="{ox + draw_w + 10}" y="{oy + draw_h/2 + 5}" {lbl_style_sm} text-anchor="start">กว้าง {p1} ม.</text>'
    elif scenario == "midpoint_rhombus":
        svg += f'<rect x="{ox}" y="{oy}" width="{draw_w}" height="{draw_h}" fill="#ffffff" stroke="#2c3e50" stroke-width="3"/>'
        pts = f"{ox+draw_w/2},{oy} {ox+draw_w},{oy+draw_h/2} {ox+draw_w/2},{oy+draw_h} {ox},{oy+draw_h/2}"
        svg += f'<polygon points="{pts}" fill="#bdc3c7" stroke="#2c3e50" stroke-width="2"/>'
        svg += f'<text x="{ox + draw_w/2}" y="{oy + draw_h + 20}" {lbl_style} text-anchor="middle">{W} ซม.</text>'
        svg += f'<text x="{ox - 10}" y="{oy + draw_h/2 + 5}" {lbl_style} text-anchor="end">{H} ซม.</text>'
    return svg + '</svg></div>'

def draw_prism_svg(w_lbl, l_lbl, h_lbl, is_water=False):
    svg = '<div style="text-align:center; margin:15px 0;"><svg width="250" height="190">'
    fill_front, fill_top, fill_right = ("#aed6f1", "#85c1e9", "#5dade2") if is_water else ("#d5f5e3", "#abebc6", "#82e0aa")
    stroke_c = "#2874a6" if is_water else "#27ae60"
    if is_water:
        y_offset = 55 
        svg += '<line x1="100" y1="10" x2="100" y2="110" stroke="#bdc3c7" stroke-width="2"/>'
        svg += '<line x1="100" y1="110" x2="200" y2="110" stroke="#bdc3c7" stroke-width="2"/>'
        svg += '<line x1="60" y1="130" x2="100" y2="110" stroke="#bdc3c7" stroke-width="2"/>'
        svg += f'<polygon points="60,{30+y_offset} 100,{10+y_offset} 200,{10+y_offset} 160,{30+y_offset}" fill="{fill_top}" stroke="{stroke_c}" stroke-width="2" opacity="0.85"/>'
        svg += f'<rect x="60" y="{30+y_offset}" width="100" height="{100-y_offset}" fill="{fill_front}" stroke="{stroke_c}" stroke-width="2" opacity="0.85"/>'
        svg += f'<polygon points="160,{30+y_offset} 200,{10+y_offset} 200,110 160,130" fill="{fill_right}" stroke="{stroke_c}" stroke-width="2" opacity="0.85"/>'
        svg += '<polygon points="60,30 100,10 200,10 160,30" fill="none" stroke="#95a5a6" stroke-width="2"/>'
        svg += '<line x1="60" y1="30" x2="60" y2="130" stroke="#95a5a6" stroke-width="2"/>'
        svg += '<line x1="160" y1="30" x2="160" y2="130" stroke="#95a5a6" stroke-width="2"/>'
        svg += '<line x1="200" y1="10" x2="200" y2="110" stroke="#95a5a6" stroke-width="2"/>'
    else:
        svg += f'<rect x="60" y="50" width="100" height="80" fill="{fill_front}" stroke="{stroke_c}" stroke-width="3"/>'
        svg += f'<polygon points="60,50 100,20 200,20 160,50" fill="{fill_top}" stroke="{stroke_c}" stroke-width="3"/>'
        svg += f'<polygon points="160,50 200,20 200,100 160,130" fill="{fill_right}" stroke="{stroke_c}" stroke-width="3"/>'
    svg += f'<text x="110" y="150" font-size="14" fill="#2c3e50" font-weight="bold" text-anchor="middle">{l_lbl}</text>'
    svg += f'<text x="190" y="125" font-size="14" fill="#2c3e50" font-weight="bold">{w_lbl}</text>'
    if is_water: svg += f'<text x="10" y="{80+y_offset/2}" font-size="14" fill="#2980b9" font-weight="bold">{h_lbl}</text>'
    else: svg += f'<text x="20" y="95" font-size="14" fill="#2c3e50" font-weight="bold">{h_lbl}</text>'
    return svg + '</svg></div>'

def draw_marbles_box_svg(color_counts):
    color_map = {"สีแดง": "#e74c3c", "สีฟ้า": "#3498db", "สีเขียว": "#2ecc71", "สีเหลือง": "#f1c40f", "สีม่วง": "#9b59b6"}
    total_marbles = sum(color_counts.values())
    cols = 10 if total_marbles > 20 else 8
    rows = (total_marbles + cols - 1) // cols
    marble_r, col_w, row_h = 12, 36, 36
    box_width, box_height = max(320, cols * col_w + 30), max(140, rows * row_h + 60)
    width, height = box_width + 100, box_height + 40
    svg = f'<div style="text-align:center; margin: 15px 0;"><svg width="{width}" height="{height}">'
    box_x, box_y = 50, 20
    svg += f'<rect x="{box_x}" y="{box_y}" width="{box_width}" height="{box_height}" fill="#ecf0f1" stroke="#34495e" stroke-width="4" rx="15"/>'
    svg += f'<path d="M {box_x} {box_y + 35} L {box_x + box_width} {box_y + 35}" stroke="#bdc3c7" stroke-width="2" stroke-dasharray="5,5"/>'
    
    marbles = []
    for c_name, count in color_counts.items():
        for _ in range(count): marbles.append(color_map[c_name])
    random.shuffle(marbles)
    
    start_x, start_y = box_x + 20 + marble_r, box_y + 35 + 15 + marble_r
    for i, color in enumerate(marbles):
        cx, cy = start_x + ((i % cols) * col_w), start_y + ((i // cols) * row_h)
        svg += f'<circle cx="{cx}" cy="{cy}" r="{marble_r}" fill="{color}" stroke="#2c3e50" stroke-width="3"/>'
        svg += f'<circle cx="{cx-4}" cy="{cy-4}" r="3" fill="#ffffff" opacity="0.5"/>'
    return svg + '</svg></div>'

def draw_avg_box(icon, count, label_count, avg_val, label_avg, bg_color="#f1f8ff", border_color="#3498db"):
    box_style = f"border: 2px dashed {border_color}; border-radius: 8px; padding: 10px 15px; display: inline-block; text-align: center; margin: 5px; background-color: {bg_color}; vertical-align: top; min-width: 120px;"
    return f'<div style="{box_style}"><div style="font-size:24px;">{icon} {count} {label_count}</div><div style="font-size: 14px; font-weight: bold; color: #7f8c8d; margin-top: 5px;">ค่าเฉลี่ย</div><div style="font-size: 20px; font-weight: bold; color: #e74c3c;">{avg_val} {label_avg}</div></div>'

def render_short_div(nums, mode="gcd"):
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
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
    font_size = "16px" if is_x else "14px"
    return arc_svg + f'<text x="{tx}" y="{ty+5}" font-size="{font_size}" font-weight="bold" font-family="Sarabun" text-anchor="middle" fill="{color_text}">{label}</text>'

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
    svg += '<line x1="40" y1="60" x2="300" y2="60" stroke="#2980b9" stroke-width="4"/><line x1="40" y1="120" x2="300" y2="120" stroke="#2980b9" stroke-width="4"/>'
    svg += '<polygon points="285,55 295,60 285,65" fill="#2980b9"/><polygon points="285,115 295,120 285,125" fill="#2980b9"/>'
    lbl_style = 'font-family:Sarabun; font-size:16px; font-weight:bold; fill:#2c3e50;'
    svg += f'<text x="20" y="65" {lbl_style}>A</text><text x="310" y="65" {lbl_style}>B</text><text x="20" y="125" {lbl_style}>C</text><text x="310" y="125" {lbl_style}>D</text>'
    meta = angle_meta[dir_key]
    bot, top = meta["bot"], meta["top"]
    svg += f'<line x1="{bot[0]}" y1="{bot[1]}" x2="{top[0]}" y2="{top[1]}" stroke="#3498db" stroke-width="4"/><circle cx="{bot[0]}" cy="{bot[1]}" r="4" fill="#3498db" /><circle cx="{top[0]}" cy="{top[1]}" r="4" fill="#3498db" />'
    V1, V2 = meta["V1"], meta["V2"]
    def draw_pos(pos, val, is_var):
        vx, arm1, arm2 = get_arms(pos, V1, V2, bot, top)
        return draw_angle_feature(vx[0], vx[1], arm1[0], arm1[1], arm2[0], arm2[1], 25, 42, "x" if is_var else f"{val}°", "#2ecc71", "#2980b9" if is_var else "#c0392b", is_x=is_var)
    svg += draw_pos(pos1, val1, is_var=False) + draw_pos(pos2, val2, is_var=True)
    return svg + '</svg></div>'

def draw_basic_angle(deg, p1_name, v_name, p2_name):
    svg = '<div style="text-align:center; margin:15px 0;"><svg width="300" height="240">'
    vx, vy, arm_l = 150, 120, 100
    bx, by = vx + arm_l, vy
    rad = math.radians(deg)
    ax, ay = vx + arm_l * math.cos(rad), vy - arm_l * math.sin(rad)
    svg += f'<line x1="{vx}" y1="{vy}" x2="{bx}" y2="{by}" stroke="#34495e" stroke-width="4" stroke-linecap="round"/><line x1="{vx}" y1="{vy}" x2="{ax}" y2="{ay}" stroke="#34495e" stroke-width="4" stroke-linecap="round"/>'
    r = 20
    if deg == 90: svg += f'<polyline points="{vx},{vy-r} {vx+r},{vy-r} {vx+r},{vy}" fill="none" stroke="#e74c3c" stroke-width="3"/>'
    elif deg == 180: svg += f'<path d="M {vx+r} {vy} A {r} {r} 0 0 0 {vx-r} {vy}" fill="none" stroke="#e74c3c" stroke-width="3"/>'
    else:
        ex, ey = vx + r * math.cos(rad), vy - r * math.sin(rad)
        large_arc = 1 if deg > 180 else 0
        svg += f'<path d="M {vx+r} {vy} A {r} {r} 0 {large_arc} 0 {ex} {ey}" fill="none" stroke="#e74c3c" stroke-width="3"/>'
    svg += f'<circle cx="{vx}" cy="{vy}" r="5" fill="#c0392b"/><circle cx="{bx}" cy="{by}" r="5" fill="#c0392b"/><circle cx="{ax}" cy="{ay}" r="5" fill="#c0392b"/>'
    lbl = 'font-family:Sarabun; font-size:18px; font-weight:bold; fill:#2c3e50;'
    svg += f'<text x="{vx-15}" y="{vy+20}" {lbl}>{v_name}</text><text x="{bx+15}" y="{by+5}" {lbl}>{p2_name}</text>'
    ax_off, ay_off = (15 if ax >= vx else -25), (5 if ay >= vy else -10)
    svg += f'<text x="{ax+ax_off}" y="{ay-ay_off}" {lbl}>{p1_name}</text>'
    tx, ty = vx + (r+25) * math.cos(rad/2), vy - (r+25) * math.sin(rad/2)
    svg += f'<text x="{tx}" y="{ty+5}" font-family="Sarabun" font-size="16" font-weight="bold" fill="#e74c3c" text-anchor="middle">{deg}°</text>'
    return svg + '</svg></div>'

def draw_protractor_svg(deg1, deg2, p1_name, v_name, p2_name):
    svg = '<div style="text-align:center; margin:15px 0;"><svg width="560" height="260">'
    cx, cy, r_outer, r_inner = 280, 200, 120, 80
    svg += f'<path d="M {cx-r_outer-15} {cy} A {r_outer+15} {r_outer+15} 0 0 1 {cx+r_outer+15} {cy} Z" fill="#eef2f5" stroke="#bdc3c7" stroke-width="1.5"/><path d="M {cx-r_outer} {cy} A {r_outer} {r_outer} 0 0 1 {cx+r_outer} {cy} Z" fill="none" stroke="#7f8c8d" stroke-width="1"/><line x1="{cx-r_outer-15}" y1="{cy}" x2="{cx+r_outer+15}" y2="{cy}" stroke="#95a5a6" stroke-width="1.5"/>'
    for i in range(181):
        angle_rad = math.radians(i)
        cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)
        if i % 10 == 0:
            tx_out, ty_out = cx + (r_outer-15)*cos_a, cy - (r_outer-15)*sin_a
            tx_in, ty_in = cx + (r_inner+15)*cos_a, cy - (r_inner+15)*sin_a
            if i not in [0, 180]:
                svg += f'<text x="{tx_out}" y="{ty_out+3}" font-family="sans-serif" font-size="9" font-weight="bold" fill="#2c3e50" text-anchor="middle">{180-i}</text><text x="{tx_in}" y="{ty_in+3}" font-family="sans-serif" font-size="9" font-weight="bold" fill="#2980b9" text-anchor="middle">{i}</text>'
            elif i == 0:
                svg += f'<text x="{cx+r_outer-15}" y="{cy-3}" font-family="sans-serif" font-size="9" font-weight="bold" fill="#2c3e50" text-anchor="middle">180</text><text x="{cx+r_inner+10}" y="{cy-3}" font-family="sans-serif" font-size="9" font-weight="bold" fill="#2980b9" text-anchor="middle">0</text>'
            elif i == 180:
                svg += f'<text x="{cx-r_outer+15}" y="{cy-3}" font-family="sans-serif" font-size="9" font-weight="bold" fill="#2c3e50" text-anchor="middle">0</text><text x="{cx-r_inner-10}" y="{cy-3}" font-family="sans-serif" font-size="9" font-weight="bold" fill="#2980b9" text-anchor="middle">180</text>'
        tick = 10 if i % 10 == 0 else (7 if i % 5 == 0 else 4)
        svg += f'<line x1="{cx+r_outer*cos_a}" y1="{cy-r_outer*sin_a}" x2="{cx+(r_outer-tick)*cos_a}" y2="{cy-(r_outer-tick)*sin_a}" stroke="#34495e" stroke-width="0.5"/>'
    arm_len = 140
    rad1, rad2 = math.radians(deg1), math.radians(deg2)
    svg += f'<line x1="{cx}" y1="{cy}" x2="{cx+arm_len*math.cos(rad1)}" y2="{cy-arm_len*math.sin(rad1)}" stroke="#e74c3c" stroke-width="1.5" stroke-linecap="round"/><line x1="{cx}" y1="{cy}" x2="{cx+arm_len*math.cos(rad2)}" y2="{cy-arm_len*math.sin(rad2)}" stroke="#e74c3c" stroke-width="1.5" stroke-linecap="round"/>'
    attr = 'font-family="sans-serif" font-size="18" font-weight="bold" fill="#c0392b" text-anchor="middle"'
    svg += f'<text x="{cx}" y="{cy+25}" {attr}>{v_name}</text>'
    for r, n in [(rad1, p1_name), (rad2, p2_name)]:
        tx, ty = cx+(arm_len+15)*math.cos(r), cy-(arm_len+15)*math.sin(r)
        ty = ty-4 if math.sin(r)>0.5 else ty+6
        svg += f'<text x="{tx}" y="{ty}" {attr}>{n}</text>'
    return svg + '</svg></div>'

# ==========================================
# ฐานข้อมูลหลักสูตร (Master Database P.4 - P.5)
# ==========================================
curriculum_db = {
    "ป.4": {
        "จำนวนนับที่มากกว่า 100,000": ["การอ่านและการเขียนตัวเลข", "หลัก ค่าประจำหลัก และรูปกระจาย", "การเปรียบเทียบและเรียงลำดับ", "ค่าประมาณเป็นจำนวนเต็มสิบ เต็มร้อย เต็มพัน"],
        "การบวก ลบ คูณ หาร": ["การบวก (แบบตั้งหลัก)", "การลบ (แบบตั้งหลัก)", "การคูณ (แบบตั้งหลัก)", "การหารยาวแบบลงตัว", "การหารยาวแบบไม่ลงตัว"],
        "เศษส่วนและทศนิยม": ["แปลงเศษเกินเป็นจำนวนคละ", "การอ่านและการเขียนทศนิยม", "การบวกเศษส่วน", "การลบเศษส่วน", "การคูณเศษส่วน", "การหารเศษส่วน", "การบวกทศนิยม", "การลบทศนิยม", "การคูณทศนิยม", "การหารทศนิยม"],
        "เรขาคณิตและการวัด": [
            "การบอกชนิดของมุม", 
            "การวัดขนาดของมุม (ไม้โปรแทรกเตอร์)", 
            "การสร้างมุมตามขนาดที่กำหนด", 
            "การหาความยาวรอบรูปสี่เหลี่ยมมุมฉาก", 
            "การหาความยาวรอบรูปสามเหลี่ยม", 
            "การหาความยาวรอบรูปสี่เหลี่ยมด้านขนานและขนมเปียกปูน",
            "การหาความยาวรอบรูปสี่เหลี่ยมรูปว่าว",
            "การหาพื้นที่รูปสี่เหลี่ยมมุมฉาก",
            "การหาพื้นที่รูปสามเหลี่ยม (พื้นฐาน)",
            "การหาพื้นที่สี่เหลี่ยมด้านขนานและขนมเปียกปูน (พื้นฐาน)",
            "การหาพื้นที่โดยการนับตาราง",
            "โจทย์ปัญหาเรขาคณิต (รั้วและพื้นที่ชีวิตจริง)"
        ],
        "สมการ": ["การแก้สมการ (บวก/ลบ)", "การแก้สมการ (คูณ/หาร)", "สมการและตัวไม่ทราบค่าจากชีวิตประจำวัน", "สมการเชิงตรรกะและตาชั่งปริศนา", "โจทย์ปัญหาสมการ: ความสัมพันธ์ของ 2 สิ่ง"]
    },
    "ป.5": {
        "เศษส่วน": ["การบวกเศษส่วน", "การลบเศษส่วน", "การคูณเศษส่วน", "การหารเศษส่วน"],
        "ทศนิยม": ["การบวกและการลบทศนิยม", "การคูณและการหารทศนิยม"],
        "สถิติและความน่าจะเป็น": ["การหาค่าเฉลี่ย (Average)", "ความน่าจะเป็นเบื้องต้น (สุ่มหยิบของ)"],
        "เรขาคณิต 2 มิติและ 3 มิติ": ["โจทย์ปัญหาพื้นที่และความยาวรอบรูป", "เส้นขนานและมุมแย้ง", "ปริมาตรและความจุทรงสี่เหลี่ยมมุมฉาก"],
        "ร้อยละและเปอร์เซ็นต์": ["การเขียนเศษส่วนในรูปร้อยละ"],
        "สมการ": ["การแก้สมการ (คูณ/หาร)"]
    }
}

# ==========================================
# 3. Logic & Dynamic Difficulty Scaling (P.4 - P.5)
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

            # ================= หมวด ป.4 และ ป.5 =================
            if actual_sub_t == "การอ่านและการเขียนตัวเลข":
                num = random.randint(100000, 999999) if not is_challenge else random.randint(1000000, 99999999)
                thai_text = generate_thai_number_text(str(num))
                mode = random.choice(["to_text", "to_num"])
                if mode == "to_text":
                    q = f"จงเขียนตัวเลข <b>{num:,}</b> เป็นตัวหนังสือภาษาไทย"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 อ่านตามหลักจากซ้ายไปขวา (ร้อยล้าน สิบล้าน ล้าน แสน หมื่น พัน ร้อย สิบ หน่วย)<br><b>ตอบ: {thai_text}</b></span>"
                else:
                    q = f"จงเขียนคำอ่าน <b>\"{thai_text}\"</b> เป็นตัวเลขฮินดูอารบิก"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 แปลงจากคำอ่านเป็นตัวเลขทีละหลัก และอย่าลืมใส่เครื่องหมายจุลภาค (,)<br><b>ตอบ: {num:,}</b></span>"



            elif actual_sub_t == "หลัก ค่าประจำหลัก และรูปกระจาย":
                num = random.randint(100000, 9999999) if not is_challenge else random.randint(10000000, 999999999)
                num_str = str(num)
                mode = random.choice(["expanded", "digit_value"])
                if mode == "expanded":
                    q = f"จงเขียนจำนวน <b>{num:,}</b> ให้อยู่ในรูปกระจาย"
                    expanded = " + ".join([f"{int(d) * (10**(len(num_str)-i-1))}" for i, d in enumerate(num_str) if d != '0'])
                    sol = f"<span style='color:#2c3e50;'><b>ตอบ: {expanded}</b></span>"
                else:
                    target_idx = random.randint(0, len(num_str)-1)
                    while num_str[target_idx] == '0': target_idx = random.randint(0, len(num_str)-1)
                    target_digit = num_str[target_idx]
                    place_names = ["หน่วย", "สิบ", "ร้อย", "พัน", "หมื่น", "แสน", "ล้าน", "สิบล้าน", "ร้อยล้าน"]
                    place = place_names[len(num_str) - target_idx - 1]
                    val = int(target_digit) * (10**(len(num_str) - target_idx - 1))
                    q = f"จากจำนวน <b>{num:,}</b> เลขโดด <b>{target_digit}</b> (ตัวที่ขีดเส้นใต้) อยู่ในหลักใด และมีค่าเท่าใด?<br><span style='font-size:24px;'>{num_str[:target_idx]}<u>{target_digit}</u>{num_str[target_idx+1:]}</span>"
                    sol = f"<span style='color:#2c3e50;'><b>ตอบ: หลัก{place} มีค่า {val:,}</b></span>"



            elif actual_sub_t == "การเปรียบเทียบและเรียงลำดับ":
                digits = random.randint(5, 7)
                base, limit = 10**(digits-1), 10**digits - 1
                nums = [random.randint(base, limit) for _ in range(4)]
                q_list = " &nbsp;&nbsp;&nbsp; ".join([f"{x:,}" for x in nums])
                mode = random.choice(["asc", "desc"])
                mode_text = "น้อยไปมาก" if mode == "asc" else "มากไปน้อย"
                sorted_nums = sorted(nums) if mode == "asc" else sorted(nums, reverse=True)
                ans_list = " &nbsp; | &nbsp; ".join([f"{x:,}" for x in sorted_nums])
                q = f"จงเรียงลำดับจำนวนต่อไปนี้จาก <b>{mode_text}</b>ให้ถูกต้อง<br><br><span style='font-size:22px; letter-spacing:1px;'>{q_list}</span>"
                sol = f"<span style='color:#2c3e50;'><b>ตอบ: {ans_list}</b></span>"



            elif actual_sub_t == "ค่าประมาณเป็นจำนวนเต็มสิบ เต็มร้อย เต็มพัน":
                target = random.choice(["สิบ", "ร้อย", "พัน"])
                num = random.randint(1234, 99999) if not is_challenge else random.randint(100000, 999999)
                if target == "สิบ":
                    check_val, round_base = num % 10, (num // 10) * 10
                    ans = round_base + 10 if check_val >= 5 else round_base
                elif target == "ร้อย":
                    check_val, round_base = (num % 100) // 10, (num // 100) * 100
                    ans = round_base + 100 if check_val >= 5 else round_base
                else:
                    check_val, round_base = (num % 1000) // 100, (num // 1000) * 1000
                    ans = round_base + 1000 if check_val >= 5 else round_base
                q = f"จงหาค่าประมาณเป็น<b>จำนวนเต็ม{target}</b> ของ <b>{num:,}</b>"
                sol = f"<span style='color:#2c3e50;'><b>ตอบ: {ans:,}</b></span>"


                
            elif actual_sub_t in ["การบวก (แบบตั้งหลัก)", "การลบ (แบบตั้งหลัก)", "การคูณ (แบบตั้งหลัก)"]:
                if actual_sub_t == "การบวก (แบบตั้งหลัก)":
                    a, b = random.randint(100000, 999999), random.randint(100000, 999999)
                    op, ans = "+", a + b
                elif actual_sub_t == "การลบ (แบบตั้งหลัก)":
                    a = random.randint(100000, 999999)
                    b = random.randint(50000, a - 1000)
                    op, ans = "-", a - b
                else:
                    a, b = random.randint(100, 9999), random.randint(12, 99)
                    op, ans = "×", a * b
                table_html = generate_vertical_table_html(a, b, op, result=ans, is_key=False)
                table_key = generate_vertical_table_html(a, b, op, result=ans, is_key=True)
                q = f"จงหาผลลัพธ์ของ <b>{a:,} {op} {b:,}</b><br>{table_html}"
                sol = f"<span style='color:#2c3e50;'>{table_key}</span>"



            elif actual_sub_t in ["การหารยาวแบบลงตัว", "การหารยาวแบบไม่ลงตัว"]:
                divisor = random.randint(2, 9) if not is_challenge else random.randint(11, 99)
                quotient = random.randint(1000, 9999)
                
                # 💡 กำหนดเงื่อนไขเศษให้ตรงกับหัวข้อ
                if actual_sub_t == "การหารยาวแบบลงตัว":
                    remainder = 0
                else:
                    remainder = random.randint(1, divisor - 1)
                    
                dividend = (divisor * quotient) + remainder
                
                eq_html = f"<div style='font-size: 24px; margin-bottom: 10px;'><b>{dividend:,} ÷ {divisor:,} = ?</b></div>"
                table_html = generate_long_division_step_by_step_html(divisor, dividend, eq_html, is_key=False)
                table_key = generate_long_division_step_by_step_html(divisor, dividend, eq_html, is_key=True)
                
                q = f"จงหาผลหารโดยวิธีหารยาว<br>{table_html}"
                ans_txt = f"{quotient:,}" if remainder == 0 else f"{quotient:,} เศษ {remainder:,}"
                sol = f"<span style='color:#2c3e50;'>{table_key}<br><b>ตอบ: {ans_txt}</b></span>"



            elif actual_sub_t == "การบอกชนิดของมุม":
                l_pool = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
                p1, v, p2 = random.sample(l_pool, 3)
                
                # 🎨 สร้างสัญลักษณ์มุม (หมวกสีแดง) ไว้บนอักษรตัวกลาง
                hat_v = f"<span style='position:relative; display:inline-block;'>{v}<span style='position:absolute; top:-12px; left:50%; transform:translateX(-50%); color:#e74c3c; font-weight:normal; font-size:22px;'>^</span></span>"
                angle_name_display = f"{p1}{hat_v}{p2}"
                
                angle = random.randint(15, 345) 
                roll = random.random()
                if roll < 0.15: angle = 90
                elif roll < 0.30: angle = 180
                
                if angle < 90: angle_type = "มุมแหลม"
                elif angle == 90: angle_type = "มุมฉาก"
                elif angle < 180: angle_type = "มุมป้าน"
                elif angle == 180: angle_type = "มุมตรง"
                else: angle_type = "มุมกลับ"
                    
                svg_html = draw_basic_angle(angle, p1, v, p2)
                q = f"จากรูป มุม <b>{angle_name_display}</b> ที่มีขนาด <b>{angle}°</b> คือมุมชนิดใด?<br>{svg_html}<span style='font-size:18px; color:#7f8c8d;'>(มุมแหลม, มุมฉาก, มุมป้าน, มุมตรง, มุมกลับ)</span>"
                sol = f"<span style='color:#2c3e50;'><b>ตอบ: {angle_type}</b></span>"



            elif actual_sub_t == "การวัดขนาดของมุม (ไม้โปรแทรกเตอร์)":
                l_pool = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
                p1, v, p2 = random.sample(l_pool, 3)
                
                # 🎨 สร้างสัญลักษณ์มุม (หมวกสีแดง) ไว้บนอักษรตัวกลาง
                hat_v = f"<span style='position:relative; display:inline-block;'>{v}<span style='position:absolute; top:-12px; left:50%; transform:translateX(-50%); color:#e74c3c; font-weight:normal; font-size:22px;'>^</span></span>"
                angle_name_display = f"{p1}{hat_v}{p2}"
                
                mode = random.choice(["read_protractor", "calc_angle"])
                if mode == "read_protractor":
                    base_deg = random.choice([0, 180, 20, 160])
                    angle = random.randint(30, 120)
                    end_deg = base_deg + angle if base_deg < 90 else base_deg - angle
                    
                    q = f"จากรูปการวัดขนาดของมุมด้วยไม้โปรแทรกเตอร์ มุม <b>{angle_name_display}</b> มีขนาดกี่องศา?<br>{draw_protractor_svg(base_deg, end_deg, p1, v, p2)}"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b> ผลต่างคือ |{base_deg} - {end_deg}| = <b>{abs(end_deg-base_deg)}°</b></span>"
                else:
                    ans = random.randint(30, 150)
                    svg = draw_parallel_svg("dir1", "TL_int", 180-ans, "BL_int", "x") 
                    
                    q = f"มุมบนเส้นตรงรวมกันได้ 180 องศา ถ้ามุมหนึ่งกาง <b>{180-ans}°</b> จงหาขนาดของมุม <b>x</b> ที่เหลือ?"
                    sol = f"<span style='color:#2c3e50;'><b>ตอบ: {ans}°</b></span>"



            elif actual_sub_t == "การสร้างมุมตามขนาดที่กำหนด":
                # 🚫 ระบบคัดกรองคำต้องห้ามสำหรับเด็ก
                bad_words = ["KUY", "KVY", "FUG", "FUQ", "FUC", "FUK", "SUK", "SUC", "CUM", "DIC", "DIK", "SEX", "ASS", "TIT", "FAP", "GAY", "PEE", "POO", "WTF", "BUM", "DOG", "PIG", "FAT", "SAD", "BAD", "MAD", "DIE", "RIP", "SOB"]
                
                while True:
                    p1, v, p2 = random.sample(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"), 3)
                    angle_name = f"{p1}{v}{p2}"
                    angle_name_rev = f"{p2}{v}{p1}"
                    if angle_name not in bad_words and angle_name_rev not in bad_words:
                        break
                        
                # 🎨 สร้างสัญลักษณ์มุม (หมวกสีแดง) ไว้บนอักษรตัวกลาง
                hat_v = f"<span style='position:relative; display:inline-block;'>{v}<span style='position:absolute; top:-12px; left:50%; transform:translateX(-50%); color:#e74c3c; font-weight:normal; font-size:22px;'>^</span></span>"
                angle_name_display = f"{p1}{hat_v}{p2}"

                # 💡 สุ่มมุมองศาแบบละเอียด (20 ถึง 160 องศา) เพื่อให้ได้ตัวเลขเช่น 32, 47, 59
                target_deg = random.randint(20, 160)
                
                # 📐 SVG สำหรับโจทย์ (จัดกึ่งกลางและมีกรอบจางๆ ให้ดูเป็นข้อสอบมาตรฐานแข่งขัน)
                svg = f'''<div style="display:flex; justify-content:center; margin: 20px 0;">
                    <div style="border: 1px solid #bdc3c7; border-radius: 8px; padding: 20px; background-color: #fdfefe; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);">
                        <svg width="400" height="150">
                            <line x1="50" y1="100" x2="350" y2="100" stroke="#ecf0f1" stroke-width="1.5" stroke-dasharray="4,4"/>
                            <line x1="200" y1="20" x2="200" y2="130" stroke="#ecf0f1" stroke-width="1.5" stroke-dasharray="4,4"/>
                            
                            <line x1="200" y1="100" x2="330" y2="100" stroke="#34495e" stroke-width="2.5"/>
                            <circle cx="200" cy="100" r="4" fill="#2c3e50"/>
                            <circle cx="330" cy="100" r="3" fill="#2c3e50"/>
                            
                            <text x="195" y="125" font-family="sans-serif" font-size="18" font-weight="bold" fill="#2c3e50" text-anchor="middle">{v}</text>
                            <text x="345" y="105" font-family="sans-serif" font-size="18" font-weight="bold" fill="#2c3e50" text-anchor="middle">{p2}</text>
                        </svg>
                    </div>
                </div>'''
                
                # 📐 SVG สำหรับเฉลย (ไม้โปรแทรกเตอร์โปร่งใส + เส้นลากมุมสีแดง + ส่วนโค้งมุม)
                cx, cy = 280, 220
                r_out, r_in = 140, 100
                svg_sol = '<div style="text-align:center; margin:15px 0;"><svg width="560" height="260">'
                
                # วาดไม้โปรแทรกเตอร์สีจางๆ เป็นพื้นหลัง
                svg_sol += f'<path d="M {cx-r_out-15} {cy} A {r_out+15} {r_out+15} 0 0 1 {cx+r_out+15} {cy} Z" fill="#eef2f5" stroke="#bdc3c7" stroke-width="1.5" opacity="0.6"/>'
                svg_sol += f'<path d="M {cx-r_out} {cy} A {r_out} {r_out} 0 0 1 {cx+r_out} {cy} Z" fill="none" stroke="#7f8c8d" stroke-width="1" opacity="0.6"/>'
                svg_sol += f'<line x1="{cx-r_out-15}" y1="{cy}" x2="{cx+r_out+15}" y2="{cy}" stroke="#95a5a6" stroke-width="1.5" opacity="0.6"/>'
                for idx in range(181):
                    angle_rad = math.radians(idx)
                    cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)
                    tick = 10 if idx % 10 == 0 else (7 if idx % 5 == 0 else 4)
                    svg_sol += f'<line x1="{cx+r_out*cos_a}" y1="{cy-r_out*sin_a}" x2="{cx+(r_out-tick)*cos_a}" y2="{cy-(r_out-tick)*sin_a}" stroke="#7f8c8d" stroke-width="0.5" opacity="0.6"/>'
                    if idx % 10 == 0 and idx not in [0, 180]:
                        tx_in, ty_in = cx + (r_in+15)*cos_a, cy - (r_in+15)*sin_a
                        svg_sol += f'<text x="{tx_in}" y="{ty_in+3}" font-family="sans-serif" font-size="9" fill="#7f8c8d" text-anchor="middle" opacity="0.8">{idx}</text>'

                # วาดแขนของมุมตามองศาเป้าหมาย
                rad = math.radians(target_deg)
                end_x, end_y = cx + 180 * math.cos(rad), cy - 180 * math.sin(rad)
                svg_sol += f'<line x1="{cx}" y1="{cy}" x2="{cx+180}" y2="{cy}" stroke="#34495e" stroke-width="2.5"/>'
                
                # 🎯 ปรับลดขนาดเส้นสีแดงลงเหลือ 1.5 
                svg_sol += f'<line x1="{cx}" y1="{cy}" x2="{end_x}" y2="{end_y}" stroke="#e74c3c" stroke-width="1.5" stroke-linecap="round"/>'
                svg_sol += f'<circle cx="{cx}" cy="{cy}" r="4" fill="#2c3e50"/><circle cx="{cx+180}" cy="{cy}" r="3" fill="#2c3e50"/><circle cx="{end_x}" cy="{end_y}" r="4" fill="#e74c3c"/>'
                
                # ใส่ตัวอักษรกำกับจุด
                svg_sol += f'<text x="{cx-5}" y="{cy+20}" font-family="sans-serif" font-size="18" font-weight="bold" fill="#2c3e50" text-anchor="middle">{v}</text>'
                svg_sol += f'<text x="{cx+195}" y="{cy+5}" font-family="sans-serif" font-size="18" font-weight="bold" fill="#2c3e50" text-anchor="middle">{p2}</text>'
                tx_p1, ty_p1 = cx + 200 * math.cos(rad), cy - 200 * math.sin(rad)
                svg_sol += f'<text x="{tx_p1}" y="{ty_p1+5}" font-family="sans-serif" font-size="18" font-weight="bold" fill="#e74c3c" text-anchor="middle">{p1}</text>'
                
                # วาดเส้นโค้งระบุมุม
                arc_r = 45
                arc_end_x, arc_end_y = cx + arc_r * math.cos(rad), cy - arc_r * math.sin(rad)
                large_arc = 1 if target_deg > 180 else 0
                svg_sol += f'<path d="M {cx+arc_r} {cy} A {arc_r} {arc_r} 0 {large_arc} 0 {arc_end_x} {arc_end_y}" fill="none" stroke="#27ae60" stroke-width="2.5"/>'
                text_r = 70
                text_x, text_y = cx + text_r * math.cos(rad/2), cy - text_r * math.sin(rad/2)
                svg_sol += f'<text x="{text_x}" y="{text_y+5}" font-family="Sarabun" font-size="16" font-weight="bold" fill="#27ae60" text-anchor="middle">{target_deg}°</text>'
                
                svg_sol += '</svg></div>'

                q = f"จงใช้ไม้โปรแทรกเตอร์สร้างมุม <b>{angle_name_display}</b> ให้มีขนาด <b>{target_deg} องศา</b> พร้อมระบุชนิดของมุม<br>{svg}"
                a_type = "มุมแหลม" if target_deg < 90 else "มุมฉาก" if target_deg == 90 else "มุมป้าน"
                sol = f"<span style='color:#2c3e50;'><b>เฉลย:</b> สร้างมุมกาง {target_deg}° (จัดเป็น <b>{a_type}</b>)<br>{svg_sol}</span>"



            elif actual_sub_t == "การหาความยาวรอบรูปสี่เหลี่ยมมุมฉาก":
                is_square = random.choice([True, False])
                units = random.choice(["ซม.", "ม.", "มม.", "นิ้ว", "วา"])
                
                # ฟังก์ชันวาดสี่เหลี่ยมสไตล์ข้อสอบ (ขยาย Canvas ป้องกันข้อความแหว่ง)
                def draw_exam_rect(w_real, h_real, w_text, h_text, is_sq):
                    # 🛠️ ขยายขนาด Canvas ให้กว้างและสูงขึ้น (450x250)
                    svg_w, svg_h = 450, 250
                    draw_w = 160 if is_sq else 240
                    draw_h = 160 if is_sq else 120
                    ox = (svg_w - draw_w) / 2
                    oy = (svg_h - draw_h) / 2
                    
                    svg = f'<svg width="{svg_w}" height="{svg_h}">'
                    # วาดรูปสี่เหลี่ยม
                    svg += f'<rect x="{ox}" y="{oy}" width="{draw_w}" height="{draw_h}" fill="#fcfcfc" stroke="#2c3e50" stroke-width="2.5"/>'
                    
                    # วาดสัญลักษณ์มุมฉาก 4 มุม
                    s = 12 # ขนาดสัญลักษณ์มุมฉาก
                    svg += f'<polyline points="{ox},{oy+s} {ox+s},{oy+s} {ox+s},{oy}" fill="none" stroke="#2c3e50" stroke-width="1.5"/>'
                    svg += f'<polyline points="{ox+draw_w-s},{oy} {ox+draw_w-s},{oy+s} {ox+draw_w},{oy+s}" fill="none" stroke="#2c3e50" stroke-width="1.5"/>'
                    svg += f'<polyline points="{ox},{oy+draw_h-s} {ox+s},{oy+draw_h-s} {ox+s},{oy+draw_h}" fill="none" stroke="#2c3e50" stroke-width="1.5"/>'
                    svg += f'<polyline points="{ox+draw_w-s},{oy+draw_h} {ox+draw_w-s},{oy+draw_h-s} {ox+draw_w},{oy+draw_h-s}" fill="none" stroke="#2c3e50" stroke-width="1.5"/>'
                    
                    # ขีดแสดงความยาวด้านเท่ากัน
                    tick_len = 8
                    mid_top_x, mid_top_y = ox + draw_w/2, oy
                    mid_bot_x, mid_bot_y = ox + draw_w/2, oy + draw_h
                    mid_l_x, mid_l_y = ox, oy + draw_h/2
                    mid_r_x, mid_r_y = ox + draw_w, oy + draw_h/2
                    
                    if is_sq:
                        # 1 ขีด ทุกด้าน (สีแดง)
                        svg += f'<line x1="{mid_top_x}" y1="{mid_top_y-tick_len}" x2="{mid_top_x}" y2="{mid_top_y+tick_len}" stroke="#e74c3c" stroke-width="2"/>'
                        svg += f'<line x1="{mid_bot_x}" y1="{mid_bot_y-tick_len}" x2="{mid_bot_x}" y2="{mid_bot_y+tick_len}" stroke="#e74c3c" stroke-width="2"/>'
                        svg += f'<line x1="{mid_l_x-tick_len}" y1="{mid_l_y}" x2="{mid_l_x+tick_len}" y2="{mid_l_y}" stroke="#e74c3c" stroke-width="2"/>'
                        svg += f'<line x1="{mid_r_x-tick_len}" y1="{mid_r_y}" x2="{mid_r_x+tick_len}" y2="{mid_r_y}" stroke="#e74c3c" stroke-width="2"/>'
                    else:
                        # 1 ขีดด้านกว้าง(น้ำเงิน), 2 ขีดด้านยาว(แดง) แนวนอนคือด้านยาว
                        svg += f'<line x1="{mid_top_x-4}" y1="{mid_top_y-tick_len}" x2="{mid_top_x-4}" y2="{mid_top_y+tick_len}" stroke="#e74c3c" stroke-width="2"/>'
                        svg += f'<line x1="{mid_top_x+4}" y1="{mid_top_y-tick_len}" x2="{mid_top_x+4}" y2="{mid_top_y+tick_len}" stroke="#e74c3c" stroke-width="2"/>'
                        
                        svg += f'<line x1="{mid_bot_x-4}" y1="{mid_bot_y-tick_len}" x2="{mid_bot_x-4}" y2="{mid_bot_y+tick_len}" stroke="#e74c3c" stroke-width="2"/>'
                        svg += f'<line x1="{mid_bot_x+4}" y1="{mid_bot_y-tick_len}" x2="{mid_bot_x+4}" y2="{mid_bot_y+tick_len}" stroke="#e74c3c" stroke-width="2"/>'
                        
                        svg += f'<line x1="{mid_l_x-tick_len}" y1="{mid_l_y}" x2="{mid_l_x+tick_len}" y2="{mid_l_y}" stroke="#3498db" stroke-width="2"/>'
                        svg += f'<line x1="{mid_r_x-tick_len}" y1="{mid_r_y}" x2="{mid_r_x+tick_len}" y2="{mid_r_y}" stroke="#3498db" stroke-width="2"/>'

                    # ข้อความกำกับความยาว (ขยับออกห่างกรอบนิดหน่อย และขยาย Canvas ทำให้ตัวหนังสือไม่แหว่ง)
                    svg += f'<text x="{mid_bot_x}" y="{mid_bot_y + 30}" font-family="Sarabun" font-size="18" font-weight="bold" fill="#2c3e50" text-anchor="middle">{w_text}</text>'
                    svg += f'<text x="{mid_r_x + 15}" y="{mid_r_y + 6}" font-family="Sarabun" font-size="18" font-weight="bold" fill="#2c3e50" text-anchor="start">{h_text}</text>'
                    
                    svg += '</svg>'
                    
                    return f'''<div style="display:flex; justify-content:center; margin: 20px 0;">
                        <div style="border: 1px solid #bdc3c7; border-radius: 8px; padding: 20px; background-color: #fdfefe; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);">
                            {svg}
                        </div>
                    </div>'''

                if is_square:
                    side = random.randint(12, 145)
                    peri = 4 * side
                    svg = draw_exam_rect(side, side, f"{side} {units}", f"{side} {units}", is_sq=True)
                    q = f"พิจารณารูป<b>สี่เหลี่ยมจัตุรัส</b>ที่กำหนดให้ จงหาความยาวรอบรูปทั้งหมด<br>{svg}"
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    <div style='background-color:#fcf3cf; border-left:4px solid #f1c40f; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    💡 <b>สูตร:</b> ความยาวรอบรูปสี่เหลี่ยมจัตุรัส = <b>4 × ความยาวด้าน</b>
                    </div>
                    <b>วิธีทำอย่างละเอียด:</b><br>
                    👉 <i>(<b>วิเคราะห์:</b> สัญลักษณ์ 1 ขีดสีแดงบนทุกด้าน บ่งบอกว่าเป็นสี่เหลี่ยมจัตุรัสที่มีด้านยาวเท่ากันทั้งหมด 4 ด้าน แทนที่จะนำมาบวกทีละด้าน เราจึงรวบใช้การคูณ 4 แทนได้เลย)</i><br>
                    👉 จากรูป ความยาวแต่ละด้าน = <b>{side} {units}</b><br>
                    👉 แทนค่าลงในสูตร: 4 × {side} = <b>{peri:,}</b><br><br>
                    <b>ตอบ: ความยาวรอบรูปคือ {peri:,} {units}</b></span>"""
                else:
                    w = random.randint(15, 85)
                    h = w + random.randint(12, 60)
                    # สลับแกนให้กว้าง-ยาวสุ่มไปมาบ้าง
                    if random.choice([True, False]):
                        w, h = h, w
                        
                    peri = 2 * (w + h)
                    # กำหนดให้วาดด้านยาวเป็นแกนนอนเสมอเพื่อความสวยงามสมมาตร
                    if w > h:
                        svg = draw_exam_rect(w, h, f"{w} {units}", f"{h} {units}", is_sq=False)
                    else:
                        svg = draw_exam_rect(h, w, f"{h} {units}", f"{w} {units}", is_sq=False)
                        
                    q = f"พิจารณารูป<b>สี่เหลี่ยมผืนผ้า</b>ที่กำหนดให้ จงหาความยาวรอบรูปทั้งหมด<br>{svg}"
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    <div style='background-color:#ebf5fb; border-left:4px solid #3498db; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    💡 <b>สูตร:</b> ความยาวรอบรูปสี่เหลี่ยมผืนผ้า = <b>2 × (กว้าง + ยาว)</b>
                    </div>
                    <b>วิธีทำอย่างละเอียด:</b><br>
                    👉 <i>(<b>วิเคราะห์:</b> สี่เหลี่ยมผืนผ้ามีด้านกว้างยาวเท่ากัน 2 ด้าน (ขีดสีน้ำเงิน) และด้านยาวเท่ากัน 2 ด้าน (ขีดสีแดง) เราจึงนำด้านกว้าง 1 ด้านมารวมกับด้านยาว 1 ด้านให้เป็น 1 ชุดก่อน แล้วค่อยคูณ 2 เพื่อให้ครบทั้ง 4 ด้าน)</i><br>
                    👉 จากรูป ด้านที่ 1 = <b>{min(w,h)} {units}</b> และ ด้านที่ 2 = <b>{max(w,h)} {units}</b><br>
                    👉 นำมาบวกกันก่อน: {min(w,h)} + {max(w,h)} = <b>{w+h}</b><br>
                    👉 นำผลบวกไปคูณ 2: 2 × {w+h} = <b>{peri:,}</b><br><br>
                    <b>ตอบ: ความยาวรอบรูปคือ {peri:,} {units}</b></span>"""



            elif actual_sub_t == "การหาความยาวรอบรูปสามเหลี่ยม":
                unit = random.choice(["ซม.", "ม.", "วา"])
                # สุ่มโหมดของสามเหลี่ยม (4 แบบ)
                tri_mode = random.choice(["equilateral", "isosceles", "scalene", "right_angled"])
                
                if tri_mode == "right_angled":
                    # --- สามเหลี่ยมมุมฉาก ---
                    a, b = random.randint(3, 12)*10, random.randint(3, 12)*10
                    c = int(math.hypot(a, b))
                    peri = a + b + c
                    svg = draw_p4_triangle_perimeter_svg("right_angled", [a, b, c], unit)
                    q = f"พิจารณารูป<b>สามเหลี่ยมมุมฉาก</b>ที่กำหนดให้ จงหาความยาวรอบรูปทั้งหมด<br>{svg}"
                    sol = f"""<span style='color:#2c3e50;'>
                    <b>วิธีทำอย่างละเอียด:</b><br>
                    👉 <i>(วิเคราะห์: สัญลักษณ์มุมฉากที่มุมด้านล่าง บอกว่าเป็นสามเหลี่ยมมุมฉาก)</i><br>
                    👉 นำความยาวทั้ง 3 ด้านมาบวกกัน: {a} + {b} + {c} = <b>{peri} {unit}</b><br><br>
                    <b>ตอบ: ความยาวรอบรูปคือ {peri} {unit}</b></span>"""
                
                elif tri_mode == "equilateral":
                    # --- สามเหลี่ยมด้านเท่า ---
                    side = random.randint(15, 120)
                    peri = side * 3
                    svg = draw_p4_triangle_perimeter_svg("equilateral", [side], unit)
                    q = f"รูปสามเหลี่ยมที่กำหนดให้เป็น<b>รูปสามเหลี่ยมด้านเท่า</b> (มีสัญลักษณ์ขีดบอกความยาวเท่ากันทุกด้าน) จงหาความยาวรอบรูป<br>{svg}"
                    sol = f"""<span style='color:#2c3e50;'>
                    <div style='background-color:#fef8eb; border-left:4px solid #f39c12; padding:15px; margin-bottom:15px; border-radius:8px;'>
                    💡 <b>สมบัติของสามเหลี่ยมด้านเท่า:</b> ด้านทั้ง 3 ด้านยาวเท่ากันเสมอ
                    </div>
                    <b>วิธีทำอย่างละเอียด:</b><br>
                    👉 นำความยาวด้านคูณด้วย 3: {side} × 3 = <b>{peri} {unit}</b><br><br>
                    <b>ตอบ: ความยาวรอบรูปคือ {peri} {unit}</b></span>"""
                
                elif tri_mode == "isosceles":
                    # --- สามเหลี่ยมหน้าจั่ว ---
                    base = random.randint(20, 90)
                    leg = random.randint(50, 140)
                    peri = base + (leg * 2)
                    svg = draw_p4_triangle_perimeter_svg("isosceles", [base, leg], unit)
                    q = f"รูปสามเหลี่ยมที่กำหนดให้มีด้านยาวเท่ากันสองด้าน (สัญลักษณ์ขีดสีแดง) จงหาความยาวรอบรูป<br>{svg}"
                    sol = f"""<span style='color:#2c3e50;'>
                    <b>วิธีทำอย่างละเอียด:</b><br>
                    👉 ด้านที่ยาวเท่ากันมี 2 ด้าน คือด้านละ {leg} {unit}<br>
                    👉 รวมกับฐาน {base} {unit} ➔ {base} + {leg} + {leg} = <b>{peri} {unit}</b><br><br>
                    <b>ตอบ: ความยาวรอบรูปคือ {peri} {unit}</b></span>"""
                
                else: # scalene (ด้านไม่เท่า)
                    s1, s2, s3 = random.randint(30, 60), random.randint(40, 70), random.randint(50, 80)
                    peri = s1 + s2 + s3
                    svg = draw_p4_triangle_perimeter_svg("scalene", [s1, s2, s3], unit)
                    q = f"จงหาความยาวรอบรูปของรูปสามเหลี่ยมที่มีความยาวแต่ละด้านตามที่กำหนดให้<br>{svg}"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b> {s1} + {s2} + {s3} = <b>{peri} {unit}</b></span>"



            elif actual_sub_t == "การหาความยาวรอบรูปสี่เหลี่ยมด้านขนานและขนมเปียกปูน":
                unit = random.choice(["ซม.", "ม.", "วา"])
                # สุ่มเลือกระหว่าง ด้านขนาน หรือ ขนมเปียกปูน
                mode = random.choice(["parallelogram", "rhombus"])
                
                if mode == "rhombus":
                    side = random.randint(15, 120)
                    peri = side * 4
                    svg = draw_p4_parallelogram_rhombus_svg("rhombus", [side], unit)
                    q = f"รูปสี่เหลี่ยมที่กำหนดให้เป็น<b>รูปสี่เหลี่ยมขนมเปียกปูน</b> (มีสัญลักษณ์ขีดบอกความยาวเท่ากันทุกด้าน) จงหาความยาวรอบรูปทั้งหมด<br>{svg}"
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    <div style='background-color:#fef8eb; border-left:4px solid #f39c12; padding:15px; margin-bottom:15px; border-radius:8px;'>
                    💡 <b>สมบัติของสี่เหลี่ยมขนมเปียกปูน:</b><br>
                    รูปสี่เหลี่ยมที่มีสัญลักษณ์ 1 ขีดสีแดงเหมือนกันทุกด้านแบบนี้ คือสี่เหลี่ยมขนมเปียกปูน ซึ่งจะมี <b>ด้านทั้ง 4 ด้านยาวเท่ากันเสมอ</b> ครับ
                    </div>
                    <b>วิธีทำอย่างละเอียด Step-by-Step:</b><br>
                    👉 <b>ขั้นที่ 1:</b> ระบุความยาวด้านละ {side} {unit}<br>
                    👉 <b>ขั้นที่ 2:</b> เนื่องจากมี 4 ด้านที่ยาวเท่ากัน สามารถคำนวณโดยใช้การคูณ 4 ➔ {side} × 4<br>
                    👉 <b>ขั้นที่ 3:</b> หาผลลัพธ์ ➔ {side} × 4 = <b>{peri} {unit}</b><br><br>
                    <b>ตอบ: ความยาวรอบรูปของรูปสี่เหลี่ยมขนมเปียกปูนคือ {peri} {unit}</b></span>"""
                
                else: # parallelogram
                    base = random.randint(40, 150)
                    side_slope = random.randint(20, 80)
                    peri = (base + side_slope) * 2
                    svg = draw_p4_parallelogram_rhombus_svg("parallelogram", [base, side_slope], unit)
                    q = f"พิจารณารูป<b>สี่เหลี่ยมด้านขนาน</b>ที่กำหนดให้ (ด้านที่อยู่ตรงข้ามกันมีขนาดเท่ากัน) จงหาความยาวรอบรูปทั้งหมด<br>{svg}"
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    <div style='background-color:#ebf5fb; border-left:4px solid #3498db; padding:15px; margin-bottom:15px; border-radius:8px;'>
                    💡 <b>สมบัติของสี่เหลี่ยมด้านขนาน:</b><br>
                    ด้านที่อยู่ตรงข้ามกันจะมีความยาวเท่ากันเสมอ (สังเกตจากสัญลักษณ์ขีดที่มีสีและจำนวนเหมือนกัน)
                    </div>
                    <b>วิธีทำอย่างละเอียด Step-by-Step:</b><br>
                    👉 <b>ขั้นที่ 1:</b> รวมความยาวด้านคู่ที่ 1 (บน+ล่าง) ➔ {base} + {base} = {base*2} {unit}<br>
                    👉 <b>ขั้นที่ 2:</b> รวมความยาวด้านคู่ที่ 2 (ซ้าย+ขวา) ➔ {side_slope} + {side_slope} = {side_slope*2} {unit}<br>
                    👉 <b>ขั้นที่ 3:</b> นำผลรวมทั้งสองคู่มาบวกกัน ➔ {base*2} + {side_slope*2} = <b>{peri} {unit}</b><br>
                    <i>(หรือใช้สูตร 2 × (กว้าง + ยาว) ➔ 2 × ({base} + {side_slope}) = <b>{peri}</b>)</i><br><br>
                    <b>ตอบ: ความยาวรอบรูปของรูปสี่เหลี่ยมด้านขนานคือ {peri} {unit}</b></span>"""


            elif actual_sub_t == "การหาความยาวรอบรูปสี่เหลี่ยมรูปว่าว":
                unit = random.choice(["ซม.", "ม.", "นิ้ว", "วา"])
                
                # สุ่มความยาวด้าน โดยบังคับให้ด้านล่างยาวกว่าด้านบนเสมอ
                s1 = random.randint(15, 60)
                s2 = random.randint(s1 + 10, s1 + 80)
                peri = 2 * (s1 + s2)
                
                svg = draw_p4_kite_svg([s1, s2], unit)
                q = f"รูปสี่เหลี่ยมที่กำหนดให้เป็น<b>รูปสี่เหลี่ยมรูปว่าว</b> (ด้านประชิดยาวเท่ากัน 2 คู่) จงหาความยาวรอบรูปทั้งหมด<br>{svg}"
                
                sol = f"""<span style='color:#2c3e50;'>
                <div style='background-color:#fef8eb; border-left:4px solid #f39c12; padding:15px; margin-bottom:15px; border-radius:8px;'>
                💡 <b>สมบัติของสี่เหลี่ยมรูปว่าว:</b><br>
                ด้านที่อยู่ติดกัน (ประชิดกัน) จะมีความยาวเท่ากัน 2 คู่เสมอ<br>
                <i>(สังเกตจากสัญลักษณ์ 1 ขีดคู่บน และ 2 ขีดคู่ล่าง)</i>
                </div>
                <b>วิธีทำอย่างละเอียด Step-by-Step:</b><br>
                👉 <b>ขั้นที่ 1:</b> คู่ที่ 1 (ด้านบน) มี 2 ด้าน ยาวด้านละ {s1} {unit} ➔ รวมเป็น {s1} + {s1} = {s1*2} {unit}<br>
                👉 <b>ขั้นที่ 2:</b> คู่ที่ 2 (ด้านล่าง) มี 2 ด้าน ยาวด้านละ {s2} {unit} ➔ รวมเป็น {s2} + {s2} = {s2*2} {unit}<br>
                👉 <b>ขั้นที่ 3:</b> นำความยาวทั้ง 4 ด้านมารวมกัน ➔ {s1*2} + {s2*2} = <b>{peri} {unit}</b><br>
                <i>(หรือคำนวณจากสูตร: 2 × (ความยาวด้านสั้น + ความยาวด้านยาว) ➔ 2 × ({s1} + {s2}) = <b>{peri}</b>)</i><br><br>
                <b>ตอบ: ความยาวรอบรูปของรูปสี่เหลี่ยมรูปว่าวนี้คือ {peri} {unit}</b></span>"""



            elif actual_sub_t == "การหาพื้นที่รูปสี่เหลี่ยมมุมฉาก":
                is_square = random.choice([True, False])
                if is_square:
                    side = random.randint(5, 25)
                    area = side * side
                    svg = draw_rect_svg(side, side, f"{side} ม.", f"{side} ม.", "#fdf2e9")
                    q = f"จงหาพื้นที่ของ<b>สี่เหลี่ยมจัตุรัส</b>ต่อไปนี้<br>{svg}"
                    
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>
                    👉 <b>สูตร:</b> พื้นที่สี่เหลี่ยมจัตุรัส = <b>ความยาวด้าน × ความยาวด้าน</b><br>
                    👉 <i>(<b>อธิบาย:</b> การหาพื้นที่คือการคำนวณขนาดของพื้นผิวที่อยู่ "ด้านใน" ของรูป เนื่องจากสี่เหลี่ยมจัตุรัสมีด้านทุกด้านยาวเท่ากัน เราจึงนำขนาดของด้านมาคูณกันเองได้เลย)</i><br>
                    👉 จากรูป ความยาวด้านแต่ละด้าน = {side} ม.<br>
                    👉 แทนค่าลงในสูตร: {side} × {side} = <b>{area:,}</b><br>
                    👉 <i>(<b>ข้อควรจำ:</b> หน่วยของการหาพื้นที่ต้องขึ้นต้นด้วยคำว่า "ตาราง" เสมอ)</i><br>
                    <b>ตอบ: {area:,} ตารางเมตร</b></span>"""
                else:
                    w, h = random.randint(4, 15), random.randint(16, 30)
                    area = w * h
                    svg = draw_rect_svg(h, w, f"{h} ซม.", f"{w} ซม.", "#e8f8f5")
                    q = f"จงหาพื้นที่ของ<b>สี่เหลี่ยมผืนผ้า</b>ต่อไปนี้<br>{svg}"
                    
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>
                    👉 <b>สูตร:</b> พื้นที่สี่เหลี่ยมผืนผ้า = <b>ความกว้าง × ความยาว</b><br>
                    👉 <i>(<b>อธิบาย:</b> การหาพื้นที่คือการคำนวณขนาดของพื้นผิวที่อยู่ "ด้านใน" รูป โดยนำความยาวของด้านที่สั้นกว่า (ความกว้าง) มาคูณกับด้านที่ยาวกว่า (ความยาว))</i><br>
                    👉 จากรูป ด้านกว้าง = {w} ซม. และ ด้านยาว = {h} ซม.<br>
                    👉 แทนค่าลงในสูตร: {w} × {h} = <b>{area:,}</b><br>
                    👉 <i>(<b>ข้อควรจำ:</b> หน่วยของการหาพื้นที่ต้องขึ้นต้นด้วยคำว่า "ตาราง" เสมอ)</i><br>
                    <b>ตอบ: {area:,} ตารางเซนติเมตร</b></span>"""



            elif actual_sub_t == "แปลงเศษเกินเป็นจำนวนคละ":
                # สุ่มเลขเศษเกิน
                den = random.randint(3, 12)
                whole = random.randint(1, 9)
                rem = random.randint(1, den - 1)
                num = (whole * den) + rem
                
                def draw_frac(n, d):
                    return f"<span style='display:inline-flex; flex-direction:column; vertical-align:middle; text-align:center; margin:0 4px; font-weight:bold;'><span style='border-bottom:2px solid #333; padding:0 3px;'>{n}</span><span>{d}</span></span>"

                q = f"จงแปลงเศษเกินต่อไปนี้ให้เป็นจำนวนคละ: <b>{draw_frac(num, den)}</b>"
                
                sol = f"""<span style='color:#2c3e50;'>
                <div style='background-color:#fcf3cf; border-left:4px solid #f1c40f; padding:10px; margin-bottom:15px; border-radius:4px;'>
                💡 <b>หลักการคิด:</b><br>
                นำตัวเศษ (เลขบน) ตั้ง แล้วหารด้วยตัวส่วน (เลขล่าง)<br>
                • <b>ผลหาร</b> จะกลายเป็น <b>"เลขจำนวนเต็มด้านหน้า"</b><br>
                • <b>เศษที่เหลือ</b> จะกลายเป็น <b>"ตัวเศษด้านบน"</b><br>
                • <b>ตัวส่วน</b> จะยังคง <b>"เป็นเลขเดิมเสมอ"</b>
                </div>
                <b>วิธีทำอย่างละเอียด:</b><br>
                👉 <b>ขั้นที่ 1: ตั้งหาร</b><br>
                &nbsp;&nbsp;&nbsp;&nbsp;{num} ÷ {den} = ?<br>
                &nbsp;&nbsp;&nbsp;&nbsp;💡 <i>ท่องแม่ {den}: {den} × <b style='color:#e67e22;'>{whole}</b> = {whole*den} (เหลือเศษ <b style='color:#e74c3c;'>{rem}</b>)</i><br><br>
                👉 <b>ขั้นที่ 2: นำมาเขียนในรูปจำนวนคละ</b><br>
                &nbsp;&nbsp;&nbsp;&nbsp;• เลขจำนวนเต็มคือ <b style='color:#e67e22;'>{whole}</b><br>
                &nbsp;&nbsp;&nbsp;&nbsp;• ตัวเศษใหม่คือ <b style='color:#e74c3c;'>{rem}</b><br>
                &nbsp;&nbsp;&nbsp;&nbsp;• ตัวส่วนคงเดิมคือ <b>{den}</b><br><br>
                <b>ตอบ: <span style='font-size:20px;'><b style='color:#e67e22;'>{whole}</b>{draw_frac(f"<b style='color:#e74c3c;'>{rem}</b>", den)}</span></b></span>"""



            elif actual_sub_t == "การอ่านและการเขียนทศนิยม":
                # สุ่มทศนิยม 2 หรือ 3 ตำแหน่ง
                val = round(random.uniform(10.01, 99.999), random.choice([2, 3]))
                val_str = f"{val:.3f}" if len(str(val).split('.')[1]) == 3 else f"{val:.2f}"
                
                # แยกหลักต่างๆ
                whole_part, dec_part = val_str.split('.')
                
                q = f"ให้นักเรียนเขียนคำอ่าน และเขียนในรูปกระจายของทศนิยมต่อไปนี้: <b>{val_str}</b>"
                
                # ฟังก์ชันเขียนคำอ่าน (แบบย่อสำหรับระบบสุ่ม)
                reading_map = {"0":"ศูนย์", "1":"หนึ่ง", "2":"สอง", "3":"สาม", "4":"สี่", "5":"ห้า", "6":"หก", "7":"เจ็ด", "8":"แปด", "9":"เก้า"}
                read_whole = "".join([reading_map[d] for d in whole_part])
                
                sol = f"""<span style='color:#2c3e50;'>
                <div style='background-color:#e8f8f5; border-left:4px solid #1abc9c; padding:10px; margin-bottom:15px; border-radius:4px;'>
                🔍 <b>วิเคราะห์ค่าประจำหลักของ {val_str}:</b><br>
                • หน้าจุด: <b>{whole_part}</b> คือจำนวนเต็ม<br>
                • หลังจุดตัวที่ 1: คือ <b>หลักส่วนสิบ</b> (1/10)<br>
                • หลังจุดตัวที่ 2: คือ <b>หลักส่วนร้อย</b> (1/100)<br>
                • หลังจุดตัวที่ 3 (ถ้ามี): คือ <b>หลักส่วนพัน</b> (1/1000)
                </div>
                <b>คำตอบอย่างละเอียด:</b><br>
                👉 <b>1. คำอ่าน:</b><br>
                &nbsp;&nbsp;&nbsp;&nbsp;อ่านว่า: (เขียนตามตัวเลขทีละตัวหลังจุดทศนิยม)<br><br>
                👉 <b>2. เขียนในรูปกระจาย:</b><br>
                &nbsp;&nbsp;&nbsp;&nbsp;{whole_part[0]}0 + {whole_part[1]} + 0.{dec_part[0]} + 0.0{dec_part[1]} {"+ 0.00" + dec_part[2] if len(dec_part)==3 else ""}<br><br>
                💡 <i>หมายเหตุ: การกระจายช่วยให้เราเข้าใจว่าเลขแต่ละตัวมีค่าเท่าไหร่ตามตำแหน่งของมัน</i></span>"""



            elif actual_sub_t == "การบวกเศษส่วน":
                
                # สุ่มรูปแบบโจทย์ (1: วงกลมแบ่งส่วน, 2: แถบสี่เหลี่ยม, 3: ตารางเงื่อนไข)
                prob_style = random.choice([1, 2, 3])
                
                # ฟังก์ชันช่วยวาดตัวเลขเศษส่วน
                def draw_frac(n, d):
                    return f"<span style='display:inline-flex; flex-direction:column; vertical-align:middle; text-align:center; margin:0 4px; font-weight:bold; font-size:18px;'><span style='border-bottom:2px solid #2c3e50; padding:0 3px;'>{n}</span><span style='padding:0 3px;'>{d}</span></span>"
                
                # ฟังก์ชันวาดวงกลมเศษส่วน (มีเส้นแบ่งส่วนชัดเจน)
                def draw_svg_pie(n, d, color="#2ecc71"):
                    if d == 1 or n == d:
                        return f'<svg width="80" height="80" viewBox="0 0 80 80"><circle cx="40" cy="40" r="38" fill="{color}" stroke="#2c3e50" stroke-width="2"/></svg>'
                    if n == 0:
                        return f'<svg width="80" height="80" viewBox="0 0 80 80"><circle cx="40" cy="40" r="38" fill="#ecf0f1" stroke="#2c3e50" stroke-width="2"/></svg>'
                    
                    svg = '<svg width="80" height="80" viewBox="0 0 80 80">'
                    svg += '<circle cx="40" cy="40" r="38" fill="#ecf0f1" stroke="#2c3e50" stroke-width="2"/>'
                    for i in range(d):
                        start_a = i * (360 / d)
                        end_a = (i + 1) * (360 / d)
                        r1 = math.radians(start_a - 90)
                        r2 = math.radians(end_a - 90)
                        x1 = 40 + 38 * math.cos(r1)
                        y1 = 40 + 38 * math.sin(r1)
                        x2 = 40 + 38 * math.cos(r2)
                        y2 = 40 + 38 * math.sin(r2)
                        fill = color if i < n else "none"
                        la = 1 if (end_a - start_a) > 180 else 0
                        # วาดชิ้นส่วนแต่ละชิ้นพร้อมเส้นขอบ
                        svg += f'<path d="M 40 40 L {x1} {y1} A 38 38 0 {la} 1 {x2} {y2} Z" fill="{fill}" stroke="#2c3e50" stroke-width="1.5"/>'
                    svg += '</svg>'
                    return svg

                # ฟังก์ชันวาดแถบสี่เหลี่ยมเศษส่วน (มีเส้นแบ่งช่องชัดเจน)
                def draw_svg_rect(n, d, color="#9b59b6"):
                    svg = f'<svg width="120" height="40" viewBox="0 0 120 40">'
                    w = 120 / d
                    for i in range(d):
                        fill = color if i < n else "#ecf0f1"
                        svg += f'<rect x="{i*w}" y="0" width="{w}" height="40" fill="{fill}" stroke="#2c3e50" stroke-width="1.5"/>'
                    svg += '</svg>'
                    return svg

                if prob_style == 1:
                    # แบบที่ 1: แผนภาพวงกลม (ตัวส่วนเท่ากัน)
                    d = random.choice([4, 6, 8, 10, 12])
                    n1 = random.randint(1, d-1)
                    n2 = random.randint(1, d-1)
                    
                    q_html = f"""
                    <div style="display: flex; justify-content: center; align-items: center; gap: 20px; padding: 25px; background: #fdfefe; border-radius: 12px; border: 2px dashed #95a5a6; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); margin: 15px 0;">
                        <div style="text-align:center;">{draw_svg_pie(n1, d, "#3498db")}<br><b style="color:#3498db;">รูปที่ 1</b></div>
                        <div style="font-size: 35px; font-weight: bold; color: #e74c3c;">+</div>
                        <div style="text-align:center;">{draw_svg_pie(n2, d, "#e67e22")}<br><b style="color:#e67e22;">รูปที่ 2</b></div>
                        <div style="font-size: 35px; font-weight: bold; color: #2c3e50;">= &nbsp;?</div>
                    </div>
                    """
                    q = f"จากภาพวงกลมที่ถูกแบ่งเป็นส่วนเท่าๆ กัน ถ้านำส่วนที่ระบายสีมารวมกัน จะเขียนเป็นเศษส่วนได้อย่างไร?<br>{q_html}"
                    
                    sum_n = n1 + n2
                    gcd_v = math.gcd(sum_n, d)
                    ans_n, ans_d = sum_n // gcd_v, d // gcd_v
                    ans_text = str(ans_n) if ans_d == 1 else draw_frac(ans_n, ans_d)
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    <div style='background-color:#ebf5fb; border-left:4px solid #3498db; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    🔍 <b>วิเคราะห์จากภาพ:</b><br>
                    • วงกลมถูกแบ่งออกเป็น <b>{d} ส่วน</b> เท่าๆ กัน (ตัวส่วนคือ {d})<br>
                    • <b style="color:#3498db;">รูปที่ 1</b> ระบายสีไป {n1} ส่วน เขียนเป็นเศษส่วนได้ {draw_frac(n1, d)}<br>
                    • <b style="color:#e67e22;">รูปที่ 2</b> ระบายสีไป {n2} ส่วน เขียนเป็นเศษส่วนได้ {draw_frac(n2, d)}
                    </div>
                    <b>วิธีทำอย่างละเอียด:</b><br>
                    👉 <b>ขั้นที่ 1: นำเศษส่วนมาบวกกัน</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;💡 <i>เมื่อ "ตัวส่วน" เท่ากันแล้ว ให้นำ "ตัวเศษ" (เลขด้านบน) มาบวกกันได้เลย</i><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;{draw_frac(n1, d)} + {draw_frac(n2, d)} = {draw_frac(f"{n1} + {n2}", d)} = <b>{draw_frac(sum_n, d)}</b><br><br>
                    """
                    if gcd_v > 1:
                        sol += f"""👉 <b>ขั้นที่ 2: ทำให้เป็นเศษส่วนอย่างต่ำ</b><br>
                        &nbsp;&nbsp;&nbsp;&nbsp;นำแม่ <b>{gcd_v}</b> มาหารทั้งเศษและส่วน: {draw_frac(f"{sum_n} ÷ {gcd_v}", f"{d} ÷ {gcd_v}")} = <b>{ans_text}</b><br><br>"""
                    sol += f"<b>ตอบ: {ans_text}</b></span>"

                elif prob_style == 2:
                    # แบบที่ 2: แถบสี่เหลี่ยม (ตัวส่วนไม่เท่ากัน)
                    d1 = random.choice([2, 3, 4])
                    m = random.choice([2, 3])
                    d2 = d1 * m
                    n1 = random.randint(1, d1-1)
                    n2 = random.randint(1, d2-1)
                    
                    q_html = f"""
                    <div style="display: flex; justify-content: center; align-items: center; gap: 15px; padding: 25px; background: #faf8f5; border-radius: 12px; border: 2px solid #dcd1c4; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); margin: 15px 0;">
                        <div style="text-align:center;">{draw_svg_rect(n1, d1, "#1abc9c")}<br><b style="color:#1abc9c;">แถบ A</b></div>
                        <div style="font-size: 35px; font-weight: bold; color: #e74c3c;">+</div>
                        <div style="text-align:center;">{draw_svg_rect(n2, d2, "#9b59b6")}<br><b style="color:#9b59b6;">แถบ B</b></div>
                        <div style="font-size: 35px; font-weight: bold; color: #2c3e50;">= &nbsp;?</div>
                    </div>
                    """
                    q = f"จากแถบเศษส่วนต่อไปนี้ จงหาผลบวกของส่วนที่ระบายสี<br><span style='font-size:14px; color:#e74c3c;'>(⭐ สังเกต: แถบทั้งสองถูกแบ่งเป็นช่องไม่เท่ากัน)</span><br>{q_html}"
                    
                    n1_new = n1 * m
                    sum_n = n1_new + n2
                    gcd_v = math.gcd(sum_n, d2)
                    ans_n, ans_d = sum_n // gcd_v, d2 // gcd_v
                    ans_text = str(ans_n) if ans_d == 1 else draw_frac(ans_n, ans_d)
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    <div style='background-color:#ebf5fb; border-left:4px solid #3498db; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    🔍 <b>วิเคราะห์จากภาพ:</b><br>
                    • <b style="color:#1abc9c;">แถบ A</b> ถูกแบ่ง {d1} ช่อง ระบายสี {n1} ช่อง = {draw_frac(n1, d1)}<br>
                    • <b style="color:#9b59b6;">แถบ B</b> ถูกแบ่ง {d2} ช่อง ระบายสี {n2} ช่อง = {draw_frac(n2, d2)}<br>
                    • จะเห็นว่าขนาดช่องไม่เท่ากัน ต้องทำ <b style="color:#1abc9c;">แถบ A</b> ให้มีช่องเล็กๆ เท่ากับแถบ B ก่อน!
                    </div>
                    <b>วิธีทำอย่างละเอียด:</b><br>
                    👉 <b>ขั้นที่ 1: ทำตัวส่วนให้เท่ากัน</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;นำ <b style='color:#e74c3c;'>{m}</b> มาคูณทั้งเศษและส่วนของ {draw_frac(n1, d1)} เพื่อให้ส่วนกลายเป็น {d2}<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;• {draw_frac(f"{n1} × <b style='color:#e74c3c;'>{m}</b>", f"{d1} × <b style='color:#e74c3c;'>{m}</b>")} = <b style='color:#1abc9c;'>{draw_frac(n1_new, d2)}</b><br><br>
                    👉 <b>ขั้นที่ 2: นำเศษส่วนมาบวกกัน</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;{draw_frac(n1_new, d2)} + {draw_frac(n2, d2)} = {draw_frac(f"{n1_new} + {n2}", d2)} = <b>{draw_frac(sum_n, d2)}</b><br><br>
                    """
                    if gcd_v > 1:
                        sol += f"""👉 <b>ขั้นที่ 3: ทำให้เป็นเศษส่วนอย่างต่ำ</b><br>
                        &nbsp;&nbsp;&nbsp;&nbsp;นำแม่ <b>{gcd_v}</b> มาหารทั้งเศษและส่วน: {draw_frac(f"{sum_n} ÷ {gcd_v}", f"{d2} ÷ {gcd_v}")} = <b>{ans_text}</b><br><br>"""
                    sol += f"<b>ตอบ: {ans_text}</b></span>"

                else:
                    # แบบที่ 3: ตารางสมมาตร (ตัวเลขล้วน ตัวส่วนไม่เท่ากัน)
                    d1 = random.choice([3, 4, 5])
                    n1 = random.randint(1, d1-1)
                    m = random.choice([2, 3, 4])
                    d2 = d1 * m
                    n2 = random.randint(1, d2-1)
                    
                    q_html = f"""
                    <div style="display: flex; justify-content: space-around; gap: 15px; margin: 20px 0;">
                        <div style="flex: 1; border: 3px solid #2980b9; border-radius: 8px; padding: 15px; background: white; text-align: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
                            <b style="color: #2980b9; font-size: 18px;">กล่อง A</b><hr style="border-top: 2px dashed #2980b9;">
                            <div style="font-size: 26px; margin-top:15px; margin-bottom:5px;">{draw_frac(n1, d1)}</div>
                        </div>
                        <div style="flex: 1; border: 3px solid #f39c12; border-radius: 8px; padding: 15px; background: white; text-align: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
                            <b style="color: #f39c12; font-size: 18px;">กล่อง B</b><hr style="border-top: 2px dashed #f39c12;">
                            <div style="font-size: 26px; margin-top:15px; margin-bottom:5px;">{draw_frac(n2, d2)}</div>
                        </div>
                    </div>
                    <div style="text-align: center; background: #e8f8f5; padding: 15px; border-radius: 8px; border: 2px solid #1abc9c; font-size: 22px;">
                        จงหาผลลัพธ์ของ &nbsp; <b>A <span style="color:#e74c3c;">+</span> B</b>
                    </div>
                    """
                    q = f"พิจารณาค่าจากกล่องที่กำหนดให้ แล้วหาคำตอบที่ถูกต้องที่สุด<br>{q_html}"
                    
                    n1_new = n1 * m
                    sum_n = n1_new + n2
                    gcd_v = math.gcd(sum_n, d2)
                    ans_n, ans_d = sum_n // gcd_v, d2 // gcd_v
                    ans_text = str(ans_n) if ans_d == 1 else draw_frac(ans_n, ans_d)
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    <b>วิธีทำอย่างละเอียด:</b><br>
                    👉 <b>ขั้นที่ 1: จัดรูปสมการ</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;นำค่าจากกล่องมาเขียนบวกกัน: {draw_frac(n1, d1)} <b style='color:#e74c3c;'>+</b> {draw_frac(n2, d2)}<br><br>
                    👉 <b>ขั้นที่ 2: ทำตัวส่วนให้เท่ากัน</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;💡 <i>สังเกตว่าตัวส่วนคือ {d1} และ {d2} เราต้องทำ {d1} ให้กลายเป็น {d2} โดยการคูณด้วย {m}</i><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;• {draw_frac(f"{n1} × <b style='color:#e74c3c;'>{m}</b>", f"{d1} × <b style='color:#e74c3c;'>{m}</b>")} = <b style='color:#2980b9;'>{draw_frac(n1_new, d2)}</b><br><br>
                    👉 <b>ขั้นที่ 3: นำเศษส่วนมาบวกกัน</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;{draw_frac(n1_new, d2)} + {draw_frac(n2, d2)} = {draw_frac(f"{n1_new} + {n2}", d2)} = <b>{draw_frac(sum_n, d2)}</b><br><br>
                    """
                    if gcd_v > 1:
                        sol += f"""👉 <b>ขั้นที่ 4: ทำให้เป็นเศษส่วนอย่างต่ำ</b><br>
                        &nbsp;&nbsp;&nbsp;&nbsp;นำแม่ <b>{gcd_v}</b> มาหารทั้งเศษและส่วน: {draw_frac(f"{sum_n} ÷ {gcd_v}", f"{d2} ÷ {gcd_v}")} = <b>{ans_text}</b><br><br>"""
                    sol += f"<b>ตอบ: {ans_text}</b></span>"



            elif actual_sub_t == "การลบเศษส่วน":
                
                # สุ่มรูปแบบโจทย์ (1: วงกลมแบ่งส่วน, 2: แถบสี่เหลี่ยม, 3: ตารางเงื่อนไขสมมาตร)
                prob_style = random.choice([1, 2, 3])
                
                # ฟังก์ชันช่วยวาดตัวเลขเศษส่วน
                def draw_frac(n, d):
                    return f"<span style='display:inline-flex; flex-direction:column; vertical-align:middle; text-align:center; margin:0 4px; font-weight:bold; font-size:18px;'><span style='border-bottom:2px solid #2c3e50; padding:0 3px;'>{n}</span><span style='padding:0 3px;'>{d}</span></span>"
                
                # ฟังก์ชันวาดวงกลมเศษส่วน (มีเส้นแบ่งส่วนชัดเจน)
                def draw_svg_pie(n, d, color="#e74c3c"):
                    if d == 1 or n == d:
                        return f'<svg width="80" height="80" viewBox="0 0 80 80"><circle cx="40" cy="40" r="38" fill="{color}" stroke="#2c3e50" stroke-width="2"/></svg>'
                    if n == 0:
                        return f'<svg width="80" height="80" viewBox="0 0 80 80"><circle cx="40" cy="40" r="38" fill="#ecf0f1" stroke="#2c3e50" stroke-width="2"/></svg>'
                    
                    svg = '<svg width="80" height="80" viewBox="0 0 80 80">'
                    svg += '<circle cx="40" cy="40" r="38" fill="#ecf0f1" stroke="#2c3e50" stroke-width="2"/>'
                    for i in range(d):
                        start_a = i * (360 / d)
                        end_a = (i + 1) * (360 / d)
                        r1 = math.radians(start_a - 90)
                        r2 = math.radians(end_a - 90)
                        x1 = 40 + 38 * math.cos(r1)
                        y1 = 40 + 38 * math.sin(r1)
                        x2 = 40 + 38 * math.cos(r2)
                        y2 = 40 + 38 * math.sin(r2)
                        fill = color if i < n else "none"
                        la = 1 if (end_a - start_a) > 180 else 0
                        svg += f'<path d="M 40 40 L {x1} {y1} A 38 38 0 {la} 1 {x2} {y2} Z" fill="{fill}" stroke="#2c3e50" stroke-width="1.5"/>'
                    svg += '</svg>'
                    return svg

                # ฟังก์ชันวาดแถบสี่เหลี่ยมเศษส่วน
                def draw_svg_rect(n, d, color="#f39c12"):
                    svg = f'<svg width="120" height="40" viewBox="0 0 120 40">'
                    w = 120 / d
                    for i in range(d):
                        fill = color if i < n else "#ecf0f1"
                        svg += f'<rect x="{i*w}" y="0" width="{w}" height="40" fill="{fill}" stroke="#2c3e50" stroke-width="1.5"/>'
                    svg += '</svg>'
                    return svg

                if prob_style == 1:
                    # แบบที่ 1: แผนภาพวงกลม (ตัวส่วนเท่ากัน) ลบกัน
                    d = random.choice([4, 6, 8, 10, 12])
                    n1 = random.randint(2, d-1)
                    n2 = random.randint(1, n1-1) # ให้ n2 น้อยกว่า n1 เสมอ จะได้ลบกันไม่ติดลบ
                    
                    q_html = f"""
                    <div style="display: flex; justify-content: center; align-items: center; gap: 20px; padding: 25px; background: #fdfefe; border-radius: 12px; border: 2px dashed #95a5a6; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); margin: 15px 0;">
                        <div style="text-align:center;">{draw_svg_pie(n1, d, "#3498db")}<br><b style="color:#3498db;">รูปที่ 1 (ตัวตั้ง)</b></div>
                        <div style="font-size: 35px; font-weight: bold; color: #e74c3c;">-</div>
                        <div style="text-align:center;">{draw_svg_pie(n2, d, "#e74c3c")}<br><b style="color:#e74c3c;">รูปที่ 2 (ตัวลบ)</b></div>
                        <div style="font-size: 35px; font-weight: bold; color: #2c3e50;">= &nbsp;?</div>
                    </div>
                    """
                    q = f"จากภาพวงกลมที่ถูกแบ่งเป็นส่วนเท่าๆ กัน ถ้านำส่วนที่ระบายสีมาหักล้างกัน (ลบกัน) จะเขียนเป็นเศษส่วนได้อย่างไร?<br>{q_html}"
                    
                    diff_n = n1 - n2
                    gcd_v = math.gcd(diff_n, d)
                    ans_n, ans_d = diff_n // gcd_v, d // gcd_v
                    ans_text = str(ans_n) if ans_d == 1 else draw_frac(ans_n, ans_d)
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    <div style='background-color:#ebf5fb; border-left:4px solid #3498db; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    🔍 <b>วิเคราะห์จากภาพ:</b><br>
                    • วงกลมถูกแบ่งออกเป็น <b>{d} ส่วน</b> เท่าๆ กัน (ตัวส่วนคือ {d})<br>
                    • <b style="color:#3498db;">รูปที่ 1</b> ระบายสีไป {n1} ส่วน เขียนเป็นเศษส่วนได้ {draw_frac(n1, d)}<br>
                    • <b style="color:#e74c3c;">รูปที่ 2</b> ระบายสีไป {n2} ส่วน เขียนเป็นเศษส่วนได้ {draw_frac(n2, d)}
                    </div>
                    <b>วิธีทำอย่างละเอียด:</b><br>
                    👉 <b>ขั้นที่ 1: นำเศษส่วนมาลบกัน</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;💡 <i>เมื่อ "ตัวส่วน" เท่ากันแล้ว ให้นำ "ตัวเศษ" (เลขด้านบน) มาลบกันได้เลย</i><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;{draw_frac(n1, d)} <b style='color:#e74c3c;'>-</b> {draw_frac(n2, d)} = {draw_frac(f"{n1} - {n2}", d)} = <b>{draw_frac(diff_n, d)}</b><br><br>
                    """
                    if gcd_v > 1:
                        sol += f"""👉 <b>ขั้นที่ 2: ทำให้เป็นเศษส่วนอย่างต่ำ</b><br>
                        &nbsp;&nbsp;&nbsp;&nbsp;นำแม่ <b>{gcd_v}</b> มาหารทั้งเศษและส่วน: {draw_frac(f"{diff_n} ÷ {gcd_v}", f"{d} ÷ {gcd_v}")} = <b>{ans_text}</b><br><br>"""
                    sol += f"<b>ตอบ: {ans_text}</b></span>"

                elif prob_style == 2:
                    # แบบที่ 2: แถบสี่เหลี่ยม (ตัวส่วนไม่เท่ากัน)
                    d1 = random.choice([2, 3, 4])
                    n1 = random.randint(1, d1-1)
                    m = random.choice([2, 3, 4])
                    d2 = d1 * m
                    
                    n1_new = n1 * m # จำนวนช่องถ้าย่อยเป็นชิ้นเล็ก
                    n2 = random.randint(1, n1_new - 1) # ตัวลบต้องน้อยกว่าตัวตั้ง
                    
                    q_html = f"""
                    <div style="display: flex; justify-content: center; align-items: center; gap: 15px; padding: 25px; background: #faf8f5; border-radius: 12px; border: 2px solid #dcd1c4; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); margin: 15px 0;">
                        <div style="text-align:center;">{draw_svg_rect(n1, d1, "#1abc9c")}<br><b style="color:#1abc9c;">แถบ A (ตัวตั้ง)</b></div>
                        <div style="font-size: 35px; font-weight: bold; color: #e74c3c;">-</div>
                        <div style="text-align:center;">{draw_svg_rect(n2, d2, "#f39c12")}<br><b style="color:#f39c12;">แถบ B (ตัวลบ)</b></div>
                        <div style="font-size: 35px; font-weight: bold; color: #2c3e50;">= &nbsp;?</div>
                    </div>
                    """
                    q = f"จากแถบเศษส่วนต่อไปนี้ จงหาผลลบของส่วนที่ระบายสี<br><span style='font-size:14px; color:#e74c3c;'>(⭐ สังเกต: แถบทั้งสองถูกแบ่งเป็นช่องไม่เท่ากัน)</span><br>{q_html}"
                    
                    diff_n = n1_new - n2
                    gcd_v = math.gcd(diff_n, d2)
                    ans_n, ans_d = diff_n // gcd_v, d2 // gcd_v
                    ans_text = str(ans_n) if ans_d == 1 else draw_frac(ans_n, ans_d)
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    <div style='background-color:#ebf5fb; border-left:4px solid #3498db; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    🔍 <b>วิเคราะห์จากภาพ:</b><br>
                    • <b style="color:#1abc9c;">แถบ A</b> ถูกแบ่ง {d1} ช่อง ระบายสี {n1} ช่อง = {draw_frac(n1, d1)}<br>
                    • <b style="color:#f39c12;">แถบ B</b> ถูกแบ่ง {d2} ช่อง ระบายสี {n2} ช่อง = {draw_frac(n2, d2)}<br>
                    • จะเห็นว่าขนาดช่องไม่เท่ากัน ต้องทำ <b style="color:#1abc9c;">แถบ A</b> ให้มีช่องเล็กๆ เท่ากับแถบ B ก่อนถึงจะลบกันได้!
                    </div>
                    <b>วิธีทำอย่างละเอียด:</b><br>
                    👉 <b>ขั้นที่ 1: ทำตัวส่วนให้เท่ากัน</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;นำ <b style='color:#e74c3c;'>{m}</b> มาคูณทั้งเศษและส่วนของ {draw_frac(n1, d1)} เพื่อให้ส่วนกลายเป็น {d2}<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;• {draw_frac(f"{n1} × <b style='color:#e74c3c;'>{m}</b>", f"{d1} × <b style='color:#e74c3c;'>{m}</b>")} = <b style='color:#1abc9c;'>{draw_frac(n1_new, d2)}</b><br><br>
                    👉 <b>ขั้นที่ 2: นำเศษส่วนมาลบกัน</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;{draw_frac(n1_new, d2)} <b style='color:#e74c3c;'>-</b> {draw_frac(n2, d2)} = {draw_frac(f"{n1_new} - {n2}", d2)} = <b>{draw_frac(diff_n, d2)}</b><br><br>
                    """
                    if gcd_v > 1:
                        sol += f"""👉 <b>ขั้นที่ 3: ทำให้เป็นเศษส่วนอย่างต่ำ</b><br>
                        &nbsp;&nbsp;&nbsp;&nbsp;นำแม่ <b>{gcd_v}</b> มาหารทั้งเศษและส่วน: {draw_frac(f"{diff_n} ÷ {gcd_v}", f"{d2} ÷ {gcd_v}")} = <b>{ans_text}</b><br><br>"""
                    sol += f"<b>ตอบ: {ans_text}</b></span>"

                else:
                    # แบบที่ 3: ตารางสมมาตร (ตัวเลขล้วน ตัวส่วนไม่เท่ากัน)
                    d1 = random.choice([3, 4, 5])
                    n1 = random.randint(1, d1-1)
                    m = random.choice([2, 3, 4])
                    d2 = d1 * m
                    
                    n1_new = n1 * m
                    n2 = random.randint(1, n1_new - 1) # เพื่อให้ A - B ไม่ติดลบ
                    
                    q_html = f"""
                    <div style="display: flex; justify-content: space-around; gap: 15px; margin: 20px 0;">
                        <div style="flex: 1; border: 3px solid #2980b9; border-radius: 8px; padding: 15px; background: white; text-align: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
                            <b style="color: #2980b9; font-size: 18px;">กล่อง A</b><hr style="border-top: 2px dashed #2980b9;">
                            <div style="font-size: 26px; margin-top:15px; margin-bottom:5px;">{draw_frac(n1, d1)}</div>
                        </div>
                        <div style="flex: 1; border: 3px solid #f39c12; border-radius: 8px; padding: 15px; background: white; text-align: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
                            <b style="color: #f39c12; font-size: 18px;">กล่อง B</b><hr style="border-top: 2px dashed #f39c12;">
                            <div style="font-size: 26px; margin-top:15px; margin-bottom:5px;">{draw_frac(n2, d2)}</div>
                        </div>
                    </div>
                    <div style="text-align: center; background: #f9ebea; padding: 15px; border-radius: 8px; border: 2px solid #e74c3c; font-size: 22px;">
                        จงหาผลลัพธ์ของ &nbsp; <b>A <span style="color:#e74c3c;">-</span> B</b>
                    </div>
                    """
                    q = f"พิจารณาค่าจากกล่องที่กำหนดให้ แล้วหาคำตอบที่ถูกต้องที่สุด<br>{q_html}"
                    
                    diff_n = n1_new - n2
                    gcd_v = math.gcd(diff_n, d2)
                    ans_n, ans_d = diff_n // gcd_v, d2 // gcd_v
                    ans_text = str(ans_n) if ans_d == 1 else draw_frac(ans_n, ans_d)
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    <b>วิธีทำอย่างละเอียด:</b><br>
                    👉 <b>ขั้นที่ 1: จัดรูปสมการ</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;นำค่าจากกล่องมาเขียนลบกัน: {draw_frac(n1, d1)} <b style='color:#e74c3c;'>-</b> {draw_frac(n2, d2)}<br><br>
                    👉 <b>ขั้นที่ 2: ทำตัวส่วนให้เท่ากัน</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;💡 <i>สังเกตว่าตัวส่วนคือ {d1} และ {d2} เราต้องทำ {d1} ให้กลายเป็น {d2} โดยการคูณด้วย {m}</i><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;• {draw_frac(f"{n1} × <b style='color:#e74c3c;'>{m}</b>", f"{d1} × <b style='color:#e74c3c;'>{m}</b>")} = <b style='color:#2980b9;'>{draw_frac(n1_new, d2)}</b><br><br>
                    👉 <b>ขั้นที่ 3: นำเศษส่วนมาลบกัน</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;{draw_frac(n1_new, d2)} <b style='color:#e74c3c;'>-</b> {draw_frac(n2, d2)} = {draw_frac(f"{n1_new} - {n2}", d2)} = <b>{draw_frac(diff_n, d2)}</b><br><br>
                    """
                    if gcd_v > 1:
                        sol += f"""👉 <b>ขั้นที่ 4: ทำให้เป็นเศษส่วนอย่างต่ำ</b><br>
                        &nbsp;&nbsp;&nbsp;&nbsp;นำแม่ <b>{gcd_v}</b> มาหารทั้งเศษและส่วน: {draw_frac(f"{diff_n} ÷ {gcd_v}", f"{d2} ÷ {gcd_v}")} = <b>{ans_text}</b><br><br>"""
                    sol += f"<b>ตอบ: {ans_text}</b></span>"



            elif actual_sub_t == "การคูณเศษส่วน":
                
                # สุ่มรูปแบบโจทย์ (1: ตารางพื้นที่ซ้อนทับ, 2: เศษส่วนคูณจำนวนเต็ม, 3: ตารางเงื่อนไขสมมาตร)
                prob_style = random.choice([1, 2, 3])
                
                # ฟังก์ชันช่วยวาดตัวเลขเศษส่วน
                def draw_frac(n, d):
                    return f"<span style='display:inline-flex; flex-direction:column; vertical-align:middle; text-align:center; margin:0 4px; font-weight:bold; font-size:18px;'><span style='border-bottom:2px solid #2c3e50; padding:0 3px;'>{n}</span><span style='padding:0 3px;'>{d}</span></span>"
                
                # ฟังก์ชันวาดตารางพื้นที่ซ้อนทับ (Area Model)
                def draw_svg_grid(n1, d1, n2, d2):
                    w, h = 120, 120
                    cw, ch = w/d1, h/d2
                    svg = f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
                    for row in range(d2):
                        for col in range(d1):
                            if col < n1 and row < n2:
                                fill = "#2ecc71" # พื้นที่ซ้อนทับ (คำตอบ)
                            elif col < n1:
                                fill = "#a9dfbf" # แนวตั้งอย่างเดียว
                            elif row < n2:
                                fill = "#f9e79f" # แนวนอนอย่างเดียว
                            else:
                                fill = "#ecf0f1" # ไม่ถูกระบาย
                            svg += f'<rect x="{col*cw}" y="{row*ch}" width="{cw}" height="{ch}" fill="{fill}" stroke="#2c3e50" stroke-width="1.5"/>'
                    svg += '</svg>'
                    return svg

                if prob_style == 1:
                    # แบบที่ 1: แผนภาพตารางซ้อนทับ (Visual Math)
                    d1 = random.choice([3, 4, 5])
                    n1 = random.randint(1, d1-1)
                    d2 = random.choice([3, 4, 5])
                    n2 = random.randint(1, d2-1)
                    
                    q_html = f"""
                    <div style="display: flex; justify-content: center; align-items: center; padding: 25px; background: #fdfefe; border-radius: 12px; border: 2px dashed #95a5a6; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); margin: 15px 0;">
                        <div style="text-align:center;">
                            {draw_svg_grid(n1, d1, n2, d2)}<br>
                            <span style="font-size:14px; color:#7f8c8d;">(พื้นที่สีเขียวเข้มคือส่วนที่ทับซ้อนกัน)</span>
                        </div>
                    </div>
                    """
                    q = f"จากแผนภาพ แสดงตารางแนวตั้งที่ระบายสี {draw_frac(n1, d1)} และแนวนอนระบายสี {draw_frac(n2, d2)} <br>พื้นที่ส่วนที่ระบายสีทับซ้อนกันเขียนเป็นประโยคสัญลักษณ์และหาคำตอบได้อย่างไร?<br>{q_html}"
                    
                    ans_n_raw = n1 * n2
                    ans_d_raw = d1 * d2
                    gcd_v = math.gcd(ans_n_raw, ans_d_raw)
                    ans_n, ans_d = ans_n_raw // gcd_v, ans_d_raw // gcd_v
                    ans_text = str(ans_n) if ans_d == 1 else draw_frac(ans_n, ans_d)
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    <div style='background-color:#ebf5fb; border-left:4px solid #3498db; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    🔍 <b>วิเคราะห์จากภาพ (Area Model):</b><br>
                    • <b>แนวตั้ง</b> แบ่งเป็น {d1} ช่อง ระบายสี {n1} ช่อง = {draw_frac(n1, d1)}<br>
                    • <b>แนวนอน</b> แบ่งเป็น {d2} ช่อง ระบายสี {n2} ช่อง = {draw_frac(n2, d2)}<br>
                    • <b>พื้นที่ทับซ้อนกัน (สีเขียวเข้ม)</b> คือผลลัพธ์ของ <b>การคูณ</b>
                    </div>
                    <b>วิธีทำอย่างละเอียด:</b><br>
                    👉 <b>ขั้นที่ 1: ตั้งสมการคูณเศษส่วน</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;ประโยคสัญลักษณ์: {draw_frac(n1, d1)} <b style='color:#e74c3c;'>×</b> {draw_frac(n2, d2)} = ?<br><br>
                    👉 <b>ขั้นที่ 2: นำเศษคูณเศษ และ ส่วนคูณส่วน</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;💡 <i>การคูณเศษส่วน <b>ไม่ต้อง</b> ทำตัวส่วนให้เท่ากัน นำบนคูณบน ล่างคูณล่างได้เลย!</i><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;• <b>ตัวเศษ (บน):</b> {n1} × {n2} = {ans_n_raw}<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;• <b>ตัวส่วน (ล่าง):</b> {d1} × {d2} = {ans_d_raw}<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;จะได้ผลลัพธ์คือ: <b>{draw_frac(ans_n_raw, ans_d_raw)}</b> <i>(ซึ่งตรงกับตารางที่มีช่องทั้งหมด {ans_d_raw} ช่อง และทับซ้อนกัน {ans_n_raw} ช่องพอดี!)</i><br><br>
                    """
                    if gcd_v > 1:
                        sol += f"""👉 <b>ขั้นที่ 3: ทำให้เป็นเศษส่วนอย่างต่ำ</b><br>
                        &nbsp;&nbsp;&nbsp;&nbsp;นำแม่ <b>{gcd_v}</b> มาหารทั้งเศษและส่วน: {draw_frac(f"{ans_n_raw} ÷ {gcd_v}", f"{ans_d_raw} ÷ {gcd_v}")} = <b>{ans_text}</b><br><br>"""
                    sol += f"<b>ตอบ: {ans_text}</b></span>"

                elif prob_style == 2:
                    # แบบที่ 2: เศษส่วน คูณ จำนวนเต็ม (ตารางสมมาตร)
                    d1 = random.choice([4, 5, 6, 8, 10])
                    n1 = random.randint(1, d1-1)
                    mult_val = random.randint(2, 12)
                    
                    q_html = f"""
                    <div style="display: flex; justify-content: space-around; gap: 15px; margin: 20px 0;">
                        <div style="flex: 1; border: 3px solid #1abc9c; border-radius: 8px; padding: 15px; background: white; text-align: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
                            <b style="color: #1abc9c; font-size: 18px;">กล่อง A</b><hr style="border-top: 2px dashed #1abc9c;">
                            <div style="font-size: 26px; margin-top:15px; margin-bottom:5px;">{draw_frac(n1, d1)}</div>
                        </div>
                        <div style="flex: 1; border: 3px solid #e67e22; border-radius: 8px; padding: 15px; background: white; text-align: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
                            <b style="color: #e67e22; font-size: 18px;">กล่อง B</b><hr style="border-top: 2px dashed #e67e22;">
                            <div style="font-size: 26px; margin-top:15px; margin-bottom:5px; font-weight:bold;">{mult_val}</div>
                        </div>
                    </div>
                    <div style="text-align: center; background: #fdf2e9; padding: 15px; border-radius: 8px; border: 2px solid #d35400; font-size: 22px;">
                        จงหาผลลัพธ์ของ &nbsp; <b>A <span style="color:#e74c3c;">×</span> B</b>
                    </div>
                    """
                    q = f"พิจารณาค่าจากกล่องที่กำหนดให้ แล้วหาคำตอบที่ถูกต้องที่สุด<br>{q_html}"
                    
                    ans_n_raw = n1 * mult_val
                    ans_d_raw = d1
                    gcd_v = math.gcd(ans_n_raw, ans_d_raw)
                    ans_n, ans_d = ans_n_raw // gcd_v, ans_d_raw // gcd_v
                    
                    # ถ้าเศษเกินส่วน ให้ทำเป็นจำนวนคละ
                    if ans_n > ans_d and ans_d != 1:
                        whole = ans_n // ans_d
                        rem = ans_n % ans_d
                        if rem == 0:
                            ans_text = str(whole)
                        else:
                            ans_text = f"{whole}{draw_frac(rem, ans_d)}"
                    else:
                        ans_text = str(ans_n) if ans_d == 1 else draw_frac(ans_n, ans_d)
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    <div style='background-color:#ebf5fb; border-left:4px solid #3498db; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    💡 <b>หลักการคูณเศษส่วนกับจำนวนเต็ม:</b><br>
                    จำนวนเต็มทุกตัว มี <b>"ส่วนเป็น 1"</b> ซ่อนอยู่เสมอ ดังนั้น {mult_val} ก็คือ {draw_frac(mult_val, 1)}
                    </div>
                    <b>วิธีทำอย่างละเอียด:</b><br>
                    👉 <b>ขั้นที่ 1: จัดรูปสมการใหม่</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;{draw_frac(n1, d1)} <b style='color:#e74c3c;'>×</b> <b>{mult_val}</b> &nbsp;&nbsp;➔&nbsp;&nbsp; {draw_frac(n1, d1)} <b style='color:#e74c3c;'>×</b> {draw_frac(mult_val, 1)}<br><br>
                    👉 <b>ขั้นที่ 2: นำบนคูณบน และ ล่างคูณล่าง</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;• <b>ตัวเศษ:</b> {n1} × {mult_val} = {ans_n_raw}<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;• <b>ตัวส่วน:</b> {d1} × 1 = {ans_d_raw}<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;จะได้ผลลัพธ์คือ: <b>{draw_frac(ans_n_raw, ans_d_raw)}</b><br><br>
                    """
                    if gcd_v > 1:
                        sol += f"""👉 <b>ขั้นที่ 3: ทำให้เป็นเศษส่วนอย่างต่ำ</b><br>
                        &nbsp;&nbsp;&nbsp;&nbsp;นำแม่ <b>{gcd_v}</b> มาหารทั้งเศษและส่วน: {draw_frac(f"{ans_n_raw} ÷ {gcd_v}", f"{ans_d_raw} ÷ {gcd_v}")} = <b>{draw_frac(ans_n, ans_d) if ans_d != 1 else ans_n}</b><br><br>"""
                    
                    if ans_n > ans_d and ans_d != 1:
                        sol += f"""👉 <b>ขั้นที่ 4: แปลงเศษเกินเป็นจำนวนคละ</b><br>
                        &nbsp;&nbsp;&nbsp;&nbsp;นำ {ans_n} ตั้ง หารด้วย {ans_d} จะได้ <b>{whole}</b> เศษ <b>{rem}</b><br>
                        &nbsp;&nbsp;&nbsp;&nbsp;เขียนเป็นจำนวนคละได้: <b>{ans_text}</b><br><br>"""
                        
                    sol += f"<b>ตอบ: {ans_text}</b></span>"

                else:
                    # แบบที่ 3: เศษส่วน คูณ เศษส่วน (ตารางสมมาตร)
                    d1 = random.choice([3, 4, 5, 6])
                    n1 = random.randint(1, d1-1)
                    d2 = random.choice([3, 4, 5, 6])
                    n2 = random.randint(1, d2-1)
                    
                    q_html = f"""
                    <div style="display: flex; justify-content: space-around; gap: 15px; margin: 20px 0;">
                        <div style="flex: 1; border: 3px solid #2980b9; border-radius: 8px; padding: 15px; background: white; text-align: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
                            <b style="color: #2980b9; font-size: 18px;">กล่อง A</b><hr style="border-top: 2px dashed #2980b9;">
                            <div style="font-size: 26px; margin-top:15px; margin-bottom:5px;">{draw_frac(n1, d1)}</div>
                        </div>
                        <div style="flex: 1; border: 3px solid #8e44ad; border-radius: 8px; padding: 15px; background: white; text-align: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
                            <b style="color: #8e44ad; font-size: 18px;">กล่อง B</b><hr style="border-top: 2px dashed #8e44ad;">
                            <div style="font-size: 26px; margin-top:15px; margin-bottom:5px;">{draw_frac(n2, d2)}</div>
                        </div>
                    </div>
                    <div style="text-align: center; background: #f5eef8; padding: 15px; border-radius: 8px; border: 2px solid #9b59b6; font-size: 22px;">
                        จงหาผลลัพธ์ของ &nbsp; <b>A <span style="color:#e74c3c;">×</span> B</b>
                    </div>
                    """
                    q = f"พิจารณาค่าจากกล่องที่กำหนดให้ แล้วหาคำตอบที่ถูกต้องที่สุด<br>{q_html}"
                    
                    ans_n_raw = n1 * n2
                    ans_d_raw = d1 * d2
                    gcd_v = math.gcd(ans_n_raw, ans_d_raw)
                    ans_n, ans_d = ans_n_raw // gcd_v, ans_d_raw // gcd_v
                    ans_text = str(ans_n) if ans_d == 1 else draw_frac(ans_n, ans_d)
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    <b>วิธีทำอย่างละเอียด:</b><br>
                    👉 <b>ขั้นที่ 1: จัดรูปสมการ</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;นำค่าจากกล่องมาเขียนคูณกัน: {draw_frac(n1, d1)} <b style='color:#e74c3c;'>×</b> {draw_frac(n2, d2)}<br><br>
                    👉 <b>ขั้นที่ 2: นำบนคูณบน และ ล่างคูณล่าง</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;💡 <i>การคูณเศษส่วน ไม่ต้องทำส่วนให้เท่ากัน!</i><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;• <b>ตัวเศษ:</b> {n1} × {n2} = {ans_n_raw}<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;• <b>ตัวส่วน:</b> {d1} × {d2} = {ans_d_raw}<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;จะได้ผลลัพธ์คือ: <b>{draw_frac(ans_n_raw, ans_d_raw)}</b><br><br>
                    """
                    if gcd_v > 1:
                        sol += f"""👉 <b>ขั้นที่ 3: ทำให้เป็นเศษส่วนอย่างต่ำ</b><br>
                        &nbsp;&nbsp;&nbsp;&nbsp;นำแม่ <b>{gcd_v}</b> มาหารทั้งเศษและส่วน: {draw_frac(f"{ans_n_raw} ÷ {gcd_v}", f"{ans_d_raw} ÷ {gcd_v}")} = <b>{ans_text}</b><br><br>"""
                    sol += f"<b>ตอบ: {ans_text}</b></span>"



            elif actual_sub_t == "การหารเศษส่วน":
                
                # สุ่มรูปแบบโจทย์ (1: ภาพจำลองการแบ่งพื้นที่, 2: ตารางสมมาตร A/B, 3: ภาพจำลองแบ่งวงกลม)
                prob_style = random.choice([1, 2, 3])
                
                # ฟังก์ชันช่วยวาดตัวเลขเศษส่วน
                def draw_frac(n, d):
                    return f"<span style='display:inline-flex; flex-direction:column; vertical-align:middle; text-align:center; margin:0 4px; font-weight:bold; font-size:18px;'><span style='border-bottom:2px solid #2c3e50; padding:0 3px;'>{n}</span><span style='padding:0 3px;'>{d}</span></span>"
                
                # ฟังก์ชันวาดภาพพื้นที่ถูกแบ่ง (สี่เหลี่ยม)
                def draw_svg_div_rect(n, d, m):
                    w, h = 120, 120
                    cw, ch = w/d, h/m
                    svg = f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
                    for row in range(m):
                        for col in range(d):
                            if col < n and row == 0:
                                fill = "#2ecc71" # พื้นที่คำตอบ (เขียวเข้ม)
                            elif col < n:
                                fill = "#a9dfbf" # พื้นที่ตัวตั้งเดิม (เขียวอ่อน)
                            else:
                                fill = "#ecf0f1" # พื้นที่ว่าง
                            svg += f'<rect x="{col*cw}" y="{row*ch}" width="{cw}" height="{ch}" fill="{fill}" stroke="#2c3e50" stroke-width="1.5"/>'
                    svg += '</svg>'
                    return svg

                # ฟังก์ชันวาดภาพวงกลมถูกแบ่ง
                def draw_svg_circles(w_count, d):
                    svg = "<div style='display:flex; justify-content:center; flex-wrap:wrap; gap:10px;'>"
                    for _ in range(w_count):
                        svg += f'<svg width="70" height="70" viewBox="0 0 70 70">'
                        svg += '<circle cx="35" cy="35" r="33" fill="#fcf3cf" stroke="#f39c12" stroke-width="2"/>'
                        for i in range(d):
                            angle = math.radians(i * (360 / d) - 90)
                            x2 = 35 + 33 * math.cos(angle)
                            y2 = 35 + 33 * math.sin(angle)
                            svg += f'<line x1="35" y1="35" x2="{x2}" y2="{y2}" stroke="#f39c12" stroke-width="1.5"/>'
                        svg += '</svg>'
                    svg += "</div>"
                    return svg

                if prob_style == 1:
                    # แบบที่ 1: เศษส่วน หาร จำนวนเต็ม (Visual Area Model)
                    d1 = random.choice([3, 4, 5])
                    n1 = random.randint(1, d1-1)
                    m = random.choice([2, 3, 4]) # จำนวนเต็มที่นำมาหาร
                    
                    q_html = f"""
                    <div style="display: flex; justify-content: center; align-items: center; padding: 25px; background: #fdfefe; border-radius: 12px; border: 2px dashed #95a5a6; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); margin: 15px 0;">
                        <div style="text-align:center;">
                            {draw_svg_div_rect(n1, d1, m)}<br>
                            <span style="font-size:14px; color:#7f8c8d;">(พื้นที่สีเขียวเข้ม 1 แถว คือผลลัพธ์ของการถูกแบ่ง)</span>
                        </div>
                    </div>
                    """
                    q = f"จากแผนภาพ มีพื้นที่ระบายสีอยู่ {draw_frac(n1, d1)} ถ้านำพื้นที่ระบายสีนี้มา <b>แบ่งออกเป็น {m} ส่วนเท่าๆ กัน</b><br>พื้นที่ส่วนที่ถูกแบ่ง (สีเขียวเข้ม) จะเขียนเป็นเศษส่วนได้อย่างไร?<br>{q_html}"
                    
                    ans_n_raw = n1
                    ans_d_raw = d1 * m
                    gcd_v = math.gcd(ans_n_raw, ans_d_raw)
                    ans_n, ans_d = ans_n_raw // gcd_v, ans_d_raw // gcd_v
                    ans_text = str(ans_n) if ans_d == 1 else draw_frac(ans_n, ans_d)
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    <div style='background-color:#ebf5fb; border-left:4px solid #3498db; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    🔍 <b>วิเคราะห์จากภาพ:</b><br>
                    • พื้นที่เดิมมี {draw_frac(n1, d1)} (แถบแนวตั้งสีเขียว)<br>
                    • การนำมา <b>"แบ่ง"</b> คือการ <b>"หาร"</b> ด้วย {m} ซึ่งทำให้เกิดช่องเล็กๆ รวมทั้งหมด {ans_d_raw} ช่อง<br>
                    • พื้นที่ 1 ส่วนที่ถูกแบ่ง (สีเขียวเข้ม) มี {n1} ช่อง จึงมีค่าเท่ากับ {draw_frac(n1, ans_d_raw)}
                    </div>
                    <b>วิธีทำด้วยการคำนวณ:</b><br>
                    👉 <b>ขั้นที่ 1: ตั้งประโยคสัญลักษณ์</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;{draw_frac(n1, d1)} <b style='color:#e74c3c;'>÷</b> <b>{m}</b> = ?<br><br>
                    👉 <b>ขั้นที่ 2: เปลี่ยนหารเป็นคูณ กลับเศษเป็นส่วน</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;💡 <i>จำนวนเต็ม {m} มีส่วนเป็น 1 ซ่อนอยู่ ({draw_frac(m, 1)}) เมื่อกลับเศษเป็นส่วนจะได้ {draw_frac(1, m)}</i><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;• เปลี่ยนเป็น: {draw_frac(n1, d1)} <b style='color:#27ae60;'>×</b> <b style='color:#e67e22;'>{draw_frac(1, m)}</b><br><br>
                    👉 <b>ขั้นที่ 3: นำบนคูณบน ล่างคูณล่าง</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;• ตัวเศษ: {n1} × 1 = {ans_n_raw}<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;• ตัวส่วน: {d1} × {m} = {ans_d_raw}<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;จะได้ผลลัพธ์คือ: <b>{draw_frac(ans_n_raw, ans_d_raw)}</b><br><br>
                    """
                    if gcd_v > 1:
                        sol += f"""👉 <b>ขั้นที่ 4: ทำให้เป็นเศษส่วนอย่างต่ำ</b><br>
                        &nbsp;&nbsp;&nbsp;&nbsp;นำแม่ <b>{gcd_v}</b> มาหารทั้งเศษและส่วน: {draw_frac(f"{ans_n_raw} ÷ {gcd_v}", f"{ans_d_raw} ÷ {gcd_v}")} = <b>{ans_text}</b><br><br>"""
                    sol += f"<b>ตอบ: {ans_text}</b></span>"

                elif prob_style == 2:
                    # แบบที่ 2: เศษส่วน หาร เศษส่วน (ตารางสมมาตร)
                    d1 = random.choice([3, 4, 5, 7])
                    n1 = random.randint(1, d1-1)
                    d2 = random.choice([3, 4, 5, 8])
                    n2 = random.randint(1, d2-1)
                    
                    q_html = f"""
                    <div style="display: flex; justify-content: space-around; gap: 15px; margin: 20px 0;">
                        <div style="flex: 1; border: 3px solid #2980b9; border-radius: 8px; padding: 15px; background: white; text-align: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
                            <b style="color: #2980b9; font-size: 18px;">ตัวตั้ง (A)</b><hr style="border-top: 2px dashed #2980b9;">
                            <div style="font-size: 26px; margin-top:15px; margin-bottom:5px;">{draw_frac(n1, d1)}</div>
                        </div>
                        <div style="flex: 1; border: 3px solid #e74c3c; border-radius: 8px; padding: 15px; background: white; text-align: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
                            <b style="color: #e74c3c; font-size: 18px;">ตัวหาร (B)</b><hr style="border-top: 2px dashed #e74c3c;">
                            <div style="font-size: 26px; margin-top:15px; margin-bottom:5px;">{draw_frac(n2, d2)}</div>
                        </div>
                    </div>
                    <div style="text-align: center; background: #fdedec; padding: 15px; border-radius: 8px; border: 2px solid #c0392b; font-size: 22px;">
                        จงหาผลลัพธ์ของ &nbsp; <b>A <span style="color:#e74c3c;">÷</span> B</b>
                    </div>
                    """
                    q = f"พิจารณาค่าจากกล่องที่กำหนดให้ แล้วหาคำตอบที่ถูกต้องที่สุด<br>{q_html}"
                    
                    ans_n_raw = n1 * d2
                    ans_d_raw = d1 * n2
                    gcd_v = math.gcd(ans_n_raw, ans_d_raw)
                    ans_n, ans_d = ans_n_raw // gcd_v, ans_d_raw // gcd_v
                    
                    # แปลงเป็นจำนวนคละถ้าจำเป็น
                    if ans_n > ans_d and ans_d != 1:
                        w = ans_n // ans_d
                        r = ans_n % ans_d
                        ans_text = f"{w}{draw_frac(r, ans_d)}" if r != 0 else str(w)
                    else:
                        ans_text = str(ans_n) if ans_d == 1 else draw_frac(ans_n, ans_d)
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    <b>วิธีทำอย่างละเอียด:</b><br>
                    👉 <b>ขั้นที่ 1: ตั้งประโยคสัญลักษณ์</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;{draw_frac(n1, d1)} <b style='color:#e74c3c;'>÷</b> {draw_frac(n2, d2)}<br><br>
                    👉 <b>ขั้นที่ 2: เปลี่ยนหารเป็นคูณ กลับเศษเป็นส่วน</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;💡 <i>ท่องจำ: "ตัวหน้าเหมือนเดิม เปลี่ยนหารเป็นคูณ กลับเศษเป็นส่วนตัวหลัง!"</i><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;• เปลี่ยนสมการเป็น: {draw_frac(n1, d1)} <b style='color:#27ae60;'>×</b> <b style='color:#e67e22;'>{draw_frac(d2, n2)}</b><br><br>
                    👉 <b>ขั้นที่ 3: นำเศษคูณเศษ และ ส่วนคูณส่วน</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;• {n1} × {d2} = {ans_n_raw}<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;• {d1} × {n2} = {ans_d_raw}<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;จะได้ผลลัพธ์คือ: <b>{draw_frac(ans_n_raw, ans_d_raw)}</b><br><br>
                    """
                    if gcd_v > 1:
                        sol += f"""👉 <b>ขั้นที่ 4: ทำให้เป็นเศษส่วนอย่างต่ำ</b><br>
                        &nbsp;&nbsp;&nbsp;&nbsp;นำแม่ <b>{gcd_v}</b> มาหารทั้งเศษและส่วน: {draw_frac(f"{ans_n_raw} ÷ {gcd_v}", f"{ans_d_raw} ÷ {gcd_v}")} = <b>{draw_frac(ans_n, ans_d) if ans_d != 1 else ans_n}</b><br><br>"""
                        
                    if ans_n > ans_d and ans_d != 1:
                        sol += f"""👉 <b>ขั้นที่ 5: แปลงเศษเกินเป็นจำนวนคละ</b><br>
                        &nbsp;&nbsp;&nbsp;&nbsp;นำ {ans_n} ตั้ง หารด้วย {ans_d} จะได้ <b>{ans_n // ans_d}</b> เศษ <b>{ans_n % ans_d}</b><br>
                        &nbsp;&nbsp;&nbsp;&nbsp;เขียนเป็นจำนวนคละได้: <b>{ans_text}</b><br><br>"""
                        
                    sol += f"<b>ตอบ: {ans_text}</b></span>"

                else:
                    # แบบที่ 3: จำนวนเต็ม หาร เศษส่วน (Visual Circles)
                    w_count = random.randint(2, 4)
                    d = random.choice([3, 4, 5, 6])
                    
                    q_html = f"""
                    <div style="padding: 20px; background: #fdfaf0; border-radius: 12px; border: 2px dashed #f1c40f; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); margin: 15px 0;">
                        {draw_svg_circles(w_count, d)}
                    </div>
                    """
                    q = f"ถ้ามีพิซซ่าอยู่ <b>{w_count} ถาด</b> นำมาแบ่งเป็นชิ้นย่อยๆ ชิ้นละ <b>{draw_frac(1, d)}</b> ถาด<br>จะได้พิซซ่าทั้งหมดกี่ชิ้น? (ประโยคสัญลักษณ์: {w_count} ÷ {draw_frac(1, d)})<br>{q_html}"
                    
                    ans_n_raw = w_count * d
                    ans_d_raw = 1
                    ans_text = str(ans_n_raw)
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    <div style='background-color:#ebf5fb; border-left:4px solid #3498db; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    🔍 <b>วิเคราะห์จากภาพ:</b><br>
                    • พิซซ่า 1 ถาด ถูกตัดเป็น {d} ชิ้น<br>
                    • ถ้ามีพิซซ่า {w_count} ถาด ก็จะนำจำนวนถาดไปคูณกับจำนวนชิ้นในแต่ละถาดได้เลย! ({w_count} × {d})
                    </div>
                    <b>วิธีทำด้วยการคำนวณ:</b><br>
                    👉 <b>ขั้นที่ 1: ตั้งประโยคสัญลักษณ์</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;<b>{w_count}</b> <b style='color:#e74c3c;'>÷</b> {draw_frac(1, d)} = ?<br><br>
                    👉 <b>ขั้นที่ 2: เปลี่ยนหารเป็นคูณ กลับเศษเป็นส่วน</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;• เปลี่ยนสมการเป็น: <b>{w_count}</b> <b style='color:#27ae60;'>×</b> <b style='color:#e67e22;'>{draw_frac(d, 1)}</b><br><br>
                    👉 <b>ขั้นที่ 3: หาผลลัพธ์</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;💡 <i>ส่วนเป็น 1 ไม่ต้องนำมาเขียน สามารถนำ {w_count} มาคูณ {d} ได้เลย</i><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;• {w_count} × {d} = <b>{ans_text}</b><br><br>
                    <b>ตอบ: {ans_text} ชิ้น</b></span>"""



            elif actual_sub_t == "การบวกทศนิยม":
                # สุ่มรูปแบบโจทย์ (1: ตารางร้อย (Visual), 2: กล่องสมมาตร, 3: ป้ายราคาสินค้า)
                prob_style = random.choice([1, 2, 3])
                
                # ฟังก์ชันวาดตารางร้อย (10x10) แสดงทศนิยม 2 ตำแหน่ง
                def draw_svg_decimal_grid(val, color="#3498db"):
                    squares = round(val * 100)
                    svg = '<svg width="100" height="100" viewBox="0 0 100 100" style="border: 2px solid #2c3e50; background-color: #ecf0f1;">'
                    count = 0
                    for row in range(10):
                        for col in range(10):
                            fill = color if count < squares else "none"
                            svg += f'<rect x="{col*10}" y="{row*10}" width="10" height="10" fill="{fill}" stroke="#bdc3c7" stroke-width="0.5"/>'
                            count += 1
                    svg += '</svg>'
                    return svg

                if prob_style == 1:
                    # แบบที่ 1: ตารางร้อย (Visual Math)
                    v1 = round(random.uniform(0.10, 0.45), 2)
                    v2 = round(random.uniform(0.10, 0.45), 2)
                    total = round(v1 + v2, 2)
                    
                    q_html = f"""
                    <div style="display: flex; justify-content: center; align-items: center; gap: 20px; padding: 25px; background: #fdfefe; border-radius: 12px; border: 2px dashed #95a5a6; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); margin: 15px 0;">
                        <div style="text-align:center;">{draw_svg_decimal_grid(v1, "#3498db")}<br><b style="color:#3498db;">รูปที่ 1</b></div>
                        <div style="font-size: 35px; font-weight: bold; color: #e74c3c;">+</div>
                        <div style="text-align:center;">{draw_svg_decimal_grid(v2, "#e67e22")}<br><b style="color:#e67e22;">รูปที่ 2</b></div>
                        <div style="font-size: 35px; font-weight: bold; color: #2c3e50;">= &nbsp;?</div>
                    </div>
                    """
                    q = f"จากภาพ ตารางร้อย 1 ตารางมีค่าเท่ากับ 1 หน่วย ถ้านำส่วนที่ระบายสีมาบวกกัน จะได้ทศนิยมเท่าใด?<br>{q_html}"
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    <div style='background-color:#ebf5fb; border-left:4px solid #3498db; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    🔍 <b>วิเคราะห์จากภาพ:</b><br>
                    • ตารางมี 100 ช่องเล็ก 1 ช่องเล็กมีค่า <b>0.01</b><br>
                    • <b style="color:#3498db;">รูปที่ 1</b> ระบายสี {round(v1*100)} ช่อง เขียนเป็นทศนิยมได้ <b>{v1:.2f}</b><br>
                    • <b style="color:#e67e22;">รูปที่ 2</b> ระบายสี {round(v2*100)} ช่อง เขียนเป็นทศนิยมได้ <b>{v2:.2f}</b>
                    </div>
                    <b>วิธีทำอย่างละเอียด:</b><br>
                    👉 <b>ขั้นที่ 1: ตั้งบวกทศนิยม</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;💡 <i>หลักสำคัญที่สุด: ต้องตั้ง "จุดทศนิยม" ให้ตรงกัน!</i><br>
                    <table style="font-family: 'Courier New', monospace; font-size: 22px; margin-left: 50px; border-collapse: collapse;">
                        <tr>
                            <td style="text-align: right; padding: 2px 10px;">{v1:.2f}</td>
                            <td style="width: 30px;"></td>
                        </tr>
                        <tr>
                            <td style="text-align: right; padding: 2px 10px; border-bottom: 2px solid #333;">{v2:.2f}</td>
                            <td style="text-align: center; color: #e74c3c; font-weight: bold; font-size: 24px; vertical-align: bottom; padding-bottom: 5px;">+</td>
                        </tr>
                        <tr>
                            <td style="text-align: right; padding: 5px 10px; border-bottom: 4px double #333;"><b>{total:.2f}</b></td>
                            <td></td>
                        </tr>
                    </table><br>
                    👉 <b>สรุปผลลัพธ์:</b> ถ้านำมาระบายสีรวมกันจะได้ทั้งหมด {round(total*100)} ช่อง หรือ <b>{total:.2f}</b><br><br>
                    <b>ตอบ: {total:.2f}</b></span>"""

                elif prob_style == 2:
                    # แบบที่ 2: กล่องสมมาตร (จำนวนตำแหน่งทศนิยมไม่เท่ากัน เพื่อดักทางเด็ก)
                    v1 = round(random.uniform(5.1, 25.9), 1)   # 1 ตำแหน่ง
                    v2 = round(random.uniform(1.11, 9.99), 2)  # 2 ตำแหน่ง
                    if random.choice([True, False]): 
                        v1, v2 = v2, v1
                    
                    total = round(v1 + v2, 2)
                    
                    q_html = f"""
                    <div style="display: flex; justify-content: space-around; gap: 15px; margin: 20px 0;">
                        <div style="flex: 1; border: 3px solid #2980b9; border-radius: 8px; padding: 15px; background: white; text-align: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
                            <b style="color: #2980b9; font-size: 18px;">กล่อง A</b><hr style="border-top: 2px dashed #2980b9;">
                            <div style="font-size: 32px; font-weight:bold; margin-top:15px; margin-bottom:5px;">{v1}</div>
                        </div>
                        <div style="flex: 1; border: 3px solid #f39c12; border-radius: 8px; padding: 15px; background: white; text-align: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
                            <b style="color: #f39c12; font-size: 18px;">กล่อง B</b><hr style="border-top: 2px dashed #f39c12;">
                            <div style="font-size: 32px; font-weight:bold; margin-top:15px; margin-bottom:5px;">{v2}</div>
                        </div>
                    </div>
                    <div style="text-align: center; background: #e8f8f5; padding: 15px; border-radius: 8px; border: 2px solid #1abc9c; font-size: 22px;">
                        จงหาผลลัพธ์ของ &nbsp; <b>A <span style="color:#e74c3c;">+</span> B</b>
                    </div>
                    """
                    q = f"พิจารณาค่าจากกล่องที่กำหนดให้ แล้วหาคำตอบที่ถูกต้องที่สุด<br><span style='font-size:14px; color:#e74c3c;'>(⭐ ระวัง: จำนวนตำแหน่งทศนิยมไม่เท่ากัน)</span><br>{q_html}"
                    
                    # ปรับ String เพื่อเติม 0 ในเฉลยให้เห็นชัดเจน
                    v1_str = f"{v1:.2f}" if len(str(v1).split('.')[1]) == 1 else str(v1)
                    v2_str = f"{v2:.2f}" if len(str(v2).split('.')[1]) == 1 else str(v2)
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    <div style='background-color:#fcf3cf; border-left:4px solid #f1c40f; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    💡 <b>เทคนิคสำคัญ (การบวกทศนิยม):</b><br>
                    เมื่อจำนวนตำแหน่งทศนิยมไม่เท่ากัน ให้ <b>"เติม 0"</b> ต่อท้ายเลขที่มีตำแหน่งน้อยกว่า เพื่อให้จำนวนหลักเท่ากัน และจะได้ตั้ง <b>"จุดทศนิยม"</b> ให้ตรงกันได้ง่ายขึ้น!
                    </div>
                    <b>วิธีทำอย่างละเอียด:</b><br>
                    👉 <b>ขั้นที่ 1: เติม 0 ให้ตำแหน่งเท่ากัน</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;• {v1} เติมศูนย์ปรับเป็น <b>{v1_str}</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;• {v2} เติมศูนย์ปรับเป็น <b>{v2_str}</b><br><br>
                    👉 <b>ขั้นที่ 2: ตั้งบวกให้จุดตรงกัน</b><br>
                    <table style="font-family: 'Courier New', monospace; font-size: 22px; margin-left: 50px; border-collapse: collapse;">
                        <tr>
                            <td style="text-align: right; padding: 2px 10px;">{v1_str}</td>
                            <td style="width: 30px;"></td>
                        </tr>
                        <tr>
                            <td style="text-align: right; padding: 2px 10px; border-bottom: 2px solid #333;">{v2_str}</td>
                            <td style="text-align: center; color: #e74c3c; font-weight: bold; font-size: 24px; vertical-align: bottom; padding-bottom: 5px;">+</td>
                        </tr>
                        <tr>
                            <td style="text-align: right; padding: 5px 10px; border-bottom: 4px double #333;"><b>{total:.2f}</b></td>
                            <td></td>
                        </tr>
                    </table><br>
                    <b>ตอบ: {total:.2f}</b></span>"""

                else:
                    # แบบที่ 3: ป้ายราคาสินค้า
                    items = [("สมุดโน้ต", 15.5, 25.5), ("ปากกาสี", 8.25, 12.75), ("ยางลบ", 5.5, 9.5), ("ไม้บรรทัด", 10.25, 15.5)]
                    item1 = random.choice(items)
                    items.remove(item1)
                    item2 = random.choice(items)
                    
                    p1 = round(random.uniform(item1[1], item1[2]), 2)
                    p1 = round(p1 * 4) / 4 
                    if p1.is_integer(): p1 += 0.5
                    
                    p2 = round(random.uniform(item2[1], item2[2]), 2)
                    p2 = round(p2 * 4) / 4
                    if p2.is_integer(): p2 += 0.25

                    total = round(p1 + p2, 2)
                    p1_str = f"{p1:.2f}"
                    p2_str = f"{p2:.2f}"
                    
                    q_html = f"""
                    <div style="display: flex; justify-content: center; gap: 20px; margin: 20px 0;">
                        <div style="background: #e74c3c; color: white; padding: 15px 25px; border-radius: 8px; position: relative; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);">
                            <div style="font-size: 16px;">{item1[0]}</div>
                            <div style="font-size: 24px; font-weight: bold;">฿ {p1_str}</div>
                            <div style="position: absolute; left: -10px; top: 20px; width: 20px; height: 20px; background: white; border-radius: 50%;"></div>
                        </div>
                        <div style="font-size: 30px; font-weight: bold; color: #7f8c8d; display:flex; align-items:center;">+</div>
                        <div style="background: #8e44ad; color: white; padding: 15px 25px; border-radius: 8px; position: relative; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);">
                            <div style="font-size: 16px;">{item2[0]}</div>
                            <div style="font-size: 24px; font-weight: bold;">฿ {p2_str}</div>
                            <div style="position: absolute; left: -10px; top: 20px; width: 20px; height: 20px; background: white; border-radius: 50%;"></div>
                        </div>
                    </div>
                    """
                    q = f"คุณแม่ต้องการซื้อสินค้า 2 ชิ้นตามป้ายราคาด้านล่าง คุณแม่ต้องจ่ายเงินทั้งหมดกี่บาท?<br>{q_html}"
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    <div style='background-color:#ebf5fb; border-left:4px solid #3498db; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    🔍 <b>วิเคราะห์โจทย์:</b><br>
                    • หา <b>"ราคารวม"</b> ต้องนำราคาสินค้าทั้งสองชิ้นมา <b>บวกกัน</b><br>
                    • ประโยคสัญลักษณ์: {p1_str} + {p2_str} = ?
                    </div>
                    <b>วิธีทำอย่างละเอียด:</b><br>
                    👉 <b>ตั้งบวกทศนิยม:</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;💡 <i>ตั้งหลักและจุดทศนิยมให้ตรงกัน จากนั้นบวกจากขวาไปซ้ายเหมือนการบวกเลขปกติ</i><br>
                    <table style="font-family: 'Courier New', monospace; font-size: 22px; margin-left: 50px; border-collapse: collapse;">
                        <tr>
                            <td style="text-align: right; padding: 2px 10px;">{p1_str}</td>
                            <td style="width: 30px;"></td>
                        </tr>
                        <tr>
                            <td style="text-align: right; padding: 2px 10px; border-bottom: 2px solid #333;">{p2_str}</td>
                            <td style="text-align: center; color: #e74c3c; font-weight: bold; font-size: 24px; vertical-align: bottom; padding-bottom: 5px;">+</td>
                        </tr>
                        <tr>
                            <td style="text-align: right; padding: 5px 10px; border-bottom: 4px double #333;"><b>{total:.2f}</b></td>
                            <td></td>
                        </tr>
                    </table><br>
                    <b>ตอบ: คุณแม่ต้องจ่ายเงินทั้งหมด {total:.2f} บาท</b></span>"""



            elif actual_sub_t == "การลบทศนิยม":
                prob_style = random.choice([1, 2, 3])
                
                def draw_svg_decimal_grid(val, color="#3498db", is_sub=False):
                    squares = round(val * 100)
                    svg = '<svg width="100" height="100" viewBox="0 0 100 100" style="border: 2px solid #2c3e50; background-color: #ecf0f1;">'
                    count = 0
                    for row in range(10):
                        for col in range(10):
                            if count < squares:
                                if is_sub:
                                    svg += f'<rect x="{col*10}" y="{row*10}" width="10" height="10" fill="#fadbd8" stroke="#bdc3c7" stroke-width="0.5"/>'
                                    svg += f'<line x1="{col*10+2}" y1="{row*10+2}" x2="{col*10+8}" y2="{row*10+8}" stroke="#e74c3c" stroke-width="1.5"/>'
                                    svg += f'<line x1="{col*10+8}" y1="{row*10+2}" x2="{col*10+2}" y2="{row*10+8}" stroke="#e74c3c" stroke-width="1.5"/>'
                                else:
                                    svg += f'<rect x="{col*10}" y="{row*10}" width="10" height="10" fill="{color}" stroke="#bdc3c7" stroke-width="0.5"/>'
                            else:
                                svg += f'<rect x="{col*10}" y="{row*10}" width="10" height="10" fill="none" stroke="#bdc3c7" stroke-width="0.5"/>'
                            count += 1
                    svg += '</svg>'
                    return svg

                if prob_style == 1:
                    v1 = round(random.uniform(0.50, 0.95), 2)
                    v2 = round(random.uniform(0.10, v1 - 0.10), 2)
                    ans = round(v1 - v2, 2)
                    
                    q_html = f"""
                    <div style="display: flex; justify-content: center; align-items: center; gap: 20px; padding: 25px; background: #fdfefe; border-radius: 12px; border: 2px dashed #95a5a6; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); margin: 15px 0;">
                        <div style="text-align:center;">{draw_svg_decimal_grid(v1, "#3498db")}<br><b style="color:#3498db;">รูปที่ 1 (ตัวตั้ง)</b></div>
                        <div style="font-size: 35px; font-weight: bold; color: #e74c3c;">-</div>
                        <div style="text-align:center;">{draw_svg_decimal_grid(v2, "#e74c3c", is_sub=True)}<br><b style="color:#e74c3c;">รูปที่ 2 (ตัวหักออก)</b></div>
                        <div style="font-size: 35px; font-weight: bold; color: #2c3e50;">= &nbsp;?</div>
                    </div>
                    """
                    q = f"จากภาพ ตารางร้อย 1 ตารางมีค่าเท่ากับ 1 หน่วย ถ้านำพื้นที่ระบายสีในรูปที่ 1 มาหักออกด้วยรูปที่ 2 จะเหลือทศนิยมเท่าใด?<br>{q_html}"
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    <div style='background-color:#ebf5fb; border-left:4px solid #3498db; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    🔍 <b>วิเคราะห์จากภาพ:</b><br>
                    • <b style="color:#3498db;">รูปที่ 1</b> ระบายสี {round(v1*100)} ช่อง เขียนเป็นทศนิยมได้ <b>{v1:.2f}</b><br>
                    • <b style="color:#e74c3c;">รูปที่ 2</b> ถูกกากบาทหักออกไป {round(v2*100)} ช่อง เขียนเป็นทศนิยมได้ <b>{v2:.2f}</b>
                    </div>
                    <b>วิธีทำอย่างละเอียด:</b><br>
                    👉 <b>ขั้นที่ 1: ตั้งลบทศนิยม</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;💡 <i>หลักสำคัญที่สุด: ต้องตั้ง "จุดทศนิยม" ให้ตรงกัน!</i><br>
                    <table style="font-family: 'Courier New', monospace; font-size: 22px; margin-left: 50px; border-collapse: collapse;">
                        <tr>
                            <td style="text-align: right; padding: 2px 10px;">{v1:.2f}</td>
                            <td style="width: 30px;"></td>
                        </tr>
                        <tr>
                            <td style="text-align: right; padding: 2px 10px; border-bottom: 2px solid #333;">{v2:.2f}</td>
                            <td style="text-align: center; color: #e74c3c; font-weight: bold; font-size: 24px; vertical-align: bottom; padding-bottom: 5px;">-</td>
                        </tr>
                        <tr>
                            <td style="text-align: right; padding: 5px 10px; border-bottom: 4px double #333;"><b>{ans:.2f}</b></td>
                            <td></td>
                        </tr>
                    </table><br>
                    👉 <b>สรุปผลลัพธ์:</b> จะเหลือช่องที่ระบายสีอยู่ {round(ans*100)} ช่อง หรือเขียนได้เป็น <b>{ans:.2f}</b><br><br>
                    <b>ตอบ: {ans:.2f}</b></span>"""

                elif prob_style == 2:
                    v1 = round(random.uniform(10.5, 25.9), 1)   
                    v2 = round(random.uniform(1.15, v1 - 2.0), 2)
                    while int(str(v2).split('.')[1][-1]) == 0:
                        v2 = round(random.uniform(1.15, v1 - 2.0), 2)
                        
                    ans = round(v1 - v2, 2)
                    
                    q_html = f"""
                    <div style="display: flex; justify-content: space-around; gap: 15px; margin: 20px 0;">
                        <div style="flex: 1; border: 3px solid #2980b9; border-radius: 8px; padding: 15px; background: white; text-align: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
                            <b style="color: #2980b9; font-size: 18px;">กล่อง A</b><hr style="border-top: 2px dashed #2980b9;">
                            <div style="font-size: 32px; font-weight:bold; margin-top:15px; margin-bottom:5px;">{v1}</div>
                        </div>
                        <div style="flex: 1; border: 3px solid #e74c3c; border-radius: 8px; padding: 15px; background: white; text-align: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
                            <b style="color: #e74c3c; font-size: 18px;">กล่อง B</b><hr style="border-top: 2px dashed #e74c3c;">
                            <div style="font-size: 32px; font-weight:bold; margin-top:15px; margin-bottom:5px;">{v2}</div>
                        </div>
                    </div>
                    <div style="text-align: center; background: #fdedec; padding: 15px; border-radius: 8px; border: 2px solid #c0392b; font-size: 22px;">
                        จงหาผลลัพธ์ของ &nbsp; <b>A <span style="color:#e74c3c;">-</span> B</b>
                    </div>
                    """
                    q = f"พิจารณาค่าจากกล่องที่กำหนดให้ แล้วหาคำตอบที่ถูกต้องที่สุด<br><span style='font-size:14px; color:#e74c3c;'>(⭐ ระวัง: จำนวนตำแหน่งทศนิยมไม่เท่ากัน)</span><br>{q_html}"
                    
                    v1_str = f"{v1:.2f}" 
                    v2_str = f"{v2:.2f}"
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    <div style='background-color:#fcf3cf; border-left:4px solid #f1c40f; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    💡 <b>เทคนิคสำคัญ (การลบทศนิยม):</b><br>
                    เมื่อจำนวนตำแหน่งทศนิยมไม่เท่ากัน ให้ <b>"เติม 0"</b> ต่อท้ายเลขที่มีตำแหน่งน้อยกว่า เพื่อให้ตั้งลบและยืมเลขได้ง่ายขึ้น!
                    </div>
                    <b>วิธีทำอย่างละเอียด:</b><br>
                    👉 <b>ขั้นที่ 1: เติม 0 ให้ตำแหน่งเท่ากัน</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;• <b>กล่อง A:</b> {v1} เติมศูนย์ปรับเป็น <b>{v1_str}</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;• <b>กล่อง B:</b> {v2} มี 2 ตำแหน่งอยู่แล้วคือ <b>{v2_str}</b><br><br>
                    👉 <b>ขั้นที่ 2: ตั้งลบให้จุดตรงกัน</b><br>
                    <table style="font-family: 'Courier New', monospace; font-size: 22px; margin-left: 50px; border-collapse: collapse;">
                        <tr>
                            <td style="text-align: right; padding: 2px 10px;">{v1_str}</td>
                            <td style="width: 30px;"></td>
                        </tr>
                        <tr>
                            <td style="text-align: right; padding: 2px 10px; border-bottom: 2px solid #333;">{v2_str}</td>
                            <td style="text-align: center; color: #e74c3c; font-weight: bold; font-size: 24px; vertical-align: bottom; padding-bottom: 5px;">-</td>
                        </tr>
                        <tr>
                            <td style="text-align: right; padding: 5px 10px; border-bottom: 4px double #333;"><b>{ans:.2f}</b></td>
                            <td></td>
                        </tr>
                    </table><br>
                    <b>ตอบ: {ans:.2f}</b></span>"""

                else:
                    items = [("สมุดโน้ต", 15.5, 30.5), ("ปากกาสี", 8.25, 12.75), ("แฟ้มเอกสาร", 20.5, 45.5), ("สีไม้", 35.25, 50.75)]
                    item1 = random.choice(items)
                    items.remove(item1)
                    item2 = random.choice(items)
                    
                    p1 = round(random.uniform(item1[1], item1[2]), 2)
                    p1 = round(p1 * 4) / 4 
                    if p1.is_integer(): p1 += 0.5
                    
                    p2 = round(random.uniform(item2[1], item2[2]), 2)
                    p2 = round(p2 * 4) / 4
                    if p2.is_integer(): p2 += 0.25

                    if p2 > p1:
                        p1, p2 = p2, p1
                        item1, item2 = item2, item1
                        
                    ans = round(p1 - p2, 2)
                    p1_str = f"{p1:.2f}"
                    p2_str = f"{p2:.2f}"
                    
                    q_html = f"""
                    <div style="display: flex; justify-content: center; gap: 20px; margin: 20px 0;">
                        <div style="background: #2980b9; color: white; padding: 15px 25px; border-radius: 8px; position: relative; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);">
                            <div style="font-size: 16px;">{item1[0]}</div>
                            <div style="font-size: 24px; font-weight: bold;">฿ {p1_str}</div>
                            <div style="position: absolute; left: -10px; top: 20px; width: 20px; height: 20px; background: white; border-radius: 50%;"></div>
                        </div>
                        <div style="font-size: 30px; font-weight: bold; color: #7f8c8d; display:flex; align-items:center;">เทียบกับ</div>
                        <div style="background: #e67e22; color: white; padding: 15px 25px; border-radius: 8px; position: relative; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);">
                            <div style="font-size: 16px;">{item2[0]}</div>
                            <div style="font-size: 24px; font-weight: bold;">฿ {p2_str}</div>
                            <div style="position: absolute; left: -10px; top: 20px; width: 20px; height: 20px; background: white; border-radius: 50%;"></div>
                        </div>
                    </div>
                    """
                    q = f"จากป้ายราคาสินค้า <b>{item1[0]}</b> มีราคาแพงกว่า <b>{item2[0]}</b> อยู่กี่บาท?<br>{q_html}"
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    <div style='background-color:#ebf5fb; border-left:4px solid #3498db; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    🔍 <b>วิเคราะห์โจทย์:</b><br>
                    • การหาว่าของชิ้นหนึ่ง <b>"แพงกว่า"</b> อีกชิ้นหนึ่งอยู่เท่าไหร่ คือการหา <b>"ผลต่าง"</b><br>
                    • หาผลต่างต้องนำของที่ราคาแพงกว่าตั้ง แล้ว <b>ลบ</b> ด้วยราคาที่ถูกกว่า<br>
                    • ประโยคสัญลักษณ์: {p1_str} - {p2_str} = ?
                    </div>
                    <b>วิธีทำอย่างละเอียด:</b><br>
                    👉 <b>ตั้งลบทศนิยม:</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;💡 <i>ตั้งหลักและจุดทศนิยมให้ตรงกัน จากนั้นลบเหมือนการลบเลขปกติ (ถ้าน้อยกว่าให้ยืมตัวหน้า)</i><br>
                    <table style="font-family: 'Courier New', monospace; font-size: 22px; margin-left: 50px; border-collapse: collapse;">
                        <tr>
                            <td style="text-align: right; padding: 2px 10px;">{p1_str}</td>
                            <td style="width: 30px;"></td>
                        </tr>
                        <tr>
                            <td style="text-align: right; padding: 2px 10px; border-bottom: 2px solid #333;">{p2_str}</td>
                            <td style="text-align: center; color: #e74c3c; font-weight: bold; font-size: 24px; vertical-align: bottom; padding-bottom: 5px;">-</td>
                        </tr>
                        <tr>
                            <td style="text-align: right; padding: 5px 10px; border-bottom: 4px double #333;"><b>{ans:.2f}</b></td>
                            <td></td>
                        </tr>
                    </table><br>
                    <b>ตอบ: {item1[0]} แพงกว่าอยู่ {ans:.2f} บาท</b></span>"""



            elif actual_sub_t == "การคูณทศนิยม":
                prob_style = random.choice([1, 2, 3])
                
                def draw_svg_decimal_grid(val, color="#3498db"):
                    squares = round(val * 100)
                    svg = '<svg width="100" height="100" viewBox="0 0 100 100" style="border: 2px solid #2c3e50; background-color: #ecf0f1;">'
                    count = 0
                    for row in range(10):
                        for col in range(10):
                            fill = color if count < squares else "none"
                            svg += f'<rect x="{col*10}" y="{row*10}" width="10" height="10" fill="{fill}" stroke="#bdc3c7" stroke-width="0.5"/>'
                            count += 1
                    svg += '</svg>'
                    return svg

                if prob_style == 1:
                    v1 = round(random.uniform(0.12, 0.25), 2)
                    m = random.randint(2, 4)
                    ans = round(v1 * m, 2)
                    
                    q_html = f"""
                    <div style="display: flex; justify-content: center; align-items: center; gap: 20px; padding: 25px; background: #fdfefe; border-radius: 12px; border: 2px dashed #95a5a6; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); margin: 15px 0;">
                        <div style="text-align:center;">{draw_svg_decimal_grid(v1, "#3498db")}<br><b style="color:#3498db; font-size:18px;">รูปที่ 1</b></div>
                        <div style="font-size: 35px; font-weight: bold; color: #e74c3c;">×</div>
                        <div style="text-align:center;"><div style="font-size: 60px; font-weight: bold; color: #e67e22; padding: 0 20px;">{m}</div><b style="color:#e67e22; font-size:18px;">จำนวนเท่า</b></div>
                        <div style="font-size: 35px; font-weight: bold; color: #2c3e50;">= &nbsp;?</div>
                    </div>
                    """
                    q = f"จากภาพ ตารางร้อย 1 ตารางมีค่าเท่ากับ 1 หน่วย ถ้านำพื้นที่ระบายสีในรูปที่ 1 มาเพิ่มขึ้นเป็น <b>{m} เท่า</b> จะได้ทศนิยมเท่าใด?<br>{q_html}"
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    <div style='background-color:#ebf5fb; border-left:4px solid #3498db; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    🔍 <b>วิเคราะห์จากภาพ:</b><br>
                    • รูปที่ 1 ระบายสี {round(v1*100)} ช่อง เขียนเป็นทศนิยมได้ <b>{v1:.2f}</b><br>
                    • การนำมาเพิ่มขึ้น <b>{m} เท่า</b> ก็คือการนำไป <b>คูณ (×)</b> ด้วย {m}<br>
                    • ประโยคสัญลักษณ์: {v1:.2f} × {m} = ?
                    </div>
                    <b>วิธีทำอย่างละเอียด:</b><br>
                    👉 <b>ขั้นที่ 1: แปลงตัวตั้งให้เป็นจำนวนเต็มเพื่อตั้งคูณ</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;💡 <i>เทคนิค: เราจะแอบนำ 100 มาคูณตัวตั้ง ({v1:.2f}) ให้กลายเป็นจำนวนเต็ม ({round(v1*100)}) เพื่อให้คูณเลขได้ง่ายขึ้น</i><br>
                    <table style="font-family: 'Courier New', monospace; font-size: 22px; margin-left: 50px; border-collapse: collapse;">
                        <tr>
                            <td style="text-align: right; padding: 2px 10px;">{round(v1*100)}</td>
                            <td style="width: 30px;"></td>
                        </tr>
                        <tr>
                            <td style="text-align: right; padding: 2px 10px; border-bottom: 2px solid #333;">{m}</td>
                            <td style="text-align: center; color: #e74c3c; font-weight: bold; font-size: 24px; vertical-align: bottom; padding-bottom: 5px;">×</td>
                        </tr>
                        <tr>
                            <td style="text-align: right; padding: 5px 10px; border-bottom: 4px double #333;"><b>{round(v1*100) * m}</b></td>
                            <td></td>
                        </tr>
                    </table><br>
                    👉 <b>ขั้นที่ 2: ปรับค่ากลับคืน (เลื่อนจุดทศนิยม)</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;💡 <i>เนื่องจากขั้นแรกเราแอบ <b>"คูณ 100 ขยายค่า"</b> ไปที่ตัวตั้ง ผลลัพธ์ที่ได้จึงพองโตเกินจริงไป 100 เท่า! เราจึงต้อง <b>"หารด้วย 100 กลับคืน"</b> เพื่อให้ค่าถูกต้อง (การหาร 100 คือการใส่ทศนิยม 2 ตำแหน่งนั่นเอง)</i><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;• นำ {round(v1*100) * m} มาใส่จุดทศนิยม 2 ตำแหน่ง จะได้ <b>{ans:.2f}</b><br><br>
                    <b>ตอบ: {ans:.2f}</b></span>"""

                elif prob_style == 2:
                    v1 = round(random.uniform(1.2, 5.5), 1)   
                    v2 = round(random.uniform(1.2, 4.5), 1)
                    
                    ans_raw = int(v1*10) * int(v2*10)
                    ans = round(v1 * v2, 2)
                    
                    q_html = f"""
                    <div style="display: flex; justify-content: space-around; gap: 15px; margin: 20px 0;">
                        <div style="flex: 1; border: 3px solid #2980b9; border-radius: 8px; padding: 15px; background: white; text-align: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
                            <b style="color: #2980b9; font-size: 18px;">ตัวตั้ง (A)</b><hr style="border-top: 2px dashed #2980b9;">
                            <div style="font-size: 32px; font-weight:bold; margin-top:15px; margin-bottom:5px;">{v1:.1f}</div>
                        </div>
                        <div style="flex: 1; border: 3px solid #8e44ad; border-radius: 8px; padding: 15px; background: white; text-align: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
                            <b style="color: #8e44ad; font-size: 18px;">ตัวคูณ (B)</b><hr style="border-top: 2px dashed #8e44ad;">
                            <div style="font-size: 32px; font-weight:bold; margin-top:15px; margin-bottom:5px;">{v2:.1f}</div>
                        </div>
                    </div>
                    <div style="text-align: center; background: #f4ecf7; padding: 15px; border-radius: 8px; border: 2px solid #9b59b6; font-size: 22px;">
                        จงหาผลลัพธ์ของ &nbsp; <b>A <span style="color:#e74c3c;">×</span> B</b>
                    </div>
                    """
                    q = f"พิจารณาค่าจากกล่องที่กำหนดให้ แล้วหาคำตอบที่ถูกต้องที่สุด<br>{q_html}"
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    <div style='background-color:#fcf3cf; border-left:4px solid #f1c40f; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    💡 <b>เทคนิคสำคัญ (เอาจุดออกก่อนแล้วตั้งคูณ):</b><br>
                    เพื่อให้คิดเลขง่ายขึ้น เราจะทำทั้งตัวตั้งและตัวคูณให้เป็นจำนวนเต็มก่อน!<br>
                    • นำตัวตั้ง ({v1:.1f}) ไปคูณ 10 จะได้ <b>{int(v1*10)}</b><br>
                    • นำตัวคูณ ({v2:.1f}) ไปคูณ 10 จะได้ <b>{int(v2*10)}</b>
                    </div>
                    <b>วิธีทำอย่างละเอียด:</b><br>
                    👉 <b>ขั้นที่ 1: ตั้งคูณจำนวนเต็มปกติ</b><br>
                    <table style="font-family: 'Courier New', monospace; font-size: 22px; margin-left: 50px; border-collapse: collapse;">
                        <tr>
                            <td style="text-align: right; padding: 2px 10px;">{int(v1*10)}</td>
                            <td style="width: 30px;"></td>
                        </tr>
                        <tr>
                            <td style="text-align: right; padding: 2px 10px; border-bottom: 2px solid #333;">{int(v2*10)}</td>
                            <td style="text-align: center; color: #e74c3c; font-weight: bold; font-size: 24px; vertical-align: bottom; padding-bottom: 5px;">×</td>
                        </tr>
                        <tr>
                            <td style="text-align: right; padding: 5px 10px; border-bottom: 4px double #333;"><b>{ans_raw}</b></td>
                            <td></td>
                        </tr>
                    </table><br>
                    <div style='background-color:#e8f8f5; border-left:4px solid #1abc9c; padding:10px; margin-bottom:10px; border-radius:4px;'>
                    💡 <b>ทำไมผลลัพธ์ต้องนำ "ตำแหน่งทศนิยม" มาบวกกัน?</b><br>
                    สังเกตว่าตอนแรกเราแอบขยายขนาดตัวตั้ง (คูณ 10) และขยายตัวคูณ (คูณ 10) แสดงว่าผลลัพธ์ที่ได้พองโตขึ้นไปถึง <b>10 × 10 = 100 เท่า!</b><br>
                    ดังนั้น การจะปรับค่ากลับให้ถูกต้อง เราจึงต้อง <b>"หารออกด้วย 100"</b> (ซึ่งก็คือการเติมทศนิยมกลับไป 2 ตำแหน่งนั่นเองครับ)
                    </div>
                    👉 <b>ขั้นที่ 2: นับตำแหน่งทศนิยมรวม</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;• ตัวตั้ง ({v1:.1f}) มี <b>1 ตำแหน่ง</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;• ตัวคูณ ({v2:.1f}) มี <b>1 ตำแหน่ง</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;• นำ {ans_raw} มาใส่ทศนิยมกลับคืน (1 + 1 = 2 ตำแหน่ง) จะได้ <b>{ans:.2f}</b><br><br>
                    <b>ตอบ: {ans:.2f}</b></span>"""

                else:
                    items = [("สมุดโน้ต", 15.25), ("ปากกาสี", 8.50), ("แฟ้มเอกสาร", 20.75), ("สีไม้", 35.50)]
                    item_name, item_price = random.choice(items)
                    
                    qty = random.randint(3, 7)
                    ans = round(item_price * qty, 2)
                    ans_raw = int(item_price * 100) * qty
                    
                    q_html = f"""
                    <div style="display: flex; justify-content: center; gap: 20px; margin: 20px 0; align-items:center;">
                        <div style="background: #e74c3c; color: white; padding: 15px 25px; border-radius: 8px; position: relative; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);">
                            <div style="font-size: 16px;">{item_name}</div>
                            <div style="font-size: 24px; font-weight: bold;">฿ {item_price:.2f}</div>
                            <div style="position: absolute; left: -10px; top: 20px; width: 20px; height: 20px; background: white; border-radius: 50%;"></div>
                        </div>
                        <div style="font-size: 35px; font-weight: bold; color: #7f8c8d;">×</div>
                        <div style="background: #34495e; color: white; padding: 15px 25px; border-radius: 8px; box-shadow: 2px 2px 5px rgba(0,0,0,0.2); text-align:center;">
                            <div style="font-size: 16px;">จำนวนที่ซื้อ</div>
                            <div style="font-size: 24px; font-weight: bold;">{qty} ชิ้น</div>
                        </div>
                    </div>
                    """
                    q = f"คุณครูต้องการสั่งซื้อ <b>{item_name} จำนวน {qty} ชิ้น</b> ตามป้ายราคาด้านล่าง คุณครูต้องจ่ายเงินทั้งหมดกี่บาท?<br>{q_html}"
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    <div style='background-color:#ebf5fb; border-left:4px solid #3498db; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    🔍 <b>วิเคราะห์โจทย์:</b><br>
                    • สินค้าราคาชิ้นละ <b>{item_price:.2f}</b> บาท ซื้อจำนวน <b>{qty}</b> ชิ้น<br>
                    • หาราคารวมทั้งหมด ต้องใช้ <b>"การคูณ"</b> (ราคา × จำนวน)
                    </div>
                    <b>วิธีทำอย่างละเอียด:</b><br>
                    👉 <b>ขั้นที่ 1: แปลงตัวตั้งเป็นจำนวนเต็มเพื่อตั้งคูณ</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;💡 <i>เราจะนำ {item_price:.2f} ไปคูณ 100 ก่อนเพื่อให้เป็นจำนวนเต็ม {int(item_price*100)} (คิดซะว่าแปลงหน่วยจาก บาท เป็น สตางค์) เพื่อให้คิดเลขง่ายขึ้น!</i><br>
                    <table style="font-family: 'Courier New', monospace; font-size: 22px; margin-left: 50px; border-collapse: collapse;">
                        <tr>
                            <td style="text-align: right; padding: 2px 10px;">{int(item_price*100)}</td>
                            <td style="width: 30px;"></td>
                        </tr>
                        <tr>
                            <td style="text-align: right; padding: 2px 10px; border-bottom: 2px solid #333;">{qty}</td>
                            <td style="text-align: center; color: #e74c3c; font-weight: bold; font-size: 24px; vertical-align: bottom; padding-bottom: 5px;">×</td>
                        </tr>
                        <tr>
                            <td style="text-align: right; padding: 5px 10px; border-bottom: 4px double #333;"><b>{ans_raw}</b></td>
                            <td></td>
                        </tr>
                    </table><br>
                    👉 <b>ขั้นที่ 2: ปรับค่ากลับคืน</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;💡 <i>ตอนแรกเราแอบขยายค่าตัวตั้งไป 100 เท่า พอได้ผลลัพธ์ก็ต้อง <b>นำมาหาร 100 คืน</b> เพื่อให้ค่าถูกต้อง (หรือก็คือการทำสตางค์กลับเป็นบาท)</i><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;• นำ {ans_raw} ÷ 100 (ใส่ทศนิยม 2 ตำแหน่ง) จะได้ <b>{ans:.2f}</b><br><br>
                    <b>ตอบ: คุณครูต้องจ่ายเงินทั้งหมด {ans:.2f} บาท</b></span>"""



            elif actual_sub_t == "การหารทศนิยม":
                prob_style = random.choice([1, 2, 3])
                
                def draw_svg_decimal_grid_div(val, parts, color_base="#a9dfbf", color_hl="#1abc9c"):
                    squares = round(val * 100)
                    sq_per_part = squares // parts
                    svg = '<svg width="100" height="100" viewBox="0 0 100 100" style="border: 2px solid #2c3e50; background-color: #ecf0f1;">'
                    count = 0
                    for row in range(10):
                        for col in range(10):
                            if count < sq_per_part:
                                fill = color_hl 
                            elif count < squares:
                                fill = color_base 
                            else:
                                fill = "none"
                            svg += f'<rect x="{col*10}" y="{row*10}" width="10" height="10" fill="{fill}" stroke="#bdc3c7" stroke-width="0.5"/>'
                            count += 1
                    svg += '</svg>'
                    return svg

                if prob_style == 1:
                    ans_raw = random.randint(12, 24)
                    parts = random.choice([2, 3, 4])
                    squares = ans_raw * parts
                    v1 = squares / 100
                    ans = ans_raw / 100
                    
                    q_html = f"""
                    <div style="display: flex; justify-content: center; align-items: center; gap: 20px; padding: 25px; background: #fdfefe; border-radius: 12px; border: 2px dashed #95a5a6; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); margin: 15px 0;">
                        <div style="text-align:center;">{draw_svg_decimal_grid_div(v1, parts)}<br><b style="color:#1abc9c; font-size:18px;">พื้นที่ทั้งหมด</b></div>
                        <div style="font-size: 35px; font-weight: bold; color: #e74c3c;">÷</div>
                        <div style="text-align:center;"><div style="font-size: 60px; font-weight: bold; color: #e67e22; padding: 0 20px;">{parts}</div><b style="color:#e67e22; font-size:18px;">กลุ่มเท่าๆ กัน</b></div>
                        <div style="font-size: 35px; font-weight: bold; color: #2c3e50;">= &nbsp;?</div>
                    </div>
                    """
                    q = f"จากภาพ ตารางร้อย 1 ตารางมีค่าเท่ากับ 1 หน่วย ถ้านำพื้นที่ระบายสีทั้งหมดมา <b>แบ่งออกเป็น {parts} กลุ่มเท่าๆ กัน</b><br>พื้นที่ 1 กลุ่ม (สีเขียวเข้ม) จะมีค่าเป็นทศนิยมเท่าใด?<br>{q_html}"
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    <div style='background-color:#ebf5fb; border-left:4px solid #3498db; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    🔍 <b>วิเคราะห์จากภาพ:</b><br>
                    • นับพื้นที่ระบายสีทั้งหมดได้ {squares} ช่อง เขียนเป็นทศนิยมได้ <b>{v1:.2f}</b><br>
                    • การ <b>"แบ่งเป็นกลุ่มเท่าๆ กัน"</b> คือการนำไป <b>หาร (÷)</b> ด้วย {parts}<br>
                    • ประโยคสัญลักษณ์: {v1:.2f} ÷ {parts} = ?
                    </div>
                    <b>วิธีทำอย่างละเอียด:</b><br>
                    👉 <b>ขั้นที่ 1: แปลงตัวตั้งให้เป็นจำนวนเต็ม</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;💡 <i>เพื่อให้คิดง่ายขึ้น เราจะทำตัวตั้ง ({v1:.2f}) ให้เป็นจำนวนเต็มก่อน</i><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;• เนื่องจาก {v1:.2f} มีทศนิยม 2 ตำแหน่ง จึงต้อง <b>คูณด้วย 100</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;• จะได้: {v1:.2f} × 100 = <b>{squares}</b><br><br>
                    👉 <b>ขั้นที่ 2: ตั้งหารปกติ</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;• นำ {squares} ÷ {parts} = <b>{ans_raw}</b> (หมายความว่ากลุ่มละ {ans_raw} ช่อง)<br><br>
                    👉 <b>ขั้นที่ 3: ปรับค่ากลับเป็นทศนิยม (เลื่อนจุดคืน)</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;💡 <i><b>ทำไมต้องหารด้วย 100 คืน?</b> เพราะตอนแรกเราแอบคูณ 100 ขยายแค่ <b>"ตัวตั้ง"</b> ฝ่ายเดียว เพื่อให้หารง่าย คำตอบที่ได้ ({ans_raw}) จึงใหญ่เกินความจริงไป 100 เท่า! เราเลยต้อง "หารออก" เพื่อคืนค่าเดิมครับ</i><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;• {ans_raw} ÷ 100 = <b>{ans:.2f}</b><br><br>
                    <b>ตอบ: {ans:.2f}</b></span>"""

                elif prob_style == 2:
                    ans_raw = random.randint(4, 15)
                    v2_raw = random.choice([2, 3, 4, 5, 6, 8])
                    v1_raw = ans_raw * v2_raw
                    
                    if random.choice([True, False]):
                        v1 = v1_raw / 10 
                        v2 = v2_raw / 10 
                        ans = v1 / v2    
                        move_step = 10
                    else:
                        v1 = v1_raw / 100 
                        v2 = v2_raw / 100 
                        ans = v1 / v2     
                        move_step = 100
                    
                    q_html = f"""
                    <div style="display: flex; justify-content: space-around; gap: 15px; margin: 20px 0;">
                        <div style="flex: 1; border: 3px solid #2980b9; border-radius: 8px; padding: 15px; background: white; text-align: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
                            <b style="color: #2980b9; font-size: 18px;">ตัวตั้ง (A)</b><hr style="border-top: 2px dashed #2980b9;">
                            <div style="font-size: 32px; font-weight:bold; margin-top:15px; margin-bottom:5px;">{v1}</div>
                        </div>
                        <div style="flex: 1; border: 3px solid #e74c3c; border-radius: 8px; padding: 15px; background: white; text-align: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
                            <b style="color: #e74c3c; font-size: 18px;">ตัวหาร (B)</b><hr style="border-top: 2px dashed #e74c3c;">
                            <div style="font-size: 32px; font-weight:bold; margin-top:15px; margin-bottom:5px;">{v2}</div>
                        </div>
                    </div>
                    <div style="text-align: center; background: #fdedec; padding: 15px; border-radius: 8px; border: 2px solid #c0392b; font-size: 22px;">
                        จงหาผลลัพธ์ของ &nbsp; <b>A <span style="color:#e74c3c;">÷</span> B</b>
                    </div>
                    """
                    q = f"พิจารณาค่าจากกล่องที่กำหนดให้ แล้วหาคำตอบที่ถูกต้องที่สุด<br>{q_html}"
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    <div style='background-color:#fcf3cf; border-left:4px solid #f1c40f; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    💡 <b>เทคนิคสำคัญ (การหารทศนิยมด้วยทศนิยม):</b><br>
                    เราไม่สามารถตั้งหารได้ถ้า "ตัวหาร" (กล่อง B) ยังติดจุดทศนิยมอยู่!<br>
                    • เราต้องทำ <b>ตัวหารให้เป็นจำนวนเต็มเสมอ</b> โดยการนำเลข (เช่น 10 หรือ 100) มาคูณ<b>ทั้งตัวตั้งและตัวหารพร้อมกัน</b> เพื่อให้สมดุลเท่าเดิม!
                    </div>
                    <b>วิธีทำอย่างละเอียด:</b><br>
                    👉 <b>ขั้นที่ 1: กำจัดจุดทศนิยมที่ตัวหาร</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;• ตัวหารคือ {v2} เราต้องการให้เป็นจำนวนเต็ม จึงต้องนำมา <b>คูณด้วย {move_step}</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;➔ {v2} × {move_step} = <b>{v2_raw}</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;• ในเมื่อตัวหารคูณ {move_step} <b>ตัวตั้ง ({v1}) ก็ต้องคูณด้วย {move_step} ด้วยเช่นกัน เพื่อรักษาสมดุล</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;➔ {v1} × {move_step} = <b>{v1_raw}</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;<i>(จะได้ประโยคสัญลักษณ์ใหม่คือ: <b>{v1_raw} ÷ {v2_raw}</b>)</i><br><br>
                    👉 <b>ขั้นที่ 2: ตั้งหารปกติ</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;นำตัวตั้งใหม่ ({v1_raw}) หารด้วย ตัวหารใหม่ ({v2_raw})<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;• {v1_raw} ÷ {v2_raw} = <b>{int(ans)}</b><br><br>
                    <div style='background-color:#e8f8f5; border-left:4px solid #1abc9c; padding:10px; margin-bottom:10px; border-radius:4px;'>
                    💡 <b>ทำไมข้อนี้ไม่ต้องเลื่อนจุดทศนิยมกลับคืน?</b><br>
                    เพราะในขั้นที่ 1 เรานำ {move_step} มาคูณขยายขนาด <b>"ทั้งตัวตั้งและตัวหารพร้อมๆ กัน"</b> (เหมือนการขยายเศษส่วน) ทำให้สัดส่วนการหารยังคงเท่าเดิมเป๊ะ! ผลหารที่ได้จึงเป็นคำตอบที่แท้จริงได้เลยครับ
                    </div>
                    <b>ตอบ: {int(ans)}</b></span>"""

                else:
                    people = random.randint(3, 6)
                    price_per_person = round(random.uniform(25.25, 85.50), 2)
                    price_per_person = round(price_per_person * 4) / 4 
                    total_bill = round(price_per_person * people, 2)
                    
                    q_html = f"""
                    <div style="display: flex; justify-content: center; gap: 20px; margin: 20px 0; align-items:center;">
                        <div style="background: #ecf0f1; border: 2px dashed #7f8c8d; padding: 15px 25px; border-radius: 8px; text-align:center; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
                            <div style="font-size: 16px; color:#34495e;">📄 บิลค่าอาหารรวม</div>
                            <div style="font-size: 28px; font-weight: bold; color:#2c3e50;">฿ {total_bill:.2f}</div>
                        </div>
                        <div style="font-size: 35px; font-weight: bold; color: #e74c3c;">÷</div>
                        <div style="background: #3498db; color: white; padding: 15px 25px; border-radius: 8px; box-shadow: 2px 2px 5px rgba(0,0,0,0.2); text-align:center;">
                            <div style="font-size: 16px;">แบ่งจ่ายเท่าๆ กัน</div>
                            <div style="font-size: 28px; font-weight: bold;">{people} คน</div>
                        </div>
                    </div>
                    """
                    q = f"กลุ่มเพื่อนไปทานอาหารด้วยกัน ได้รับบิลค่าอาหารดังภาพ หากต้องการแชร์จ่ายเท่าๆ กัน จะต้องจ่ายคนละกี่บาท?<br>{q_html}"
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    <div style='background-color:#ebf5fb; border-left:4px solid #3498db; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    🔍 <b>วิเคราะห์โจทย์:</b><br>
                    • ยอดรวมคือ <b>{total_bill:.2f}</b> บาท แบ่งจ่าย <b>{people}</b> คน<br>
                    • การแชร์จ่ายเท่าๆ กัน ต้องใช้ <b>"การหาร"</b><br>
                    • ประโยคสัญลักษณ์: {total_bill:.2f} ÷ {people} = ?
                    </div>
                    <b>วิธีทำอย่างละเอียด:</b><br>
                    👉 <b>ขั้นที่ 1: แปลงตัวตั้งให้เป็นจำนวนเต็ม</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;💡 <i>เพื่อให้หารเลขง่ายขึ้น เราจะทำตัวตั้ง ({total_bill:.2f}) ให้เป็นจำนวนเต็มก่อน</i><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;• เนื่องจาก {total_bill:.2f} มีทศนิยม 2 ตำแหน่ง จึงต้อง <b>นำ 100 มาคูณ</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;• จะได้: {total_bill:.2f} × 100 = <b>{int(total_bill*100)}</b><br><br>
                    👉 <b>ขั้นที่ 2: ตั้งหารปกติ</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;• นำ {int(total_bill*100)} ÷ {people} = <b>{int(price_per_person*100)}</b><br><br>
                    👉 <b>ขั้นที่ 3: ปรับค่ากลับเป็นทศนิยม (เลื่อนจุดคืน)</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;💡 <i><b>ทำไมต้องหารด้วย 100 กลับคืน?</b> เพราะตอนตั้งหาร เราแอบคูณ 100 ขยายแค่ <b>"ตัวตั้ง (ยอดเงิน)"</b> ฝ่ายเดียว แต่ "ตัวหาร (จำนวนคน)" ไม่ได้คูณตาม คำตอบที่หารมาได้จึงพองโตเกินจริงไป 100 เท่า! เลยต้องหารด้วย 100 กลับคืนครับ (ซึ่งก็คือการใส่จุดทศนิยม 2 ตำแหน่ง)</i><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;• {int(price_per_person*100)} ÷ 100 = <b>{price_per_person:.2f}</b><br><br>
                    <b>ตอบ: จะต้องจ่ายคนละ {price_per_person:.2f} บาท</b></span>"""



            elif actual_sub_t == "การบวกและการลบทศนิยม":
                op = random.choice(["+", "-"])
                dp1, dp2 = random.choice([1, 2, 3]), random.choice([1, 2, 3])
                if op == "+": a, b = round(random.uniform(1.0, 500.0), dp1), round(random.uniform(1.0, 500.0), dp2)
                else: a, b = round(random.uniform(50.0, 500.0), dp1), round(random.uniform(1.0, 49.0), dp2)
                q = f"จงหาผลลัพธ์ของ <b>{a} {op} {b}</b><br>{generate_decimal_vertical_html(a, b, op, is_key=False)}"
                sol = f"<span style='color:#2c3e50;'>{generate_decimal_vertical_html(a, b, op, is_key=True)}</span>"

            elif actual_sub_t in ["การหาค่าเฉลี่ย (Average)", "สถิติและความน่าจะเป็น"]:
                items, target_avg = random.randint(4, 6), random.randint(20, 80)
                total = target_avg * items
                nums = [random.randint(target_avg - 10, target_avg + 10) for _ in range(items - 1)]
                nums.append(total - sum(nums))
                q = f"จงหา <b>'ค่าเฉลี่ย'</b> ของข้อมูลชุดนี้: <b>{', '.join(map(str, nums))}</b>"
                sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b> ผลรวม = {total} ÷ จำนวนข้อมูล {items} = <b>{target_avg}</b></span>"

            elif actual_sub_t == "โจทย์ปัญหา ห.ร.ม. และ ค.ร.น.":
                a, b, c = random.randint(12, 45), random.randint(20, 60), random.randint(30, 90)
                l = (a * b) // math.gcd(a, b)
                lcm = (l * c) // math.gcd(l, c)
                q = f"จงหา <b>ค.ร.น.</b> ของ <b>{a}, {b} และ {c}</b>"
                sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b> ตั้งหารสั้นเพื่อหาผลคูณร่วมน้อย จะได้ <b>{lcm}</b></span>"

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
        
        hide_ws = False
        if "(แบบตั้งหลัก)" in sub_t or "หารยาว" in sub_t or "การคูณและการหารทศนิยม" in sub_t or "การบวกและการลบทศนิยม" in sub_t:
            hide_ws = True
        elif any(keyword in item["question"] for keyword in ["จงหาผลบวกของ", "จงหาผลลบของ", "จงหาผลคูณของ", "วิธีหารยาว", "แบบตั้งหารยาว"]):
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

selected_grade = st.sidebar.selectbox("📚 เลือกระดับชั้น:", ["ป.4", "ป.5"])
main_topics_list = list(curriculum_db[selected_grade].keys())
main_topics_list.append("🌟 โหมดพิเศษ (สุ่มทุกเรื่อง)")

selected_main = st.sidebar.selectbox("📂 เลือกหัวข้อหลัก:", main_topics_list)

if selected_main == "🌟 โหมดพิเศษ (สุ่มทุกเรื่อง)":
    selected_sub = "แบบทดสอบรวมปลายภาค"
    st.sidebar.info("💡 โหมดนี้จะสุ่มดึงโจทย์จากทุกเรื่องในชั้นเรียนนี้มายำรวมกัน")
else:
    selected_sub = st.sidebar.selectbox("📝 เลือกหัวข้อย่อย:", curriculum_db[selected_grade][selected_main])

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
    value="ปานกลาง"
)

if spacing_level == "แคบ": q_margin, ws_height = "15px", "100px"
elif spacing_level == "ปานกลาง": q_margin, ws_height = "20px", "180px"
elif spacing_level == "กว้าง": q_margin, ws_height = "30px", "280px"
else: q_margin, ws_height = "40px", "400px"

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎨 ตั้งค่าแบรนด์")
brand_name = st.sidebar.text_input("🏷️ ชื่อแบรนด์ / ผู้สอน:", value="บ้านทีเด็ด")

if st.sidebar.button("🚀 สั่งสร้างใบงาน ป.4-ป.5", type="primary", use_container_width=True):
    with st.spinner("กำลังออกแบบรูปภาพและสร้างเฉลยแบบ Step-by-Step..."):
        
        qs = generate_questions_logic(selected_grade, selected_main, selected_sub, num_input, is_challenge)
        
        html_w = create_page(selected_grade, selected_sub, qs, is_key=False, q_margin=q_margin, ws_height=ws_height, brand_name=brand_name)
        html_k = create_page(selected_grade, selected_sub, qs, is_key=True, q_margin=q_margin, ws_height=ws_height, brand_name=brand_name)
        
        st.session_state['worksheet_html'] = html_w
        st.session_state['answerkey_html'] = html_k
        
        ebook_body = f'\n<div class="a4-wrapper">{extract_body(html_w)}</div>\n<div class="a4-wrapper">{extract_body(html_k)}</div>\n'
        
        full_ebook_html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap" rel="stylesheet"><style>@page {{ size: A4; margin: 15mm; }} @media screen {{ body {{ font-family: 'Sarabun', sans-serif; background-color: #525659; display: flex; flex-direction: column; align-items: center; padding: 40px 0; margin: 0; }} .a4-wrapper {{ width: 210mm; min-height: 297mm; background: white; margin-bottom: 30px; box-shadow: 0 10px 20px rgba(0,0,0,0.3); padding: 15mm; box-sizing: border-box; }} }} @media print {{ body {{ font-family: 'Sarabun', sans-serif; background: transparent; padding: 0; display: block; margin: 0; }} .a4-wrapper {{ width: 100%; min-height: auto; margin: 0; padding: 0; box-shadow: none; page-break-after: always; }} }} .header {{ text-align: center; border-bottom: 2px solid #333; margin-bottom: 10px; padding-bottom: 10px; }} .q-box {{ margin-bottom: {q_margin}; padding: 10px 15px; page-break-inside: avoid; font-size: 20px; line-height: 1.6; }} .workspace {{ height: {ws_height}; border: 2px dashed #bdc3c7; border-radius: 8px; margin: 15px 0; padding: 10px; color: #95a5a6; font-size: 16px; background-color: #fafbfc; }} .ans-line {{ margin-top: 10px; border-bottom: 1px dotted #999; width: 80%; height: 30px; font-weight: bold; font-size: 20px; display: flex; align-items: flex-end; padding-bottom: 5px; }} .sol-text {{ color: #333; font-size: 18px; display: block; margin-top: 15px; padding: 15px; background-color: #f1f8ff; border-left: 4px solid #3498db; border-radius: 4px; line-height: 1.6; }} .page-footer {{ text-align: right; font-size: 14px; color: #95a5a6; margin-top: 20px; border-top: 1px solid #eee; padding-top: 10px; }} </style></head><body>{ebook_body}</body></html>"""

        filename_base = f"BaanTded_P4_P5_{selected_grade}_{int(time.time())}"
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
