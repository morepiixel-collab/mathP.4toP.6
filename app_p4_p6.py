import streamlit as st
import streamlit.components.v1 as components
import random
import math
import zipfile
import io
import time
import itertools

# ==========================================
# ⚙️ ตรวจสอบไลบรารี pdfkit (สำหรับปุ่ม Export PDF โดยตรง)
# ==========================================
try:
    import pdfkit
    HAS_PDFKIT = True
except ImportError:
    HAS_PDFKIT = False

# ==========================================
# ตั้งค่าหน้าเพจ Web App & Professional CSS
# ==========================================
st.set_page_config(page_title="Math Generator Pro Standard", page_icon="🚀", layout="wide")

st.markdown("""
<style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1200px; }
    div[data-testid="stSidebar"] div.stButton > button { background-color: #27ae60; color: white; border-radius: 8px; height: 3.5rem; font-size: 18px; font-weight: bold; transition: all 0.3s ease; border: none; box-shadow: 0 4px 6px rgba(39,174,96,0.3); }
    div[data-testid="stSidebar"] div.stButton > button:hover { background-color: #219653; box-shadow: 0 6px 12px rgba(39,174,96,0.4); transform: translateY(-2px); }
    div.stDownloadButton > button { border-radius: 8px; font-weight: bold; border: 1px solid #bdc3c7; transition: all 0.2s ease; }
    div.stDownloadButton > button:hover { border-color: #3498db; color: #3498db; }
    .main-header { background: linear-gradient(135deg, #2980b9, #2c3e50); padding: 2rem; border-radius: 15px; color: white; margin-bottom: 2rem; box-shadow: 0 10px 20px rgba(0,0,0,0.15); transition: all 0.3s ease; }
    .main-header.challenge { background: linear-gradient(135deg, #c0392b, #8e44ad); }
    .main-header h1 { margin: 0; font-size: 2.8rem; font-weight: 800; text-shadow: 2px 2px 4px rgba(0,0,0,0.2); }
    .main-header p { margin: 10px 0 0 0; font-size: 1.2rem; opacity: 0.9; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>🚀 Math Worksheet Pro <span style="font-size: 20px; background: #f39c12; color: #fff; padding: 5px 15px; border-radius: 20px; vertical-align: middle;">Standard Edition</span></h1>
    <p>ระบบสร้างสื่อการสอนคณิตศาสตร์ (ป.1 - ป.6) หลักสูตรปกติ พร้อมระบบ Spacing ที่ยืดหยุ่น และเฉลยละเอียดยิบ</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 1. คลังคำศัพท์และฟังก์ชันตัวช่วย
# ==========================================
NAMES = ["อคิณ", "นาวิน", "ภูผา", "สายฟ้า", "เจ้านาย", "ข้าวหอม", "ใบบัว", "มะลิ", "น้ำใส", "ญาญ่า", "ปลื้ม", "พายุ", "ไออุ่น", "กะทิ", "คุณครู", "นักเรียน"]
LOCS = ["โรงเรียน", "สวนสัตว์", "สวนสนุก", "ห้างสรรพสินค้า", "ห้องสมุด", "สวนสาธารณะ", "พิพิธภัณฑ์", "ลานกิจกรรม", "ค่ายลูกเสือ"]
ITEMS = ["ลูกแก้ว", "สติกเกอร์", "การ์ดพลัง", "โมเดลรถ", "ตุ๊กตาหมี", "สมุดระบายสี", "ดินสอสี", "ลูกโป่ง"]
SNACKS = ["ช็อกโกแลต", "คุกกี้", "โดนัท", "เยลลี่", "ขนมปัง", "ไอศกรีม", "น้ำผลไม้", "นมเย็น"]
ANIMALS = ["แมงมุม", "มดแดง", "กบ", "จิ้งจก", "ตั๊กแตน", "เต่า", "หอยทาก"]
PUBLISHERS = ["สำนักพิมพ์", "โรงพิมพ์", "ฝ่ายวิชาการ", "ร้านถ่ายเอกสาร", "ทีมงานจัดทำเอกสาร", "บริษัทสิ่งพิมพ์"]
DOC_TYPES = ["หนังสือนิทาน", "รายงานการประชุม", "แคตตาล็อกสินค้า", "เอกสารประกอบการเรียน", "สมุดภาพ", "นิตยสารรายเดือน", "พจนานุกรม"]
BUILDERS = ["บริษัทรับเหมา", "ผู้ใหญ่บ้าน", "เทศบาลตำบล", "เจ้าของโครงการ", "ผู้อำนวยการโรงเรียน", "กรมทางหลวง", "อบต."]
BUILD_ACTIONS = ["ปักเสาไฟ", "ปลูกต้นไม้", "ตั้งศาลาริมทาง", "ติดป้ายประกาศ", "ตั้งถังขยะ", "ปักธงประดับ", "ติดตั้งกล้องวงจรปิด"]
BUILD_LOCS = ["ริมถนนทางเข้าหมู่บ้าน", "เลียบคลองส่งน้ำ", "ริมทางเดินรอบสวน", "บนสะพานยาว", "สองข้างทางเข้างาน", "รอบรั้วโรงเรียน"]
CONTAINERS = ["กล่อง", "ถุงผ้า", "ตะกร้า", "ลังกระดาษ", "แพ็คพลาสติก"]
FRUIT_EMOJIS = {"แอปเปิล": "🍎", "ส้ม": "🍊", "สตรอว์เบอร์รี": "🍓", "กล้วย": "🍌", "มะม่วง": "🥭", "แตงโม": "🍉", "ลูกพีช": "🍑"}
FRUITS = list(FRUIT_EMOJIS.keys())
MATERIALS = ["แผ่นไม้", "กระดาษสี", "แผ่นพลาสติก", "ผืนผ้าใบ", "แผ่นเหล็ก", "แผ่นกระเบื้อง"]
VEHICLES = ["รถยนต์", "รถจักรยานยนต์", "รถบรรทุก", "รถไฟ", "รถตู้"]
WORK_ACTIONS = ["ทาสีบ้าน", "ปลูกต้นไม้", "สร้างกำแพง", "ประกอบหุ่นยนต์", "เก็บขยะ", "จัดหนังสือ"]
ROOMS = ["ห้องนอน", "ห้องนั่งเล่น", "ห้องเรียน", "ห้องทำงาน", "ห้องประชุม", "ห้องเก็บของ"]
FURNITURE = ["ตู้เสื้อผ้า", "โต๊ะทำงาน", "เตียงนอน", "ชั้นวางหนังสือ", "โซฟา", "ตู้โชว์", "โต๊ะเรียน", "ตู้เก็บเอกสาร"]

PLACE_EMOJIS = {"บ้าน": "🏠", "โรงเรียน": "🏫", "ตลาด": "🛒", "วัด": "🛕", "สวนสาธารณะ": "🌳", "โรงพยาบาล": "🏥", "ห้องสมุด": "📚", "สถานีตำรวจ": "🚓"}

box_html = "<span style='display: inline-block; width: 22px; height: 22px; border: 2px solid #333; border-radius: 3px; vertical-align: middle; margin-left: 5px; position: relative; top: -2px;'></span>"

def f_html(n, d, c="#2c3e50", b=True):
    w = "bold" if b else "normal"
    return f"<span style='display:inline-flex; flex-direction:column; vertical-align:middle; text-align:center; line-height:1.4; margin:0 4px;'><span style='border-bottom:2px solid {c}; padding:0 4px; font-weight:{w}; color:{c};'>{n}</span><span style='padding:0 4px; font-weight:{w}; color:{c};'>{d}</span></span>"

def get_vertical_fraction(num, den, color="#c0392b", is_bold=True):
    weight = "bold" if is_bold else "normal"
    return f"""<span style="display:inline-flex; flex-direction:column; vertical-align:middle; text-align:center; line-height:1.4; margin: 0 6px; font-family:'Sarabun', sans-serif; white-space: nowrap;"><span style="border-bottom: 2px solid {color}; padding: 2px 6px; font-weight:{weight}; color:{color};">{num}</span><span style="padding: 2px 6px; font-weight:{weight}; color:{color};">{den}</span></span>"""

def generate_vertical_table_html(a, b, op, result="", is_key=False):
    a_str = f"{a:,}" if isinstance(a, int) else str(a)
    b_str = f"{b:,}" if isinstance(b, int) else str(b)
    res_str = f"{result:,}" if isinstance(result, int) and result != "" else str(result)
    
    ans_val = res_str if is_key else ""
    border_ans = "border-bottom: 4px double #000;" if is_key else ""
    
    return f"""
    <div style='margin-left: 60px; display: block; font-family: "Sarabun", sans-serif; font-variant-numeric: tabular-nums; font-size: 26px; margin-top: 15px; margin-bottom: 15px;'>
        <table style='border-collapse: collapse; text-align: right;'>
            <tr>
                <td style='padding: 0 10px 0 0; border: none;'>{a_str}</td>
                <td rowspan='2' style='vertical-align: middle; text-align: left; padding: 0 0 0 15px; font-size: 28px; font-weight: bold; border: none; color: #333;'>{op}</td>
            </tr>
            <tr>
                <td style='padding: 5px 10px 5px 0; border: none; border-bottom: 2px solid #000;'>{b_str}</td>
            </tr>
            <tr>
                <td style='padding: 5px 10px 0 0; border: none; {border_ans} height: 35px;'>{ans_val}</td>
                <td style='border: none;'></td>
            </tr>
        </table>
    </div>
    """

def generate_unit_math_html(u_maj, u_min, v1_maj, v1_min, v2_maj, v2_min, op, multiplier):
    """ตัวช่วยสำหรับวาดตารางตั้งบวกลบของหน่วยการวัดข้ามหน่วย"""
    if op == "+":
        raw_min = v1_min + v2_min
        raw_maj = v1_maj + v2_maj
        carry = raw_min // multiplier
        fin_min = raw_min % multiplier
        fin_maj = raw_maj + carry
        
        html = f"<div style='margin-left: 40px;'><table style='text-align: center; border-collapse: collapse; font-size: 22px; font-family: Sarabun; margin: 10px 0;'>"
        html += f"<tr style='border-bottom: 2px solid #333; font-weight: bold; color: #2c3e50;'><td style='padding: 5px 25px;'>{u_maj}</td><td style='padding: 5px 25px;'>{u_min}</td><td></td></tr>"
        html += f"<tr><td style='padding: 5px;'>{v1_maj:,}</td><td>{v1_min:,}</td><td></td></tr>"
        html += f"<tr><td style='padding: 5px; border-bottom: 2px solid #333;'>{v2_maj:,}</td><td style='border-bottom: 2px solid #333;'>{v2_min:,}</td><td style='font-weight:bold; font-size:26px; padding-left:15px;'>{op}</td></tr>"
        
        if carry > 0:
            html += f"<tr><td style='padding: 5px;'>{raw_maj:,}</td><td>{raw_min:,}</td><td></td></tr>"
            html += f"<tr style='font-weight: bold; color: #c0392b;'><td style='padding: 5px; border-bottom: 4px double #333;'>{fin_maj:,}</td><td style='border-bottom: 4px double #333;'>{fin_min:,}</td><td style='font-size: 16px; text-align: left; padding-left: 10px;'>(ทด <b style='color:red;'>{carry}</b> {u_maj})</td></tr>"
        else:
            html += f"<tr style='font-weight: bold; color: #c0392b;'><td style='padding: 5px; border-bottom: 4px double #333;'>{fin_maj:,}</td><td style='border-bottom: 4px double #333;'>{fin_min:,}</td><td></td></tr>"
        html += "</table></div>"
        ans_str = f"{fin_maj:,} {u_maj} {fin_min:,} {u_min}" if fin_min > 0 else f"{fin_maj:,} {u_maj}"
        return html, ans_str
        
    else: # Subtraction
        is_borrow = v1_min < v2_min
        if is_borrow:
            c_v1_maj = v1_maj - 1
            c_v1_min = v1_min + multiplier
        else:
            c_v1_maj = v1_maj
            c_v1_min = v1_min
            
        fin_maj = c_v1_maj - v2_maj
        fin_min = c_v1_min - v2_min
        
        html = f"<div style='margin-left: 40px;'><table style='text-align: center; border-collapse: collapse; font-size: 22px; font-family: Sarabun; margin: 10px 0;'>"
        html += f"<tr style='border-bottom: 2px solid #333; font-weight: bold; color: #2c3e50;'><td style='padding: 5px 25px;'>{u_maj}</td><td style='padding: 5px 25px;'>{u_min}</td><td></td></tr>"
        
        if is_borrow:
            html += f"<tr style='color: #e74c3c; font-size: 18px; font-weight: bold;'><td>{c_v1_maj:,}</td><td>{c_v1_min:,}</td><td></td></tr>"
            html += f"<tr><td style='padding: 5px; text-decoration: line-through;'>{v1_maj:,}</td><td style='text-decoration: line-through;'>{v1_min:,}</td><td></td></tr>"
        else:
            html += f"<tr><td style='padding: 5px;'>{v1_maj:,}</td><td>{v1_min:,}</td><td></td></tr>"
            
        html += f"<tr><td style='padding: 5px; border-bottom: 2px solid #333;'>{v2_maj:,}</td><td style='border-bottom: 2px solid #333;'>{v2_min:,}</td><td style='font-weight:bold; font-size:26px; padding-left:15px;'>{op}</td></tr>"
        html += f"<tr style='font-weight: bold; color: #c0392b;'><td style='padding: 5px; border-bottom: 4px double #333;'>{fin_maj:,}</td><td style='border-bottom: 4px double #333;'>{fin_min:,}</td><td></td></tr>"
        html += "</table></div>"
        
        ans_str = f"{fin_maj:,} {u_maj} {fin_min:,} {u_min}" if fin_min > 0 else f"{fin_maj:,} {u_maj}"
        if fin_maj <= 0: ans_str = f"{fin_min:,} {u_min}"
        return html, ans_str

def generate_mixed_number_html(whole, num, den):
    return f"<span style='font-size: 24px; vertical-align: middle;'>{whole}</span> {f_html(num, den)}"

def cm_to_m_cm_mm(cm_float):
    total_mm = int(round(cm_float * 10))
    m = total_mm // 1000
    cm = (total_mm % 1000) // 10
    mm = total_mm % 10
    parts = []
    if m > 0: parts.append(f"{m} เมตร")
    if cm > 0: parts.append(f"{cm} เซนติเมตร")
    if mm > 0: parts.append(f"{mm} มิลลิเมตร")
    if not parts: return "0 เซนติเมตร"
    return " ".join(parts)

# ==========================================
# 🌟 ฟังก์ชันวาดรูปภาพ SVG 🌟
# ==========================================
def draw_beakers_svg(v1_l, v1_ml, v2_l, v2_ml):
    def single_beaker(l, ml, name, color):
        tot = l * 1000 + ml
        d_max = math.ceil(tot/1000)*1000 if tot > 0 else 1000
        if d_max < 1000: d_max = 1000
        h = 100
        w = 60
        fill_h = (tot / d_max) * h
        svg = f'<g>'
        svg += f'<rect x="0" y="{20+h-fill_h}" width="{w}" height="{fill_h}" fill="{color}" opacity="0.7"/>'
        svg += f'<path d="M0,20 L0,{20+h} Q0,{20+h+5} 5,{20+h+5} L{w-5},{20+h+5} Q{w},{20+h+5} {w},{20+h} L{w},20" fill="none" stroke="#34495e" stroke-width="3"/>'
        for i in range(1, 4):
            yy = 20 + h - (i * h / 4)
            svg += f'<line x1="0" y1="{yy}" x2="10" y2="{yy}" stroke="#34495e" stroke-width="2"/>'
        lbl = f"{l} ลิตร {ml} มล." if l > 0 else f"{ml} มล."
        if ml == 0 and l > 0: lbl = f"{l} ลิตร"
        svg += f'<text x="{w/2}" y="{h+45}" font-family="Sarabun" font-size="16" font-weight="bold" fill="#333" text-anchor="middle">{name}</text>'
        svg += f'<text x="{w/2}" y="{h+65}" font-family="Sarabun" font-size="14" fill="#e74c3c" font-weight="bold" text-anchor="middle">{lbl}</text>'
        svg += f'</g>'
        return svg

    svg1 = single_beaker(v1_l, v1_ml, "ถัง A", "#3498db")
    svg2 = single_beaker(v2_l, v2_ml, "ถัง B", "#1abc9c")
    
    full_svg = f'<div style="text-align:center; margin: 20px 0;"><svg width="300" height="200">'
    full_svg += f'<g transform="translate(50, 0)">{svg1}</g>'
    full_svg += f'<g transform="translate(190, 0)">{svg2}</g>'
    full_svg += '</svg></div>'
    return full_svg

def draw_distance_route_svg(p_names, p_emojis, dist_texts):
    width = 500
    height = 120
    svg = f'<div style="text-align:center; margin: 15px 0;"><svg width="{width}" height="{height}">'
    
    svg += f'<line x1="50" y1="60" x2="250" y2="60" stroke="#34495e" stroke-width="4" stroke-dasharray="10,5"/>'
    if len(p_names) == 3:
        svg += f'<line x1="250" y1="60" x2="450" y2="60" stroke="#34495e" stroke-width="4" stroke-dasharray="10,5"/>'
    
    svg += f'<text x="150" y="45" font-family="Sarabun" font-size="16" font-weight="bold" fill="#c0392b" text-anchor="middle">{dist_texts[0]}</text>'
    if len(p_names) == 3:
        svg += f'<text x="350" y="45" font-family="Sarabun" font-size="16" font-weight="bold" fill="#c0392b" text-anchor="middle">{dist_texts[1]}</text>'

    xs = [50, 250, 450]
    for i, name in enumerate(p_names):
        emoji = p_emojis[i]
        svg += f'<circle cx="{xs[i]}" cy="60" r="28" fill="#ecf0f1" stroke="#2c3e50" stroke-width="3"/>'
        svg += f'<text x="{xs[i]}" y="68" font-size="28" text-anchor="middle">{emoji}</text>'
        svg += f'<text x="{xs[i]}" y="110" font-family="Sarabun" font-size="16" font-weight="bold" fill="#2c3e50" text-anchor="middle">{name}</text>'

    svg += '</svg></div>'
    return svg

def draw_ruler_svg(start_cm, end_cm):
    scale = 40  
    max_cm = max(10, math.ceil(end_cm) + 1)
    width = max_cm * scale + 60
    height = 140
    svg = f'<div style="text-align:center; margin: 15px 0;"><svg width="{width}" height="{height}">'
    obj_x = 30 + (start_cm * scale)
    obj_w = (end_cm - start_cm) * scale
    tip_len = min(20, obj_w / 3) 
    
    svg += f'<rect x="{obj_x}" y="20" width="{obj_w - tip_len}" height="24" fill="#f1c40f" stroke="#d35400" stroke-width="2" rx="2"/>'
    svg += f'<polygon points="{obj_x + obj_w - tip_len},20 {obj_x + obj_w - tip_len},44 {obj_x + obj_w},32" fill="#34495e"/>'
    svg += f'<line x1="{obj_x}" y1="44" x2="{obj_x}" y2="70" stroke="#e74c3c" stroke-width="2" stroke-dasharray="4,4"/>'
    svg += f'<line x1="{obj_x + obj_w}" y1="32" x2="{obj_x + obj_w}" y2="70" stroke="#e74c3c" stroke-width="2" stroke-dasharray="4,4"/>'
    svg += f'<rect x="20" y="70" width="{max_cm*scale + 20}" height="50" fill="#ecf0f1" stroke="#bdc3c7" stroke-width="2" rx="5"/>'
    
    for i in range(max_cm * 10 + 1):
        x = 30 + i * (scale / 10)
        if i % 10 == 0:  
            svg += f'<line x1="{x}" y1="70" x2="{x}" y2="90" stroke="#2c3e50" stroke-width="3"/>'
            svg += f'<text x="{x}" y="110" font-family="sans-serif" font-size="16" font-weight="bold" fill="#2c3e50" text-anchor="middle">{i//10}</text>'
        elif i % 5 == 0: 
            svg += f'<line x1="{x}" y1="70" x2="{x}" y2="85" stroke="#2c3e50" stroke-width="2"/>'
        else:  
            svg += f'<line x1="{x}" y1="70" x2="{x}" y2="80" stroke="#7f8c8d" stroke-width="1"/>'
    svg += '</svg></div>'
    return svg

def draw_long_ruler_svg(length_cm, color="#f1c40f", name=""):
    scale = 40
    base_cm = int(length_cm) - 2
    if base_cm < 0: base_cm = 0
    max_cm_display = 6 
    width = max_cm_display * scale + 60
    height = 140
    svg = f'<div style="text-align:center; margin: 15px 0;"><svg width="{width}" height="{height}">'
    svg += f'<rect x="20" y="70" width="{max_cm_display*scale + 20}" height="50" fill="#ecf0f1" stroke="#bdc3c7" stroke-width="2" rx="5"/>'
    
    obj_end_x = 30 + (length_cm - base_cm) * scale
    tip_len = min(20, obj_end_x - 10)
    
    svg += f'<rect x="0" y="20" width="{obj_end_x - tip_len}" height="24" fill="{color}" stroke="#333" stroke-width="2"/>'
    svg += f'<polygon points="{obj_end_x - tip_len},20 {obj_end_x - tip_len},44 {obj_end_x},32" fill="#34495e"/>'
    svg += f'<text x="10" y="15" font-family="Sarabun" font-size="14" font-weight="bold" fill="#e74c3c">← {name} (เริ่มจาก 0)</text>'
    svg += f'<line x1="{obj_end_x}" y1="32" x2="{obj_end_x}" y2="70" stroke="#e74c3c" stroke-width="2" stroke-dasharray="4,4"/>'

    for i in range(max_cm_display * 10 + 1):
        x = 30 + i * (scale / 10)
        if i % 10 == 0:
            svg += f'<line x1="{x}" y1="70" x2="{x}" y2="90" stroke="#2c3e50" stroke-width="3"/>'
            lbl = base_cm + i//10
            svg += f'<text x="{x}" y="110" font-family="sans-serif" font-size="16" font-weight="bold" fill="#2c3e50" text-anchor="middle">{lbl}</text>'
        elif i % 5 == 0:
            svg += f'<line x1="{x}" y1="70" x2="{x}" y2="85" stroke="#2c3e50" stroke-width="2"/>'
        else:
            svg += f'<line x1="{x}" y1="70" x2="{x}" y2="80" stroke="#7f8c8d" stroke-width="1"/>'
    svg += '</svg></div>'
    return svg

def draw_fraction_svg(num, den):
    width = 250
    height = 60
    slice_w = width / den
    svg = f'<div style="text-align:center; margin: 10px 0;"><svg width="{width}" height="{height}" style="border: 2px solid #2c3e50;">'
    for i in range(den):
        fill = "#3498db" if i < num else "#ffffff"
        svg += f'<rect x="{i*slice_w}" y="0" width="{slice_w}" height="{height}" fill="{fill}" stroke="#2c3e50" stroke-width="2"/>'
    svg += '</svg></div>'
    return svg

def draw_clock_svg(h_24, m):
    cx, cy, r = 150, 150, 110
    h_12 = h_24 % 12
    m_angle = math.radians(m * 6 - 90)
    h_angle = math.radians(h_12 * 30 + (m * 0.5) - 90)
    
    hx, hy = cx + 60 * math.cos(h_angle), cy + 60 * math.sin(h_angle)
    mx, my = cx + 90 * math.cos(m_angle), cy + 90 * math.sin(m_angle)
    
    h_ext_x, h_ext_y = cx + r * math.cos(h_angle), cy + r * math.sin(h_angle)
    m_ext_x, m_ext_y = cx + r * math.cos(m_angle), cy + r * math.sin(m_angle)

    svg = f'<div style="text-align:center;"><svg width="300" height="300">'
    svg += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="white" stroke="#333" stroke-width="4"/>'
    
    for i in range(60):
        angle = math.radians(i * 6 - 90)
        is_hour = i % 5 == 0
        tick_len = 10 if is_hour else 5
        x1, y1 = cx + (r - tick_len) * math.cos(angle), cy + (r - tick_len) * math.sin(angle)
        x2, y2 = cx + r * math.cos(angle), cy + r * math.sin(angle)
        sw = 3 if is_hour else 1
        svg += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#333" stroke-width="{sw}"/>'
        if is_hour:
            num = i // 5
            if num == 0: num = 12
            nx, ny = cx + (r - 28) * math.cos(angle), cy + (r - 28) * math.sin(angle)
            svg += f'<text x="{nx}" y="{ny}" font-family="sans-serif" font-size="20" font-weight="bold" fill="#333" text-anchor="middle" dominant-baseline="central">{num}</text>'

    svg += f'<line x1="{hx}" y1="{hy}" x2="{h_ext_x}" y2="{h_ext_y}" stroke="#e74c3c" stroke-width="2" stroke-dasharray="5,5"/>'
    svg += f'<line x1="{mx}" y1="{my}" x2="{m_ext_x}" y2="{m_ext_y}" stroke="#3498db" stroke-width="2" stroke-dasharray="5,5"/>'
    
    svg += f'<line x1="{cx}" y1="{cy}" x2="{hx}" y2="{hy}" stroke="#e74c3c" stroke-width="6" stroke-linecap="round"/>'
    svg += f'<line x1="{cx}" y1="{cy}" x2="{mx}" y2="{my}" stroke="#3498db" stroke-width="4" stroke-linecap="round"/>'
    svg += f'<circle cx="{cx}" cy="{cy}" r="6" fill="#333"/>'
    svg += '</svg></div>'
    return svg

def draw_scale_svg(kg, kheed, max_kg=5):
    cx, cy, r = 150, 150, 120
    total_kheed = kg * 10 + kheed
    angle = math.radians(total_kheed * 7.2 - 90)
    
    nx, ny = cx + 100 * math.cos(angle), cy + 100 * math.sin(angle) 
    
    svg = f'<div style="text-align:center;"><svg width="300" height="300">'
    svg += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#fdfefe" stroke="#2c3e50" stroke-width="6"/>'
    svg += f'<circle cx="{cx}" cy="{cy}" r="{r-25}" fill="none" stroke="#bdc3c7" stroke-width="1"/>' 
    svg += f'<text x="{cx}" y="{cy+45}" font-family="sans-serif" font-size="20" font-weight="bold" fill="#7f8c8d" text-anchor="middle">kg</text>'
    
    for i in range(max_kg * 10):
        tick_angle = math.radians(i * 7.2 - 90)
        is_kg = i % 10 == 0
        tick_len = 25 if is_kg else (15 if i % 5 == 0 else 10) 
        x1, y1 = cx + (r - tick_len) * math.cos(tick_angle), cy + (r - tick_len) * math.sin(tick_angle)
        x2, y2 = cx + r * math.cos(tick_angle), cy + r * math.sin(tick_angle)
        sw = 4 if is_kg else (3 if i % 5 == 0 else 2) 
        svg += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#2c3e50" stroke-width="{sw}"/>'
        if is_kg:
            num = i // 10
            nx_t, ny_t = cx + (r - 40) * math.cos(tick_angle), cy + (r - 40) * math.sin(tick_angle)
            svg += f'<text x="{nx_t}" y="{ny_t}" font-family="sans-serif" font-size="26" font-weight="bold" fill="#2c3e50" text-anchor="middle" dominant-baseline="central">{num}</text>'
            
    svg += f'<line x1="{cx}" y1="{cy}" x2="{nx}" y2="{ny}" stroke="#c0392b" stroke-width="4" stroke-linecap="round"/>'
    svg += f'<circle cx="{cx}" cy="{cy}" r="10" fill="#c0392b"/>'
    svg += '</svg></div>'
    return svg

def draw_complex_pictogram_html(item, emoji, pic_val):
    days = random.sample(["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์"], 3)
    counts = [random.randint(2, 6) for _ in range(3)]
    html = f"""
    <div style="border: 2px solid #34495e; border-radius: 10px; width: 80%; margin: 15px auto; background-color: #fff; font-family: 'Sarabun', sans-serif;">
        <div style="text-align: center; background-color: #ecf0f1; padding: 10px; font-weight: bold; border-bottom: 2px solid #34495e; font-size: 20px;">จำนวน{item}ที่ขายได้</div>
        <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 24px;">
    """
    for d, c in zip(days, counts):
        icons = "".join([f"<span style='margin: 0 4px;'>{emoji}</span>"] * c)
        html += f'<tr><td style="padding: 10px; border-bottom: 1px solid #eee; width: 30%; border-right: 2px solid #34495e; text-align: center;"><b>วัน{d}</b></td><td style="padding: 10px; border-bottom: 1px solid #eee; text-align: left; padding-left: 20px;">{icons}</td></tr>'
    html += f"""</table>
        <div style="background-color: #fdf2e9; padding: 10px; text-align: center; font-size: 18px; color: #d35400; font-weight: bold; border-top: 2px solid #34495e;">กำหนดให้ {emoji} 1 รูป แทนจำนวน {pic_val} ผล</div>
    </div>"""
    return html, days, counts

def generate_short_division_html(a, b, mode="ห.ร.ม."):
    factors = []
    ca = a
    cb = b
    steps_html = ""
    while True:
        found = False
        for i in range(2, min(ca, cb) + 1):
            if ca % i == 0 and cb % i == 0:
                steps_html += f"<tr><td style='text-align: right; padding-right: 10px; font-weight: bold; color: #c0392b;'>{i}</td><td style='border-left: 2px solid #000; border-bottom: 2px solid #000; padding: 5px 15px; text-align: center;'>{ca}</td><td style='border-bottom: 2px solid #000; padding: 5px 15px; text-align: center;'>{cb}</td></tr>"
                factors.append(i)
                ca //= i
                cb //= i
                found = True
                break
        if not found: break
    if not factors:
        if mode == "ห.ร.ม.": return f"<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด (Step-by-step):</b><br><b>ขั้นที่ 1:</b> ลองหาตัวเลขที่สามารถหารทั้ง {a} และ {b} ลงตัวพร้อมกัน<br><b>ขั้นที่ 2:</b> พบว่าไม่มีตัวเลขใดเลยที่หารทั้งคู่ลงตัวได้ (นอกจากเลข 1)<br><b>ดังนั้น ห.ร.ม. = 1</b></span>"
        else: return f"<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด (Step-by-step):</b><br><b>ขั้นที่ 1:</b> ลองหาตัวเลขที่สามารถหารทั้ง {a} และ {b} ลงตัวพร้อมกัน<br><b>ขั้นที่ 2:</b> พบว่าไม่มีตัวเลขใดเลยที่หารทั้งคู่ลงตัว<br><b>ขั้นที่ 3:</b> การหา ค.ร.น. ในกรณีนี้ ให้นำตัวเลขทั้งสองตัวมาคูณกันได้เลย<br><b>ดังนั้น ค.ร.น. = {a} × {b} = {a*b}</b></span>"
    steps_html += f"<tr><td></td><td style='padding: 5px 15px; text-align: center;'>{ca}</td><td style='padding: 5px 15px; text-align: center;'>{cb}</td></tr>"
    table = f"<table style='margin: 10px 0; font-size: 20px; border-collapse: collapse; color: #333;'>{steps_html}</table>"
    if mode == "ห.ร.ม.":
        ans = math.prod(factors)
        calc_str = " × ".join(map(str, factors))
        sol = f"<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด (การตั้งหารสั้น):</b><br><b>ขั้นที่ 1:</b> หาตัวเลขที่สามารถหารทั้ง {a} และ {b} ลงตัวพร้อมกัน นำมาใส่เป็นตัวหารด้านหน้า<br><b>ขั้นที่ 2:</b> หารไปเรื่อยๆ จนกว่าจะไม่มีตัวเลขใดหารลงตัวทั้งคู่แล้ว<br>{table}<br><b>ขั้นที่ 3:</b> การหา ห.ร.ม. ให้นำเฉพาะ <b>ตัวเลขด้านหน้าเครื่องหมายหารสั้น</b> มาคูณกัน<br><b>ดังนั้น ห.ร.ม. = {calc_str} = {ans}</b></span>"
    else:
        ans = math.prod(factors) * ca * cb
        calc_str = " × ".join(map(str, factors + [ca, cb]))
        sol = f"<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด (การตั้งหารสั้น):</b><br><b>ขั้นที่ 1:</b> หาตัวเลขที่สามารถหารทั้ง {a} และ {b} ลงตัวพร้อมกัน นำมาใส่เป็นตัวหารด้านหน้า<br><b>ขั้นที่ 2:</b> หารไปเรื่อยๆ จนกว่าจะไม่มีตัวเลขใดหารลงตัวทั้งคู่แล้ว<br>{table}<br><b>ขั้นที่ 3:</b> การหา ค.ร.น. ให้นำ <b>ตัวเลขด้านหน้าทั้งหมด และ เศษที่เหลือด้านล่างสุดทั้งหมด (นำมาเป็นรูปตัว L)</b> มาคูณกัน<br><b>ดังนั้น ค.ร.น. = {calc_str} = {ans}</b></span>"
    return sol

def generate_decimal_vertical_html(a, b, op, is_key=False):
    str_a = f"{a:.2f}"
    str_b = f"{b:.2f}"
    ans = a + b if op == '+' else round(a - b, 2)
    str_ans = f"{ans:.2f}"
    max_len = max(len(str_a), len(str_b), len(str_ans)) + 1 
    str_a = str_a.rjust(max_len, " ")
    str_b = str_b.rjust(max_len, " ")
    str_ans = str_ans.rjust(max_len, " ")
    strike = [False] * max_len
    top_marks = [""] * max_len
    
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
            a_chars = list(str_a)
            b_chars = list(str_b)
            a_digits = [int(c) if c.strip() and c != '.' else 0 for c in a_chars]
            b_digits = [int(c) if c.strip() and c != '.' else 0 for c in b_chars]
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
            if strike[i] and is_key: 
                td_content = f'<div style="position: relative;"><span style="position: absolute; top: -25px; left: 50%; transform: translateX(-50%); font-size: 20px; color: red; font-weight: bold;">{mark}</span><span style="text-decoration: line-through; text-decoration-color: red; text-decoration-thickness: 2px;">{val}</span></div>'
            elif mark and is_key: 
                td_content = f'<div style="position: relative;"><span style="position: absolute; top: -25px; left: 50%; transform: translateX(-50%); font-size: 20px; color: red; font-weight: bold;">{mark}</span><span>{val}</span></div>'
        a_tds += f"<td style='width: 35px; text-align: center; height: 50px; vertical-align: bottom;'>{td_content}</td>"
        
    b_tds = "".join([f"<td style='width: 35px; text-align: center; border-bottom: 2px solid #000; height: 40px; vertical-align: bottom;'>{c.strip() if c.strip() else ('.' if c=='.' else '')}</td>" for c in str_b])
    
    if is_key: 
        ans_tds = "".join([f"<td style='width: 35px; text-align: center; color: red; font-weight: bold; height: 45px; vertical-align: bottom;'>{c.strip() if c.strip() else ('.' if c=='.' else '')}</td>" for c in str_ans])
    else: 
        ans_tds = "".join([f"<td style='width: 35px; height: 45px;'></td>" for _ in str_ans])
        
    return f"""<div style="display: block; margin-left: 60px; margin-top: 15px; margin-bottom: 15px;"><div style="display: inline-block; font-family: 'Sarabun', sans-serif; font-size: 32px; line-height: 1.2;"><table style="border-collapse: collapse;"><tr><td style="width: 20px;"></td>{a_tds}<td style="width: 50px; text-align: left; padding-left: 15px; vertical-align: middle;" rowspan="2">{op}</td></tr><tr><td></td>{b_tds}</tr><tr><td></td>{ans_tds}<td></td></tr><tr><td></td><td colspan="{max_len}" style="border-bottom: 6px double #000; height: 10px;"></td><td></td></tr></table></div></div>"""

def generate_long_division_step_by_step_html(divisor, dividend, equation_html, is_key=False):
    div_str = str(dividend)
    div_len = len(div_str)
    
    if not is_key:
        ans_tds_list = [f'<td style="width: 35px; height: 45px;"></td>' for _ in div_str]
        ans_tds_list.append('<td style="width: 35px;"></td>')
        div_tds_list = []
        for i, c in enumerate(div_str):
            left_border = "border-left: 3px solid #000;" if i == 0 else ""
            div_tds_list.append(f'<td style="width: 35px; text-align: center; border-top: 3px solid #000; {left_border} font-size: 38px; height: 50px; vertical-align: bottom;">{c}</td>')
        div_tds_list.append('<td style="width: 35px;"></td>')
        empty_rows = ""
        for _ in range(div_len + 1): 
            empty_rows += f"<tr><td style='border: none;'></td>"
            for _ in range(div_len + 1):
                empty_rows += f"<td style='width: 35px; height: 45px;'></td>"
            empty_rows += "</tr>"
        return f"{equation_html}<div style=\"display: block; margin-left: 60px; margin-top: 15px; margin-bottom: 15px;\"><div style=\"display: inline-block; font-family: 'Sarabun', sans-serif; line-height: 1.2;\"><table style=\"border-collapse: collapse;\"><tr><td style=\"border: none;\"></td>{''.join(ans_tds_list)}</tr><tr><td style=\"border: none; text-align: right; padding-right: 12px; vertical-align: bottom; font-size: 38px;\">{divisor}</td>{''.join(div_tds_list)}</tr>{empty_rows}</table></div></div>"
    
    steps = []
    current_val_str = ""
    ans_str = ""
    has_started = False
    
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
        cur_chars = list(str(current_val))
        m_chars = list(str(mul_res).zfill(len(str(current_val))))
        c_dig = [int(c) for c in cur_chars]
        m_dig = [int(c) for c in m_chars]
        
        top_m = [""] * len(c_dig)
        strik = [False] * len(c_dig)
        for idx_b in range(len(c_dig) - 1, -1, -1):
            if c_dig[idx_b] < m_dig[idx_b]:
                for j in range(idx_b-1, -1, -1):
                    if c_dig[j] > 0:
                        strik[j] = True
                        c_dig[j] -= 1
                        top_m[j] = str(c_dig[j])
                        for k in range(j+1, idx_b): 
                            strik[k] = True
                            c_dig[k] = 9
                            top_m[k] = "9"
                        strik[idx_b] = True
                        c_dig[idx_b] += 10
                        top_m[idx_b] = str(c_dig[idx_b])
                        break
        steps.append({'mul_res': mul_res, 'rem': rem, 'col_index': i, 'top_m': top_m, 'strik': strik})
        current_val_str = str(rem) if rem != 0 else ""
        
    ans_padded = ans_str.rjust(div_len, " ")
    ans_tds_list = [f'<td style="width: 35px; text-align: center; color: red; font-weight: bold; font-size: 38px;">{c.strip()}</td>' for c in ans_padded]
    ans_tds_list.append('<td style="width: 35px;"></td>') 
    div_tds_list = []
    s0 = steps[0] if len(steps) > 0 else None
    s0_start = s0['col_index'] + 1 - len(s0['top_m']) if s0 else 0
    for i, c in enumerate(div_str):
        left_border = "border-left: 3px solid #000;" if i == 0 else ""
        td_content = c
        if is_key and s0 and s0_start <= i <= s0['col_index']:
            t_idx = i - s0_start
            mark = s0['top_m'][t_idx]
            is_strik = s0['strik'][t_idx]
            if is_strik: 
                td_content = f'<div style="position: relative;"><span style="position: absolute; top: -25px; left: 50%; transform: translateX(-50%); font-size: 20px; color: red; font-weight: bold;">{mark}</span><span style="text-decoration: line-through; text-decoration-color: red; text-decoration-thickness: 2px;">{c}</span></div>'
            elif mark: 
                td_content = f'<div style="position: relative;"><span style="position: absolute; top: -25px; left: 50%; transform: translateX(-50%); font-size: 20px; color: red; font-weight: bold;">{mark}</span><span>{c}</span></div>'
        div_tds_list.append(f'<td style="width: 35px; height: 50px; vertical-align: bottom; text-align: center; border-top: 3px solid #000; {left_border} font-size: 38px;">{td_content}</td>')
    div_tds_list.append('<td style="width: 35px;"></td>') 
    
    html = f"{equation_html}<div style=\"display: block; margin-left: 60px; margin-top: 15px; margin-bottom: 15px;\"><div style=\"display: inline-block; font-family: 'Sarabun', sans-serif; line-height: 1.2;\"><table style=\"border-collapse: collapse;\"><tr><td style=\"border: none;\"></td>{''.join(ans_tds_list)}</tr><tr><td style=\"border: none; text-align: right; padding-right: 12px; vertical-align: bottom; font-size: 38px;\">{divisor}</td>{''.join(div_tds_list)}</tr>"
    
    for idx, step in enumerate(steps):
        mul_res_str = str(step['mul_res'])
        pad_len = step['col_index'] + 1 - len(mul_res_str)
        mul_tds = ""
        for i in range(div_len + 1):
            if i >= pad_len and i <= step['col_index']:
                digit_idx = i - pad_len
                border_b = "border-bottom: 2px solid #000;" if i <= step['col_index'] else ""
                mul_tds += f'<td style="width: 35px; height: 50px; vertical-align: bottom; text-align: center; font-size: 38px; {border_b}">{mul_res_str[digit_idx]}</td>'
            elif i == step['col_index'] + 1: 
                mul_tds += '<td style="width: 35px; text-align: center; font-size: 38px; color: #333; position: relative; top: -24px;">-</td>'
            else: 
                mul_tds += '<td style="width: 35px;"></td>'
        html += f"<tr><td style='border: none;'></td>{mul_tds}</tr>"
        
        is_last_step = (idx == len(steps) - 1)
        next_step = steps[idx+1] if not is_last_step else None
        ns_start = next_step['col_index'] + 1 - len(next_step['top_m']) if next_step else 0
        rem_str = str(step['rem'])
        next_digit = div_str[step['col_index'] + 1] if not is_last_step else ""
        display_str = rem_str if rem_str != "0" or is_last_step else ""
        
        if not is_last_step and display_str == "": pass
        else: display_str += next_digit
        if display_str == "": display_str = next_digit
        
        pad_len_rem = step['col_index'] + 1 - len(display_str) + (1 if not is_last_step else 0)
        rem_tds = ""
        for i in range(div_len + 1):
            if i >= pad_len_rem and i <= step['col_index'] + (1 if not is_last_step else 0):
                digit_idx = i - pad_len_rem
                char_val = display_str[digit_idx]
                td_content = char_val
                if is_key and next_step and ns_start <= i <= next_step['col_index']:
                    t_idx = i - ns_start
                    mark = next_step['top_m'][t_idx]
                    is_strik = next_step['strik'][t_idx]
                    if is_strik: 
                        td_content = f'<div style="position: relative;"><span style="position: absolute; top: -25px; left: 50%; transform: translateX(-50%); font-size: 20px; color: red; font-weight: bold;">{mark}</span><span style="text-decoration: line-through; text-decoration-color: red; text-decoration-thickness: 2px;">{char_val}</span></div>'
                    elif mark: 
                        td_content = f'<div style="position: relative;"><span style="position: absolute; top: -25px; left: 50%; transform: translateX(-50%); font-size: 20px; color: red; font-weight: bold;">{mark}</span><span>{char_val}</span></div>'
                border_b2 = "border-bottom: 6px double #000;" if is_last_step else ""
                rem_tds += f'<td style="width: 35px; height: 50px; vertical-align: bottom; text-align: center; font-size: 38px; {border_b2}">{td_content}</td>'
            else: 
                rem_tds += '<td style="width: 35px;"></td>'
        html += f"<tr><td style='border: none;'></td>{rem_tds}</tr>"
        
    html += "</table></div></div>"
    html += f"<div style='margin-top: 15px; color: #2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>1) นำตัวหาร ({divisor}) ไปหารตัวตั้ง ({dividend}) ทีละหลักจากซ้ายไปขวา<br>2) ท่องสูตรคูณแม่ {divisor} ว่าคูณอะไรแล้วได้ใกล้เคียงหรือเท่ากับตัวตั้งในหลักนั้นที่สุด (แต่ห้ามเกิน)<br>3) ใส่ผลลัพธ์ไว้ด้านบน และนำผลคูณมาลบกันด้านล่าง<br>4) ดึงตัวเลขในหลักถัดไปลงมา แล้วทำซ้ำขั้นตอนเดิมจนหมดทุกหลัก</div>"
    return html

def generate_thai_number_text(num_str):
    thai_nums = ["ศูนย์", "หนึ่ง", "สอง", "สาม", "สี่", "ห้า", "หก", "เจ็ด", "แปด", "เก้า"]
    positions = ["", "สิบ", "ร้อย", "พัน", "หมื่น", "แสน", "ล้าน"]
    parts = str(num_str).replace(",", "").split(".")
    int_part = parts[0]
    dec_part = parts[1] if len(parts) > 1 else ""
    
    def read_int(s):
        if s == "0" or s == "": return "ศูนย์"
        
        # 💡 ส่วนที่เพิ่มเข้ามาแก้บั๊ก: จัดการเลขที่เกินหลักล้าน (8 ตำแหน่งขึ้นไป)
        if len(s) > 6:
            mil_part = s[:-6] # ตัดเอาเฉพาะส่วนที่เกินหลักล้านมาอ่านก่อน
            rest_part = s[-6:] # ส่วนที่เหลือ 6 หลักหลัง
            res = read_int(mil_part) + "ล้าน"
            if int(rest_part) > 0:
                res += read_int(rest_part)
            return res
            
        res = ""
        length = len(s)
        for i, digit in enumerate(s):
            d = int(digit)
            if d == 0: continue
            pos = length - i - 1
            if pos == 1 and d == 2: res += "ยี่สิบ"
            elif pos == 1 and d == 1: res += "สิบ"
            elif pos == 0 and d == 1 and length > 1: res += "เอ็ด"
            else: res += thai_nums[d] + positions[pos]
        return res
        
    int_text = read_int(int_part)
    dec_text = ("จุด" + "".join([thai_nums[int(d)] for d in dec_part])) if dec_part else ""
    return int_text + dec_text

def get_prefix(grade):
    if grade in ["ป.1", "ป.2", "ป.3"]: 
        return "<b style='color: #2c3e50; margin-right: 5px;'>ประโยคสัญลักษณ์:</b>"
    return ""

# ==========================================
# 2. ฐานข้อมูลหลักสูตร (Master Database)
# ==========================================
curriculum_db = {
    "ป.1": {
        "จำนวนนับ 1 ถึง 100 และ 0": ["การนับทีละ 1", "การนับทีละ 10", "การอ่านและการเขียนตัวเลข", "การแสดงจำนวนในรูปความสัมพันธ์แบบส่วนย่อย-ส่วนรวม", "แบบรูปซ้ำของรูปเรขาคณิต", "การบอกอันดับที่ (รถแข่ง)", "หลัก ค่าของเลขโดดในแต่ละหลัก และรูปกระจาย", "การเปรียบเทียบจำนวน (> <)",  "การเปรียบเทียบจำนวน (= ≠)", "การเรียงลำดับจำนวน (น้อยไปมาก)", "การเรียงลำดับจำนวน (มากไปน้อย)"],
        "การบวก การลบ": ["การบวก (แบบตั้งหลัก)", "การลบ (แบบตั้งหลัก)"],
        "แผนภูมิรูปภาพ": ["การอ่านแผนภูมิรูปภาพ"]
    },
    "ป.2": {
        "จำนวนนับไม่เกิน 1,000 และ 0": ["การนับทีละ 2 ทีละ 5 ทีละ 10 และทีละ 100", "การอ่านและการเขียนตัวเลข", "จำนวนคู่ จำนวนคี่", "หลัก ค่าของเลขโดด และรูปกระจาย", "การเปรียบเทียบจำนวน (> <)", "การเรียงลำดับจำนวน (น้อยไปมาก)", "การเรียงลำดับจำนวน (มากไปน้อย)"],
        "เวลาและการวัด": ["การบอกเวลาเป็นนาฬิกาและนาที", "การอ่านน้ำหนักจากเครื่องชั่งสปริง", "การอ่านความยาวจากไม้บรรทัด"],
        "การบวก ลบ คูณ หาร": ["การบวก (แบบตั้งหลัก)", "การลบ (แบบตั้งหลัก)", "การคูณ (แบบตั้งหลัก)", "การหารพื้นฐาน"],
        "แผนภูมิรูปภาพ": ["การอ่านแผนภูมิรูปภาพ"]
    },
    "ป.3": {
        "จำนวนนับและเศษส่วน": ["การอ่าน การเขียนตัวเลข", "หลัก ค่าของเลขโดด และรูปกระจาย", "การเปรียบเทียบจำนวน (> <)", "การเรียงลำดับจำนวน (น้อยไปมาก)", "การเรียงลำดับจำนวน (มากไปน้อย)", "การอ่านและเขียนเศษส่วน", "การบวกลบเศษส่วน (ตัวส่วนเท่ากัน)"],
        "เวลา เงิน และการวัด": [
            "การบอกเวลาเป็นนาฬิกาและนาที", 
            "การบอกจำนวนเงินทั้งหมด", 
            "การอ่านน้ำหนักจากเครื่องชั่งสปริง", 
            "การอ่านความยาวจากไม้บรรทัด", 
            "ระยะทาง (กิโลเมตรและเมตร)", 
            "โจทย์ปัญหาความยาว (คูณและหาร)", 
            "การเปรียบเทียบหน่วยการวัด และการแปลงหน่วย (มิลลิเมตร เซนติเมตร เมตร)",
            "การเปรียบเทียบหน่วยระยะทาง และการแปลงหน่วย (เมตร กิโลเมตร)",
            "การเปรียบเทียบหน่วยน้ำหนัก และการแปลงหน่วย (กรัม กิโลกรัม ตัน)",
            "ปริมาตรและความจุ (มิลลิลิตร ลิตร)"
        ],
        "การบวก ลบ คูณ หาร": ["การบวก (แบบตั้งหลัก)", "การลบ (แบบตั้งหลัก)", "การคูณ (แบบตั้งหลัก)", "การหารยาว"],
        "แผนภูมิรูปภาพ": ["การอ่านแผนภูมิรูปภาพ"]
    },
    "ป.4": {
        "จำนวนนับที่มากกว่า 100,000": ["การอ่านและการเขียนตัวเลข", "หลัก ค่าประจำหลัก และรูปกระจาย", "การเปรียบเทียบและเรียงลำดับ", "ค่าประมาณเป็นจำนวนเต็มสิบ เต็มร้อย เต็มพัน"],
        "การบวก ลบ คูณ หาร": ["การบวก (แบบตั้งหลัก)", "การลบ (แบบตั้งหลัก)", "การคูณ (แบบตั้งหลัก)", "การหารยาว"],
        "เศษส่วนและทศนิยม": ["แปลงเศษเกินเป็นจำนวนคละ", "การอ่านและการเขียนทศนิยม"],
        "เรขาคณิตและการวัด": ["การบอกชนิดของมุม", "การวัดขนาดของมุม (ไม้โปรแทรกเตอร์)", "การหาความยาวรอบรูปสี่เหลี่ยมมุมฉาก", "การหาพื้นที่รูปสี่เหลี่ยมมุมฉาก"],
        "สมการ": ["การแก้สมการ (บวก/ลบ)"]
    },
    "ป.5": {
        "เศษส่วน": ["การบวกเศษส่วน", "การลบเศษส่วน", "การคูณเศษส่วน", "การหารเศษส่วน"],
        "ทศนิยม": ["การบวกและการลบทศนิยม", "การคูณและการหารทศนิยม"],
        "บทประยุกต์ (บัญญัติไตรยางศ์)": ["โจทย์ปัญหาบัญญัติไตรยางศ์"],
        "สถิติและความน่าจะเป็น": ["การหาค่าเฉลี่ย (Average)", "ความน่าจะเป็นเบื้องต้น (สุ่มหยิบของ)"],
        "เรขาคณิต 2 มิติ": ["โจทย์ปัญหาพื้นที่และความยาวรอบรูป", "การหาขนาดของมุมที่หายไป", "เส้นขนานและมุมแย้ง"],
        "เรขาคณิต 3 มิติ": ["ปริมาตรและความจุทรงสี่เหลี่ยมมุมฉาก"],
        "ร้อยละและเปอร์เซ็นต์": ["การเขียนเศษส่วนในรูปร้อยละ"],
        "สมการ": ["การแก้สมการ (คูณ/หาร)"],
        "เตรียมสอบเข้า ม.1 (Gifted)": ["โจทย์ปัญหา ห.ร.ม. และ ค.ร.น.", "โจทย์ปัญหา ร้อยละ (กำไร-ขาดทุน)", "โจทย์ปัญหาคลาสสิก (สมการประยุกต์)", "แบบรูปและอนุกรม (Number Patterns)", "มาตราส่วนและทิศทาง", "เรขาคณิตประยุกต์ (หาพื้นที่แรเงา)"]
    },
    "ป.6": {
        "ตัวประกอบของจำนวนนับ": ["การหา ห.ร.ม.", "การหา ค.ร.น."],
        "อัตราส่วนและร้อยละ": ["การหาอัตราส่วนที่เท่ากัน", "โจทย์ปัญหาอัตราส่วน", "โจทย์ปัญหาร้อยละ"],
        "สมการ": ["การแก้สมการ (สองขั้นตอน)"]
    }
}

# ==========================================
# 3. Logic & Dynamic Difficulty Scaling
# ==========================================
def generate_questions_logic(grade, main_t, sub_t, num_q, is_challenge=False):
    questions = []
    seen = set()
    limit_map = {"ป.1": 100, "ป.2": 1000, "ป.3": 100000, "ป.4": 1000000, "ป.5": 9000000, "ป.6": 9000000}
    
    base_limit = limit_map.get(grade, 100)
    limit = base_limit * (10 if is_challenge else 1)

    for _ in range(num_q):
        q = ""
        sol = ""
        attempts = 0
        
        while attempts < 300:
            actual_sub_t = sub_t
            if sub_t == "แบบทดสอบรวมปลายภาค":
                all_mains = [m for m in curriculum_db[grade].keys()]
                rand_main = random.choice(all_mains)
                actual_sub_t = random.choice(curriculum_db[grade][rand_main])

            prefix = get_prefix(grade)

            if actual_sub_t == "ปริมาตรและความจุ (มิลลิลิตร ลิตร)":
                
                # ----------------------------------------------------
                # ฟังก์ชันวาดเส้นจำนวน (Number Line) สำหรับปริมาตร
                # ----------------------------------------------------
                def draw_vol_number_line(val_ml, max_l=3):
                    max_ml = max_l * 1000
                    width = 550
                    height = 120
                    svg = f'<div style="text-align:center; margin:15px 0;"><svg width="{width}" height="{height}">'
                    svg += f'<line x1="40" y1="60" x2="510" y2="60" stroke="#34495e" stroke-width="4"/>'
                    
                    total_ticks = max_l * 10
                    tick_spacing = 460 / total_ticks
                    
                    for i in range(total_ticks + 1):
                        x = 40 + i * tick_spacing
                        is_major = (i % 10 == 0)
                        is_mid = (i % 5 == 0) and not is_major
                        
                        if is_major:
                            tick_len, sw = 15, 3
                        elif is_mid:
                            tick_len, sw = 10, 2
                        else:
                            tick_len, sw = 6, 1
                            
                        svg += f'<line x1="{x}" y1="{60-tick_len}" x2="{x}" y2="{60+tick_len}" stroke="#34495e" stroke-width="{sw}"/>'
                        
                        if is_major:
                            lbl_l = i // 10
                            svg += f'<text x="{x}" y="95" font-family="sans-serif" font-size="16" font-weight="bold" fill="#333" text-anchor="middle">{lbl_l}L</text>'
                    
                    val_x = 40 + (val_ml / max_ml) * 460
                    svg += f'<circle cx="{val_x}" cy="60" r="6" fill="#e74c3c"/>'
                    svg += f'<polygon points="{val_x-8},40 {val_x+8},40 {val_x},54" fill="#e74c3c"/>'
                    svg += '</svg></div>'
                    return svg

                # ----------------------------------------------------
                # ฟังก์ชันวาดบาร์โมเดล (Bar Model)
                # ----------------------------------------------------
                def draw_bar_model_svg(v1_str, v2_str="", mode="add", parts=1):
                    svg = f'<div style="text-align:center; margin:15px 0;"><svg width="550" height="160">'
                    if mode == "add":
                        svg += f'<rect x="50" y="50" width="200" height="40" fill="#3498db" stroke="#2c3e50" stroke-width="2" rx="4"/>'
                        svg += f'<text x="150" y="75" font-family="Sarabun" font-size="14" fill="#fff" font-weight="bold" text-anchor="middle" dominant-baseline="middle">{v1_str}</text>'
                        svg += f'<rect x="250" y="50" width="170" height="40" fill="#2ecc71" stroke="#2c3e50" stroke-width="2" rx="4"/>'
                        svg += f'<text x="335" y="75" font-family="Sarabun" font-size="14" fill="#fff" font-weight="bold" text-anchor="middle" dominant-baseline="middle">{v2_str}</text>'
                        svg += f'<path d="M50,40 Q50,20 235,20 T420,40" fill="none" stroke="#e74c3c" stroke-width="2"/>'
                        svg += f'<text x="235" y="15" font-family="Sarabun" font-size="16" fill="#e74c3c" font-weight="bold" text-anchor="middle">? รวมเป็นเท่าไร ?</text>'
                    elif mode == "diff":
                        svg += f'<rect x="50" y="20" width="370" height="40" fill="#3498db" stroke="#2c3e50" stroke-width="2" rx="4"/>'
                        svg += f'<text x="235" y="45" font-family="Sarabun" font-size="14" fill="#fff" font-weight="bold" text-anchor="middle" dominant-baseline="middle">{v1_str}</text>'
                        svg += f'<rect x="50" y="70" width="220" height="40" fill="#e67e22" stroke="#2c3e50" stroke-width="2" rx="4"/>'
                        svg += f'<text x="160" y="95" font-family="Sarabun" font-size="14" fill="#fff" font-weight="bold" text-anchor="middle" dominant-baseline="middle">{v2_str}</text>'
                        svg += f'<path d="M270,90 L420,90" stroke="#e74c3c" stroke-width="2" stroke-dasharray="5,5"/>'
                        svg += f'<line x1="270" y1="80" x2="270" y2="100" stroke="#e74c3c" stroke-width="2"/>'
                        svg += f'<line x1="420" y1="80" x2="420" y2="100" stroke="#e74c3c" stroke-width="2"/>'
                        svg += f'<text x="345" y="115" font-family="Sarabun" font-size="14" fill="#e74c3c" font-weight="bold" text-anchor="middle">? ต่างกันเท่าไร ?</text>'
                    elif mode == "2step_total":
                        svg += f'<rect x="50" y="20" width="300" height="40" fill="#3498db" stroke="#2c3e50" stroke-width="2" rx="4"/>'
                        svg += f'<text x="200" y="45" font-family="Sarabun" font-size="14" fill="#fff" font-weight="bold" text-anchor="middle" dominant-baseline="middle">{v1_str}</text>'
                        svg += f'<rect x="50" y="70" width="180" height="40" fill="#e67e22" stroke="#2c3e50" stroke-width="2" rx="4"/>'
                        svg += f'<text x="140" y="95" font-family="Sarabun" font-size="16" fill="#fff" font-weight="bold" text-anchor="middle" dominant-baseline="middle">?</text>'
                        svg += f'<path d="M230,90 L350,90" stroke="#e74c3c" stroke-width="2" stroke-dasharray="5,5"/>'
                        svg += f'<line x1="230" y1="80" x2="230" y2="100" stroke="#e74c3c" stroke-width="2"/>'
                        svg += f'<line x1="350" y1="80" x2="350" y2="100" stroke="#e74c3c" stroke-width="2"/>'
                        svg += f'<text x="290" y="115" font-family="Sarabun" font-size="14" fill="#e74c3c" font-weight="bold" text-anchor="middle">น้อยกว่า {v2_str}</text>'
                        svg += f'<path d="M370,20 Q390,65 370,110" fill="none" stroke="#27ae60" stroke-width="3"/>'
                        svg += f'<text x="430" y="70" font-family="Sarabun" font-size="16" fill="#27ae60" font-weight="bold" text-anchor="middle">รวมทั้งหมด = ?</text>'
                    elif mode == "multiply":
                        total_w = 380
                        part_w = total_w / parts
                        for i in range(parts):
                            svg += f'<rect x="{50 + i*part_w}" y="50" width="{part_w}" height="40" fill="#9b59b6" stroke="#2c3e50" stroke-width="2"/>'
                            if i == 0: 
                                svg += f'<text x="{50 + part_w/2}" y="70" font-family="Sarabun" font-size="11" fill="#fff" font-weight="bold" text-anchor="middle" dominant-baseline="middle">{v1_str}</text>'
                        svg += f'<path d="M50,40 Q240,10 430,40" fill="none" stroke="#e74c3c" stroke-width="2"/>'
                        svg += f'<text x="240" y="25" font-family="Sarabun" font-size="16" fill="#e74c3c" font-weight="bold" text-anchor="middle">รวมทั้งหมด = ?</text>'
                        svg += f'<text x="240" y="110" font-family="Sarabun" font-size="14" fill="#333" font-weight="bold" text-anchor="middle">(แบ่งเป็น {parts} ส่วนเท่าๆ กัน)</text>'
                    svg += '</svg></div>'
                    return svg

                q_cat = random.choice(["compare", "add_sub", "divide", "recipe_convert", "number_line", "bar_model"])
                multiplier = 1000
                u_major, u_minor = "ลิตร", "มิลลิลิตร"
                
                if q_cat == "recipe_convert": 
                    recipe_item = random.choice(["น้ำเชื่อม", "น้ำปลา", "ซีอิ๊ว", "กะทิ", "น้ำมะนาว", "นมข้นหวาน"])
                    note_html = "<br><span style='font-size:16px; color:#7f8c8d;'><i>(หมายเหตุ: 1 ช้อนชา = 5 มล., 1 ช้อนโต๊ะ = 15 มล., 1 ถ้วยตวง = 250 มล.)</i></span>"
                    
                    if is_challenge:
                        cup = random.randint(1, 4)
                        tbsp = random.randint(2, 6)
                        tsp = random.randint(2, 5)
                        batches = random.randint(3, 8)
                        
                        total_1_batch = (cup * 250) + (tbsp * 15) + (tsp * 5)
                        total_all = total_1_batch * batches
                        
                        ans_l = total_all // 1000
                        ans_ml = total_all % 1000
                        ans_str = f"{ans_l} ลิตร {ans_ml} มิลลิลิตร" if ans_ml > 0 else f"{ans_l} ลิตร"
                        
                        q = f"สูตรทำ{recipe_item} 1 ชุด ต้องใช้ส่วนผสม <b>{cup} ถ้วยตวง, {tbsp} ช้อนโต๊ะ และ {tsp} ช้อนชา</b><br>ถ้าต้องการทำทั้งหมด <b>{batches} ชุด</b> จะต้องใช้ปริมาตรรวมกี่ลิตร กี่มิลลิลิตร?{note_html}"
                        sol = f"""<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด (🔥 ชาเลนจ์ - การแปลงหน่วยและคูณทวีคูณ):</b><br>
                        <b>ขั้นที่ 1: หาปริมาตรของส่วนผสม 1 ชุด (แปลงเป็นมิลลิลิตร)</b><br>
                        👉 {cup} ถ้วยตวง = {cup} × 250 = <b>{cup * 250} มล.</b><br>
                        👉 {tbsp} ช้อนโต๊ะ = {tbsp} × 15 = <b>{tbsp * 15} มล.</b><br>
                        👉 {tsp} ช้อนชา = {tsp} × 5 = <b>{tsp * 5} มล.</b><br>
                        👉 ปริมาตร 1 ชุด = {cup * 250} + {tbsp * 15} + {tsp * 5} = <b>{total_1_batch:,} มล.</b><br>
                        <b>ขั้นที่ 2: คูณด้วยจำนวนชุดที่ต้องการทำ</b><br>
                        👉 ทำ {batches} ชุด ➔ {total_1_batch:,} × {batches} = <b>{total_all:,} มล.</b><br>
                        <b>ขั้นที่ 3: แปลงกลับเป็นหน่วยผสม</b><br>
                        👉 {total_all:,} มล. คิดเป็น <b>{ans_str}</b><br>
                        <b>ตอบ: {ans_str}</b></span>"""
                    else:
                        unit_name, unit_val = random.choice([("ช้อนชา", 5), ("ช้อนโต๊ะ", 15), ("ถ้วยตวง", 250)])
                        qty = random.randint(2, 15)
                        ans = qty * unit_val
                        
                        q = f"สูตรทำน้ำจิ้มต้องใช้{recipe_item} <b>{qty} {unit_name}</b><br>คิดเป็นปริมาตรกี่มิลลิลิตร?{note_html}"
                        sol = f"""<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>
                        <b>ขั้นที่ 1: ดูอัตราการแปลงหน่วย</b><br>
                        👉 1 {unit_name} เท่ากับ {unit_val} มิลลิลิตร<br>
                        <b>ขั้นที่ 2: ตั้งคูณเพื่อหาปริมาตรรวม</b><br>
                        👉 {qty} {unit_name} = {qty} × {unit_val} = <b>{ans:,} มิลลิลิตร</b><br>
                        <b>ตอบ: {ans:,} มิลลิลิตร</b></span>"""
                        
                elif q_cat == "number_line": 
                    if is_challenge:
                        max_l = random.randint(3, 6)
                        val_ml = random.randint(5, (max_l * 1000 // 50) - 5) * 50
                        ans_l = val_ml // 1000
                        ans_ml = val_ml % 1000
                        ans_str = f"{ans_l} ลิตร {ans_ml} มิลลิลิตร" if ans_l > 0 else f"{ans_ml} มิลลิลิตร"
                        if ans_ml == 0: ans_str = f"{ans_l} ลิตร"
                        
                        svg = draw_vol_number_line(val_ml, max_l)
                        q = f"จากเส้นจำนวนด้านล่าง ลูกศรชี้ที่ปริมาตรความจุเท่าใด? (ตอบเป็นลิตรและมิลลิลิตร)<br>{svg}"
                        sol = f"""<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด (🔥 ชาเลนจ์ - เส้นจำนวนข้ามหน่วย):</b><br>
                        <b>ขั้นที่ 1: วิเคราะห์ความกว้างของช่องสเกล</b><br>
                        👉 สังเกตจาก 0L ไปถึง 1L (1,000 มล.) มีช่องเล็กทั้งหมด 10 ช่อง<br>
                        👉 แสดงว่า 1 ช่องเล็ก มีค่าเท่ากับ 1,000 ÷ 10 = <b>100 มิลลิลิตร</b> (และขีดกลางคือ 500 มล.)<br>
                        <b>ขั้นที่ 2: อ่านค่าจากลูกศรและแปลงหน่วย</b><br>
                        👉 ลูกศรชี้อยู่ที่ตำแหน่ง <b>{val_ml:,} มล.</b><br>
                        👉 แปลงหน่วยเป็นลิตร: {val_ml:,} ÷ 1,000 จะได้ <b>{ans_str}</b><br>
                        <b>ตอบ: {ans_str}</b></span>"""
                    else:
                        max_l = random.randint(1, 2)
                        val_ml = random.randint(1, (max_l * 10) - 1) * 100
                        svg = draw_vol_number_line(val_ml, max_l)
                        
                        ans_l = val_ml // 1000
                        ans_ml = val_ml % 1000
                        ans_str = f"{ans_l} ลิตร {ans_ml} มิลลิลิตร" if ans_l > 0 else f"{ans_ml} มิลลิลิตร"
                        if ans_ml == 0: ans_str = f"{ans_l} ลิตร"
                        
                        q = f"จากเส้นจำนวนด้านล่าง ลูกศรชี้ที่ปริมาตรความจุเท่าใด?<br>{svg}"
                        sol = f"""<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>
                        <b>ขั้นที่ 1: วิเคราะห์เส้นจำนวน</b><br>
                        👉 จาก 0L ถึง 1L ถูกแบ่งเป็น 10 ช่องย่อย<br>
                        👉 แสดงว่า 1 ช่องย่อย มีค่าเท่ากับ <b>100 มิลลิลิตร</b><br>
                        <b>ขั้นที่ 2: อ่านค่าจากลูกศร</b><br>
                        👉 นับช่องมาถึงลูกศร จะได้ <b>{val_ml:,} มิลลิลิตร</b><br>
                        👉 คิดเป็น <b>{ans_str}</b><br>
                        <b>ตอบ: {ans_str}</b></span>"""

                elif q_cat == "bar_model": 
                    if is_challenge:
                        mode = random.choice(["2step_total", "multiply"])
                        if mode == "2step_total":
                            v1_l, v1_ml = random.randint(12, 35), random.randint(100, 900)
                            diff_l, diff_ml = random.randint(2, 6), random.randint(100, 900)
                            
                            tot1_ml = v1_l * 1000 + v1_ml
                            tot_diff_ml = diff_l * 1000 + diff_ml
                            
                            if tot1_ml <= tot_diff_ml: tot1_ml += tot_diff_ml + 2000
                            
                            tot2_ml = tot1_ml - tot_diff_ml
                            sum_ml = tot1_ml + tot2_ml
                            
                            ans_l = sum_ml // 1000
                            ans_ml = sum_ml % 1000
                            ans_str = f"{ans_l} ลิตร {ans_ml} มล."
                            
                            str1 = f"{tot1_ml//1000} ลิตร {tot1_ml%1000} มล."
                            str_diff = f"{diff_l} ลิตร {diff_ml} มล."
                            
                            svg = draw_bar_model_svg(str1, str_diff, "2step_total")
                            q = f"จากบาร์โมเดล (Bar Model) ที่กำหนดให้ ถังใบที่สองมีน้ำน้อยกว่าถังใบแรก<br>จงหา <b>ปริมาตรรวมทั้งหมด</b> ของทั้งสองถัง?<br>{svg}"
                            
                            sol = f"""<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด (🔥 ชาเลนจ์ - บาร์โมเดล 2 ขั้นตอน):</b><br>
                            <b>ขั้นที่ 1: หาปริมาตรของถังใบที่สอง (สีส้ม)</b><br>
                            👉 ถังใบแรกมี = {tot1_ml:,} มล.<br>
                            👉 ถังใบที่สองน้อยกว่าอยู่ = {tot_diff_ml:,} มล.<br>
                            👉 ถังใบที่สอง = {tot1_ml:,} - {tot_diff_ml:,} = <b>{tot2_ml:,} มล.</b><br>
                            <b>ขั้นที่ 2: หาปริมาตรรวมทั้งหมด</b><br>
                            👉 รวม = ถังแรก + ถังที่สอง = {tot1_ml:,} + {tot2_ml:,} = <b>{sum_ml:,} มล.</b><br>
                            👉 แปลงกลับเป็นลิตร: <b>{ans_str}</b><br>
                            <b>ตอบ: {ans_str}</b></span>"""
                        else: # multiply
                            parts = random.randint(3, 6)
                            v1_l, v1_ml = random.randint(1, 4), random.randint(100, 900)
                            tot1_ml = v1_l * 1000 + v1_ml
                            sum_ml = tot1_ml * parts
                            ans_l = sum_ml // 1000
                            ans_ml = sum_ml % 1000
                            ans_str = f"{ans_l} ลิตร {ans_ml} มล."
                            str1 = f"{v1_l} ลิตร {v1_ml} มล."
                            
                            svg = draw_bar_model_svg(str1, "", "multiply", parts)
                            q = f"จากบาร์โมเดล (Bar Model) แสดงปริมาณน้ำที่แบ่งเท่าๆ กัน {parts} ส่วน<br>จงหา <b>ปริมาตรรวมทั้งหมด</b>?<br>{svg}"
                            sol = f"""<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด (🔥 ชาเลนจ์ - บาร์โมเดลการคูณ):</b><br>
                            <b>ขั้นที่ 1: แปลงปริมาตร 1 ส่วนให้เป็นมิลลิลิตร</b><br>
                            👉 1 ส่วน = {v1_l} ลิตร {v1_ml} มล. = <b>{tot1_ml:,} มล.</b><br>
                            <b>ขั้นที่ 2: คูณด้วยจำนวนส่วนทั้งหมด</b><br>
                            👉 มีทั้งหมด {parts} ส่วน นำมาคูณ: {tot1_ml:,} × {parts} = <b>{sum_ml:,} มล.</b><br>
                            <b>ขั้นที่ 3: แปลงกลับเป็นลิตร</b><br>
                            👉 <b>{ans_str}</b><br>
                            <b>ตอบ: {ans_str}</b></span>"""
                    else:
                        mode = random.choice(["add", "diff"])
                        v1_l, v1_ml = random.randint(3, 8), random.randint(100, 900)
                        
                        if mode == "add":
                            v2_l = random.randint(1, 5)
                            v2_ml = random.randint(100, 900)
                            str1 = f"{v1_l} ลิตร {v1_ml} มล."
                            str2 = f"{v2_l} ลิตร {v2_ml} มล."
                            svg = draw_bar_model_svg(str1, str2, "add")
                            q = f"จากบาร์โมเดล (Bar Model) ที่กำหนดให้ <b>ปริมาตรรวมทั้งหมด</b> คือเท่าไร?<br>{svg}"
                            op = "+"
                        else:
                            v2_l = random.randint(1, v1_l-1)
                            v2_ml = random.randint(100, 900)
                            if v1_ml < v2_ml:
                                v1_ml, v2_ml = v2_ml, v1_ml + 100
                                
                            str1 = f"{v1_l} ลิตร {v1_ml} มล."
                            str2 = f"{v2_l} ลิตร {v2_ml} มล."
                            svg = draw_bar_model_svg(str1, str2, "diff")
                            q = f"จากบาร์โมเดล (Bar Model) ที่กำหนดให้ ปริมาตรทั้งสองส่วน<b>ต่างกันอยู่เท่าไร</b>?<br>{svg}"
                            op = "-"

                        table_html, ans_str = generate_unit_math_html(u_major, u_minor, v1_l, v1_ml, v2_l, v2_ml, op, multiplier)
                        sol = f"""<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด (การแก้โจทย์บาร์โมเดล):</b><br>
                        👉 จากรูปภาพ เราต้องนำปริมาตรทั้งสองมาทำเครื่องหมาย <b>{'+' if op=='+' else '-'}</b> กัน<br>
                        {table_html}
                        <b>ตอบ: {ans_str}</b></span>"""

                elif q_cat == "compare":
                    val_major = random.randint(5, 50) if is_challenge else random.randint(1, 15)
                    val_minor = random.randint(50, 950)
                    total_minor_1 = (val_major * multiplier) + val_minor
                    
                    case = random.choice(["greater", "less", "equal"])
                    if case == "equal":
                        total_minor_2 = total_minor_1
                    elif case == "greater":
                        total_minor_2 = total_minor_1 - random.randint(1, multiplier - 1)
                    else:
                        total_minor_2 = total_minor_1 + random.randint(1, multiplier - 1)

                    str_val_1 = f"{val_major} {u_major} {val_minor} {u_minor}"
                    str_val_2 = f"{total_minor_2:,} {u_minor}"

                    if random.choice([True, False]):
                        item_A, item_B = str_val_1, str_val_2
                        val_A, val_B = total_minor_1, total_minor_2
                    else:
                        item_A, item_B = str_val_2, str_val_1
                        val_A, val_B = total_minor_2, total_minor_1

                    if total_minor_1 == total_minor_2:
                        final_ans = "จุเท่ากัน"
                    else:
                        final_ans = "จุมากกว่า" if val_A > val_B else "จุน้อยกว่า"
                        
                    q = f"จงเติมคำว่า <b>จุมากกว่า, จุน้อยกว่า</b> หรือ <b>เท่ากับ</b> ลงในช่องว่างให้ถูกต้อง<br><br><span style='font-size:22px; font-weight:bold; margin-left: 20px;'>{item_A} &nbsp;&nbsp; ____________________ &nbsp;&nbsp; {item_B}</span>"

                    sol = f"""<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด (การเปรียบเทียบความจุ):</b><br>
                    <b>ขั้นที่ 1: สร้างสมการแปลงหน่วยให้เหมือนกัน</b><br>
                    👉 แปลง <b>{str_val_1}</b> ให้เป็น <b>{u_minor}</b> ทั้งหมด<br>
                    👉 เนื่องจาก 1 {u_major} = {multiplier:,} {u_minor}<br>
                    👉 <b>สมการล่าสุด:</b> ({val_major} <b style='color:red;'>× {multiplier:,}</b>) + {val_minor} = {val_major * multiplier:,} + {val_minor} = <b>{total_minor_1:,} {u_minor}</b><br>
                    <b>ขั้นที่ 2: เปรียบเทียบปริมาตร</b><br>"""

                    if val_A == val_B:
                        sol += f"👉 จะเห็นว่า {total_minor_1:,} {u_minor} <b>เท่ากับ</b> {total_minor_2:,} {u_minor} พอดี!<br>"
                    else:
                        comp_sign = "น้อยกว่า" if val_A < val_B else "มากกว่า"
                        sol += f"👉 เปรียบเทียบ {val_A:,} {u_minor} กับ {val_B:,} {u_minor}<br>"
                        sol += f"👉 จะเห็นว่า {val_A:,} <b>{comp_sign}</b> {val_B:,}<br>"

                    sol += f"<b>ตอบ: {final_ans}</b></span>"

                elif q_cat == "add_sub":
                    op = random.choice(["+", "-"])
                    v1_maj = random.randint(3, 10)
                    v1_min = random.randint(100, 900)
                    v2_maj = random.randint(1, v1_maj-1) if op == "-" else random.randint(1, 10)
                    v2_min = random.randint(100, 900)
                    
                    if op == "-":
                        if v1_min >= v2_min:
                            v1_min, v2_min = v2_min, v1_min + 50
                            if v2_min >= 1000: v2_min = 950
                    
                    svg = draw_beakers_svg(v1_maj, v1_min, v2_maj, v2_min)
                    
                    if op == "+":
                        q = f"{svg}จากรูป ถ้านำน้ำจากทั้งสองถังมา<b>รวมกัน</b> จะได้ปริมาตรน้ำทั้งหมดเท่าไร?"
                    else:
                        q = f"{svg}จากรูป ถัง A กับถัง B มีปริมาตรน้ำ<b>ต่างกันอยู่เท่าไร</b>?"
                        
                    table_html, ans_str = generate_unit_math_html(u_major, u_minor, v1_maj, v1_min, v2_maj, v2_min, op, multiplier)
                    
                    sol = f"""<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด (การตั้ง{'บวก' if op=='+' else 'ลบ'}แบบข้ามหน่วย):</b><br>
                    {table_html}
                    <b>ตอบ: {ans_str}</b></span>"""

                else: # divide
                    items = ["น้ำผลไม้", "นมสด", "น้ำยาซักผ้า", "น้ำแร่", "น้ำเชื่อม"]
                    containers = ["ขวด", "แก้ว", "เหยือก", "ถ้วย"]
                    item = random.choice(items)
                    container = random.choice(containers)
                    
                    if is_challenge:
                        N_ml = random.choice([150, 200, 250, 300, 450, 500])
                        tot_l = random.randint(3, 8)
                        tot_ml = random.randint(100, 900)
                        total_vol_ml = tot_l * 1000 + tot_ml
                        
                        bottles = total_vol_ml // N_ml
                        rem_ml = total_vol_ml % N_ml
                        
                        q = f"มี{item}อยู่ <b>{tot_l} ลิตร {tot_ml} มิลลิลิตร</b> ต้องการนำไปแบ่งใส่{container} {container}ละ <b>{N_ml} มิลลิลิตร</b> เท่าๆ กัน<br>จะสามารถแบ่งได้กี่{container} และจะเหลือ{item}เศษอีกกี่มิลลิลิตร?"
                        
                        sol = f"""<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด (🔥 ชาเลนจ์ - การหารแบบมีเศษ):</b><br>
                        <b>ขั้นที่ 1: แปลงปริมาตรทั้งหมดให้เป็นมิลลิลิตร</b><br>
                        👉 {tot_l} ลิตร {tot_ml} มล. = ({tot_l} × 1,000) + {tot_ml} = <b>{total_vol_ml:,} มล.</b><br>
                        <b>ขั้นที่ 2: นำไปหารด้วยความจุต่อ{container}</b><br>
                        👉 ตั้งหาร: {total_vol_ml:,} ÷ {N_ml} <br>
                        👉 จะได้ผลหาร <b>{bottles}</b> และเหลือเศษ <b>{rem_ml}</b><br>
                        <b>ตอบ: แบ่งได้ {bottles} {container} และเหลือเศษ {rem_ml} มิลลิลิตร</b></span>"""
                    else:
                        N = random.randint(3, 9)
                        ans_maj = random.randint(0, 2)
                        ans_min = random.randint(15, 85) * 10
                        if ans_maj == 0 and ans_min < 200: ans_min += 300
                        
                        ans_total_min = ans_maj * multiplier + ans_min
                        total_min = ans_total_min * N
                        
                        tot_maj = total_min // multiplier
                        tot_rem_min = total_min % multiplier
                        
                        str_tot = f"{tot_maj} {u_major} {tot_rem_min} {u_minor}" if tot_rem_min > 0 else f"{tot_maj} {u_major}"
                        str_ans = f"{ans_maj} {u_major} {ans_min} {u_minor}" if ans_maj > 0 else f"{ans_min} {u_minor}"
                        
                        q = f"มี{item}อยู่ <b>{str_tot}</b> ถ้าต้องการแบ่งใส่{container} ทั้งหมด <b>{N} {container}</b> ({container}ละเท่าๆ กัน) <br>จะได้{item}{container}ละเท่าไร?"
                        
                        sol = f"""<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด (โจทย์ปัญหาการแบ่งปริมาตร):</b><br>
                        <b>ขั้นที่ 1: แปลงปริมาตรทั้งหมดให้เป็นหน่วยเล็กสุด ({u_minor})</b><br>
                        👉 ปริมาตรทั้งหมด = ({tot_maj} × {multiplier:,}) + {tot_rem_min} = <b>{total_min:,} {u_minor}</b><br>
                        <b>ขั้นที่ 2: นำปริมาตรทั้งหมดมาหารด้วยจำนวน{container}</b><br>
                        👉 {total_min:,} ÷ {N} = <b>{ans_total_min:,} {u_minor}</b><br>
                        <b>ขั้นที่ 3: แปลงหน่วยกลับเป็น {u_major} และ {u_minor}</b><br>
                        👉 นำ {ans_total_min:,} ÷ {multiplier:,} จะได้ <b>{ans_maj} {u_major}</b> และเศษ <b>{ans_min} {u_minor}</b><br>
                        <b>ตอบ: {str_ans}</b></span>"""

            elif actual_sub_t == "การเปรียบเทียบหน่วยการวัด และการแปลงหน่วย (มิลลิเมตร เซนติเมตร เมตร)":
                q_cat = random.choice(["compare", "add_sub"])
                selected_type = random.choice(["cm_mm", "m_cm"])
                if selected_type == "cm_mm":
                    u_major, u_minor = "เซนติเมตร", "มิลลิเมตร"
                    multiplier = 10
                else: # m_cm
                    u_major, u_minor = "เมตร", "เซนติเมตร"
                    multiplier = 100
                    
                if q_cat == "compare":
                    val_major = random.randint(5, 50) if is_challenge else random.randint(2, 20)
                    val_minor = random.randint(1, multiplier-1)
                    
                    total_minor_1 = (val_major * multiplier) + val_minor
                    case = random.choice(["greater", "less", "equal"])
                    if case == "equal":
                        total_minor_2 = total_minor_1
                    elif case == "greater":
                        total_minor_2 = total_minor_1 - random.randint(1, multiplier - 1)
                    else:
                        total_minor_2 = total_minor_1 + random.randint(1, multiplier - 1)

                    str_val_1 = f"{val_major} {u_major} {val_minor} {u_minor}"
                    str_val_2 = f"{total_minor_2:,} {u_minor}"

                    if random.choice([True, False]):
                        item_A, item_B = str_val_1, str_val_2
                        val_A, val_B = total_minor_1, total_minor_2
                    else:
                        item_A, item_B = str_val_2, str_val_1
                        val_A, val_B = total_minor_2, total_minor_1

                    if total_minor_1 == total_minor_2:
                        final_ans = "ยาวเท่ากัน"
                    else:
                        final_ans = "ยาวกว่า" if val_A > val_B else "สั้นกว่า"
                        
                    q = f"จงเติมคำว่า <b>ยาวกว่า, สั้นกว่า</b> หรือ <b>เท่ากับ</b> ลงในช่องว่างให้ถูกต้อง<br><br><span style='font-size:22px; font-weight:bold; margin-left: 20px;'>{item_A} &nbsp;&nbsp; ____________________ &nbsp;&nbsp; {item_B}</span>"

                    sol = f"""<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด (การเปรียบเทียบความยาว):</b><br>
                    <b>ขั้นที่ 1: สร้างสมการแปลงหน่วยให้เหมือนกัน</b><br>
                    👉 แปลง <b>{str_val_1}</b> ให้เป็น <b>{u_minor}</b> ทั้งหมด<br>
                    👉 เนื่องจาก 1 {u_major} = {multiplier:,} {u_minor}<br>
                    👉 <b>สมการล่าสุด:</b> ({val_major} <b style='color:red;'>× {multiplier:,}</b>) + {val_minor} = {val_major * multiplier:,} + {val_minor} = <b>{total_minor_1:,} {u_minor}</b><br>
                    <b>ขั้นที่ 2: เปรียบเทียบความยาว</b><br>"""

                    if val_A == val_B:
                        sol += f"👉 จะเห็นว่า {total_minor_1:,} {u_minor} <b>เท่ากับ</b> {total_minor_2:,} {u_minor} พอดี!<br>"
                    else:
                        comp_sign = "น้อยกว่า" if val_A < val_B else "มากกว่า"
                        sol += f"👉 เปรียบเทียบ {val_A:,} {u_minor} กับ {val_B:,} {u_minor}<br>"
                        sol += f"👉 จะเห็นว่า {val_A:,} <b>{comp_sign}</b> {val_B:,}<br>"

                    sol += f"<b>ตอบ: {final_ans}</b></span>"
                else: # add_sub
                    op = random.choice(["+", "-"])
                    v1_maj = random.randint(3, 20)
                    v1_min = random.randint(1, multiplier-1)
                    v2_maj = random.randint(1, v1_maj-1) if op == "-" else random.randint(1, 20)
                    v2_min = random.randint(1, multiplier-1)
                    
                    if op == "-":
                        if v1_min >= v2_min:
                            v1_min, v2_min = v2_min, v1_min + (multiplier//2)
                            if v2_min >= multiplier: v2_min = multiplier - 1
                    
                    if op == "+":
                        q = f"สิ่งของชิ้นแรกยาว <b>{v1_maj} {u_major} {v1_min} {u_minor}</b> และชิ้นที่สองยาว <b>{v2_maj} {u_major} {v2_min} {u_minor}</b> <br>ถ้านำมาวางต่อกันจะมีความยาว<b>รวมกัน</b>เท่าไร?"
                    else:
                        q = f"สิ่งของชิ้นแรกยาว <b>{v1_maj} {u_major} {v1_min} {u_minor}</b> และชิ้นที่สองยาว <b>{v2_maj} {u_major} {v2_min} {u_minor}</b> <br>สิ่งของสองชิ้นนี้มีความยาว<b>ต่างกันอยู่เท่าไร</b>?"
                        
                    table_html, ans_str = generate_unit_math_html(u_major, u_minor, v1_maj, v1_min, v2_maj, v2_min, op, multiplier)
                    sol = f"""<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด (การตั้ง{'บวก' if op=='+' else 'ลบ'}แบบข้ามหน่วย):</b><br>
                    {table_html}
                    <b>ตอบ: {ans_str}</b></span>"""

            elif actual_sub_t == "การเปรียบเทียบหน่วยระยะทาง และการแปลงหน่วย (เมตร กิโลเมตร)":
                q_cat = random.choice(["compare", "add_sub"])
                u_major, u_minor = "กิโลเมตร", "เมตร"
                multiplier = 1000
                
                if q_cat == "compare":
                    val_major = random.randint(2, 20) if is_challenge else random.randint(1, 9)
                    val_minor = random.randint(50, 950)
                    
                    total_minor_1 = (val_major * multiplier) + val_minor
                    case = random.choice(["greater", "less", "equal"])
                    if case == "equal":
                        total_minor_2 = total_minor_1
                    elif case == "greater":
                        total_minor_2 = total_minor_1 - random.randint(1, multiplier - 1)
                    else:
                        total_minor_2 = total_minor_1 + random.randint(1, multiplier - 1)

                    str_val_1 = f"{val_major} {u_major} {val_minor} {u_minor}"
                    str_val_2 = f"{total_minor_2:,} {u_minor}"

                    if random.choice([True, False]):
                        item_A, item_B = str_val_1, str_val_2
                        val_A, val_B = total_minor_1, total_minor_2
                    else:
                        item_A, item_B = str_val_2, str_val_1
                        val_A, val_B = total_minor_2, total_minor_1

                    if total_minor_1 == total_minor_2:
                        final_ans = "ไกลเท่ากัน"
                    else:
                        final_ans = "ไกลกว่า" if val_A > val_B else "ใกล้กว่า"
                        
                    q = f"จงเติมคำว่า <b>ไกลกว่า, ใกล้กว่า</b> หรือ <b>เท่ากับ</b> ลงในช่องว่างให้ถูกต้อง<br><br><span style='font-size:22px; font-weight:bold; margin-left: 20px;'>{item_A} &nbsp;&nbsp; ____________________ &nbsp;&nbsp; {item_B}</span>"

                    sol = f"""<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด (การเปรียบเทียบระยะทาง):</b><br>
                    <b>ขั้นที่ 1: สร้างสมการแปลงหน่วยให้เหมือนกัน</b><br>
                    👉 แปลง <b>{str_val_1}</b> ให้เป็น <b>{u_minor}</b> ทั้งหมด<br>
                    👉 เนื่องจาก 1 {u_major} = {multiplier:,} {u_minor}<br>
                    👉 <b>สมการล่าสุด:</b> ({val_major} <b style='color:red;'>× {multiplier:,}</b>) + {val_minor} = {val_major * multiplier:,} + {val_minor} = <b>{total_minor_1:,} {u_minor}</b><br>
                    <b>ขั้นที่ 2: เปรียบเทียบระยะทาง</b><br>"""

                    if val_A == val_B:
                        sol += f"👉 จะเห็นว่า {total_minor_1:,} {u_minor} <b>เท่ากับ</b> {total_minor_2:,} {u_minor} พอดี!<br>"
                    else:
                        comp_sign = "น้อยกว่า" if val_A < val_B else "มากกว่า"
                        sol += f"👉 เปรียบเทียบ {val_A:,} {u_minor} กับ {val_B:,} {u_minor}<br>"
                        sol += f"👉 จะเห็นว่า {val_A:,} <b>{comp_sign}</b> {val_B:,}<br>"

                    sol += f"<b>ตอบ: {final_ans}</b></span>"
                else: # add_sub
                    op = random.choice(["+", "-"])
                    v1_maj = random.randint(5, 50)
                    v1_min = random.randint(100, 900)
                    v2_maj = random.randint(1, v1_maj-1) if op == "-" else random.randint(1, 50)
                    v2_min = random.randint(100, 900)
                    
                    if op == "-":
                        if v1_min >= v2_min:
                            v1_min, v2_min = v2_min, v1_min + 500
                            if v2_min >= 1000: v2_min = 950
                            
                    if op == "+":
                        q = f"ระยะทาง <b>{v1_maj} {u_major} {v1_min} {u_minor}</b> กับ <b>{v2_maj} {u_major} {v2_min} {u_minor}</b> <br>ถ้านำระยะทางมา<b>รวมกัน</b> จะได้ระยะทางทั้งหมดเท่าไร?"
                    else:
                        q = f"ระยะทาง <b>{v1_maj} {u_major} {v1_min} {u_minor}</b> กับ <b>{v2_maj} {u_major} {v2_min} {u_minor}</b> <br>ระยะทางทั้งสองนี้<b>ต่างกันอยู่เท่าไร</b>?"
                        
                    table_html, ans_str = generate_unit_math_html(u_major, u_minor, v1_maj, v1_min, v2_maj, v2_min, op, multiplier)
                    sol = f"""<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด (การตั้ง{'บวก' if op=='+' else 'ลบ'}แบบข้ามหน่วย):</b><br>
                    {table_html}
                    <b>ตอบ: {ans_str}</b></span>"""

            elif actual_sub_t == "การเปรียบเทียบหน่วยน้ำหนัก และการแปลงหน่วย (กรัม กิโลกรัม ตัน)":
                q_cat = random.choice(["compare", "add_sub", "divide"]) # เพิ่มการหาร (divide) เข้ามา
                selected_type = random.choice(["kg_g", "ton_kg"])
                if selected_type == "kg_g":
                    u_major, u_minor = "กิโลกรัม", "กรัม"
                else: # ton_kg
                    u_major, u_minor = "ตัน", "กิโลกรัม"
                multiplier = 1000
                
                if q_cat == "compare":
                    val_major = random.randint(5, 50) if is_challenge else random.randint(1, 15)
                    val_minor = random.randint(50, 950)
                    
                    total_minor_1 = (val_major * multiplier) + val_minor
                    case = random.choice(["greater", "less", "equal"])
                    if case == "equal":
                        total_minor_2 = total_minor_1
                    elif case == "greater":
                        total_minor_2 = total_minor_1 - random.randint(1, multiplier - 1)
                    else:
                        total_minor_2 = total_minor_1 + random.randint(1, multiplier - 1)

                    str_val_1 = f"{val_major} {u_major} {val_minor} {u_minor}"
                    str_val_2 = f"{total_minor_2:,} {u_minor}"

                    if random.choice([True, False]):
                        item_A, item_B = str_val_1, str_val_2
                        val_A, val_B = total_minor_1, total_minor_2
                    else:
                        item_A, item_B = str_val_2, str_val_1
                        val_A, val_B = total_minor_2, total_minor_1

                    if total_minor_1 == total_minor_2:
                        final_ans = "หนักเท่ากัน"
                    else:
                        final_ans = "หนักกว่า" if val_A > val_B else "เบากว่า"
                        
                    q = f"จงเติมคำว่า <b>หนักกว่า, เบากว่า</b> หรือ <b>เท่ากับ</b> ลงในช่องว่างให้ถูกต้อง<br><br><span style='font-size:22px; font-weight:bold; margin-left: 20px;'>{item_A} &nbsp;&nbsp; ____________________ &nbsp;&nbsp; {item_B}</span>"

                    sol = f"""<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด (การเปรียบเทียบน้ำหนัก):</b><br>
                    <b>ขั้นที่ 1: สร้างสมการแปลงหน่วยให้เหมือนกัน</b><br>
                    👉 แปลง <b>{str_val_1}</b> ให้เป็น <b>{u_minor}</b> ทั้งหมด<br>
                    👉 เนื่องจาก 1 {u_major} = {multiplier:,} {u_minor}<br>
                    👉 <b>สมการล่าสุด:</b> ({val_major} <b style='color:red;'>× {multiplier:,}</b>) + {val_minor} = {val_major * multiplier:,} + {val_minor} = <b>{total_minor_1:,} {u_minor}</b><br>
                    <b>ขั้นที่ 2: เปรียบเทียบน้ำหนัก</b><br>"""

                    if val_A == val_B:
                        sol += f"👉 จะเห็นว่า {total_minor_1:,} {u_minor} <b>เท่ากับ</b> {total_minor_2:,} {u_minor} พอดี!<br>"
                    else:
                        comp_sign = "น้อยกว่า" if val_A < val_B else "มากกว่า"
                        sol += f"👉 เปรียบเทียบ {val_A:,} {u_minor} กับ {val_B:,} {u_minor}<br>"
                        sol += f"👉 จะเห็นว่า {val_A:,} <b>{comp_sign}</b> {val_B:,}<br>"

                    sol += f"<b>ตอบ: {final_ans}</b></span>"
                elif q_cat == "add_sub":
                    op = random.choice(["+", "-"])
                    v1_maj = random.randint(5, 50)
                    v1_min = random.randint(100, 900)
                    v2_maj = random.randint(1, v1_maj-1) if op == "-" else random.randint(1, 50)
                    v2_min = random.randint(100, 900)
                    
                    if op == "-":
                        if v1_min >= v2_min:
                            v1_min, v2_min = v2_min, v1_min + 500
                            if v2_min >= 1000: v2_min = 950
                            
                    if op == "+":
                        q = f"สิ่งของชิ้นแรกหนัก <b>{v1_maj} {u_major} {v1_min} {u_minor}</b> และชิ้นที่สองหนัก <b>{v2_maj} {u_major} {v2_min} {u_minor}</b> <br>ถ้านำมาชั่ง<b>รวมกัน</b> จะได้น้ำหนักทั้งหมดเท่าไร?"
                    else:
                        q = f"สิ่งของชิ้นแรกหนัก <b>{v1_maj} {u_major} {v1_min} {u_minor}</b> และชิ้นที่สองหนัก <b>{v2_maj} {u_major} {v2_min} {u_minor}</b> <br>สิ่งของสองชิ้นนี้มีน้ำหนัก<b>ต่างกันอยู่เท่าไร</b>?"
                        
                    table_html, ans_str = generate_unit_math_html(u_major, u_minor, v1_maj, v1_min, v2_maj, v2_min, op, multiplier)
                    sol = f"""<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด (การตั้ง{'บวก' if op=='+' else 'ลบ'}แบบข้ามหน่วย):</b><br>
                    {table_html}
                    <b>ตอบ: {ans_str}</b></span>"""
                else: # divide (เพิ่มการหารน้ำหนัก)
                    if selected_type == "kg_g":
                        items = ["เนื้อหมู", "แป้งทำขนม", "น้ำตาลทราย", "เกลือ", "ผักกาด"]
                        containers = ["ถุง", "กล่อง", "ตะกร้า", "แพ็ค"]
                    else:
                        items = ["น้ำตาล", "ข้าวสาร", "ปุ๋ย", "ทราย", "อาหารสัตว์"]
                        containers = ["กระสอบ", "คันรถ", "เข่ง"]
                    
                    item = random.choice(items)
                    container = random.choice(containers)
                    N = random.randint(3, 9)
                    
                    ans_maj = random.randint(0, 2)
                    ans_min = random.randint(15, 85) * 10
                    if ans_maj == 0 and ans_min < 200: ans_min += 300
                    
                    ans_total_min = ans_maj * multiplier + ans_min
                    total_min = ans_total_min * N
                    
                    tot_maj = total_min // multiplier
                    tot_rem_min = total_min % multiplier
                    
                    str_tot = f"{tot_maj} {u_major} {tot_rem_min} {u_minor}" if tot_rem_min > 0 else f"{tot_maj} {u_major}"
                    str_ans = f"{ans_maj} {u_major} {ans_min} {u_minor}" if ans_maj > 0 else f"{ans_min} {u_minor}"
                    
                    q = f"มี{item}อยู่ <b>{str_tot}</b> ถ้าต้องการแบ่งใส่{container} ทั้งหมด <b>{N} {container}</b> ({container}ละเท่าๆ กัน) <br>จะได้{item}{container}ละเท่าไร?"
                    
                    sol = f"""<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด (โจทย์ปัญหาการแบ่ง/หารหน่วยน้ำหนัก):</b><br>
                    <b>ขั้นที่ 1: แปลงหน่วยน้ำหนักทั้งหมดให้เป็นหน่วยเล็กสุด ({u_minor}) เพื่อให้คำนวณง่าย</b><br>
                    👉 น้ำหนักทั้งหมด = {tot_maj} {u_major} {tot_rem_min} {u_minor}<br>
                    👉 นำมาแปลงเป็น{u_minor}: ({tot_maj} × {multiplier:,}) + {tot_rem_min} = <b>{total_min:,} {u_minor}</b><br>
                    <b>ขั้นที่ 2: นำน้ำหนักทั้งหมดมาหารด้วยจำนวน{container}</b><br>
                    👉 ต้องการแบ่ง {N} {container} นำไปหาร: {total_min:,} ÷ {N} = <b>{ans_total_min:,} {u_minor}</b><br>
                    <b>ขั้นที่ 3: แปลงหน่วยกลับเป็น {u_major} และ {u_minor}</b><br>
                    👉 นำ {ans_total_min:,} ÷ {multiplier:,} จะได้ <b>{ans_maj} {u_major}</b> และเศษ <b>{ans_min} {u_minor}</b><br>
                    <b>ตอบ: {str_ans}</b></span>"""

            elif actual_sub_t == "โจทย์ปัญหาความยาว (คูณและหาร)":
                q_type = random.choice(["fit_objects", "equal_parts", "multiply_length"])
                
                if q_type == "fit_objects":
                    room = random.choice(ROOMS)
                    furn = random.choice(FURNITURE)
                    
                    if is_challenge:
                        r_m = random.randint(5, 12)
                        r_cm = random.choice([15, 35, 45, 75, 95])
                        f_m = random.randint(0, 1)
                        f_cm = random.choice([45, 65, 85, 125]) if f_m == 0 else random.choice([15, 35, 55])
                    else:
                        r_m = random.randint(3, 8)
                        r_cm = random.choice([0, 20, 50, 80])
                        f_m = random.randint(0, 1)
                        f_cm = random.choice([50, 60, 80, 100]) if f_m == 0 else random.choice([0, 20, 50])
                        
                    if f_m == 0 and f_cm < 40: f_cm = 50 
                    if f_m == 1 and f_cm == 100: f_m, f_cm = 2, 0
                    
                    room_total_cm = r_m * 100 + r_cm
                    furn_total_cm = f_m * 100 + f_cm
                    
                    count = room_total_cm // furn_total_cm
                    rem_cm = room_total_cm % furn_total_cm
                    
                    room_str = f"{r_m} เมตร {r_cm} เซนติเมตร" if r_cm > 0 else f"{r_m} เมตร"
                    furn_str = f"{f_m} เมตร {f_cm} เซนติเมตร" if f_m > 0 and f_cm > 0 else (f"{f_m} เมตร" if f_cm == 0 else f"{f_cm} เซนติเมตร")
                    
                    q = f"<b>{room}</b> มีความกว้าง {room_str} <br>ถ้าต้องการนำ <b>{furn}</b> ที่มีความกว้าง {furn_str} มาวางเรียงติดกัน <br>จะสามารถวาง{furn}ได้มากที่สุดกี่ตัว และเหลือพื้นที่ว่างกี่เซนติเมตร?"
                    
                    sol = f"""<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด (โจทย์ปัญหาการหาร):</b><br>
                    <b>ขั้นที่ 1: แปลงหน่วยให้เป็นเซนติเมตรทั้งหมด เพื่อให้คำนวณง่ายขึ้น</b><br>
                    👉 ความกว้างของ{room} = {r_m} เมตร {r_cm} ซม. ➔ ({r_m} × 100) + {r_cm} = <b>{room_total_cm} เซนติเมตร</b><br>
                    👉 ความกว้างของ{furn} = {f_m} เมตร {f_cm} ซม. ➔ ({f_m} × 100) + {f_cm} = <b>{furn_total_cm} เซนติเมตร</b><br>
                    <b>ขั้นที่ 2: นำความกว้างห้องมาตั้ง หารด้วยความกว้างเฟอร์นิเจอร์</b><br>
                    👉 {room_total_cm} ÷ {furn_total_cm} ได้ <b>{count}</b> เศษ <b>{rem_cm}</b><br>
                    <b>ขั้นที่ 3: สรุปคำตอบ</b><br>
                    👉 ผลหารคือจำนวน{furn}ที่สามารถจัดวางได้ = {count} ตัว<br>
                    👉 เศษที่เหลือคือพื้นที่ว่าง = {rem_cm} เซนติเมตร<br>
                    <b>ตอบ: วางได้ {count} ตัว และเหลือพื้นที่ว่าง {rem_cm} เซนติเมตร</b></span>"""

                elif q_type == "equal_parts":
                    material = random.choice(["เชือก", "ริบบิ้น", "ลวด", "ผ้า", "ไม้กระดาน"])
                    N = random.randint(3, 8) if not is_challenge else random.randint(6, 15)
                    ans_m = random.randint(0, 2)
                    ans_cm = random.randint(10, 95)
                    piece_total_cm = ans_m * 100 + ans_cm
                    
                    total_cm = piece_total_cm * N
                    tot_m = total_cm // 100
                    tot_cm = total_cm % 100
                    
                    tot_str = f"{tot_m} เมตร {tot_cm} เซนติเมตร" if tot_cm > 0 else f"{tot_m} เมตร"
                    ans_str = f"{ans_m} เมตร {ans_cm} เซนติเมตร" if ans_m > 0 else f"{ans_cm} เซนติเมตร"
                    
                    q = f"มี{material}ยาว {tot_str} <br>นำมาตัดแบ่งเป็น {N} ส่วนยาวเท่าๆ กัน <br>{material}แต่ละส่วนจะมีความยาวเท่าไร?"
                    
                    sol = f"""<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด (โจทย์ปัญหาการหาร):</b><br>
                    <b>ขั้นที่ 1: แปลงหน่วยเป็นเซนติเมตรเพื่อการคำนวณที่ง่ายขึ้น</b><br>
                    👉 ความยาว{material}ทั้งหมด = {tot_m} เมตร {tot_cm} ซม. ➔ ({tot_m} × 100) + {tot_cm} = <b>{total_cm} เซนติเมตร</b><br>
                    <b>ขั้นที่ 2: นำความยาวทั้งหมดมาหารด้วยจำนวนที่ต้องการแบ่ง</b><br>
                    👉 นำ {total_cm} ÷ {N} = <b>{piece_total_cm} เซนติเมตร</b><br>
                    <b>ขั้นที่ 3: แปลงหน่วยกลับเป็นเมตรและเซนติเมตร</b><br>
                    👉 {piece_total_cm} เซนติเมตร คิดเป็น <b>{ans_str}</b><br>
                    <b>ตอบ: {ans_str}</b></span>"""
                    
                elif q_type == "multiply_length":
                    furn = random.choice(FURNITURE)
                    N = random.randint(3, 9) if not is_challenge else random.randint(8, 25)
                    f_m = random.randint(0, 2)
                    f_cm = random.randint(15, 95)
                    furn_total_cm = f_m * 100 + f_cm
                    
                    total_cm = furn_total_cm * N
                    tot_m = total_cm // 100
                    tot_cm = total_cm % 100
                    
                    furn_str = f"{f_m} เมตร {f_cm} เซนติเมตร" if f_m > 0 else f"{f_cm} เซนติเมตร"
                    tot_str = f"{tot_m} เมตร {tot_cm} เซนติเมตร" if tot_cm > 0 else f"{tot_m} เมตร"
                    
                    q = f"<b>{furn}</b> 1 ตัว มีความยาว {furn_str} <br>ถ้านำ{furn}รุ่นเดียวกันจำนวน {N} ตัว มาวางต่อกันเป็นแนวยาว <br>จะมีความยาวรวมทั้งหมดกี่เมตร กี่เซนติเมตร?"
                    
                    sol = f"""<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด (โจทย์ปัญหาการคูณ):</b><br>
                    <b>ขั้นที่ 1: ตั้งคูณความยาวของ{furn} 1 ตัว ด้วยจำนวนตัว</b><br>
                    👉 {furn} 1 ตัว ยาว {f_m} เมตร {f_cm} เซนติเมตร นำมาคูณด้วย {N}<br>
                    👉 แยกคูณหน่วยเซนติเมตร และหน่วยเมตร<br>
                    <b>ขั้นที่ 2: คูณหน่วยเซนติเมตร</b><br>
                    👉 {f_cm} × {N} = <b>{f_cm * N} เซนติเมตร</b><br>"""
                    
                    carry_m = (f_cm * N) // 100
                    rem_cm = (f_cm * N) % 100
                    
                    if carry_m > 0:
                        sol += f"👉 เนื่องจากผลลัพธ์เกิน 100 เซนติเมตร ให้แปลงเป็นเมตร จะได้ <b>{carry_m} เมตร กับอีก {rem_cm} เซนติเมตร</b> (นำ {carry_m} เมตรไปทดไว้)<br>"
                        
                    sol += f"""<b>ขั้นที่ 3: คูณหน่วยเมตร</b><br>
                    👉 {f_m} × {N} = <b>{f_m * N} เมตร</b><br>"""
                    
                    if carry_m > 0:
                        sol += f"👉 รวมกับที่ทดมาอีก {carry_m} เมตร จะได้ {f_m * N} + {carry_m} = <b>{tot_m} เมตร</b><br>"
                        
                    sol += f"""<b>ตอบ: {tot_str}</b></span>"""

            elif actual_sub_t == "ระยะทาง (กิโลเมตรและเมตร)":
                p_names = random.sample(list(PLACE_EMOJIS.keys()), 3)
                p_emojis = [PLACE_EMOJIS[n] for n in p_names]
                
                if is_challenge:
                    q_type = random.choice(["diff", "roundtrip"])
                else:
                    q_type = random.choice(["convert_to_km", "convert_to_m", "add"])

                if q_type == "convert_to_km":
                    dist_m = random.randint(1100, 9800)
                    km = dist_m // 1000
                    m = dist_m % 1000
                    svg = draw_distance_route_svg([p_names[0], p_names[1]], [p_emojis[0], p_emojis[1]], [f"{dist_m:,} ม."])
                    q = svg + f"<br>ระยะทางจาก <b>{p_names[0]}</b> ไปถึง <b>{p_names[1]}</b> คือ {dist_m:,} เมตร<br>คิดเป็นระยะทางกี่กิโลเมตร กี่เมตร?"
                    sol = f"""<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>
                    <b>ขั้นที่ 1:</b> ทบทวนความรู้: <b>1,000 เมตร = 1 กิโลเมตร</b><br>
                    <b>ขั้นที่ 2:</b> แยกตัวเลข {dist_m:,} เมตร ออกเป็นส่วนหลักพันและส่วนที่เหลือ<br>
                    👉 จะได้ {km * 1000:,} เมตร + {m} เมตร<br>
                    <b>ขั้นที่ 3:</b> แปลง {km * 1000:,} เมตร เป็น {km} กิโลเมตร<br>
                    <b>ตอบ: {km} กิโลเมตร {m} เมตร</b></span>"""
                    
                elif q_type == "convert_to_m":
                    km = random.randint(1, 9)
                    m = random.randint(50, 950)
                    total_m = (km * 1000) + m
                    svg = draw_distance_route_svg([p_names[0], p_names[1]], [p_emojis[0], p_emojis[1]], [f"{km} กม. {m} ม."])
                    q = svg + f"<br>ระยะทางจาก <b>{p_names[0]}</b> ไป <b>{p_names[1]}</b> คือ {km} กิโลเมตร {m} เมตร<br>คิดเป็นระยะทางทั้งหมดกี่เมตร?"
                    sol = f"""<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>
                    <b>ขั้นที่ 1:</b> ทบทวนความรู้: <b>1 กิโลเมตร = 1,000 เมตร</b><br>
                    <b>ขั้นที่ 2:</b> แปลง {km} กิโลเมตร ให้เป็นหน่วยเมตร ➔ {km} × 1,000 = {km * 1000:,} เมตร<br>
                    <b>ขั้นที่ 3:</b> นำไปบวกกับระยะทางที่เหลืออีก {m} เมตร<br>
                    👉 {km * 1000:,} + {m} = <b>{total_m:,} เมตร</b><br>
                    <b>ตอบ: {total_m:,} เมตร</b></span>"""
                    
                elif q_type == "add":
                    km1, m1 = random.randint(1, 5), random.randint(100, 800)
                    km2, m2 = random.randint(1, 5), random.randint(100, 800)
                    total_m = m1 + m2
                    carry_km = total_m // 1000
                    rem_m = total_m % 1000
                    total_km = km1 + km2 + carry_km
                    
                    svg = draw_distance_route_svg(p_names, p_emojis, [f"{km1} กม. {m1} ม.", f"{km2} กม. {m2} ม."])
                    q = svg + f"<br>{NAMES[0]}เดินทางจาก <b>{p_names[0]}</b> ผ่าน <b>{p_names[1]}</b> เพื่อไป <b>{p_names[2]}</b> ตามแผนที่<br>รวมระยะทางทั้งหมดกี่กิโลเมตร กี่เมตร?"
                    
                    sol = f"""<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>
                    นำระยะทางทั้งสองช่วงมาบวกกัน โดยแยกบวกหน่วยเมตรและกิโลเมตร<br>
                    <b>ขั้นที่ 1: บวกหน่วยเมตร</b><br>
                    👉 {m1} + {m2} = <b>{total_m} เมตร</b><br>"""
                    if carry_km > 0:
                        sol += f"👉 เนื่องจากเกิน 1,000 เมตร จึงปัด 1,000 เมตรเป็น 1 กิโลเมตร (เหลือ {rem_m} เมตร)<br>"
                    sol += f"""<b>ขั้นที่ 2: บวกหน่วยกิโลเมตร</b><br>
                    👉 {km1} + {km2} = {km1+km2} กิโลเมตร<br>"""
                    if carry_km > 0:
                        sol += f"👉 รวมกับที่ทดมาอีก 1 กิโลเมตร เป็น <b>{total_km} กิโลเมตร</b><br>"
                    sol += f"""<b>ตอบ: {total_km} กิโลเมตร {rem_m} เมตร</b></span>"""
                    
                elif q_type == "diff": 
                    km1, m1 = random.randint(4, 9), random.randint(100, 950)
                    km2, m2 = random.randint(1, km1-1), random.randint(100, 950)
                    
                    if m1 >= m2:
                        m1, m2 = m2, m1 + 50
                        if m2 >= 1000: m2 = 950
                        
                    dist1 = km1 * 1000 + m1
                    dist2 = km2 * 1000 + m2
                    diff = dist1 - dist2
                    diff_km = diff // 1000
                    diff_m = diff % 1000
                    
                    is_more = random.choice([True, False])
                    if is_more:
                        q_word = "ไกลกว่า"
                        sub_q = f"เส้นทางที่ 1 {q_word}เส้นทางที่ 2"
                    else:
                        q_word = "สั้นกว่า (ใกล้กว่า)"
                        sub_q = f"เส้นทางที่ 2 {q_word}เส้นทางที่ 1"
                    
                    q = f"เส้นทางที่ 1 จาก <b>{p_names[0]}</b> ไป <b>{p_names[1]}</b> ระยะทาง {km1} กิโลเมตร {m1} เมตร<br>เส้นทางที่ 2 จาก <b>{p_names[0]}</b> ไป <b>{p_names[2]}</b> ระยะทาง {km2} กิโลเมตร {m2} เมตร<br>{sub_q} อยู่กี่กิโลเมตร กี่เมตร?"
                    sol = f"""<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด (🔥 โหมดชาเลนจ์):</b><br>
                    นำระยะทางมาลบกันเพื่อหาผลต่าง โดยแยกตั้งหน่วยกิโลเมตรและเมตรให้ตรงกัน<br>
                    <b>ขั้นที่ 1: ลบหน่วยเมตร</b><br>
                    👉 นำ {m1} เมตร ลบด้วย {m2} เมตร ซึ่งตัวตั้งน้อยกว่าตัวลบ จึงลบไม่ได้<br>
                    👉 ต้องไป <b>ยืม</b> จากหน่วยกิโลเมตรมา 1 กม. (ซึ่งเท่ากับ 1,000 เมตร)<br>
                    👉 ทำให้หน่วยเมตรตัวตั้งกลายเป็น {m1} + 1,000 = {1000+m1} เมตร<br>
                    👉 นำ {1000+m1} - {m2} = <b>{diff_m} เมตร</b><br>
                    <b>ขั้นที่ 2: ลบหน่วยกิโลเมตร</b><br>
                    👉 ตัวตั้งถูกยืมไป 1 กม. จะเหลือ {km1-1} กม.<br>
                    👉 นำ {km1-1} - {km2} = <b>{diff_km} กิโลเมตร</b><br>
                    <b>ตอบ: {diff_km} กิโลเมตร {diff_m} เมตร</b></span>"""
                    
                elif q_type == "roundtrip": 
                    km, m = random.randint(2, 6), random.randint(300, 800)
                    dist_m = km * 1000 + m
                    total_m = dist_m * 2
                    tot_km = total_m // 1000
                    tot_m = total_m % 1000
                    
                    svg = draw_distance_route_svg([p_names[0], p_names[1]], [p_emojis[0], p_emojis[1]], [f"{km} กม. {m} ม."])
                    q = svg + f"<br>{NAMES[0]}ต้องเดินทางจาก <b>{p_names[0]}</b> ไป <b>{p_names[1]}</b> และเดินทางกลับตามเส้นทางเดิม<br>อยากทราบว่า{NAMES[0]}ต้องเดินทาง <b>ไป-กลับ</b> รวมระยะทางทั้งหมดกี่กิโลเมตร กี่เมตร?"
                    sol = f"""<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด (🔥 โหมดชาเลนจ์):</b><br>
                    คำว่า <b>"ไป-กลับ"</b> หมายถึงต้องเดินทาง 2 รอบ (ขาไป 1 รอบ ขากลับ 1 รอบ)<br>
                    <b>ขั้นที่ 1: นำระยะทางมาบวกกัน 2 ครั้ง (หรือคูณ 2)</b><br>
                    👉 ขาไป: {km} กม. {m} ม.<br>
                    👉 ขากลับ: {km} กม. {m} ม.<br>
                    <b>ขั้นที่ 2: รวมหน่วยเมตร</b><br>
                    👉 {m} + {m} = {m*2} เมตร<br>"""
                    if m*2 >= 1000:
                        sol += f"👉 แปลงหน่วย: {m*2} เมตร คิดเป็น 1 กิโลเมตร กับ {tot_m} เมตร<br>"
                    sol += f"""<b>ขั้นที่ 3: รวมหน่วยกิโลเมตร</b><br>
                    👉 {km} + {km} = {km*2} กิโลเมตร<br>"""
                    if m*2 >= 1000:
                        sol += f"👉 นำไปบวกกับที่ทดมาอีก 1 กม. จะได้ <b>{tot_km} กิโลเมตร</b><br>"
                    sol += f"""<b>ตอบ: {tot_km} กิโลเมตร {tot_m} เมตร</b></span>"""

            elif actual_sub_t == "การบอกเวลาเป็นนาฬิกาและนาที":
                h_24 = random.randint(0, 23)
                m = random.randint(0, 59)
                period = "เวลากลางวัน" if 6 <= h_24 <= 17 else "เวลากลางคืน"
                
                q = draw_clock_svg(h_24, m) + f"<br>จากรูปนาฬิกาด้านบน (กำหนดเป็น<b>{period}</b>) อ่านเวลาได้ว่าอย่างไร?"
                sol = f"""<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด (Step-by-step):</b><br>
                <b>ขั้นที่ 1: ดูเข็มสั้น (สีแดง) เพื่อบอกนาฬิกา</b><br>
                👉 เข็มสั้นชี้ที่เลข {h_24 % 12 if h_24 % 12 != 0 else 12} แต่โจทย์กำหนดเป็น <b>{period}</b> จึงอ่านค่าเป็น <b>{h_24:02d} นาฬิกา</b><br>
                <b>ขั้นที่ 2: ดูเข็มยาว (สีฟ้า) เพื่อบอกนาที</b><br>
                👉 เข็มยาวชี้เลยตัวเลขหลักมาอยู่ที่ขีดที่ {m} (นำช่องละ 5 นาทีมาบวกกัน) จึงอ่านค่าเป็น <b>{m:02d} นาที</b><br>
                <b>ขั้นที่ 3: นำมาอ่านรวมกัน</b><br>
                👉 จะได้ <b>{h_24:02d} นาฬิกา {m:02d} นาที</b><br>
                <b>ตอบ: {h_24:02d}:{m:02d} น. หรือ {h_24} นาฬิกา {m} นาที</b></span>"""

            elif actual_sub_t == "การอ่านน้ำหนักจากเครื่องชั่งสปริง":
                kg = random.randint(0, 4)
                kheed = random.randint(1, 9)
                g = kheed * 100
                
                q = draw_scale_svg(kg, kheed) + "<br>จากรูป เครื่องชั่งสปริงแสดงน้ำหนักเท่าไร? (ตอบเป็นกิโลกรัมและกรัม)"
                sol = f"""<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด (Step-by-step):</b><br>
                <b>ขั้นที่ 1: ดูเข็มชี้ตัวเลขหลัก (กิโลกรัม)</b><br>
                👉 เข็มสีแดงชี้เลยเลข <b>{kg}</b> มาแล้ว แปลว่ามีน้ำหนักหลักคือ <b>{kg} กิโลกรัม</b><br>
                <b>ขั้นที่ 2: นับขีดย่อย (1 ขีด = 100 กรัม)</b><br>
                👉 เข็มชี้เลยเลข {kg} ไป <b>{kheed} ขีดย่อย</b><br>
                👉 แปลงหน่วยขีดเป็นหน่วยกรัม: นำ {kheed} ขีด × 100 = <b>{g} กรัม</b><br>
                <b>ขั้นที่ 3: นำน้ำหนักมารวมกัน</b><br>
                👉 นำกิโลกรัมและกรัมมาต่อกัน ➔ <b>{kg} กิโลกรัม {g} กรัม</b><br>
                <b>ตอบ: {kg} กิโลกรัม {g} กรัม</b></span>"""

            elif actual_sub_t == "การอ่านความยาวจากไม้บรรทัด":
                if grade == "ป.3":
                    if is_challenge:
                        len_a = round(random.uniform(110.0, 350.0), 1)
                        len_b = round(random.uniform(110.0, 350.0), 1)
                        while abs(len_a - len_b) < 1.0: 
                            len_b = round(random.uniform(110.0, 350.0), 1)
                        
                        name_a, color_a = "สิ่งของ A", "#f1c40f"
                        name_b, color_b = "สิ่งของ B", "#3498db"
                        
                        svg_a = draw_long_ruler_svg(len_a, color_a, name_a)
                        svg_b = draw_long_ruler_svg(len_b, color_b, name_b)
                        
                        str_a = cm_to_m_cm_mm(len_a)
                        str_b = cm_to_m_cm_mm(len_b)
                        
                        is_ask_more = random.choice([True, False])
                        if is_ask_more:
                            compare_word = "มากกว่า"
                            if len_a > len_b:
                                target_name, other_name = name_a, name_b
                                diff_len = len_a - len_b
                            else:
                                target_name, other_name = name_b, name_a
                                diff_len = len_b - len_a
                        else:
                            compare_word = "น้อยกว่า"
                            if len_a < len_b:
                                target_name, other_name = name_a, name_b
                                diff_len = len_b - len_a
                            else:
                                target_name, other_name = name_b, name_a
                                diff_len = len_a - len_b
                                
                        diff_str = cm_to_m_cm_mm(diff_len)
                        
                        q = f"สายวัดด้านล่างแสดงตำแหน่งส่วนปลายของสิ่งของ 2 ชิ้น (เริ่มวัดจาก 0 เสมอ)<br>{svg_a}{svg_b}จงหาว่าสิ่งของใดมีความยาว<b>{compare_word}กัน</b> และ{compare_word}กันอยู่เท่าไร? <br>(ตอบในหน่วย เมตร เซนติเมตร มิลลิเมตร)"
                        
                        sol = f"""<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด (🔥 โหมดชาเลนจ์ ป.3):</b><br>
                        <b>ขั้นที่ 1: อ่านความยาวของแต่ละสิ่งของ</b><br>
                        👉 {name_a} จุดปลายอยู่ที่ {len_a} ซม. คิดเป็น <b>{str_a}</b><br>
                        👉 {name_b} จุดปลายอยู่ที่ {len_b} ซม. คิดเป็น <b>{str_b}</b><br>
                        <b>ขั้นที่ 2: เปรียบเทียบความยาว</b><br>
                        👉 จะเห็นได้ชัดเจนว่า <b>{target_name}</b> มีความยาว{compare_word}<br>
                        <b>ขั้นที่ 3: หาผลต่าง (ตั้งลบความยาว)</b><br>
                        👉 นำ {max(len_a, len_b):.1f} - {min(len_a, len_b):.1f} = <b>{diff_len:.1f} ซม.</b><br>
                        👉 แปลงผลลัพธ์เป็นหน่วยผสม: {diff_len:.1f} ซม. คิดเป็น <b>{diff_str}</b><br>
                        <b>ตอบ: {target_name} {compare_word}อยู่ {diff_str}</b></span>"""
                        
                    else:
                        len_a = round(random.uniform(110.0, 350.0), 1)
                        svg = draw_long_ruler_svg(len_a, "#f1c40f", "สิ่งของ (เริ่มวัดจาก 0)")
                        str_a = cm_to_m_cm_mm(len_a)
                        
                        q = f"จากรูป สายวัดแสดงตำแหน่งส่วนปลายของสิ่งของ (โดยเริ่มวัดจาก 0 เสมอ)<br>{svg}จงหาว่าสิ่งของนี้ยาวเท่าไร? <br>(ตอบในหน่วย เมตร เซนติเมตร มิลลิเมตร)"
                        
                        sol = f"""<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด (Step-by-step):</b><br>
                        <b>ขั้นที่ 1: อ่านค่าจากสายวัด</b><br>
                        👉 จุดปลายชี้ที่ <b>{len_a}</b> เซนติเมตร (หรือ {int(len_a)} ซม. กับอีก {int(round((len_a-int(len_a))*10))} มม.)<br>
                        <b>ขั้นที่ 2: แปลงหน่วยเป็น เมตร เซนติเมตร มิลลิเมตร</b><br>
                        👉 ความรู้: 100 เซนติเมตร = 1 เมตร<br>
                        👉 ดังนั้น {len_a} ซม. สามารถแบ่งเป็น เมตร และ เซนติเมตร ได้เป็น <b>{str_a}</b><br>
                        <b>ตอบ: {str_a}</b></span>"""
                else:
                    if is_challenge:
                        start_cm = random.randint(1, 4) + (random.randint(0, 9) * 0.1)
                    else:
                        start_cm = 0.0
                    
                    length_cm = random.randint(3, 8) + (random.randint(0, 9) * 0.1)
                    end_cm = start_cm + length_cm
                    
                    ans_cm = int(length_cm)
                    ans_mm = int(round((length_cm - ans_cm) * 10))
                    
                    q = draw_ruler_svg(start_cm, end_cm) + "<br>จากรูป สิ่งของมีความยาวกี่เซนติเมตร กี่มิลลิเมตร?"
                    
                    if start_cm == 0.0:
                        sol = f"""<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด (Step-by-step):</b><br>
                        <b>ขั้นที่ 1:</b> สังเกตว่าสิ่งของเริ่มวัดจากขีด 0 พอดี จึงสามารถอ่านค่าที่จุดปลายได้เลย<br>
                        <b>ขั้นที่ 2:</b> จุดปลายชี้ที่ <b>{int(end_cm)}</b> เซนติเมตร กับอีก <b>{int(round((end_cm - int(end_cm)) * 10))}</b> มิลลิเมตร (ขีดเล็ก)<br>
                        <b>ตอบ: {ans_cm} เซนติเมตร {ans_mm} มิลลิเมตร</b></span>"""
                    else:
                        sol = f"""<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด (🔥 โหมดชาเลนจ์):</b><br>
                        <b>ขั้นที่ 1:</b> สิ่งของไม่ได้เริ่มวัดจาก 0 จึงต้องนำ <b>จุดปลาย - จุดเริ่มต้น</b><br>
                        <b>ขั้นที่ 2:</b> จุดปลายชี้ที่ {end_cm:.1f} ซม. และจุดเริ่มต้นอยู่ที่ {start_cm:.1f} ซม.<br>
                        <b>ขั้นที่ 3:</b> คำนวณ {end_cm:.1f} - {start_cm:.1f} = <b>{length_cm:.1f} ซม.</b><br>
                        <b>ขั้นที่ 4:</b> แปลงความยาวที่ได้: {length_cm:.1f} ซม. คือ {ans_cm} เซนติเมตร กับ {ans_mm} มิลลิเมตร<br>
                        <b>ตอบ: {ans_cm} เซนติเมตร {ans_mm} มิลลิเมตร</b></span>"""

            elif actual_sub_t == "การอ่านแผนภูมิรูปภาพ":
                item_keys = list(FRUIT_EMOJIS.keys())
                item = random.choice(item_keys)
                emoji = FRUIT_EMOJIS[item]
                pic_val = random.choice([2, 5, 10]) * (5 if is_challenge else 1)
                
                q_type = random.choice(["single", "total", "diff"])
                pic_html, days, counts = draw_complex_pictogram_html(item, emoji, pic_val)
                
                if q_type == "single":
                    ask_idx = random.randint(0, 2)
                    ans = counts[ask_idx] * pic_val
                    q = pic_html + f"<br>จากแผนภูมิรูปภาพ ใน<b>วัน{days[ask_idx]}</b> ขาย{item}ได้กี่ผล?"
                    sol = f"""<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด (Step-by-step):</b><br>
                    <b>ขั้นที่ 1:</b> ดูในตารางวัน{days[ask_idx]} มีรูป {emoji} ทั้งหมด {counts[ask_idx]} รูป<br>
                    <b>ขั้นที่ 2:</b> กำหนดให้ 1 รูป = {pic_val} ผล<br>
                    <b>ขั้นที่ 3:</b> นำ {counts[ask_idx]} รูป × {pic_val} = <b>{ans} ผล</b><br>
                    <b>ตอบ: {ans} ผล</b></span>"""
                elif q_type == "total":
                    total_counts = sum(counts)
                    ans = total_counts * pic_val
                    q = pic_html + f"<br>จากแผนภูมิรูปภาพ รวมทั้ง 3 วัน ขาย{item}ได้ทั้งหมดกี่ผล?"
                    sol = f"""<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด (Step-by-step):</b><br>
                    <b>ขั้นที่ 1:</b> นับจำนวนรูป {emoji} ทั้ง 3 วันรวมกัน จะได้ {total_counts} รูป<br>
                    <b>ขั้นที่ 2:</b> กำหนดให้ 1 รูป = {pic_val} ผล<br>
                    <b>ขั้นที่ 3:</b> นำ {total_counts} รูป × {pic_val} = <b>{ans} ผล</b><br>
                    <b>ตอบ: {ans} ผล</b></span>"""
                else:
                    d1, d2 = random.sample([0, 1, 2], 2)
                    if counts[d1] < counts[d2]: d1, d2 = d2, d1 
                    diff_counts = counts[d1] - counts[d2]
                    ans = diff_counts * pic_val
                    
                    is_more = random.choice([True, False])
                    if is_more:
                        compare_word = "มากกว่า"
                        q = pic_html + f"<br>จากแผนภูมิรูปภาพ วัน{days[d1]} ขาย{item}ได้<b>{compare_word}</b>วัน{days[d2]} กี่ผล?"
                        sol = f"""<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด (Step-by-step):</b><br>
                        <b>ขั้นที่ 1:</b> วัน{days[d1]} มีรูป {emoji} {counts[d1]} รูป ส่วนวัน{days[d2]} มี {counts[d2]} รูป<br>
                        <b>ขั้นที่ 2:</b> หาผลต่างของจำนวนรูป: {counts[d1]} - {counts[d2]} = {diff_counts} รูป<br>
                        <b>ขั้นที่ 3:</b> นำผลต่างของรูป × {pic_val} ผล ➔ {diff_counts} × {pic_val} = <b>{ans} ผล</b><br>
                        <b>ตอบ: {ans} ผล</b></span>"""
                    else:
                        compare_word = "น้อยกว่า"
                        q = pic_html + f"<br>จากแผนภูมิรูปภาพ วัน{days[d2]} ขาย{item}ได้<b>{compare_word}</b>วัน{days[d1]} กี่ผล?"
                        sol = f"""<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด (Step-by-step):</b><br>
                        <b>ขั้นที่ 1:</b> วัน{days[d2]} มีรูป {emoji} {counts[d2]} รูป ส่วนวัน{days[d1]} มี {counts[d1]} รูป<br>
                        <b>ขั้นที่ 2:</b> หาผลต่างของจำนวนรูป: {counts[d1]} - {counts[d2]} = {diff_counts} รูป<br>
                        <b>ขั้นที่ 3:</b> นำผลต่างของรูป × {pic_val} ผล ➔ {diff_counts} × {pic_val} = <b>{ans} ผล</b><br>
                        <b>ตอบ: {ans} ผล</b></span>"""

            elif actual_sub_t == "การบวกและการลบทศนิยม":
                op = random.choice(["+", "-"])
                dp1 = random.choice([1, 2, 3])
                dp2 = random.choice([1, 2, 3])
                
                if op == "+":
                    a = round(random.uniform(1.0, 500.0), dp1)
                    b = round(random.uniform(1.0, 500.0), dp2)
                else:
                    a = round(random.uniform(50.0, 500.0), dp1)
                    b = round(random.uniform(1.0, a - 1.0), dp2)
                
                q_base = f"จงหาผลลัพธ์ของ <b>{a} {op} {b}</b>"
                table_html = generate_decimal_vertical_html(a, b, op, is_key=False)
                table_key = generate_decimal_vertical_html(a, b, op, is_key=True)
                
                q = f"{q_base}<br>{table_html}"
                sol = f"{q_base}<br>{table_key}"

            elif actual_sub_t == "การคูณและการหารทศนิยม":
                
                # ----------------------------------------------------
                # ฟังก์ชันวาดตารางตั้งหารยาวสำหรับทศนิยม (ย้ายลบไปขวา + อธิบายเศษ)
                # ----------------------------------------------------
                def get_decimal_long_div_html(divisor, dividend_str, max_dp=2):
                    div_chars = list(dividend_str)
                    ans_chars = []
                    steps = []
                    curr_val = 0
                    
                    i = 0
                    dp_count = 0
                    
                    while True:
                        if i < len(div_chars):
                            char = div_chars[i]
                        else:
                            if '.' not in div_chars:
                                div_chars.append('.')
                                ans_chars.append('.')
                                i += 1
                                continue
                            char = '0'
                            div_chars.append('0')
                            
                        if char == '.':
                            if '.' not in ans_chars:
                                ans_chars.append('.')
                            i += 1
                            continue
                            
                        curr_val = curr_val * 10 + int(char)
                        q = curr_val // divisor
                        ans_chars.append(str(q))
                        
                        mul = q * divisor
                        rem = curr_val - mul
                        
                        if q > 0 or i >= len(dividend_str) - 1:
                            steps.append({'col': i, 'curr': curr_val, 'mul': mul, 'rem': rem})
                            
                        curr_val = rem
                        
                        if '.' in ans_chars:
                            dp_count = len(ans_chars) - ans_chars.index('.') - 1
                            
                        i += 1
                        
                        # เงื่อนไขการหยุดหาร
                        if i >= len(dividend_str) and curr_val == 0:
                            break
                        if dp_count >= max_dp:
                            break
                            
                    # ลบเลข 0 ส่วนเกินด้านหน้าผลลัพธ์
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
                    
                    html = "<div style='margin: 15px 40px; font-family: \"Sarabun\", sans-serif; font-size: 24px;'>"
                    html += "<table style='border-collapse: collapse; text-align: center;'>"
                    
                    # แถวผลลัพธ์ (ด้านบนสุด)
                    html += "<tr><td style='border: none;'></td>"
                    for c in ans_chars:
                        html += f"<td style='padding: 2px 10px; color: #c0392b; font-weight: bold;'>{c}</td>"
                    html += "<td style='border: none;'></td></tr>" # คอลัมน์เผื่อเครื่องหมายลบ
                    
                    # แถวตัวหาร & ตัวตั้ง
                    html += f"<tr><td style='padding: 2px 15px; font-weight: bold; text-align: right;'>{divisor}</td>"
                    for j, c in enumerate(div_chars):
                        bt = "border-top: 2px solid #333;"
                        bl = "border-left: 2px solid #333;" if j == 0 else ""
                        html += f"<td style='{bt} {bl} padding: 2px 10px; font-weight: bold;'>{c}</td>"
                    html += "<td style='border: none;'></td></tr>"
                    
                    # แถวแสดงสเต็ปการลบดึงตัวเลข
                    for idx, step in enumerate(steps):
                        if step['mul'] == 0 and step['curr'] == 0 and idx != len(steps)-1: continue
                        
                        if idx > 0:
                            html += "<tr><td style='border: none;'></td>"
                            cv_str = str(step['curr'])
                            cols = []
                            c_ptr = step['col']
                            while len(cols) < len(cv_str):
                                if div_chars[c_ptr] != '.': cols.append(c_ptr)
                                c_ptr -= 1
                            cols.reverse()
                            for j in range(len(div_chars) + 1):
                                if j in cols: html += f"<td style='padding: 2px 10px;'>{cv_str[cols.index(j)]}</td>"
                                else: html += "<td style='border: none;'></td>"
                            html += "</tr>"
                            
                        html += "<tr><td style='border: none;'></td>"
                        mul_str = str(step['mul'])
                        cols = []
                        c_ptr = step['col']
                        while len(cols) < len(mul_str):
                            if div_chars[c_ptr] != '.': cols.append(c_ptr)
                            c_ptr -= 1
                        cols.reverse()
                        for j in range(len(div_chars) + 1):
                            if j in cols:
                                bb = "border-bottom: 2px solid #333;"
                                html += f"<td style='{bb} padding: 2px 10px;'>{mul_str[cols.index(j)]}</td>"
                            elif len(cols) > 0 and j == cols[-1] + 1:
                                # ย้ายเครื่องหมายลบมาอยู่ด้านขวาตรงนี้ครับ!
                                html += "<td style='padding: 2px 10px; font-weight: bold; color: #e74c3c;'>-</td>"
                            else: 
                                html += "<td style='border: none;'></td>"
                        html += "</tr>"
                        
                    if len(steps) > 0:
                        html += "<tr><td style='border: none;'></td>"
                        rem_str = str(steps[-1]['rem'])
                        cols = []
                        c_ptr = steps[-1]['col']
                        while len(cols) < len(rem_str):
                            if div_chars[c_ptr] != '.': cols.append(c_ptr)
                            c_ptr -= 1
                        cols.reverse()
                        for j in range(len(div_chars) + 1):
                            if j in cols:
                                bb = "border-bottom: 4px double #333;"
                                html += f"<td style='{bb} padding: 2px 10px;'>{rem_str[cols.index(j)]}</td>"
                            else: 
                                html += "<td style='border: none;'></td>"
                        html += "</tr>"
                        
                    html += "</table></div>"
                    
                    # เพิ่มกล่องอธิบายเหตุผลการค้างเศษ (วงสีเหลือง)
                    if steps and steps[-1]['rem'] != 0:
                        html += f"<div style='margin: 10px 40px; padding: 10px; background: #fdf2e9; border-left: 4px solid #e67e22; font-size: 16px;'>"
                        html += f"<b>💡 ทำไมถึงมีเศษค้างไว้ ไม่หารต่อให้หมด?</b><br>"
                        html += f"เนื่องจากการหารข้อนี้ไม่ลงตัว หรือโจทย์ต้องการผลลัพธ์ทศนิยม <b>{max_dp} ตำแหน่ง</b> "
                        html += f"เราจึงสามารถหยุดหารแค่นี้ได้เลยครับ (โดยเศษ <b>{steps[-1]['rem']}</b> ที่เหลืออยู่ คือเศษที่อยู่ในหลักทศนิยมถัดไปนั่นเอง)"
                        html += "</div>"
                    elif steps and steps[-1]['rem'] == 0:
                        html += f"<div style='margin: 10px 40px; padding: 10px; background: #eaeded; border-left: 4px solid #3498db; font-size: 16px;'>"
                        html += f"<b>💡 ข้อสังเกต:</b> เศษเป็น 0 แสดงว่าการหารนี้ <b>ลงตัวพอดี</b> ไม่เหลือเศษ"
                        html += "</div>"
                        
                    return html, final_quotient

                op = random.choice(["×", "÷"])
                
                if op == "×":
                    dp1 = random.choice([1, 2])
                    dp2 = random.choice([1, 2])
                    
                    if is_challenge:
                        a = round(random.uniform(10.0, 99.99), dp1)
                        b = round(random.uniform(5.0, 50.99), dp2)
                    else:
                        a = round(random.uniform(1.0, 15.9), dp1)
                        b = round(random.uniform(1.0, 9.9), dp2)
                        
                    ans = round(a * b, dp1 + dp2)
                    
                    a_str = f"{a:.{dp1}f}"
                    b_str = f"{b:.{dp2}f}"
                    ans_str = f"{ans:.{dp1+dp2}f}"
                    
                    a_int = int(a_str.replace(".", ""))
                    b_int = int(b_str.replace(".", ""))
                    
                    q = f"จงหาผลลัพธ์ของ <b>{a_str} × {b_str}</b>"
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (การคูณทศนิยม):</b><br>
                    <b>ขั้นที่ 1:</b> นับตำแหน่งทศนิยมของตัวตั้งและตัวคูณ<br>
                    👉 ตัวตั้ง ({a_str}) มีทศนิยม {dp1} ตำแหน่ง<br>
                    👉 ตัวคูณ ({b_str}) มีทศนิยม {dp2} ตำแหน่ง<br>
                    👉 ผลลัพธ์จะต้องมีทศนิยมรวม = {dp1} + {dp2} = <b>{dp1+dp2} ตำแหน่ง</b><br>
                    <b>ขั้นที่ 2:</b> นำตัวเลขมาคูณกันแบบจำนวนนับ (โดยเอาเครื่องหมายจุดออกก่อน)<br>
                    👉 {a_int:,} × {b_int:,} = <b>{a_int * b_int:,}</b><br>
                    <b>ขั้นที่ 3:</b> ใส่จุดทศนิยมกลับเข้าไปให้ครบ {dp1+dp2} ตำแหน่ง (โดยนับจากหลังสุดมาข้างหน้า)<br>
                    👉 จะได้ <b>{ans_str}</b><br>
                    <b>ตอบ: {ans_str}</b></span>"""
                    
                else: # การหาร
                    dp_ans = random.choice([1, 2])
                    dp_b = random.choice([1, 2])
                    
                    # สุ่มว่าข้อนี้จะเป็นหารลงตัว หรือ หารค้างเศษ
                    is_exact = random.choice([True, False])
                    
                    if is_exact:
                        if is_challenge:
                            ans_val = round(random.uniform(5.0, 50.0), dp_ans)
                            b = round(random.uniform(2.0, 15.0), dp_b)
                        else:
                            ans_val = round(random.uniform(1.0, 12.0), dp_ans)
                            b = round(random.choice([0.2, 0.4, 0.5, 1.2, 1.5, 2.5, 3.2]), dp_b)
                        a = round(ans_val * b, dp_ans + dp_b)
                    else:
                        if is_challenge:
                            a = round(random.uniform(20.0, 99.0), 1)
                            b = round(random.choice([0.3, 0.7, 0.9, 1.1, 1.3]), 1)
                        else:
                            a = round(random.uniform(5.0, 25.0), 1)
                            b = round(random.choice([0.3, 0.6, 1.5, 2.5]), 1)
                            
                    a_str = f"{a:g}"
                    b_str = f"{b:g}"
                    
                    b_parts = b_str.split('.')
                    b_dp = len(b_parts[1]) if len(b_parts) > 1 else 0
                    
                    mult_factor = 10 ** b_dp
                    a_shift = round(a * mult_factor, 4)
                    b_shift = int(round(b * mult_factor))
                    a_shift_str = f"{a_shift:g}" 
                    
                    max_dp = dp_ans if is_exact else random.choice([2, 3])
                    div_table_html, ans_str = get_decimal_long_div_html(b_shift, a_shift_str, max_dp)
                    
                    q = f"จงหาผลลัพธ์ของ <b>{a_str} ÷ {b_str}</b>"
                    
                    if b_dp > 0:
                        sol = f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (การหารทศนิยม):</b><br>
                        <b>ขั้นที่ 1:</b> สังเกตตัวหาร ({b_str}) ว่าเป็นทศนิยมกี่ตำแหน่ง<br>
                        👉 ตัวหารเป็นทศนิยม {b_dp} ตำแหน่ง เราต้องเลื่อนจุดเพื่อให้ตัวหารกลายเป็น <b>จำนวนเต็ม</b> เสมอ<br>
                        <b>ขั้นที่ 2:</b> นำ <b>{mult_factor:,}</b> มาคูณทั้งตัวตั้งและตัวหาร (เพื่อเลื่อนจุดทศนิยมไปทางขวา {b_dp} ตำแหน่ง)<br>
                        👉 ตัวตั้ง: {a_str} × {mult_factor:,} = <b>{a_shift_str}</b><br>
                        👉 ตัวหาร: {b_str} × {mult_factor:,} = <b>{b_shift:,}</b><br>
                        <b>ขั้นที่ 3:</b> นำมาตั้งหารยาวด้วยโจทย์ใหม่ที่ได้<br>
                        {div_table_html}
                        <b>ตอบ: ประมาณ {ans_str}</b></span>""" if not is_exact else f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (การหารทศนิยม):</b><br>
                        <b>ขั้นที่ 1:</b> สังเกตตัวหาร ({b_str}) ว่าเป็นทศนิยมกี่ตำแหน่ง<br>
                        👉 ตัวหารเป็นทศนิยม {b_dp} ตำแหน่ง เราต้องเลื่อนจุดเพื่อให้ตัวหารกลายเป็น <b>จำนวนเต็ม</b> เสมอ<br>
                        <b>ขั้นที่ 2:</b> นำ <b>{mult_factor:,}</b> มาคูณทั้งตัวตั้งและตัวหาร (เพื่อเลื่อนจุดทศนิยมไปทางขวา {b_dp} ตำแหน่ง)<br>
                        👉 ตัวตั้ง: {a_str} × {mult_factor:,} = <b>{a_shift_str}</b><br>
                        👉 ตัวหาร: {b_str} × {mult_factor:,} = <b>{b_shift:,}</b><br>
                        <b>ขั้นที่ 3:</b> นำมาตั้งหารยาวด้วยโจทย์ใหม่ที่ได้<br>
                        {div_table_html}
                        <b>ตอบ: {ans_str}</b></span>"""
                    else:
                        sol = f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (การหารทศนิยม):</b><br>
                        <b>ขั้นที่ 1:</b> สังเกตตัวหาร ({b_str}) พบว่าเป็นจำนวนเต็มแล้ว สามารถตั้งหารยาวได้เลย<br>
                        👉 โดยวางจุดทศนิยมของผลลัพธ์ (ด้านบน) ให้ตรงกับจุดทศนิยมของตัวตั้ง (ด้านล่าง)<br>
                        <b>ขั้นที่ 2:</b> ตั้งหารยาว<br>
                        {div_table_html}
                        <b>ตอบ: ประมาณ {ans_str}</b></span>""" if not is_exact else f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (การหารทศนิยม):</b><br>
                        <b>ขั้นที่ 1:</b> สังเกตตัวหาร ({b_str}) พบว่าเป็นจำนวนเต็มแล้ว สามารถตั้งหารยาวได้เลย<br>
                        👉 โดยวางจุดทศนิยมของผลลัพธ์ (ด้านบน) ให้ตรงกับจุดทศนิยมของตัวตั้ง (ด้านล่าง)<br>
                        <b>ขั้นที่ 2:</b> ตั้งหารยาว<br>
                        {div_table_html}
                        <b>ตอบ: {ans_str}</b></span>"""
            elif actual_sub_t == "โจทย์ปัญหาบัญญัติไตรยางศ์":
                
                # --- ฟังก์ชันวาดรูปสำหรับบัญญัติไตรยางศ์ ---
                def draw_unitary_step(emoji, qty, price_str, label_unit, is_target=False):
                    bg_color = "#fdf2e9" if is_target else "#f1f8ff"
                    border_color = "#e67e22" if is_target else "#3498db"
                    box_style = f"border: 2px dashed {border_color}; border-radius: 8px; padding: 10px; display: inline-block; text-align: center; margin: 5px; background-color: {bg_color}; min-width: 100px; vertical-align: top;"
                    emoji_str = "".join([f"<span style='font-size:24px;'>{emoji}</span>"] * min(qty, 4))
                    if qty > 4: emoji_str += f"<span style='font-size:18px; font-weight:bold; color:#7f8c8d;'>...({qty})</span>"
                    return f"""
                    <div style="{box_style}">
                        <div>{emoji_str}</div>
                        <div style="font-size: 16px; font-weight: bold; color: #2c3e50; margin-top: 5px;">{qty} {label_unit}</div>
                        <div style="font-size: 18px; font-weight: bold; color: #e74c3c;">{price_str}</div>
                    </div>
                    """
                    
                def draw_fuel_step(emoji, liters, dist_str, is_target=False):
                    bg_color = "#fdf2e9" if is_target else "#eafaf1"
                    border_color = "#e67e22" if is_target else "#2ecc71"
                    box_style = f"border: 2px dashed {border_color}; border-radius: 8px; padding: 10px; display: inline-block; text-align: center; margin: 5px; background-color: {bg_color}; min-width: 120px; vertical-align: top;"
                    return f"""
                    <div style="{box_style}">
                        <div style="font-size:24px;">{emoji} ⛽ <span style="font-size:18px; font-weight:bold;">{liters} ลิตร</span></div>
                        <div style="font-size: 16px; font-weight: bold; color: #2c3e50; margin-top: 5px;">วิ่งได้ระยะทาง</div>
                        <div style="font-size: 18px; font-weight: bold; color: #27ae60;">{dist_str}</div>
                    </div>
                    """

                def draw_time_step(emoji, time_val, time_unit, amount_str, is_target=False):
                    bg_color = "#fdf2e9" if is_target else "#f5eef8"
                    border_color = "#e67e22" if is_target else "#8e44ad"
                    box_style = f"border: 2px dashed {border_color}; border-radius: 8px; padding: 10px; display: inline-block; text-align: center; margin: 5px; background-color: {bg_color}; min-width: 120px; vertical-align: top;"
                    return f"""
                    <div style="{box_style}">
                        <div style="font-size:24px;">⏱️ {time_val} {time_unit}</div>
                        <div style="font-size: 16px; font-weight: bold; color: #2c3e50; margin-top: 5px;">ผลิต{emoji}ได้</div>
                        <div style="font-size: 18px; font-weight: bold; color: #8e44ad;">{amount_str}</div>
                    </div>
                    """
                    
                def draw_recipe_step(emoji, people, amount_str, is_target=False):
                    bg_color = "#fdf2e9" if is_target else "#fef9e7"
                    border_color = "#e67e22" if is_target else "#f1c40f"
                    box_style = f"border: 2px dashed {border_color}; border-radius: 8px; padding: 10px; display: inline-block; text-align: center; margin: 5px; background-color: {bg_color}; min-width: 120px; vertical-align: top;"
                    return f"""
                    <div style="{box_style}">
                        <div style="font-size:24px;">👥 {people} คน</div>
                        <div style="font-size: 16px; font-weight: bold; color: #2c3e50; margin-top: 5px;">ใช้ {emoji}</div>
                        <div style="font-size: 18px; font-weight: bold; color: #d35400;">{amount_str}</div>
                    </div>
                    """

                def draw_inverse_step(emoji1, val1, unit1, emoji2, val2, unit2, is_target=False):
                    bg_color = "#fdf2e9" if is_target else "#f4f6f7"
                    border_color = "#e67e22" if is_target else "#7f8c8d"
                    box_style = f"border: 2px dashed {border_color}; border-radius: 8px; padding: 10px; display: inline-block; text-align: center; margin: 5px; background-color: {bg_color}; min-width: 120px; vertical-align: top;"
                    return f"""
                    <div style="{box_style}">
                        <div style="font-size:20px; font-weight:bold; color:#2c3e50;">{emoji1} {val1} {unit1}</div>
                        <div style="font-size: 14px; font-weight: bold; color: #7f8c8d; margin: 5px 0;">{"ใช้เวลา" if "วัน" in unit2 or "ชั่วโมง" in unit2 else "อยู่ได้"}</div>
                        <div style="font-size: 18px; font-weight: bold; color: #d35400;">{emoji2} {val2} {unit2}</div>
                    </div>
                    """

                def draw_shadow_step(obj_name, h_val, s_val, is_target=False):
                    bg_color = "#fdf2e9" if is_target else "#eaf2f8"
                    border_color = "#e67e22" if is_target else "#2980b9"
                    box_style = f"border: 2px dashed {border_color}; border-radius: 8px; padding: 10px; display: inline-block; text-align: center; margin: 5px; background-color: {bg_color}; min-width: 120px; vertical-align: top;"
                    return f"""
                    <div style="{box_style}">
                        <div style="font-size:18px; font-weight:bold; color:#2c3e50;">{obj_name}</div>
                        <div style="font-size: 16px; font-weight: bold; color: #27ae60; margin-top: 5px;">สูง {h_val}</div>
                        <div style="font-size: 16px; font-weight: bold; color: #8e44ad;">เงายาว {s_val}</div>
                    </div>
                    """
                # ----------------------------------------
                
                name = random.choice(NAMES)
                
                if is_challenge:
                    scenario = random.choice(["buy_change", "recipe_convert", "inverse_work", "inverse_food", "shadow_height"])
                else:
                    scenario = random.choice(["buy", "distance", "work_time", "find_qty"])
                    
                if scenario == "buy_change":
                    item = random.choice(["ส้ม", "แอปเปิล", "มะม่วง", "ไข่ไก่", "โดนัท", "คัพเค้ก"])
                    unit = "ผล" if item in ["ส้ม", "แอปเปิล", "มะม่วง"] else ("ฟอง" if item == "ไข่ไก่" else "ชิ้น")
                    emoji = {"ส้ม":"🍊", "แอปเปิล":"🍎", "มะม่วง":"🥭", "ไข่ไก่":"🥚", "โดนัท":"🍩", "คัพเค้ก":"🧁"}[item]
                    
                    unit_price = random.randint(7, 25)
                    A = random.randint(4, 12) * 5 
                    B = A * unit_price 
                    
                    C_budget = (random.randint(15, 40) * 10 * unit_price) + random.randint(1, unit_price - 1)
                    max_items = C_budget // unit_price
                    rem_money = C_budget % unit_price
                    
                    q_graphic = f"<div style='text-align:center; margin:10px 0;'>{draw_unitary_step(emoji, A, f'{B:,} บาท', unit)} <span style='font-size:30px; vertical-align:middle; color:#bdc3c7; margin:0 10px;'>➔</span> <div style='display:inline-block; border: 2px solid #e67e22; border-radius:8px; padding:15px; background:#fdf2e9; vertical-align:top; min-width:120px;'><div style='font-size:24px;'>💰</div><div style='font-size:16px; font-weight:bold; color:#2c3e50;'>มีเงินทั้งหมด</div><div style='font-size:18px; font-weight:bold; color:#e74c3c;'>{C_budget:,} บาท</div></div></div>"
                    sol_graphic = f"<div style='text-align:center; margin:10px 0; background:#fff; padding:10px; border-radius:8px; border:1px solid #eee;'>{draw_unitary_step(emoji, A, f'{B:,} บาท', unit)} <div style='display:inline-block; vertical-align:middle; font-size:14px; color:#7f8c8d; font-weight:bold; margin:0 5px;'>หาร {A}<br>➔</div> {draw_unitary_step(emoji, 1, f'{unit_price:,} บาท', unit, True)}</div>"
                    
                    q = f"แม่ค้าติดป้ายขาย{item} <b>{A} {unit}</b> ในราคา <b>{B:,} บาท</b> <br>ถ้า{name}มีเงินในกระเป๋า <b>{C_budget:,} บาท</b> จะสามารถซื้อ{item}ได้อย่างมากที่สุดกี่{unit} และจะเหลือเงินทอนกี่บาท?<br>{q_graphic}"
                    
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (🔥 ชาเลนจ์ - หารมีเศษ):</b><br>
                    <b>ขั้นที่ 1: หาค่าของ 1 หน่วย</b><br>
                    {sol_graphic}
                    👉 นำเงินราคาเซ็ต ({B:,}) หารด้วยจำนวนของ ({A})<br>
                    👉 <b>{B:,} ÷ {A} = {unit_price:,} บาท/ชิ้น</b><br><br>
                    
                    <b>ขั้นที่ 2: คำนวณจำนวนชิ้นที่จะซื้อได้จากเงินที่มี</b><br>
                    👉 นำเงินทั้งหมดมาแบ่งจ่ายออกทีละ {unit_price:,} บาท<br>
                    👉 ตั้งหาร: <b>{C_budget:,} ÷ {unit_price:,}</b><br>
                    👉 ได้ผลหารคือ <b>{max_items:,}</b> และเหลือเศษ <b>{rem_money:,}</b><br><br>
                    
                    <b>ขั้นที่ 3: สรุปคำตอบ</b><br>
                    👉 ซื้อได้เต็มๆ {max_items:,} {unit} และเศษคือเงินทอนที่เหลือ<br>
                    <b>ตอบ: ซื้อได้ {max_items:,} {unit} เหลือเงินทอน {rem_money:,} บาท</b></span>"""
                    
                elif scenario == "recipe_convert":
                    item = random.choice(["เนื้อหมู", "เนื้อไก่", "กุ้งสด", "ปลาหมึก"])
                    emoji = {"เนื้อหมู":"🥩", "เนื้อไก่":"🍗", "กุ้งสด":"🦐", "ปลาหมึก":"🦑"}[item]
                    
                    people_A = random.randint(4, 10)
                    grams_per_person = random.randint(120, 350)
                    total_grams_A = people_A * grams_per_person
                    
                    people_C = random.randint(25, 80)
                    total_grams_C = people_C * grams_per_person
                    ans_kg = total_grams_C // 1000
                    ans_g = total_grams_C % 1000
                    ans_str = f"{ans_kg} กิโลกรัม {ans_g} กรัม" if ans_g > 0 else f"{ans_kg} กิโลกรัม"
                    
                    q_graphic = f"<div style='text-align:center; margin:10px 0;'>{draw_recipe_step(emoji, people_A, f'{total_grams_A:,} กรัม')} <span style='font-size:30px; vertical-align:middle; color:#bdc3c7; margin:0 10px;'>➔</span> {draw_recipe_step(emoji, people_C, '? กิโลกรัม', True)}</div>"
                    sol_graphic = f"<div style='text-align:center; margin:10px 0; background:#fff; padding:10px; border-radius:8px; border:1px solid #eee;'>{draw_recipe_step(emoji, people_A, f'{total_grams_A:,} กรัม')} <div style='display:inline-block; vertical-align:middle; font-size:14px; color:#7f8c8d; font-weight:bold; margin:0 5px;'>หาร {people_A}<br>➔</div> {draw_recipe_step(emoji, 1, f'{grams_per_person:,} กรัม')} <div style='display:inline-block; vertical-align:middle; font-size:14px; color:#7f8c8d; font-weight:bold; margin:0 5px;'>คูณ {people_C}<br>➔</div> {draw_recipe_step(emoji, people_C, f'{total_grams_C:,} กรัม', True)}</div>"
                    
                    q = f"การทำอาหารเลี้ยงคน <b>{people_A} คน</b> จะต้องเตรียม{item}น้ำหนักรวม <b>{total_grams_A:,} กรัม</b><br>ถ้า{name}ต้องการทำอาหารเลี้ยงคนจำนวน <b>{people_C} คน</b> จะต้องเตรียม{item}ทั้งหมด <b>กี่กิโลกรัม กี่กรัม</b>?<br>{q_graphic}"
                    
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (🔥 ชาเลนจ์ - บัญญัติไตรยางศ์ข้ามหน่วย):</b><br>
                    <b>ขั้นที่ 1: หาปริมาณที่ใช้ต่อคน 1 คน</b><br>
                    {sol_graphic}
                    👉 นำปริมาณเนื้อทั้งหมด ({total_grams_A:,} กรัม) หารด้วยจำนวนคน ({people_A})<br>
                    👉 <b>{total_grams_A:,} ÷ {people_A} = {grams_per_person:,} กรัม/คน</b><br><br>
                    
                    <b>ขั้นที่ 2: คำนวณปริมาณรวมสำหรับ {people_C} คน</b><br>
                    👉 นำปริมาณต่อคนไปคูณกับจำนวนคนที่ต้องการ<br>
                    👉 <b>{grams_per_person:,} × {people_C} = {total_grams_C:,} กรัม</b><br><br>
                    
                    <b>ขั้นที่ 3: แปลงหน่วยเป็นกิโลกรัมและกรัม</b><br>
                    👉 1 กิโลกรัม = 1,000 กรัม<br>
                    👉 นำ {total_grams_C:,} ÷ 1,000 จะได้ <b>{ans_kg} กิโลกรัม</b> เศษ <b>{ans_g} กรัม</b><br>
                    <b>ตอบ: {ans_str}</b></span>"""

                elif scenario == "inverse_work":
                    job = random.choice(["ทาสีบ้าน", "สร้างกำแพง", "เกี่ยวข้าว", "ขุดบ่อ", "ปูพื้นกระเบื้อง"])
                    A_workers = random.randint(4, 15)
                    B_days = random.randint(4, 20)
                    total_man_days = A_workers * B_days
                    
                    factors = [i for i in range(2, total_man_days + 1) if total_man_days % i == 0 and i != A_workers]
                    if not factors:
                        A_workers, B_days = 5, 12
                        total_man_days = 60
                        factors = [2, 3, 4, 6, 10, 15, 20, 30]
                    C_workers = random.choice(factors)
                    ans_days = total_man_days // C_workers
                    
                    q_graphic = f"<div style='text-align:center; margin:10px 0;'>{draw_inverse_step('👷‍♂️', A_workers, 'คน', '⏳', B_days, 'วัน')} <span style='font-size:30px; vertical-align:middle; color:#bdc3c7; margin:0 10px;'>➔</span> {draw_inverse_step('👷‍♂️', C_workers, 'คน', '⏳', '?', 'วัน', True)}</div>"
                    sol_graphic = f"<div style='text-align:center; margin:10px 0; background:#fff; padding:10px; border-radius:8px; border:1px solid #eee;'>{draw_inverse_step('👷‍♂️', A_workers, 'คน', '⏳', B_days, 'วัน')} <div style='display:inline-block; vertical-align:middle; font-size:14px; color:#c0392b; font-weight:bold; margin:0 5px;'>คูณ {A_workers}<br>(งานเท่าเดิม คนลดลง)<br>➔</div> {draw_inverse_step('👨‍🔧', 1, 'คน', '⏳', total_man_days, 'วัน')} <div style='display:inline-block; vertical-align:middle; font-size:14px; color:#27ae60; font-weight:bold; margin:0 5px;'>หาร {C_workers}<br>(ช่วยกันทำ)<br>➔</div> {draw_inverse_step('👷‍♂️', C_workers, 'คน', '⏳', ans_days, 'วัน', True)}</div>"
                    
                    q = f"ในการรับเหมา<b>{job}</b> ถ้าใช้คนงาน <b>{A_workers} คน</b> จะทำงานเสร็จในเวลา <b>{B_days} วัน</b> <br>ถ้าผู้รับเหมาต้องการเปลี่ยนแผน โดยใช้คนงาน <b>{C_workers} คน</b> งานนี้จะเสร็จในเวลากี่วัน?<br>{q_graphic}"
                    
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (🚨 บัญญัติไตรยางศ์ส่วนกลับ):</b><br>
                    <i>ข้อควรระวัง: ข้อนี้ไม่สามารถ "หารแล้วค่อยคูณ" ได้ เพราะยิ่งใช้คนช่วยทำงานเยอะ งานก็จะยิ่งเสร็จเร็วขึ้น (เวลาลดลง) ดังนั้นเราจะใช้การ "คูณก่อน แล้วค่อยหาร"</i><br>
                    {sol_graphic}
                    <b>ขั้นที่ 1: หาปริมาณงานทั้งหมด (ถ้าใช้คนแค่ 1 คนทำ)</b><br>
                    👉 คนงาน {A_workers} คน ทำงานเสร็จใน {B_days} วัน<br>
                    👉 ถ้าให้คนทำแค่ 1 คน จะต้องใช้เวลานานขึ้น จึงต้องนำไปคูณ: <b>{A_workers} × {B_days} = {total_man_days} วัน</b><br><br>
                    
                    <b>ขั้นที่ 2: คำนวณเวลาเมื่อใช้คนงาน {C_workers} คน</b><br>
                    👉 งานทั้งหมดต้องใช้เวลาทำ {total_man_days} วัน (สำหรับ 1 คน)<br>
                    👉 ถ้านำคนมาช่วยกัน {C_workers} คน เวลาจะลดลง จึงนำไปหาร: <b>{total_man_days} ÷ {C_workers} = {ans_days} วัน</b><br>
                    <b>ตอบ: {ans_days} วัน</b></span>"""

                elif scenario == "inverse_food":
                    animal = random.choice(["วัว", "ไก่", "หมู", "เป็ด", "แพะ"])
                    emoji = {"วัว":"🐄", "ไก่":"🐔", "หมู":"🐖", "เป็ด":"🦆", "แพะ":"🐐"}[animal]
                    A_animals = random.randint(10, 40)
                    B_days = random.randint(10, 30)
                    total_animal_days = A_animals * B_days
                    
                    action = random.choice(["buy", "sell"])
                    if action == "buy":
                        valid_C = [i for i in range(A_animals + 1, total_animal_days + 1) if total_animal_days % i == 0]
                        if not valid_C:
                            A_animals, B_days = 20, 15
                            total_animal_days = 300
                            valid_C = [25, 30, 50, 60]
                        C_animals = random.choice(valid_C)
                        diff = C_animals - A_animals
                        action_text = f"ชาวฟาร์ม<b>ซื้อ{animal}มาเพิ่มอีก {diff} ตัว</b>"
                    else:
                        valid_C = [i for i in range(2, A_animals) if total_animal_days % i == 0]
                        if not valid_C:
                            A_animals, B_days = 20, 15
                            total_animal_days = 300
                            valid_C = [10, 12, 15]
                        C_animals = random.choice(valid_C)
                        diff = A_animals - C_animals
                        action_text = f"ชาวฟาร์ม<b>ขาย{animal}ออกไป {diff} ตัว</b>"
                        
                    ans_days = total_animal_days // C_animals
                    
                    q_graphic = f"<div style='text-align:center; margin:10px 0;'>{draw_inverse_step(emoji, A_animals, 'ตัว', '🥣', B_days, 'วัน')} <span style='font-size:30px; vertical-align:middle; color:#bdc3c7; margin:0 10px;'>➔</span> {draw_inverse_step(emoji, C_animals, 'ตัว', '🥣', '?', 'วัน', True)}</div>"
                    sol_graphic = f"<div style='text-align:center; margin:10px 0; background:#fff; padding:10px; border-radius:8px; border:1px solid #eee;'>{draw_inverse_step(emoji, A_animals, 'ตัว', '🥣', B_days, 'วัน')} <div style='display:inline-block; vertical-align:middle; font-size:14px; color:#c0392b; font-weight:bold; margin:0 5px;'>คูณ {A_animals}<br>➔</div> {draw_inverse_step(emoji, 1, 'ตัว', '🥣', total_animal_days, 'วัน')} <div style='display:inline-block; vertical-align:middle; font-size:14px; color:#27ae60; font-weight:bold; margin:0 5px;'>หาร {C_animals}<br>➔</div> {draw_inverse_step(emoji, C_animals, 'ตัว', '🥣', ans_days, 'วัน', True)}</div>"
                    
                    q = f"ชาวฟาร์มแห่งหนึ่งมีอาหารสัตว์พอสำหรับเลี้ยง{animal} <b>{A_animals} ตัว</b> ได้นาน <b>{B_days} วัน</b> <br>ถ้าต่อมา {action_text} (ทำให้มี{animal}รวมเป็น <b>{C_animals} ตัว</b>) อาหารสัตว์ที่มีอยู่จะเลี้ยง{animal}ได้นานกี่วัน?<br>{q_graphic}"
                    
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (🚨 บัญญัติไตรยางศ์ส่วนกลับ):</b><br>
                    <i>ข้อควรระวัง: ยิ่งมีสัตว์เยอะขึ้น อาหารก็จะยิ่งหมดเร็วขึ้น (จำนวนวันลดลง) ดังนั้นต้อง "คูณก่อน แล้วค่อยหาร"</i><br>
                    {sol_graphic}
                    <b>ขั้นที่ 1: หาปริมาณอาหารทั้งหมด (สำหรับสัตว์ 1 ตัว)</b><br>
                    👉 {animal} {A_animals} ตัว กินอาหารหมดใน {B_days} วัน<br>
                    👉 ถ้ามี{animal}แค่ 1 ตัว อาหารจะอยู่ได้นานขึ้น: <b>{A_animals} × {B_days} = {total_animal_days} วัน</b><br><br>
                    
                    <b>ขั้นที่ 2: คำนวณจำนวนวันสำหรับสัตว์ {C_animals} ตัว</b><br>
                    👉 อาหารทั้งหมดกินได้ {total_animal_days} วัน (สำหรับ 1 ตัว)<br>
                    👉 นำมาแบ่งให้{animal} {C_animals} ตัว จำนวนวันจะลดลง: <b>{total_animal_days} ÷ {C_animals} = {ans_days} วัน</b><br>
                    <b>ตอบ: {ans_days} วัน</b></span>"""

                elif scenario == "shadow_height":
                    obj1 = random.choice(["ต้นไม้", "เสาธง", "ตึก", "เสาไฟฟ้า"])
                    mult = random.randint(2, 6)
                    s1 = random.randint(2, 6)
                    h1 = s1 * mult
                    
                    s2 = random.randint(8, 25)
                    while s2 == s1: s2 += 1
                    h2 = s2 * mult
                    
                    q_graphic = f"<div style='text-align:center; margin:10px 0;'>{draw_shadow_step('🧍 ไม้เมตร', f'{mult} เมตร', '1 เมตร')} <span style='font-size:30px; vertical-align:middle; color:#bdc3c7; margin:0 10px;'>➔</span> {draw_shadow_step(obj1, '? เมตร', f'{s2} เมตร', True)}</div>"
                    sol_graphic = f"<div style='text-align:center; margin:10px 0; background:#fff; padding:10px; border-radius:8px; border:1px solid #eee;'>{draw_shadow_step('ไม้เมตร', f'{mult} เมตร', '1 เมตร')} <div style='display:inline-block; vertical-align:middle; font-size:14px; color:#7f8c8d; font-weight:bold; margin:0 5px;'>คูณ {s2}<br>➔</div> {draw_shadow_step(obj1, f'{h2} เมตร', f'{s2} เมตร', True)}</div>"
                    
                    q = f"ในเวลาเดียวกันของวันหนึ่ง ถ้านำไม้เมตรความยาว <b>{mult} เมตร</b> มาตั้งตรง จะทอดเงายาว <b>1 เมตร</b> พอดี<br>ถ้า<b>{obj1}</b>ที่อยู่ใกล้เคียงกันทอดเงายาว <b>{s2} เมตร</b> {obj1}นี้จะมีความสูงกี่เมตร?<br>{q_graphic}"
                    
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (🔥 ชาเลนจ์ - สัดส่วนเงากับความสูง):</b><br>
                    {sol_graphic}
                    <b>ขั้นที่ 1: หาอัตราส่วนของความสูงต่อเงา 1 เมตร</b><br>
                    👉 โจทย์บอกว่าเงายาว 1 เมตร มาจากของที่สูง {mult} เมตร (นี่คือค่าของ 1 หน่วยแล้ว!)<br><br>
                    
                    <b>ขั้นที่ 2: คำนวณความสูงของ{obj1}</b><br>
                    👉 {obj1}ทอดเงายาว {s2} เมตร<br>
                    👉 นำความยาวเงาไปคูณกับความสูงต่อเงา 1 เมตร<br>
                    👉 คำนวณ: <b>{s2} × {mult} = {h2} เมตร</b><br>
                    <b>ตอบ: {h2} เมตร</b></span>"""

                elif scenario == "buy":
                    item = random.choice(["สมุด", "ปากกา", "ดินสอ", "ยางลบ", "ไม้บรรทัด", "แฟ้ม"])
                    unit = "เล่ม" if item in ["สมุด", "แฟ้ม"] else ("ด้าม" if item == "ปากกา" else "แท่ง" if item == "ดินสอ" else "อัน")
                    emoji = {"สมุด":"📓", "ปากกา":"🖊️", "ดินสอ":"✏️", "ยางลบ":"🧽", "ไม้บรรทัด":"📏", "แฟ้ม":"📁"}[item]
                    
                    A = random.randint(3, 12) 
                    unit_price = random.randint(5, 30) * random.choice([1, 2, 5])
                    B = A * unit_price 
                    C = random.randint(15, 50) 
                    while C == A: C = random.randint(15, 50)
                    ans = C * unit_price
                    
                    q_graphic = f"<div style='text-align:center; margin:10px 0;'>{draw_unitary_step(emoji, A, f'{B:,} บาท', unit)} <span style='font-size:30px; vertical-align:middle; color:#bdc3c7; margin:0 10px;'>➔</span> {draw_unitary_step(emoji, C, '? บาท', unit, True)}</div>"
                    sol_graphic = f"<div style='text-align:center; margin:10px 0; background:#fff; padding:10px; border-radius:8px; border:1px solid #eee;'>{draw_unitary_step(emoji, A, f'{B:,} บาท', unit)} <div style='display:inline-block; vertical-align:middle; font-size:14px; color:#7f8c8d; font-weight:bold; margin:0 5px;'>หาร {A}<br>➔</div> {draw_unitary_step(emoji, 1, f'{unit_price:,} บาท', unit)} <div style='display:inline-block; vertical-align:middle; font-size:14px; color:#7f8c8d; font-weight:bold; margin:0 5px;'>คูณ {C}<br>➔</div> {draw_unitary_step(emoji, C, f'{ans:,} บาท', unit, True)}</div>"
                    
                    q = f"ร้านค้าสหกรณ์ขาย{item} <b>{A} {unit}</b> ในราคา <b>{B:,} บาท</b> <br>ถ้าคุณครูต้องการสั่งซื้อ{item}แบบเดียวกันจำนวน <b>{C} {unit}</b> จะต้องจ่ายเงินทั้งหมดกี่บาท?<br>{q_graphic}"
                    
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (บัญญัติไตรยางศ์ แบบหาค่า 1 หน่วย):</b><br>
                    หลักการของบัญญัติไตรยางศ์คือ "หารให้เป็น 1 ก่อน แล้วค่อยนำไปคูณจำนวนที่ต้องการ"<br>
                    {sol_graphic}
                    <b>ขั้นที่ 1: หาค่าของ 1 หน่วย (หัวใจสำคัญ)</b><br>
                    👉 เราต้องรู้ให้ได้ก่อนว่า {item} <b>แค่ 1 {unit}</b> ราคาเท่าไร?<br>
                    👉 คำนวณ: <b>{B:,} ÷ {A} = {unit_price:,} บาท</b><br><br>
                    
                    <b>ขั้นที่ 2: คำนวณหาสิ่งที่โจทย์ถาม</b><br>
                    👉 นำราคาต่อ 1 {unit} (คือ <b>{unit_price:,}</b>) มาคูณกับจำนวนที่ต้องการซื้อ ({C})<br>
                    👉 คำนวณ: <b>{unit_price:,} × {C} = {ans:,} บาท</b><br>
                    <b>ตอบ: {ans:,} บาท</b></span>"""
                    
                elif scenario == "distance":
                    vehicle = random.choice(["รถยนต์", "รถตู้", "รถกระบะ"])
                    emoji = {"รถยนต์":"🚗", "รถตู้":"🚐", "รถกระบะ":"🛻"}[vehicle]
                    A = random.randint(5, 15) 
                    dist_per_liter = random.randint(12, 22)
                    B = A * dist_per_liter 
                    C = random.randint(20, 60)
                    while C == A: C = random.randint(20, 60)
                    ans = C * dist_per_liter
                    
                    q_graphic = f"<div style='text-align:center; margin:10px 0;'>{draw_fuel_step(emoji, A, f'{B:,} กม.')} <span style='font-size:30px; vertical-align:middle; color:#bdc3c7; margin:0 10px;'>➔</span> {draw_fuel_step(emoji, C, '? กม.', True)}</div>"
                    sol_graphic = f"<div style='text-align:center; margin:10px 0; background:#fff; padding:10px; border-radius:8px; border:1px solid #eee;'>{draw_fuel_step(emoji, A, f'{B:,} กม.')} <div style='display:inline-block; vertical-align:middle; font-size:14px; color:#7f8c8d; font-weight:bold; margin:0 5px;'>หาร {A}<br>➔</div> {draw_fuel_step(emoji, 1, f'{dist_per_liter:,} กม.')} <div style='display:inline-block; vertical-align:middle; font-size:14px; color:#7f8c8d; font-weight:bold; margin:0 5px;'>คูณ {C}<br>➔</div> {draw_fuel_step(emoji, C, f'{ans:,} กม.', True)}</div>"
                    
                    q = f"<b>{vehicle}</b>คันหนึ่งใช้น้ำมัน <b>{A} ลิตร</b> สามารถแล่นได้ระยะทาง <b>{B:,} กิโลเมตร</b> <br>ถ้าในถังมีน้ำมัน <b>{C} ลิตร</b> {vehicle}คันนี้จะแล่นได้ระยะทางทั้งหมดกี่กิโลเมตร?<br>{q_graphic}"
                    
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (บัญญัติไตรยางศ์ อัตราส่วนระยะทาง):</b><br>
                    {sol_graphic}
                    <b>ขั้นที่ 1: หาค่าของ 1 หน่วย (น้ำมัน 1 ลิตร วิ่งได้ไกลแค่ไหน?)</b><br>
                    👉 นำระยะทางทั้งหมด ({B:,}) มาหารแบ่งด้วยจำนวนลิตรน้ำมัน ({A})<br>
                    👉 คำนวณ: <b>{B:,} ÷ {A} = {dist_per_liter:,} กม./ลิตร</b><br><br>
                    
                    <b>ขั้นที่ 2: คำนวณระยะทางจากน้ำมันที่โจทย์กำหนด</b><br>
                    👉 นำระยะทางต่อ 1 ลิตร (<b>{dist_per_liter:,}</b>) มาคูณกับน้ำมันที่มี (<b>{C}</b>)<br>
                    👉 คำนวณ: <b>{dist_per_liter:,} × {C} = {ans:,} กม.</b><br>
                    <b>ตอบ: {ans:,} กิโลเมตร</b></span>"""

                elif scenario == "work_time":
                    item = random.choice(["ขวดน้ำ", "ตุ๊กตา", "ลูกอม", "กระป๋อง"])
                    unit = "ขวด" if item == "ขวดน้ำ" else ("ตัว" if item == "ตุ๊กตา" else "เม็ด" if item == "ลูกอม" else "ใบ")
                    emoji = {"ขวดน้ำ":"🍾", "ตุ๊กตา":"🧸", "ลูกอม":"🍬", "กระป๋อง":"🥫"}[item]
                    
                    time_A = random.randint(2, 10)
                    rate = random.randint(15, 60) 
                    amount_A = time_A * rate
                    
                    time_C = random.randint(15, 45)
                    while time_C == time_A: time_C = random.randint(15, 45)
                    ans = time_C * rate
                    
                    q_graphic = f"<div style='text-align:center; margin:10px 0;'>{draw_time_step(emoji, time_A, 'นาที', f'{amount_A:,} {unit}')} <span style='font-size:30px; vertical-align:middle; color:#bdc3c7; margin:0 10px;'>➔</span> {draw_time_step(emoji, time_C, 'นาที', f'? {unit}', True)}</div>"
                    sol_graphic = f"<div style='text-align:center; margin:10px 0; background:#fff; padding:10px; border-radius:8px; border:1px solid #eee;'>{draw_time_step(emoji, time_A, 'นาที', f'{amount_A:,} {unit}')} <div style='display:inline-block; vertical-align:middle; font-size:14px; color:#7f8c8d; font-weight:bold; margin:0 5px;'>หาร {time_A}<br>➔</div> {draw_time_step(emoji, 1, 'นาที', f'{rate:,} {unit}')} <div style='display:inline-block; vertical-align:middle; font-size:14px; color:#7f8c8d; font-weight:bold; margin:0 5px;'>คูณ {time_C}<br>➔</div> {draw_time_step(emoji, time_C, 'นาที', f'{ans:,} {unit}', True)}</div>"
                    
                    q = f"เครื่องจักรในโรงงานใช้เวลา <b>{time_A} นาที</b> สามารถผลิต{item}ได้ <b>{amount_A:,} {unit}</b><br>ถ้าเปิดเครื่องจักรทำงานต่อเนื่องเป็นเวลา <b>{time_C} นาที</b> จะสามารถผลิต{item}ได้ทั้งหมดกี่{unit}?<br>{q_graphic}"
                    
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (บัญญัติไตรยางศ์ งานและเวลา):</b><br>
                    {sol_graphic}
                    <b>ขั้นที่ 1: หาว่า 1 นาที ผลิตได้กี่ชิ้น</b><br>
                    👉 นำจำนวน{item}ทั้งหมด ({amount_A:,}) หารด้วยเวลาที่ใช้ ({time_A} นาที)<br>
                    👉 คำนวณ: <b>{amount_A:,} ÷ {time_A} = {rate:,} {unit}/นาที</b><br><br>
                    
                    <b>ขั้นที่ 2: คำนวณผลผลิตตามเวลาที่ต้องการ</b><br>
                    👉 นำกำลังการผลิตต่อนาที (<b>{rate:,}</b>) มาคูณกับเวลาใหม่ (<b>{time_C}</b>)<br>
                    👉 คำนวณ: <b>{rate:,} × {time_C} = {ans:,} {unit}</b><br>
                    <b>ตอบ: {ans:,} {unit}</b></span>"""

                elif scenario == "find_qty":
                    item = random.choice(["สมุด", "ปากกา", "แฟ้ม", "กรรไกร"])
                    unit = "เล่ม" if item in ["สมุด", "แฟ้ม"] else ("ด้าม" if item == "ปากกา" else "อัน")
                    emoji = {"สมุด":"📓", "ปากกา":"🖊️", "แฟ้ม":"📁", "กรรไกร":"✂️"}[item]
                    
                    A = random.randint(3, 10) 
                    unit_price = random.randint(12, 45)
                    B = A * unit_price 
                    
                    ans_qty = random.randint(15, 60)
                    while ans_qty == A: ans_qty = random.randint(15, 60)
                    C_budget = ans_qty * unit_price
                    
                    q_graphic = f"<div style='text-align:center; margin:10px 0;'>{draw_unitary_step(emoji, A, f'{B:,} บาท', unit)} <span style='font-size:30px; vertical-align:middle; color:#bdc3c7; margin:0 10px;'>➔</span> <div style='display:inline-block; border: 2px dashed #e67e22; border-radius:8px; padding:10px; background:#fdf2e9; min-width:120px; vertical-align:top;'><div style='font-size:24px;'>❓ {unit}</div><div style='font-size:16px; font-weight:bold; color:#2c3e50; margin-top:5px;'>จ่ายเงินไป</div><div style='font-size:18px; font-weight:bold; color:#e74c3c;'>{C_budget:,} บาท</div></div></div>"
                    sol_graphic = f"<div style='text-align:center; margin:10px 0; background:#fff; padding:10px; border-radius:8px; border:1px solid #eee;'>{draw_unitary_step(emoji, A, f'{B:,} บาท', unit)} <div style='display:inline-block; vertical-align:middle; font-size:14px; color:#7f8c8d; font-weight:bold; margin:0 5px;'>หาร {A}<br>➔</div> {draw_unitary_step(emoji, 1, f'{unit_price:,} บาท', unit)} <div style='display:inline-block; vertical-align:middle; font-size:14px; color:#7f8c8d; font-weight:bold; margin:0 5px;'>เงิน {C_budget:,} บ.<br>หาร {unit_price:,}<br>➔</div> <div style='display:inline-block; border: 2px dashed #e67e22; border-radius:8px; padding:10px; background:#fdf2e9; min-width:120px; vertical-align:top;'><div style='font-size:24px;'>✔️ {ans_qty:,} {unit}</div><div style='font-size:16px; font-weight:bold; color:#2c3e50; margin-top:5px;'>จ่ายเงินไป</div><div style='font-size:18px; font-weight:bold; color:#e74c3c;'>{C_budget:,} บาท</div></div></div>"
                    
                    q = f"ร้านค้าขาย{item} <b>{A} {unit}</b> ในราคา <b>{B:,} บาท</b> <br>ถ้า{name}จ่ายเงินซื้อ{item}ไปทั้งหมด <b>{C_budget:,} บาท</b> เขาจะได้{item}กี่{unit}?<br>{q_graphic}"
                    
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (บัญญัติไตรยางศ์ แบบย้อนหาจำนวน):</b><br>
                    {sol_graphic}
                    <b>ขั้นที่ 1: หาว่า 1 {unit} ราคาเท่าไร</b><br>
                    👉 นำราคาตั้ง ({B:,}) หารด้วยจำนวนชิ้น ({A})<br>
                    👉 คำนวณ: <b>{B:,} ÷ {A} = {unit_price:,} บาท/{unit}</b><br><br>
                    
                    <b>ขั้นที่ 2: นำเงินที่มีไปหารราคาต่อชิ้น</b><br>
                    👉 {name}จ่ายเงินไป {C_budget:,} บาท และของราคาชิ้นละ {unit_price:,} บาท<br>
                    👉 คำนวณ: <b>{C_budget:,} ÷ {unit_price:,} = {ans_qty:,} {unit}</b><br>
                    <b>ตอบ: {ans_qty:,} {unit}</b></span>"""

            elif actual_sub_t == "การหาค่าเฉลี่ย (Average)":
                
                def draw_avg_box(icon, count, label_count, avg_val, label_avg, bg_color="#f1f8ff", border_color="#3498db"):
                    box_style = f"border: 2px dashed {border_color}; border-radius: 8px; padding: 10px 15px; display: inline-block; text-align: center; margin: 5px; background-color: {bg_color}; vertical-align: top; min-width: 120px;"
                    return f"""
                    <div style="{box_style}">
                        <div style="font-size:24px;">{icon} {count} {label_count}</div>
                        <div style="font-size: 14px; font-weight: bold; color: #7f8c8d; margin-top: 5px;">ค่าเฉลี่ย</div>
                        <div style="font-size: 20px; font-weight: bold; color: #e74c3c;">{avg_val} {label_avg}</div>
                    </div>
                    """
                
                name = random.choice(NAMES)

                if is_challenge:
                    scenario = random.choice(["group_change", "combine_groups", "target_score", "wrong_data"])
                else:
                    scenario = random.choice(["basic", "missing", "total_from_avg"])
                
                if scenario == "basic":
                    # หาค่าเฉลี่ยพื้นฐาน
                    items = random.randint(4, 6)
                    target_avg = random.randint(20, 80)
                    total = target_avg * items
                    
                    nums = []
                    current_sum = 0
                    for i in range(items - 1):
                        n = random.randint(target_avg - 10, target_avg + 10)
                        nums.append(n)
                        current_sum += n
                    
                    nums.append(total - current_sum)
                    random.shuffle(nums)
                    
                    nums_str = ", ".join(map(str, nums))
                    
                    q = f"จากการสำรวจข้อมูลน้ำหนักของนักเรียน <b>{items} คน</b> พบว่ามีน้ำหนักดังนี้: <br><span style='font-size:22px; font-weight:bold; color:#2980b9;'>{nums_str} กิโลกรัม</span><br>จงหาน้ำหนัก <b>'เฉลี่ย'</b> ของนักเรียนกลุ่มนี้?"
                    
                    sum_str = " + ".join(map(str, nums))
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (การหาค่าเฉลี่ย):</b><br>
                    <b>สูตร:</b> ค่าเฉลี่ย = ผลรวมของข้อมูลทั้งหมด ÷ จำนวนข้อมูล<br><br>
                    <b>ขั้นที่ 1: หาผลรวมของข้อมูลทั้งหมด</b><br>
                    👉 นำน้ำหนักของทุกคนมาบวกกัน<br>
                    👉 {sum_str} = <b>{total} กิโลกรัม</b><br><br>
                    <b>ขั้นที่ 2: นำผลรวมไปหารด้วยจำนวนคน</b><br>
                    👉 มีนักเรียนทั้งหมด {items} คน<br>
                    👉 {total} ÷ {items} = <b>{target_avg} กิโลกรัม</b><br>
                    <b>ตอบ: {target_avg} กิโลกรัม</b></span>"""
                    
                elif scenario == "missing":
                    # ทราบค่าเฉลี่ย หาตัวที่หายไป
                    items = random.randint(3, 5)
                    target_avg = random.randint(40, 90)
                    total = target_avg * items
                    
                    nums = []
                    current_sum = 0
                    for i in range(items - 1):
                        n = random.randint(target_avg - 15, target_avg + 15)
                        nums.append(n)
                        current_sum += n
                        
                    missing_val = total - current_sum
                    nums_str = ", ".join(map(str, nums))
                    
                    q = f"นักเรียน <b>{items} คน</b> มีคะแนนสอบ <b>'เฉลี่ย'</b> อยู่ที่ <b>{target_avg} คะแนน</b><br>ถ้ารู้คะแนนของเพื่อน {items-1} คน คือ <b>{nums_str} คะแนน</b><br>จงหาว่านักเรียนคนที่เหลือสอบได้กี่คะแนน?"
                    
                    sum_str = " + ".join(map(str, nums))
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (หาค่าข้อมูลที่หายไปจากค่าเฉลี่ย):</b><br>
                    <b>ขั้นที่ 1: หาผลรวมคะแนนที่ควรจะเป็นทั้งหมด</b><br>
                    👉 ถ้านักเรียน {items} คน มีคะแนนเฉลี่ยคนละ {target_avg} คะแนน<br>
                    👉 แสดงว่าคะแนนรวมทั้งหมด = {items} × {target_avg} = <b>{total} คะแนน</b><br><br>
                    <b>ขั้นที่ 2: หาผลรวมคะแนนของคนที่มีอยู่แล้ว</b><br>
                    👉 {sum_str} = <b>{current_sum} คะแนน</b><br><br>
                    <b>ขั้นที่ 3: หาคะแนนของคนที่หายไป</b><br>
                    👉 นำคะแนนรวมทั้งหมด ลบด้วย คะแนนรวมของคนที่มีอยู่<br>
                    👉 {total} - {current_sum} = <b>{missing_val} คะแนน</b><br>
                    <b>ตอบ: {missing_val} คะแนน</b></span>"""

                elif scenario == "total_from_avg":
                    items = random.randint(5, 12)
                    avg = random.randint(25, 85)
                    total = items * avg
                    
                    obj = random.choice(["กระสอบข้าวสาร", "ลังผลไม้", "กล่องหนังสือ"])
                    unit = "กระสอบ" if obj == "กระสอบข้าวสาร" else ("ลัง" if obj == "ลังผลไม้" else "กล่อง")
                    
                    q = f"ชั่งน้ำหนัก{obj}จำนวน <b>{items} {unit}</b> พบว่ามีน้ำหนัก <b>'เฉลี่ย'</b> {unit}ละ <b>{avg} กิโลกรัม</b><br>จงหาน้ำหนักรวมทั้งหมดของ{obj}กองนี้?"
                    
                    svg = f"<div style='text-align:center;'>{draw_avg_box('📦', items, unit, avg, 'กก.')}</div>"
                    
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (หาผลรวมจากค่าเฉลี่ย):</b><br>
                    {svg}
                    <b>สูตร:</b> ผลรวม = จำนวนข้อมูล × ค่าเฉลี่ย<br><br>
                    <b>ขั้นที่ 1: นำจำนวน{unit}มาคูณกับน้ำหนักเฉลี่ย</b><br>
                    👉 มี{obj}ทั้งหมด {items} {unit}<br>
                    👉 แต่ละ{unit}หนักเฉลี่ย {avg} กิโลกรัม<br>
                    👉 {items} × {avg} = <b>{total} กิโลกรัม</b><br><br>
                    <b>ตอบ: {total} กิโลกรัม</b></span>"""

                elif scenario == "group_change":
                    count1 = random.randint(4, 9)
                    avg1 = random.randint(30, 60)
                    sum1 = count1 * avg1
                    
                    is_join = random.choice([True, False])
                    if is_join:
                        count2 = count1 + 1
                        avg2 = avg1 + random.randint(1, 4)
                        sum2 = count2 * avg2
                        diff = sum2 - sum1
                        action_txt = f"มีเพื่อนเดินมา <b>ขอเข้ากลุ่มเพิ่ม 1 คน</b>"
                        q_ask = "เพื่อนคนที่เดินเข้ามาใหม่ มีน้ำหนักกี่กิโลกรัม?"
                        svg = f"<div style='text-align:center;'>{draw_avg_box('👥', count1, 'คน', avg1, 'กก.')} <span style='font-size:24px; vertical-align:middle; margin:0 10px;'>➕ 🧍‍♂️ ➔</span> {draw_avg_box('👥', count2, 'คน', avg2, 'กก.', '#fef9e7', '#f1c40f')}</div>"
                    else:
                        count2 = count1 - 1
                        avg2 = avg1 - random.randint(1, 4)
                        sum2 = count2 * avg2
                        diff = sum1 - sum2
                        action_txt = f"มีเพื่อน <b>เดินออกจากกลุ่มไป 1 คน</b>"
                        q_ask = "เพื่อนคนที่เดินออกไป มีน้ำหนักกี่กิโลกรัม?"
                        svg = f"<div style='text-align:center;'>{draw_avg_box('👥', count1, 'คน', avg1, 'กก.')} <span style='font-size:24px; vertical-align:middle; margin:0 10px;'>➖ 🧍‍♂️ ➔</span> {draw_avg_box('👥', count2, 'คน', avg2, 'กก.', '#fef9e7', '#f1c40f')}</div>"
                        
                    q = f"กลุ่มของนักเรียน <b>{count1} คน</b> มีน้ำหนัก <b>'เฉลี่ย'</b> อยู่ที่ <b>{avg1} กิโลกรัม</b><br>ต่อมา {action_txt} ทำให้น้ำหนักเฉลี่ยของกลุ่มเปลี่ยนเป็น <b>{avg2} กิโลกรัม</b><br>{q_ask}<br>{svg}"
                    
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (🔥 ชาเลนจ์ - ค่าเฉลี่ยเปลี่ยนกลุ่ม):</b><br>
                    <i>หลักการสำคัญ: เมื่อเจอโจทย์ค่าเฉลี่ย ให้แปลงเป็น <b>"ผลรวม"</b> ก่อนเสมอ!</i><br><br>
                    <b>ขั้นที่ 1: หาผลรวมน้ำหนักของกลุ่มเดิม ({count1} คน)</b><br>
                    👉 ผลรวมเดิม = จำนวนคน × ค่าเฉลี่ย<br>
                    👉 {count1} × {avg1} = <b>{sum1} กิโลกรัม</b><br><br>
                    <b>ขั้นที่ 2: หาผลรวมน้ำหนักของกลุ่มใหม่ ({count2} คน)</b><br>
                    👉 ผลรวมใหม่ = จำนวนคนใหม่ × ค่าเฉลี่ยใหม่<br>
                    👉 {count2} × {avg2} = <b>{sum2} กิโลกรัม</b><br><br>
                    <b>ขั้นที่ 3: หาน้ำหนักของคนที่ทำให้ค่าเฉลี่ยเปลี่ยนไป</b><br>
                    👉 นำผลรวมที่มากกว่า ลบด้วย ผลรวมที่น้อยกว่า<br>
                    👉 | {sum1} - {sum2} | = <b>{diff} กิโลกรัม</b><br>
                    <b>ตอบ: {diff} กิโลกรัม</b></span>"""
                    
                elif scenario == "combine_groups":
                    nA = random.choice([10, 20, 25, 30])
                    avgA = random.randint(50, 80)
                    
                    nB = random.choice([10, 20, 25, 30])
                    while nB == nA: nB = random.choice([10, 20, 25, 30])
                    
                    avgB = avgA + random.choice([4, 5, 8, 10])
                    
                    sumA = nA * avgA
                    sumB = nB * avgB
                    total_sum = sumA + sumB
                    total_n = nA + nB
                    final_avg_str = f"{(total_sum / total_n):g}"
                    
                    svg = f"<div style='text-align:center;'>{draw_avg_box('👦', nA, 'คน (ห้อง A)', avgA, 'คะแนน', '#eaf2f8', '#2980b9')} <span style='font-size:30px; vertical-align:middle; margin:0 10px;'>➕</span> {draw_avg_box('👧', nB, 'คน (ห้อง B)', avgB, 'คะแนน', '#fdedec', '#c0392b')}</div>"
                    
                    q = f"ในการสอบวิชาคณิตศาสตร์<br>นักเรียนห้อง A จำนวน <b>{nA} คน</b> สอบได้คะแนนเฉลี่ย <b>{avgA} คะแนน</b><br>นักเรียนห้อง B จำนวน <b>{nB} คน</b> สอบได้คะแนนเฉลี่ย <b>{avgB} คะแนน</b><br>ถ้านำคะแนนของนักเรียนทั้งสองห้องมารวมกัน จะได้คะแนน <b>'เฉลี่ยรวม'</b> กี่คะแนน?<br>{svg}"
                    
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (🔥 ชาเลนจ์ - ค่าเฉลี่ยรวม):</b><br>
                    <i>ข้อควรระวัง: เราไม่สามารถนำค่าเฉลี่ยมาบวกกันแล้วหารสองได้โดยตรง (เพราะจำนวนคนไม่เท่ากัน) ต้องหาผลรวมคะแนนของแต่ละห้องก่อน!</i><br><br>
                    <b>ขั้นที่ 1: หาผลรวมคะแนนของแต่ละห้อง</b><br>
                    👉 ผลรวมห้อง A = {nA} คน × {avgA} คะแนน = <b>{sumA:,} คะแนน</b><br>
                    👉 ผลรวมห้อง B = {nB} คน × {avgB} คะแนน = <b>{sumB:,} คะแนน</b><br><br>
                    <b>ขั้นที่ 2: หาผลรวมคะแนนทั้งหมด และ จำนวนคนทั้งหมด</b><br>
                    👉 คะแนนรวมสองห้อง = {sumA:,} + {sumB:,} = <b>{total_sum:,} คะแนน</b><br>
                    👉 จำนวนคนรวมสองห้อง = {nA} + {nB} = <b>{total_n} คน</b><br><br>
                    <b>ขั้นที่ 3: คำนวณค่าเฉลี่ยรวม</b><br>
                    👉 นำคะแนนรวมทั้งหมด หารด้วย จำนวนคนทั้งหมด<br>
                    👉 {total_sum:,} ÷ {total_n} = <b>{final_avg_str} คะแนน</b><br>
                    <b>ตอบ: {final_avg_str} คะแนน</b></span>"""

                elif scenario == "target_score":
                    n_exams = random.randint(3, 5)
                    current_avg = random.randint(65, 85)
                    target_avg = current_avg + random.randint(1, 3)
                    
                    sum1 = n_exams * current_avg
                    sum2 = (n_exams + 1) * target_avg
                    needed_score = sum2 - sum1
                    
                    svg = f"<div style='text-align:center;'>{draw_avg_box('📝', n_exams, 'ครั้งแรก', current_avg, 'คะแนน')} <span style='font-size:20px; vertical-align:middle; margin:0 10px; color:#27ae60;'><b>เป้าหมายใหม่ ➔</b></span> {draw_avg_box('🏆', n_exams + 1, 'ครั้ง', target_avg, 'คะแนน', '#fef9e7', '#f1c40f')}</div>"
                    
                    q = f"<b>{name}</b>สอบวิชาคณิตศาสตร์ไปแล้ว <b>{n_exams} ครั้ง</b> ได้คะแนน <b>'เฉลี่ย'</b> อยู่ที่ <b>{current_avg} คะแนน</b><br>ถ้าต้องการให้คะแนนเฉลี่ยรวมเพิ่มขึ้นเป็น <b>{target_avg} คะแนน</b> ในการสอบครั้งที่ {n_exams + 1} {name}จะต้องทำคะแนนให้ได้อย่างน้อยกี่คะแนน?<br>{svg}"
                    
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (🔥 ชาเลนจ์ - หาคะแนนตามเป้าหมาย):</b><br>
                    <b>ขั้นที่ 1: หาผลรวมคะแนนเดิมที่ทำได้ไปแล้ว</b><br>
                    👉 สอบไป {n_exams} ครั้ง เฉลี่ย {current_avg} คะแนน<br>
                    👉 คะแนนรวมเดิม = {n_exams} × {current_avg} = <b>{sum1} คะแนน</b><br><br>
                    <b>ขั้นที่ 2: หาผลรวมคะแนนใหม่ที่ต้องการ (เป้าหมาย)</b><br>
                    👉 ถ้ารวมการสอบครั้งหน้า จะสอบทั้งหมด {n_exams + 1} ครั้ง และอยากได้เฉลี่ย {target_avg} คะแนน<br>
                    👉 คะแนนรวมเป้าหมาย = {n_exams + 1} × {target_avg} = <b>{sum2} คะแนน</b><br><br>
                    <b>ขั้นที่ 3: หาคะแนนสอบครั้งสุดท้ายที่ต้องทำเพิ่ม</b><br>
                    👉 นำคะแนนรวมเป้าหมาย ลบด้วย คะแนนรวมเดิมที่มีอยู่<br>
                    👉 {sum2} - {sum1} = <b>{needed_score} คะแนน</b><br>
                    <b>ตอบ: {needed_score} คะแนน</b></span>"""

                elif scenario == "wrong_data":
                    n_items = random.choice([10, 20, 25, 40, 50])
                    old_avg = random.randint(40, 70)
                    wrong_val = random.randint(15, 45)
                    diff = random.choice([10, 20, 25, 40, 50])
                    correct_val = wrong_val + diff
                    
                    old_sum = n_items * old_avg
                    new_sum = old_sum - wrong_val + correct_val
                    new_avg = new_sum / n_items
                    new_avg_str = f"{new_avg:g}"
                    
                    svg = f"<div style='text-align:center;'>{draw_avg_box('📊', n_items, 'จำนวน', old_avg, '(เดิม)')} <span style='font-size:20px; vertical-align:middle; margin:0 10px;'>พบว่าอ่านผิด <br><b style='color:#e74c3c;'>❌ {wrong_val} ➔ ✔️ {correct_val}</b></span></div>"
                    
                    q = f"ค่าเฉลี่ยของข้อมูล <b>{n_items} จำนวน</b> คือ <b>{old_avg}</b><br>แต่ภายหลังตรวจสอบพบว่ามีการอ่านข้อมูลผิดไป 1 จำนวน คือ <b>อ่านผิดเป็น {wrong_val}</b> แต่ตัวเลขที่ถูกต้องคือ <b>{correct_val}</b><br>จงหา <b>'ค่าเฉลี่ยที่ถูกต้อง'</b> ของข้อมูลชุดนี้?<br>{svg}"
                    
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (🔥 ชาเลนจ์ - แก้ไขข้อมูลผิดพลาด):</b><br>
                    <b>ขั้นที่ 1: หาผลรวมของข้อมูลชุดเดิม (ที่ผิด) ก่อน</b><br>
                    👉 ผลรวมเดิม = จำนวนข้อมูล × ค่าเฉลี่ยเดิม<br>
                    👉 {n_items} × {old_avg} = <b>{old_sum:,}</b><br><br>
                    <b>ขั้นที่ 2: ปรับแก้ผลรวมให้ถูกต้อง</b><br>
                    👉 นำผลรวมเดิม ลบตัวที่ผิดออก แล้วบวกตัวที่ถูกเข้าไปแทน<br>
                    👉 {old_sum:,} - {wrong_val} + {correct_val} = <b>{new_sum:,}</b> (นี่คือผลรวมที่ถูกต้อง)<br><br>
                    <b>ขั้นที่ 3: หาค่าเฉลี่ยใหม่</b><br>
                    👉 นำผลรวมที่ถูกต้อง หารด้วย จำนวนข้อมูลเท่าเดิม ({n_items})<br>
                    👉 {new_sum:,} ÷ {n_items} = <b>{new_avg_str}</b><br>
                    <b>ตอบ: {new_avg_str}</b></span>"""

            elif actual_sub_t == "ความน่าจะเป็นเบื้องต้น (สุ่มหยิบของ)":
                
                # --- ฟังก์ชันวาดกล่องลูกแก้ว (VERSION 4 - Auto Resize ยืดหดกล่องอัตโนมัติ) ---
                def draw_marbles_box_svg(color_counts):
                    color_map = {"สีแดง": "#e74c3c", "สีฟ้า": "#3498db", "สีเขียว": "#2ecc71", "สีเหลือง": "#f1c40f", "สีม่วง": "#9b59b6"}
                    
                    total_marbles = sum(color_counts.values())
                    # ปรับจำนวนคอลัมน์ตามปริมาณลูกแก้ว
                    cols = 10 if total_marbles > 20 else 8
                    rows = (total_marbles + cols - 1) // cols
                    
                    marble_r = 12
                    col_w = 36
                    row_h = 36
                    
                    box_stroke_width = 4
                    # คำนวณขนาดกล่องแบบไดนามิก ยืดตามจำนวนแถวและคอลัมน์
                    box_width = max(320, cols * col_w + 30)
                    box_height = max(140, rows * row_h + 60)
                    
                    width = box_width + 100
                    height = box_height + 40
                    
                    svg = f'<div style="text-align:center; margin: 15px 0;"><svg width="{width}" height="{height}">'
                    
                    box_x = 50
                    box_y = 20
                    # วาดตัวกล่อง
                    svg += f'<rect x="{box_x}" y="{box_y}" width="{box_width}" height="{box_height}" fill="#ecf0f1" stroke="#34495e" stroke-width="{box_stroke_width}" rx="15"/>'
                    # เส้นแบ่งครึ่ง
                    svg += f'<path d="M {box_x} {box_y + 35} L {box_x + box_width} {box_y + 35}" stroke="#bdc3c7" stroke-width="2" stroke-dasharray="5,5"/>'
                    
                    marbles = []
                    for c_name, count in color_counts.items():
                        for _ in range(count):
                            marbles.append(color_map[c_name])
                    random.shuffle(marbles)
                    
                    # จุดเริ่มต้นวางลูกแก้ว
                    start_x = box_x + 20 + marble_r 
                    start_y = box_y + 35 + 15 + marble_r
                    
                    for i, color in enumerate(marbles):
                        r_idx = i // cols
                        c_idx = i % cols
                        cx = start_x + (c_idx * col_w)
                        cy = start_y + (r_idx * row_h)
                        
                        # วาดลูกแก้ว
                        svg += f'<circle cx="{cx}" cy="{cy}" r="{marble_r}" fill="{color}" stroke="#2c3e50" stroke-width="3"/>'
                        svg += f'<circle cx="{cx-4}" cy="{cy-4}" r="3" fill="#ffffff" opacity="0.5"/>'
                        
                    svg += '</svg></div>'
                    return svg

                colors_avail = ["สีแดง", "สีฟ้า", "สีเขียว", "สีเหลือง", "สีม่วง"]
                name = random.choice(NAMES)
                
                if is_challenge:
                    q_type = random.choice(["fraction", "not_color", "inverse"])
                    
                    if q_type == "inverse":
                        den = random.choice([3, 4, 5, 8, 10]) 
                        while True:
                            num = random.randint(1, den - 1) 
                            if math.gcd(num, den) == 1: break 
                        
                        mult = random.choice([2, 3, 4, 5])
                        target_count = num * mult
                        total_marbles = den * mult
                        
                        target_color = random.choice(colors_avail)
                        other_colors = [c for c in colors_avail if c != target_color]
                        
                        color_counts = {target_color: target_count}
                        rem_count = total_marbles - target_count
                        
                        n_others = random.randint(1, min(rem_count, len(other_colors)))
                        chosen_others = random.sample(other_colors, n_others)
                        
                        temp_rem = rem_count
                        for i, oc in enumerate(chosen_others):
                            if i == n_others - 1:
                                color_counts[oc] = temp_rem
                            else:
                                c_count = random.randint(1, temp_rem - (n_others - 1 - i))
                                color_counts[oc] = c_count
                                temp_rem -= c_count
                                
                        svg = draw_marbles_box_svg(color_counts)
                        
                        q = f"ในกล่องใบหนึ่งมีลูกแก้วสีต่างๆ รวมกัน <b>{total_marbles} ลูก</b> ดังรูป<br>{svg}<b style='color:#e67e22;'>รู้เพียงว่า</b> โอกาสที่จะสุ่มหยิบได้ <b>ลูกแก้ว{target_color}</b> คือ เศษ {num} ส่วน {den} ( <b>{num}/{den}</b> )<br>จงหาว่า ในกล่องมีลูกแก้ว{target_color}อยู่ทั้งหมดกี่ลูก?"
                        
                        sol = f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (🔥 ชาเลนจ์ - โจทย์ย้อนกลับ):</b><br>
                        <b>หลักการ:</b> เราสามารถขยายเศษส่วนความน่าจะเป็น เพื่อให้ส่วนเท่ากับจำนวนทั้งหมดได้<br><br>
                        <b>ขั้นที่ 1: วิเคราะห์เศษส่วนความน่าจะเป็นที่โจทย์กำหนด</b><br>
                        👉 โอกาสหยิบได้{target_color} = {num}/{den}<br>
                        👉 ตัวเลข <b>เศษ {num}</b> หมายถึง ถ้ามีของ {den} ลูก จะเป็น{target_color} {num} ลูก<br>
                        👉 ตัวเลข <b>ส่วน {den}</b> หมายถึง จำนวนทั้งหมดในสัดส่วนขั้นต่ำ<br><br>
                        <b>ขั้นที่ 2: เปรียบเทียบกับจำนวนจริง</b><br>
                        👉 จำนวนลูกแก้วทั้งหมดในกล่องจริงๆ คือ <b>{total_marbles} ลูก</b><br>
                        👉 เราต้องหาว่าต้องคูณอะไรเข้าที่ 'ส่วน {den}' ถึงจะได้ {total_marbles}?<br>
                        👉 คำนวณ: {total_marbles} ÷ {den} = <b>{mult}</b> (นี่คือตัวคูณ)<br><br>
                        <b>ขั้นที่ 3: คำนวณจำนวนลูกแก้ว{target_color}จริง</b><br>
                        👉 นำตัวคูณ ({mult}) ไปคูณทั้งเศษและส่วน<br>
                        👉 {num}/{den} x {mult}/{mult} = <b>{target_count}/{total_marbles}</b><br>
                        👉 ตัวเลขด้านบน (เศษ) คือจำนวนสีที่ต้องการ<br>
                        <b>ตอบ: ในกล่องมีลูกแก้ว{target_color}อยู่ {target_count} ลูก</b></span>"""
                        
                    elif q_type == "not_color":
                        num_colors = random.randint(3, 5)
                        chosen_colors = random.sample(colors_avail, num_colors)
                        color_counts = {}
                        total_marbles = 0
                        for c in chosen_colors:
                            count = random.randint(2, 6)
                            color_counts[c] = count
                            total_marbles += count
                        
                        svg = draw_marbles_box_svg(color_counts)
                        
                        not_target = random.choice(chosen_colors)
                        not_target_count = color_counts[not_target]
                        interested_count = total_marbles - not_target_count 
                        
                        g = math.gcd(interested_count, total_marbles)
                        num = interested_count // g
                        den = total_marbles // g
                        
                        q = f"ในกล่องมีลูกแก้วสีต่างๆ ดังรูป<br>{svg}ถ้า{name}หลับตาสุ่มหยิบลูกแก้ว 1 ลูก โอกาสที่จะ <b><span style='color:#e74c3c;'>ไม่</span>หยิบได้</b> <b>ลูกแก้ว{not_target}</b> คิดเป็นเศษส่วนเท่าใด?"
                        
                        colors_other_text = ", ".join([c for c in chosen_colors if c != not_target])
                        sol = f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (🔥 ชาเลนจ์ - โอกาสที่จะ 'ไม่'):</b><br>
                        <b>หลักการ:</b> โอกาสที่จะ <span style='color:#e74c3c;'>ไม่</span> หยิบได้สีA หมายถึง โอกาสที่จะหยิบได้สีอื่นๆ ทั้งหมดที่ไม่ใช่สีA!<br><br>
                        <b>ขั้นที่ 1: นับจำนวนลูกแก้วทั้งหมดในกล่อง</b><br>
                        👉 ในกล่องมีลูกแก้วรวมทั้งหมด <b>{total_marbles} ลูก</b><br><br>
                        <b>ขั้นที่ 2: หาจำนวนลูกแก้วสีที่เราสนใจ (คือไม่ใช่สี{not_target})</b><br>
                        👉 <b>วิธีที่ 1:</b> นับสีอื่นๆ รวมกัน ({colors_other_text}) = {interested_count} ลูก<br>
                        👉 <b>วิธีที่ 2 (เร็วกว่า):</b> เอาทั้งหมด - จำนวนสีที่ไม่ต้องการ ({total_marbles} - {not_target_count}) = <b>{interested_count} ลูก</b><br><br>
                        <b>ขั้นที่ 3: เขียนเป็นเศษส่วนอย่างต่ำ</b><br>
                        👉 โอกาสคือ เศษ {interested_count} ส่วน {total_marbles} ( <b>{interested_count}/{total_marbles}</b> )<br>
                        👉 ทอนเป็นเศษส่วนอย่างต่ำ โดยนำ {g} มาหาร จะได้ <b>{num}/{den}</b><br>
                        <b>ตอบ: เศษ {num} ส่วน {den}</b></span>"""

                    else: 
                        num_colors = random.randint(2, 4)
                        chosen_colors = random.sample(colors_avail, num_colors)
                        color_counts = {}
                        total_marbles = 0
                        for c in chosen_colors:
                            count = random.randint(2, 6)
                            color_counts[c] = count
                            total_marbles += count
                        
                        svg = draw_marbles_box_svg(color_counts)
                        
                        target_color = random.choice(chosen_colors)
                        target_count = color_counts[target_color]
                        
                        g = math.gcd(target_count, total_marbles)
                        num = target_count // g
                        den = total_marbles // g
                        
                        q = f"ในกล่องมีลูกแก้วสีต่างๆ ดังรูป<br>{svg}ถ้าสุ่มหยิบลูกแก้ว 1 ลูก โอกาสที่จะได้ <b>ลูกแก้ว{target_color}</b> คิดเป็นเศษส่วนเท่าใด?"
                        
                        sol = f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (🔥 ชาเลนจ์ - ความน่าจะเป็นแบบเศษส่วน):</b><br>
                        <b>สูตรความน่าจะเป็น:</b> จำนวนเหตุการณ์ที่สนใจ ÷ จำนวนเหตุการณ์ทั้งหมดที่เป็นไปได้<br><br>
                        <b>ขั้นที่ 1: นับจำนวนลูกแก้วทั้งหมดในกล่อง</b><br>
                        👉 ในกล่องมีลูกแก้วรวมทั้งหมด <b>{total_marbles} ลูก</b><br><br>
                        <b>ขั้นที่ 2: นับจำนวนลูกแก้วสีที่สนใจ</b><br>
                        👉 มีลูกแก้ว <b>{target_color}</b> ทั้งหมด <b>{target_count} ลูก</b><br><br>
                        <b>ขั้นที่ 3: เขียนเป็นเศษส่วนและทอนเป็นเศษส่วนอย่างต่ำ</b><br>
                        👉 โอกาสหยิบได้ คือ เศษ {target_count} ส่วน {total_marbles} ( <b>{target_count}/{total_marbles}</b> )<br>
                        👉 ทอนเป็นเศษส่วนอย่างต่ำ โดยนำ {g} มาหารทั้งเศษและส่วน จะได้ <b>{num}/{den}</b><br>
                        <b>ตอบ: เศษ {num} ส่วน {den}</b></span>"""

                else:
                    q_type_std = random.choice(["qualitative", "comparison"])
                    
                    if q_type_std == "comparison":
                        num_colors = random.randint(3, 4)
                        chosen_colors = random.sample(colors_avail, num_colors)
                        color_counts = {}
                        target_type = random.choice(["most_likely", "least_likely"])
                        
                        count_arr = []
                        if target_type == "most_likely":
                            count_arr.append(random.randint(6, 9)) 
                            for _ in range(num_colors - 1):
                                count_arr.append(random.randint(2, 5))
                        else:
                            count_arr.append(random.randint(2, 3)) 
                            for _ in range(num_colors - 1):
                                count_arr.append(random.randint(5, 8))
                                
                        random.shuffle(count_arr)
                        for c in chosen_colors:
                            color_counts[c] = count_arr.pop(0)
                        
                        svg = draw_marbles_box_svg(color_counts)
                        
                        if target_type == "most_likely":
                            q_text = "มีโอกาสถูกหยิบได้ <b>'มากที่สุด'</b>"
                            ans_val = max(color_counts.values())
                            ans_colors = [k for k, v in color_counts.items() if v == ans_val]
                            reason = f"มีจำนวนมากที่สุดในกล่อง ({ans_val} ลูก)"
                        else:
                            q_text = "มีโอกาสถูกหยิบได้ <b>'น้อยที่สุด'</b>"
                            ans_val = min(color_counts.values())
                            ans_colors = [k for k, v in color_counts.items() if v == ans_val]
                            reason = f"มีจำนวนน้อยที่สุดในกล่อง ({ans_val} ลูก)"
                            
                        ans_text = " และ ".join(ans_colors)
                        count_details = ", ".join([f"{k} {v} ลูก" for k, v in color_counts.items()])
                        
                        q = f"ในกล่องมีลูกแก้วสีต่างๆ ดังรูป<br>{svg}ถ้าหลับตาสุ่มหยิบลูกแก้ว 1 ลูก ลูกแก้ว <b>สีใด</b> {q_text}?"
                        
                        sol = f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (การเปรียบเทียบโอกาส):</b><br>
                        <b>หลักการ:</b> สีที่มีจำนวน <span style='color:#e74c3c;'>'มากที่สุด'</span> จะมีโอกาสถูกหยิบโดน <span style='color:#e74c3c;'>'มากที่สุด'</span> <br>
                        ในทางกลับกัน สีที่มีจำนวน <span style='color:#e74c3c;'>'น้อยที่สุด'</span> ก็จะมีโอกาส <span style='color:#e74c3c;'>'น้อยที่สุด'</span> เช่นกัน<br><br>
                        <b>ขั้นที่ 1: นับจำนวนลูกแก้วแต่ละสีจากรูปภาพ</b><br>
                        👉 {count_details}<br><br>
                        <b>ขั้นที่ 2: พิจารณาหาสิ่งที่โจทย์ถาม</b><br>
                        👉 โจทย์ถามหาสีที่ {q_text}<br>
                        👉 จากการนับ พบว่า <b>{ans_text}</b> {reason}<br>
                        <b>ตอบ: {ans_text}</b></span>"""
                        
                    else:
                        scenario_type = random.choice(["certain", "impossible", "possible"])
                        chosen_colors = random.sample(colors_avail, 2)
                        color_counts = {}
                        
                        if scenario_type == "certain":
                            target_color = chosen_colors[0]
                            color_counts[target_color] = random.randint(8, 16) 
                            ans = "เกิดขึ้นอย่างแน่นอน"
                            reason = f"ในกล่องมีแต่ลูกแก้ว{target_color}เพียงสีเดียว ไม่มีลูกแก้วสีอื่นปนอยู่เลย"
                        elif scenario_type == "impossible":
                            color_counts[chosen_colors[0]] = random.randint(4, 8)
                            color_counts[chosen_colors[1]] = random.randint(4, 8)
                            target_color = [c for c in colors_avail if c not in chosen_colors][0]
                            ans = "ไม่เกิดขึ้นอย่างแน่นอน"
                            reason = f"ในกล่องไม่มีลูกแก้ว{target_color}อยู่เลยแม้แต่ลูกเดียว"
                        else:
                            color_counts[chosen_colors[0]] = random.randint(4, 8)
                            color_counts[chosen_colors[1]] = random.randint(4, 8)
                            target_color = chosen_colors[0]
                            ans = "อาจจะเกิดขึ้นหรือไม่ก็ได้"
                            reason = f"ในกล่องมีลูกแก้ว{target_color}ปนอยู่กับสีอื่นด้วย จึงมีโอกาสที่จะหยิบได้สีนี้ หรืออาจจะไปหยิบโดนสีอื่นก็ได้"
                            
                        svg = draw_marbles_box_svg(color_counts)
                        q = f"ในกล่องมีลูกแก้วสีต่างๆ ดังรูป<br>{svg}ถ้าหลับตาสุ่มหยิบลูกแก้ว 1 ลูก เหตุการณ์ที่จะหยิบได้ <b>ลูกแก้ว{target_color}</b> เป็นอย่างไร?<br><br><span style='font-size:18px; color:#7f8c8d;'>(ตัวเลือก: <b>เกิดขึ้นอย่างแน่นอน</b> / <b>อาจจะเกิดขึ้นหรือไม่ก็ได้</b> / <b>ไม่เกิดขึ้นอย่างแน่นอน</b>)</span>"
                        
                        sol = f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (ความน่าจะเป็นเบื้องต้น):</b><br>
                        <b>พิจารณาสิ่งที่อยู่ในกล่อง:</b><br>
                        👉 จากรูปภาพ เหตุการณ์ที่จะหยิบได้ลูกแก้ว <b>{target_color}</b> คือ <b>"{ans}"</b><br>
                        👉 <b>เหตุผล:</b> เพราะ{reason}<br>
                        <b>ตอบ: {ans}</b></span>"""

            elif actual_sub_t == "โจทย์ปัญหาพื้นที่และความยาวรอบรูป":
                
                # --- ฟังก์ชันวาดรูปเรขาคณิต ---
                def draw_rect_svg(w_val, h_val, w_lbl, h_lbl, fill_color="#eaf2f8"):
                    scale = 140 / max(w_val, h_val)
                    dw = w_val * scale
                    dh = h_val * scale
                    svg = f'<div style="text-align:center; margin: 15px 0;"><svg width="300" height="200">'
                    svg += f'<rect x="{150 - dw/2}" y="{100 - dh/2}" width="{dw}" height="{dh}" fill="{fill_color}" stroke="#2980b9" stroke-width="3"/>'
                    svg += f'<text x="150" y="{100 - dh/2 - 10}" font-family="Sarabun" font-size="16" font-weight="bold" fill="#c0392b" text-anchor="middle">{w_lbl}</text>'
                    svg += f'<text x="{150 + dw/2 + 10}" y="100" font-family="Sarabun" font-size="16" font-weight="bold" fill="#c0392b" text-anchor="start" dominant-baseline="middle">{h_lbl}</text>'
                    svg += '</svg></div>'
                    return svg

                def draw_frame_svg(w_out, h_out, w_in, h_in, w_lbl, h_lbl, in_w_lbl, in_h_lbl):
                    scale = 140 / max(w_out, h_out)
                    dw_o = w_out * scale
                    dh_o = h_out * scale
                    dw_i = w_in * scale
                    dh_i = h_in * scale
                    svg = f'<div style="text-align:center; margin: 15px 0;"><svg width="300" height="200">'
                    # สี่เหลี่ยมใหญ่ด้านนอก
                    svg += f'<rect x="{150 - dw_o/2}" y="{100 - dh_o/2}" width="{dw_o}" height="{dh_o}" fill="#bdc3c7" stroke="#2c3e50" stroke-width="3"/>'
                    # สี่เหลี่ยมเล็กด้านใน (สระน้ำ)
                    svg += f'<rect x="{150 - dw_i/2}" y="{100 - dh_i/2}" width="{dw_i}" height="{dh_i}" fill="#85c1e9" stroke="#2c3e50" stroke-width="2" stroke-dasharray="4,4"/>'
                    
                    # ตัวเลขด้านนอก
                    svg += f'<text x="150" y="{100 - dh_o/2 - 10}" font-family="Sarabun" font-size="14" font-weight="bold" fill="#c0392b" text-anchor="middle">{w_lbl}</text>'
                    svg += f'<text x="{150 + dw_o/2 + 10}" y="100" font-family="Sarabun" font-size="14" font-weight="bold" fill="#c0392b" text-anchor="start" dominant-baseline="middle">{h_lbl}</text>'
                    
                    # 💡 แก้ไข: เอาคำว่า "สระน้ำ" ออก และจัดวางตำแหน่งตัวเลขด้านในให้ชัดเจน ไม่ทับกัน
                    svg += f'<text x="150" y="{100 - dh_i/2 + 18}" font-family="Sarabun" font-size="14" font-weight="bold" fill="#154360" text-anchor="middle">{in_w_lbl}</text>'
                    svg += f'<text x="{150 + dw_i/2 - 8}" y="100" font-family="Sarabun" font-size="14" font-weight="bold" fill="#154360" text-anchor="end" dominant-baseline="middle">{in_h_lbl}</text>'
                    
                    svg += '</svg></div>'
                    return svg
                
                if is_challenge:
                    scenario = random.choice(["reverse_square", "shaded_area", "cost_calc"])
                    
                    if scenario == "reverse_square":
                        side = random.randint(12, 35)
                        area = side * side
                        perimeter = 4 * side
                        
                        q = f"สนามหญ้ารูปสี่เหลี่ยมจัตุรัส มีพื้นที่ <b>{area:,} ตารางเมตร</b><br>ถ้าต้องการทำรั้วล้อมรอบสนามหญ้านี้ 1 รอบ จะต้องใช้รั้วยาวกี่เมตร?"
                        
                        sol = f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (🔥 ชาเลนจ์ - ย้อนกลับหาความยาวด้าน):</b><br>
                        <b>ขั้นที่ 1: หาความยาวด้านของรูปสี่เหลี่ยมจัตุรัส</b><br>
                        👉 สูตรพื้นที่สี่เหลี่ยมจัตุรัส = ด้าน × ด้าน<br>
                        👉 เราต้องหาว่า ตัวเลขอะไรคูณตัวเองแล้วได้ {area:,} ?<br>
                        👉 พบว่า <b>{side} × {side} = {area:,}</b><br>
                        👉 ดังนั้น สนามหญ้านี้ยาวด้านละ <b>{side} เมตร</b><br><br>
                        <b>ขั้นที่ 2: หาความยาวรอบรูป (ความยาวรั้ว)</b><br>
                        👉 สี่เหลี่ยมจัตุรัสมี 4 ด้านยาวเท่ากัน<br>
                        👉 ความยาวรอบรูป = 4 × ด้าน = 4 × {side} = <b>{perimeter:,} เมตร</b><br>
                        <b>ตอบ: {perimeter:,} เมตร</b></span>"""
                        
                    elif scenario == "shaded_area":
                        path_w = random.randint(2, 4)
                        
                        # 💡 แก้ไข: บังคับให้แนวนอน (ยาว) มีค่ามากกว่าแนวตั้ง (กว้าง) เสมอ
                        side_a = random.randint(5, 10)
                        side_b = random.randint(11, 16)
                        in_w = max(side_a, side_b) # แนวนอน (ยาว)
                        in_h = min(side_a, side_b) # แนวตั้ง (กว้าง)
                        
                        out_w = in_w + (2 * path_w)
                        out_h = in_h + (2 * path_w)
                        
                        area_out = out_w * out_h
                        area_in = in_w * in_h
                        area_shaded = area_out - area_in
                        
                        svg = draw_frame_svg(out_w, out_h, in_w, in_h, f"{out_w} ม.", f"{out_h} ม.", f"{in_w} ม.", f"{in_h} ม.")
                        
                        q = f"สวนสาธารณะรูปสี่เหลี่ยมผืนผ้า กว้าง <b>{out_h} ม.</b> ยาว <b>{out_w} ม.</b><br>มีสระน้ำอยู่ตรงกลาง กว้าง <b>{in_h} ม.</b> ยาว <b>{in_w} ม.</b> ดังรูป<br>จงหาพื้นที่ของ <b>ทางเดินรอบสระน้ำ</b> (พื้นที่แรเงาสีเทา) ว่ามีกี่ตารางเมตร?<br>{svg}"
                        
                        sol = f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (🔥 ชาเลนจ์ - พื้นที่แรเงา):</b><br>
                        <i>หลักการ: พื้นที่ทางเดิน = พื้นที่รูปใหญ่ (ทั้งหมด) - พื้นที่รูปเล็ก (สระน้ำ)</i><br><br>
                        <b>ขั้นที่ 1: หาพื้นที่สี่เหลี่ยมรูปใหญ่ (พื้นที่ทั้งหมด)</b><br>
                        👉 สูตร: กว้าง × ยาว<br>
                        👉 คำนวณ: {out_h} × {out_w} = <b>{area_out:,} ตารางเมตร</b><br><br>
                        <b>ขั้นที่ 2: หาพื้นที่สี่เหลี่ยมรูปเล็ก (สระน้ำตรงกลาง)</b><br>
                        👉 คำนวณ: {in_h} × {in_w} = <b>{area_in:,} ตารางเมตร</b><br><br>
                        <b>ขั้นที่ 3: หาพื้นที่ทางเดินรอบสระ</b><br>
                        👉 นำพื้นที่ทั้งหมด ลบด้วย พื้นที่สระน้ำ<br>
                        👉 {area_out:,} - {area_in:,} = <b>{area_shaded:,} ตารางเมตร</b><br>
                        <b>ตอบ: {area_shaded:,} ตารางเมตร</b></span>"""
                        
                    elif scenario == "cost_calc":
                        w = random.randint(8, 15)
                        h = random.randint(16, 25)
                        area = w * h
                        rate = random.choice([250, 350, 450, 500])
                        total_cost = area * rate
                        
                        q = f"ห้องประชุมรูปสี่เหลี่ยมผืนผ้า กว้าง <b>{w} เมตร</b> ยาว <b>{h} เมตร</b><br>ถ้าต้องการปูกระเบื้องพื้นห้อง โดยช่างคิดค่าปูกระเบื้อง <b>ตารางเมตรละ {rate:,} บาท</b><br>จะต้องจ่ายเงินค่าปูกระเบื้องทั้งหมดกี่บาท?"
                        
                        sol = f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (🔥 ชาเลนจ์ - ประยุกต์หาค่าใช้จ่าย):</b><br>
                        <b>ขั้นที่ 1: หาพื้นที่ของห้องประชุมก่อน</b><br>
                        👉 เพราะช่างคิดราคาเป็น "ตารางเมตร" เราจึงต้องหาพื้นที่ ไม่ใช่ความยาวรอบรูป!<br>
                        👉 พื้นที่ห้อง = กว้าง × ยาว<br>
                        👉 คำนวณ: {w} × {h} = <b>{area:,} ตารางเมตร</b><br><br>
                        <b>ขั้นที่ 2: คำนวณค่าใช้จ่ายทั้งหมด</b><br>
                        👉 พื้นที่ 1 ตารางเมตร จ่าย {rate:,} บาท<br>
                        👉 พื้นที่ {area:,} ตารางเมตร ต้องจ่าย = {area:,} × {rate:,} = <b>{total_cost:,} บาท</b><br>
                        <b>ตอบ: {total_cost:,} บาท</b></span>"""
                        
                else:
                    scenario = random.choice(["find_area", "find_peri", "find_side"])
                    is_square = random.choice([True, False])
                    
                    if is_square:
                        side = random.randint(8, 25)
                        area = side * side
                        perimeter = 4 * side
                        shape_name = "สี่เหลี่ยมจัตุรัส"
                        svg = draw_rect_svg(side, side, f"{side} ซม.", f"{side} ซม.", "#fcf3cf")
                    else:
                        w = random.randint(5, 15)
                        h = random.randint(16, 30)
                        area = w * h
                        perimeter = 2 * (w + h)
                        shape_name = "สี่เหลี่ยมผืนผ้า"
                        svg = draw_rect_svg(h, w, f"{h} ซม.", f"{w} ซม.", "#d5f5e3")
                        
                    if scenario == "find_area":
                        q = f"รูป{shape_name}ดังรูป มี<b>พื้นที่</b>กี่ตารางเซนติเมตร?<br>{svg}"
                        if is_square:
                            sol = f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>
                            👉 สูตรพื้นที่สี่เหลี่ยมจัตุรัส = ด้าน × ด้าน<br>
                            👉 คำนวณ: {side} × {side} = <b>{area:,} ตารางเซนติเมตร</b><br>
                            <b>ตอบ: {area:,} ตารางเซนติเมตร</b></span>"""
                        else:
                            sol = f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>
                            👉 สูตรพื้นที่สี่เหลี่ยมผืนผ้า = กว้าง × ยาว<br>
                            👉 คำนวณ: {w} × {h} = <b>{area:,} ตารางเซนติเมตร</b><br>
                            <b>ตอบ: {area:,} ตารางเซนติเมตร</b></span>"""
                            
                    elif scenario == "find_peri":
                        q = f"รูป{shape_name}ดังรูป มี<b>ความยาวรอบรูป</b>กี่เซนติเมตร?<br>{svg}"
                        if is_square:
                            sol = f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>
                            👉 ความยาวรอบรูปสี่เหลี่ยมจัตุรัส = 4 × ด้าน (นำทั้ง 4 ด้านมาบวกกัน)<br>
                            👉 คำนวณ: 4 × {side} = <b>{perimeter:,} เซนติเมตร</b><br>
                            <b>ตอบ: {perimeter:,} เซนติเมตร</b></span>"""
                        else:
                            sol = f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>
                            👉 ความยาวรอบรูปสี่เหลี่ยมผืนผ้า = (กว้าง + ยาว) × 2<br>
                            👉 คำนวณ: กว้าง + ยาว = {w} + {h} = {w+h} ซม.<br>
                            👉 นำมาคูณ 2 (เพราะมีด้านละ 2 ฝั่ง): {w+h} × 2 = <b>{perimeter:,} เซนติเมตร</b><br>
                            <b>ตอบ: {perimeter:,} เซนติเมตร</b></span>"""
                            
                    elif scenario == "find_side":
                        if is_square:
                            q = f"กระดาษรูปสี่เหลี่ยมจัตุรัส มี<b>ความยาวรอบรูป {perimeter:,} เซนติเมตร</b><br>จงหาว่ากระดาษแผ่นนี้มีความยาวด้านละกี่เซนติเมตร?"
                            sol = f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>
                            👉 สี่เหลี่ยมจัตุรัสมีด้านยาวเท่ากัน 4 ด้าน<br>
                            👉 ถ้าความยาวทั้ง 4 ด้านรวมกันได้ {perimeter:,} ซม.<br>
                            👉 หาความยาว 1 ด้าน โดยการนำไปหาร 4<br>
                            👉 คำนวณ: {perimeter:,} ÷ 4 = <b>{side} เซนติเมตร</b><br>
                            <b>ตอบ: {side} เซนติเมตร</b></span>"""
                        else:
                            q = f"กรอบรูปร้านหนึ่งเป็นรูปสี่เหลี่ยมผืนผ้า มี<b>ความยาวรอบรูป {perimeter:,} เซนติเมตร</b><br>ถ้ากรอบรูปนี้กว้าง <b>{w} เซนติเมตร</b> จะมีความยาวกี่เซนติเมตร?"
                            sol = f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>
                            <b>ขั้นที่ 1: หาความยาวของด้านกว้างทั้ง 2 ด้านรวมกัน</b><br>
                            👉 กรอบรูปมีด้านกว้าง 2 ด้าน = {w} × 2 = <b>{w*2} ซม.</b><br><br>
                            <b>ขั้นที่ 2: หาความยาวที่เหลือ (สำหรับด้านยาว 2 ด้าน)</b><br>
                            👉 นำความยาวรอบรูปทั้งหมด ลบด้วย ความยาวด้านกว้าง<br>
                            👉 {perimeter:,} - {w*2} = <b>{perimeter - (w*2)} ซม.</b><br><br>
                            <b>ขั้นที่ 3: หาความยาว 1 ด้าน</b><br>
                            👉 ด้านยาวมี 2 ด้าน จึงต้องแบ่งครึ่งความยาวที่เหลือ<br>
                            👉 {(perimeter - (w*2))} ÷ 2 = <b>{h} เซนติเมตร</b><br>
                            <b>ตอบ: {h} เซนติเมตร</b></span>"""
            elif actual_sub_t == "การหาขนาดของมุมที่หายไป":
                def draw_angle_feature(vx, vy, ax, ay, bx, by, r_arc, r_text, label, color_arc, color_text, is_x=False):
                    len_a = math.hypot(ax - vx, ay - vy)
                    len_b = math.hypot(bx - vx, by - vy)
                    if len_a == 0 or len_b == 0: return ""
                    sx = vx + (ax - vx) * r_arc / len_a
                    sy = vy + (ay - vy) * r_arc / len_a
                    ex = vx + (bx - vx) * r_arc / len_b
                    ey = vy + (by - vy) * r_arc / len_b
                    cp = (sx - vx) * (ey - vy) - (sy - vy) * (ex - vx)
                    sweep = 1 if cp > 0 else 0
                    arc_svg = f'<path d="M {sx} {sy} A {r_arc} {r_arc} 0 0 {sweep} {ex} {ey}" fill="none" stroke="{color_arc}" stroke-width="3"/>'
                    mid_x = (sx - vx)/r_arc + (ex - vx)/r_arc
                    mid_y = (sy - vy)/r_arc + (ey - vy)/r_arc
                    len_mid = math.hypot(mid_x, mid_y)
                    if len_mid == 0: tx, ty = vx, vy - r_text
                    else: tx, ty = vx + (mid_x / len_mid) * r_text, vy + (mid_y / len_mid) * r_text
                    ty += 4 
                    font_size = "16px" if is_x else "13px"
                    lbl_svg = f'<text x="{tx}" y="{ty}" font-size="{font_size}" font-weight="bold" font-family="Sarabun" text-anchor="middle" fill="{color_text}">{label}</text>'
                    return arc_svg + lbl_svg

                def draw_angle_svg(mode, val1, val2, val3=""):
                    svg = '<div style="text-align:center; margin:15px 0;"><svg width="340" height="200">'
                    lbl_style = 'font-family:Sarabun; font-size:16px; font-weight:bold; fill:#2c3e50;'
                    if mode == "straight":
                        vx, vy = 170, 160
                        phi = val2 
                        ax, ay = 40, 160 
                        cx, cy = 300, 160 
                        bx = vx + 120 * math.cos(math.radians(phi)) 
                        by = vy - 120 * math.sin(math.radians(phi))
                        svg += f'<line x1="{ax}" y1="{ay}" x2="{cx}" y2="{cy}" stroke="#34495e" stroke-width="4"/>'
                        svg += f'<line x1="{vx}" y1="{vy}" x2="{bx}" y2="{by}" stroke="#c0392b" stroke-width="3"/>'
                        svg += f'<circle cx="{bx}" cy="{by}" r="3" fill="#c0392b"/>'
                        svg += f'<text x="{ax-15}" y="{ay+5}" {lbl_style}>A</text>'
                        svg += f'<text x="{cx+5}" y="{cy+5}" {lbl_style}>B</text>'
                        svg += f'<text x="{bx-5}" y="{by-10}" {lbl_style}>C</text>'
                        svg += f'<text x="{vx-5}" y="{vy+20}" {lbl_style}>O</text>'
                        svg += draw_angle_feature(vx, vy, ax, ay, bx, by, 28, 45, f"{val1}°", "#2ecc71", "#c0392b")
                        svg += draw_angle_feature(vx, vy, bx, by, cx, cy, 28, 45, val2 if val3=="" else val3, "#2ecc71", "#2980b9", is_x=True)
                    elif mode == "opposite":
                        vx, vy = 170, 100
                        phi = val1 
                        L = 85
                        tl_x = vx + L*math.cos(math.radians(180-phi))
                        tl_y = vy - L*math.sin(math.radians(180-phi))
                        br_x = vx + L*math.cos(math.radians(-phi))
                        br_y = vy - L*math.sin(math.radians(-phi))
                        bl_x = vx + L*math.cos(math.radians(180+phi))
                        bl_y = vy - L*math.sin(math.radians(180+phi))
                        tr_x = vx + L*math.cos(math.radians(phi))
                        tr_y = vy - L*math.sin(math.radians(phi))
                        svg += f'<line x1="{tl_x}" y1="{tl_y}" x2="{br_x}" y2="{br_y}" stroke="#34495e" stroke-width="4"/>'
                        svg += f'<line x1="{bl_x}" y1="{bl_y}" x2="{tr_x}" y2="{tr_y}" stroke="#34495e" stroke-width="4"/>'
                        svg += f'<text x="{tl_x-15}" y="{tl_y-5}" {lbl_style}>A</text>'
                        svg += f'<text x="{br_x+5}" y="{br_y+15}" {lbl_style}>B</text>'
                        svg += f'<text x="{bl_x-15}" y="{bl_y+15}" {lbl_style}>C</text>'
                        svg += f'<text x="{tr_x+5}" y="{tr_y-5}" {lbl_style}>D</text>'
                        svg += draw_angle_feature(vx, vy, tl_x, tl_y, tr_x, tr_y, 25, 42, f"{val1}°", "#2ecc71", "#c0392b")
                        svg += draw_angle_feature(vx, vy, bl_x, bl_y, br_x, br_y, 25, 42, val2 if val3=="" else val3, "#2ecc71", "#2980b9", is_x=True)
                    elif mode == "triangle":
                        base_y = 160
                        L = 160
                        rad1 = math.radians(val1)
                        rad2 = math.radians(val2)
                        raw_h = L / (1/math.tan(rad1) + 1/math.tan(rad2))
                        if raw_h > 120:
                            scale = 120 / raw_h
                            L = L * scale
                            h = 120
                        else: h = raw_h
                        p1x = 170 - L/2
                        p2x = 170 + L/2
                        top_y = base_y - h
                        top_x = p1x + h / math.tan(rad1)
                        svg += f'<polygon points="{p1x},{base_y} {p2x},{base_y} {top_x},{top_y}" fill="#fef9e7" stroke="#f39c12" stroke-width="3" stroke-linejoin="round"/>'
                        svg += f'<text x="{top_x}" y="{top_y-10}" {lbl_style} text-anchor="middle">A</text>'
                        svg += f'<text x="{p1x-15}" y="{base_y+5}" {lbl_style}>B</text>'
                        svg += f'<text x="{p2x+5}" y="{base_y+5}" {lbl_style}>C</text>'
                        svg += draw_angle_feature(p1x, base_y, p2x, base_y, top_x, top_y, 25, 40, f"{val1}°", "#2ecc71", "#c0392b")
                        svg += draw_angle_feature(p2x, base_y, top_x, top_y, p1x, base_y, 25, 40, f"{val2}°", "#2ecc71", "#c0392b")
                        svg += draw_angle_feature(top_x, top_y, p1x, base_y, p2x, base_y, 25, 42, val3, "#2ecc71", "#2980b9", is_x=True)
                    svg += '</svg></div>'
                    return svg

                scenario = random.choice(["straight", "opposite", "triangle"])
                if scenario == "straight":
                    ans = random.randint(35, 145)
                    given = 180 - ans 
                    svg = draw_angle_svg("straight", given, ans, "x")
                    q = f"จากรูป มุมบนเส้นตรงมีขนาดรวม 180°<br>จงหาขนาดของมุม <b>x</b> ?<br>{svg}"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (มุมบนเส้นตรง):</b><br>👉 มุมบนเส้นตรงมีขนาดรวม 180° เสมอ<br>👉 จะได้สมการ: {given}° + x = 180°<br>👉 x = 180° - {given}° = <b>{ans}°</b><br><b>ตอบ: {ans}°</b></span>"
                elif scenario == "opposite":
                    ans = random.randint(40, 80)
                    svg = draw_angle_svg("opposite", ans, ans, "x")
                    q = f"จากรูป เส้นตรงสองเส้นตัดกัน<br>จงหาขนาดของมุม <b>x</b> ?<br>{svg}"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (มุมตรงข้าม):</b><br>👉 เมื่อเส้นตรงตัดกัน <b>มุมที่อยู่ตรงข้ามกันจะมีขนาดเท่ากัน</b><br>👉 จากรูป มุม x อยู่ตรงข้ามกับมุม {ans}° พอดี<br>👉 ดังนั้น x = <b>{ans}°</b><br><b>ตอบ: {ans}°</b></span>"
                else: 
                    a1 = random.randint(40, 75)
                    a2 = random.randint(40, 75)
                    ans = 180 - a1 - a2
                    svg = draw_angle_svg("triangle", a1, a2, "x")
                    q = f"จากรูป รูปสามเหลี่ยมมีผลรวมมุมภายใน 180°<br>จงหาขนาดของมุม <b>x</b> ?<br>{svg}"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (มุมภายในรูปสามเหลี่ยม):</b><br>👉 ผลรวมมุมภายในของรูปสามเหลี่ยมทุกชนิด = 180°<br>👉 มุมที่โจทย์กำหนดให้ 2 มุม รวมกัน = {a1}° + {a2}° = {a1+a2}°<br>👉 มุมที่เหลือ x = 180° - {a1+a2}° = <b>{ans}°</b><br><b>ตอบ: {ans}°</b></span>"

            elif actual_sub_t == "เส้นขนานและมุมแย้ง":
                def draw_angle_feature(vx, vy, ax, ay, bx, by, r_arc, r_text, label, color_arc, color_text, is_x=False):
                    len_a = math.hypot(ax - vx, ay - vy)
                    len_b = math.hypot(bx - vx, by - vy)
                    if len_a == 0 or len_b == 0: return ""
                    sx = vx + (ax - vx) * r_arc / len_a
                    sy = vy + (ay - vy) * r_arc / len_a
                    ex = vx + (bx - vx) * r_arc / len_b
                    ey = vy + (by - vy) * r_arc / len_b
                    cp = (sx - vx) * (ey - vy) - (sy - vy) * (ex - vx)
                    sweep = 1 if cp > 0 else 0
                    arc_svg = f'<path d="M {sx} {sy} A {r_arc} {r_arc} 0 0 {sweep} {ex} {ey}" fill="none" stroke="{color_arc}" stroke-width="3"/>'
                    mid_x = (sx - vx)/r_arc + (ex - vx)/r_arc
                    mid_y = (sy - vy)/r_arc + (ey - vy)/r_arc
                    len_mid = math.hypot(mid_x, mid_y)
                    if len_mid == 0: tx, ty = vx, vy - r_text
                    else: tx, ty = vx + (mid_x / len_mid) * r_text, vy + (mid_y / len_mid) * r_text
                    ty += 5 
                    font_size = "16px" if is_x else "14px"
                    lbl_svg = f'<text x="{tx}" y="{ty}" font-size="{font_size}" font-weight="bold" font-family="Sarabun" text-anchor="middle" fill="{color_text}">{label}</text>'
                    return arc_svg + lbl_svg

                angle_meta = {
                    "dir1": { 
                        "bot": (110, 165), "top": (210, 15),
                        "V1": (180, 60), "V2": (140, 120),
                        "acute": ["TR_ext", "BL_int", "TL_int", "BR_ext"],
                        "obtuse": ["TL_ext", "BR_int", "TR_int", "BL_ext"]
                    },
                    "dir2": { 
                        "bot": (220, 165), "top": (120, 15),
                        "V1": (150, 60), "V2": (190, 120),
                        "acute": ["TL_ext", "BR_int", "TR_int", "BL_ext"],
                        "obtuse": ["TR_ext", "BL_int", "TL_int", "BR_ext"]
                    }
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

                def draw_parallel_svg(dir_key, pos1, val1, pos2, val2):
                    svg = '<div style="text-align:center; margin:15px 0;"><svg width="340" height="200">'
                    svg += '<line x1="40" y1="60" x2="300" y2="60" stroke="#2980b9" stroke-width="4"/>'
                    svg += '<line x1="40" y1="120" x2="300" y2="120" stroke="#2980b9" stroke-width="4"/>'
                    svg += '<polygon points="285,55 295,60 285,65" fill="#2980b9"/>'
                    svg += '<polygon points="285,115 295,120 285,125" fill="#2980b9"/>'
                    lbl_style = 'font-family:Sarabun; font-size:16px; font-weight:bold; fill:#2c3e50;'
                    svg += f'<text x="20" y="65" {lbl_style}>A</text>'
                    svg += f'<text x="310" y="65" {lbl_style}>B</text>'
                    svg += f'<text x="20" y="125" {lbl_style}>C</text>'
                    svg += f'<text x="310" y="125" {lbl_style}>D</text>'
                    meta = angle_meta[dir_key]
                    bot, top = meta["bot"], meta["top"]
                    svg += f'<line x1="{bot[0]}" y1="{bot[1]}" x2="{top[0]}" y2="{top[1]}" stroke="#3498db" stroke-width="4"/>'
                    svg += f'<circle cx="{bot[0]}" cy="{bot[1]}" r="4" fill="#3498db" />'
                    svg += f'<circle cx="{top[0]}" cy="{top[1]}" r="4" fill="#3498db" />'
                    V1, V2 = meta["V1"], meta["V2"]
                    def draw_pos(pos, val, is_var):
                        vx, arm1, arm2 = get_arms(pos, V1, V2, bot, top)
                        color = "#2980b9" if is_var else "#c0392b"
                        text_label = "x" if is_var else f"{val}°" 
                        return draw_angle_feature(vx[0], vx[1], arm1[0], arm1[1], arm2[0], arm2[1], 25, 42, text_label, "#2ecc71", color, is_x=is_var)
                    svg += draw_pos(pos1, val1, is_var=False)
                    svg += draw_pos(pos2, val2, is_var=True)
                    svg += '</svg></div>'
                    return svg

                direction = random.choice(["dir1", "dir2"])
                scenario = random.choice(["Z", "C", "F"])
                pairs = {
                    "Z": [("BL_int", "TR_int"), ("BR_int", "TL_int")],
                    "C": [("BL_int", "TL_int"), ("BR_int", "TR_int")],
                    "F": [("TL_ext", "TL_int"), ("TR_ext", "TR_int"), ("BL_int", "BL_ext"), ("BR_int", "BR_ext")]
                }
                pair = random.choice(pairs[scenario])
                if random.choice([True, False]): pos1, pos2 = pair
                else: pos2, pos1 = pair
                is_acute = pos1 in angle_meta[direction]["acute"]
                if is_acute: val = random.randint(40, 85)
                else: val = random.randint(95, 140)
                    
                if scenario == "Z":
                    ans = val
                    svg = draw_parallel_svg(direction, pos1, val, pos2, "x")
                    q = f"จากรูป เส้นตรงสองเส้นขนานกัน<br>จงหาขนาดของมุม <b>x</b> (พิจารณามุมแย้ง)?<br>{svg}"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (เส้นขนาน รูปตัว Z):</b><br>👉 เมื่อเส้นขนานถูกตัดด้วยเส้นตรง <b>มุมแย้ง (ตัว Z) จะมีขนาดเท่ากัน</b>เสมอ<br>👉 จากรูป มุม x เป็นมุมแย้งกับมุม {val}°<br>👉 ดังนั้น x = <b>{ans}°</b><br><b>ตอบ: {ans}°</b></span>"
                elif scenario == "C":
                    ans = 180 - val
                    svg = draw_parallel_svg(direction, pos1, val, pos2, "x")
                    q = f"จากรูป เส้นตรงสองเส้นขนานกัน<br>จงหาขนาดของมุม <b>x</b> (พิจารณามุมภายในข้างเดียวกัน)?<br>{svg}"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (เส้นขนาน รูปตัว C):</b><br>👉 <b>มุมภายในที่อยู่บนข้างเดียวกัน</b>ของเส้นตัด (ตัว C) จะรวมกันได้ <b>180°</b> เสมอ<br>👉 จะได้สมการ: {val}° + x = 180°<br>👉 x = 180° - {val}° = <b>{ans}°</b><br><b>ตอบ: {ans}°</b></span>"
                elif scenario == "F":
                    ans = val
                    svg = draw_parallel_svg(direction, pos1, val, pos2, "x")
                    q = f"จากรูป เส้นตรงสองเส้นขนานกัน<br>จงหาขนาดของมุม <b>x</b> (พิจารณามุมภายนอกและมุมภายใน)?<br>{svg}"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (เส้นขนาน รูปตัว F):</b><br>👉 <b>มุมภายนอกและมุมภายใน</b>ที่อยู่บนข้างเดียวกันของเส้นตัด จะมีขนาด<b>เท่ากัน</b>เสมอ<br>👉 จากรูป มุม x มีตำแหน่งสอดคล้องกับมุม {val}° พอดี<br>👉 ดังนั้น x = <b>{ans}°</b><br><b>ตอบ: {ans}°</b></span>"

            elif actual_sub_t == "ปริมาตรและความจุทรงสี่เหลี่ยมมุมฉาก":
                def draw_prism_svg(w_lbl, l_lbl, h_lbl, is_water=False):
                    svg = '<div style="text-align:center; margin:15px 0;"><svg width="250" height="190">'
                    fill_front = "#aed6f1" if is_water else "#d5f5e3"
                    fill_top = "#85c1e9" if is_water else "#abebc6"
                    fill_right = "#5dade2" if is_water else "#82e0aa"
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
                    svg += '</svg></div>'
                    return svg

                scenario = random.choice(["basic", "tank"])
                if scenario == "basic":
                    w = random.randint(3, 10)
                    l = random.randint(5, 15)
                    while l <= w: l += 1
                    h = random.randint(4, 12)
                    vol = w * l * h
                    svg = draw_prism_svg(f"{w} ซม.", f"{l} ซม.", f"{h} ซม.")
                    q = f"กล่องทรงสี่เหลี่ยมมุมฉาก กว้าง <b>{w} ซม.</b> ยาว <b>{l} ซม.</b> และสูง <b>{h} ซม.</b><br>กล่องใบนี้จะมี<b>ปริมาตร</b>ความจุกี่ลูกบาศก์เซนติเมตร?<br>{svg}"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (การหาปริมาตร):</b><br><b>สูตร:</b> ปริมาตรทรงสี่เหลี่ยมมุมฉาก = กว้าง × ยาว × สูง<br>👉 แทนค่า: กว้าง = {w}, ยาว = {l}, สูง = {h}<br>👉 คำนวณ: {w} × {l} × {h} = <b>{vol:,} ลูกบาศก์เซนติเมตร</b><br><b>ตอบ: {vol:,} ลูกบาศก์เซนติเมตร</b></span>"
                elif scenario == "tank":
                    w = random.randint(10, 20)
                    l = random.randint(20, 40)
                    h = random.randint(15, 30)
                    water_h = random.randint(5, h - 5)
                    vol = w * l * water_h
                    svg = draw_prism_svg(f"{w} ซม.", f"{l} ซม.", f"น้ำสูง {water_h} ซม.", is_water=True)
                    q = f"ตู้ปลาทรงสี่เหลี่ยมมุมฉาก กว้าง <b>{w} ซม.</b> ยาว <b>{l} ซม.</b> สูง <b>{h} ซม.</b><br>ถ้าเติมน้ำลงไปในตู้ปลาให้มีระดับน้ำสูง <b>{water_h} ซม.</b><br>ปริมาตรของน้ำในตู้ปลาจะเป็นกี่ลูกบาศก์เซนติเมตร?<br>{svg}"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (ประยุกต์ปริมาตรน้ำ):</b><br><i>จุดระวัง: โจทย์ถามปริมาตรของ 'น้ำ' ดังนั้นเราต้องใช้ 'ความสูงของน้ำ' ไม่ใช่ความสูงของตู้ปลานะครับ!</i><br><br><b>สูตร:</b> ปริมาตรน้ำ = กว้าง × ยาว × ความสูงของน้ำ<br>👉 แทนค่า: กว้าง = {w}, ยาว = {l}, สูงของน้ำ = {water_h}<br>👉 คำนวณ: {w} × {l} × {water_h} = <b>{vol:,} ลูกบาศก์เซนติเมตร</b><br><b>ตอบ: {vol:,} ลูกบาศก์เซนติเมตร</b></span>"

            elif actual_sub_t in ["การบวกเศษส่วน", "การลบเศษส่วน", "การคูณเศษส่วน", "การหารเศษส่วน"]:
                def render_frac(n, d, w=0):
                    frac_html = f"<div style='display:inline-block; vertical-align:middle; text-align:center; margin: 0 5px;'><div style='border-bottom:2px solid #2c3e50; padding:0 4px;'><b>{n}</b></div><div style='padding-top:2px;'><b>{d}</b></div></div>"
                    if w != 0: return f"<div style='display:inline-block; vertical-align:middle;'><span style='font-size:24px; font-weight:bold; color:#2c3e50; margin-right:3px;'>{w}</span>{frac_html}</div>"
                    return frac_html
                def get_mixed(n, d):
                    if n == 0: return "0"
                    if d == 1: return str(n)
                    if n < d: return render_frac(n, d)
                    w = n // d
                    rem = n % d
                    if rem == 0: return str(w)
                    return render_frac(rem, d, w)

                op_map = {"การบวกเศษส่วน": "+", "การลบเศษส่วน": "-", "การคูณเศษส่วน": "×", "การหารเศษส่วน": "÷"}
                op_sign = op_map[actual_sub_t]
                
                if is_challenge:
                    d1, d2 = random.randint(3, 9), random.randint(3, 9)
                    while d1 == d2: d2 = random.randint(3, 9)
                    n1, n2 = random.randint(1, d1-1), random.randint(1, d2-1)
                    w1, w2 = random.randint(1, 5), random.randint(1, 5)
                    
                    if actual_sub_t in ["การลบเศษส่วน", "การหารเศษส่วน"]:
                        val1, val2 = w1 + (n1/d1), w2 + (n2/d2)
                        if val1 <= val2: w1, w2, n1, n2, d1, d2 = w2, w1, n2, n1, d2, d1
                            
                    f1_str, f2_str = render_frac(n1, d1, w1), render_frac(n2, d2, w2)
                    q = f"จงหาผลลัพธ์ต่อไปนี้ให้อยู่ในรูปอย่างง่าย<br><br><div style='text-align:center; font-size:24px;'>{f1_str} <span style='color:#e74c3c; margin: 0 10px; font-size:28px; vertical-align:middle;'><b>{op_sign}</b></span> {f2_str} = ?</div>"
                    
                    imp_n1, imp_n2 = (w1 * d1) + n1, (w2 * d2) + n2
                    step_mixed = f"<b>ขั้นที่ 1:</b> แปลงจำนวนคละให้เป็นเศษเกิน<br>👉 {f1_str} = {render_frac(imp_n1, d1)}<br>👉 {f2_str} = {render_frac(imp_n2, d2)}<br><br>"
                    
                    lcm = (d1 * d2) // math.gcd(d1, d2)
                    if actual_sub_t == "การบวกเศษส่วน":
                        new_n1, new_n2 = imp_n1 * (lcm // d1), imp_n2 * (lcm // d2)
                        res_n, res_d = new_n1 + new_n2, lcm
                        step1 = f"<b>ขั้นที่ 2:</b> หา ค.ร.น. ของ {d1} และ {d2} คือ <b>{lcm}</b>"
                        step2 = f"<b>ขั้นที่ 3:</b> แปลงส่วนให้เท่ากัน แล้วนำเศษมาบวกกัน<br>👉 ({new_n1} + {new_n2}) / {lcm} = {render_frac(res_n, res_d)}"
                    elif actual_sub_t == "การลบเศษส่วน":
                        new_n1, new_n2 = imp_n1 * (lcm // d1), imp_n2 * (lcm // d2)
                        res_n, res_d = new_n1 - new_n2, lcm
                        step1 = f"<b>ขั้นที่ 2:</b> หา ค.ร.น. ของ {d1} และ {d2} คือ <b>{lcm}</b>"
                        step2 = f"<b>ขั้นที่ 3:</b> แปลงส่วนให้เท่ากัน แล้วนำเศษมาลบกัน<br>👉 ({new_n1} - {new_n2}) / {lcm} = {render_frac(res_n, res_d)}"
                    elif actual_sub_t == "การคูณเศษส่วน":
                        res_n, res_d = imp_n1 * imp_n2, d1 * d2
                        step1 = f"<b>ขั้นที่ 2:</b> นำ (เศษ × เศษ) และ (ส่วน × ส่วน)"
                        step2 = f"👉 คำนวณ: ({imp_n1} × {imp_n2}) / ({d1} × {d2}) = {render_frac(res_n, res_d)}"
                    elif actual_sub_t == "การหารเศษส่วน":
                        res_n, res_d = imp_n1 * d2, d1 * imp_n2
                        step1 = f"<b>ขั้นที่ 2:</b> เปลี่ยนหารเป็นคูณ กลับเศษเป็นส่วนของตัวหลัง<br>👉 {render_frac(imp_n1, d1)} × {render_frac(d2, imp_n2)}"
                        step2 = f"👉 คำนวณ: ({imp_n1} × {d2}) / ({d1} × {imp_n2}) = {render_frac(res_n, res_d)}"
                        
                    g = math.gcd(abs(res_n), res_d)
                    ans_str = get_mixed(res_n // g, res_d // g)
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (🔥 ชาเลนจ์):</b><br>{step_mixed}{step1}<br>{step2}<br><br><b>ขั้นสุดท้าย:</b> ทอนเป็นเศษส่วนอย่างต่ำหรือจำนวนคละ<br>👉 คำตอบคือ <b><span style='font-size:24px; color:#e74c3c;'>{ans_str}</span></b></span>"
                else:
                    d1, d2 = random.randint(3, 12), random.randint(3, 12)
                    while d1 == d2: d2 = random.randint(3, 12) 
                    n1, n2 = random.randint(1, d1-1), random.randint(1, d2-1)
                    
                    if actual_sub_t in ["การลบเศษส่วน", "การหารเศษส่วน"]:
                        if n1*d2 <= n2*d1: n1, n2, d1, d2 = n2, n1, d2, d1
                            
                    f1_str, f2_str = render_frac(n1, d1), render_frac(n2, d2)
                    q = f"จงหาผลลัพธ์ต่อไปนี้ให้อยู่ในรูปอย่างง่าย<br><br><div style='text-align:center; font-size:24px;'>{f1_str} <span style='color:#e74c3c; margin: 0 10px; font-size:28px; vertical-align:middle;'><b>{op_sign}</b></span> {f2_str} = ?</div>"
                    
                    lcm = (d1 * d2) // math.gcd(d1, d2)
                    if actual_sub_t == "การบวกเศษส่วน":
                        new_n1, new_n2 = n1 * (lcm // d1), n2 * (lcm // d2)
                        res_n, res_d = new_n1 + new_n2, lcm
                        step1 = f"<b>ขั้นที่ 1:</b> หา ค.ร.น. ของส่วน {d1} และ {d2} คือ <b>{lcm}</b>"
                        step2 = f"<b>ขั้นที่ 2:</b> แปลงเศษส่วนให้ส่วนเท่ากัน<br>👉 {render_frac(n1, d1)} = {render_frac(new_n1, lcm)} <br>👉 {render_frac(n2, d2)} = {render_frac(new_n2, lcm)}"
                        step3 = f"<b>ขั้นที่ 3:</b> นำตัวเศษมาบวกกัน: {new_n1} + {new_n2} = {res_n} <br>ได้ผลลัพธ์คือ {render_frac(res_n, lcm)}"
                    elif actual_sub_t == "การลบเศษส่วน":
                        new_n1, new_n2 = n1 * (lcm // d1), n2 * (lcm // d2)
                        res_n, res_d = new_n1 - new_n2, lcm
                        step1 = f"<b>ขั้นที่ 1:</b> หา ค.ร.น. ของส่วน {d1} และ {d2} คือ <b>{lcm}</b>"
                        step2 = f"<b>ขั้นที่ 2:</b> แปลงเศษส่วนให้ส่วนเท่ากัน<br>👉 {render_frac(n1, d1)} = {render_frac(new_n1, lcm)} <br>👉 {render_frac(n2, d2)} = {render_frac(new_n2, lcm)}"
                        step3 = f"<b>ขั้นที่ 3:</b> นำตัวเศษมาลบกัน: {new_n1} - {new_n2} = {res_n} <br>ได้ผลลัพธ์คือ {render_frac(res_n, lcm)}"
                    elif actual_sub_t == "การคูณเศษส่วน":
                        res_n, res_d = n1 * n2, d1 * d2
                        step1 = f"<b>หลักการ:</b> การคูณเศษส่วน ให้นำ (เศษ × เศษ) และ (ส่วน × ส่วน)"
                        step2 = f"<b>ขั้นที่ 1:</b> เข้าสมการ ({n1} × {n2}) / ({d1} × {d2})"
                        step3 = f"<b>ขั้นที่ 2:</b> ได้ผลลัพธ์คือ {render_frac(res_n, res_d)}"
                    elif actual_sub_t == "การหารเศษส่วน":
                        res_n, res_d = n1 * d2, d1 * n2
                        step1 = f"<b>หลักการ:</b> การหารเศษส่วน ให้เปลี่ยนเครื่องหมาย ÷ เป็น × แล้วกลับเศษเป็นส่วนของตัวหาร"
                        step2 = f"<b>ขั้นที่ 1:</b> จะได้ {render_frac(n1, d1)} × {render_frac(d2, n2)}"
                        step3 = f"<b>ขั้นที่ 2:</b> คำนวณ ({n1} × {d2}) / ({d1} × {n2}) = {render_frac(res_n, res_d)}"
                        
                    g = math.gcd(abs(res_n), res_d)
                    ans_str = get_mixed(res_n // g, res_d // g)
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>{step1}<br>{step2}<br>{step3}<br><br><b>ขั้นสุดท้าย:</b> ทอนเป็นเศษส่วนอย่างต่ำ/จำนวนคละ<br>👉 คำตอบคือ <b><span style='font-size:24px; color:#e74c3c;'>{ans_str}</span></b></span>"

            elif actual_sub_t == "การเขียนเศษส่วนในรูปร้อยละ":
                def render_frac(n, d, w=0):
                    frac_html = f"<div style='display:inline-block; vertical-align:middle; text-align:center; margin: 0 5px;'><div style='border-bottom:2px solid #2c3e50; padding:0 4px;'><b>{n}</b></div><div style='padding-top:2px;'><b>{d}</b></div></div>"
                    if w != 0: return f"<div style='display:inline-block; vertical-align:middle;'><span style='font-size:24px; font-weight:bold; color:#2c3e50; margin-right:3px;'>{w}</span>{frac_html}</div>"
                    return frac_html

                if is_challenge:
                    w = random.randint(1, 3)
                    d = random.choice([2, 4, 5, 10, 20, 25])
                    n = random.randint(1, d-1)
                    
                    f_str = render_frac(n, d, w)
                    imp_n = w * d + n
                    m = 100 // d
                    ans = imp_n * m
                    
                    q = f"จงเขียนจำนวนคละต่อไปนี้ให้อยู่ในรูป <b>ร้อยละ (เปอร์เซ็นต์)</b><br><br><div style='text-align:center; font-size:26px;'>{f_str} = <span style='color:#2980b9;'>?</span> %</div>"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (🔥 ชาเลนจ์):</b><br><b>ขั้นที่ 1:</b> แปลงจำนวนคละเป็นเศษเกิน<br>👉 {f_str} = {render_frac(imp_n, d)}<br><br><b>ขั้นที่ 2:</b> ทำตัวส่วนให้เป็น 100 โดยหาตัวเลขมาคูณ<br>👉 พบว่า {d} × <b>{m}</b> = 100 จึงนำ {m} มาคูณทั้งเศษและส่วน<br>👉 ({imp_n} × {m}) / ({d} × {m}) = {render_frac(ans, 100)}<br><br><b>ขั้นที่ 3:</b> เมื่อส่วนเป็น 100 แล้ว ตัวเศษคือค่าร้อยละ<br>👉 ได้ <b>ร้อยละ {ans}</b> หรือ <b>{ans}%</b><br><b>ตอบ: {ans}%</b></span>"
                else:
                    d = random.choice([2, 4, 5, 10, 20, 25, 50])
                    n = random.randint(1, d-1)
                    f_str = render_frac(n, d)
                    m = 100 // d
                    ans = n * m
                    
                    q = f"จงเขียนเศษส่วนต่อไปนี้ให้อยู่ในรูป <b>ร้อยละ (เปอร์เซ็นต์)</b><br><br><div style='text-align:center; font-size:26px;'>{f_str} = <span style='color:#2980b9;'>?</span> %</div>"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br><b>หลักการ:</b> การทำเศษส่วนให้เป็นร้อยละ ต้องทำ <b>'ตัวส่วนให้เท่ากับ 100'</b> เสมอ<br><br><b>ขั้นที่ 1:</b> หาตัวเลขที่คูณกับส่วน {d} แล้วได้ 100<br>👉 พบว่า {d} × <b>{m}</b> = 100<br><br><b>ขั้นที่ 2:</b> นำ {m} มาคูณทั้งเศษและส่วน<br>👉 ({n} × {m}) / ({d} × {m}) = {render_frac(ans, 100)}<br><br><b>ขั้นที่ 3:</b> เมื่อส่วนเป็น 100 แล้ว ตัวเศษคือค่าร้อยละ<br>👉 ได้ <b>ร้อยละ {ans}</b> หรือ <b>{ans}%</b><br><b>ตอบ: {ans}%</b></span>"

            elif actual_sub_t == "การแก้สมการ (คูณ/หาร)":
                def r_frac(num, den):
                    return f"<div style='display:inline-block; vertical-align:middle; text-align:center; margin: 0 5px;'><div style='border-bottom:2px solid #2c3e50; padding:0 4px;'><b>{num}</b></div><div style='padding-top:2px;'><b>{den}</b></div></div>"

                var = random.choice(["x", "y", "a", "m", "k", "p"])
                
                if is_challenge:
                    scenario = random.choice(["distributive", "fractional_coef", "both_sides", "word_problem"])
                    
                    if scenario == "distributive":
                        a = random.randint(2, 6)
                        ans = random.randint(3, 12)
                        b = random.randint(1, 10)
                        is_plus = random.choice([True, False])
                        
                        if is_plus:
                            c = a * (ans + b)
                            q = f"จงหาค่าของ <b>{var}</b> จากสมการ: <br><div style='text-align:center; font-size:24px; margin: 15px 0;'><b>{a}({var} + {b}) = {c}</b></div>"
                            sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (🔥 ชาเลนจ์):</b><br>👉 นำ {a} ที่คูณอยู่หน้าวงเล็บ ย้ายไปหารอีกฝั่ง<br>👉 {var} + {b} = {c} ÷ {a}<br>👉 {var} + {b} = {c//a}<br>👉 ย้าย +{b} ไปลบ<br>👉 {var} = {c//a} - {b}<br>👉 {var} = <b>{ans}</b><br><b>ตอบ: {ans}</b></span>"
                        else:
                            while ans <= b: 
                                ans = random.randint(5, 15)
                                b = random.randint(1, 5)
                            c = a * (ans - b)
                            q = f"จงหาค่าของ <b>{var}</b> จากสมการ: <br><div style='text-align:center; font-size:24px; margin: 15px 0;'><b>{a}({var} - {b}) = {c}</b></div>"
                            sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (🔥 ชาเลนจ์):</b><br>👉 นำ {a} ที่คูณอยู่หน้าวงเล็บ ย้ายไปหารอีกฝั่ง<br>👉 {var} - {b} = {c} ÷ {a}<br>👉 {var} - {b} = {c//a}<br>👉 ย้าย -{b} ไปบวก<br>👉 {var} = {c//a} + {b}<br>👉 {var} = <b>{ans}</b><br><b>ตอบ: {ans}</b></span>"
                            
                    elif scenario == "fractional_coef":
                        a = random.randint(2, 5)
                        b = random.randint(3, 7)
                        while math.gcd(a, b) != 1: b = random.randint(3, 7)
                        ans = b * random.randint(1, 5) 
                        c = random.randint(5, 15)
                        d = (a * ans // b) + c
                        
                        f_html = r_frac(f"{a}{var}", b)
                        q = f"จงหาค่าของ <b>{var}</b> จากสมการ: <br><div style='text-align:center; font-size:24px; margin: 15px 0;'>{f_html} + <b>{c} = {d}</b></div>"
                        
                        sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (🔥 ชาเลนจ์):</b><br>👉 ย้าย +{c} ไปลบอีกฝั่งก่อน<br>👉 {f_html} = {d} - {c}<br>👉 {f_html} = {d-c}<br>👉 ย้าย {b} ที่เป็นตัวส่วน (หารอยู่) ไปคูณ<br>👉 {a}{var} = {d-c} × {b}<br>👉 {a}{var} = {(d-c)*b}<br>👉 ย้าย {a} ไปหาร<br>👉 {var} = {(d-c)*b} ÷ {a}<br>👉 {var} = <b>{ans}</b><br><b>ตอบ: {ans}</b></span>"
                        
                    elif scenario == "both_sides":
                        ans = random.randint(2, 10)
                        c = random.randint(2, 5)
                        a = c + random.randint(1, 4)
                        diff_a = a - c
                        diff_val = diff_a * ans
                        b = random.randint(1, 10)
                        d = diff_val + b
                        
                        q = f"จงหาค่าของ <b>{var}</b> จากสมการ: <br><div style='text-align:center; font-size:24px; margin: 15px 0;'><b>{a}{var} + {b} = {c}{var} + {d}</b></div>"
                        sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (🔥 ชาเลนจ์ - ตัวแปรสองฝั่ง):</b><br>👉 ย้ายตัวแปรให้อยู่ฝั่งเดียวกัน และย้ายตัวเลขไปอีกฝั่ง<br>👉 ย้าย {c}{var} ไปลบ และย้าย +{b} ไปลบอีกฝั่ง<br>👉 {a}{var} - {c}{var} = {d} - {b}<br>👉 {diff_a}{var} = {d-b}<br>👉 {var} = {d-b} ÷ {diff_a}<br>👉 {var} = <b>{ans}</b><br><b>ตอบ: {ans}</b></span>"

                    elif scenario == "word_problem":
                        ans = random.randint(5, 20)
                        mult = random.randint(2, 5)
                        sub = random.randint(2, 10)
                        res = (mult * ans) - sub
                        q = f"<b>{mult} เท่า</b> ของจำนวนจำนวนหนึ่ง หักออกด้วย <b>{sub}</b> จะมีค่าเท่ากับ <b>{res}</b><br>จงหาจำนวนนั้น?"
                        sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (🔥 ชาเลนจ์ - ตีโจทย์ปัญหา):</b><br>👉 กำหนดให้จำนวนนั้นคือ <b>{var}</b><br>👉 สร้างสมการได้เป็น: <b>{mult}{var} - {sub} = {res}</b><br>👉 ย้าย -{sub} ไปบวกอีกฝั่ง: {mult}{var} = {res} + {sub}<br>👉 {mult}{var} = {res+sub}<br>👉 ย้าย {mult} ไปหาร: {var} = {res+sub} ÷ {mult}<br>👉 {var} = <b>{ans}</b><br><b>ตอบ: {ans}</b></span>"

                else:
                    scenario = random.choice(["mult", "div", "mult_add", "div_sub"])
                    if scenario == "mult":
                        a = random.randint(4, 15)
                        ans = random.randint(3, 12)
                        b = a * ans
                        q = f"จงแก้สมการเพื่อหาค่าของ <b>{var}</b>: <br><div style='text-align:center; font-size:24px; margin: 15px 0;'><b>{a}{var} = {b}</b></div>"
                        sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 {a} คูณอยู่กับ {var} จึงย้าย {a} ไปหารอีกฝั่ง<br>👉 {var} = {b} ÷ {a}<br>👉 {var} = <b>{ans}</b><br><b>ตอบ: {ans}</b></span>"
                    elif scenario == "div":
                        a = random.randint(3, 9)
                        ans = random.randint(5, 20)
                        c = a * ans
                        f_html = r_frac(var, a)
                        q = f"จงแก้สมการเพื่อหาค่าของ <b>{var}</b>: <br><div style='text-align:center; font-size:24px; margin: 15px 0;'>{f_html} <b>= {ans}</b></div>"
                        sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 {a} หารอยู่กับ {var} จึงย้าย {a} ไปคูณอีกฝั่ง<br>👉 {var} = {ans} × {a}<br>👉 {var} = <b>{c}</b><br><b>ตอบ: {c}</b></span>"
                    elif scenario == "mult_add":
                        a = random.randint(2, 6)
                        ans = random.randint(3, 10)
                        b = random.randint(1, 15)
                        c = (a * ans) + b
                        q = f"จงแก้สมการเพื่อหาค่าของ <b>{var}</b>: <br><div style='text-align:center; font-size:24px; margin: 15px 0;'><b>{a}{var} + {b} = {c}</b></div>"
                        sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 ย้าย +{b} ไปลบอีกฝั่งก่อน<br>👉 {a}{var} = {c} - {b}<br>👉 {a}{var} = {c-b}<br>👉 ย้าย {a} ที่คูณอยู่ไปหาร<br>👉 {var} = {c-b} ÷ {a}<br>👉 {var} = <b>{ans}</b><br><b>ตอบ: {ans}</b></span>"
                    elif scenario == "div_sub":
                        a = random.randint(2, 6)
                        ans = a * random.randint(4, 12)
                        b = random.randint(1, 10)
                        c = (ans // a) - b
                        while c <= 0:
                            ans = a * random.randint(4, 12)
                            b = random.randint(1, 10)
                            c = (ans // a) - b
                        f_html = r_frac(var, a)
                        q = f"จงแก้สมการเพื่อหาค่าของ <b>{var}</b>: <br><div style='text-align:center; font-size:24px; margin: 15px 0;'>{f_html} - <b>{b} = {c}</b></div>"
                        sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 ย้าย -{b} ไปบวกอีกฝั่งก่อน<br>👉 {f_html} = {c} + {b}<br>👉 {f_html} = {c+b}<br>👉 ย้าย {a} ที่หารอยู่ไปคูณ<br>👉 {var} = {c+b} × {a}<br>👉 {var} = <b>{ans}</b><br><b>ตอบ: {ans}</b></span>"

            elif actual_sub_t == "โจทย์ปัญหา ห.ร.ม. และ ค.ร.น.":
                # --- เครื่องยนต์แสดงวิธีหารสั้นแบบอัตโนมัติ (Visual Short Division Engine) ---
                def prod(lst):
                    p = 1
                    for x in lst: p *= x
                    return p

                def render_short_div(nums, mode="gcd"):
                    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
                    steps = []
                    current_nums = list(nums)
                    divisors = []
                    
                    # หารร่วมทุกตัว (สำหรับ ห.ร.ม. และ ค.ร.น. ขั้นแรก)
                    while True:
                        found = False
                        for p in primes:
                            if all(n % p == 0 for n in current_nums):
                                divisors.append(p)
                                steps.append(list(current_nums))
                                current_nums = [n // p for n in current_nums]
                                found = True
                                break
                        if not found: break
                    
                    # หารร่วมอย่างน้อย 2 ตัว (สำหรับ ค.ร.น. ขั้นที่สอง)
                    if mode == "lcm":
                        while True:
                            found = False
                            for p in primes:
                                if sum(1 for n in current_nums if n % p == 0) >= 2:
                                    divisors.append(p)
                                    steps.append(list(current_nums))
                                    current_nums = [n // p if n % p == 0 else n for n in current_nums]
                                    found = True
                                    break
                            if not found: break
                            
                    # วาด HTML หารสั้น
                    html = "<div style='display:block; text-align:center; margin: 20px 0;'><div style='display:inline-block; text-align:left; font-family:\"Courier New\", Courier, monospace; font-size:20px; background:#f8f9fa; padding:15px 25px; border-radius:8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); border: 1px solid #e0e0e0;'>"
                    for i in range(len(divisors)):
                        html += f"<div style='display: flex; align-items: baseline;'>"
                        html += f"<div style='width: 35px; text-align: right; color: #c0392b; font-weight: bold; padding-right: 12px;'>{divisors[i]}</div>"
                        html += f"<div style='border-left: 2px solid #2c3e50; border-bottom: 2px solid #2c3e50; padding: 4px 15px; display: flex; gap: 20px;'>"
                        for n in steps[i]:
                            html += f"<div style='width: 40px; text-align: center; color: #333;'>{n}</div>"
                        html += "</div></div>"
                        
                    html += f"<div style='display: flex; align-items: baseline;'>"
                    html += f"<div style='width: 35px; text-align: right; padding-right: 12px;'></div>"
                    html += f"<div style='padding: 6px 15px 0px 15px; display: flex; gap: 20px; color: #2980b9; font-weight: bold; border-bottom: 4px double #2980b9;'>"
                    for n in current_nums:
                        html += f"<div style='width: 40px; text-align: center;'>{n}</div>"
                    html += "</div></div></div></div>"
                    
                    return html, divisors, current_nums

                # สุ่มโจทย์ 10 รูปแบบที่ครอบคลุมทุกสนามสอบ
                scenario = random.choice([
                    "gcd_fruit", "gcd_student", "gcd_wire", "gcd_tile", "gcd_fence",
                    "lcm_clock", "lcm_bus", "lcm_run", "lcm_bell", "lcm_med"
                ])

                # ================= หมวด ห.ร.ม. =================
                if scenario.startswith("gcd_"):
                    if scenario == "gcd_fruit":
                        g = random.choice([5, 6, 8, 10, 12, 15, 20])
                        m1, m2, m3 = random.sample([3, 4, 5, 7, 9, 11], 3)
                        a, b, c = g * m1, g * m2, g * m3
                        div_html, divs, rems = render_short_div([a, b, c], "gcd")
                        gcd_val = prod(divs)
                        gcd_exp = " × ".join(map(str, divs))
                        
                        q = f"แม่ค้ามีส้ม <b>{a} ผล</b>, มังคุด <b>{b} ผล</b> และชมพู่ <b>{c} ผล</b><br>ต้องการจัดผลไม้ใส่ถุง ถุงละเท่าๆ กัน โดยไม่ให้ผลไม้ปะปนกันและไม่เหลือเศษ<br>จะจัดผลไม้ได้<b>มากที่สุด</b>ถุงละกี่ผล และจัดได้ทั้งหมดกี่ถุง?"
                        sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (ประยุกต์ ห.ร.ม.):</b><br>👉 คีย์เวิร์ด: 'แบ่งเท่าๆ กัน' และ 'มากที่สุด' = หา <b>ห.ร.ม.</b> ของ {a}, {b}, {c}<br><br><b>ขั้นที่ 1: หา ห.ร.ม. ด้วยการตั้งหารสั้น</b>{div_html}👉 <b>ห.ร.ม.</b> คือการนำ <span style='color:#c0392b;'><b>ตัวหาร (สีแดง)</b></span> มาคูณกัน<br>👉 จะได้ ห.ร.ม. = {gcd_exp} = <b>{gcd_val}</b><br><i>(หมายความว่า: จัดผลไม้ได้มากที่สุดถุงละ <b>{gcd_val} ผล</b>)</i><br><br><b>ขั้นที่ 2: หาจำนวนถุงทั้งหมด</b> (นำผลลัพธ์จากการหารมารวมกัน)<br>👉 ส้มได้ {rems[0]} ถุง, มังคุดได้ {rems[1]} ถุง, ชมพู่ได้ {rems[2]} ถุง<br>👉 รวมทั้งหมด: {rems[0]} + {rems[1]} + {rems[2]} = <b>{sum(rems)} ถุง</b><br><b>ตอบ: ถุงละ {gcd_val} ผล, ได้ทั้งหมด {sum(rems)} ถุง</b></span>"
                        
                    elif scenario == "gcd_student":
                        g = random.choice([12, 15, 18, 20, 24])
                        m1, m2, m3 = random.sample([2, 3, 4, 5, 7], 3)
                        a, b, c = g * m1, g * m2, g * m3
                        div_html, divs, rems = render_short_div([a, b, c], "gcd")
                        gcd_val = prod(divs)
                        gcd_exp = " × ".join(map(str, divs))
                        
                        q = f"โรงเรียนแห่งหนึ่งมีนักเรียนชั้น ป.4 จำนวน <b>{a} คน</b>, ป.5 จำนวน <b>{b} คน</b> และ ป.6 จำนวน <b>{c} คน</b><br>ครูต้องการแบ่งนักเรียนเป็นกลุ่ม กลุ่มละเท่าๆ กัน โดยนักเรียนในแต่ละกลุ่มต้องอยู่ชั้นเดียวกัน<br>จะแบ่งนักเรียนได้กลุ่มละ<b>มากที่สุด</b>กี่คน และได้ทั้งหมดกี่กลุ่ม?"
                        sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (ประยุกต์ ห.ร.ม.):</b><br>👉 คีย์เวิร์ด: 'แบ่งกลุ่มเท่าๆ กัน' และ 'มากที่สุด' = หา <b>ห.ร.ม.</b> ของ {a}, {b}, {c}<br><br><b>ขั้นที่ 1: หา ห.ร.ม. ด้วยการตั้งหารสั้น</b>{div_html}👉 <b>ห.ร.ม.</b> คือการนำ <span style='color:#c0392b;'><b>ตัวหาร (สีแดง)</b></span> มาคูณกัน<br>👉 จะได้ ห.ร.ม. = {gcd_exp} = <b>{gcd_val}</b><br><i>(หมายความว่า: แบ่งนักเรียนได้กลุ่มละมากที่สุด <b>{gcd_val} คน</b>)</i><br><br><b>ขั้นที่ 2: หาจำนวนกลุ่มทั้งหมด</b> (นำผลลัพธ์สุดท้ายมารวมกัน)<br>👉 รวมทั้งหมด: {rems[0]} + {rems[1]} + {rems[2]} = <b>{sum(rems)} กลุ่ม</b><br><b>ตอบ: กลุ่มละ {gcd_val} คน, ได้ทั้งหมด {sum(rems)} กลุ่ม</b></span>"

                    elif scenario == "gcd_wire":
                        g = random.choice([4, 6, 8, 12, 14, 16])
                        m1, m2, m3 = random.sample([3, 5, 7, 9, 11], 3)
                        a, b, c = g * m1, g * m2, g * m3
                        div_html, divs, rems = render_short_div([a, b, c], "gcd")
                        gcd_val = prod(divs)
                        gcd_exp = " × ".join(map(str, divs))
                        
                        q = f"ช่างมีลวดอยู่ 3 เส้น ยาว <b>{a} เมตร</b>, <b>{b} เมตร</b> และ <b>{c} เมตร</b><br>ต้องการตัดลวดให้ยาวเท่าๆ กัน และยาว<b>มากที่สุด</b> โดยไม่เหลือเศษ<br>ช่างจะตัดลวดได้ยาวเส้นละกี่เมตร และได้ลวดทั้งหมดกี่เส้น?"
                        sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (ประยุกต์ ห.ร.ม.):</b><br>👉 คีย์เวิร์ด: 'ตัดเท่าๆ กัน' และ 'ยาวมากที่สุด' = หา <b>ห.ร.ม.</b> ของ {a}, {b}, {c}<br><br><b>ขั้นที่ 1: หา ห.ร.ม. ด้วยการตั้งหารสั้น</b>{div_html}👉 <b>ห.ร.ม.</b> คือการนำ <span style='color:#c0392b;'><b>ตัวหาร (สีแดง)</b></span> มาคูณกัน<br>👉 จะได้ ห.ร.ม. = {gcd_exp} = <b>{gcd_val}</b><br><i>(หมายความว่า: ตัดลวดได้ยาวที่สุดเส้นละ <b>{gcd_val} เมตร</b>)</i><br><br><b>ขั้นที่ 2: หาจำนวนเส้นลวดทั้งหมด</b> (นำผลลัพธ์มารวมกัน)<br>👉 รวมทั้งหมด: {rems[0]} + {rems[1]} + {rems[2]} = <b>{sum(rems)} เส้น</b><br><b>ตอบ: ตัดยาวเส้นละ {gcd_val} เมตร, ได้ทั้งหมด {sum(rems)} เส้น</b></span>"

                    elif scenario == "gcd_tile":
                        g = random.choice([15, 20, 25, 30, 40])
                        m1, m2 = random.choice([(8, 15), (10, 13), (12, 17), (14, 25)])
                        w = g * m1
                        h = g * m2
                        div_html, divs, rems = render_short_div([w, h], "gcd")
                        gcd_val = prod(divs)
                        gcd_exp = " × ".join(map(str, divs))
                        
                        q = f"ห้องโถงรูปสี่เหลี่ยมผืนผ้า กว้าง <b>{w} ซม.</b> ยาว <b>{h} ซม.</b><br>ต้องการปูกระเบื้องรูป<b>สี่เหลี่ยมจัตุรัส</b>ที่มีขนาด<b>ใหญ่ที่สุด</b>ให้เต็มห้องพอดีโดยไม่ต้องตัดกระเบื้อง<br>กระเบื้องแต่ละแผ่นจะมีความยาวด้านละกี่เซนติเมตร และต้องใช้กระเบื้องทั้งหมดกี่แผ่น?"
                        sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (ประยุกต์ ห.ร.ม. ขั้นสูง):</b><br>👉 คีย์เวิร์ด: ปูกระเบื้อง 'จัตุรัส' (ด้านเท่ากัน) ที่ 'ใหญ่ที่สุด' = หา <b>ห.ร.ม.</b> ของ {w} และ {h}<br><br><b>ขั้นที่ 1: หา ห.ร.ม. ด้วยการตั้งหารสั้น</b>{div_html}👉 <b>ห.ร.ม.</b> คือการนำ <span style='color:#c0392b;'><b>ตัวหาร (สีแดง)</b></span> มาคูณกัน<br>👉 จะได้ ห.ร.ม. = {gcd_exp} = <b>{gcd_val}</b><br><i>(หมายความว่า: กระเบื้องต้องยาวด้านละ <b>{gcd_val} ซม.</b>)</i><br><br><b>ขั้นที่ 2: หาจำนวนแผ่นกระเบื้อง</b><br>👉 <i>ระวัง! การหาพื้นที่ต้องนำผลลัพธ์มา 'คูณกัน' ไม่ใช่บวกกัน!</i><br>👉 ด้านกว้างปูได้ {rems[0]} แผ่น, ด้านยาวปูได้ {rems[1]} แผ่น<br>👉 จำนวนแผ่นทั้งหมด = {rems[0]} × {rems[1]} = <b>{rems[0]*rems[1]} แผ่น</b><br><b>ตอบ: ยาวด้านละ {gcd_val} ซม., ใช้ทั้งหมด {rems[0]*rems[1]} แผ่น</b></span>"

                    elif scenario == "gcd_fence":
                        g = random.choice([4, 5, 8, 10, 15])
                        m1, m2 = random.choice([(6, 11), (7, 12), (9, 14), (8, 15)])
                        w = g * m1
                        h = g * m2
                        div_html, divs, rems = render_short_div([w, h], "gcd")
                        gcd_val = prod(divs)
                        gcd_exp = " × ".join(map(str, divs))
                        peri = 2 * (w + h)
                        total_posts = peri // gcd_val
                        
                        q = f"ที่ดินรูปสี่เหลี่ยมผืนผ้า กว้าง <b>{w} เมตร</b> ยาว <b>{h} เมตร</b><br>ต้องการปักเสารั้วล้อมรอบที่ดินให้มีระยะห่างเท่าๆ กัน และห่างกัน<b>มากที่สุด</b> โดยให้มีเสาอยู่ตามมุมทั้งสี่ด้วย<br>จะต้องปักเสาห่างกันกี่เมตร และใช้เสาทั้งหมดกี่ต้น?"
                        sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (🔥 ข้อสอบแข่งขัน):</b><br>👉 คีย์เวิร์ด: 'ห่างเท่าๆ กัน' และ 'มากที่สุด' = หา <b>ห.ร.ม.</b> ของกว้างและยาว<br><br><b>ขั้นที่ 1: หา ห.ร.ม. ด้วยการตั้งหารสั้น</b>{div_html}👉 <b>ห.ร.ม.</b> คือการนำ <span style='color:#c0392b;'><b>ตัวหาร (สีแดง)</b></span> มาคูณกัน<br>👉 จะได้ ห.ร.ม. = {gcd_exp} = <b>{gcd_val}</b><br><i>(หมายความว่า: ต้องปักเสาห่างกันต้นละ <b>{gcd_val} เมตร</b>)</i><br><br><b>ขั้นที่ 2: หาจำนวนเสาทั้งหมด</b><br>👉 หาความยาวรอบรูปที่ดินทั้งหมด: ({w} + {h}) × 2 = {peri} เมตร<br>👉 นำความยาวรอบรูป หารด้วย ระยะห่าง: {peri} ÷ {gcd_val} = <b>{total_posts} ต้น</b><br><b>ตอบ: ห่างกัน {gcd_val} เมตร, ใช้ทั้งหมด {total_posts} ต้น</b></span>"

                # ================= หมวด ค.ร.น. =================
                elif scenario.startswith("lcm_"):
                    sets = [(10, 15, 20), (12, 15, 20), (15, 20, 30), (20, 30, 40), (15, 30, 45), (20, 30, 45), (30, 45, 60), (4, 6, 8), (3, 4, 6)]
                    t_tuple = random.choice(sets)
                    t1, t2, t3 = t_tuple
                    
                    div_html, divs, rems = render_short_div([t1, t2, t3], "lcm")
                    lcm_factors = divs + [x for x in rems if x > 1]
                    if not lcm_factors: lcm_factors = rems 
                    lcm_val = prod(divs) * prod(rems)
                    lcm_exp = " × ".join(map(str, lcm_factors))

                    start_h = random.randint(6, 9)
                    start_m = random.choice([0, 15, 30])
                    add_h, add_m = lcm_val // 60, lcm_val % 60
                    end_h, end_m = start_h + add_h, start_m + add_m
                    if end_m >= 60:
                        end_h += 1; end_m -= 60

                    if scenario == "lcm_clock":
                        q = f"นาฬิกาปลุก 3 เรือน ตั้งเวลาปลุกดังนี้:<br>เรือนแรก ปลุกทุกๆ <b>{t1} นาที</b><br>เรือนที่สอง ปลุกทุกๆ <b>{t2} นาที</b><br>เรือนที่สาม ปลุกทุกๆ <b>{t3} นาที</b><br>ถ้านาฬิกาทั้งสามเรือนปลุกพร้อมกันครั้งแรกเวลา <b>{start_h:02d}:{start_m:02d} น.</b><br>นาฬิกาทั้งสามเรือนจะปลุกพร้อมกันอีกครั้งเวลาใด?"
                        obj_name = "เวลาทั้ง 3 เรือน"
                    elif scenario == "lcm_bus":
                        q = f"รถโดยสาร 3 สาย ออกจากสถานีพร้อมกันเวลา <b>{start_h:02d}:{start_m:02d} น.</b><br>สายที่ 1 ออกทุกๆ <b>{t1} นาที</b><br>สายที่ 2 ออกทุกๆ <b>{t2} นาที</b><br>สายที่ 3 ออกทุกๆ <b>{t3} นาที</b><br>รถโดยสารทั้งสามสายจะออกจากสถานีพร้อมกันอีกครั้งเวลาใด?"
                        obj_name = "เวลารถทั้ง 3 สาย"
                    elif scenario == "lcm_run":
                        q = f"นักกีฬา 3 คน ออกวิ่งจากจุดเริ่มต้นพร้อมกันเวลา <b>{start_h:02d}:{start_m:02d} น.</b><br>คนที่ 1 วิ่งวนรอบสนาม 1 รอบใช้เวลา <b>{t1} นาที</b><br>คนที่ 2 ใช้เวลา <b>{t2} นาที</b><br>คนที่ 3 ใช้เวลา <b>{t3} นาที</b><br>นักกีฬาทั้งสามคนจะวิ่งมาเจอกันที่จุดเริ่มต้นพร้อมกันอีกครั้งเวลาใด?"
                        obj_name = "เวลาวิ่งทั้ง 3 คน"
                    elif scenario == "lcm_bell":
                        q = f"ที่วัดแห่งหนึ่งมีระฆัง 3 ใบ ตีพร้อมกันครั้งแรกเวลา <b>{start_h:02d}:{start_m:02d} น.</b><br>ใบที่ 1 ตีทุกๆ <b>{t1} นาที</b><br>ใบที่ 2 ตีทุกๆ <b>{t2} นาที</b><br>ใบที่ 3 ตีทุกๆ <b>{t3} นาที</b><br>ระฆังทั้งสามใบจะตีดังพร้อมกันอีกครั้งเวลาใด?"
                        obj_name = "เวลาตีระฆังทั้ง 3 ใบ"
                    elif scenario == "lcm_med":
                        q = f"แพทย์สั่งให้ผู้ป่วยทานยา 3 ชนิด ดังนี้:<br>ชนิดที่ 1 ทานทุกๆ <b>{t1} ชั่วโมง</b><br>ชนิดที่ 2 ทานทุกๆ <b>{t2} ชั่วโมง</b><br>ชนิดที่ 3 ทานทุกๆ <b>{t3} ชั่วโมง</b><br>ถ้ารับประทานยาพร้อมกันครั้งแรกเวลา <b>08:00 น.</b><br>ผู้ป่วยจะต้องรับประทานยาทั้ง 3 ชนิดพร้อมกันอีกครั้งในอีกกี่ชั่วโมง?"
                        obj_name = "เวลาทานยาทั้ง 3 ชนิด"

                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (ประยุกต์ ค.ร.น.):</b><br>👉 คีย์เวิร์ด: 'พร้อมกันอีกครั้ง' = หา <b>ค.ร.น.</b> ของ{obj_name}<br><br><b>ขั้นที่ 1: หา ค.ร.น. ด้วยการตั้งหารสั้น</b>{div_html}👉 <b>ค.ร.น.</b> คือการนำ <span style='color:#c0392b;'><b>ตัวหาร (สีแดง)</b></span> และ <span style='color:#2980b9;'><b>ผลลัพธ์สุดท้าย (สีฟ้า)</b></span> มาคูณกัน<br>👉 จะได้ ค.ร.น. = {lcm_exp} = <b>{lcm_val}</b><br><br>"
                    
                    if scenario == "lcm_med":
                        sol += f"<b>ขั้นที่ 2: สรุปคำตอบ</b><br>👉 ผู้ป่วยต้องทานยาพร้อมกันอีกครั้งในอีก <b>{lcm_val} ชั่วโมง</b><br><b>ตอบ: อีก {lcm_val} ชั่วโมง</b></span>"
                    else:
                        sol += f"<b>ขั้นที่ 2: แปลงเวลาและบวกเพิ่ม</b><br>👉 เวลาที่ต้องรอคือ {lcm_val} นาที แปลงเป็น <b>{add_h} ชั่วโมง {add_m} นาที</b><br>👉 เริ่มต้นเวลา {start_h:02d}:{start_m:02d} น. นับบวกเพิ่มไปอีก {add_h} ชม. {add_m} นาที<br>👉 จะได้เป็นเวลา <b>{end_h:02d}:{end_m:02d} น.</b><br><b>ตอบ: {end_h:02d}:{end_m:02d} น.</b></span>"

            elif actual_sub_t == "โจทย์ปัญหาคลาสสิก (สมการประยุกต์)":
                scenario = random.choice(["legs", "age", "coins", "consecutive", "fraction_money"])

                if scenario == "legs":
                    pigs = random.randint(5, 25)
                    chickens = random.randint(10, 35)
                    heads = pigs + chickens
                    legs = (pigs * 4) + (chickens * 2)

                    q = f"ฟาร์มแห่งหนึ่งมี <b>หมู</b> และ <b>ไก่</b> รวมกัน <b>{heads} ตัว</b><br>ถ้านับขาสัตว์รวมกันได้ <b>{legs} ขา</b><br>ฟาร์มแห่งนี้มีหมูกี่ตัว?"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (โจทย์ขาสัตว์):</b><br><br><b>ขั้นที่ 1: สมมติตัวแปร (แยกจำนวนตัว)</b><br>👉 สมมติให้ มีหมูอยู่ <b>x</b> ตัว<br>👉 เนื่องจากมีสัตว์ 2 ชนิดรวมกันทั้งหมด {heads} ตัว <i>(ความหมายคือ: หมู + ไก่ = {heads})</i><br>👉 ถ้าเราอยากรู้จำนวนไก่ เราต้องเอาสัตว์ทั้งหมด <b>หักออก (ลบ)</b> ด้วยจำนวนหมู<br>👉 ดังนั้น จะเหลือไก่ = สัตว์ทั้งหมด - หมู = <b>{heads} - x</b> ตัว<br><br><b>ขั้นที่ 2: เปลี่ยน 'จำนวนตัว' ให้เป็น 'จำนวนขา'</b><br>👉 หมู 1 ตัว มี 4 ขา ดังนั้น หมู x ตัว จะมีขารวม <b>4 คูณ x = 4x ขา</b><br>👉 ไก่ 1 ตัว มี 2 ขา ดังนั้น ไก่ ({heads} - x) ตัว จะมีขารวม <b>2 คูณ ({heads} - x) = 2({heads} - x) ขา</b><br><br><b>ขั้นที่ 3: สร้างสมการจากขารวม</b><br>👉 ขาหมู + ขาไก่ = {legs} ขา<br>👉 <b>4x + 2({heads} - x) = {legs}</b><br><br><b>ขั้นที่ 4: แก้สมการ</b><br>👉 4x + {heads*2} - 2x = {legs} <i>(นำ 2 กระจายคูณเข้าไปในวงเล็บ)</i><br>👉 2x + {heads*2} = {legs}<br>👉 2x = {legs} - {heads*2}<br>👉 2x = {legs - (heads*2)}<br>👉 x = {(legs - (heads*2))} ÷ 2<br>👉 x = <b>{pigs}</b><br><br><b>ตอบ: ฟาร์มนี้มีหมู {pigs} ตัว</b></span>"

                elif scenario == "age":
                    son_now = random.randint(8, 15)
                    future_y = random.randint(3, 10)
                    son_future = son_now + future_y
                    M = random.choice([2, 3]) 
                    dad_future = son_future * M
                    dad_now = dad_future - future_y
                    diff = dad_now - son_now

                    q = f"ปัจจุบัน พ่อมีอายุมากกว่าลูก <b>{diff} ปี</b><br>อีก <b>{future_y} ปีข้างหน้า</b> พ่อจะมีอายุเป็น <b>{M} เท่า</b> ของลูก<br>ปัจจุบันลูกอายุเท่าไหร่?"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (โจทย์อายุ):</b><br>👉 กำหนดให้ ปัจจุบันลูกอายุ <b>x</b> ปี<br>👉 ปัจจุบันพ่ออายุมากกว่าลูก {diff} ปี ดังนั้นพ่ออายุ <b>x + {diff}</b> ปี<br><br><b>ขั้นที่ 1: วิเคราะห์อายุในอีก {future_y} ปีข้างหน้า</b><br>👉 ลูกจะอายุ: x + {future_y} ปี<br>👉 พ่อจะอายุ: (x + {diff}) + {future_y} = x + {diff + future_y} ปี<br><br><b>ขั้นที่ 2: สร้างสมการ</b> (พ่อจะเป็น {M} เท่าของลูก)<br>👉 อายุพ่ออนาคต = {M} × อายุลูกอนาคต<br>👉 x + {diff + future_y} = {M}(x + {future_y})<br><br><b>ขั้นที่ 3: แก้สมการ</b><br>👉 x + {diff + future_y} = {M}x + {M * future_y}<br>👉 ย้ายตัวแปร x ไปฝั่งเดียวกัน: {diff + future_y} - {M * future_y} = {M}x - x<br>👉 {diff + future_y - (M * future_y)} = {(M-1)}x<br>👉 x = {diff + future_y - (M * future_y)} ÷ {(M-1)}<br>👉 x = <b>{son_now}</b><br><br><b>ตอบ: ปัจจุบันลูกอายุ {son_now} ปี</b></span>"

                elif scenario == "coins":
                    c10 = random.randint(5, 20)
                    c5 = random.randint(8, 25)
                    total_coins = c10 + c5
                    total_val = (c10 * 10) + (c5 * 5)

                    q = f"กระปุกออมสินมี <b>เหรียญสิบบาท</b> และ <b>เหรียญห้าบาท</b> รวมกัน <b>{total_coins} เหรียญ</b><br>เมื่อนำเงินมานับรวมกันได้ทั้งหมด <b>{total_val} บาท</b><br>กระปุกออมสินนี้มีเหรียญสิบบาทกี่เหรียญ?"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (โจทย์นับเหรียญ):</b><br><br><b>ขั้นที่ 1: กำหนดตัวแปร (แยกจำนวนเหรียญก่อน)</b><br>👉 สมมติให้มี เหรียญสิบบาท อยู่ <b>x</b> เหรียญ<br>👉 เนื่องจากในกระปุกมีเหรียญ 2 ชนิดรวมกันทั้งหมด {total_coins} เหรียญ <i>(ความหมายคือ: เหรียญ 10 + เหรียญ 5 = {total_coins})</i><br>👉 ถ้าเราอยากรู้จำนวนเหรียญ 5 บาท เราต้องเอาเหรียญทั้งหมด <b>หักออก (ลบ)</b> ด้วยจำนวนเหรียญ 10 บาท<br>👉 ดังนั้น จะมีเหรียญห้าบาท = เหรียญทั้งหมด - เหรียญสิบ = <b>{total_coins} - x</b> เหรียญ<br><br><b>ขั้นที่ 2: เปลี่ยน 'จำนวนเหรียญ' ให้เป็น 'มูลค่าเงิน (บาท)'</b><br>👉 เหรียญ 10 บาท จำนวน x เหรียญ คิดเป็นเงิน <b>10 คูณ x = 10x บาท</b><br>👉 เหรียญ 5 บาท จำนวน ({total_coins} - x) เหรียญ คิดเป็นเงิน <b>5 คูณ ({total_coins} - x) = 5({total_coins} - x) บาท</b><br><br><b>ขั้นที่ 3: สร้างสมการจากมูลค่าเงินรวม</b><br>👉 เงินจากเหรียญสิบ + เงินจากเหรียญห้า = {total_val} บาท<br>👉 <b>10x + 5({total_coins} - x) = {total_val}</b><br><br><b>ขั้นที่ 4: แก้สมการ</b><br>👉 10x + {total_coins*5} - 5x = {total_val} <i>(นำ 5 กระจายคูณเข้าไปในวงเล็บ)</i><br>👉 5x + {total_coins*5} = {total_val}<br>👉 5x = {total_val} - {total_coins*5}<br>👉 5x = {total_val - (total_coins*5)}<br>👉 x = {(total_val - (total_coins*5))} ÷ 5<br>👉 x = <b>{c10}</b><br><br><b>ตอบ: มีเหรียญสิบบาททั้งหมด {c10} เหรียญ</b></span>"

                elif scenario == "consecutive":
                    ctype = random.choice(["ธรรมดา", "คู่", "คี่"])
                    if ctype == "ธรรมดา":
                        start = random.randint(10, 50)
                        ans = start + 2 
                        total = start + (start+1) + (start+2)
                        q = f"ผลบวกของ<b>จำนวนเต็มเรียงติดกัน 3 จำนวน</b> เท่ากับ <b>{total}</b><br>จงหาจำนวนที่<b>มากที่สุด</b>?"
                        sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (จำนวนเรียงติดกัน):</b><br>👉 กำหนดให้จำนวนที่น้อยที่สุดคือ <b>x</b><br>👉 จำนวนถัดไปคือ <b>x + 1</b> และ <b>x + 2</b><br><br><b>ขั้นที่ 1: สร้างสมการ</b><br>👉 x + (x + 1) + (x + 2) = {total}<br>👉 3x + 3 = {total}<br><br><b>ขั้นที่ 2: แก้สมการ</b><br>👉 3x = {total} - 3<br>👉 3x = {total-3}<br>👉 x = {(total-3)} ÷ 3 = <b>{start}</b><br><br><b>ขั้นที่ 3: สรุปหาจำนวนที่มากที่สุด</b><br>👉 จากขั้นที่ 2 เราหาค่า x ได้ <b>{start}</b> ซึ่งก็คือ 'จำนวนที่น้อยที่สุด' <br>👉 เรามาลองเขียนไล่ลำดับจำนวนทั้ง 3 จำนวน จะได้: <b>{start}</b>, <b>{start+1}</b>, และ <b>{start+2}</b><br>👉 จะเห็นได้ชัดเจนว่า จำนวนที่มากที่สุด (ตัวที่สาม) ก็คือ <b>{ans}</b><br><b>ตอบ: {ans}</b></span>"
                    else:
                        start = random.randint(10, 40) * 2
                        if ctype == "คี่": start += 1
                        ans = start + 4
                        total = start + (start+2) + (start+4)
                        q = f"ผลบวกของ<b>จำนวน{ctype}เรียงติดกัน 3 จำนวน</b> เท่ากับ <b>{total}</b><br>จงหาจำนวนที่<b>มากที่สุด</b>?"
                        sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (จำนวน{ctype}เรียงติดกัน):</b><br>👉 <i>ข้อควรระวัง: จำนวน{ctype}เรียงติดกัน จะห่างกันทีละ 2</i><br>👉 กำหนดให้จำนวนที่น้อยที่สุดคือ <b>x</b><br>👉 จำนวนถัดไปคือ <b>x + 2</b> และ <b>x + 4</b><br><br><b>ขั้นที่ 1: สร้างสมการ</b><br>👉 x + (x + 2) + (x + 4) = {total}<br>👉 3x + 6 = {total}<br><br><b>ขั้นที่ 2: แก้สมการ</b><br>👉 3x = {total} - 6<br>👉 3x = {total-6}<br>👉 x = {(total-6)} ÷ 3 = <b>{start}</b><br><br><b>ขั้นที่ 3: สรุปหาจำนวนที่มากที่สุด</b><br>👉 จากขั้นที่ 2 เราหาค่า x ได้ <b>{start}</b> ซึ่งก็คือ 'จำนวน{ctype}ที่น้อยที่สุด' <br>👉 เรามาลองเขียนไล่ลำดับจำนวนทั้ง 3 จำนวน จะได้: <b>{start}</b>, <b>{start+2}</b>, และ <b>{start+4}</b><br>👉 จะเห็นได้ชัดเจนว่า จำนวนที่มากที่สุด (ตัวที่สาม) ก็คือ <b>{ans}</b><br><b>ตอบ: {ans}</b></span>"

                elif scenario == "fraction_money":
                    d1 = random.choice([3, 4, 5])
                    d2 = random.choice([4, 5, 6])
                    while d1 == d2: d2 = random.choice([4, 5, 6])
                    lcm = (d1 * d2) // math.gcd(d1, d2)
                    
                    n1, n2 = 1, 1
                    while (n1*lcm//d1) + (n2*lcm//d2) >= lcm:
                        d1, d2 = 4, 5 
                        lcm = 20
                        
                    used_frac_n = (n1*lcm//d1) + (n2*lcm//d2)
                    rem_frac_n = lcm - used_frac_n
                    
                    ans = random.randint(5, 15) * 100 * lcm 
                    rem_money = ans * rem_frac_n // lcm
                    
                    m1_list = [d1 * i for i in range(1, (lcm//d1) + 1)]
                    m2_list = [d2 * i for i in range(1, (lcm//d2) + 1)]
                    lcm_explain = f"<br><span style='color:#7f8c8d; font-size:15px;'><i>&nbsp;&nbsp;&nbsp;&nbsp;(วิธีหา ค.ร.น. แบบง่ายๆ คือไล่สูตรคูณหาตัวเลขที่ซ้ำกันตัวแรก:<br>&nbsp;&nbsp;&nbsp;&nbsp;แม่ {d1} : {', '.join(map(str, m1_list))} <br>&nbsp;&nbsp;&nbsp;&nbsp;แม่ {d2} : {', '.join(map(str, m2_list))} <br>&nbsp;&nbsp;&nbsp;&nbsp;เจอเลข <b>{lcm}</b> ซ้ำกันเป็นตัวแรก ดังนั้น ค.ร.น. คือ {lcm})</i></span>"
                    
                    f_norm1 = f"<div style='display:inline-block; vertical-align:middle; text-align:center; margin: 0 5px;'><div style='border-bottom:2px solid #2c3e50; padding:0 4px;'><b>{lcm}x</b></div><div style='padding-top:2px;'><b>{d1}</b></div></div>"
                    f_norm2 = f"<div style='display:inline-block; vertical-align:middle; text-align:center; margin: 0 5px;'><div style='border-bottom:2px solid #2c3e50; padding:0 4px;'><b>{lcm}x</b></div><div style='padding-top:2px;'><b>{d2}</b></div></div>"
                    
                    f_canc1 = f"<div style='display:inline-block; vertical-align:middle; text-align:center; margin: 0 5px;'><div style='border-bottom:2px solid #2c3e50; padding:0 4px;'><b><s style='color:#e74c3c;'>{lcm}</s><sup style='color:#27ae60; font-size:14px; margin-left:3px;'>{lcm//d1}</sup>x</b></div><div style='padding-top:2px;'><b><s style='color:#e74c3c;'>{d1}</s><sub style='color:#27ae60; font-size:12px; margin-left:3px;'>1</sub></b></div></div>"
                    f_canc2 = f"<div style='display:inline-block; vertical-align:middle; text-align:center; margin: 0 5px;'><div style='border-bottom:2px solid #2c3e50; padding:0 4px;'><b><s style='color:#e74c3c;'>{lcm}</s><sup style='color:#27ae60; font-size:14px; margin-left:3px;'>{lcm//d2}</sup>x</b></div><div style='padding-top:2px;'><b><s style='color:#e74c3c;'>{d2}</s><sub style='color:#27ae60; font-size:12px; margin-left:3px;'>1</sub></b></div></div>"
                    
                    q = f"สมชายใช้เงินซื้อหนังสือไป <b>1/{d1} ของเงินทั้งหมด</b> และซื้อขนมไปอีก <b>1/{d2} ของเงินทั้งหมด</b><br>ปรากฏว่าสมชายยังเหลือเงินอยู่ <b>{rem_money:,} บาท</b><br>เดิมสมชายมีเงินทั้งหมดกี่บาท?"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (โจทย์สมการเศษส่วน):</b><br>👉 กำหนดให้เดิมสมชายมีเงินทั้งหมด <b>x</b> บาท<br>👉 ซื้อหนังสือ: x/{d1} บาท, ซื้อขนม: x/{d2} บาท<br><br><b>ขั้นที่ 1: สร้างสมการ</b><br>👉 เงินทั้งหมด - หนังสือ - ขนม = เงินที่เหลือ<br>👉 x - (x/{d1}) - (x/{d2}) = {rem_money:,}<br><br><b>ขั้นที่ 2: แก้สมการโดยหา ค.ร.น.</b><br>👉 ค.ร.น. ของส่วน {d1} และ {d2} คือ <b>{lcm}</b> {lcm_explain}<br><br>👉 นำ ค.ร.น. ({lcm}) คูณกระจายเข้าไปใน <b>ทุกๆ จำนวน</b> ของสมการ:<br><div style='margin: 12px 0;'>👉 <b>({lcm} × x) - {f_norm1} - {f_norm2} = {rem_money:,} × {lcm}</b></div>👉 นำตัวส่วนไปตัดทอนกับ {lcm} ให้กลายเป็นจำนวนเต็ม:<br><div style='margin: 12px 0;'>👉 <b>{lcm}x - {f_canc1} - {f_canc2} = {rem_money * lcm:,}</b></div>👉 จะได้สมการใหม่ที่ไม่มีเศษส่วนกวนใจแล้ว:<br>👉 <b>{lcm}x - {lcm//d1}x - {lcm//d2}x = {rem_money * lcm:,}</b><br><br><div style='background-color:#fef9e7; padding:10px; border-radius:5px; border-left: 4px solid #f39c12; margin: 10px 0;'><span style='color:#d35400; font-size:15px;'><i><b>💡 ทำไมบรรทัดต่อไปถึงเหลือ x เดียว? (สมบัติการแจกแจง / ดึงตัวร่วม)</b><br>สังเกตว่าทุกจำนวนมี <b>x</b> เกาะอยู่เหมือนกันหมด เราจึงสามารถดึง <b>x</b> ออกมาเป็นตัวแทนไว้ข้างนอกวงเล็บได้!<br>เปรียบเทียบให้เห็นภาพ: มีเงิน {lcm} บาท จ่ายไป {lcm//d1} บาท และจ่ายอีก {lcm//d2} บาท<br>ก็คือเอาตัวเลขมาหักลบกันก่อน <b>({lcm} - {lcm//d1} - {lcm//d2})</b> แล้วค่อยแปะคำว่า <b>x (แทนหน่วยบาท)</b> ไว้ข้างหลังครับ!</i></span></div>👉 <b>({lcm} - {lcm//d1} - {lcm//d2})x = {rem_money * lcm:,}</b><br>👉 <b>{rem_frac_n}x = {rem_money * lcm:,}</b><br>👉 x = {rem_money * lcm:,} ÷ {rem_frac_n} = <b>{ans:,}</b><br><br><b>ตอบ: เดิมสมชายมีเงิน {ans:,} บาท</b></span>"

            elif actual_sub_t == "แบบรูปและอนุกรม (Number Patterns)":
                scenario = random.choice(["increasing_diff", "fibonacci", "telescoping", "alternating", "perfect_square"])
                
                def f_html(n, d): return f"<div style='display:inline-block; vertical-align:middle; text-align:center; margin: 0 2px;'><div style='border-bottom:1px solid #2c3e50; padding:0 2px; font-size:15px;'><b>{n}</b></div><div style='padding-top:1px; font-size:15px;'><b>{d}</b></div></div>"
                def f_canc(n, d): return f"<div style='display:inline-block; vertical-align:middle; text-align:center; margin: 0 2px;'><div style='border-bottom:1px solid #e74c3c; padding:0 2px; font-size:15px;'><s style='color:#e74c3c; opacity:0.6;'><span style='color:#2c3e50;'><b>{n}</b></span></s></div><div style='padding-top:1px; font-size:15px;'><s style='color:#e74c3c; opacity:0.6;'><span style='color:#2c3e50;'><b>{d}</b></span></s></div></div>"

                if scenario == "increasing_diff":
                    start = random.randint(1, 10)
                    diff_start = random.choice([2, 3, 4])
                    diff_step = random.choice([1, 2])
                    
                    seq = [start]
                    diffs = []
                    cur = start
                    cur_diff = diff_start
                    
                    for _ in range(5):
                        cur += cur_diff
                        seq.append(cur)
                        diffs.append(cur_diff)
                        cur_diff += diff_step
                        
                    ans = seq[-1]
                    given_seq = seq[:-1]
                    
                    q = f"จากแบบรูปของจำนวนที่กำหนดให้:<br><div style='font-size:22px; margin:15px 0; color:#c0392b;'><b>{', '.join(map(str, given_seq))}, ...</b></div>จงหาจำนวนถัดไป?"
                    
                    relation_html = "<div style='font-family: monospace; font-size: 16px;'>"
                    relation_html += " &nbsp;&nbsp;&nbsp; ".join([f"<b>{x}</b>" for x in seq]) + "<br>"
                    relation_html += "&nbsp;&nbsp;&nbsp;".join([f"<span style='color:#2980b9;'>+{d}</span>&nbsp;&nbsp;" for d in diffs])
                    relation_html += "</div>"

                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (หาความสัมพันธ์):</b><br>👉 ให้เราลองหาผลต่าง (ระยะห่าง) ของตัวเลขแต่ละคู่ที่อยู่ติดกันดูครับ<br><br><div style='background:#f8f9fa; padding:10px; border-radius:5px; margin: 10px 0;'>{relation_html}</div>👉 จะสังเกตเห็นว่า ระยะห่างมันไม่ได้เพิ่มขึ้นแบบคงที่ แต่มัน **เพิ่มขึ้นทีละ {diff_step}** (จาก +{diffs[0]} เป็น +{diffs[1]}, +{diffs[2]}, ...)<br>👉 ดังนั้น ระยะห่างตัวสุดท้ายที่จะนำไปบวกคือ <b>+{diffs[-1]}</b><br>👉 นำตัวเลขล่าสุดมาบวกกับระยะห่าง: {given_seq[-1]} + {diffs[-1]} = <b>{ans}</b><br><br><b>ตอบ: {ans}</b></span>"

                elif scenario == "fibonacci":
                    a = random.randint(1, 3)
                    b = random.randint(1, 5)
                    seq = [a, b]
                    for _ in range(5):
                        seq.append(seq[-1] + seq[-2])
                        
                    ans = seq[-1]
                    given_seq = seq[:-1]
                    
                    q = f"จากแบบรูปของจำนวนที่กำหนดให้:<br><div style='font-size:22px; margin:15px 0; color:#c0392b;'><b>{', '.join(map(str, given_seq))}, ...</b></div>จงหาจำนวนถัดไป?"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (อนุกรมสะสม):</b><br>👉 ข้อนี้ถ้าน้องๆ ลองหาระยะห่างดู จะพบว่ามันไม่มีกฎเกณฑ์ที่ชัดเจนครับ<br>👉 ให้ลองสังเกตความสัมพันธ์แบบ **'นำตัวเลข 2 ตัวหน้า มาบวกกัน จะได้ตัวเลขถัดไป'** เสมอ!<br><br><b>ลองพิสูจน์ดู:</b><br>👉 {seq[0]} + {seq[1]} = <b>{seq[2]}</b><br>👉 {seq[1]} + {seq[2]} = <b>{seq[3]}</b><br>👉 {seq[2]} + {seq[3]} = <b>{seq[4]}</b><br><br><b>ขั้นสุดท้าย: หาคำตอบ</b><br>👉 นำตัวเลข 2 ตัวสุดท้ายมาบวกกัน: {given_seq[-2]} + {given_seq[-1]} = <b>{ans}</b><br><b>ตอบ: {ans}</b></span>"

                elif scenario == "telescoping":
                    end_n = random.choice([20, 30, 40, 50, 99])
                    
                    term1 = f_html(1, "1×2")
                    term2 = f_html(1, "2×3")
                    term3 = f_html(1, "3×4")
                    term_n = f_html(1, f"{end_n}×{end_n+1}")
                    
                    q = f"จงหาผลบวกของอนุกรมเศษส่วนต่อไปนี้:<br><br><div style='font-size:20px; text-align:center;'>{term1} + {term2} + {term3} + ... + {term_n} = ?</div>"
                    
                    t1_split = f"({f_html(1,1)} - {f_html(1,2)})"
                    t2_split = f"({f_html(1,2)} - {f_html(1,3)})"
                    t3_split = f"({f_html(1,3)} - {f_html(1,4)})"
                    tn_split = f"({f_html(1,end_n)} - {f_html(1,end_n+1)})"
                    
                    cancel_view = f"<div style='margin:15px 0; font-size:18px;'>= {f_html(1,1)} <span style='color:#e74c3c;'><b>- {f_canc(1,2)} + {f_canc(1,2)}</b></span> <span style='color:#e74c3c;'><b>- {f_canc(1,3)} + {f_canc(1,3)}</b></span> - ... + <span style='color:#e74c3c;'><b>{f_canc(1,end_n)}</b></span> - {f_html(1,end_n+1)}</div>"
                    
                    ans_n = end_n
                    ans_d = end_n + 1
                    ans_html = f_html(ans_n, ans_d)

                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (🔥 เทคนิคเศษส่วนต่อเนื่อง / Telescoping):</b><br>👉 ถ้าน้องๆ มัวแต่หา ค.ร.น. ข้อนี้ทำทั้งวันก็ไม่เสร็จครับ! เราต้องใช้เทคนิค <b>'การแยกเศษส่วน'</b><br><br><b>ขั้นที่ 1: แปลงร่างเศษส่วน</b><br>สังเกตว่าตัวส่วนเป็นตัวเลขเรียงติดกันคูณกัน เราสามารถจับแยกเป็น 2 ก้อนลบกันได้เสมอ ดังนี้:<br>👉 {term1} แยกได้เป็น {t1_split}<br>👉 {term2} แยกได้เป็น {t2_split}<br>👉 ...ไปเรื่อยๆ จนถึงตัวสุดท้าย...<br>👉 {term_n} แยกได้เป็น {tn_split}<br><br><b>ขั้นที่ 2: นำมาเขียนเรียงต่อกันแล้วสังเกตความวิเศษ!</b><br>เมื่อเราเอาวงเล็บออก จะเกิดการ <b>'ตัดกันเอง'</b> ของตัวเลขตรงกลาง (ตัวติดลบเจอตัวบวก หักล้างกันกลายเป็นศูนย์)<br>{cancel_view}👉 จะเห็นว่าตัวเลขตรงกลางโดน <span style='color:#e74c3c;'><b>ขีดฆ่าตายเรียบ!</b></span> เหลือรอดแค่ <b>'หัวตัวแรก'</b> กับ <b>'หางตัวสุดท้าย'</b> เท่านั้น!<br><br><b>ขั้นที่ 3: คำนวณคำตอบสุดท้าย</b><br>👉 เหลือแค่: {f_html(1,1)} - {f_html(1,end_n+1)}<br>👉 แปลงร่าง 1 ให้ส่วนเท่ากัน: {f_html(end_n+1, end_n+1)} - {f_html(1, end_n+1)}<br>👉 นำเศษมาลบกัน: {ans_html}<br><br><b>ตอบ: {ans_n}/{ans_d}</b></span>"

                elif scenario == "alternating":
                    # อนุกรมสลับ (2 ชุดซ้อนกัน)
                    start1 = random.randint(2, 5)
                    step1 = random.randint(2, 4)
                    start2 = random.randint(20, 30)
                    step2 = random.randint(1, 3)
                    
                    seq1 = [start1 + (i*step1) for i in range(4)]
                    seq2 = [start2 - (i*step2) for i in range(4)]
                    
                    # สลับตัวเลข
                    mixed_seq = []
                    for i in range(4):
                        mixed_seq.append(seq1[i])
                        mixed_seq.append(seq2[i])
                        
                    ans = mixed_seq[6] # ถามตัวที่ 7 (อยู่ในชุดที่ 1)
                    given_seq = mixed_seq[:6]
                    
                    q = f"จากแบบรูปของจำนวนที่กำหนดให้:<br><div style='font-size:22px; margin:15px 0; color:#c0392b;'><b>{', '.join(map(str, given_seq))}, ...</b></div>จงหาจำนวนถัดไป?"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (🔥 อนุกรมสลับซ้อนกัน):</b><br>👉 ข้อนี้ดูเผินๆ เหมือนตัวเลขเดี๋ยวเพิ่มเดี๋ยวลด ไม่มีกฎเกณฑ์ที่แน่นอน<br>👉 <b>ความลับคือ:</b> มีอนุกรม 2 ชุดซ่อนสลับกันอยู่! ให้เราลองมอง <b>'ข้ามกระโดดทีละ 1 ตัว'</b> ดูครับ<br><br><b>แยกอนุกรมออกเป็น 2 ชุด:</b><br>🔹 <b>ชุดที่ 1 (ตัวคี่):</b> {seq1[0]}, {seq1[1]}, {seq1[2]}, <b>...ตัวที่กำลังหา...</b><br><i>(สังเกตว่า: บวกเพิ่มทีละ {step1})</i><br>🔸 <b>ชุดที่ 2 (ตัวคู่):</b> {seq2[0]}, {seq2[1]}, {seq2[2]}<br><i>(สังเกตว่า: ลบออกทีละ {step2})</i><br><br><b>ขั้นสุดท้าย: หาคำตอบ</b><br>👉 ตำแหน่งที่เราต้องการหา คือตัวถัดไปของ <b>ชุดที่ 1</b><br>👉 นำตัวสุดท้ายของชุดที่ 1 มาบวกเพิ่ม: {seq1[2]} + {step1} = <b>{ans}</b><br><b>ตอบ: {ans}</b></span>"

                elif scenario == "perfect_square":
                    # อนุกรมยกกำลังสอง (Perfect Squares)
                    start_base = random.randint(1, 4)
                    bases = [start_base + i for i in range(6)]
                    seq = [b**2 for b in bases]
                    ans = seq[-1]
                    given_seq = seq[:-1]
                    
                    q = f"จากแบบรูปของจำนวนที่กำหนดให้:<br><div style='font-size:22px; margin:15px 0; color:#c0392b;'><b>{', '.join(map(str, given_seq))}, ...</b></div>จงหาจำนวนถัดไป?"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (อนุกรมกำลังสอง):</b><br>👉 ข้อนี้ถ้าลองหาระยะห่าง จะพบว่ามันเพิ่มขึ้นทีละเลขคี่ (ตัวอย่าง: ลองลบกันดูจะได้ระยะห่างไม่เท่ากัน)<br>👉 แต่ถ้าเราแม่นสูตรคูณ เราจะสังเกตเห็นความน่าสนใจของตัวเลขกลุ่มนี้ครับ!<br><br><b>ลองแยกตัวประกอบดู:</b><br>👉 {seq[0]} เกิดจาก <b>{bases[0]} × {bases[0]}</b><br>👉 {seq[1]} เกิดจาก <b>{bases[1]} × {bases[1]}</b><br>👉 {seq[2]} เกิดจาก <b>{bases[2]} × {bases[2]}</b><br>👉 {seq[3]} เกิดจาก <b>{bases[3]} × {bases[3]}</b><br>👉 {seq[4]} เกิดจาก <b>{bases[4]} × {bases[4]}</b><br><br><b>ขั้นสุดท้าย: หาคำตอบ</b><br>👉 จะเห็นว่ามันคือตัวเลขเรียงติดกันคูณด้วยตัวมันเอง (ยกกำลังสอง)<br>👉 ดังนั้น ตัวถัดไปต้องเป็น <b>{bases[5]} × {bases[5]} = {ans}</b><br><b>ตอบ: {ans}</b></span>"

            elif actual_sub_t == "มาตราส่วนและทิศทาง":
                scenario = random.choice(["map_to_real", "real_to_map", "map_area", "find_scale"])
                
                if scenario == "map_to_real":
                    scale_km = random.choice([5, 10, 20, 25, 50, 100])
                    map_cm_base = random.randint(2, 15)
                    has_decimal = random.choice([True, False])
                    if has_decimal: 
                        map_cm = map_cm_base + 0.5
                        map_str = f"{map_cm:.1f}"
                    else: 
                        map_cm = map_cm_base
                        map_str = f"{map_cm}"
                        
                    ans = map_cm * scale_km
                    ans_str = f"{ans:g}" 
                    
                    q = f"แผนที่ฉบับหนึ่งกำหนดมาตราส่วน <b>1 ซม. : {scale_km} กม.</b><br>ถ้าวัดระยะทางจากเมือง A ไปเมือง B ในแผนที่ได้ <b>{map_str} เซนติเมตร</b><br>ระยะทางจริงจากเมือง A ไปเมือง B คือกี่กิโลเมตร?"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (การอ่านมาตราส่วนแผนที่):</b><br>👉 มาตราส่วน 1 ซม. : {scale_km} กม. หมายความว่า <b>'ระยะทางในกระดาษ 1 ซม. เท่ากับระยะทางจริง {scale_km} กิโลเมตร'</b><br><br><b>ขั้นที่ 1: เทียบบัญญัติไตรยางศ์</b><br>👉 แผนที่ 1 ซม. = ของจริง {scale_km} กม.<br>👉 แผนที่ {map_str} ซม. = ของจริง {map_str} × {scale_km} กม.<br><br><b>ขั้นที่ 2: คำนวณคำตอบ</b><br>👉 {map_str} × {scale_km} = <b>{ans_str} กิโลเมตร</b><br><b>ตอบ: {ans_str} กิโลเมตร</b></span>"
                    
                elif scenario == "real_to_map":
                    scale_m = random.choice([10, 20, 50, 100, 200])
                    map_ans_cm = random.randint(3, 12)
                    has_decimal = random.choice([True, False])
                    if has_decimal: map_ans_cm += 0.5
                    real_m = map_ans_cm * scale_m
                    real_str = f"{real_m:g}"
                    map_str = f"{map_ans_cm:g}"
                    
                    q = f"แผนผังหมู่บ้านแห่งหนึ่งใช้มาตราส่วน <b>1 ซม. : {scale_m} เมตร</b><br>ถ้าระยะทางจริงจากหน้าหมู่บ้านถึงสวนสาธารณะคือ <b>{real_str} เมตร</b><br>ในแผนผังนี้ ระยะทางดังกล่าวจะมีความยาวกี่เซนติเมตร?"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (แปลงระยะจริงลงในแผนผัง):</b><br>👉 มาตราส่วน 1 ซม. : {scale_m} เมตร หมายความว่า <b>'ระยะทางจริงทุกๆ {scale_m} เมตร จะวาดลงในกระดาษ 1 เซนติเมตร'</b><br><br><b>ขั้นที่ 1: เทียบบัญญัติไตรยางศ์ (คิดย้อนกลับ)</b><br>👉 ระยะจริง {scale_m} เมตร = วาดในแผนผัง 1 ซม.<br>👉 ระยะจริง {real_str} เมตร = นำไปหารด้วย {scale_m} เพื่อดูว่าจะได้กระดาษกี่เซนติเมตร<br><br><b>ขั้นที่ 2: คำนวณคำตอบ</b><br>👉 วาดในแผนผัง = {real_str} ÷ {scale_m}<br>👉 วาดในแผนผัง = <b>{map_str} เซนติเมตร</b><br><b>ตอบ: {map_str} เซนติเมตร</b></span>"

                elif scenario == "map_area":
                    scale_m = random.choice([5, 10, 20, 50])
                    w_cm = random.randint(3, 8)
                    l_cm = random.randint(4, 12)
                    while w_cm >= l_cm: l_cm += 1
                    
                    real_w = w_cm * scale_m
                    real_l = l_cm * scale_m
                    real_area = real_w * real_l
                    
                    q = f"แผนผังที่ดินรูปสี่เหลี่ยมผืนผ้า กว้าง <b>{w_cm} ซม.</b> ยาว <b>{l_cm} ซม.</b><br>ใช้มาตราส่วน <b>1 ซม. : {scale_m} เมตร</b><br>ที่ดินผืนนี้มี <b>พื้นที่จริง</b> กี่ตารางเมตร?"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (🔥 ข้อสอบแข่งขัน - หาพื้นที่จริง):</b><br><div style='background-color:#fce4e4; padding:10px; border-radius:5px; border-left: 4px solid #c0392b; margin: 10px 0;'><span style='color:#c0392b; font-size:15px;'><i><b>⚠️ จุดระวัง (ข้อนี้เด็กๆ โดนหลอกบ่อยมาก!):</b><br>ห้ามเอา (กว้าง × ยาว) ในกระดาษ แล้วมาคูณ {scale_m} โดยเด็ดขาด!<br>เพราะการหาพื้นที่ จะต้องแปลง <b>'ความกว้าง'</b> และ <b>'ความยาว'</b> ให้เป็นของจริงก่อนนำมาคูณกันครับ!</i></span></div><br><b>ขั้นที่ 1: แปลงความกว้างและความยาวให้เป็นของจริง</b><br>👉 ความกว้างจริง = {w_cm} ซม. × {scale_m} เมตร = <b>{real_w} เมตร</b><br>👉 ความยาวจริง = {l_cm} ซม. × {scale_m} เมตร = <b>{real_l} เมตร</b><br><br><b>ขั้นที่ 2: คำนวณหาพื้นที่จริง</b><br>👉 พื้นที่สี่เหลี่ยมผืนผ้า = กว้างจริง × ยาวจริง<br>👉 พื้นที่ = {real_w} × {real_l} = <b>{real_area:,} ตารางเมตร</b><br><br><b>ตอบ: {real_area:,} ตารางเมตร</b></span>"

                elif scenario == "find_scale":
                    real_km = random.choice([15, 20, 30, 45, 60, 120])
                    map_cm = random.choice([3, 4, 5, 6, 10, 12])
                    while real_km * 100000 % map_cm != 0:
                        map_cm = random.choice([3, 4, 5, 6, 10, 12])
                    
                    real_cm = real_km * 100000
                    scale_val = real_cm // map_cm
                    
                    q = f"ระยะทางจริงจากจังหวัด ก ไปจังหวัด ข คือ <b>{real_km} กิโลเมตร</b><br>ถ้าวัดระยะทางในแผนที่ได้ <b>{map_cm} เซนติเมตร</b><br>แผนที่ฉบับนี้ใช้มาตราส่วน <b>1 : เท่าใด?</b>"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (🔥 ข้อสอบแข่งขัน - หามาตราส่วน):</b><br>👉 การหามาตราส่วน 1 : x  เราต้องทำให้หน่วยของทั้งสองฝั่ง <b>'เป็นเซนติเมตรเหมือนกัน'</b> ก่อนครับ<br><br><b>ขั้นที่ 1: แปลงระยะทางจริงจาก กิโลเมตร เป็น เซนติเมตร</b><br>👉 1 กิโลเมตร = 1,000 เมตร<br>👉 1 เมตร = 100 เซนติเมตร<br>👉 ดังนั้น 1 กิโลเมตร = 1,000 × 100 = <b>100,000 เซนติเมตร</b><br>👉 ระยะจริง {real_km} กม. = {real_km} × 100,000 = <b>{real_cm:,} เซนติเมตร</b><br><br><b>ขั้นที่ 2: เทียบอัตราส่วนเพื่อหามาตราส่วน</b><br>👉 ระยะในแผนที่ : ระยะจริง<br>👉 <b>{map_cm} ซม. : {real_cm:,} ซม.</b><br>👉 ทำฝั่งซ้ายให้เป็น 1 โดยนำ {map_cm} ไปหารทั้งสองฝั่ง<br>👉 1 : ({real_cm:,} ÷ {map_cm})<br>👉 <b>1 : {scale_val:,}</b><br><br><b>ตอบ: มาตราส่วน 1 : {scale_val:,}</b></span>"

            elif actual_sub_t == "เรขาคณิตประยุกต์ (หาพื้นที่แรเงา)":
                def draw_shaded_svg(scenario, W, H, p1=0):
                    svg = '<div style="text-align:center; margin:15px 0;"><svg width="460" height="240">'
                    max_w, max_h = 200, 140 
                    scale = min(max_w / W, max_h / H)
                    draw_w = W * scale
                    draw_h = H * scale
                    
                    ox = (460 - draw_w) / 2
                    oy = (240 - draw_h) / 2

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

                    elif scenario == "four_corners":
                        c = p1 * scale
                        svg += f'<rect x="{ox}" y="{oy}" width="{draw_w}" height="{draw_h}" fill="none" stroke="#7f8c8d" stroke-width="2" stroke-dasharray="5,5"/>'
                        pts = f"{ox+c},{oy} {ox+draw_w-c},{oy} {ox+draw_w-c},{oy+c} {ox+draw_w},{oy+c} {ox+draw_w},{oy+draw_h-c} {ox+draw_w-c},{oy+draw_h-c} {ox+draw_w-c},{oy+draw_h} {ox+c},{oy+draw_h} {ox+c},{oy+draw_h-c} {ox},{oy+draw_h-c} {ox},{oy+c} {ox+c},{oy+c}"
                        svg += f'<polygon points="{pts}" fill="#bdc3c7" stroke="#2c3e50" stroke-width="3"/>'
                        
                        svg += f'<text x="{ox + draw_w/2}" y="{oy + draw_h + 20}" {lbl_style} text-anchor="middle">{W} ซม.</text>'
                        svg += f'<text x="{ox - 10}" y="{oy + draw_h/2 + 5}" {lbl_style} text-anchor="end">{H} ซม.</text>'
                        svg += f'<text x="{ox + draw_w/2}" y="{oy - 10}" {lbl_style_sm} text-anchor="middle">ตัดมุมละ {p1}x{p1}</text>'

                    elif scenario == "midpoint_rhombus":
                        svg += f'<rect x="{ox}" y="{oy}" width="{draw_w}" height="{draw_h}" fill="#ffffff" stroke="#2c3e50" stroke-width="3"/>'
                        pts = f"{ox+draw_w/2},{oy} {ox+draw_w},{oy+draw_h/2} {ox+draw_w/2},{oy+draw_h} {ox},{oy+draw_h/2}"
                        svg += f'<polygon points="{pts}" fill="#bdc3c7" stroke="#2c3e50" stroke-width="2"/>'
                        
                        svg += f'<text x="{ox + draw_w/2}" y="{oy + draw_h + 20}" {lbl_style} text-anchor="middle">{W} ซม.</text>'
                        svg += f'<text x="{ox - 10}" y="{oy + draw_h/2 + 5}" {lbl_style} text-anchor="end">{H} ซม.</text>'

                    elif scenario == "l_shape_path":
                        p_scale = p1 * scale
                        svg += f'<rect x="{ox}" y="{oy}" width="{draw_w}" height="{draw_h}" fill="#bdc3c7" stroke="#2c3e50" stroke-width="3"/>'
                        svg += f'<rect x="{ox+p_scale}" y="{oy}" width="{draw_w-p_scale}" height="{draw_h-p_scale}" fill="#ffffff" stroke="#2c3e50" stroke-width="2"/>'
                        
                        svg += f'<text x="{ox + draw_w/2}" y="{oy + draw_h + 20}" {lbl_style} text-anchor="middle">{W} ม.</text>'
                        svg += f'<text x="{ox + draw_w + 10}" y="{oy + draw_h/2 + 5}" {lbl_style} text-anchor="start">{H} ม.</text>'
                        svg += f'<text x="{ox + p_scale/2}" y="{oy + draw_h/2 + 5}" {lbl_style_sm} text-anchor="middle">{p1} ม.</text>'

                    svg += '</svg></div>'
                    return svg

                scenario = random.choice(["frame", "corner_cut", "triangle_in_rect", "cross_path", "four_corners", "midpoint_rhombus", "l_shape_path"])
                
                if scenario == "frame":
                    W = random.randint(15, 30)
                    H = random.randint(10, 20)
                    while W <= H: W += random.randint(2, 5)
                    border = random.randint(1, 3)
                    inner_w = W - 2*border
                    inner_h = H - 2*border
                    area_out = W * H
                    area_in = inner_w * inner_h
                    ans = area_out - area_in
                    
                    svg = draw_shaded_svg("frame", W, H, border)
                    q = f"สระว่ายน้ำมีทางเดินรอบขอบสระ (ส่วนที่แรเงา) รูปสี่เหลี่ยมผืนผ้าขนาดใหญ่ กว้าง <b>{H} เมตร</b> ยาว <b>{W} เมตร</b><br>ถ้าทางเดินกว้าง <b>{border} เมตร</b> เท่ากันโดยตลอด<br>จงหาพื้นที่ของทางเดินนี้?<br>{svg}"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (หาพื้นที่แรเงา - กรอบรูป):</b><br>👉 หลักการคิด: <b>พื้นที่ส่วนที่แรเงา = พื้นที่สี่เหลี่ยมรูปใหญ่(ข้างนอก) - พื้นที่สี่เหลี่ยมรูปเล็ก(ข้างใน)</b><br><br><b>ขั้นที่ 1: หาพื้นที่สี่เหลี่ยมรูปใหญ่ (ทั้งหมด)</b><br>👉 กว้าง {H} ม., ยาว {W} ม.<br>👉 พื้นที่รูปใหญ่ = {H} × {W} = <b>{area_out} ตารางเมตร</b><br><br><b>ขั้นที่ 2: หาขนาดของสี่เหลี่ยมรูปเล็ก (สีขาวข้างใน)</b><br>👉 ความกว้างด้านใน = กว้างรูปใหญ่ - (ขอบบน + ขอบล่าง) = {H} - ({border} + {border}) = <b>{inner_h} เมตร</b><br>👉 ความยาวด้านใน = ยาวรูปใหญ่ - (ขอบซ้าย + ขอบขวา) = {W} - ({border} + {border}) = <b>{inner_w} เมตร</b><br>👉 พื้นที่รูปเล็ก = {inner_h} × {inner_w} = <b>{area_in} ตารางเมตร</b><br><br><b>ขั้นที่ 3: หาพื้นที่ทางเดิน (แรเงา)</b><br>👉 นำพื้นที่รูปใหญ่ ลบ พื้นที่รูปเล็ก: {area_out} - {area_in} = <b>{ans} ตารางเมตร</b><br><br><b>ตอบ: {ans} ตารางเมตร</b></span>"

                elif scenario == "corner_cut":
                    W = random.randint(12, 25)
                    H = random.randint(10, 20)
                    while W <= H: W += random.randint(1, 4)
                    cut = random.randint(2, 5)
                    area_out = W * H
                    area_cut = cut * cut
                    ans = area_out - area_cut
                    
                    svg = draw_shaded_svg("corner_cut", W, H, cut)
                    q = f"กระดาษรูปสี่เหลี่ยมผืนผ้า กว้าง <b>{H} เซนติเมตร</b> ยาว <b>{W} เซนติเมตร</b><br>ถูกตัดมุมออก 1 มุม เป็นรูปสี่เหลี่ยมจัตุรัสยาวด้านละ <b>{cut} เซนติเมตร</b> (ดังรูป)<br>จงหาพื้นที่ของกระดาษส่วนที่เหลือ (ส่วนที่แรเงา)?<br>{svg}"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (หาพื้นที่แรเงา - ตัดมุม):</b><br>👉 หลักการคิด: <b>พื้นที่ส่วนที่แรเงา = พื้นที่กระดาษแผ่นเต็ม - พื้นที่ส่วนที่ถูกตัดออก</b><br><br><b>ขั้นที่ 1: หาพื้นที่กระดาษแผ่นเต็ม</b><br>👉 พื้นที่สี่เหลี่ยมผืนผ้า = กว้าง × ยาว<br>👉 พื้นที่แผ่นเต็ม = {H} × {W} = <b>{area_out} ตารางเซนติเมตร</b><br><br><b>ขั้นที่ 2: หาพื้นที่ส่วนที่ถูกตัดออก</b><br>👉 เป็นรูปสี่เหลี่ยมจัตุรัส ด้านละ {cut} ซม.<br>👉 พื้นที่ตัดออก = ด้าน × ด้าน = {cut} × {cut} = <b>{area_cut} ตารางเซนติเมตร</b><br><br><b>ขั้นที่ 3: หาพื้นที่ส่วนที่เหลือ (แรเงา)</b><br>👉 นำพื้นที่แผ่นเต็ม ลบ พื้นที่ตัดออก: {area_out} - {area_cut} = <b>{ans} ตารางเซนติเมตร</b><br><br><b>ตอบ: {ans} ตารางเซนติเมตร</b></span>"

                elif scenario == "triangle_in_rect":
                    W = random.randint(10, 24)
                    if W % 2 != 0: W += 1
                    H = random.randint(8, 20)
                    area_out = W * H
                    area_tri = (W * H) // 2
                    ans = area_out - area_tri
                    
                    svg = draw_shaded_svg("triangle_in_rect", W, H)
                    
                    # ภาพประกอบสูตรลัดสามเหลี่ยม (ลากเส้นประผ่ากลาง)
                    explain_svg = '''<div style="text-align:center; margin: 15px 0;">
                    <svg width="240" height="140">
                        <rect x="20" y="20" width="200" height="100" fill="#bdc3c7" stroke="#2c3e50" stroke-width="2"/>
                        <polygon points="20,120 220,120 120,20" fill="#ffffff" stroke="#2c3e50" stroke-width="2"/>
                        <line x1="120" y1="20" x2="120" y2="120" stroke="#e74c3c" stroke-dasharray="5,5" stroke-width="2"/>
                        <text x="60" y="80" font-family="Sarabun" font-size="16" fill="#c0392b" font-weight="bold">เท่ากัน</text>
                        <text x="180" y="80" font-family="Sarabun" font-size="16" fill="#c0392b" font-weight="bold">เท่ากัน</text>
                    </svg>
                    </div>'''

                    q = f"รูปสี่เหลี่ยมผืนผ้า กว้าง <b>{H} นิ้ว</b> ยาว <b>{W} นิ้ว</b><br>มีรูปสามเหลี่ยมสีขาวเจาะอยู่ด้านใน โดยที่ฐานของสามเหลี่ยมพอดีกับความยาวของสี่เหลี่ยม (ดังรูป)<br>จงหาพื้นที่ของส่วนที่แรเงา?<br>{svg}"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (หาพื้นที่แรเงา - สามเหลี่ยมในสี่เหลี่ยม):</b><br>👉 หลักการคิด: <b>พื้นที่ส่วนที่แรเงา = พื้นที่สี่เหลี่ยม - พื้นที่สามเหลี่ยม(สีขาว)</b><br><br><b>ขั้นที่ 1: หาพื้นที่สี่เหลี่ยมผืนผ้า (ทั้งหมด)</b><br>👉 พื้นที่ = กว้าง × ยาว = {H} × {W} = <b>{area_out} ตารางนิ้ว</b><br><br><b>ขั้นที่ 2: หาพื้นที่รูปสามเหลี่ยม (สีขาว)</b><br>👉 ฐานของสามเหลี่ยม = ความยาวสี่เหลี่ยม = {W} นิ้ว<br>👉 ความสูงของสามเหลี่ยม = ความกว้างสี่เหลี่ยม = {H} นิ้ว<br>👉 พื้นที่สามเหลี่ยม = (1/2) × ฐาน × สูง = (1/2) × {W} × {H} = <b>{area_tri} ตารางนิ้ว</b><br><br><b>ขั้นที่ 3: หาพื้นที่แรเงา</b><br>👉 พื้นที่ทั้งหมด ลบ พื้นที่สามเหลี่ยม: {area_out} - {area_tri} = <b>{ans} ตารางนิ้ว</b><br><br><div style='background-color:#fef9e7; padding:10px; border-radius:5px; border-left: 4px solid #f39c12; margin: 10px 0;'><span style='color:#d35400; font-size:15px;'><i><b>💡 ทริคข้อสอบ (ทำไมถึงเป็นครึ่งหนึ่ง?):</b><br>{explain_svg}ถ้าเราลากเส้นประผ่าครึ่งรูป จะเห็นว่าสี่เหลี่ยมถูกแบ่งเป็น 2 ฝั่ง<br>และในแต่ละฝั่ง <b>พื้นที่แรเงา จะมีขนาดเท่ากับ พื้นที่สีขาวพอดีเป๊ะ!</b><br>ดังนั้น พื้นที่แรเงารวมกันก็คือ <b>'ครึ่งหนึ่ง'</b> ของสี่เหลี่ยมใหญ่ครับ ({area_out} ÷ 2 = {ans})</i></span></div><br><b>ตอบ: {ans} ตารางนิ้ว</b></span>"

                elif scenario == "cross_path":
                    W = random.randint(20, 40)
                    H = random.randint(15, 25)
                    path = random.randint(2, 4)
                    area_h = W * path
                    area_v = H * path
                    area_mid = path * path
                    ans = area_h + area_v - area_mid
                    
                    svg = draw_shaded_svg("cross_path", W, H, path)
                    
                    # ภาพประกอบอธิบายพื้นที่ทับซ้อนตรงกลาง
                    explain_svg = '''<div style="text-align:center; margin: 15px 0;">
                    <svg width="240" height="160">
                        <rect x="20" y="20" width="200" height="120" fill="none" stroke="#bdc3c7" stroke-width="1"/>
                        <rect x="20" y="60" width="200" height="40" fill="#aed6f1" stroke="none"/>
                        <rect x="100" y="20" width="40" height="120" fill="#aed6f1" stroke="none"/>
                        <rect x="100" y="60" width="40" height="40" fill="#e74c3c" stroke="#c0392b" stroke-width="2"/>
                        <text x="120" y="85" font-family="Sarabun" font-size="14" fill="#ffffff" font-weight="bold" text-anchor="middle">ซ้ำ!</text>
                    </svg>
                    </div>'''

                    q = f"สนามหญ้ารูปสี่เหลี่ยมผืนผ้า กว้าง <b>{H} เมตร</b> ยาว <b>{W} เมตร</b><br>มีทางเดินตัดกันเป็นรูปกากบาทตรงกลาง (ส่วนที่แรเงา) โดยทางเดินมีความกว้าง <b>{path} เมตร</b> เท่ากัน<br>จงหาพื้นที่ของทางเดินทั้งหมด?<br>{svg}"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (🔥 ข้อสอบแข่งขัน - ทางเดินตัดกัน):</b><br><div style='background-color:#fce4e4; padding:10px; border-radius:5px; border-left: 4px solid #c0392b; margin: 10px 0;'><span style='color:#c0392b; font-size:15px;'><i><b>⚠️ จุดระวัง:</b> น้องๆ หลายคนมักจะเอา (พื้นที่แนวนอน + พื้นที่แนวตั้ง) แล้วตอบเลย ซึ่ง <b>ผิด!</b> ลองดูภาพด้านล่างครับ<br>{explain_svg}ตรงกลางที่ทางเดินตัดกัน (สีแดง) จะถูกนับไปแล้วตอนคิดแนวนอน และถูกนับซ้ำอีกตอนคิดแนวตั้ง เราจึงต้อง <b>ลบออก 1 ครั้ง</b> ครับ!</i></span></div><br><b>ขั้นที่ 1: หาพื้นที่ทางเดินแนวนอน และ แนวตั้ง</b><br>👉 ทางแนวนอน = ความยาวสนาม × ความกว้างทางเดิน = {W} × {path} = <b>{area_h} ตร.ม.</b><br>👉 ทางแนวตั้ง = ความกว้างสนาม × ความกว้างทางเดิน = {H} × {path} = <b>{area_v} ตร.ม.</b><br><br><b>ขั้นที่ 2: หาพื้นที่สี่เหลี่ยมจัตุรัสตรงกลาง (สีแดงที่ซ้อนทับกัน)</b><br>👉 พื้นที่ตรงกลาง = กว้างทางเดิน × กว้างทางเดิน = {path} × {path} = <b>{area_mid} ตร.ม.</b><br><br><b>ขั้นที่ 3: คำนวณพื้นที่ทางเดินที่แท้จริง</b><br>👉 พื้นที่ทางเดิน = แนวนอน + แนวตั้ง - ส่วนที่ซ้อนทับ<br>👉 พื้นที่ทางเดิน = {area_h} + {area_v} - {area_mid} = <b>{ans} ตารางเมตร</b><br><br><b>ตอบ: {ans} ตารางเมตร</b></span>"

                elif scenario == "four_corners":
                    W = random.randint(15, 30)
                    H = random.randint(12, 20)
                    cut = random.randint(2, 4)
                    area_out = W * H
                    area_1cut = cut * cut
                    area_4cuts = 4 * area_1cut
                    ans = area_out - area_4cuts
                    
                    svg = draw_shaded_svg("four_corners", W, H, cut)
                    q = f"กระดาษรูปสี่เหลี่ยมผืนผ้า กว้าง <b>{H} เซนติเมตร</b> ยาว <b>{W} เซนติเมตร</b><br>ถูกตัดมุมออก <b>ทั้ง 4 มุม</b> เป็นรูปสี่เหลี่ยมจัตุรัสยาวด้านละ <b>{cut} เซนติเมตร</b> เพื่อนำไปพับเป็นกล่อง (ดังรูป)<br>จงหาพื้นที่ของกระดาษส่วนที่เหลือ (ส่วนที่แรเงา)?<br>{svg}"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (หาพื้นที่แรเงา - ตัด 4 มุม):</b><br>👉 หลักการคิด: <b>พื้นที่ส่วนที่แรเงา = พื้นที่กระดาษแผ่นเต็ม - พื้นที่ส่วนที่ถูกตัดออก (4 ชิ้น)</b><br><br><b>ขั้นที่ 1: หาพื้นที่กระดาษแผ่นเต็ม</b><br>👉 พื้นที่ = กว้าง × ยาว = {H} × {W} = <b>{area_out} ตารางเซนติเมตร</b><br><br><b>ขั้นที่ 2: หาพื้นที่ส่วนที่ถูกตัดออกทั้งหมด</b><br>👉 ตัดออก 1 มุม = ด้าน × ด้าน = {cut} × {cut} = <b>{area_1cut} ตร.ซม.</b><br>👉 แต่เราตัดออก 4 มุม จึงต้องคูณ 4 = 4 × {area_1cut} = <b>{area_4cuts} ตร.ซม.</b><br><br><b>ขั้นที่ 3: หาพื้นที่ส่วนที่เหลือ (แรเงา)</b><br>👉 นำพื้นที่แผ่นเต็ม ลบ พื้นที่ถูกตัดทั้งหมด: {area_out} - {area_4cuts} = <b>{ans} ตารางเซนติเมตร</b><br><br><b>ตอบ: {ans} ตารางเซนติเมตร</b></span>"

                elif scenario == "midpoint_rhombus":
                    W = random.randint(12, 30)
                    if W % 2 != 0: W += 1
                    H = random.randint(10, 24)
                    if H % 2 != 0: H += 1
                    area_out = W * H
                    ans = area_out // 2
                    
                    svg = draw_shaded_svg("midpoint_rhombus", W, H)
                    
                    explain_svg = '''<div style="text-align:center; margin: 15px 0;">
                    <svg width="240" height="160">
                        <rect x="20" y="20" width="200" height="120" fill="none" stroke="#2c3e50" stroke-width="2"/>
                        <polygon points="120,20 220,80 120,140 20,80" fill="#bdc3c7" stroke="#2c3e50" stroke-width="2"/>
                        <line x1="120" y1="20" x2="120" y2="140" stroke="#e74c3c" stroke-dasharray="5,5" stroke-width="2"/>
                        <line x1="20" y1="80" x2="220" y2="80" stroke="#e74c3c" stroke-dasharray="5,5" stroke-width="2"/>
                        <text x="50" y="45" font-family="Sarabun" font-size="16" fill="#2c3e50" font-weight="bold">1</text>
                        <text x="190" y="45" font-family="Sarabun" font-size="16" fill="#2c3e50" font-weight="bold">2</text>
                        <text x="50" y="125" font-family="Sarabun" font-size="16" fill="#2c3e50" font-weight="bold">3</text>
                        <text x="190" y="125" font-family="Sarabun" font-size="16" fill="#2c3e50" font-weight="bold">4</text>
                        <text x="90" y="65" font-family="Sarabun" font-size="16" fill="#c0392b" font-weight="bold">1</text>
                        <text x="150" y="65" font-family="Sarabun" font-size="16" fill="#c0392b" font-weight="bold">2</text>
                        <text x="90" y="105" font-family="Sarabun" font-size="16" fill="#c0392b" font-weight="bold">3</text>
                        <text x="150" y="105" font-family="Sarabun" font-size="16" fill="#c0392b" font-weight="bold">4</text>
                    </svg>
                    </div>'''

                    q = f"รูปสี่เหลี่ยมผืนผ้า กว้าง <b>{H} เซนติเมตร</b> ยาว <b>{W} เซนติเมตร</b><br>ถูกลากเส้นเชื่อม <b>จุดกึ่งกลาง</b> ของความยาวแต่ละด้าน เกิดเป็นรูปที่แรเงา (ดังรูป)<br>จงหาพื้นที่ของส่วนที่แรเงา?<br>{svg}"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (🔥 สี่เหลี่ยมแนบใน):</b><br>👉 การหาพื้นที่รูปแบบนี้ ถ้าเราวาดเส้นกากบาทแบ่งครึ่งรูป จะเห็นความลับซ่อนอยู่ครับ!<br>{explain_svg}👉 <i>สังเกตจากรูป: เมื่อลากเส้นประแบ่งครึ่ง สี่เหลี่ยมใหญ่จะถูกแบ่งเป็น 4 ส่วนย่อย</i><br>👉 <i>ในแต่ละส่วนย่อย เส้นขอบของสี่เหลี่ยมแรเงาจะ <b>'ผ่าครึ่งแนวทแยงมุม'</b> พอดีเป๊ะ! (แรเงาเบอร์ 1 เท่ากับ สีขาวเบอร์ 1)</i><br>👉 สรุปได้ว่า พื้นที่สีเทา รวมกันแล้วจะเท่ากับ พื้นที่สีขาว<br>👉 ทำให้เกิดเป็นสูตรลัดคือ <b>พื้นที่ส่วนที่แรเงา จะมีขนาดเท่ากับ 'ครึ่งหนึ่ง' ของรูปใหญ่เสมอ!</b><br><br><b>ขั้นที่ 1: หาพื้นที่สี่เหลี่ยมรูปใหญ่</b><br>👉 กว้าง × ยาว = {H} × {W} = <b>{area_out} ตารางเซนติเมตร</b><br><br><b>ขั้นที่ 2: หาพื้นที่แรเงา (ใช้สูตรลัด)</b><br>👉 พื้นที่แรเงา = พื้นที่รูปใหญ่ ÷ 2<br>👉 {area_out} ÷ 2 = <b>{ans} ตารางเซนติเมตร</b><br><br><b>ตอบ: {ans} ตารางเซนติเมตร</b></span>"

                elif scenario == "l_shape_path":
                    W = random.randint(15, 30)
                    H = random.randint(12, 20)
                    path = random.randint(2, 4)
                    area_out = W * H
                    inner_w = W - path
                    inner_h = H - path
                    area_in = inner_w * inner_h
                    ans = area_out - area_in
                    
                    svg = draw_shaded_svg("l_shape_path", W, H, path)
                    q = f"สระว่ายน้ำแห่งหนึ่งถูกสร้างทางเดิน (ส่วนที่แรเงา) ล้อมรอบเพียง <b>2 ด้าน</b> ดังรูป<br>ถ้าสระว่ายน้ำรวมทางเดิน กว้าง <b>{H} เมตร</b> ยาว <b>{W} เมตร</b> และทางเดินกว้าง <b>{path} เมตร</b><br>จงหาพื้นที่ของทางเดินรูปตัว L นี้?<br>{svg}"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (🔥 ทางเดินตัว L):</b><br>👉 หลักการคิดที่ง่ายที่สุดคือ: มองให้เป็น <b>กรอบรูปที่ถูกดันไปชิดมุม</b><br>👉 <b>พื้นที่ทางเดิน = พื้นที่สี่เหลี่ยมรูปใหญ่(รวมทางเดิน) - พื้นที่สี่เหลี่ยมรูปเล็ก(เฉพาะสระสีขาว)</b><br><br><b>ขั้นที่ 1: หาพื้นที่สี่เหลี่ยมรูปใหญ่ (ทั้งหมด)</b><br>👉 กว้าง {H} ม., ยาว {W} ม.<br>👉 พื้นที่รูปใหญ่ = {H} × {W} = <b>{area_out} ตารางเมตร</b><br><br><b>ขั้นที่ 2: หาขนาดของสี่เหลี่ยมรูปเล็ก (สีขาว)</b><br>👉 ความกว้างด้านใน = กว้างรวม - ความกว้างทางเดิน = {H} - {path} = <b>{inner_h} เมตร</b><br>👉 ความยาวด้านใน = ยาวรวม - ความกว้างทางเดิน = {W} - {path} = <b>{inner_w} เมตร</b><br>👉 พื้นที่รูปเล็ก = {inner_h} × {inner_w} = <b>{area_in} ตารางเมตร</b><br><br><b>ขั้นที่ 3: หาพื้นที่ทางเดินตัว L (แรเงา)</b><br>👉 นำพื้นที่รูปใหญ่ ลบ พื้นที่รูปเล็ก: {area_out} - {area_in} = <b>{ans} ตารางเมตร</b><br><br><b>ตอบ: {ans} ตารางเมตร</b></span>"

            # ================= หมวด ป.4 (ครบ 15 หัวข้อ แก้บั๊กวาดรูปและย่อหน้าแล้ว) =================
            elif actual_sub_t == "การอ่านและการเขียนตัวเลข":
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
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 นำค่าของเลขโดดในแต่ละหลักมาเขียนบวกกัน (หลักใดเป็น 0 ไม่ต้องนำมาเขียน)<br><b>ตอบ: {expanded}</b></span>"
                else:
                    target_idx = random.randint(0, len(num_str)-1)
                    while num_str[target_idx] == '0':
                        target_idx = random.randint(0, len(num_str)-1)
                    target_digit = num_str[target_idx]
                    place_names = ["หน่วย", "สิบ", "ร้อย", "พัน", "หมื่น", "แสน", "ล้าน", "สิบล้าน", "ร้อยล้าน"]
                    place = place_names[len(num_str) - target_idx - 1]
                    val = int(target_digit) * (10**(len(num_str) - target_idx - 1))
                    q = f"จากจำนวน <b>{num:,}</b> เลขโดด <b>{target_digit}</b> (ตัวที่ขีดเส้นใต้) อยู่ในหลักใด และมีค่าเท่าใด?<br><span style='font-size:24px;'>{num_str[:target_idx]}<u>{target_digit}</u>{num_str[target_idx+1:]}</span>"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 เลขโดด <b>{target_digit}</b> อยู่ในหลัก<b>{place}</b><br>👉 จึงมีค่าเท่ากับ <b>{val:,}</b><br><b>ตอบ: หลัก{place} มีค่า {val:,}</b></span>"

            elif actual_sub_t == "การเปรียบเทียบและเรียงลำดับ":
                count = random.randint(4, 5)
                base = random.randint(100000, 999999) if not is_challenge else random.randint(1000000, 9999999)
                nums = [base + random.randint(-50000, 50000) for _ in range(count)]
                nums = list(set(nums))
                while len(nums) < count:
                    nums.append(base + random.randint(-50000, 50000))
                    nums = list(set(nums))
                order = random.choice(["น้อยไปมาก", "มากไปน้อย"])
                nums_str = ", ".join([f"{n:,}" for n in nums])
                sorted_nums = sorted(nums) if order == "น้อยไปมาก" else sorted(nums, reverse=True)
                sorted_str = ", ".join([f"{n:,}" for n in sorted_nums])
                q = f"จงเรียงลำดับจำนวนต่อไปนี้จาก<b>{order}</b>:<br><div style='text-align:center; font-size:22px; margin: 10px 0; color:#2980b9;'>{nums_str}</div>"
                sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 เปรียบเทียบจำนวนหลัก และค่าของเลขโดดทีละหลักจากซ้ายไปขวา<br>👉 เรียงลำดับจาก{order} จะได้:<br><b>ตอบ: {sorted_str}</b></span>"

            elif actual_sub_t == "ค่าประมาณเป็นจำนวนเต็มสิบ เต็มร้อย เต็มพัน":
                target = random.choice(["สิบ", "ร้อย", "พัน"])
                num = random.randint(1234, 99999) if not is_challenge else random.randint(100000, 999999)
                if target == "สิบ":
                    check_val = num % 10
                    round_base = (num // 10) * 10
                    if check_val >= 5: ans, explain = round_base + 10, f"หลักหน่วยคือเลข {check_val} (ตั้งแต่ 5 ขึ้นไป) จึงปัดขึ้น"
                    else: ans, explain = round_base, f"หลักหน่วยคือเลข {check_val} (น้อยกว่า 5) จึงปัดทิ้งเป็น 0"
                elif target == "ร้อย":
                    check_val = (num % 100) // 10
                    round_base = (num // 100) * 100
                    if check_val >= 5: ans, explain = round_base + 100, f"หลักสิบคือเลข {check_val} (ตั้งแต่ 5 ขึ้นไป) จึงปัดขึ้น"
                    else: ans, explain = round_base, f"หลักสิบคือเลข {check_val} (น้อยกว่า 5) จึงปัดทิ้งเป็น 0"
                else:
                    check_val = (num % 1000) // 100
                    round_base = (num // 1000) * 1000
                    if check_val >= 5: ans, explain = round_base + 1000, f"หลักร้อยคือเลข {check_val} (ตั้งแต่ 5 ขึ้นไป) จึงปัดขึ้น"
                    else: ans, explain = round_base, f"หลักร้อยคือเลข {check_val} (น้อยกว่า 5) จึงปัดทิ้งเป็น 0"
                q = f"จงหาค่าประมาณเป็น<b>จำนวนเต็ม{target}</b> ของ <b>{num:,}</b>"
                sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 การหาค่าประมาณเป็นจำนวนเต็ม{target} ให้พิจารณาเลขโดดในหลักที่อยู่ติดกันทางขวา<br>👉 ในข้อนี้ {explain}<br><b>ตอบ: {ans:,}</b></span>"

            elif actual_sub_t == "การบวก (แบบตั้งหลัก)":
                a = random.randint(100000, 999999) if not is_challenge else random.randint(1000000, 9999999)
                b = random.randint(100000, 999999) if not is_challenge else random.randint(1000000, 9999999)
                ans = a + b
                q_base = f"จงหาผลบวกของ <b>{a:,} + {b:,}</b>"
                table_html = generate_vertical_table_html(a, b, "+", result=ans, is_key=False)
                table_key = generate_vertical_table_html(a, b, "+", result=ans, is_key=True)
                q = f"{q_base}<br>{table_html}"
                sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>ตั้งหลักให้ตรงกัน แล้วบวกจากหลักหน่วย (ขวาไปซ้าย)<br>{table_key}</span>"

            elif actual_sub_t == "การลบ (แบบตั้งหลัก)":
                a = random.randint(100000, 999999) if not is_challenge else random.randint(1000000, 9999999)
                b = random.randint(50000, a - 1000)
                ans = a - b
                q_base = f"จงหาผลลบของ <b>{a:,} - {b:,}</b>"
                table_html = generate_vertical_table_html(a, b, "-", result=ans, is_key=False)
                table_key = generate_vertical_table_html(a, b, "-", result=ans, is_key=True)
                q = f"{q_base}<br>{table_html}"
                sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>ตั้งหลักให้ตรงกัน ลบจากขวาไปซ้าย หากหลักใดตัวตั้งน้อยกว่าให้ยืมหลักข้างหน้า<br>{table_key}</span>"

            elif actual_sub_t == "การคูณ (แบบตั้งหลัก)":
                a = random.randint(100, 9999) if not is_challenge else random.randint(5000, 99999)
                b = random.randint(12, 99) if not is_challenge else random.randint(101, 999)
                ans = a * b
                q_base = f"จงหาผลคูณของ <b>{a:,} × {b:,}</b>"
                table_html = generate_vertical_table_html(a, b, "×", result=ans, is_key=False)
                table_key = generate_vertical_table_html(a, b, "×", result=ans, is_key=True)
                q = f"{q_base}<br>{table_html}"
                sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>นำตัวคูณแต่ละหลักไปคูณตัวตั้ง แล้วนำผลคูณในแต่ละบรรทัดมาบวกกัน<br>{table_key}</span>"

            elif actual_sub_t == "การหารยาว":
                divisor = random.randint(2, 9) if not is_challenge else random.randint(11, 99)
                quotient = random.randint(1000, 9999)
                remainder = random.randint(0, divisor - 1)
                dividend = (divisor * quotient) + remainder
                equation_html = f"<div style='font-size: 24px; margin-bottom: 10px;'><b>{dividend:,} ÷ {divisor:,} = ?</b></div>"
                table_html = generate_long_division_step_by_step_html(divisor, dividend, equation_html, is_key=False)
                table_key = generate_long_division_step_by_step_html(divisor, dividend, equation_html, is_key=True)
                q = f"จงหาผลหารโดยวิธีหารยาว<br>{table_html}"
                ans_txt = f"{quotient:,}" if remainder == 0 else f"{quotient:,} เศษ {remainder:,}"
                sol = f"<span style='color:#2c3e50;'><b>เฉลยวิธีทำ (หารยาว):</b><br>{table_key}<br><b>ตอบ: {ans_txt}</b></span>"

            elif actual_sub_t == "แปลงเศษเกินเป็นจำนวนคละ":
                den = random.randint(3, 12) if not is_challenge else random.randint(13, 25)
                whole = random.randint(2, 9)
                num_rem = random.randint(1, den - 1)
                num_total = (whole * den) + num_rem
                frac_str = f_html(num_total, den)
                mixed_str = generate_mixed_number_html(whole, num_rem, den)
                q = f"จงแปลงเศษเกินต่อไปนี้ให้เป็นจำนวนคละ<br><br><div style='text-align:center; font-size:26px;'>{frac_str} = <span style='color:#2980b9;'>?</span></div>"
                sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 นำตัวเศษ (ด้านบน) หารด้วยตัวส่วน (ด้านล่าง)<br>👉 นำ {num_total} ÷ {den} <br>👉 จะได้ <b>{whole}</b> และเหลือเศษ <b>{num_rem}</b><br>👉 นำมาเขียนเป็นจำนวนคละได้คือ <b>{mixed_str}</b><br><b>ตอบ: {mixed_str}</b></span>"

            elif actual_sub_t == "การอ่านและการเขียนทศนิยม":
                dp = random.randint(1, 3)
                whole = random.randint(0, 99)
                if dp == 1:
                    dec = random.randint(1, 9)
                    num_str = f"{whole}.{dec}"
                elif dp == 2:
                    dec = random.randint(1, 99)
                    num_str = f"{whole}.{dec:02d}"
                else:
                    dec = random.randint(1, 999)
                    num_str = f"{whole}.{dec:03d}"
                thai_whole = generate_thai_number_text(str(whole)) if whole > 0 else "ศูนย์"
                thai_dec = "".join([["ศูนย์","หนึ่ง","สอง","สาม","สี่","ห้า","หก","เจ็ด","แปด","เก้า"][int(d)] for d in num_str.split(".")[1]])
                thai_read = f"{thai_whole}จุด{thai_dec}"
                mode = random.choice(["to_text", "to_num"])
                if mode == "to_text":
                    q = f"จงเขียนทศนิยม <b>{num_str}</b> เป็นคำอ่าน"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 ตัวเลขหน้าจุดทศนิยมให้อ่านแบบจำนวนนับปกติ<br>👉 ตัวเลขหลังจุดทศนิยมให้อ่านเรียงตัว<br><b>ตอบ: {thai_read}</b></span>"
                else:
                    q = f"จงเขียนคำอ่าน <b>\"{thai_read}\"</b> ให้เป็นตัวเลขทศนิยม"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 แปลงคำอ่านเป็นตัวเลข โดยตัวเลขหลังคำว่า 'จุด' ให้เขียนเรียงกันทีละหลัก<br><b>ตอบ: {num_str}</b></span>"

            elif actual_sub_t == "การบอกชนิดของมุม":
                angle = random.randint(10, 175)
                if angle < 90:
                    angle_type, reason = "มุมแหลม", "มีขนาดน้อยกว่า 90 องศา"
                elif 85 < angle < 95:
                    angle, angle_type, reason = 90, "มุมฉาก", "มีขนาดเท่ากับ 90 องศาพอดี"
                elif angle == 180:
                    angle_type, reason = "มุมตรง", "มีขนาดเท่ากับ 180 องศาพอดี"
                else:
                    angle_type, reason = "มุมป้าน", "มีขนาดมากกว่า 90 องศา แต่น้อยกว่า 180 องศา"
                q = f"มุมที่มีขนาด <b>{angle}°</b> คือมุมชนิดใด?<br><span style='font-size:18px; color:#7f8c8d;'>(มุมแหลม, มุมฉาก, มุมป้าน, มุมตรง)</span>"
                sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 มุม {angle}° {reason}<br>👉 ดังนั้นจึงจัดเป็น <b>{angle_type}</b><br><b>ตอบ: {angle_type}</b></span>"

            elif actual_sub_t == "การวัดขนาดของมุม (ไม้โปรแทรกเตอร์)":
                def draw_angle_feature_local(vx, vy, ax, ay, bx, by, r_arc, r_text, label, color_arc, color_text, is_x=False):
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
                    ty += 4 
                    font_size = "16px" if is_x else "13px"
                    return arc_svg + f'<text x="{tx}" y="{ty}" font-size="{font_size}" font-weight="bold" font-family="Sarabun" text-anchor="middle" fill="{color_text}">{label}</text>'

                def draw_angle_svg_local(mode, val1, val2, val3=""):
                    svg = '<div style="text-align:center; margin:15px 0;"><svg width="340" height="200">'
                    lbl_style = 'font-family:Sarabun; font-size:16px; font-weight:bold; fill:#2c3e50;'
                    vx, vy, phi = 170, 160, val2 
                    ax, ay, cx, cy = 40, 160, 300, 160 
                    bx, by = vx + 120 * math.cos(math.radians(phi)), vy - 120 * math.sin(math.radians(phi))
                    svg += f'<line x1="{ax}" y1="{ay}" x2="{cx}" y2="{cy}" stroke="#34495e" stroke-width="4"/>'
                    svg += f'<line x1="{vx}" y1="{vy}" x2="{bx}" y2="{by}" stroke="#c0392b" stroke-width="3"/>'
                    svg += f'<circle cx="{bx}" cy="{by}" r="3" fill="#c0392b"/>'
                    svg += f'<text x="{ax-15}" y="{ay+5}" {lbl_style}>A</text>'
                    svg += f'<text x="{cx+5}" y="{cy+5}" {lbl_style}>B</text>'
                    svg += f'<text x="{bx-5}" y="{by-10}" {lbl_style}>C</text>'
                    svg += f'<text x="{vx-5}" y="{vy+20}" {lbl_style}>O</text>'
                    svg += draw_angle_feature_local(vx, vy, ax, ay, bx, by, 28, 45, f"{val1}°", "#2ecc71", "#c0392b")
                    svg += draw_angle_feature_local(vx, vy, bx, by, cx, cy, 28, 45, val2 if val3=="" else val3, "#2ecc71", "#2980b9", is_x=True)
                    return svg + '</svg></div>'

                mode = random.choice(["read_protractor", "calc_angle"])
                if mode == "read_protractor":
                    base_deg = random.choice([0, 10, 20])
                    angle = random.randint(30, 150)
                    end_deg = base_deg + angle
                    q = f"ในการวัดขนาดของมุม <b>AOB</b> ด้วยไม้โปรแทรกเตอร์<br>ถ้าแขน OA ชี้ที่สเกลตัวเลข <b>{base_deg}°</b> และแขน OB ชี้ที่สเกลตัวเลข <b>{end_deg}°</b><br>มุม AOB มีขนาดกี่องศา?"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 นำตัวเลขที่แขนของมุมทั้งสองข้างชี้มาลบกัน เพื่อหาขนาดความกว้างของมุม<br>👉 {end_deg}° - {base_deg}° = <b>{angle}°</b><br><b>ตอบ: {angle} องศา</b></span>"
                else:
                    ans = random.randint(25, 160)
                    svg = draw_angle_svg_local("straight", 180-ans, ans, "?")
                    q = f"ถ้านำไม้โปรแทรกเตอร์มาวัดมุม <b>x</b> ในรูป จะได้ขนาดกี่องศา?<br>(กำหนดให้เส้นตรงด้านล่างคือ 180°)<br>{svg}"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 มุมบนเส้นตรงมีขนาดรวม 180°<br>👉 ถ้ามุมอีกฝั่งกาง {180-ans}° มุม x จะเท่ากับ 180° - {180-ans}° = <b>{ans}°</b><br><b>ตอบ: {ans} องศา</b></span>"

            elif actual_sub_t == "การหาความยาวรอบรูปสี่เหลี่ยมมุมฉาก":
                def draw_rect_svg_local(w_val, h_val, w_lbl, h_lbl, fill_color="#eaf2f8"):
                    scale = 140 / max(w_val, h_val)
                    dw, dh = w_val * scale, h_val * scale
                    svg = f'<div style="text-align:center; margin: 15px 0;"><svg width="300" height="200">'
                    svg += f'<rect x="{150 - dw/2}" y="{100 - dh/2}" width="{dw}" height="{dh}" fill="{fill_color}" stroke="#2980b9" stroke-width="3"/>'
                    svg += f'<text x="150" y="{100 - dh/2 - 10}" font-family="Sarabun" font-size="16" font-weight="bold" fill="#c0392b" text-anchor="middle">{w_lbl}</text>'
                    svg += f'<text x="{150 + dw/2 + 10}" y="100" font-family="Sarabun" font-size="16" font-weight="bold" fill="#c0392b" text-anchor="start" dominant-baseline="middle">{h_lbl}</text>'
                    return svg + '</svg></div>'

                is_square = random.choice([True, False])
                if is_square:
                    side = random.randint(5, 25)
                    peri = 4 * side
                    svg = draw_rect_svg_local(side, side, f"{side} ม.", f"{side} ม.", "#fdf2e9")
                    q = f"จงหาความยาวรอบรูปของ<b>สี่เหลี่ยมจัตุรัส</b>ต่อไปนี้<br>{svg}"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 สูตรความยาวรอบรูปสี่เหลี่ยมจัตุรัส = 4 × ความยาวด้าน<br>👉 4 × {side} = <b>{peri} เมตร</b><br><b>ตอบ: {peri} เมตร</b></span>"
                else:
                    w, h = random.randint(4, 15), random.randint(16, 30)
                    peri = 2 * (w + h)
                    svg = draw_rect_svg_local(h, w, f"{h} ซม.", f"{w} ซม.", "#e8f8f5")
                    q = f"จงหาความยาวรอบรูปของ<b>สี่เหลี่ยมผืนผ้า</b>ต่อไปนี้<br>{svg}"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 สูตรความยาวรอบรูปสี่เหลี่ยมผืนผ้า = 2 × (กว้าง + ยาว)<br>👉 กว้าง + ยาว = {w} + {h} = {w+h}<br>👉 2 × {w+h} = <b>{peri} เซนติเมตร</b><br><b>ตอบ: {peri} เซนติเมตร</b></span>"

            elif actual_sub_t == "การหาพื้นที่รูปสี่เหลี่ยมมุมฉาก":
                def draw_rect_svg_local(w_val, h_val, w_lbl, h_lbl, fill_color="#eaf2f8"):
                    scale = 140 / max(w_val, h_val)
                    dw, dh = w_val * scale, h_val * scale
                    svg = f'<div style="text-align:center; margin: 15px 0;"><svg width="300" height="200">'
                    svg += f'<rect x="{150 - dw/2}" y="{100 - dh/2}" width="{dw}" height="{dh}" fill="{fill_color}" stroke="#2980b9" stroke-width="3"/>'
                    svg += f'<text x="150" y="{100 - dh/2 - 10}" font-family="Sarabun" font-size="16" font-weight="bold" fill="#c0392b" text-anchor="middle">{w_lbl}</text>'
                    svg += f'<text x="{150 + dw/2 + 10}" y="100" font-family="Sarabun" font-size="16" font-weight="bold" fill="#c0392b" text-anchor="start" dominant-baseline="middle">{h_lbl}</text>'
                    return svg + '</svg></div>'

                is_square = random.choice([True, False])
                if is_square:
                    side = random.randint(5, 25)
                    area = side * side
                    svg = draw_rect_svg_local(side, side, f"{side} ม.", f"{side} ม.", "#fdf2e9")
                    q = f"จงหาพื้นที่ของ<b>สี่เหลี่ยมจัตุรัส</b>ต่อไปนี้<br>{svg}"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 สูตรพื้นที่สี่เหลี่ยมจัตุรัส = ด้าน × ด้าน<br>👉 {side} × {side} = <b>{area:,} ตารางเมตร</b><br><b>ตอบ: {area:,} ตารางเมตร</b></span>"
                else:
                    w, h = random.randint(4, 15), random.randint(16, 30)
                    area = w * h
                    svg = draw_rect_svg_local(h, w, f"{h} ซม.", f"{w} ซม.", "#e8f8f5")
                    q = f"จงหาพื้นที่ของ<b>สี่เหลี่ยมผืนผ้า</b>ต่อไปนี้<br>{svg}"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 สูตรพื้นที่สี่เหลี่ยมผืนผ้า = กว้าง × ยาว<br>👉 {w} × {h} = <b>{area:,} ตารางเซนติเมตร</b><br><b>ตอบ: {area:,} ตารางเซนติเมตร</b></span>"

            elif actual_sub_t == "การแก้สมการ (บวก/ลบ)":
                var = random.choice(["A", "B", "x", "y", "ก", "ข"])
                a = random.randint(1000, 9999) if not is_challenge else random.randint(15000, 50000)
                op = random.choice(["+", "-"])
                if op == "+":
                    ans = random.randint(1000, 9999) if not is_challenge else random.randint(15000, 50000)
                    c = ans + a
                    q = f"จงแก้สมการเพื่อหาค่าของ <b>{var}</b> : <br><div style='text-align:center; font-size:24px; margin: 15px 0;'><b>{var} + {a:,} = {c:,}</b></div>"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 ย้ายตัวเลข <b>+{a:,}</b> ไปอยู่อีกฝั่ง โดยเปลี่ยนเครื่องหมายบวกเป็นลบ<br>👉 จะได้: {var} = {c:,} - {a:,}<br>👉 คำนวณ: {var} = <b>{ans:,}</b><br><b>ตอบ: {ans:,}</b></span>"
                else:
                    c = random.randint(1000, 9999) if not is_challenge else random.randint(15000, 50000)
                    ans = c + a
                    q = f"จงแก้สมการเพื่อหาค่าของ <b>{var}</b> : <br><div style='text-align:center; font-size:24px; margin: 15px 0;'><b>{var} - {a:,} = {c:,}</b></div>"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 ย้ายตัวเลข <b>-{a:,}</b> ไปอยู่อีกฝั่ง โดยเปลี่ยนเครื่องหมายลบเป็นบวก<br>👉 จะได้: {var} = {c:,} + {a:,}<br>👉 คำนวณ: {var} = <b>{ans:,}</b><br><b>ตอบ: {ans:,}</b></span>"

            elif actual_sub_t == "การอ่านและการเขียนตัวเลข":
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
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 นำค่าของเลขโดดในแต่ละหลักมาเขียนบวกกัน (หลักใดเป็น 0 ไม่ต้องนำมาเขียน)<br><b>ตอบ: {expanded}</b></span>"
                else:
                    target_idx = random.randint(0, len(num_str)-1)
                    while num_str[target_idx] == '0':
                        target_idx = random.randint(0, len(num_str)-1)
                    target_digit = num_str[target_idx]
                    place_names = ["หน่วย", "สิบ", "ร้อย", "พัน", "หมื่น", "แสน", "ล้าน", "สิบล้าน", "ร้อยล้าน"]
                    place = place_names[len(num_str) - target_idx - 1]
                    val = int(target_digit) * (10**(len(num_str) - target_idx - 1))
                    q = f"จากจำนวน <b>{num:,}</b> เลขโดด <b>{target_digit}</b> (ตัวที่ขีดเส้นใต้) อยู่ในหลักใด และมีค่าเท่าใด?<br><span style='font-size:24px;'>{num_str[:target_idx]}<u>{target_digit}</u>{num_str[target_idx+1:]}</span>"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 เลขโดด <b>{target_digit}</b> อยู่ในหลัก<b>{place}</b><br>👉 จึงมีค่าเท่ากับ <b>{val:,}</b><br><b>ตอบ: หลัก{place} มีค่า {val:,}</b></span>"

            elif actual_sub_t == "การเปรียบเทียบและเรียงลำดับ":
                count = random.randint(4, 5)
                base = random.randint(100000, 999999) if not is_challenge else random.randint(1000000, 9999999)
                nums = [base + random.randint(-50000, 50000) for _ in range(count)]
                nums = list(set(nums))
                while len(nums) < count:
                    nums.append(base + random.randint(-50000, 50000))
                    nums = list(set(nums))
                order = random.choice(["น้อยไปมาก", "มากไปน้อย"])
                nums_str = ", ".join([f"{n:,}" for n in nums])
                sorted_nums = sorted(nums) if order == "น้อยไปมาก" else sorted(nums, reverse=True)
                sorted_str = ", ".join([f"{n:,}" for n in sorted_nums])
                q = f"จงเรียงลำดับจำนวนต่อไปนี้จาก<b>{order}</b>:<br><div style='text-align:center; font-size:22px; margin: 10px 0; color:#2980b9;'>{nums_str}</div>"
                sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 เปรียบเทียบจำนวนหลัก และค่าของเลขโดดทีละหลักจากซ้ายไปขวา<br>👉 เรียงลำดับจาก{order} จะได้:<br><b>ตอบ: {sorted_str}</b></span>"

            elif actual_sub_t == "ค่าประมาณเป็นจำนวนเต็มสิบ เต็มร้อย เต็มพัน":
                target = random.choice(["สิบ", "ร้อย", "พัน"])
                num = random.randint(1234, 99999) if not is_challenge else random.randint(100000, 999999)
                if target == "สิบ":
                    check_val = num % 10
                    round_base = (num // 10) * 10
                    if check_val >= 5: ans, explain = round_base + 10, f"หลักหน่วยคือเลข {check_val} (ตั้งแต่ 5 ขึ้นไป) จึงปัดขึ้น"
                    else: ans, explain = round_base, f"หลักหน่วยคือเลข {check_val} (น้อยกว่า 5) จึงปัดทิ้งเป็น 0"
                elif target == "ร้อย":
                    check_val = (num % 100) // 10
                    round_base = (num // 100) * 100
                    if check_val >= 5: ans, explain = round_base + 100, f"หลักสิบคือเลข {check_val} (ตั้งแต่ 5 ขึ้นไป) จึงปัดขึ้น"
                    else: ans, explain = round_base, f"หลักสิบคือเลข {check_val} (น้อยกว่า 5) จึงปัดทิ้งเป็น 0"
                else:
                    check_val = (num % 1000) // 100
                    round_base = (num // 1000) * 1000
                    if check_val >= 5: ans, explain = round_base + 1000, f"หลักร้อยคือเลข {check_val} (ตั้งแต่ 5 ขึ้นไป) จึงปัดขึ้น"
                    else: ans, explain = round_base, f"หลักร้อยคือเลข {check_val} (น้อยกว่า 5) จึงปัดทิ้งเป็น 0"
                q = f"จงหาค่าประมาณเป็น<b>จำนวนเต็ม{target}</b> ของ <b>{num:,}</b>"
                sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 การหาค่าประมาณเป็นจำนวนเต็ม{target} ให้พิจารณาเลขโดดในหลักที่อยู่ติดกันทางขวา<br>👉 ในข้อนี้ {explain}<br><b>ตอบ: {ans:,}</b></span>"

            elif actual_sub_t == "การบวก (แบบตั้งหลัก)":
                a = random.randint(100000, 999999) if not is_challenge else random.randint(1000000, 9999999)
                b = random.randint(100000, 999999) if not is_challenge else random.randint(1000000, 9999999)
                ans = a + b
                q_base = f"จงหาผลบวกของ <b>{a:,} + {b:,}</b>"
                table_html = generate_vertical_table_html(a, b, "+", result=ans, is_key=False)
                table_key = generate_vertical_table_html(a, b, "+", result=ans, is_key=True)
                q = f"{q_base}<br>{table_html}"
                sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>ตั้งหลักให้ตรงกัน แล้วบวกจากหลักหน่วย (ขวาไปซ้าย)<br>{table_key}</span>"

            elif actual_sub_t == "การลบ (แบบตั้งหลัก)":
                a = random.randint(100000, 999999) if not is_challenge else random.randint(1000000, 9999999)
                b = random.randint(50000, a - 1000)
                ans = a - b
                q_base = f"จงหาผลลบของ <b>{a:,} - {b:,}</b>"
                table_html = generate_vertical_table_html(a, b, "-", result=ans, is_key=False)
                table_key = generate_vertical_table_html(a, b, "-", result=ans, is_key=True)
                q = f"{q_base}<br>{table_html}"
                sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>ตั้งหลักให้ตรงกัน ลบจากขวาไปซ้าย หากหลักใดตัวตั้งน้อยกว่าให้ยืมหลักข้างหน้า<br>{table_key}</span>"

            elif actual_sub_t == "การคูณ (แบบตั้งหลัก)":
                a = random.randint(100, 9999) if not is_challenge else random.randint(5000, 99999)
                b = random.randint(12, 99) if not is_challenge else random.randint(101, 999)
                ans = a * b
                q_base = f"จงหาผลคูณของ <b>{a:,} × {b:,}</b>"
                table_html = generate_vertical_table_html(a, b, "×", result=ans, is_key=False)
                table_key = generate_vertical_table_html(a, b, "×", result=ans, is_key=True)
                q = f"{q_base}<br>{table_html}"
                sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>นำตัวคูณแต่ละหลักไปคูณตัวตั้ง แล้วนำผลคูณในแต่ละบรรทัดมาบวกกัน<br>{table_key}</span>"

            elif actual_sub_t == "การหารยาว":
                divisor = random.randint(2, 9) if not is_challenge else random.randint(11, 99)
                quotient = random.randint(1000, 9999)
                remainder = random.randint(0, divisor - 1)
                dividend = (divisor * quotient) + remainder
                equation_html = f"<div style='font-size: 24px; margin-bottom: 10px;'><b>{dividend:,} ÷ {divisor:,} = ?</b></div>"
                table_html = generate_long_division_step_by_step_html(divisor, dividend, equation_html, is_key=False)
                table_key = generate_long_division_step_by_step_html(divisor, dividend, equation_html, is_key=True)
                q = f"จงหาผลหารโดยวิธีหารยาว<br>{table_html}"
                ans_txt = f"{quotient:,}" if remainder == 0 else f"{quotient:,} เศษ {remainder:,}"
                sol = f"<span style='color:#2c3e50;'><b>เฉลยวิธีทำ (หารยาว):</b><br>{table_key}<br><b>ตอบ: {ans_txt}</b></span>"

            elif actual_sub_t == "แปลงเศษเกินเป็นจำนวนคละ":
                den = random.randint(3, 12) if not is_challenge else random.randint(13, 25)
                whole = random.randint(2, 9)
                num_rem = random.randint(1, den - 1)
                num_total = (whole * den) + num_rem
                frac_str = f_html(num_total, den)
                mixed_str = generate_mixed_number_html(whole, num_rem, den)
                q = f"จงแปลงเศษเกินต่อไปนี้ให้เป็นจำนวนคละ<br><br><div style='text-align:center; font-size:26px;'>{frac_str} = <span style='color:#2980b9;'>?</span></div>"
                sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 นำตัวเศษ (ด้านบน) หารด้วยตัวส่วน (ด้านล่าง)<br>👉 นำ {num_total} ÷ {den} <br>👉 จะได้ <b>{whole}</b> และเหลือเศษ <b>{num_rem}</b><br>👉 นำมาเขียนเป็นจำนวนคละได้คือ <b>{mixed_str}</b><br><b>ตอบ: {mixed_str}</b></span>"

            elif actual_sub_t == "การอ่านและการเขียนทศนิยม":
                dp = random.randint(1, 3)
                whole = random.randint(0, 99)
                if dp == 1:
                    dec = random.randint(1, 9)
                    num_str = f"{whole}.{dec}"
                elif dp == 2:
                    dec = random.randint(1, 99)
                    num_str = f"{whole}.{dec:02d}"
                else:
                    dec = random.randint(1, 999)
                    num_str = f"{whole}.{dec:03d}"
                thai_whole = generate_thai_number_text(str(whole)) if whole > 0 else "ศูนย์"
                thai_dec = "".join([["ศูนย์","หนึ่ง","สอง","สาม","สี่","ห้า","หก","เจ็ด","แปด","เก้า"][int(d)] for d in num_str.split(".")[1]])
                thai_read = f"{thai_whole}จุด{thai_dec}"
                mode = random.choice(["to_text", "to_num"])
                if mode == "to_text":
                    q = f"จงเขียนทศนิยม <b>{num_str}</b> เป็นคำอ่าน"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 ตัวเลขหน้าจุดทศนิยมให้อ่านแบบจำนวนนับปกติ<br>👉 ตัวเลขหลังจุดทศนิยมให้อ่านเรียงตัว<br><b>ตอบ: {thai_read}</b></span>"
                else:
                    q = f"จงเขียนคำอ่าน <b>\"{thai_read}\"</b> ให้เป็นตัวเลขทศนิยม"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 แปลงคำอ่านเป็นตัวเลข โดยตัวเลขหลังคำว่า 'จุด' ให้เขียนเรียงกันทีละหลัก<br><b>ตอบ: {num_str}</b></span>"

            elif actual_sub_t == "การบอกชนิดของมุม":
                angle = random.randint(10, 175)
                if angle < 90:
                    angle_type, reason = "มุมแหลม", "มีขนาดน้อยกว่า 90 องศา"
                elif 85 < angle < 95:
                    angle, angle_type, reason = 90, "มุมฉาก", "มีขนาดเท่ากับ 90 องศาพอดี"
                elif angle == 180:
                    angle_type, reason = "มุมตรง", "มีขนาดเท่ากับ 180 องศาพอดี"
                else:
                    angle_type, reason = "มุมป้าน", "มีขนาดมากกว่า 90 องศา แต่น้อยกว่า 180 องศา"
                q = f"มุมที่มีขนาด <b>{angle}°</b> คือมุมชนิดใด?<br><span style='font-size:18px; color:#7f8c8d;'>(มุมแหลม, มุมฉาก, มุมป้าน, มุมตรง)</span>"
                sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 มุม {angle}° {reason}<br>👉 ดังนั้นจึงจัดเป็น <b>{angle_type}</b><br><b>ตอบ: {angle_type}</b></span>"

            elif actual_sub_t == "การวัดขนาดของมุม (ไม้โปรแทรกเตอร์)":
                def draw_angle_feature_local(vx, vy, ax, ay, bx, by, r_arc, r_text, label, color_arc, color_text, is_x=False):
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
                    ty += 4 
                    font_size = "16px" if is_x else "13px"
                    return arc_svg + f'<text x="{tx}" y="{ty}" font-size="{font_size}" font-weight="bold" font-family="Sarabun" text-anchor="middle" fill="{color_text}">{label}</text>'

                def draw_angle_svg_local(mode, val1, val2, val3=""):
                    svg = '<div style="text-align:center; margin:15px 0;"><svg width="340" height="200">'
                    lbl_style = 'font-family:Sarabun; font-size:16px; font-weight:bold; fill:#2c3e50;'
                    vx, vy, phi = 170, 160, val2 
                    ax, ay, cx, cy = 40, 160, 300, 160 
                    bx, by = vx + 120 * math.cos(math.radians(phi)), vy - 120 * math.sin(math.radians(phi))
                    svg += f'<line x1="{ax}" y1="{ay}" x2="{cx}" y2="{cy}" stroke="#34495e" stroke-width="4"/>'
                    svg += f'<line x1="{vx}" y1="{vy}" x2="{bx}" y2="{by}" stroke="#c0392b" stroke-width="3"/>'
                    svg += f'<circle cx="{bx}" cy="{by}" r="3" fill="#c0392b"/>'
                    svg += f'<text x="{ax-15}" y="{ay+5}" {lbl_style}>A</text>'
                    svg += f'<text x="{cx+5}" y="{cy+5}" {lbl_style}>B</text>'
                    svg += f'<text x="{bx-5}" y="{by-10}" {lbl_style}>C</text>'
                    svg += f'<text x="{vx-5}" y="{vy+20}" {lbl_style}>O</text>'
                    svg += draw_angle_feature_local(vx, vy, ax, ay, bx, by, 28, 45, f"{val1}°", "#2ecc71", "#c0392b")
                    svg += draw_angle_feature_local(vx, vy, bx, by, cx, cy, 28, 45, val2 if val3=="" else val3, "#2ecc71", "#2980b9", is_x=True)
                    return svg + '</svg></div>'

                mode = random.choice(["read_protractor", "calc_angle"])
                if mode == "read_protractor":
                    base_deg = random.choice([0, 10, 20])
                    angle = random.randint(30, 150)
                    end_deg = base_deg + angle
                    q = f"ในการวัดขนาดของมุม <b>AOB</b> ด้วยไม้โปรแทรกเตอร์<br>ถ้าแขน OA ชี้ที่สเกลตัวเลข <b>{base_deg}°</b> และแขน OB ชี้ที่สเกลตัวเลข <b>{end_deg}°</b><br>มุม AOB มีขนาดกี่องศา?"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 นำตัวเลขที่แขนของมุมทั้งสองข้างชี้มาลบกัน เพื่อหาขนาดความกว้างของมุม<br>👉 {end_deg}° - {base_deg}° = <b>{angle}°</b><br><b>ตอบ: {angle} องศา</b></span>"
                else:
                    ans = random.randint(25, 160)
                    svg = draw_angle_svg_local("straight", 180-ans, ans, "?")
                    q = f"ถ้านำไม้โปรแทรกเตอร์มาวัดมุม <b>x</b> ในรูป จะได้ขนาดกี่องศา?<br>(กำหนดให้เส้นตรงด้านล่างคือ 180°)<br>{svg}"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 มุมบนเส้นตรงมีขนาดรวม 180°<br>👉 ถ้ามุมอีกฝั่งกาง {180-ans}° มุม x จะเท่ากับ 180° - {180-ans}° = <b>{ans}°</b><br><b>ตอบ: {ans} องศา</b></span>"

            elif actual_sub_t == "การหาความยาวรอบรูปสี่เหลี่ยมมุมฉาก":
                def draw_rect_svg_local(w_val, h_val, w_lbl, h_lbl, fill_color="#eaf2f8"):
                    scale = 140 / max(w_val, h_val)
                    dw, dh = w_val * scale, h_val * scale
                    svg = f'<div style="text-align:center; margin: 15px 0;"><svg width="300" height="200">'
                    svg += f'<rect x="{150 - dw/2}" y="{100 - dh/2}" width="{dw}" height="{dh}" fill="{fill_color}" stroke="#2980b9" stroke-width="3"/>'
                    svg += f'<text x="150" y="{100 - dh/2 - 10}" font-family="Sarabun" font-size="16" font-weight="bold" fill="#c0392b" text-anchor="middle">{w_lbl}</text>'
                    svg += f'<text x="{150 + dw/2 + 10}" y="100" font-family="Sarabun" font-size="16" font-weight="bold" fill="#c0392b" text-anchor="start" dominant-baseline="middle">{h_lbl}</text>'
                    return svg + '</svg></div>'

                is_square = random.choice([True, False])
                if is_square:
                    side = random.randint(5, 25)
                    peri = 4 * side
                    svg = draw_rect_svg_local(side, side, f"{side} ม.", f"{side} ม.", "#fdf2e9")
                    q = f"จงหาความยาวรอบรูปของ<b>สี่เหลี่ยมจัตุรัส</b>ต่อไปนี้<br>{svg}"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 สูตรความยาวรอบรูปสี่เหลี่ยมจัตุรัส = 4 × ความยาวด้าน<br>👉 4 × {side} = <b>{peri} เมตร</b><br><b>ตอบ: {peri} เมตร</b></span>"
                else:
                    w, h = random.randint(4, 15), random.randint(16, 30)
                    peri = 2 * (w + h)
                    svg = draw_rect_svg_local(h, w, f"{h} ซม.", f"{w} ซม.", "#e8f8f5")
                    q = f"จงหาความยาวรอบรูปของ<b>สี่เหลี่ยมผืนผ้า</b>ต่อไปนี้<br>{svg}"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 สูตรความยาวรอบรูปสี่เหลี่ยมผืนผ้า = 2 × (กว้าง + ยาว)<br>👉 กว้าง + ยาว = {w} + {h} = {w+h}<br>👉 2 × {w+h} = <b>{peri} เซนติเมตร</b><br><b>ตอบ: {peri} เซนติเมตร</b></span>"

            elif actual_sub_t == "การหาพื้นที่รูปสี่เหลี่ยมมุมฉาก":
                def draw_rect_svg_local(w_val, h_val, w_lbl, h_lbl, fill_color="#eaf2f8"):
                    scale = 140 / max(w_val, h_val)
                    dw, dh = w_val * scale, h_val * scale
                    svg = f'<div style="text-align:center; margin: 15px 0;"><svg width="300" height="200">'
                    svg += f'<rect x="{150 - dw/2}" y="{100 - dh/2}" width="{dw}" height="{dh}" fill="{fill_color}" stroke="#2980b9" stroke-width="3"/>'
                    svg += f'<text x="150" y="{100 - dh/2 - 10}" font-family="Sarabun" font-size="16" font-weight="bold" fill="#c0392b" text-anchor="middle">{w_lbl}</text>'
                    svg += f'<text x="{150 + dw/2 + 10}" y="100" font-family="Sarabun" font-size="16" font-weight="bold" fill="#c0392b" text-anchor="start" dominant-baseline="middle">{h_lbl}</text>'
                    return svg + '</svg></div>'

                is_square = random.choice([True, False])
                if is_square:
                    side = random.randint(5, 25)
                    area = side * side
                    svg = draw_rect_svg_local(side, side, f"{side} ม.", f"{side} ม.", "#fdf2e9")
                    q = f"จงหาพื้นที่ของ<b>สี่เหลี่ยมจัตุรัส</b>ต่อไปนี้<br>{svg}"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 สูตรพื้นที่สี่เหลี่ยมจัตุรัส = ด้าน × ด้าน<br>👉 {side} × {side} = <b>{area:,} ตารางเมตร</b><br><b>ตอบ: {area:,} ตารางเมตร</b></span>"
                else:
                    w, h = random.randint(4, 15), random.randint(16, 30)
                    area = w * h
                    svg = draw_rect_svg_local(h, w, f"{h} ซม.", f"{w} ซม.", "#e8f8f5")
                    q = f"จงหาพื้นที่ของ<b>สี่เหลี่ยมผืนผ้า</b>ต่อไปนี้<br>{svg}"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 สูตรพื้นที่สี่เหลี่ยมผืนผ้า = กว้าง × ยาว<br>👉 {w} × {h} = <b>{area:,} ตารางเซนติเมตร</b><br><b>ตอบ: {area:,} ตารางเซนติเมตร</b></span>"

            elif actual_sub_t == "การแก้สมการ (บวก/ลบ)":
                var = random.choice(["A", "B", "x", "y", "ก", "ข"])
                a = random.randint(1000, 9999) if not is_challenge else random.randint(15000, 50000)
                op = random.choice(["+", "-"])
                if op == "+":
                    ans = random.randint(1000, 9999) if not is_challenge else random.randint(15000, 50000)
                    c = ans + a
                    q = f"จงแก้สมการเพื่อหาค่าของ <b>{var}</b> : <br><div style='text-align:center; font-size:24px; margin: 15px 0;'><b>{var} + {a:,} = {c:,}</b></div>"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 ย้ายตัวเลข <b>+{a:,}</b> ไปอยู่อีกฝั่ง โดยเปลี่ยนเครื่องหมายบวกเป็นลบ<br>👉 จะได้: {var} = {c:,} - {a:,}<br>👉 คำนวณ: {var} = <b>{ans:,}</b><br><b>ตอบ: {ans:,}</b></span>"
                else:
                    c = random.randint(1000, 9999) if not is_challenge else random.randint(15000, 50000)
                    ans = c + a
                    q = f"จงแก้สมการเพื่อหาค่าของ <b>{var}</b> : <br><div style='text-align:center; font-size:24px; margin: 15px 0;'><b>{var} - {a:,} = {c:,}</b></div>"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 ย้ายตัวเลข <b>-{a:,}</b> ไปอยู่อีกฝั่ง โดยเปลี่ยนเครื่องหมายลบเป็นบวก<br>👉 จะได้: {var} = {c:,} + {a:,}<br>👉 คำนวณ: {var} = <b>{ans:,}</b><br><b>ตอบ: {ans:,}</b></span>"

            else:
                q = f"⚠️ [ระบบผิดพลาด] ไม่พบเงื่อนไขสำหรับหัวข้อ: <b>{actual_sub_t}</b>"
                sol = "Error"
                
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
# UI Rendering
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
        if is_key:
            if "(แบบตั้งหลัก)" in sub_t or "หารยาว" in sub_t or "การคูณและการหารทศนิยม" in sub_t or "การบวกและการลบทศนิยม" in sub_t: 
                html += f'{item["solution"]}'
            else: 
                html += f'{item["question"]}<div class="sol-text">{item["solution"]}</div>'
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

selected_grade = st.sidebar.selectbox("📚 เลือกระดับชั้น:", ["ป.1", "ป.2", "ป.3", "ป.4", "ป.5", "ป.6"])
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

if st.sidebar.button("🚀 สั่งสร้างใบงานเดี๋ยวนี้", type="primary", use_container_width=True):
    with st.spinner("กำลังออกแบบรูปภาพและสร้างเฉลยแบบ Step-by-Step..."):
        
        qs = generate_questions_logic(selected_grade, selected_main, selected_sub, num_input, is_challenge)
        
        html_w = create_page(selected_grade, selected_sub, qs, is_key=False, q_margin=q_margin, ws_height=ws_height, brand_name=brand_name)
        html_k = create_page(selected_grade, selected_sub, qs, is_key=True, q_margin=q_margin, ws_height=ws_height, brand_name=brand_name)
        
        st.session_state['worksheet_html'] = html_w
        st.session_state['answerkey_html'] = html_k
        
        ebook_body = f'\n<div class="a4-wrapper">{extract_body(html_w)}</div>\n<div class="a4-wrapper">{extract_body(html_k)}</div>\n'
        
        full_ebook_html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap" rel="stylesheet"><style>@page {{ size: A4; margin: 15mm; }} @media screen {{ body {{ font-family: 'Sarabun', sans-serif; background-color: #525659; display: flex; flex-direction: column; align-items: center; padding: 40px 0; margin: 0; }} .a4-wrapper {{ width: 210mm; min-height: 297mm; background: white; margin-bottom: 30px; box-shadow: 0 10px 20px rgba(0,0,0,0.3); padding: 15mm; box-sizing: border-box; }} }} @media print {{ body {{ font-family: 'Sarabun', sans-serif; background: transparent; padding: 0; display: block; margin: 0; }} .a4-wrapper {{ width: 100%; min-height: auto; margin: 0; padding: 0; box-shadow: none; page-break-after: always; }} }} .header {{ text-align: center; border-bottom: 2px solid #333; margin-bottom: 10px; padding-bottom: 10px; }} .q-box {{ margin-bottom: {q_margin}; padding: 10px 15px; page-break-inside: avoid; font-size: 20px; line-height: 1.6; }} .workspace {{ height: {ws_height}; border: 2px dashed #bdc3c7; border-radius: 8px; margin: 15px 0; padding: 10px; color: #95a5a6; font-size: 16px; background-color: #fafbfc; }} .ans-line {{ margin-top: 10px; border-bottom: 1px dotted #999; width: 80%; height: 30px; font-weight: bold; font-size: 20px; display: flex; align-items: flex-end; padding-bottom: 5px; }} .sol-text {{ color: #333; font-size: 18px; display: block; margin-top: 15px; padding: 15px; background-color: #f1f8ff; border-left: 4px solid #3498db; border-radius: 4px; line-height: 1.6; }} .page-footer {{ text-align: right; font-size: 14px; color: #95a5a6; margin-top: 20px; border-top: 1px solid #eee; padding-top: 10px; }} </style></head><body>{ebook_body}</body></html>"""

        filename_base = f"Std_{selected_grade}_{selected_sub}"
        st.session_state['ebook_html'] = full_ebook_html
        st.session_state['filename_base'] = f"{filename_base}_{int(time.time())}"
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(f"{filename_base}_Full_EBook.html", full_ebook_html.encode('utf-8'))
            zip_file.writestr(f"{filename_base}_Worksheet.html", html_w.encode('utf-8'))
            zip_file.writestr(f"{filename_base}_AnswerKey.html", html_k.encode('utf-8'))
        st.session_state['zip_data'] = zip_buffer.getvalue()

if 'ebook_html' in st.session_state:
    st.success(f"✅ ลิขสิทธิ์นี้เป็นของ บ้านทีเด็ด เท่านั้น ห้ามนำไปขาย หรือแจกจ่าย ก่อนได้รับอนุญาติ จาก บ้านทีเด็ด")
    c1, c2 = st.columns(2)
    with c1:
        st.download_button("📄 โหลดเฉพาะโจทย์", data=st.session_state['worksheet_html'], file_name=f"{st.session_state['filename_base']}_Worksheet.html", mime="text/html", use_container_width=True)
        st.download_button("🔑 โหลดเฉพาะเฉลย", data=st.session_state['answerkey_html'], file_name=f"{st.session_state['filename_base']}_AnswerKey.html", mime="text/html", use_container_width=True)
    with c2:
        st.download_button("📚 โหลดรวมเล่ม E-Book", data=st.session_state['ebook_html'], file_name=f"{st.session_state['filename_base']}_Full_EBook.html", mime="text/html", use_container_width=True)
        st.download_button("🗂️ โหลดแพ็กเกจ (.zip)", data=st.session_state['zip_data'], file_name=f"{st.session_state['filename_base']}.zip", mime="application/zip", use_container_width=True)
    st.markdown("---")
    components.html(st.session_state['ebook_html'], height=800, scrolling=True)
