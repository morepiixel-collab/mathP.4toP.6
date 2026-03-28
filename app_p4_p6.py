import streamlit as st
import streamlit.components.v1 as components
import random
import math
import zipfile
import io
import time

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
st.set_page_config(page_title="Math Generator - Primary 4", page_icon="🎓", layout="wide")

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
    <h1>🎓 Math Worksheet Pro <span style="font-size: 20px; background: #e74c3c; color: #fff; padding: 5px 15px; border-radius: 20px; vertical-align: middle;">ประถมปลาย ป.4</span></h1>
    <p>ระบบสร้างโจทย์คณิตศาสตร์และสมการ (ฉบับปรับปรุงเฉพาะ ป.4)</p>
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

def draw_p4_real_life_geo_svg(scenario, shape_type, sides, unit="ม."):
    svg_w, svg_h = 450, 250
    cx, cy = 225, 125
    svg = f'<svg width="{svg_w}" height="{svg_h}">'
    
    if shape_type == "square":
        v_length = 140
        v_width = 140
        disp_l, disp_w = sides[0], sides[0]
    else:
        w_val, l_val = sides[0], sides[1]
        ratio = w_val / l_val
        v_length = 180
        v_width = v_length * ratio
        if v_width < 70: v_width = 70
        if v_width > 150: 
            v_width = 150
            v_length = v_width / ratio
        disp_w, disp_l = sides[0], sides[1]

    tl = (cx - v_length/2, cy - v_width/2)
    tr = (cx + v_length/2, cy - v_width/2)
    bl = (cx - v_length/2, cy + v_width/2)
    br = (cx + v_length/2, cy + v_width/2)
    
    pts = f"{tl[0]},{tl[1]} {tr[0]},{tr[1]} {br[0]},{br[1]} {bl[0]},{bl[1]}"
    
    if scenario == "fence":
        svg += f'<polygon points="{pts}" fill="#d5f5e3" stroke="#27ae60" stroke-width="4"/>'
        svg += f'<rect x="{tl[0]-6}" y="{tl[1]-6}" width="{v_length+12}" height="{v_width+12}" fill="none" stroke="#e67e22" stroke-width="2.5" stroke-dasharray="8,4"/>'
    elif scenario == "running":
        svg += f'<polygon points="{pts}" fill="#abebc6" stroke="#2ecc71" stroke-width="2"/>'
        svg += f'<rect x="{tl[0]-8}" y="{tl[1]-8}" width="{v_length+16}" height="{v_width+16}" fill="none" stroke="#e74c3c" stroke-width="3" stroke-dasharray="5,5"/>'
    elif scenario == "frame":
        svg += f'<polygon points="{pts}" fill="#fcf3cf" stroke="#8a360f" stroke-width="8" stroke-linejoin="miter"/>'
        svg += f'<rect x="{tl[0]+8}" y="{tl[1]+8}" width="{v_length-16}" height="{v_width-16}" fill="none" stroke="#f39c12" stroke-width="1.5"/>'
    elif scenario == "tile":
        svg += f'''<defs><pattern id="tilePattern" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
                <rect width="20" height="20" fill="#fdfefe" stroke="#d5d8dc" stroke-width="1"/></pattern></defs>'''
        svg += f'<polygon points="{pts}" fill="url(#tilePattern)" stroke="#34495e" stroke-width="3"/>'
        svg += f'<polygon points="{pts}" fill="#f5cba7" fill-opacity="0.2" stroke="none"/>'
    elif scenario == "carpet":
        svg += f'<polygon points="{pts}" fill="#ebdef0" stroke="#8e44ad" stroke-width="5" stroke-linejoin="round"/>'
        svg += f'<rect x="{tl[0]+5}" y="{tl[1]+5}" width="{v_length-10}" height="{v_width-10}" fill="none" stroke="#6c3483" stroke-width="2" stroke-dasharray="4,4"/>'
    elif scenario == "paint":
        svg += f'<polygon points="{pts}" fill="#fadbd8" stroke="#c0392b" stroke-width="3"/>'

    text_color = "#2c3e50"
    if shape_type == "square":
        svg += f'<text x="{cx}" y="{bl[1] + 25}" font-family="Sarabun" font-size="18" font-weight="bold" text-anchor="middle" fill="{text_color}">ด้านละ {disp_l} {unit}</text>'
    else:
        svg += f'<text x="{cx}" y="{bl[1] + 25}" font-family="Sarabun" font-size="18" font-weight="bold" text-anchor="middle" fill="{text_color}">ยาว {disp_l} {unit}</text>'
        svg += f'<text x="{tr[0] + 15}" y="{cy + 5}" font-family="Sarabun" font-size="18" font-weight="bold" text-anchor="start" fill="{text_color}">กว้าง {disp_w} {unit}</text>'

    svg += '</svg>'
    return f'''<div style="display:flex; justify-content:center; margin: 20px 0;">
        <div style="border: 1px solid #bdc3c7; border-radius: 12px; padding: 25px; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            {svg}
        </div></div>'''

def draw_p4_grid_area_svg(shape_pts, unit="ตารางหน่วย"):
    svg_w, svg_h = 450, 270
    cols, rows = 14, 8
    cell = 25
    ox = (svg_w - (cols * cell)) / 2
    oy = (svg_h - (rows * cell)) / 2 - 15 
    svg = f'<svg width="{svg_w}" height="{svg_h}">'

    for r in range(rows + 1):
        y = oy + r * cell
        svg += f'<line x1="{ox}" y1="{y}" x2="{ox + cols * cell}" y2="{y}" stroke="#bdc3c7" stroke-width="1" stroke-dasharray="3,3"/>'
    for c in range(cols + 1):
        x = ox + c * cell
        svg += f'<line x1="{x}" y1="{oy}" x2="{x}" y2="{oy + rows * cell}" stroke="#bdc3c7" stroke-width="1" stroke-dasharray="3,3"/>'

    pts_str = " ".join([f"{ox + p[0]*cell},{oy + p[1]*cell}" for p in shape_pts])
    svg += f'<polygon points="{pts_str}" fill="#85c1e9" fill-opacity="0.9" stroke="#2980b9" stroke-width="2.5" stroke-linejoin="round"/>'

    leg_y = oy + rows * cell + 25
    svg += f'<rect x="{ox + 30}" y="{leg_y - 15}" width="20" height="20" fill="#85c1e9" fill-opacity="0.9" stroke="#2980b9" stroke-width="1.5"/>'
    svg += f'<text x="{ox + 60}" y="{leg_y}" font-family="Sarabun" font-size="16" font-weight="bold" fill="#2c3e50">กำหนดให้ 1 ช่อง มีพื้นที่ = 1 {unit}</text>'

    svg += '</svg>'
    return f'''<div style="display:flex; justify-content:center; margin: 20px 0;">
        <div style="border: 1px solid #bdc3c7; border-radius: 12px; padding: 20px 25px; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            {svg}
        </div></div>'''
    
def draw_p4_grid_area_solution_svg(rects, unit="ตารางหน่วย"):
    svg_w, svg_h = 450, 270
    cols, rows = 14, 8
    cell = 25
    min_x = min(r[0] for r in rects)
    max_x = max(r[0] + r[2] for r in rects)
    min_y = min(r[1] for r in rects)
    max_y = max(r[1] + r[3] for r in rects)
    shape_w = max_x - min_x
    shape_h = max_y - min_y
    offset_x = (cols - shape_w) // 2 - min_x
    offset_y = (rows - shape_h) // 2 - min_y
    ox = (svg_w - (cols * cell)) / 2
    oy = (svg_h - (rows * cell)) / 2 - 15 
    svg = f'<svg width="{svg_w}" height="{svg_h}">'

    for r in range(rows + 1):
        y = oy + r * cell
        svg += f'<line x1="{ox}" y1="{y}" x2="{ox + cols * cell}" y2="{y}" stroke="#bdc3c7" stroke-width="1" stroke-dasharray="3,3"/>'
    for c in range(cols + 1):
        x = ox + c * cell
        svg += f'<line x1="{x}" y1="{oy}" x2="{x}" y2="{oy + rows * cell}" stroke="#bdc3c7" stroke-width="1" stroke-dasharray="3,3"/>'

    for rx, ry, rw, rh, color in rects:
        final_x = ox + (rx + offset_x) * cell
        final_y = oy + (ry + offset_y) * cell
        final_w = rw * cell
        final_h = rh * cell
        svg += f'<rect x="{final_x}" y="{final_y}" width="{final_w}" height="{final_h}" fill="{color}" fill-opacity="0.85" stroke="#2c3e50" stroke-width="2" stroke-linejoin="round"/>'
        cx_rect = final_x + final_w/2
        cy_rect = final_y + final_h/2 + 6 
        area_val = rw * rh
        svg += f'<text x="{cx_rect}" y="{cy_rect}" font-family="Sarabun" font-size="18" font-weight="bold" text-anchor="middle" fill="#ffffff" style="text-shadow: 1px 1px 2px rgba(0,0,0,0.8);">{area_val}</text>'

    svg += '</svg>'
    return f'''<div style="display:flex; justify-content:center; margin: 10px 0;">
        <div style="border: 2px dashed #8e44ad; border-radius: 12px; padding: 15px; background-color: #fdfafb; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
            <div style="text-align:center; font-weight:bold; font-size:16px; color:#8e44ad; margin-bottom:10px;">ภาพอธิบาย: การแบ่งรูปเพื่อคำนวณพื้นที่</div>
            {svg}
        </div></div>'''
    def draw_p4_parallelogram_rhombus_area_svg(shape_type, base_val, height_val, unit="ซม."):
    svg_w, svg_h = 450, 250
    cx, cy = 225, 120
    svg = f'<svg width="{svg_w}" height="{svg_h}">'
    
    if shape_type == "rhombus":
        v_height = 80
        dx = 60
        v_base = 100
    else:
        v_height = random.randint(75, 95)
        v_base = random.randint(130, 170)
        dx = random.randint(35, 55)

    top_y = cy - v_height/2
    bot_y = cy + v_height/2
    tl = (cx - v_base/2 + dx/2, top_y)
    tr = (cx + v_base/2 + dx/2, top_y)
    bl = (cx - v_base/2 - dx/2, bot_y)
    br = (cx + v_base/2 - dx/2, bot_y)
    
    pts = f"{tl[0]},{tl[1]} {tr[0]},{tr[1]} {br[0]},{br[1]} {bl[0]},{bl[1]}"
    svg += f'<polygon points="{pts}" fill="#ebf5fb" stroke="#2c3e50" stroke-width="2.5"/>'
    svg += f'<line x1="{tl[0]}" y1="{tl[1]}" x2="{tl[0]}" y2="{bot_y}" stroke="#e74c3c" stroke-width="2.5" stroke-dasharray="6,4"/>'
    
    s = 12
    svg += f'<polyline points="{tl[0]},{bot_y-s} {tl[0]+s},{bot_y-s} {tl[0]+s},{bot_y}" fill="none" stroke="#e74c3c" stroke-width="2.5"/>'
    svg += f'<text x="{cx}" y="{bot_y + 30}" font-family="Sarabun" font-size="18" font-weight="bold" text-anchor="middle" fill="#2980b9">ฐาน {base_val} {unit}</text>'
    svg += f'<text x="{tl[0] + 12}" y="{cy + 5}" font-family="Sarabun" font-size="18" font-weight="bold" text-anchor="start" fill="#e74c3c">สูง {height_val} {unit}</text>'

    svg += '</svg>'
    return f'''<div style="display:flex; justify-content:center; margin: 20px 0;">
        <div style="border: 1px solid #bdc3c7; border-radius: 12px; padding: 25px; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            {svg}
        </div></div>'''

def draw_p4_triangle_area_svg(tri_type, base_val, height_val, unit="ซม."):
    svg_w, svg_h = 450, 250
    cx, cy = 225, 120 
    svg = f'<svg width="{svg_w}" height="{svg_h}">'

    v_base = random.randint(140, 200)   
    v_height = random.randint(90, 130)  
    bottom_y = cy + v_height/2
    top_y = cy - v_height/2

    if tri_type == "right":
        bl = (cx - v_base/2, bottom_y)
        br = (cx + v_base/2, bottom_y)
        top = (bl[0], top_y)
        pts = f"{top[0]},{top[1]} {br[0]},{br[1]} {bl[0]},{bl[1]}"
        svg += f'<polygon points="{pts}" fill="#e8f8f5" stroke="#2c3e50" stroke-width="2.5"/>'
        s = 15
        svg += f'<polyline points="{bl[0]},{bl[1]-s} {bl[0]+s},{bl[1]-s} {bl[0]+s},{bl[1]}" fill="none" stroke="#e74c3c" stroke-width="2.5"/>'
        svg += f'<text x="{cx}" y="{bottom_y + 30}" font-family="Sarabun" font-size="18" font-weight="bold" text-anchor="middle" fill="#2980b9">ฐาน {base_val} {unit}</text>'
        svg += f'<text x="{bl[0] - 15}" y="{cy}" font-family="Sarabun" font-size="18" font-weight="bold" text-anchor="end" fill="#e74c3c">สูง {height_val} {unit}</text>'
    else: 
        bl = (cx - v_base/2, bottom_y)
        br = (cx + v_base/2, bottom_y)
        if tri_type == "isosceles":
            top_x = cx
        else:
            offset = random.choice([-v_base*0.3, v_base*0.25, v_base*0.35])
            top_x = cx + offset

        top = (top_x, top_y)
        pts = f"{top[0]},{top[1]} {br[0]},{br[1]} {bl[0]},{bl[1]}"
        svg += f'<polygon points="{pts}" fill="#e8f8f5" stroke="#2c3e50" stroke-width="2.5"/>'
        svg += f'<line x1="{top_x}" y1="{top_y}" x2="{top_x}" y2="{bottom_y}" stroke="#e74c3c" stroke-width="2.5" stroke-dasharray="6,4"/>'
        s = 12
        svg += f'<polyline points="{top_x},{bottom_y-s} {top_x+s},{bottom_y-s} {top_x+s},{bottom_y}" fill="none" stroke="#e74c3c" stroke-width="2.5"/>'
        svg += f'<text x="{cx}" y="{bottom_y + 30}" font-family="Sarabun" font-size="18" font-weight="bold" text-anchor="middle" fill="#2980b9">ฐาน {base_val} {unit}</text>'
        svg += f'<text x="{top_x + 10}" y="{cy}" font-family="Sarabun" font-size="18" font-weight="bold" text-anchor="start" fill="#e74c3c">สูง {height_val} {unit}</text>'

    svg += '</svg>'
    return f'''<div style="display:flex; justify-content:center; margin: 20px 0;">
        <div style="border: 1px solid #bdc3c7; border-radius: 12px; padding: 25px; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            {svg}
        </div></div>'''

def draw_p4_kite_svg(sides, unit="ซม."):
    svg_w, svg_h = 450, 250
    cx, cy = 225, 125
    svg = f'<svg width="{svg_w}" height="{svg_h}">'
    
    half_w = random.randint(55, 95)    
    top_h = random.randint(30, 50)     
    bottom_h = random.randint(65, 105) 
    
    top = (cx, cy - top_h)
    right = (cx + half_w, cy)
    bottom = (cx, cy + bottom_h)
    left = (cx - half_w, cy)
    pts = f"{top[0]},{top[1]} {right[0]},{right[1]} {bottom[0]},{bottom[1]} {left[0]},{left[1]}"
    svg += f'<polygon points="{pts}" fill="#fcfcfc" stroke="#2c3e50" stroke-width="2.5"/>'
    
    def get_perpendicular_angle(p1, p2):
        return math.degrees(math.atan2(p2[1] - p1[1], p2[0] - p1[0]))

    for p1, p2 in [(left, top), (top, right)]:
        mx, my = (p1[0]+p2[0])/2, (p1[1]+p2[1])/2
        angle = get_perpendicular_angle(p1, p2)
        svg += f'<line x1="{mx}" y1="{my-8}" x2="{mx}" y2="{my+8}" stroke="#3498db" stroke-width="2.5" stroke-linecap="round" transform="rotate({angle}, {mx}, {my})"/>'
        
    for p1, p2 in [(left, bottom), (right, bottom)]:
        mx, my = (p1[0]+p2[0])/2, (p1[1]+p2[1])/2
        angle = get_perpendicular_angle(p1, p2)
        svg += f'<line x1="{mx-3}" y1="{my-8}" x2="{mx-3}" y2="{my+8}" stroke="#e74c3c" stroke-width="2.5" stroke-linecap="round" transform="rotate({angle}, {mx}, {my})"/>'
        svg += f'<line x1="{mx+3}" y1="{my-8}" x2="{mx+3}" y2="{my+8}" stroke="#e74c3c" stroke-width="2.5" stroke-linecap="round" transform="rotate({angle}, {mx}, {my})"/>'

    mx_top, my_top = (top[0]+right[0])/2, (top[1]+right[1])/2
    svg += f'<text x="{mx_top + 15}" y="{my_top - 10}" font-family="Sarabun" font-size="18" font-weight="bold" text-anchor="start" fill="#2980b9">{sides[0]} {unit}</text>'
    mx_bot, my_bot = (right[0]+bottom[0])/2, (right[1]+bottom[1])/2
    svg += f'<text x="{mx_bot + 15}" y="{my_bot + 25}" font-family="Sarabun" font-size="18" font-weight="bold" text-anchor="start" fill="#2980b9">{sides[1]} {unit}</text>'

    svg += '</svg>'
    return f'''<div style="display:flex; justify-content:center; margin: 20px 0;">
        <div style="border: 1px solid #bdc3c7; border-radius: 12px; padding: 25px; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            {svg}
        </div></div>'''

def draw_p4_rectangle_area_svg(shape_type, sides, unit="ซม."):
    svg_w, svg_h = 450, 250
    cx, cy = 225, 125
    svg = f'<svg width="{svg_w}" height="{svg_h}">'
    
    if shape_type == "square":
        v_side = 120 
        tl = (cx - v_side/2, cy - v_side/2)
        tr = (cx + v_side/2, cy - v_side/2)
        bl = (cx - v_side/2, cy + v_side/2)
        br = (cx + v_side/2, cy + v_side/2)
        pts = f"{tl[0]},{tl[1]} {tr[0]},{tr[1]} {br[0]},{br[1]} {bl[0]},{bl[1]}"
        svg += f'<polygon points="{pts}" fill="#ebf5fb" stroke="#2c3e50" stroke-width="2.5"/>'
        
        sides_to_tick = [(tl, tr, 0), (tr, br, 90), (br, bl, 0), (bl, tl, 90)]
        for p1, p2, angle in sides_to_tick:
            mx, my = (p1[0]+p2[0])/2, (p1[1]+p2[1])/2
            svg += f'<line x1="{mx}" y1="{my-6}" x2="{mx}" y2="{my+6}" stroke="#e74c3c" stroke-width="2.5" stroke-linecap="round" transform="rotate({angle}, {mx}, {my})"/>'
        svg += f'<text x="{cx}" y="{bl[1] + 30}" font-family="Sarabun" font-size="18" font-weight="bold" text-anchor="middle" fill="#2980b9">{sides[0]} {unit}</text>'

    else: 
        w_val, l_val = sides[0], sides[1] 
        ratio = w_val / l_val 
        v_length = 200 
        v_width = v_length * ratio 
        if v_width < 60: v_width = 60
        if v_width > 140: 
            v_width = 140
            v_length = v_width / ratio

        tl = (cx - v_length/2, cy - v_width/2)
        tr = (cx + v_length/2, cy - v_width/2)
        bl = (cx - v_length/2, cy + v_width/2)
        br = (cx + v_length/2, cy + v_width/2)
        pts = f"{tl[0]},{tl[1]} {tr[0]},{tr[1]} {br[0]},{br[1]} {bl[0]},{bl[1]}"
        svg += f'<polygon points="{pts}" fill="#ebf5fb" stroke="#2c3e50" stroke-width="2.5"/>'
        
        for p1, p2 in [(tl, tr), (br, bl)]:
            mx, my = (p1[0]+p2[0])/2, (p1[1]+p2[1])/2
            svg += f'<line x1="{mx-3}" y1="{my-6}" x2="{mx-3}" y2="{my+6}" stroke="#e74c3c" stroke-width="2.5" stroke-linecap="round"/>'
            svg += f'<line x1="{mx+3}" y1="{my-6}" x2="{mx+3}" y2="{my+6}" stroke="#e74c3c" stroke-width="2.5" stroke-linecap="round"/>'
            
        for p1, p2 in [(tr, br), (bl, tl)]:
            mx, my = (p1[0]+p2[0])/2, (p1[1]+p2[1])/2
            svg += f'<line x1="{mx-6}" y1="{my}" x2="{mx+6}" y2="{my}" stroke="#3498db" stroke-width="2.5" stroke-linecap="round"/>'

        svg += f'<text x="{cx}" y="{bl[1] + 30}" font-family="Sarabun" font-size="18" font-weight="bold" text-anchor="middle" fill="#2980b9">{sides[1]} {unit}</text>'
        svg += f'<text x="{tr[0] + 15}" y="{cy + 5}" font-family="Sarabun" font-size="18" font-weight="bold" text-anchor="start" fill="#2980b9">{sides[0]} {unit}</text>'

    s = 12
    svg += f'<polyline points="{tl[0]},{tl[1]+s} {tl[0]+s},{tl[1]+s} {tl[0]+s},{tl[1]}" fill="none" stroke="#2c3e50" stroke-width="2"/>'
    svg += f'<polyline points="{tr[0]-s},{tr[1]} {tr[0]-s},{tr[1]+s} {tr[0]},{tr[1]+s}" fill="none" stroke="#2c3e50" stroke-width="2"/>'
    svg += f'<polyline points="{br[0]},{br[1]-s} {br[0]-s},{br[1]-s} {br[0]-s},{br[1]}" fill="none" stroke="#2c3e50" stroke-width="2"/>'
    svg += f'<polyline points="{bl[0]+s},{bl[1]} {bl[0]+s},{bl[1]-s} {bl[0]},{bl[1]-s}" fill="none" stroke="#2c3e50" stroke-width="2"/>'

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
        tl, tr = (cx - 30, cy - 52), (cx + 90, cy - 52)
        bl, br = (cx - 90, cy + 52), (cx + 30, cy + 52)
        pts = f"{tl[0]},{tl[1]} {tr[0]},{tr[1]} {br[0]},{br[1]} {bl[0]},{bl[1]}"
        svg += f'<polygon points="{pts}" fill="#fcfcfc" stroke="#2c3e50" stroke-width="2.5"/>'
        
        sides_to_tick = [(tl, tr, 0), (tr, br, -60), (br, bl, 0), (bl, tl, -60)]
        for p1, p2, angle in sides_to_tick:
            mx, my = (p1[0]+p2[0])/2, (p1[1]+p2[1])/2
            svg += f'<line x1="{mx}" y1="{my-8}" x2="{mx}" y2="{my+8}" stroke="#e74c3c" stroke-width="2.5" stroke-linecap="round" transform="rotate({angle}, {mx}, {my})"/>'
        svg += f'<text x="{cx - 30}" y="{cy + 85}" font-family="Sarabun" font-size="18" font-weight="bold" text-anchor="middle" fill="#2980b9">{sides[0]} {unit}</text>'
    else: 
        tl, tr = (cx - 57.5, cy - 39), (cx + 102.5, cy - 39)
        bl, br = (cx - 102.5, cy + 39), (cx + 57.5, cy + 39)
        pts = f"{tl[0]},{tl[1]} {tr[0]},{tr[1]} {br[0]},{br[1]} {bl[0]},{bl[1]}"
        svg += f'<polygon points="{pts}" fill="#fcfcfc" stroke="#2c3e50" stroke-width="2.5"/>'
        
        for p1, p2 in [(tl, tr), (br, bl)]:
            mx, my = (p1[0]+p2[0])/2, (p1[1]+p2[1])/2
            svg += f'<line x1="{mx-3}" y1="{my-8}" x2="{mx-3}" y2="{my+8}" stroke="#e74c3c" stroke-width="2.5" stroke-linecap="round"/>'
            svg += f'<line x1="{mx+3}" y1="{my-8}" x2="{mx+3}" y2="{my+8}" stroke="#e74c3c" stroke-width="2.5" stroke-linecap="round"/>'
        
        for p1, p2 in [(tr, br), (bl, tl)]:
            mx, my = (p1[0]+p2[0])/2, (p1[1]+p2[1])/2
            svg += f'<line x1="{mx}" y1="{my-8}" x2="{mx}" y2="{my+8}" stroke="#3498db" stroke-width="2.5" stroke-linecap="round" transform="rotate(-60, {mx}, {my})"/>'

        svg += f'<text x="{cx - 22.5}" y="{cy + 75}" font-family="Sarabun" font-size="18" font-weight="bold" text-anchor="middle" fill="#2980b9">{sides[0]} {unit}</text>'
        svg += f'<text x="{cx + 100}" y="{cy + 5}" font-family="Sarabun" font-size="18" font-weight="bold" text-anchor="start" fill="#2980b9">{sides[1]} {unit}</text>'

    svg += '</svg>'
    return f'''<div style="display:flex; justify-content:center; margin: 20px 0;">
        <div style="border: 1px solid #bdc3c7; border-radius: 12px; padding: 25px; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            {svg}
        </div></div>'''

def draw_p4_triangle_perimeter_svg(triangle_type, sides, unit="ซม."):
    svg_w, svg_h = 450, 250
    cx, cy = 225, 125 
    svg = f'<svg width="{svg_w}" height="{svg_h}">'
    
    if triangle_type == "right_angled":
        p_right, p_top, p_base = (160, 190), (160, 70), (300, 190)
        pts = f"{p_right[0]},{p_right[1]} {p_top[0]},{p_top[1]} {p_base[0]},{p_base[1]}"
        svg += f'<polygon points="{pts}" fill="#fcfcfc" stroke="#2c3e50" stroke-width="2.5"/>'
        s = 15
        svg += f'<polyline points="{p_right[0]},{p_right[1]-s} {p_right[0]+s},{p_right[1]-s} {p_right[0]+s},{p_right[1]}" fill="none" stroke="#2c3e50" stroke-width="1.5"/>'
        svg += f'<text x="150" y="130" font-family="Sarabun" font-size="18" font-weight="bold" text-anchor="end" fill="#2980b9">{sides[0]} {unit}</text>'
        svg += f'<text x="230" y="215" font-family="Sarabun" font-size="18" font-weight="bold" text-anchor="middle" fill="#2980b9">{sides[1]} {unit}</text>' 
        svg += f'<text x="245" y="120" font-family="Sarabun" font-size="18" font-weight="bold" text-anchor="start" fill="#2980b9">{sides[2]} {unit}</text>'
    else:
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
        else: 
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
# 2. ฐานข้อมูลหลักสูตร (Master Database P.4)
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
    }
}

# ==========================================
# 3. Logic & Dynamic Difficulty Scaling (P.4)
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
                    q = f"มุมบนเส้นตรงรวมกันได้ 180 องศา ถ้ามุมหนึ่งกาง <b>{180-ans}°</b> จงหาขนาดของมุม <b>x</b> ที่เหลือ?<br>{svg}"
                    sol = f"<span style='color:#2c3e50;'><b>ตอบ: {ans}°</b></span>"

            elif actual_sub_t == "การสร้างมุมตามขนาดที่กำหนด":
                bad_words = ["KUY", "KVY", "FUG", "FUQ", "FUC", "FUK", "SUK", "SUC", "CUM", "DIC", "DIK", "SEX", "ASS", "TIT", "FAP", "GAY", "PEE", "POO", "WTF", "BUM", "DOG", "PIG", "FAT", "SAD", "BAD", "MAD", "DIE", "RIP", "SOB"]
                while True:
                    p1, v, p2 = random.sample(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"), 3)
                    angle_name = f"{p1}{v}{p2}"
                    angle_name_rev = f"{p2}{v}{p1}"
                    if angle_name not in bad_words and angle_name_rev not in bad_words:
                        break
                        
                hat_v = f"<span style='position:relative; display:inline-block;'>{v}<span style='position:absolute; top:-12px; left:50%; transform:translateX(-50%); color:#e74c3c; font-weight:normal; font-size:22px;'>^</span></span>"
                angle_name_display = f"{p1}{hat_v}{p2}"
                target_deg = random.randint(20, 160)
                
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
                
                cx, cy = 280, 220
                r_out, r_in = 140, 100
                svg_sol = '<div style="text-align:center; margin:15px 0;"><svg width="560" height="260">'
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

                rad = math.radians(target_deg)
                end_x, end_y = cx + 180 * math.cos(rad), cy - 180 * math.sin(rad)
                svg_sol += f'<line x1="{cx}" y1="{cy}" x2="{cx+180}" y2="{cy}" stroke="#34495e" stroke-width="2.5"/>'
                svg_sol += f'<line x1="{cx}" y1="{cy}" x2="{end_x}" y2="{end_y}" stroke="#e74c3c" stroke-width="1.5" stroke-linecap="round"/>'
                svg_sol += f'<circle cx="{cx}" cy="{cy}" r="4" fill="#2c3e50"/><circle cx="{cx+180}" cy="{cy}" r="3" fill="#2c3e50"/><circle cx="{end_x}" cy="{end_y}" r="4" fill="#e74c3c"/>'
                
                svg_sol += f'<text x="{cx-5}" y="{cy+20}" font-family="sans-serif" font-size="18" font-weight="bold" fill="#2c3e50" text-anchor="middle">{v}</text>'
                svg_sol += f'<text x="{cx+195}" y="{cy+5}" font-family="sans-serif" font-size="18" font-weight="bold" fill="#2c3e50" text-anchor="middle">{p2}</text>'
                tx_p1, ty_p1 = cx + 200 * math.cos(rad), cy - 200 * math.sin(rad)
                svg_sol += f'<text x="{tx_p1}" y="{ty_p1+5}" font-family="sans-serif" font-size="18" font-weight="bold" fill="#e74c3c" text-anchor="middle">{p1}</text>'
                
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
                
                def draw_exam_rect(w_real, h_real, w_text, h_text, is_sq):
                    svg_w, svg_h = 450, 250
                    draw_w = 160 if is_sq else 240
                    draw_h = 160 if is_sq else 120
                    ox = (svg_w - draw_w) / 2
                    oy = (svg_h - draw_h) / 2
                    
                    svg = f'<svg width="{svg_w}" height="{svg_h}">'
                    svg += f'<rect x="{ox}" y="{oy}" width="{draw_w}" height="{draw_h}" fill="#fcfcfc" stroke="#2c3e50" stroke-width="2.5"/>'
                    
                    s = 12 
                    svg += f'<polyline points="{ox},{oy+s} {ox+s},{oy+s} {ox+s},{oy}" fill="none" stroke="#2c3e50" stroke-width="1.5"/>'
                    svg += f'<polyline points="{ox+draw_w-s},{oy} {ox+draw_w-s},{oy+s} {ox+draw_w},{oy+s}" fill="none" stroke="#2c3e50" stroke-width="1.5"/>'
                    svg += f'<polyline points="{ox},{oy+draw_h-s} {ox+s},{oy+draw_h-s} {ox+s},{oy+draw_h}" fill="none" stroke="#2c3e50" stroke-width="1.5"/>'
                    svg += f'<polyline points="{ox+draw_w-s},{oy+draw_h} {ox+draw_w-s},{oy+draw_h-s} {ox+draw_w},{oy+draw_h-s}" fill="none" stroke="#2c3e50" stroke-width="1.5"/>'
                    
                    tick_len = 8
                    mid_top_x, mid_top_y = ox + draw_w/2, oy
                    mid_bot_x, mid_bot_y = ox + draw_w/2, oy + draw_h
                    mid_l_x, mid_l_y = ox, oy + draw_h/2
                    mid_r_x, mid_r_y = ox + draw_w, oy + draw_h/2
                    
                    if is_sq:
                        svg += f'<line x1="{mid_top_x}" y1="{mid_top_y-tick_len}" x2="{mid_top_x}" y2="{mid_top_y+tick_len}" stroke="#e74c3c" stroke-width="2"/>'
                        svg += f'<line x1="{mid_bot_x}" y1="{mid_bot_y-tick_len}" x2="{mid_bot_x}" y2="{mid_bot_y+tick_len}" stroke="#e74c3c" stroke-width="2"/>'
                        svg += f'<line x1="{mid_l_x-tick_len}" y1="{mid_l_y}" x2="{mid_l_x+tick_len}" y2="{mid_l_y}" stroke="#e74c3c" stroke-width="2"/>'
                        svg += f'<line x1="{mid_r_x-tick_len}" y1="{mid_r_y}" x2="{mid_r_x+tick_len}" y2="{mid_r_y}" stroke="#e74c3c" stroke-width="2"/>'
                    else:
                        svg += f'<line x1="{mid_top_x-4}" y1="{mid_top_y-tick_len}" x2="{mid_top_x-4}" y2="{mid_top_y+tick_len}" stroke="#e74c3c" stroke-width="2"/>'
                        svg += f'<line x1="{mid_top_x+4}" y1="{mid_top_y-tick_len}" x2="{mid_top_x+4}" y2="{mid_top_y+tick_len}" stroke="#e74c3c" stroke-width="2"/>'
                        svg += f'<line x1="{mid_bot_x-4}" y1="{mid_bot_y-tick_len}" x2="{mid_bot_x-4}" y2="{mid_bot_y+tick_len}" stroke="#e74c3c" stroke-width="2"/>'
                        svg += f'<line x1="{mid_bot_x+4}" y1="{mid_bot_y-tick_len}" x2="{mid_bot_x+4}" y2="{mid_bot_y+tick_len}" stroke="#e74c3c" stroke-width="2"/>'
                        svg += f'<line x1="{mid_l_x-tick_len}" y1="{mid_l_y}" x2="{mid_l_x+tick_len}" y2="{mid_l_y}" stroke="#3498db" stroke-width="2"/>'
                        svg += f'<line x1="{mid_r_x-tick_len}" y1="{mid_r_y}" x2="{mid_r_x+tick_len}" y2="{mid_r_y}" stroke="#3498db" stroke-width="2"/>'

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
                    if random.choice([True, False]): w, h = h, w
                    peri = 2 * (w + h)
                    if w > h: svg = draw_exam_rect(w, h, f"{w} {units}", f"{h} {units}", is_sq=False)
                    else: svg = draw_exam_rect(h, w, f"{h} {units}", f"{w} {units}", is_sq=False)
                        
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
                tri_mode = random.choice(["equilateral", "isosceles", "scalene", "right_angled"])
                
                if tri_mode == "right_angled":
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
                
                else:
                    s1, s2, s3 = random.randint(30, 60), random.randint(40, 70), random.randint(50, 80)
                    peri = s1 + s2 + s3
                    svg = draw_p4_triangle_perimeter_svg("scalene", [s1, s2, s3], unit)
                    q = f"จงหาความยาวรอบรูปของรูปสามเหลี่ยมที่มีความยาวแต่ละด้านตามที่กำหนดให้<br>{svg}"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b> {s1} + {s2} + {s3} = <b>{peri} {unit}</b></span>"

            elif actual_sub_t == "การหาความยาวรอบรูปสี่เหลี่ยมด้านขนานและขนมเปียกปูน":
                unit = random.choice(["ซม.", "ม.", "วา"])
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
                
                else: 
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
                s1 = random.randint(15, 60)
                s2 = random.randint(s1 + 12, s1 + 80)
                peri = 2 * (s1 + s2)
                svg = draw_p4_kite_svg([s1, s2], unit)
                q = f"พิจารณารูป<b>สี่เหลี่ยมรูปว่าว</b>ที่กำหนดให้ (มีด้านประชิดยาวเท่ากัน 2 คู่) จงหาความยาวรอบรูปทั้งหมด<br>{svg}"
                sol = f"""<span style='color:#2c3e50;'>
                <div style='background-color:#fef8eb; border-left:4px solid #f39c12; padding:15px; margin-bottom:15px; border-radius:8px;'>
                💡 <b>สมบัติของสี่เหลี่ยมรูปว่าว:</b><br>
                ด้านที่อยู่ติดกัน (ประชิดกัน) จะมีความยาวเท่ากัน 2 คู่เสมอ<br>
                <i>(สังเกตจากสัญลักษณ์ 1 ขีดสีน้ำเงินคู่บน และ 2 ขีดสีแดงคู่ล่างที่ตั้งฉากกับเส้น)</i>
                </div>
                <b>วิธีทำอย่างละเอียด Step-by-Step:</b><br>
                👉 <b>ขั้นที่ 1:</b> คู่ที่ 1 (ด้านบน) มีสัญลักษณ์ 1 ขีด 2 ด้าน ยาวด้านละ {s1} {unit} ➔ รวมเป็น {s1} + {s1} = {s1*2} {unit}<br>
                👉 <b>ขั้นที่ 2:</b> คู่ที่ 2 (ด้านล่าง) มีสัญลักษณ์ 2 ขีด 2 ด้าน ยาวด้านละ {s2} {unit} ➔ รวมเป็น {s2} + {s2} = {s2*2} {unit}<br>
                👉 <b>ขั้นที่ 3:</b> นำความยาวทั้ง 4 ด้านมารวมกัน ➔ {s1*2} + {s2*2} = <b>{peri} {unit}</b><br>
                <i>(หรือคำนวณจากสูตร: 2 × (ความยาวด้านสั้น + ความยาวด้านยาว) ➔ 2 × ({s1} + {s2}) = <b>{peri}</b>)</i><br><br>
                <b>ตอบ: ความยาวรอบรูปของรูปสี่เหลี่ยมรูปว่าวนี้คือ {peri} {unit}</b></span>"""

            elif actual_sub_t == "การหาพื้นที่รูปสี่เหลี่ยมมุมฉาก":
                unit = random.choice(["ซม.", "ม.", "วา"])
                mode = random.choice(["square", "rectangle"])
                if mode == "square":
                    side = random.randint(12, 45)
                    area = side * side
                    svg = draw_p4_rectangle_area_svg("square", [side], unit)
                    q = f"พิจารณารูป<b>สี่เหลี่ยมจัตุรัส</b>ที่กำหนดให้ (มีสัญลักษณ์มุมฉากและด้านยาวเท่ากันทุกด้าน) จงหา<b>พื้นที่</b>ของรูปสี่เหลี่ยมนี้<br>{svg}"
                    sol = f"""<span style='color:#2c3e50;'>
                    <div style='background-color:#e8f8f5; border-left:4px solid #1abc9c; padding:15px; margin-bottom:15px; border-radius:8px;'>
                    💡 <b>สูตรการหาพื้นที่สี่เหลี่ยมจัตุรัส:</b><br>
                    <b>พื้นที่</b> = ความยาวด้าน × ความยาวด้าน (หรือ ด้าน × ด้าน)
                    </div>
                    <b>วิธีทำอย่างละเอียด Step-by-Step:</b><br>
                    👉 <b>ขั้นที่ 1:</b> จากรูป ความยาวด้านคือ {side} {unit}<br>
                    👉 <b>ขั้นที่ 2:</b> แทนค่าในสูตร ➔ {side} × {side}<br>
                    👉 <b>ขั้นที่ 3:</b> คำนวณผลคูณ ➔ {side} × {side} = <b>{area:,}</b><br><br>
                    <b>ตอบ: พื้นที่ของรูปสี่เหลี่ยมจัตุรัสคือ {area:,} ตาราง{unit.replace('.','')}</b></span>"""
                else: 
                    width = random.randint(10, 35)
                    length = random.randint(width + 5, width + 50)
                    area = width * length
                    svg = draw_p4_rectangle_area_svg("rectangle", [width, length], unit)
                    q = f"พิจารณารูป<b>สี่เหลี่ยมผืนผ้า</b>ที่กำหนดให้ จงหา<b>พื้นที่</b>ของรูปสี่เหลี่ยมส่วนที่ระบายสี<br>{svg}"
                    sol = f"""<span style='color:#2c3e50;'>
                    <div style='background-color:#e8f8f5; border-left:4px solid #1abc9c; padding:15px; margin-bottom:15px; border-radius:8px;'>
                    💡 <b>สูตรการหาพื้นที่สี่เหลี่ยมผืนผ้า:</b><br>
                    <b>พื้นที่</b> = ความกว้าง × ความยาว (หรือ กว้าง × ยาว)
                    </div>
                    <b>วิธีทำอย่างละเอียด Step-by-Step:</b><br>
                    👉 <b>ขั้นที่ 1:</b> จากรูป ความกว้าง (ด้านสั้น) = {width} {unit} และ ความยาว (ด้านยาว) = {length} {unit}<br>
                    👉 <b>ขั้นที่ 2:</b> แทนค่าในสูตร ➔ {width} × {length}<br>
                    👉 <b>ขั้นที่ 3:</b> คำนวณผลคูณ ➔ {width} × {length} = <b>{area:,}</b><br><br>
                    <b>ตอบ: พื้นที่ของรูปสี่เหลี่ยมผืนผ้าคือ {area:,} ตาราง{unit.replace('.','')}</b></span>"""

            elif actual_sub_t == "การหาพื้นที่รูปสามเหลี่ยม (พื้นฐาน)":
                unit = random.choice(["ซม.", "ม.", "วา"])
                tri_type = random.choice(["right", "isosceles", "scalene"])
                base = random.randint(6, 30) * 2 
                height = random.randint(8, 45)
                area = (base * height) // 2
                svg = draw_p4_triangle_area_svg(tri_type, base, height, unit)
                if tri_type == "right":
                    q = f"พิจารณารูป<b>สามเหลี่ยมมุมฉาก</b>ที่กำหนดให้ จงหา<b>พื้นที่</b>ของรูปสามเหลี่ยมนี้<br>{svg}"
                else:
                    q = f"พิจารณารูป<b>สามเหลี่ยม</b>ที่กำหนดให้ (มีเส้นประบอกความสูง) จงหา<b>พื้นที่</b>ของรูปสามเหลี่ยมนี้<br>{svg}"
                sol = f"""<span style='color:#2c3e50;'>
                <div style='background-color:#e8f8f5; border-left:4px solid #1abc9c; padding:15px; margin-bottom:15px; border-radius:8px;'>
                💡 <b>สูตรการหาพื้นที่รูปสามเหลี่ยม:</b><br>
                <b>พื้นที่</b> = &frac12; × ความยาวฐาน × ความสูง<br>
                <i>(หรือนำ ฐาน คูณ สูง แล้วหารด้วย 2)</i>
                </div>
                <b>วิธีทำอย่างละเอียด Step-by-Step:</b><br>
                👉 <b>ขั้นที่ 1:</b> จากรูป ระบุความยาวฐาน = <b style="color:#2980b9;">{base} {unit}</b> และ ความสูง = <b style="color:#e74c3c;">{height} {unit}</b><br>
                👉 <b>ขั้นที่ 2:</b> แทนค่าในสูตร ➔ &frac12; × {base} × {height}<br>
                👉 <b>ขั้นที่ 3:</b> จับคู่หาร 2 ให้ง่ายขึ้น ➔ (ครึ่งหนึ่งของ {base} คือ {base//2})<br>
                👉 <b>ขั้นที่ 4:</b> คำนวณผลคูณ ➔ {base//2} × {height} = <b>{area:,}</b><br><br>
                <b>ตอบ: พื้นที่ของรูปสามเหลี่ยมนี้คือ {area:,} ตาราง{unit.replace('.','')}</b></span>"""

            elif actual_sub_t == "การหาพื้นที่สี่เหลี่ยมด้านขนานและขนมเปียกปูน (พื้นฐาน)":
                unit = random.choice(["ซม.", "ม.", "วา"])
                mode = random.choice(["parallelogram", "rhombus"])
                base = random.randint(15, 60)
                height = random.randint(10, base - 2) if base > 12 else random.randint(10, 30)
                area = base * height
                if mode == "rhombus":
                    svg = draw_p4_parallelogram_rhombus_area_svg("rhombus", base, height, unit)
                    q = f"พิจารณารูป<b>สี่เหลี่ยมขนมเปียกปูน</b>ที่กำหนดให้ (สังเกตเส้นประบอกความสูง) จงหา<b>พื้นที่</b>ของรูปสี่เหลี่ยมนี้<br>{svg}"
                else:
                    svg = draw_p4_parallelogram_rhombus_area_svg("parallelogram", base, height, unit)
                    q = f"พิจารณารูป<b>สี่เหลี่ยมด้านขนาน</b>ที่กำหนดให้ (สังเกตเส้นประบอกความสูง) จงหา<b>พื้นที่</b>ของรูปสี่เหลี่ยมนี้<br>{svg}"
                sol = f"""<span style='color:#2c3e50;'>
                <div style='background-color:#e8f8f5; border-left:4px solid #1abc9c; padding:15px; margin-bottom:15px; border-radius:8px;'>
                💡 <b>สูตรการหาพื้นที่สี่เหลี่ยมด้านขนานและขนมเปียกปูน:</b><br>
                <b>พื้นที่</b> = ความยาวฐาน × ความสูง
                </div>
                <b>วิธีทำอย่างละเอียด Step-by-Step:</b><br>
                👉 <b>ขั้นที่ 1:</b> จากรูป ระบุความยาวฐาน = <b style="color:#2980b9;">{base} {unit}</b> และ ความสูง (เส้นตั้งฉาก) = <b style="color:#e74c3c;">{height} {unit}</b><br>
                👉 <b>ขั้นที่ 2:</b> นำตัวเลขมาแทนค่าในสูตร ➔ {base} × {height}<br>
                👉 <b>ขั้นที่ 3:</b> คำนวณผลคูณ ➔ {base} × {height} = <b>{area:,}</b><br><br>
                <b>ตอบ: พื้นที่ของรูปสี่เหลี่ยมนี้คือ {area:,} ตาราง{unit.replace('.','')}</b></span>"""

            elif actual_sub_t == "การหาพื้นที่โดยการนับตาราง":
                unit = random.choice(["ตร.ซม.", "ตร.ม.", "ตารางหน่วย"])
                shapes_list = ["L", "T", "U", "Plus", "Stair", "Rectangle"]
                choice = random.choice(shapes_list)
                c_blue, c_red, c_green = "#3498db", "#e74c3c", "#2ecc71"

                if choice == "Rectangle":
                    w, h = random.randint(3, 7), random.randint(3, 6)
                    pts = [(0,0), (w,0), (w,h), (0,h)]
                    rects = [(0, 0, w, h, c_blue)]
                    area = w * h
                    calc_steps = f"รูปนี้เป็นรูปสี่เหลี่ยมมุมฉากอยู่แล้ว ไม่ต้องแบ่งส่วนย่อย<br>👉 <b style='color:{c_blue};'>ส่วนสีฟ้า:</b> กว้าง {w} ช่อง × ยาว {h} ช่อง = <b>{area}</b> ช่อง"
                elif choice == "L":
                    t = random.randint(1, 2)
                    h, w = random.randint(4, 7), random.randint(4, 7)
                    pts = [(0,0), (t,0), (t,h-t), (w,h-t), (w,h), (0,h)]
                    rects = [(0, 0, t, h, c_blue), (t, h-t, w-t, t, c_red)]
                    area = (t*h) + ((w-t)*t)
                    calc_steps = f"แบ่งรูปออกเป็น 2 ส่วนย่อย เพื่อคำนวณแยกกัน:<br>👉 <b style='color:{c_blue};'>ส่วนที่ 1 (สีฟ้า):</b> กว้าง {t} × ยาว {h} = {t*h} ช่อง<br>👉 <b style='color:{c_red};'>ส่วนที่ 2 (สีแดง):</b> กว้าง {w-t} × ยาว {t} = {(w-t)*t} ช่อง<br>👉 นำพื้นที่มารวมกัน = {t*h} + {(w-t)*t} = <b>{area}</b> ช่อง"
                elif choice == "T":
                    t = random.randint(1, 2)
                    w = random.choice([5, 7]) 
                    h = random.randint(4, 7)
                    stem_w = random.choice([1, 3])
                    margin = (w - stem_w) // 2
                    pts = [(0,0), (w,0), (w,t), (margin+stem_w,t), (margin+stem_w,h), (margin,h), (margin,t), (0,t)]
                    rects = [(0, 0, w, t, c_blue), (margin, t, stem_w, h-t, c_red)]
                    area = (w*t) + (stem_w*(h-t))
                    calc_steps = f"แบ่งรูปออกเป็น 2 ส่วน (ส่วนหัวและก้าน):<br>👉 <b style='color:{c_blue};'>ส่วนหัว (สีฟ้า):</b> กว้าง {w} × ยาว {t} = {w*t} ช่อง<br>👉 <b style='color:{c_red};'>ส่วนก้าน (สีแดง):</b> กว้าง {stem_w} × ยาว {h-t} = {stem_w*(h-t)} ช่อง<br>👉 นำพื้นที่มารวมกัน = {w*t} + {stem_w*(h-t)} = <b>{area}</b> ช่อง"
                elif choice == "U":
                    t = random.randint(1, 2)
                    w = random.choice([5, 6, 7])
                    h = random.randint(4, 6)
                    pts = [(0,0), (t,0), (t,h-t), (w-t,h-t), (w-t,0), (w,0), (w,h), (0,h)]
                    rects = [(0, 0, t, h, c_blue), (w-t, 0, t, h, c_red), (t, h-t, w-2*t, t, c_green)]
                    area = (t*h) + (t*h) + ((w-2*t)*t)
                    calc_steps = f"แบ่งรูปตัว U ออกเป็น 3 แท่ง:<br>👉 <b style='color:{c_blue};'>ขาซ้าย (สีฟ้า):</b> กว้าง {t} × ยาว {h} = {t*h} ช่อง<br>👉 <b style='color:{c_red};'>ขาขวา (สีแดง):</b> กว้าง {t} × ยาว {h} = {t*h} ช่อง<br>👉 <b style='color:{c_green};'>ฐานเชื่อม (สีเขียว):</b> กว้าง {w-2*t} × ยาว {t} = {(w-2*t)*t} ช่อง<br>👉 นำพื้นที่มารวมกัน = {t*h} + {t*h} + {(w-2*t)*t} = <b>{area}</b> ช่อง"
                elif choice == "Plus":
                    t = random.randint(1, 2)
                    arm = random.randint(1, 2)
                    w, h = t + arm*2, t + arm*2
                    pts = [(arm,0), (arm+t,0), (arm+t,arm), (w,arm), (w,arm+t), (arm+t,arm+t), (arm+t,h), (arm,h), (arm,arm+t), (0,arm+t), (0,arm), (arm,arm)]
                    rects = [(arm, 0, t, h, c_blue), (0, arm, arm, t, c_red), (arm+t, arm, arm, t, c_green)]
                    area = (t*h) + (arm*t) + (arm*t)
                    calc_steps = f"แบ่งรูปกากบาทออกเป็น 3 ส่วน:<br>👉 <b style='color:{c_blue};'>แกนกลาง (สีฟ้า):</b> กว้าง {t} × ยาว {h} = {t*h} ช่อง<br>👉 <b style='color:{c_red};'>แขนซ้าย (สีแดง):</b> กว้าง {arm} × ยาว {t} = {arm*t} ช่อง<br>👉 <b style='color:{c_green};'>แขนขวา (สีเขียว):</b> กว้าง {arm} × ยาว {t} = {arm*t} ช่อง<br>👉 นำพื้นที่มารวมกัน = {t*h} + {arm*t} + {arm*t} = <b>{area}</b> ช่อง"
                elif choice == "Stair":
                    step_w, step_h = random.randint(1, 2), random.randint(1, 2)
                    pts = [(0, 0), (step_w, 0), (step_w, step_h), (step_w*2, step_h), (step_w*2, step_h*2), (step_w*3, step_h*2), (step_w*3, step_h*3), (0, step_h*3)]
                    col1, col2, col3 = 3*step_h*step_w, 2*step_h*step_w, 1*step_h*step_w
                    rects = [(0, 0, step_w, 3*step_h, c_blue), (step_w, step_h, step_w, 2*step_h, c_red), (step_w*2, step_h*2, step_w, step_h, c_green)]
                    area = col1 + col2 + col3
                    calc_steps = f"แบ่งรูปขั้นบันไดเป็นแท่งแนวตั้ง 3 แท่ง:<br>👉 <b style='color:{c_blue};'>แท่งที่ 1 (สีฟ้า):</b> กว้าง {step_w} × ยาว {3*step_h} = {col1} ช่อง<br>👉 <b style='color:{c_red};'>แท่งที่ 2 (สีแดง):</b> กว้าง {step_w} × ยาว {2*step_h} = {col2} ช่อง<br>👉 <b style='color:{c_green};'>แท่งที่ 3 (สีเขียว):</b> กว้าง {step_w} × ยาว {step_h} = {col3} ช่อง<br>👉 นำพื้นที่มารวมกัน = {col1} + {col2} + {col3} = <b>{area}</b> ช่อง"

                max_x = max(p[0] for p in pts)
                max_y = max(p[1] for p in pts)
                offset_x = (14 - max_x) // 2
                offset_y = (8 - max_y) // 2
                final_pts = [(p[0]+offset_x, p[1]+offset_y) for p in pts]

                svg_q = draw_p4_grid_area_svg(final_pts, unit)
                svg_sol = draw_p4_grid_area_solution_svg(rects, unit)
                q = f"พิจารณารูปที่กำหนดให้บนตาราง จงหา<b>พื้นที่</b>ของส่วนที่ระบายสี<br>{svg_q}"
                sol = f"""<span style='color:#2c3e50;'>
                <div style='background-color:#f8f9f9; border-left:4px solid #8e44ad; padding:15px; margin-bottom:15px; border-radius:8px;'>
                💡 <b>เทคนิคการแบ่งรูป (Decomposition):</b><br>
                แทนที่จะเสียเวลานั่งนับทีละช่อง ให้เราขีดเส้นแบ่งรูปทรงที่ซับซ้อนออกเป็นสี่เหลี่ยมมุมฉากย่อยๆ จากนั้นใช้สูตร <b>(กว้าง × ยาว)</b> เพื่อหาพื้นที่แต่ละส่วน แล้วนำมารวมกันครับ
                </div>
                {svg_sol}
                <b>วิธีทำอย่างละเอียด Step-by-Step:</b><br>
                {calc_steps}<br><br>
                <b>ตอบ: พื้นที่ของรูประบายสีคือ {area} {unit}</b></span>"""

            elif actual_sub_t == "โจทย์ปัญหาเรขาคณิต (รั้วและพื้นที่ชีวิตจริง)":
                scenario_list = ["fence", "running", "frame", "tile", "carpet", "paint"]
                scenario = random.choice(scenario_list)
                shape_type = random.choice(["square", "rectangle"])
                c_blue, c_red = "#3498db", "#e74c3c"
                unit = "ซม." if scenario in ["frame", "carpet"] else "ม."
                
                if scenario in ["fence", "running", "frame"]:
                    if shape_type == "square":
                        side = random.randint(15, 60)
                        perimeter = side * 4
                        shape_desc = f"รูปสี่เหลี่ยมจัตุรัส (ด้านละ {side} {unit})"
                        step1_calc = f"{side} × 4 = <b style='color:{c_blue};'>{perimeter}</b> {unit}"
                        w, l = side, side
                    else:
                        w = random.randint(10, 30)
                        l = random.randint(w + 5, w + 30)
                        perimeter = (w + l) * 2
                        shape_desc = f"รูปสี่เหลี่ยมผืนผ้า (กว้าง {w} {unit}, ยาว {l} {unit})"
                        step1_calc = f"({w} + {l}) × 2 = <b style='color:{c_blue};'>{perimeter}</b> {unit}"

                    svg = draw_p4_real_life_geo_svg(scenario, shape_type, [w, l], unit)

                    if scenario == "fence":
                        persons = ["คุณพ่อ", "คุณตา", "ชาวสวน", "คุณป้า", "เจ้าของฟาร์ม", "ผู้รับเหมา"]
                        places = ["สวนผลไม้", "ฟาร์มเลี้ยงไก่", "แปลงดอกไม้", "บ่อปลา", "คอกม้า", "สนามเด็กเล่น"]
                        person = random.choice(persons)
                        place = random.choice(places)
                        cost = random.choice([50, 80, 120, 150])
                        ans = perimeter * cost
                        q = f"{person}ต้องการล้อมรั้วรอบ{place}{shape_desc} ถ้าค่าทำรั้ว{unit}ละ {cost} บาท จะต้องจ่ายเงินทั้งหมดเท่าไร?<br>{svg}"
                        step2_desc = f"นำความยาวรอบรูป คูณกับ ราคาต่อ{unit}"
                        step2_calc = f"{perimeter} × <b style='color:{c_red};'>{cost}</b> = <b style='color:#27ae60;'>{ans:,}</b> บาท"
                        ans_text = f"{ans:,} บาท"
                    elif scenario == "running":
                        persons = ["นักกีฬา", "นักเรียน", "คุณลุง", "ชาวบ้าน", "เด็กๆ", "คุณครูพละ"]
                        places = ["สนามฟุตบอล", "ลานออกกำลังกาย", "สวนสาธารณะ", "ลานกีฬากลางแจ้ง", "รอบสระว่ายน้ำ"]
                        person = random.choice(persons)
                        place = random.choice(places)
                        laps = random.choice([3, 4, 5, 6, 10])
                        ans = perimeter * laps
                        q = f"{person}มาซ้อมวิ่งรอบ{place}{shape_desc} ถ้า{person}วิ่งรอบสถานที่นี้ทั้งหมด <b>{laps} รอบ</b> จะวิ่งได้ระยะทางรวมกี่{unit}?<br>{svg}"
                        step2_desc = f"นำความยาว 1 รอบ คูณกับ จำนวนรอบที่วิ่ง"
                        step2_calc = f"{perimeter} × <b style='color:{c_red};'>{laps}</b> รอบ = <b style='color:#27ae60;'>{ans:,}</b> {unit}"
                        ans_text = f"{ans:,} {unit}"
                    elif scenario == "frame":
                        persons = ["นักเรียน", "คุณครู", "ประธานนักเรียน", "เจ้าของร้าน", "นักออกแบบ"]
                        places = ["บอร์ดนิทรรศการ", "ป้ายประกาศ", "กรอบรูปขนาดใหญ่", "ป้ายโฆษณา", "ขอบเวที"]
                        items = ["ติดแถบไฟ LED", "ติดริบบิ้น", "ตอกคิ้วไม้", "ติดกระดาษสีตกแต่ง"]
                        person = random.choice(persons)
                        place = random.choice(places)
                        item = random.choice(items)
                        cost = random.choice([15, 20, 25, 30])
                        ans = perimeter * cost
                        q = f"{person}ต้องการ{item}รอบขอบ{place}{shape_desc} ถ้าวัสดุตกแต่งราคา{unit}ละ {cost} บาท จะต้องจ่ายเงินกี่บาท?<br>{svg}"
                        step2_desc = f"นำความยาวรอบขอบ คูณกับ ราคาต่อ{unit}"
                        step2_calc = f"{perimeter} × <b style='color:{c_red};'>{cost}</b> = <b style='color:#27ae60;'>{ans:,}</b> บาท"
                        ans_text = f"{ans:,} บาท"

                    sol = f"""<span style='color:#2c3e50;'>
                    <div style='background-color:#fef5e7; border-left:4px solid #e67e22; padding:15px; margin-bottom:15px; border-radius:8px;'>
                    💡 <b>วิเคราะห์โจทย์ (ล้อมรอบขอบ = ความยาวรอบรูป):</b><br>
                    คำว่า "ล้อมรั้ว, วิ่งรอบ, ตกแต่งขอบ" หมายถึงการหา <b>ความยาวรอบรูป</b> จากนั้นค่อยนำไปคำนวณราคาหรือจำนวนรอบตามที่โจทย์ถามครับ
                    </div>
                    <b>วิธีทำอย่างละเอียด Step-by-Step:</b><br>
                    👉 <b>ขั้นที่ 1: หาความยาวรอบรูป 1 รอบ</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;พื้นที่เป็น {shape_desc}<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;ความยาวรอบรูป = {step1_calc}<br>
                    👉 <b>ขั้นที่ 2: คำนวณสิ่งที่โจทย์ถามหา</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;{step2_desc}<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;➔ {step2_calc}<br><br>
                    <b>ตอบ: {ans_text}</b></span>"""

                else:
                    if shape_type == "square":
                        side = random.randint(5, 20)
                        area = side * side
                        shape_desc = f"รูปสี่เหลี่ยมจัตุรัส (ด้านละ {side} {unit})"
                        step1_calc = f"{side} × {side} = <b style='color:{c_blue};'>{area:,}</b> ตาราง{unit}"
                        w, l = side, side
                    else:
                        w = random.randint(4, 15)
                        l = random.randint(w + 2, w + 12)
                        area = w * l
                        shape_desc = f"รูปสี่เหลี่ยมผืนผ้า (กว้าง {w} {unit}, ยาว {l} {unit})"
                        step1_calc = f"{w} × {l} = <b style='color:{c_blue};'>{area:,}</b> ตาราง{unit}"

                    svg = draw_p4_real_life_geo_svg(scenario, shape_type, [w, l], unit)

                    if scenario == "tile":
                        persons = ["ช่างปูน", "ผู้รับเหมา", "คุณพ่อ", "ผู้อำนวยการโรงเรียน", "เจ้าของบ้าน"]
                        places = ["ห้องโถง", "ลานซักล้าง", "ระเบียงบ้าน", "พื้นลานจอดรถ", "ลานวัด", "ลานกิจกรรม"]
                        person = random.choice(persons)
                        place = random.choice(places)
                        cost = random.choice([150, 200, 250, 300, 400])
                        ans = area * cost
                        q = f"{person}ต้องการปูกระเบื้อง{place}{shape_desc} ถ้าค่าปูกระเบื้องตาราง{unit}ละ {cost} บาท จะต้องจ่ายค่าจ้างทั้งหมดกี่บาท?<br>{svg}"
                    elif scenario == "carpet":
                        persons = ["คุณแม่", "ฝ่ายอาคาร", "เจ้าของห้อง", "ผู้จัดการโรงแรม", "ห้องสมุด"]
                        places = ["ห้องนอน", "ห้องประชุม", "ห้องอ่านหนังสือ", "เวทีการแสดง", "ห้องนั่งเล่น"]
                        person = random.choice(persons)
                        place = random.choice(places)
                        cost = random.choice([120, 180, 250, 350])
                        ans = area * cost
                        q = f"{person}สั่งซื้อพรมมาปูพื้น{place}{shape_desc} ถ้าพรมราคาตาราง{unit}ละ {cost} บาท จะต้องจ่ายเงินกี่บาท?<br>{svg}"
                    elif scenario == "paint":
                        persons = ["ลุงช่างทาสี", "เทศบาล", "จิตรกร", "ภารโรง", "กลุ่มนักศึกษา"]
                        places = ["กำแพงบ้าน", "ผนังห้องเรียน", "กำแพงโรงเรียน", "รั้วปูน", "ป้ายร้านค้าขนาดใหญ่"]
                        person = random.choice(persons)
                        place = random.choice(places)
                        cost = random.choice([80, 100, 150, 200])
                        ans = area * cost
                        q = f"{person}รับเหมาทาสี{place}{shape_desc} ถ้าคิดค่าจ้างทาสีตาราง{unit}ละ {cost} บาท {person}จะได้ค่าจ้างทั้งหมดกี่บาท?<br>{svg}"

                    sol = f"""<span style='color:#2c3e50;'>
                    <div style='background-color:#e8f8f5; border-left:4px solid #1abc9c; padding:15px; margin-bottom:15px; border-radius:8px;'>
                    💡 <b>วิเคราะห์โจทย์ (ปกคลุมพื้นผิว = การหาพื้นที่):</b><br>
                    คำว่า "ปูกระเบื้อง, ปูพรม, ทาสี" คือการทำสิ่งที่คลุมผิวหน้าทั้งหมด จึงต้องหา <b>พื้นที่ (กว้าง × ยาว หรือ ด้าน × ด้าน)</b> จากนั้นนำไปคูณกับราคาต่อตารางหน่วยครับ
                    </div>
                    <b>วิธีทำอย่างละเอียด Step-by-Step:</b><br>
                    👉 <b>ขั้นที่ 1: หาพื้นที่ทั้งหมด</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;บริเวณดังกล่าวเป็น {shape_desc}<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;พื้นที่ = {step1_calc}<br>
                    👉 <b>ขั้นที่ 2: คำนวณค่าใช้จ่ายทั้งหมด</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;ค่าใช้จ่ายตาราง{unit}ละ <b style='color:{c_red};'>{cost}</b> บาท<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;นำพื้นที่ทั้งหมด คูณกับ ราคา ➔ {area} × <b style='color:{c_red};'>{cost}</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;คิดเป็นเงิน = <b style='color:#27ae60;'>{ans:,}</b> บาท<br><br>
                    <b>ตอบ: จะต้องจ่ายเงินทั้งหมด {ans:,} บาท</b></span>"""

    elif actual_sub_t == "แปลงเศษเกินเป็นจำนวนคละ":
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
                val = round(random.uniform(10.01, 99.999), random.choice([2, 3]))
                val_str = f"{val:.3f}" if len(str(val).split('.')[1]) == 3 else f"{val:.2f}"
                whole_part, dec_part = val_str.split('.')
                q = f"ให้นักเรียนเขียนคำอ่าน และเขียนในรูปกระจายของทศนิยมต่อไปนี้: <b>{val_str}</b>"
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
                &nbsp;&nbsp;&nbsp;&nbsp;อ่านว่า: (อ่านตัวเลขหน้าจุดเป็นจำนวนเต็ม ส่วนตัวเลขหลังจุดให้อ่านเรียงตัว)<br><br>
                👉 <b>2. เขียนในรูปกระจาย:</b><br>
                &nbsp;&nbsp;&nbsp;&nbsp;{whole_part[0]}0 + {whole_part[1]} + 0.{dec_part[0]} + 0.0{dec_part[1]} {"+ 0.00" + dec_part[2] if len(dec_part)==3 else ""}<br><br>
                💡 <i>หมายเหตุ: การกระจายช่วยให้เราเข้าใจว่าเลขแต่ละตัวมีค่าเท่าไหร่ตามตำแหน่งของมัน</i></span>"""

            elif actual_sub_t in ["การบวกเศษส่วน", "การลบเศษส่วน", "การคูณเศษส่วน", "การหารเศษส่วน"]:
                q = f"จงคำนวณและแสดงวิธีทำ {actual_sub_t} ตามที่กำหนดให้"
                sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b> หาผลลัพธ์ของ {actual_sub_t} พร้อมทำเป็นเศษส่วนอย่างต่ำ</span>"
            
            elif actual_sub_t in ["การบวกทศนิยม", "การลบทศนิยม", "การคูณทศนิยม", "การหารทศนิยม", "การบวกและการลบทศนิยม"]:
                op = "+" if "บวก" in actual_sub_t else "-"
                if "คูณ" in actual_sub_t: op = "×"
                if "หาร" in actual_sub_t: op = "÷"
                
                a = round(random.uniform(1.0, 50.0), random.choice([1, 2]))
                b = round(random.uniform(1.0, 49.0), random.choice([1, 2]))
                
                if op == "+": ans = round(a + b, 2)
                elif op == "-": 
                    if b > a: a, b = b, a
                    ans = round(a - b, 2)
                elif op == "×": ans = round(a * b, 4)
                else: ans = round(a / b, 2)
                
                q = f"จงหาผลลัพธ์ของ <b>{a} {op} {b}</b>"
                if op in ["+", "-"]:
                    sol = f"<span style='color:#2c3e50;'>{generate_decimal_vertical_html(a, b, op, is_key=True)}</span>"
                else:
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b> คำนวณผลลัพธ์ = <b>{ans}</b></span>"
            
            elif actual_sub_t in ["การแก้สมการ (บวก/ลบ)", "การแก้สมการ (คูณ/หาร)", "สมการและตัวไม่ทราบค่าจากชีวิตประจำวัน", "สมการเชิงตรรกะและตาชั่งปริศนา", "โจทย์ปัญหาสมการ: ความสัมพันธ์ของ 2 สิ่ง"]:
                var = random.choice(["x", "y", "a", "m"])
                num1 = random.randint(10, 100)
                num2 = random.randint(100, 500)
                q = f"จงแก้สมการเพื่อหาค่า <b>{var}</b> จากสมการ: <b>{var} + {num1} = {num2}</b>"
                sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b> ย้ายข้างสมการ<br>{var} = {num2} - {num1}<br><b>ตอบ: {var} = {num2 - num1}</b></span>"

            else:
                q = f"⚠️ [ระบบอยู่ระหว่างการอัปเดต] ไม่พบเงื่อนไขการสร้างโจทย์สำหรับหัวข้อ: <b>{actual_sub_t}</b>"
                sol = "กรุณาเลือกหัวข้ออื่น"

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

selected_grade = "ป.4"  # บังคับเลือก ป.4 อย่างเดียว
st.sidebar.markdown("📚 **ระดับชั้น:** ป.4")

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

if st.sidebar.button("🚀 สั่งสร้างใบงาน ป.4", type="primary", use_container_width=True):
    with st.spinner("กำลังออกแบบรูปภาพและสร้างเฉลยแบบ Step-by-Step..."):
        
        qs = generate_questions_logic(selected_grade, selected_main, selected_sub, num_input, is_challenge)
        
        html_w = create_page(selected_grade, selected_sub, qs, is_key=False, q_margin=q_margin, ws_height=ws_height, brand_name=brand_name)
        html_k = create_page(selected_grade, selected_sub, qs, is_key=True, q_margin=q_margin, ws_height=ws_height, brand_name=brand_name)
        
        st.session_state['worksheet_html'] = html_w
        st.session_state['answerkey_html'] = html_k
        
        ebook_body = f'\n<div class="a4-wrapper">{extract_body(html_w)}</div>\n<div class="a4-wrapper">{extract_body(html_k)}</div>\n'
        
        full_ebook_html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap" rel="stylesheet"><style>@page {{ size: A4; margin: 15mm; }} @media screen {{ body {{ font-family: 'Sarabun', sans-serif; background-color: #525659; display: flex; flex-direction: column; align-items: center; padding: 40px 0; margin: 0; }} .a4-wrapper {{ width: 210mm; min-height: 297mm; background: white; margin-bottom: 30px; box-shadow: 0 10px 20px rgba(0,0,0,0.3); padding: 15mm; box-sizing: border-box; }} }} @media print {{ body {{ font-family: 'Sarabun', sans-serif; background: transparent; padding: 0; display: block; margin: 0; }} .a4-wrapper {{ width: 100%; min-height: auto; margin: 0; padding: 0; box-shadow: none; page-break-after: always; }} }} .header {{ text-align: center; border-bottom: 2px solid #333; margin-bottom: 10px; padding-bottom: 10px; }} .q-box {{ margin-bottom: {q_margin}; padding: 10px 15px; page-break-inside: avoid; font-size: 20px; line-height: 1.6; }} .workspace {{ height: {ws_height}; border: 2px dashed #bdc3c7; border-radius: 8px; margin: 15px 0; padding: 10px; color: #95a5a6; font-size: 16px; background-color: #fafbfc; }} .ans-line {{ margin-top: 10px; border-bottom: 1px dotted #999; width: 80%; height: 30px; font-weight: bold; font-size: 20px; display: flex; align-items: flex-end; padding-bottom: 5px; }} .sol-text {{ color: #333; font-size: 18px; display: block; margin-top: 15px; padding: 15px; background-color: #f1f8ff; border-left: 4px solid #3498db; border-radius: 4px; line-height: 1.6; }} .page-footer {{ text-align: right; font-size: 14px; color: #95a5a6; margin-top: 20px; border-top: 1px solid #eee; padding-top: 10px; }} </style></head><body>{ebook_body}</body></html>"""

        filename_base = f"BaanTded_P4_{int(time.time())}"
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
