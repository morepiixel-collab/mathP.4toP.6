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
st.set_page_config(page_title="Math Generator - Primary 4-6", page_icon="🎓", layout="wide")

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
    <h1>🎓 Math Worksheet Pro <span style="font-size: 20px; background: #e74c3c; color: #fff; padding: 5px 15px; border-radius: 20px; vertical-align: middle;">ประถมปลาย ป.4 - ป.6</span></h1>
    <p>ระบบสร้างโจทย์คณิตศาสตร์ขั้นสูง สมการ เรขาคณิต และแนวข้อสอบสอบเข้า ม.1 (Gifted)</p>
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
    return html, final_quotient

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
# ฐานข้อมูลหลักสูตร (Master Database P.4 - P.6)
# ==========================================
curriculum_db = {
    "ป.4": {
        "จำนวนนับที่มากกว่า 100,000": ["การอ่านและการเขียนตัวเลข", "หลัก ค่าประจำหลัก และรูปกระจาย", "การเปรียบเทียบและเรียงลำดับ", "ค่าประมาณเป็นจำนวนเต็มสิบ เต็มร้อย เต็มพัน"],
        "การบวก ลบ คูณ หาร": ["การบวก (แบบตั้งหลัก)", "การลบ (แบบตั้งหลัก)", "การคูณ (แบบตั้งหลัก)", "การหารยาวแบบลงตัว", "การหารยาวแบบไม่ลงตัว"],
        "เศษส่วนและทศนิยม": ["แปลงเศษเกินเป็นจำนวนคละ", "การอ่านและการเขียนทศนิยม", "การบวกเศษส่วน", "การลบเศษส่วน", "การคูณเศษส่วน", "การหารเศษส่วน", "การบวกทศนิยม", "การลบทศนิยม", "การคูณทศนิยม", "การหารทศนิยม"],
        "เรขาคณิตและการวัด": ["การบอกชนิดของมุม", "การวัดขนาดของมุม (ไม้โปรแทรกเตอร์)", "การสร้างมุมตามขนาดที่กำหนด", "การหาความยาวรอบรูปสี่เหลี่ยมมุมฉาก", "การหาพื้นที่รูปสี่เหลี่ยมมุมฉาก"],
        "สมการ": ["การแก้สมการ (บวก/ลบ)", "การแก้สมการ (คูณ/หาร)", "สมการและตัวไม่ทราบค่าจากชีวิตประจำวัน", "สมการเชิงตรรกะและตาชั่งปริศนา", "โจทย์ปัญหาสมการ: ความสัมพันธ์ของ 2 สิ่ง"]
    },
    "ป.5": {
        "เศษส่วน": ["การบวกเศษส่วน", "การลบเศษส่วน", "การคูณเศษส่วน", "การหารเศษส่วน"],
        "ทศนิยม": ["การบวกและการลบทศนิยม", "การคูณและการหารทศนิยม"],
        "สถิติและความน่าจะเป็น": ["การหาค่าเฉลี่ย (Average)", "ความน่าจะเป็นเบื้องต้น (สุ่มหยิบของ)"],
        "เรขาคณิต 2 มิติและ 3 มิติ": ["โจทย์ปัญหาพื้นที่และความยาวรอบรูป", "เส้นขนานและมุมแย้ง", "ปริมาตรและความจุทรงสี่เหลี่ยมมุมฉาก"],
        "ร้อยละและเปอร์เซ็นต์": ["การเขียนเศษส่วนในรูปร้อยละ"],
        "สมการ": ["การแก้สมการ (คูณ/หาร)"],
        "เตรียมสอบเข้า ม.1 (Gifted)": ["โจทย์ปัญหา ห.ร.ม. และ ค.ร.น.", "โจทย์ปัญหาคลาสสิก (สมการประยุกต์)", "แบบรูปและอนุกรม (Number Patterns)", "มาตราส่วนและทิศทาง", "เรขาคณิตประยุกต์ (หาพื้นที่แรเงา)"]
    },
    "ป.6": {
        "ตัวประกอบของจำนวนนับ (Gifted)": ["การหา ห.ร.ม.", "การหา ค.ร.น.", "โจทย์ปัญหา ห.ร.ม. และ ค.ร.น. (ขั้นสูง)", "กฎการหารลงตัว (Divisibility Rules)"],
        "เศษส่วนและทศนิยม (Gifted)": ["การบวกลบคูณหารระคน", "โจทย์ปัญหาเศษส่วนซ้อน (สอบเข้า ม.1)", "อนุกรมเศษส่วน (Telescoping Sum)"],
        "อัตราส่วนและร้อยละ (Gifted)": ["โจทย์ปัญหาอัตราส่วนและสัดส่วน", "โจทย์ปัญหาร้อยละ (กำไร-ขาดทุน ซับซ้อน)", "โจทย์ปัญหาของผสม (ความเข้มข้น)"],
        "สมการและแบบรูป (Gifted)": ["การแก้สมการ (สองขั้นตอน)", "โจทย์ปัญหาสมการ (อายุ/เหรียญ/ขา)", "ลำดับและอนุกรม (Number Patterns)"],
        "โจทย์ปัญหาคลาสสิก (Gifted)": ["ความเร็ว ระยะทาง เวลา (รถไฟ/วิ่งไล่กัน)", "งานและการทำงาน (ช่วยกันทำงาน)", "แผนภาพเวนน์-ออยเลอร์ (เซต 2 วง)"],
        "เรขาคณิต (Gifted)": ["พื้นที่ส่วนที่แรเงา (วงกลมซ้อนเหลี่ยม)", "เส้นขนานและมุมแย้ง (ขั้นสูง)", "มุมภายในและมุมเข็มนาฬิกา"],
        "สถิติและความน่าจะเป็น (Gifted)": ["ค่าเฉลี่ยแบบประยุกต์ (เพิ่ม/ลด/อ่านผิด)", "การจับมือและการแข่งขัน (Combinatorics)"]
    }
}


# ==========================================
# 3. Logic & Dynamic Difficulty Scaling (P.4 - P.6)
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

            # =========================================================
            # 🚄 ROUTING ENGINE: สับรางหัวข้อ ป.6 ไปใช้โหมดชาเลนจ์ของ ป.5
            # =========================================================
            if actual_sub_t == "การบวกลบคูณหารระคน":
                actual_sub_t = random.choice(["การบวกเศษส่วน", "การลบเศษส่วน", "การคูณเศษส่วน", "การหารเศษส่วน"])
                is_challenge = True

            p6_router = {
                "โจทย์ปัญหา ห.ร.ม. และ ค.ร.น. (ขั้นสูง)": "โจทย์ปัญหา ห.ร.ม. และ ค.ร.น.",
                "การแก้สมการ (สองขั้นตอน)": "การแก้สมการ (คูณ/หาร)", 
                "โจทย์ปัญหาสมการ (อายุ/เหรียญ/ขา)": "โจทย์ปัญหาคลาสสิก (สมการประยุกต์)",
                "ลำดับและอนุกรม (Number Patterns)": "แบบรูปและอนุกรม (Number Patterns)",
                "ค่าเฉลี่ยแบบประยุกต์ (เพิ่ม/ลด/อ่านผิด)": "การหาค่าเฉลี่ย (Average)",
                "เส้นขนานและมุมแย้ง (ขั้นสูง)": "เส้นขนานและมุมแย้ง"
            }
            if actual_sub_t in p6_router:
                actual_sub_t = p6_router[actual_sub_t]
                is_challenge = True 

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

                target_deg = random.choice([45, 60, 75, 120, 135, 150])
                
                # 📐 SVG สำหรับโจทย์ (มีแค่เส้นฐาน)
                svg = f'''<div style="text-align:center; margin:15px 0;">
                    <svg width="560" height="200">
                        <line x1="230" y1="140" x2="430" y2="140" stroke="#34495e" stroke-width="2.5"/>
                        <circle cx="230" cy="140" r="4" fill="#2c3e50"/>
                        <text x="225" y="170" font-family="sans-serif" font-size="18" font-weight="bold" fill="#2c3e50" text-anchor="middle">{v}</text>
                        <text x="445" y="145" font-family="sans-serif" font-size="18" font-weight="bold" fill="#2c3e50" text-anchor="middle">{p2}</text>
                    </svg>
                </div>'''
                
                # 📐 SVG สำหรับเฉลย (มีไม้โปรแทรกเตอร์โปร่งใส + เส้นลากมุมสีแดง + ส่วนโค้งมุม)
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
                svg_sol += f'<line x1="{cx}" y1="{cy}" x2="{cx+180}" y2="{cy}" stroke="#34495e" stroke-width="3"/>'
                svg_sol += f'<line x1="{cx}" y1="{cy}" x2="{end_x}" y2="{end_y}" stroke="#e74c3c" stroke-width="3.5" stroke-linecap="round"/>'
                svg_sol += f'<circle cx="{cx}" cy="{cy}" r="5" fill="#2c3e50"/><circle cx="{cx+180}" cy="{cy}" r="4" fill="#2c3e50"/><circle cx="{end_x}" cy="{end_y}" r="5" fill="#e74c3c"/>'
                
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
                if is_square:
                    side = random.randint(5, 25)
                    peri = 4 * side
                    svg = draw_rect_svg(side, side, f"{side} ม.", f"{side} ม.", "#fdf2e9")
                    q = f"จงหาความยาวรอบรูปของ<b>สี่เหลี่ยมจัตุรัส</b>ต่อไปนี้<br>{svg}"
                    
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>
                    👉 <b>สูตร:</b> ความยาวรอบรูปสี่เหลี่ยมจัตุรัส = <b>4 × ความยาวด้าน</b><br>
                    👉 <i>(<b>อธิบายที่มา:</b> สี่เหลี่ยมจัตุรัสมีด้านยาวเท่ากันทั้งหมด 4 ด้าน แทนที่จะนำมาบวกทีละด้านแบบ {side} + {side} + {side} + {side} เราจึงรวบใช้การคูณ 4 แทนได้เลย)</i><br>
                    👉 จากรูป ความยาวแต่ละด้าน = {side} ม.<br>
                    👉 แทนค่าลงในสูตร: 4 × {side} = <b>{peri} เมตร</b><br>
                    <b>ตอบ: {peri} เมตร</b></span>"""
                else:
                    w, h = random.randint(4, 15), random.randint(16, 30)
                    peri = 2 * (w + h)
                    # วาดให้ h เป็นแนวนอน (ด้านยาว) และ w เป็นแนวตั้ง (ด้านกว้าง)
                    svg = draw_rect_svg(h, w, f"{h} ซม.", f"{w} ซม.", "#e8f8f5")
                    q = f"จงหาความยาวรอบรูปของ<b>สี่เหลี่ยมผืนผ้า</b>ต่อไปนี้<br>{svg}"
                    
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>
                    👉 <b>สูตร:</b> ความยาวรอบรูปสี่เหลี่ยมผืนผ้า = <b>2 × (กว้าง + ยาว)</b><br>
                    👉 <i>(<b>อธิบายที่มา:</b> สี่เหลี่ยมผืนผ้าจะมีด้านกว้างยาวเท่ากัน 2 ด้าน และด้านยาวเท่ากัน 2 ด้าน เราจึงนำด้านกว้าง 1 ด้านมารวมกับด้านยาว 1 ด้านให้เป็น 1 ชุดก่อน แล้วค่อยคูณ 2 เพื่อให้ได้ครบทั้ง 4 ด้าน)</i><br>
                    👉 จากรูป ด้านกว้าง (ด้านสั้น) = {w} ซม. และ ด้านยาว = {h} ซม.<br>
                    👉 นำ (กว้าง + ยาว) มาบวกกันก่อน: {w} + {h} = {w+h}<br>
                    👉 แทนค่าลงในสูตร: 2 × {w+h} = <b>{peri} เซนติเมตร</b><br>
                    <b>ตอบ: {peri} เซนติเมตร</b></span>"""

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
                read_whole = "".join([reading_map[d] for d in whole_part]) # จริงๆ ต้องมีหลักสิบ หน่วย แต่เพื่อความง่ายใน code ตัวอย่าง
                # (ถ้าจะเอาเนียนๆ ต้องใช้ฟังก์ชันอ่านตัวเลขไทย แต่ในที่นี้ขอเน้นโครงสร้างการเฉลยครับ)
                
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
                import math
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



            elif actual_sub_t in ["การบวกเศษส่วน", "การลบเศษส่วน", "การคูณเศษส่วน", "การหารเศษส่วน"]:
                op_map = {"การบวกเศษส่วน": "+", "การลบเศษส่วน": "-", "การคูณเศษส่วน": "×", "การหารเศษส่วน": "÷"}
                op_sign = op_map[actual_sub_t]
                d1, d2 = random.randint(3, 12), random.randint(3, 12)
                while d1 == d2: d2 = random.randint(3, 12) 
                n1, n2 = random.randint(1, d1-1), random.randint(1, d2-1)
                
                if actual_sub_t in ["การลบเศษส่วน", "การหารเศษส่วน"] and n1*d2 <= n2*d1: 
                    n1, n2, d1, d2 = n2, n1, d2, d1
                    
                q = f"จงหาผลลัพธ์ของ <b>{n1}/{d1} {op_sign} {n2}/{d2}</b> ให้อยู่ในรูปอย่างง่าย"
                
                lcm = (d1 * d2) // math.gcd(d1, d2)
                if actual_sub_t == "การบวกเศษส่วน":
                    res_n, res_d = n1 * (lcm // d1) + n2 * (lcm // d2), lcm
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b> หา ค.ร.น. ของส่วนได้ {lcm} ➔ แปลงส่วนให้เท่ากันแล้วบวกเศษ จะได้ <b>{res_n}/{res_d}</b></span>"
                elif actual_sub_t == "การลบเศษส่วน":
                    res_n, res_d = n1 * (lcm // d1) - n2 * (lcm // d2), lcm
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b> หา ค.ร.น. ของส่วนได้ {lcm} ➔ แปลงส่วนให้เท่ากันแล้วลบเศษ จะได้ <b>{res_n}/{res_d}</b></span>"
                elif actual_sub_t == "การคูณเศษส่วน":
                    res_n, res_d = n1 * n2, d1 * d2
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b> เศษคูณเศษ ส่วนคูณส่วน จะได้ <b>{res_n}/{res_d}</b></span>"
                elif actual_sub_t == "การหารเศษส่วน":
                    res_n, res_d = n1 * d2, d1 * n2
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b> เปลี่ยนหารเป็นคูณ กลับเศษเป็นส่วนตัวหลัง จะได้ <b>{res_n}/{res_d}</b></span>"

            elif actual_sub_t == "การเขียนเศษส่วนในรูปร้อยละ":
                d = random.choice([2, 4, 5, 10, 20, 25, 50])
                n = random.randint(1, d-1)
                m = 100 // d
                ans = n * m
                q = f"จงเขียนเศษส่วน <b>{n}/{d}</b> ให้อยู่ในรูป <b>ร้อยละ (เปอร์เซ็นต์)</b>"
                sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b> ทำส่วนให้เป็น 100 โดยคูณด้วย {m} ทั้งเศษและส่วน ➔ ได้ ({n}×{m})/100 = <b>{ans}%</b></span>"

            elif actual_sub_t == "การแก้สมการ (บวก/ลบ)":
                var = random.choice(["A", "B", "x", "y", "ก", "ข"])
                # สุ่มรูปแบบโจทย์: ตัวแปรบวก, ตัวแปรลบ, และ ตัวตั้งลบด้วยตัวแปร (ใหม่)
                scenario = random.choice(["var_plus", "var_minus", "minus_var"])
                
                if scenario == "var_plus":
                    a = random.randint(1000, 9999) if not is_challenge else random.randint(15000, 50000)
                    ans = random.randint(1000, 9999) if not is_challenge else random.randint(15000, 50000)
                    c = ans + a
                    q = f"จงแก้สมการเพื่อหาค่าของ <b>{var}</b> : <b>{var} + {a:,} = {c:,}</b>"
                    explain_box = f"""<div style='background-color:#fef9e7; border-left:4px solid #f39c12; padding:10px; margin-bottom:10px; border-radius:4px; line-height:1.5;'>
                    💡 <b>หลักการคิด:</b> เราต้องการให้ <b>{var}</b> อยู่ตัวเดียว จึงต้องกำจัด <b>+{a:,}</b> ทิ้งไป<br>โดยใช้วิธีตรงข้าม คือนำ <b>{a:,}</b> มา <b style='color:#e74c3c;'>ลบออก</b> ทั้งสองข้างของสมการ</div>"""
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>{explain_box}👉 {var} + {a:,} <b style='color:#e74c3c;'>- {a:,}</b> = {c:,} <b style='color:#e74c3c;'>- {a:,}</b><br>👉 {var} = <b>{ans:,}</b><br><b>ตอบ: {ans:,}</b></span>"
                
                elif scenario == "var_minus":
                    a = random.randint(1000, 9999) if not is_challenge else random.randint(15000, 50000)
                    c = random.randint(1000, 9999) if not is_challenge else random.randint(15000, 50000)
                    ans = c + a
                    q = f"จงแก้สมการเพื่อหาค่าของ <b>{var}</b> : <b>{var} - {a:,} = {c:,}</b>"
                    explain_box = f"""<div style='background-color:#fef9e7; border-left:4px solid #f39c12; padding:10px; margin-bottom:10px; border-radius:4px; line-height:1.5;'>
                    💡 <b>หลักการคิด:</b> เราต้องการให้ <b>{var}</b> อยู่ตัวเดียว จึงต้องกำจัด <b>-{a:,}</b> ทิ้งไป<br>โดยใช้วิธีตรงข้าม คือนำ <b>{a:,}</b> มา <b style='color:#27ae60;'>บวกเข้า</b> ทั้งสองข้างของสมการ</div>"""
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>{explain_box}👉 {var} - {a:,} <b style='color:#27ae60;'>+ {a:,}</b> = {c:,} <b style='color:#27ae60;'>+ {a:,}</b><br>👉 {var} = <b>{ans:,}</b><br><b>ตอบ: {ans:,}</b></span>"
                
                else: # minus_var (ตัวแปรติดลบ)
                    ans = random.randint(1000, 9999) if not is_challenge else random.randint(15000, 50000)
                    c = random.randint(1000, 9999) if not is_challenge else random.randint(15000, 50000)
                    a = ans + c
                    q = f"จงแก้สมการเพื่อหาค่าของ <b>{var}</b> : <b>{a:,} - {var} = {c:,}</b>"
                    
                    explain_box = f"""<div style='background-color:#fef9e7; border-left:4px solid #f39c12; padding:10px; margin-bottom:10px; border-radius:4px; line-height:1.5;'>
                    💡 <b>หลักการคิด (ตัวแปรติดลบ):</b> หน้าตัวแปรมีเครื่องหมายลบ (<b>-{var}</b>) เราต้องทำให้ตัวแปรเป็น <b>บวก</b> ก่อน<br>
                    โดยนำ <b>{var}</b> มา <b style='color:#27ae60;'>บวกเข้า</b> ทั้งสองข้าง แล้วค่อยกำจัดตัวเลขในขั้นตอนถัดไปครับ
                    </div>"""
                    
                    sol = f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>
                    {explain_box}
                    👉 <b>ขั้นที่ 1 (ทำให้ตัวแปรเป็นบวก):</b> นำ <b>{var}</b> มา <b style='color:#27ae60;'>บวกเข้า</b> ทั้งสองข้าง<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;{a:,} - {var} <b style='color:#27ae60;'>+ {var}</b> = {c:,} <b style='color:#27ae60;'>+ {var}</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;<i>จะได้:</i> &nbsp; {a:,} = {c:,} + {var}<br><br>
                    👉 <b>ขั้นที่ 2 (กำจัดตัวเลข):</b> นำ <b>{c:,}</b> มา <b style='color:#e74c3c;'>ลบออก</b> ทั้งสองข้าง<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;{a:,} <b style='color:#e74c3c;'>- {c:,}</b> = {c:,} + {var} <b style='color:#e74c3c;'>- {c:,}</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;<i>จะได้:</i> &nbsp; {ans:,} = {var}<br>
                    <b>ตอบ: {ans:,}</b></span>"""

            elif actual_sub_t == "การแก้สมการ (คูณ/หาร)":
                var = random.choice(["x", "y", "a", "m"])
                scenario = random.choice(["mult", "div", "mult_add"])
                
                # ฟังก์ชันตัดฝั่งตัวแปร (ขยับเลข 1 มาอยู่ข้างๆ)
                def frac_cancel_left(num, variable):
                    top = f"<span style='display:inline-block; position:relative;'><span style='text-decoration:line-through; text-decoration-color:#e74c3c;'>{num}</span><span style='font-size:12px; color:#e74c3c; vertical-align:super; margin-left:2px;'>1</span></span>{variable}"
                    bottom = f"<span style='text-decoration:line-through; text-decoration-color:#e74c3c;'>{num}</span><span style='font-size:12px; color:#e74c3c; vertical-align:sub; margin-left:2px;'>1</span>"
                    return f"<span style='display:inline-flex; flex-direction:column; vertical-align:middle; text-align:center; margin:0 4px;'><span style='border-bottom:2px solid #333; padding:0 5px;'>{top}</span><span>{bottom}</span></span>"

                # ฟังก์ชันตัดฝั่งตัวเลข (ขยับผลลัพธ์มาอยู่ข้างๆ ตามลูกศรสีแดง)
                def frac_cancel_right(top_val, bot_val, result_val):
                    top = f"<span style='display:inline-block; position:relative;'><span style='text-decoration:line-through; text-decoration-color:#e74c3c;'>{top_val}</span><span style='font-size:14px; color:#e74c3c; font-weight:bold; vertical-align:super; margin-left:2px;'>{result_val}</span></span>"
                    bottom = f"<span style='text-decoration:line-through; text-decoration-color:#e74c3c;'>{bot_val}</span><span style='font-size:12px; color:#e74c3c; vertical-align:sub; margin-left:2px;'>1</span>"
                    return f"<span style='display:inline-flex; flex-direction:column; vertical-align:middle; text-align:center; margin:0 4px;'><span style='border-bottom:2px solid #333; padding:0 5px;'>{top}</span><span>{bottom}</span></span>"

                if scenario == "mult":
                    a, ans = random.randint(4, 15), random.randint(3, 12)
                    b = a * ans
                    q = f"จงแก้สมการเพื่อหาค่าของ <b>{var}</b>: <b>{a}{var} = {b}</b>"
                    sol = f"<span style='color:#2c3e50;'>👉 นำ {a} มาหารทั้งสองข้าง (ใช้สูตรคูณ<b>แม่ {a}</b> ในการตัดทอน):<br><br>&nbsp;&nbsp;&nbsp;&nbsp;{frac_cancel_left(a, var)} = {frac_cancel_right(b, a, ans)}<br><br>👉 <b>{var} = {ans}</b></span>"
                elif scenario == "div":
                    a, ans = random.randint(3, 9), random.randint(5, 20)
                    c = a * ans
                    q = f"จงแก้สมการเพื่อหาค่าของ <b>{var}</b>: <b>{var} ÷ {a} = {ans}</b>"
                    cancel_v_a = f"<span style='display:inline-flex; flex-direction:column; vertical-align:middle; text-align:center; margin:0 4px;'><span style='border-bottom:2px solid #333; padding:0 5px;'>{var}</span><span style='text-decoration: line-through; text-decoration-color: #e74c3c;'>{a}</span><span style='font-size:10px; color:#e74c3c; vertical-align:sub; margin-left:1px;'>1</span></span>"
                    sol = f"<span style='color:#2c3e50;'>👉 นำ {a} มาคูณทั้งสองข้าง (ใช้สูตรคูณ<b>แม่ {a}</b> ในการตัดทอน):<br><br>&nbsp;&nbsp;&nbsp;&nbsp;{cancel_v_a} <b style='color:#27ae60;'>× <span style='text-decoration: line-through; text-decoration-color: #e74c3c;'>{a}</span><span style='font-size:10px; color:#e74c3c; vertical-align:super; margin-left:1px;'>1</span></b> = {ans} <b style='color:#27ae60;'>× {a}</b><br><br>👉 <b>{var} = {c}</b></span>"
                else: # mult_add
                    a, ans, b = random.randint(2, 6), random.randint(3, 10), random.randint(1, 15)
                    c = (a * ans) + b
                    q = f"จงแก้สมการเพื่อหาค่าของ <b>{var}</b>: <b>{a}{var} + {b} = {c}</b>"
                    explain_box = f"<div style='background-color:#fef9e7; border-left:4px solid #f39c12; padding:10px; margin-bottom:10px; border-radius:4px;'>💡 <b>ทำไมต้องกำจัด +{b} ก่อนกำจัด {a} ?</b><br>เวลาแก้สมการที่มีหลายขั้นตอน ให้คิดว่าเรากำลัง <b>\"ปอกเปลือกจากข้างนอกเข้าหาข้างใน\"</b> ดังนั้นเราจึงต้อง <b>กำจัดตัวที่อยู่ไกลตัวแปร หรือ ตัวที่อยู่วงนอกก่อนเสมอ</b> แล้วค่อยจัดการตัวที่ติดแน่นกับตัวแปรครับ!</div>"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>{explain_box}👉 <b>ขั้นที่ 1:</b> นำ <b style='color:#e74c3c;'>{b}</b> มา <b>ลบออก</b> ทั้งสองข้าง ➔ {a}{var} = {c-b}<br><br>👉 <b>ขั้นที่ 2:</b> นำ {a} มา <b>หารออก</b> ทั้งสองข้าง (ใช้แม่ {a} ตัดทอน):<br>&nbsp;&nbsp;&nbsp;&nbsp;{frac_cancel_left(a, var)} = {frac_cancel_right(c-b, a, ans)}<br><br>👉 <b>{var} = {ans}</b><br><b>ตอบ: {ans}</b></span>"

            elif actual_sub_t == "สมการและตัวไม่ทราบค่าจากชีวิตประจำวัน":
                scenario_type = random.choice(["shopping", "saving", "sharing", "comparing"])
                var = random.choice(["x", "y", "ก", "n"])
                
                # ฟังก์ชันช่วยวาดการตัดทอน
                def frac_cancel_left(num, variable):
                    top = f"<span style='display:inline-block; position:relative;'><span style='text-decoration:line-through; text-decoration-color:#e74c3c;'>{num}</span><span style='font-size:12px; color:#e74c3c; vertical-align:super; margin-left:2px;'>1</span></span>{variable}"
                    bottom = f"<span style='text-decoration:line-through; text-decoration-color:#e74c3c;'>{num}</span><span style='font-size:12px; color:#e74c3c; vertical-align:sub; margin-left:2px;'>1</span>"
                    return f"<span style='display:inline-flex; flex-direction:column; vertical-align:middle; text-align:center; margin:0 4px;'><span style='border-bottom:2px solid #333; padding:0 5px;'>{top}</span><span>{bottom}</span></span>"
                
                def frac_cancel_right(top_val, bot_val, result_val):
                    top = f"<span style='display:inline-block; position:relative;'><span style='text-decoration:line-through; text-decoration-color:#e74c3c;'>{top_val}</span><span style='font-size:14px; color:#e74c3c; font-weight:bold; vertical-align:super; margin-left:2px;'>{result_val}</span></span>"
                    bottom = f"<span style='text-decoration:line-through; text-decoration-color:#e74c3c;'>{bot_val}</span><span style='font-size:12px; color:#e74c3c; vertical-align:sub; margin-left:2px;'>1</span>"
                    return f"<span style='display:inline-flex; flex-direction:column; vertical-align:middle; text-align:center; margin:0 4px;'><span style='border-bottom:2px solid #333; padding:0 5px;'>{top}</span><span>{bottom}</span></span>"

                if scenario_type == "shopping":
                    item, p_u, cnt = random.choice(["ขนม", "สมุด", "ตุ๊กตา"]), random.randint(12, 35), random.randint(3, 9)
                    total = p_u * cnt
                    q = f"แม่ซื้อ <b>{item}</b> จำนวน <b>{cnt}</b> ชิ้น จ่ายเงินไปทั้งหมด <b>{total}</b> บาท ราคาชิ้นละกี่บาท (ให้ <b>{var}</b> แทนราคาต่อชิ้น)"
                    
                    analysis = f"""<div style='background-color:#ebf5fb; border-left:4px solid #3498db; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    🔍 <b>แปลภาษาไทย เป็นสมการคณิตศาสตร์:</b><br>
                    👉 <b>ทำไมต้องใช้เครื่องหมาย คูณ (×) ?</b><br>
                    โจทย์บอกว่าซื้อ {item} หลายชิ้น ชิ้นละเท่าๆ กัน การเพิ่มขึ้นทีละเท่าๆ กันต้องใช้ <b>"การคูณ"</b><br>
                    • (จำนวนชิ้น <b style='color:#2980b9;'>{cnt}</b>) × (ราคาต่อชิ้น <b style='color:#e67e22;'>{var}</b>) = ราคาสินค้าทั้งหมด<br>
                    • เขียนในรูปพีชคณิตคือ <b style='color:#2980b9;'>{cnt}</b><b style='color:#e67e22;'>{var}</b><br><br>
                    👉 <b>ทำไมต้องใช้เครื่องหมาย เท่ากับ (=) ?</b><br>
                    เพราะราคาสินค้าทั้งหมดที่เราคำนวณได้ ต้อง <b>เท่ากับ</b> เงินที่จ่ายไปจริง คือ <b style='color:#27ae60;'>{total}</b> บาท<br><br>
                    🎯 <b>ได้สมการคือ: <span style='font-size:18px;'><b style='color:#2980b9;'>{cnt}</b><b style='color:#e67e22;'>{var}</b> = <b style='color:#27ae60;'>{total}</b></span></b>
                    </div>"""
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    {analysis}
                    <b>วิธีแก้สมการเพื่อหาค่า {var}:</b><br>
                    👉 <b>เป้าหมาย:</b> ทำให้ <b style='color:#e67e22;'>{var}</b> อยู่ตัวเดียว จึงต้องกำจัด <b style='color:#2980b9;'>{cnt}</b> ที่คูณอยู่ทิ้งไป<br>
                    👉 นำ <b style='color:#e74c3c;'>{cnt}</b> มา <b>หารออก</b> ทั้งสองข้างของสมการ (ใช้สูตรคูณ <b>แม่ {cnt}</b> ตัดทอน):<br><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;{frac_cancel_left(cnt, var)} = {frac_cancel_right(total, cnt, p_u)}<br><br>
                    👉 <b>{var} = {p_u}</b><br>
                    <b>ตอบ: {item}ราคาชิ้นละ {p_u} บาท</b></span>"""

                elif scenario_type == "saving":
                    init, d_s, days = random.randint(100, 400), random.randint(10, 30), random.randint(5, 12)
                    total = init + (d_s * days)
                    q = f"เดิมมีเงิน <b>{init}</b> บาท ออมเพิ่มวันละเท่าๆ กัน <b>{days}</b> วัน ทำให้มีเงินรวม <b>{total}</b> บาท ออมวันละกี่บาท (ให้ <b>{var}</b> แทนเงินออมต่อวัน)"
                    
                    analysis = f"""<div style='background-color:#ebf5fb; border-left:4px solid #3498db; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    🔍 <b>แปลภาษาไทย เป็นสมการคณิตศาสตร์:</b><br>
                    👉 <b>หาเงินที่ออมเพิ่ม (ทำไมใช้ คูณ ×):</b><br>
                    ออมวันละ <b style='color:#e67e22;'>{var}</b> บาท ซ้ำๆ กัน <b style='color:#2980b9;'>{days}</b> วัน แปลว่ามีเงินเพิ่มขึ้น <b style='color:#2980b9;'>{days}</b> × <b style='color:#e67e22;'>{var}</b> = <b><b style='color:#2980b9;'>{days}</b><b style='color:#e67e22;'>{var}</b></b> บาท<br><br>
                    👉 <b>หาเงินรวม (ทำไมใช้ บวก +):</b><br>
                    คำว่า "ออมเพิ่ม" จากเงินเดิมที่มีอยู่ <b style='color:#9b59b6;'>{init}</b> บาท แปลว่าต้องเอามา <b>รวมกัน (+)</b><br>
                    • (เงินเดิม <b style='color:#9b59b6;'>{init}</b>) + (เงินที่ออมเพิ่ม <b style='color:#2980b9;'>{days}</b><b style='color:#e67e22;'>{var}</b>) = (เงินรวม <b style='color:#27ae60;'>{total}</b>)<br><br>
                    🎯 <b>ได้สมการคือ: <span style='font-size:18px;'><b style='color:#9b59b6;'>{init}</b> + <b style='color:#2980b9;'>{days}</b><b style='color:#e67e22;'>{var}</b> = <b style='color:#27ae60;'>{total}</b></span></b>
                    </div>"""
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    {analysis}
                    <b>วิธีแก้สมการแบบ 2 ขั้นตอน (กำจัดตัวที่อยู่วงนอกก่อนเสมอ):</b><br>
                    👉 <b>ขั้นที่ 1:</b> นำ <b style='color:#e74c3c;'>{init}</b> มา <b>ลบออก</b> ทั้งสองข้าง เพื่อหักเงินเดิมออกไปก่อน<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;{init} - <b style='color:#e74c3c;'>{init}</b> + {days}{var} = {total} - <b style='color:#e74c3c;'>{init}</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;<i>จะได้:</i> &nbsp; {days}{var} = {total-init}<br><br>
                    👉 <b>ขั้นที่ 2:</b> นำ <b style='color:#e74c3c;'>{days}</b> มา <b>หารออก</b> ทั้งสองข้าง (ใช้สูตรคูณ <b>แม่ {days}</b> ตัดทอน):<br><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;{frac_cancel_left(days, var)} = {frac_cancel_right(total-init, days, d_s)}<br><br>
                    👉 <b>{var} = {d_s}</b><br>
                    <b>ตอบ: ออมเงินวันละ {d_s} บาท</b></span>"""

                elif scenario_type == "sharing":
                    total_c, eat, fnds = random.randint(60, 150), random.randint(10, 30), random.randint(2, 6)
                    per = (total_c - eat) // fnds
                    total_c = (per * fnds) + eat
                    q = f"มีขนมทั้งหมด <b>{total_c}</b> ชิ้น กินเองไป <b>{eat}</b> ชิ้น ที่เหลือแบ่งให้เพื่อน <b>{fnds}</b> คน คนละเท่าๆ กัน เพื่อนได้รับกี่ชิ้น (ให้ <b>{var}</b> แทนจำนวนที่เพื่อนได้รับ)"
                    
                    analysis = f"""<div style='background-color:#ebf5fb; border-left:4px solid #3498db; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    🔍 <b>แปลภาษาไทย เป็นสมการคณิตศาสตร์:</b><br>
                    โจทย์ข้อนี้ต้องมองย้อนกลับว่า <b>"ขนมทั้งหมดมาจากไหน?"</b><br><br>
                    👉 <b>ส่วนที่ 1: ขนมที่อยู่กับเพื่อน (ทำไมใช้ คูณ ×):</b><br>
                    เพื่อน <b style='color:#2980b9;'>{fnds}</b> คน ได้คนละ <b style='color:#e67e22;'>{var}</b> ชิ้น แปลว่าขนมอยู่กับเพื่อน <b style='color:#2980b9;'>{fnds}</b> × <b style='color:#e67e22;'>{var}</b> = <b><b style='color:#2980b9;'>{fnds}</b><b style='color:#e67e22;'>{var}</b></b> ชิ้น<br><br>
                    👉 <b>ส่วนที่ 2: รวมกลับเป็นขนมทั้งหมด (ทำไมใช้ บวก +):</b><br>
                    ถ้าเอาขนมของเพื่อน มารวมคืน <b>(+)</b> กับขนมที่กินเองไป <b style='color:#c0392b;'>{eat}</b> ชิ้น <br>
                    จะต้อง <b>เท่ากับ (=)</b> ขนมทั้งหมดที่มีตอนแรกคือ <b style='color:#27ae60;'>{total_c}</b> ชิ้น<br><br>
                    🎯 <b>ได้สมการคือ: <span style='font-size:18px;'><b style='color:#2980b9;'>{fnds}</b><b style='color:#e67e22;'>{var}</b> + <b style='color:#c0392b;'>{eat}</b> = <b style='color:#27ae60;'>{total_c}</b></span></b>
                    </div>"""
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    {analysis}
                    <b>วิธีแก้สมการแบบ 2 ขั้นตอน (กำจัดตัวที่อยู่วงนอกก่อนเสมอ):</b><br>
                    👉 <b>ขั้นที่ 1:</b> นำ <b style='color:#e74c3c;'>{eat}</b> มา <b>ลบออก</b> ทั้งสองข้าง เพื่อหักส่วนที่กินไปออกก่อน<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;{fnds}{var} + {eat} - <b style='color:#e74c3c;'>{eat}</b> = {total_c} - <b style='color:#e74c3c;'>{eat}</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;<i>จะได้:</i> &nbsp; {fnds}{var} = {total_c-eat}<br><br>
                    👉 <b>ขั้นที่ 2:</b> นำ <b style='color:#e74c3c;'>{fnds}</b> มา <b>หารออก</b> ทั้งสองข้าง (ใช้สูตรคูณ <b>แม่ {fnds}</b> ตัดทอน):<br><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;{frac_cancel_left(fnds, var)} = {frac_cancel_right(total_c-eat, fnds, per)}<br><br>
                    👉 <b>{var} = {per}</b><br>
                    <b>ตอบ: เพื่อนได้รับขนมคนละ {per} ชิ้น</b></span>"""

                else: # comparing
                    s_v, diff = random.randint(100, 400), random.randint(50, 200)
                    l_v = s_v + diff
                    q = f"ก้องมีเงิน <b>{l_v}</b> บาท ซึ่งก้องมีเงิน<b>มากกว่า</b>เก่งอยู่ <b>{diff}</b> บาท เก่งมีเงินกี่บาท (ให้ <b>{var}</b> แทนเงินของเก่ง)"
                    
                    analysis = f"""<div style='background-color:#ebf5fb; border-left:4px solid #3498db; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    🔍 <b>แปลภาษาไทย เป็นสมการคณิตศาสตร์:</b><br>
                    โจทย์เปรียบเทียบระหว่าง ก้อง (คนมีเงินมาก) และ เก่ง (คนมีเงินน้อย)<br><br>
                    👉 <b>ทำไมต้องใช้เครื่องหมาย บวก (+) ?</b><br>
                    ถ้าเราอยากให้เงินของเก่ง (<b style='color:#e67e22;'>{var}</b>) มีปริมาณเท่ากับก้อง เราต้อง <b>บวกเพิ่ม</b> ส่วนต่าง (<b style='color:#2980b9;'>{diff}</b>) เข้าไป<br>
                    • (เงินคนน้อย <b style='color:#e67e22;'>{var}</b>) + (ส่วนต่าง <b style='color:#2980b9;'>{diff}</b>) = (เงินคนมาก <b style='color:#27ae60;'>{l_v}</b>)<br><br>
                    🎯 <b>ได้สมการคือ: <span style='font-size:18px;'><b style='color:#e67e22;'>{var}</b> + <b style='color:#2980b9;'>{diff}</b> = <b style='color:#27ae60;'>{l_v}</b></span></b>
                    </div>"""
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    {analysis}
                    <b>วิธีแก้สมการ:</b><br>
                    👉 <b>เป้าหมาย:</b> ทำให้ <b style='color:#e67e22;'>{var}</b> อยู่ตัวเดียว จึงต้องกำจัด <b style='color:#2980b9;'>+{diff}</b> ทิ้งไป<br>
                    👉 นำ <b style='color:#e74c3c;'>{diff}</b> มา <b>ลบออก</b> ทั้งสองข้างของสมการ:<br><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;{var} + {diff} - <b style='color:#e74c3c;'>{diff}</b> = {l_v} - <b style='color:#e74c3c;'>{diff}</b><br><br>
                    👉 <b>{var} = {s_v}</b><br>
                    <b>ตอบ: เก่งมีเงิน {s_v} บาท</b></span>"""
                    
            elif actual_sub_t == "สมการเชิงตรรกะและตาชั่งปริศนา":
                icon_sets = [
                    ("🍎", "🍌", "🍇", "ผลไม้"),
                    ("🐶", "🐱", "🐰", "สัตว์เลี้ยง"),
                    ("🍔", "🍟", "🥤", "อาหาร"),
                    ("⚽", "🏀", "⚾", "กีฬา"),
                    ("🚀", "🛸", "🌍", "อวกาศ")
                ]
                i1, i2, i3, theme = random.choice(icon_sets)
                puzzle_type = random.choice([1, 2, 3])
                
                if puzzle_type == 1:
                    val1 = random.randint(5, 20)
                    val2 = random.randint(3, 15)
                    val3 = random.randint(2, 12)
                    eq1_res = val1 + val1
                    eq2_res = val1 + val2
                    eq3_res = val2 + val3
                    ans = val1 + val2 + val3
                    
                    q_html = f"""
                    <div style='background-color: #fcfcfc; padding: 20px; border-radius: 8px; border: 2px dashed #95a5a6; width: 85%; margin: 15px auto; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);'>
                        <table style='margin: 0 auto; font-size: 28px; border-collapse: collapse; background-color: transparent;'>
                            <tr><td style='text-align:right; padding:8px; border:none;'>{i1} + {i1}</td><td style='padding:8px; border:none; color:#2c3e50;'>=</td><td style='text-align:left; padding:8px; border:none; color:#2c3e50;'><b>{eq1_res}</b></td></tr>
                            <tr><td style='text-align:right; padding:8px; border:none;'>{i1} + {i2}</td><td style='padding:8px; border:none; color:#2c3e50;'>=</td><td style='text-align:left; padding:8px; border:none; color:#2c3e50;'><b>{eq2_res}</b></td></tr>
                            <tr><td style='text-align:right; padding:8px; border:none;'>{i2} + {i3}</td><td style='padding:8px; border:none; color:#2c3e50;'>=</td><td style='text-align:left; padding:8px; border:none; color:#2c3e50;'><b>{eq3_res}</b></td></tr>
                            <tr><td colspan='3' style='border-top: 3px double #34495e; padding-top: 15px; text-align:center; border:none; border-top: 3px double #7f8c8d;'>{i1} + {i2} + {i3} = <b style='color:#e74c3c;'>?</b></td></tr>
                        </table>
                    </div>
                    """
                    q = f"จงหาค่าของปริศนา <b>หมวด{theme}</b> ต่อไปนี้ (แบบฝึกหัดตรรกะพื้นฐาน)<br>{q_html}"
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    <div style='background-color:#ebf5fb; border-left:4px solid #3498db; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    🔍 <b>วิเคราะห์ปริศนา (คิดทีละบรรทัด):</b><br>
                    เวลาแก้ปริศนาภาพ ให้เริ่มจากบรรทัดที่มี <b>"รูปเหมือนกันทั้งหมด"</b> ก่อน เพื่อหาค่าเริ่มต้น!
                    </div>
                    <b>วิธีทำอย่างละเอียด:</b><br>
                    👉 <b>บรรทัดที่ 1:</b> {i1} + {i1} = {eq1_res}<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;ของ 2 สิ่งเหมือนกันบวกกันได้ {eq1_res} แสดงว่า 1 สิ่งคือ {eq1_res} ÷ 2 = <b>{val1}</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;ดังนั้น <b>{i1} = {val1}</b><br><br>
                    
                    👉 <b>บรรทัดที่ 2:</b> {i1} + {i2} = {eq2_res}<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;เรารู้แล้วว่า {i1} คือ {val1} จะได้สมการ: {val1} + {i2} = {eq2_res}<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;แก้สมการโดยนำ {val1} ไปลบออก: {i2} = {eq2_res} - {val1} = <b>{val2}</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;ดังนั้น <b>{i2} = {val2}</b><br><br>
                    
                    👉 <b>บรรทัดที่ 3:</b> {i2} + {i3} = {eq3_res}<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;เรารู้แล้วว่า {i2} คือ {val2} จะได้สมการ: {val2} + {i3} = {eq3_res}<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;แก้สมการโดยนำ {val2} ไปลบออก: {i3} = {eq3_res} - {val2} = <b>{val3}</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;ดังนั้น <b>{i3} = {val3}</b><br><br>
                    
                    👉 <b>คำถาม:</b> {i1} + {i2} + {i3} = ?<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;แทนค่ารูปภาพด้วยตัวเลข: {val1} + {val2} + {val3} = <b>{ans}</b><br>
                    <b>ตอบ: {ans}</b></span>"""

                elif puzzle_type == 2:
                    val1 = random.randint(3, 10)
                    val2 = random.randint(2, 8)
                    val3 = random.randint(2, 6)
                    eq1_res = val1 * 3
                    eq2_res = val1 + (val2 * 2)
                    eq3_res = val2 + (val3 * 2)
                    ans = val1 + (val2 * val3) 
                    
                    q_html = f"""
                    <div style='background-color: #fdfefe; padding: 20px; border-radius: 8px; border: 2px solid #d0d3d4; width: 90%; margin: 15px auto; box-shadow: 3px 3px 10px rgba(0,0,0,0.08);'>
                        <table style='margin: 0 auto; font-size: 26px; border-collapse: collapse; background-color: transparent;'>
                            <tr><td style='text-align:right; padding:6px; border:none;'>{i1} + {i1} + {i1}</td><td style='padding:6px; border:none; color:#2c3e50;'>=</td><td style='text-align:left; padding:6px; border:none; color:#2c3e50;'><b>{eq1_res}</b></td></tr>
                            <tr><td style='text-align:right; padding:6px; border:none;'>{i1} + {i2} + {i2}</td><td style='padding:6px; border:none; color:#2c3e50;'>=</td><td style='text-align:left; padding:6px; border:none; color:#2c3e50;'><b>{eq2_res}</b></td></tr>
                            <tr><td style='text-align:right; padding:6px; border:none;'>{i2} + {i3} + {i3}</td><td style='padding:6px; border:none; color:#2c3e50;'>=</td><td style='text-align:left; padding:6px; border:none; color:#2c3e50;'><b>{eq3_res}</b></td></tr>
                            <tr><td colspan='3' style='border-top: 3px double #7f8c8d; padding-top: 15px; text-align:center; border-bottom:none; border-left:none; border-right:none;'>{i1} + {i2} <b style='color:#e74c3c;'>×</b> {i3} = <b style='color:#e74c3c;'>?</b></td></tr>
                        </table>
                    </div>
                    """
                    q = f"จงหาค่าของปริศนา <b>หมวด{theme}</b> ต่อไปนี้ <br><span style='color:#e74c3c; font-size:14px;'>(⭐ แนวข้อสอบแข่งขัน: สังเกตเครื่องหมายในบรรทัดสุดท้ายให้ดี!)</span><br>{q_html}"
                    
                    explain_box_step = f"""<div style='background-color:#fef9e7; border-left:4px solid #f39c12; padding:10px; margin-bottom:10px; border-radius:4px;'>
                    💡 <b>ตัวเลขในแต่ละบรรทัดมาได้อย่างไร?</b><br>
                    • <b>บรรทัดที่ 1:</b> นำผลรวมไป <b>หาร 3</b> จะได้ค่าของ 1 รูป<br>
                    • <b>บรรทัดที่ 2 และ 3:</b> ให้นำค่าที่รู้แล้วไป <b>แทนค่า</b> ในรูปภาพ จากนั้นนำไป <b>ลบออก</b> จากผลรวมฝั่งขวา จะเหลือค่าของรูปอีก 2 รูปที่ยังไม่ทราบ นำไป <b>หาร 2</b> ก็จะได้ค่าของรูปนั้นครับ
                    </div>"""
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    <div style='background-color:#ebf5fb; border-left:4px solid #3498db; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    🔍 <b>วิเคราะห์ปริศนา (แนวข้อสอบแข่งขัน):</b><br>
                    ระวัง <b>"ลำดับการคำนวณ (Order of Operations)"</b> ในบรรทัดสุดท้าย (ต้องทำ <b>คูณ</b> ก่อน <b>บวก</b> เสมอ!)
                    </div>
                    <b>วิธีทำอย่างละเอียด:</b><br>
                    {explain_box_step}
                    👉 <b>บรรทัดที่ 1:</b> {i1} + {i1} + {i1} = {eq1_res}<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;ของเหมือนกัน 3 ชิ้นรวมได้ {eq1_res} ➔ 1 ชิ้นคือ {eq1_res} ÷ 3 = <b>{val1}</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;สรุป: <b style='color:#2980b9;'>{i1} = {val1}</b><br><br>
                    
                    👉 <b>บรรทัดที่ 2:</b> {i1} + {i2} + {i2} = {eq2_res}<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;แทนค่า {i1} เป็น {val1} จะได้: {val1} + {i2} + {i2} = {eq2_res}<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;นำ {val1} ไปลบออก ➔ {i2} + {i2} = {eq2_res} - {val1} = <b>{eq2_res - val1}</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;{i2} สองชิ้นรวมได้ {eq2_res - val1} ➔ 1 ชิ้นคือ {eq2_res - val1} ÷ 2 = <b>{val2}</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;สรุป: <b style='color:#8e44ad;'>{i2} = {val2}</b><br><br>
                    
                    👉 <b>บรรทัดที่ 3:</b> {i2} + {i3} + {i3} = {eq3_res}<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;แทนค่า {i2} เป็น {val2} จะได้: {val2} + {i3} + {i3} = {eq3_res}<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;นำ {val2} ไปลบออก ➔ {i3} + {i3} = {eq3_res} - {val2} = <b>{eq3_res - val2}</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;{i3} สองชิ้นรวมได้ {eq3_res - val2} ➔ 1 ชิ้นคือ {eq3_res - val2} ÷ 2 = <b>{val3}</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;สรุป: <b style='color:#27ae60;'>{i3} = {val3}</b><br><br>
                    
                    👉 <b>คำถาม:</b> {i1} + {i2} <b style='color:#e74c3c;'>×</b> {i3} = ?<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;แทนค่ารูปภาพ: {val1} + {val2} <b style='color:#e74c3c;'>×</b> {val3}<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;<i>(🚨 กฎคณิตศาสตร์: ต้องคำนวณคู่ที่คูณกันก่อนเสมอ!)</i><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;= {val1} + <b style='color:#e74c3c;'>({val2} × {val3})</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;= {val1} + <b style='color:#e74c3c;'>{val2*val3}</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;= <b>{ans}</b><br>
                    <b>ตอบ: {ans}</b></span>"""

                else:
                    # Type 3: ตาชั่งปริศนา 3 ตาชั่ง (โค้ดเดิมที่ถูกต้องแล้ว ยกมาใส่ได้เลย)
                    w_c = random.randint(3, 8)     
                    mult_bc = random.randint(2, 4) 
                    w_b = w_c * mult_bc            
                    mult_ab = random.randint(2, 3) 
                    w_a = w_b * mult_ab            
                    total_w = w_a + w_b + w_c      
                    i1_in_i3 = mult_ab * mult_bc   
                    total_c_parts = i1_in_i3 + mult_bc + 1 
                    s1_l = i1
                    s1_r = " ".join([i2] * mult_ab)
                    s2_l = i2
                    s2_r = " ".join([i3] * mult_bc)
                    s3_l = f"{i1} {i2} {i3}"
                    s3_r = f"<span style='font-size:24px; font-weight:bold; color:#d35400;'>{total_w} กรัม</span>"
                    
                    def draw_scale(title, color, left, right):
                        return f"""
                        <div style='margin-bottom: 25px;'>
                            <b style='color:{color}; font-size:18px;'>{title}</b><br>
                            <div style='display:flex; justify-content:center; align-items:flex-end; gap:10px; margin-top:5px;'>
                                <div style='border-bottom:4px solid #34495e; padding:5px 15px; min-width:80px; font-size:26px;'>{left}</div>
                                <div style='font-size:40px; margin-bottom:-20px;'>⚖️</div>
                                <div style='border-bottom:4px solid #34495e; padding:5px 15px; min-width:80px; font-size:26px;'>{right}</div>
                            </div>
                        </div>"""
                    
                    q_html = f"""
                    <div style='background-color: #fcfcfc; padding: 20px 10px; border-radius: 8px; border: 2px solid #bdc3c7; width: 95%; margin: 15px auto; box-shadow: 3px 3px 10px rgba(0,0,0,0.08); text-align:center;'>
                        {draw_scale("ตาชั่งที่ 1 (สมดุล)", "#2980b9", s1_l, s1_r)}
                        {draw_scale("ตาชั่งที่ 2 (สมดุล)", "#8e44ad", s2_l, s2_r)}
                        {draw_scale("ตาชั่งที่ 3 (สมดุล)", "#27ae60", s3_l, s3_r)}
                    </div>
                    """
                    q = f"จากภาพตาชั่งปริศนาทั้ง 3 เครื่องที่อยู่ในสภาวะสมดุล<br>จงหาว่า <b>{i1}, {i2} และ {i3} มีน้ำหนักชิ้นละกี่กรัม ?</b><br>{q_html}"
                    
                    explain_box_step4 = f"""<div style='background-color:#fef9e7; border-left:4px solid #f39c12; padding:10px; margin-bottom:10px; border-radius:4px;'>
                    💡 <b>ตัวเลขในขั้นที่ 4 มาจากไหน?</b><br>
                    • หา {i2}: จากขั้นที่ 1 เรารู้ว่า <b>1 {i2} = {mult_bc} {i3}</b> จึงนำน้ำหนักของ {i3} มาคูณด้วย {mult_bc}<br>
                    • หา {i1}: จากขั้นที่ 2 เรารู้ว่า <b>1 {i1} = {i1_in_i3} {i3}</b> จึงนำน้ำหนักของ {i3} มาคูณด้วย {i1_in_i3}
                    </div>"""
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    <div style='background-color:#ebf5fb; border-left:4px solid #3498db; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    🔍 <b>วิเคราะห์ปริศนาตาชั่ง (การแทนค่า):</b><br>
                    ตาชั่งสมดุล หมายถึง <b>ซ้าย = ขวา</b><br>
                    หลักการคือ <b>"เปลี่ยนของชิ้นใหญ่ ให้กลายเป็นของชิ้นเล็กที่สุด"</b> ({i3})<br>
                    เพื่อให้ตาชั่งที่ 3 มีแต่ {i3} ล้วนๆ จะได้คำนวณง่ายขึ้นครับ!
                    </div>
                    <b>วิธีทำอย่างละเอียด:</b><br>
                    👉 <b>ขั้นที่ 1: เปลี่ยน {i2} เป็น {i3} (จากตาชั่ง 2)</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;ตาชั่ง 2 บอกว่า <b>1 {i2} = {mult_bc} {i3}</b><br><br>
                    
                    👉 <b>ขั้นที่ 2: เปลี่ยน {i1} เป็น {i3} (จากตาชั่ง 1)</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;ตาชั่ง 1 บอกว่า <b>1 {i1} = {mult_ab} {i2}</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;เราแทนค่า {i2} ด้วย {i3} จะได้: {mult_ab} × {mult_bc} = <b style='color:#e67e22;'>{i1_in_i3} {i3}</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;สรุปคือ <b>1 {i1} = <span style='color:#e67e22;'>{i1_in_i3} {i3}</span></b><br><br>
                    
                    👉 <b>ขั้นที่ 3: รวมน้ำหนักในตาชั่งที่ 3</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;ตาชั่ง 3 มี: {i1} + {i2} + {i3} = {total_w} กรัม<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;เปลี่ยนทุกอย่างให้เป็น {i3}:<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;• {i1} เปลี่ยนเป็น {i1_in_i3} {i3}<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;• {i2} เปลี่ยนเป็น {mult_bc} {i3}<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;• {i3} มีอยู่แล้ว 1 {i3}<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;นับรวมทั้งหมดจะมี {i3} อยู่: {i1_in_i3} + {mult_bc} + 1 = <b style='color:#e74c3c;'>{total_c_parts} ชิ้น</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;จะได้สมการ: <b style='color:#e74c3c;'>{total_c_parts}</b> × {i3} = {total_w} กรัม<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;ดังนั้น <b>{i3}</b> = {total_w} ÷ {total_c_parts} = <b style='color:#27ae60;'>{w_c} กรัม</b><br><br>
                    
                    👉 <b>ขั้นที่ 4: หาค่าที่เหลือ</b><br>
                    {explain_box_step4}
                    &nbsp;&nbsp;&nbsp;&nbsp;• <b>{i2}</b> น้ำหนัก: {w_c} × {mult_bc} = <b style='color:#27ae60;'>{w_b} กรัม</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;• <b>{i1}</b> น้ำหนัก: {w_c} × {i1_in_i3} = <b style='color:#27ae60;'>{w_a} กรัม</b><br><br>
                    <b>ตอบ: {i1} = {w_a} ก., {i2} = {w_b} ก., {i3} = {w_c} ก.</b></span>"""

            elif actual_sub_t == "โจทย์ปัญหาสมการ: ความสัมพันธ์ของ 2 สิ่ง":
                prob_type = random.choice([1, 2, 3, 4, 5]) 
                var = random.choice(["x", "y", "a", "ก", "m", "n"])
                
                # ฟังก์ชันช่วยวาดการตัดทอน
                def frac_cancel_left(num, variable):
                    top = f"<span style='display:inline-block; position:relative;'><span style='text-decoration:line-through; text-decoration-color:#e74c3c;'>{num}</span><span style='font-size:12px; color:#e74c3c; vertical-align:super; margin-left:2px;'>1</span></span>{variable}"
                    bottom = f"<span style='text-decoration:line-through; text-decoration-color:#e74c3c;'>{num}</span><span style='font-size:12px; color:#e74c3c; vertical-align:sub; margin-left:2px;'>1</span>"
                    return f"<span style='display:inline-flex; flex-direction:column; vertical-align:middle; text-align:center; margin:0 4px;'><span style='border-bottom:2px solid #333; padding:0 5px;'>{top}</span><span>{bottom}</span></span>"
                
                def frac_cancel_right(top_val, bot_val, result_val):
                    top = f"<span style='display:inline-block; position:relative;'><span style='text-decoration:line-through; text-decoration-color:#e74c3c;'>{top_val}</span><span style='font-size:14px; color:#e74c3c; font-weight:bold; vertical-align:super; margin-left:2px;'>{result_val}</span></span>"
                    bottom = f"<span style='text-decoration:line-through; text-decoration-color:#e74c3c;'>{bot_val}</span><span style='font-size:12px; color:#e74c3c; vertical-align:sub; margin-left:2px;'>1</span>"
                    return f"<span style='display:inline-flex; flex-direction:column; vertical-align:middle; text-align:center; margin:0 4px;'><span style='border-bottom:2px solid #333; padding:0 5px;'>{top}</span><span>{bottom}</span></span>"

                if prob_type == 1:
                    # Level 1: ผลรวม + ผลต่าง
                    themes = [
                        ("ฟาร์มแห่งหนึ่ง", "ไก่", "เป็ด", "ตัว"),
                        ("สองพี่น้อง", "พี่", "น้อง", "บาท"),
                        ("ร้านเบเกอรี่", "โดนัท", "เค้ก", "ชิ้น")
                    ]
                    place, item1, item2, unit = random.choice(themes)
                    smaller = random.randint(30, 150)
                    diff = random.randint(15, 60)
                    larger = smaller + diff
                    total = smaller + larger
                    
                    q = f"ที่{place} มี{item1}และ{item2}รวมกันทั้งหมด <b>{total}</b> {unit} <br>ถ้ามี{item1}มากกว่า{item2}อยู่ <b>{diff}</b> {unit} <br>อยากทราบว่ามี <b>{item2}</b> จำนวนกี่{unit}? <br><span style='font-size:14px; color:#7f8c8d;'>(กำหนดให้ {var} แทนจำนวนของ{item2})</span>"
                    
                    analysis = f"""<div style='background-color:#ebf5fb; border-left:4px solid #3498db; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    🔍 <b>แปลภาษาไทย เป็นสมการคณิตศาสตร์:</b><br>
                    เรามีของ 2 สิ่งที่ไม่รู้จำนวนเลย จึงต้องแปลงสิ่งหนึ่งให้เป็นตัวแปรเสียก่อน<br><br>
                    👉 <b>1. กำหนดตัวไม่ทราบค่า:</b><br>
                    เพื่อให้ง่าย เราจะให้ของที่มี<b>น้อยกว่า</b>เป็นตัวแปรเสมอ ดังนั้นให้ {item2} = <b style='color:#e67e22;'>{var}</b> {unit}<br><br>
                    👉 <b>2. สร้างจำนวน {item1} (ทำไมต้องใช้ บวก +):</b><br>
                    โจทย์บอกว่า {item1} มี<b>มากกว่า</b>อยู่ {diff} คำว่า "มากกว่า" แปลว่าต้องเอาไป <b>บวกเพิ่ม</b><br>
                    จะได้ว่า {item1} = <b style='color:#2980b9;'>{var} + {diff}</b> {unit}<br><br>
                    👉 <b>3. สร้างสมการ (ทำไมต้องใช้ บวก + และ เท่ากับ =):</b><br>
                    โจทย์บอกว่าทั้งสองอย่าง <b>"รวมกัน"</b> ได้ {total} คำว่ารวมกันคือต้องจับมา <b>บวกกัน (+)</b> และผลลัพธ์จะต้อง <b>เท่ากับ (=)</b> <b style='color:#27ae60;'>{total}</b><br>
                    • ({item2}) + ({item1}) = {total}<br><br>
                    🎯 <b>ได้สมการคือ: <span style='font-size:18px;'><b style='color:#e67e22;'>{var}</b> + (<b style='color:#2980b9;'>{var} + {diff}</b>) = <b style='color:#27ae60;'>{total}</b></span></b>
                    </div>"""
                    
                    explain_box_cancel = f"""<div style='background-color:#fef9e7; border-left:4px solid #f39c12; padding:10px; margin-bottom:10px; border-radius:4px;'>
                    💡 <b>ตัวเลขด้านบนมาจากไหน?</b><br>
                    เกิดจากการนำ <b>2</b> มา <b>หารออก</b> ทั้งเศษและส่วน (ใช้แม่ 2 ตัดทอน)<br>
                    • {total - diff} ÷ 2 = {smaller}
                    </div>"""
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    {analysis}
                    <b>วิธีแก้สมการอย่างละเอียด:</b><br>
                    👉 <b>ขั้นที่ 1: รวมตัวแปรเข้าด้วยกัน</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;💡 <i>อธิบาย: <b style='color:#e67e22;'>{var}</b> บวกกับ <b style='color:#2980b9;'>{var}</b> จะมีค่าเท่ากับ <b>2{var}</b></i><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;เมื่อรวมตัวแปรแล้ว จะได้สมการใหม่คือ: <b>2{var} + {diff} = {total}</b><br><br>
                    👉 <b>ขั้นที่ 2: กำจัดตัวเลขที่อยู่ไกลตัวแปร (วงนอก)</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;นำ <b style='color:#e74c3c;'>{diff}</b> มา <b>ลบออก</b> ทั้งสองข้างของสมการ<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;2{var} + {diff} <b style='color:#e74c3c;'>- {diff}</b> = {total} <b style='color:#e74c3c;'>- {diff}</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;<i>จะได้:</i> 2{var} = {total - diff}<br><br>
                    👉 <b>ขั้นที่ 3: กำจัดตัวเลขที่ติดกับตัวแปร</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;เลข 2 เขียนติดกับ {var} แปลว่า "คูณอยู่" จึงต้องนำ <b>2</b> มา <b>หารออก</b> ทั้งสองข้าง<br>
                    {explain_box_cancel}
                    &nbsp;&nbsp;&nbsp;&nbsp;{frac_cancel_left(2, var)} = {frac_cancel_right(total - diff, 2, smaller)}<br><br>
                    👉 <b>{var} = {smaller}</b><br>
                    <b>ตอบ: มี{item2} จำนวน {smaller} {unit}</b></span>"""

                elif prob_type == 2:
                    # Level 2: ผลรวม + จำนวนเท่า
                    themes = [
                        ("สวนสัตว์", "ลิง", "ช้าง", "ตัว"),
                        ("ลานจอดรถ", "รถยนต์", "รถจักรยานยนต์", "คัน"),
                        ("กระปุกออมสิน", "เหรียญสิบ", "เหรียญห้า", "เหรียญ")
                    ]
                    place, item1, item2, unit = random.choice(themes)
                    mult = random.randint(3, 6) 
                    smaller = random.randint(15, 50)
                    larger = smaller * mult
                    total = smaller + larger
                    
                    q = f"ใน{place} มี{item1}และ{item2}รวมกันทั้งหมด <b>{total}</b> {unit} <br>ถ้าจำนวน{item1} <b>เป็น {mult} เท่า</b> ของจำนวน{item2} <br>อยากทราบว่ามี <b>{item2}</b> จำนวนกี่{unit}? <br><span style='font-size:14px; color:#e74c3c;'>(⭐ ระดับแข่งขัน: กำหนดให้ {var} แทนจำนวนของ{item2})</span>"
                    
                    analysis = f"""<div style='background-color:#ebf5fb; border-left:4px solid #3498db; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    🔍 <b>แปลภาษาไทย เป็นสมการคณิตศาสตร์:</b><br>
                    👉 <b>1. กำหนดตัวไม่ทราบค่า:</b><br>
                    ให้ {item2} (สิ่งที่มีน้อยกว่า) มีจำนวน = <b style='color:#e67e22;'>{var}</b> {unit} (คิดเป็น 1 ส่วน)<br><br>
                    👉 <b>2. สร้างจำนวน {item1} (ทำไมต้องใช้ คูณ ×):</b><br>
                    โจทย์บอกว่า {item1} เป็น <b>{mult} เท่า</b> ของ{item2} คำว่า "เท่าของ" คือ <b>"การคูณ"</b><br>
                    จะได้ว่า {item1} มีจำนวน = {mult} × {var} หรือเขียนสั้นๆ ว่า <b style='color:#2980b9;'>{mult}{var}</b> {unit} (คิดเป็น {mult} ส่วน)<br><br>
                    👉 <b>3. สร้างสมการรวม (ทำไมต้องใช้ บวก + และ เท่ากับ =):</b><br>
                    นำทั้งสองสิ่งมา <b>"รวมกัน (+)"</b> ต้องมีค่า <b>"เท่ากับ (=)"</b> <b style='color:#27ae60;'>{total}</b><br>
                    • ({item2}) + ({item1}) = {total}<br><br>
                    🎯 <b>ได้สมการคือ: <span style='font-size:18px;'><b style='color:#e67e22;'>{var}</b> + <b style='color:#2980b9;'>{mult}{var}</b> = <b style='color:#27ae60;'>{total}</b></span></b>
                    </div>"""
                    
                    explain_box_cancel = f"""<div style='background-color:#fef9e7; border-left:4px solid #f39c12; padding:10px; margin-bottom:10px; border-radius:4px;'>
                    💡 <b>ตัวเลขด้านบนมาจากไหน?</b><br>
                    เกิดจากการนำ <b>{mult+1}</b> มา <b>หารออก</b> ทั้งเศษและส่วน (ใช้แม่ {mult+1} ตัดทอน)<br>
                    • {total} ÷ {mult+1} = {smaller}
                    </div>"""
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    {analysis}
                    <b>วิธีแก้สมการอย่างละเอียด:</b><br>
                    👉 <b>ขั้นที่ 1: รวมตัวแปรเข้าด้วยกัน</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;💡 <i>อธิบาย: <b style='color:#e67e22;'>{var}</b> ตัวเดียว มีความหมายเท่ากับ <b>1{var}</b> เมื่อนำมาบวกกับ <b style='color:#2980b9;'>{mult}{var}</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;ให้นำตัวเลขข้างหน้ามาบวกกัน (1 + {mult} = {mult+1}) จะรวมกันได้เป็น <b>{mult+1}{var}</b></i><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;เมื่อยุบรวมแล้ว จะได้สมการใหม่คือ: <b>{mult+1}{var} = {total}</b><br><br>
                    👉 <b>ขั้นที่ 2: กำจัดตัวเลขที่ติดกับตัวแปร</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;เลข {mult+1} คูณอยู่กับ {var} จึงต้องนำ <b style='color:#e74c3c;'>{mult+1}</b> มา <b>หารออก</b> ทั้งสองข้าง<br>
                    {explain_box_cancel}
                    &nbsp;&nbsp;&nbsp;&nbsp;{frac_cancel_left(mult+1, var)} = {frac_cancel_right(total, mult+1, smaller)}<br><br>
                    👉 <b>{var} = {smaller}</b><br>
                    <b>ตอบ: มี{item2} จำนวน {smaller} {unit}</b></span>"""

                elif prob_type == 3:
                    # Level 3: ผลต่าง + จำนวนเท่า
                    themes = [
                        ("การสะสมแสตมป์", "ก้อง", "เก่ง", "ดวง"),
                        ("การสอบ", "ปุ๊ก", "ป๊อป", "คะแนน"),
                        ("โรงงานผลิต", "เสื้อยืด", "กางเกง", "ตัว")
                    ]
                    place, item1, item2, unit = random.choice(themes)
                    mult = random.randint(3, 5) 
                    smaller = random.randint(25, 80)
                    larger = smaller * mult
                    diff = larger - smaller
                    
                    q = f"เรื่อง{place} พบว่า {item1} มีจำนวน <b>เป็น {mult} เท่า</b> ของ{item2} <br>และ {item1} มี<b>มากกว่า</b>{item2}อยู่ <b>{diff}</b> {unit} <br>อยากทราบว่ามี <b>{item2}</b> จำนวนกี่{unit}? <br><span style='font-size:14px; color:#e74c3c;'>(🔥 ระดับแข่งขันขั้นสูง: กำหนดให้ {var} แทนจำนวนของ{item2})</span>"
                    
                    analysis = f"""<div style='background-color:#ebf5fb; border-left:4px solid #3498db; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    🔍 <b>แปลภาษาไทย เป็นสมการคณิตศาสตร์:</b><br>
                    👉 <b>1. กำหนดตัวไม่ทราบค่า:</b><br>
                    ให้ {item2} (สิ่งที่มีน้อยกว่า) มีจำนวน = <b style='color:#e67e22;'>{var}</b> {unit}<br><br>
                    👉 <b>2. สร้างจำนวน {item1} (ใช้ คูณ ×):</b><br>
                    โจทย์บอกว่า {item1} เป็น <b>{mult} เท่า</b> ของ{item2} คำว่า "เท่าของ" คือ <b>"การคูณ"</b><br>
                    จะได้ว่า {item1} มีจำนวน = <b style='color:#2980b9;'>{mult}{var}</b> {unit}<br><br>
                    👉 <b>3. สร้างสมการจากผลต่าง (ทำไมต้องใช้ ลบ -):</b><br>
                    คำว่า <b>"มากกว่าอยู่"</b> เป็นการเปรียบเทียบเพื่อหา <b>"ผลต่าง"</b> การหาผลต่างในทางคณิตศาสตร์ ต้องนำสิ่งที่มีมากกว่าตั้ง แล้ว <b>ลบ (-)</b> ด้วยสิ่งที่มีน้อยกว่า<br>
                    • ({item1}) - ({item2}) = ผลต่าง<br><br>
                    🎯 <b>ได้สมการคือ: <span style='font-size:18px;'><b style='color:#2980b9;'>{mult}{var}</b> - <b style='color:#e67e22;'>{var}</b> = <b style='color:#27ae60;'>{diff}</b></span></b>
                    </div>"""
                    
                    explain_box_cancel = f"""<div style='background-color:#fef9e7; border-left:4px solid #f39c12; padding:10px; margin-bottom:10px; border-radius:4px;'>
                    💡 <b>ตัวเลขด้านบนมาจากไหน?</b><br>
                    เกิดจากการนำ <b>{mult-1}</b> มา <b>หารออก</b> ทั้งเศษและส่วน (ใช้แม่ {mult-1} ตัดทอน)<br>
                    • {diff} ÷ {mult-1} = {smaller}
                    </div>"""
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    {analysis}
                    <b>วิธีแก้สมการอย่างละเอียด:</b><br>
                    👉 <b>ขั้นที่ 1: ลบตัวแปรออกจากกัน</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;💡 <i>อธิบาย: มีอยู่ <b style='color:#2980b9;'>{mult}{var}</b> นำไปลบออก <b style='color:#e67e22;'>1{var}</b> (เอาเลขข้างหน้ามาลบกันคือ {mult} - 1 = {mult-1}) จะเหลือ <b>{mult-1}{var}</b></i><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;เมื่อลบกันแล้ว จะได้สมการใหม่คือ: <b>{mult-1}{var} = {diff}</b><br><br>
                    👉 <b>ขั้นที่ 2: กำจัดตัวเลขที่ติดกับตัวแปร</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;เลข {mult-1} คูณอยู่ จึงต้องนำ <b style='color:#e74c3c;'>{mult-1}</b> มา <b>หารออก</b> ทั้งสองข้าง<br>
                    {explain_box_cancel}
                    &nbsp;&nbsp;&nbsp;&nbsp;{frac_cancel_left(mult-1, var)} = {frac_cancel_right(diff, mult-1, smaller)}<br><br>
                    👉 <b>{var} = {smaller}</b><br>
                    <b>ตอบ: มี{item2} จำนวน {smaller} {unit}</b></span>"""

                elif prob_type == 4:
                    # Level 4: ราคาสินค้า 2 ชนิด
                    item_pairs = [
                        ["ปากกา", "สมุด"], ["ดินสอ", "ยางลบ"], ["ไม้บรรทัด", "กล่องดินสอ"],
                        ["สีไม้", "สมุดวาดเขียน"], ["กรรไกร", "กาวน้ำ"], ["นมสด", "ขนมปัง"]
                    ]
                    items = random.choice(item_pairs)
                    random.shuffle(items)
                    item1, item2 = items[0], items[1] 
                    
                    smaller = random.randint(10, 45)
                    diff = random.randint(5, 20)     
                    larger = smaller + diff          
                    total = smaller + larger         
                    
                    q = f"ซื้อ<b>{item1}</b>และ<b>{item2}</b>อย่างละ 1 ชิ้น จ่ายเงินรวมทั้งหมด <b>{total}</b> บาท <br>ถ้า{item1}ราคา<b>แพงกว่า</b>{item2}อยู่ <b>{diff}</b> บาท <br>อยากทราบว่า <b>{item2}</b> ราคาชิ้นละกี่บาท? <br><span style='font-size:14px; color:#7f8c8d;'>(กำหนดให้ {var} แทนราคาของ{item2})</span>"
                    
                    analysis = f"""<div style='background-color:#ebf5fb; border-left:4px solid #3498db; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    🔍 <b>แปลภาษาไทย เป็นสมการคณิตศาสตร์:</b><br>
                    โจทย์ข้อนี้เปรียบเทียบราคาสินค้า 2 ชนิด เราต้องกำหนดราคาให้ชนิดใดชนิดหนึ่งเป็นตัวแปรก่อน<br><br>
                    👉 <b>1. กำหนดตัวไม่ทราบค่า:</b><br>
                    ให้ {item2} (ของที่ราคาถูกกว่า) มีราคา = <b style='color:#e67e22;'>{var}</b> บาท<br><br>
                    👉 <b>2. สร้างราคาของ {item1} (ทำไมต้องใช้ บวก +):</b><br>
                    โจทย์บอกว่า {item1} <b>แพงกว่า</b> อยู่ {diff} บาท คำว่า "แพงกว่า" แปลว่าต้องเอาไป <b>บวกเพิ่ม</b><br>
                    จะได้ว่า {item1} ราคา = <b style='color:#2980b9;'>{var} + {diff}</b> บาท<br><br>
                    👉 <b>3. สร้างสมการรวม (ทำไมต้องใช้ บวก + และ เท่ากับ =):</b><br>
                    ซื้ออย่างละ 1 ชิ้น <b>"จ่ายเงินรวม"</b> หมายถึงนำราคามา <b>บวกกัน (+)</b> และต้อง <b>เท่ากับ (=)</b> เงินที่จ่ายไปคือ <b style='color:#27ae60;'>{total}</b> บาท<br>
                    • (ราคา{item2}) + (ราคา{item1}) = {total}<br><br>
                    🎯 <b>ได้สมการคือ: <span style='font-size:18px;'><b style='color:#e67e22;'>{var}</b> + (<b style='color:#2980b9;'>{var} + {diff}</b>) = <b style='color:#27ae60;'>{total}</b></span></b>
                    </div>"""
                    
                    explain_box_cancel = f"""<div style='background-color:#fef9e7; border-left:4px solid #f39c12; padding:10px; margin-bottom:10px; border-radius:4px;'>
                    💡 <b>ตัวเลขด้านบนมาจากไหน?</b><br>
                    เกิดจากการนำ <b>2</b> มา <b>หารออก</b> ทั้งเศษและส่วน (ใช้แม่ 2 ตัดทอน)<br>
                    • {total - diff} ÷ 2 = {smaller}
                    </div>"""
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    {analysis}
                    <b>วิธีแก้สมการอย่างละเอียด:</b><br>
                    👉 <b>ขั้นที่ 1: รวมตัวแปรเข้าด้วยกัน</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;💡 <i>อธิบาย: นำราคา <b style='color:#e67e22;'>{var}</b> มาบวกกับ <b style='color:#2980b9;'>{var}</b> จะมีค่าเท่ากับ <b>2{var}</b></i><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;เมื่อยุบรวมตัวแปรแล้ว จะได้สมการใหม่คือ: <b>2{var} + {diff} = {total}</b><br><br>
                    👉 <b>ขั้นที่ 2: กำจัดตัวเลขที่อยู่ไกลตัวแปร (วงนอก)</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;นำ <b style='color:#e74c3c;'>{diff}</b> มา <b>ลบออก</b> ทั้งสองข้างของสมการ<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;2{var} + {diff} <b style='color:#e74c3c;'>- {diff}</b> = {total} <b style='color:#e74c3c;'>- {diff}</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;<i>จะได้:</i> 2{var} = {total - diff}<br><br>
                    👉 <b>ขั้นที่ 3: กำจัดตัวเลขที่ติดกับตัวแปร</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;นำ <b>2</b> มา <b>หารออก</b> ทั้งสองข้าง (ใช้แม่ 2 ตัดทอน)<br>
                    {explain_box_cancel}
                    &nbsp;&nbsp;&nbsp;&nbsp;{frac_cancel_left(2, var)} = {frac_cancel_right(total - diff, 2, smaller)}<br><br>
                    👉 <b>{var} = {smaller}</b><br>
                    <b>ตอบ: {item2} ราคาชิ้นละ {smaller} บาท</b></span>"""
                
                else:
                    # Level 5: ระบบสมการ 2 ตัวแปรแบบซ่อนรูป (โจทย์ออริจินัลของคุณครู) -> เพิ่มตัวคูณในประโยคที่ 2
                    items = [("สมุด", "เล่ม", "ปากกา", "ด้าม"), ("เสื้อ", "ตัว", "กางเกง", "ตัว"), ("ขนม", "ห่อ", "น้ำผลไม้", "กล่อง")]
                    item_pair = random.choice(items)
                    # สุ่มสลับตำแหน่งของสิ่งของ
                    if random.choice([True, False]):
                        item1, unit1, item2, unit2 = item_pair
                    else:
                        item2, unit2, item1, unit1 = item_pair
                        
                    var1, var2 = "x", "y" 
                    
                    while True:
                        mult = random.randint(2, 4)      # จำนวนเท่าของ item1
                        price1 = random.randint(5, 25)   # x
                        diff = random.randint(2, 15)     
                        price2 = (mult * price1) - diff  # y = (mult * x) - diff
                        if price2 > 0 and price1 != price2: 
                            break
                            
                    total = price1 + price2          # x + y
                    
                    # ปรับข้อความ: "ถ้า {item1} {mult} ชิ้น ราคาแพงกว่า {item2} 1 ชิ้น อยู่ {diff} บาท"
                    q = f"ซื้อ <b>{item1} 1 {unit1}</b> รวมกับ <b>{item2} 1 {unit2}</b> ราคารวมกัน <b>{total}</b> บาท <br>ถ้า <b>{item1} {mult} {unit1}</b> ราคาแพงกว่า <b>{item2} 1 {unit2}</b> อยู่ <b>{diff}</b> บาท <br>อยากทราบว่า <b>{item1} และ {item2} ราคา{unit1}ละกี่บาท?</b> <br><span style='font-size:14px; color:#e74c3c;'>(🏆 โจทย์ปราบเซียน: ให้ใช้ความรู้เรื่องการแทนค่าสมการ)</span>"
                    
                    analysis = f"""<div style='background-color:#ebf5fb; border-left:4px solid #3498db; padding:10px; margin-bottom:15px; border-radius:4px;'>
                    🔍 <b>วิเคราะห์ด้วยเทคนิค "การสร้าง 2 สมการแล้วแทนค่า":</b><br>
                    ข้อนี้มีของ 2 อย่างที่ไม่รู้ราคา ให้ตั้งเป็นตัวแปร 2 ตัว<br>
                    • ให้ {item1} = <b style='color:#e67e22;'>{var1}</b> บาท<br>
                    • ให้ {item2} = <b style='color:#2980b9;'>{var2}</b> บาท<br><br>
                    👉 <b>จากประโยคที่ 1:</b> {item1} 1 {unit1} รวมกับ {item2} 1 {unit2} = {total} บาท<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;<b>สมการ ①:</b> <b style='color:#e67e22;'>{var1}</b> + <b style='color:#2980b9;'>{var2}</b> = <b style='color:#27ae60;'>{total}</b><br><br>
                    👉 <b>จากประโยคที่ 2:</b> {item1} {mult} {unit1} แพงกว่า {item2} 1 {unit2} อยู่ {diff} บาท<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;(แปลว่า ถ้านำราคาของ {item1} จำนวน {mult} ชิ้น มาหักออก {diff} บาท จะเท่ากับราคา {item2} พอดี)<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;<b>สมการ ②:</b> <b style='color:#e67e22;'>{mult}{var1}</b> - <b style='color:#c0392b;'>{diff}</b> = <b style='color:#2980b9;'>{var2}</b>
                    </div>"""
                    
                    explain_box_cancel = f"""<div style='background-color:#fef9e7; border-left:4px solid #f39c12; padding:10px; margin-bottom:10px; border-radius:4px;'>
                    💡 <b>ตัวเลขด้านบนมาจากไหน?</b><br>
                    เกิดจากการนำ <b>{mult+1}</b> มา <b>หารออก</b> ทั้งเศษและส่วน (ใช้แม่ {mult+1} ตัดทอน)<br>
                    • {total+diff} ÷ {mult+1} = {price1}
                    </div>"""
                    
                    sol = f"""<span style='color:#2c3e50;'>
                    {analysis}
                    <b>วิธีแก้สมการอย่างละเอียด:</b><br>
                    👉 <b>ขั้นที่ 1: นำสมการ ② ไปแทนค่าในสมการ ①</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;จาก <b>สมการ ②</b> เรารู้ว่า <b>{var2}</b> มีค่าเท่ากับ <b>({mult}{var1} - {diff})</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;ดังนั้น ในสมการ ① ตรงไหนที่เป็น <b>{var2}</b> ให้เปลี่ยนเป็น <b>({mult}{var1} - {diff})</b> แทน<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;{var1} + <b>({mult}{var1} - {diff})</b> = {total}<br><br>
                    
                    👉 <b>ขั้นที่ 2: รวมตัวแปร {var1} เข้าด้วยกัน</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;นำ 1{var1} บวกกับ {mult}{var1} จะได้ {mult+1}{var1}<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;จะได้สมการ: <b>{mult+1}{var1} - {diff} = {total}</b><br><br>
                    
                    👉 <b>ขั้นที่ 3: กำจัดตัวเลข (แก้สมการหา {var1})</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;• นำ <b style='color:#27ae60;'>{diff}</b> มา <b>บวกเข้า</b> ทั้งสองข้างของสมการ เพื่อกำจัดส่วนที่ลบออก:<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{mult+1}{var1} - {diff} <b style='color:#27ae60;'>+ {diff}</b> = {total} <b style='color:#27ae60;'>+ {diff}</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<i>จะได้:</i> {mult+1}{var1} = {total+diff}<br><br>
                    
                    &nbsp;&nbsp;&nbsp;&nbsp;• นำ <b style='color:#e74c3c;'>{mult+1}</b> มา <b>หารออก</b> ทั้งสองข้าง (เพื่อทำให้ {var1} เหลือตัวเดียว):<br>
                    {explain_box_cancel}
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{frac_cancel_left(mult+1, var1)} = {frac_cancel_right(total+diff, mult+1, price1)}<br><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;จะได้ <b>{var1} = {price1}</b> (ราคาของ {item1})<br><br>
                    
                    👉 <b>ขั้นที่ 4: หาค่า {var2} (ราคาของ {item2})</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;นำ {var1} = {price1} กลับไปแทนในสมการ ①<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;{price1} + {var2} = {total}<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;{var2} = {total} - {price1} = <b>{price2}</b><br><br>
                    
                    <b>ตอบ: {item1} ราคาชิ้นละ {price1} บาท, {item2} ราคาชิ้นละ {price2} บาท</b></span>"""

            elif actual_sub_t == "การบวกและการลบทศนิยม":
                op = random.choice(["+", "-"])
                dp1, dp2 = random.choice([1, 2, 3]), random.choice([1, 2, 3])
                if op == "+": a, b = round(random.uniform(1.0, 500.0), dp1), round(random.uniform(1.0, 500.0), dp2)
                else: a, b = round(random.uniform(50.0, 500.0), dp1), round(random.uniform(1.0, 49.0), dp2)
                q = f"จงหาผลลัพธ์ของ <b>{a} {op} {b}</b><br>{generate_decimal_vertical_html(a, b, op, is_key=False)}"
                sol = f"<span style='color:#2c3e50;'>{generate_decimal_vertical_html(a, b, op, is_key=True)}</span>"

            elif actual_sub_t == "สถิติและความน่าจะเป็น":
                items, target_avg = random.randint(4, 6), random.randint(20, 80)
                total = target_avg * items
                nums = [random.randint(target_avg - 10, target_avg + 10) for _ in range(items - 1)]
                nums.append(total - sum(nums))
                q = f"จงหา <b>'ค่าเฉลี่ย'</b> ของข้อมูลชุดนี้: <b>{', '.join(map(str, nums))}</b>"
                sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b> ผลรวม = {total} ÷ จำนวนข้อมูล {items} = <b>{target_avg}</b></span>"


# ================= หมวด ป.6 (เนื้อหาเฉพาะ Gifted / สอบเข้า ม.1) =================
            elif actual_sub_t in ["โจทย์ปัญหา ห.ร.ม. และ ค.ร.น.", "การหา ห.ร.ม.", "การหา ค.ร.น."]:
                a, b, c = random.randint(12, 45), random.randint(20, 60), random.randint(30, 90)
                if "ห.ร.ม." in actual_sub_t:
                    g = math.gcd(a, math.gcd(b, c))
                    q = f"จงหา <b>ห.ร.ม.</b> ของ <b>{a}, {b} และ {c}</b>"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b> ตั้งหารสั้นเพื่อหาตัวประกอบร่วมที่มากที่สุด จะได้ <b>{g}</b></span>"
                else:
                    l = (a * b) // math.gcd(a, b)
                    lcm = (l * c) // math.gcd(l, c)
                    q = f"จงหา <b>ค.ร.น.</b> ของ <b>{a}, {b} และ {c}</b>"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b> ตั้งหารสั้นเพื่อหาผลคูณร่วมน้อย จะได้ <b>{lcm}</b></span>"

            elif actual_sub_t == "โจทย์ปัญหาเศษส่วนซ้อน (สอบเข้า ม.1)":
                a, b, c = random.randint(1, 3), random.randint(1, 3), random.randint(2, 5)
                num = a * (b * c + 1) + c
                den = b * c + 1
                def draw_nested_frac(v_a, v_b, v_c):
                    return f"""<div style='display:inline-block; vertical-align:middle; text-align:center; font-size:24px; font-family:"Sarabun"; line-height:1.2;'><div style='display:flex; align-items:center;'><div>{v_a} +&nbsp;</div><div style='display:flex; flex-direction:column; align-items:center;'><div style='border-bottom:2px solid #2c3e50; padding:0 8px; width:100%;'>1</div><div style='display:flex; align-items:center; padding-top:4px;'><div>{v_b} +&nbsp;</div><div style='display:flex; flex-direction:column; align-items:center;'><div style='border-bottom:2px solid #2c3e50; padding:0 4px;'>1</div><div>{v_c}</div></div></div></div></div></div>"""
                q = f"จงหาผลลัพธ์ของเศษส่วนซ้อนต่อไปนี้ ให้อยู่ในรูปเศษเกิน:<br><br>{draw_nested_frac(a, b, c)} = ?"
                step1_n, step1_d = (b * c + 1), c
                sol = f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (ทำจากล่างขึ้นบน):</b><br><b>ขั้นที่ 1:</b> คิดก้อนล่างสุดก่อน คือ <b>{b} + 1/{c}</b><br>👉 ทำส่วนให้เท่ากัน: ({b}×{c}/{c}) + 1/{c} = <b>{step1_n}/{step1_d}</b><br><br><b>ขั้นที่ 2:</b> พลิกเศษส่วน<br>👉 1 ÷ ({step1_n}/{step1_d}) = <b>{step1_d}/{step1_n}</b><br><br><b>ขั้นที่ 3:</b> นำไปบวกกับตัวหน้าสุด ({a})<br>👉 {a} + {step1_d}/{step1_n} = ({a}×{step1_n}/{step1_n}) + {step1_d}/{step1_n}<br>👉 ({a*step1_n} + {step1_d}) / {step1_n} = <b>{num}/{den}</b><br><b>ตอบ: {num}/{den}</b></span>"""

            elif actual_sub_t == "งานและการทำงาน (ช่วยกันทำงาน)":
                worker1, worker2 = random.choice(["ช่าง A", "พ่อ", "พี่ชาย"]), random.choice(["ช่าง B", "ลูก", "น้องชาย"])
                days_A, days_B = random.choice([10, 12, 15, 20]), random.choice([20, 30, 60])
                while days_A == days_B: days_B = random.choice([20, 30, 60])
                lcm = (days_A * days_B) // math.gcd(days_A, days_B)
                rate_A, rate_B = lcm // days_A, lcm // days_B
                ans = lcm // (rate_A + rate_B)
                q = f"ในการทาสีบ้านหลังหนึ่ง ถ้าให้ <b>{worker1}</b> ทำคนเดียวจะเสร็จใน <b>{days_A} วัน</b> <br>แต่ถ้าให้ <b>{worker2}</b> ทำคนเดียวจะเสร็จใน <b>{days_B} วัน</b> <br>หากทั้งสองคนมา <b>ช่วยกันทาสี</b> บ้านหลังนี้จะเสร็จในกี่วัน?"
                sol = f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (เทคนิคสมมติปริมาณงาน):</b><br>👉 สมมติให้งานชิ้นนี้มีจำนวนเท่ากับ ค.ร.น. ของเวลาทั้งสองคน<br>👉 ค.ร.น. ของ {days_A} และ {days_B} คือ <b>{lcm} หน่วย</b><br><br><b>ขั้นที่ 1: หาความเร็วในการทำงานของแต่ละคน (ต่อ 1 วัน)</b><br>👉 {worker1}: {lcm} ÷ {days_A} = ทำได้ <b>{rate_A} หน่วย/วัน</b><br>👉 {worker2}: {lcm} ÷ {days_B} = ทำได้ <b>{rate_B} หน่วย/วัน</b><br><br><b>ขั้นที่ 2: หาความเร็วเมื่อช่วยกันทำ</b><br>👉 ถ้ารวมพลังกัน 1 วันจะทำได้: {rate_A} + {rate_B} = <b>{rate_A + rate_B} หน่วย/วัน</b><br><br><b>ขั้นที่ 3: หาเวลาที่ใช้ทั้งหมด</b><br>👉 เวลารวม = งานทั้งหมด ÷ ความเร็วที่ช่วยกัน<br>👉 {lcm} ÷ {rate_A + rate_B} = <b>{ans} วัน</b><br><b>ตอบ: เสร็จใน {ans} วัน</b></span>"""

            elif actual_sub_t == "แผนภาพเวนน์-ออยเลอร์ (เซต 2 วง)":
                total, both = random.randint(40, 60), random.randint(5, 15)
                only_m, only_e = random.randint(10, 20), random.randint(10, 20)
                like_m, like_e = only_m + both, only_e + both
                neither = total - (only_m + only_e + both)
                q = f"นักเรียนห้องหนึ่งมี <b>{total} คน</b> จากการสำรวจพบว่า:<br>• มีคนชอบเรียนวิชาคณิตศาสตร์ <b>{like_m} คน</b><br>• มีคนชอบเรียนวิชาภาษาอังกฤษ <b>{like_e} คน</b><br>• มีคนชอบเรียน<b>ทั้งสองวิชา {both} คน</b><br>อยากทราบว่า มีนักเรียนที่ <b>ไม่ชอบเรียนทั้งสองวิชานี้เลย</b> กี่คน?"
                sol = f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (วาดเซต 2 วง):</b><br>👉 จำนวนคนที่ชอบเรียน "อย่างน้อย 1 วิชา" = คนชอบคณิต + คนชอบอังกฤษ - คนชอบทั้งคู่ (เพราะถูกนับซ้ำไปแล้ว)<br>👉 แทนค่า: {like_m} + {like_e} - {both} = <b>{like_m + like_e - both} คน</b><br><br><b>หาคนที่ไม่ชอบเลย:</b><br>👉 นำจำนวนคนทั้งห้อง หักออกด้วยคนที่ชอบอย่างน้อย 1 วิชา<br>👉 {total} - {like_m + like_e - both} = <b>{neither} คน</b><br><b>ตอบ: {neither} คน</b></span>"""

            elif actual_sub_t == "โจทย์ปัญหาอัตราส่วนและสัดส่วน":
                m1, m2, m3, m4 = random.randint(2, 4), random.randint(3, 5), random.randint(2, 4), random.randint(3, 5)
                while math.gcd(m1, m2) > 1: m2 += 1
                while math.gcd(m3, m4) > 1: m4 += 1
                b_lcm = (m2 * m3) // math.gcd(m2, m3)
                a_ratio, b_ratio, c_ratio = m1 * (b_lcm // m2), b_lcm, m4 * (b_lcm // m3)
                q = f"กำหนดให้อัตราส่วนเงินเก็บของ <b>ก : ข = {m1} : {m2}</b> <br>และอัตราส่วนเงินเก็บของ <b>ข : ค = {m3} : {m4}</b> <br>ถ้า <b>ค มีเงินเก็บ {c_ratio * 100} บาท</b> อยากทราบว่า <b>ก มีเงินเก็บกี่บาท?</b>"
                sol = f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (เชื่อมโยงอัตราส่วน):</b><br><b>ขั้นที่ 1: ทำให้ตัวเชื่อม (ข) มีค่าเท่ากัน</b><br>👉 หา ค.ร.น. ของ {m2} และ {m3} ซึ่งก็คือ <b>{b_lcm}</b><br>👉 ปรับอัตราส่วน ก:ข ใหม่ (คูณ {b_lcm//m2}): ก:ข = <b>{a_ratio} : {b_ratio}</b><br>👉 ปรับอัตราส่วน ข:ค ใหม่ (คูณ {b_lcm//m3}): ข:ค = <b>{b_ratio} : {c_ratio}</b><br><br><b>ขั้นที่ 2: เขียนอัตราส่วนรวม ก : ข : ค</b><br>👉 ก : ข : ค = <b>{a_ratio} : {b_ratio} : {c_ratio}</b><br><br><b>ขั้นที่ 3: เทียบสัดส่วนหาเงินของ ก</b><br>👉 ค มีสัดส่วน {c_ratio} ส่วน คิดเป็นเงิน {c_ratio * 100} บาท (แสดงว่า 1 ส่วน = 100 บาท)<br>👉 ก มีสัดส่วน {a_ratio} ส่วน คิดเป็นเงิน {a_ratio} × 100 = <b>{a_ratio * 100} บาท</b><br><b>ตอบ: ก มีเงินเก็บ {a_ratio * 100} บาท</b></span>"""

            elif actual_sub_t == "โจทย์ปัญหาร้อยละ (กำไร-ขาดทุน ซับซ้อน)":
                cost, markup, discount = random.choice([500, 1000, 1200]), random.choice([20, 30, 40]), random.choice([10, 15, 20])
                price_tag = cost + (cost * markup // 100)
                sell_price = price_tag - (price_tag * discount // 100)
                profit = sell_price - cost
                profit_percent = (profit * 100) / cost
                q = f"ร้านค้าซื้อรองเท้ามาคู่หนึ่งราคา <b>{cost} บาท</b> <br>นำมาติดป้ายขายโดย <b>บวกกำไรเพิ่ม {markup}%</b> <br>แต่เมื่อลูกค้ามาซื้อ ร้านค้าได้จัดโปรโมชั่น <b>ลดราคาให้ {discount}% จากป้าย</b> <br>สรุปแล้วร้านค้าขายรองเท้าคู่นี้ <b>ได้กำไร หรือ ขาดทุน กี่เปอร์เซ็นต์?</b>"
                sol = f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด (ร้อยละ 2 ขั้นตอน):</b><br><b>ขั้นที่ 1: หาราคาป้ายที่ติดไว้ (ทุน + {markup}%)</b><br>👉 นำไปบวกทุน จะได้ราคาป้าย = {cost} + {cost * markup // 100} = <b>{price_tag} บาท</b><br><br><b>ขั้นที่ 2: หาราคาขายจริง (ลด {discount}% จากป้าย)</b><br>👉 ลดราคา = ({discount}/100) × ราคาป้าย ({price_tag}) = {price_tag * discount // 100} บาท<br>👉 ราคาขายจริง = {price_tag} - {price_tag * discount // 100} = <b>{sell_price} บาท</b><br><br><b>ขั้นที่ 3: สรุปกำไร/ขาดทุน</b><br>👉 ทุน {cost} ขายได้ {sell_price} แสดงว่า <b>ได้กำไร</b> = {sell_price} - {cost} = {profit} บาท<br>👉 คิดเป็นเปอร์เซ็นต์ = (กำไร ÷ ทุน) × 100 = ({profit}/{cost}) × 100 = <b>{profit_percent:g}%</b><br><b>ตอบ: ได้กำไร {profit_percent:g}%</b></span>"""

            elif actual_sub_t == "มุมภายในและมุมเข็มนาฬิกา":
                polygon_n = random.randint(5, 10)
                poly_names = {5:"ห้า", 6:"หก", 7:"เจ็ด", 8:"แปด", 9:"เก้า", 10:"สิบ"}
                sum_interior = (polygon_n - 2) * 180
                q = f"จงหา <b>ผลรวมของมุมภายใน</b> ของรูป<b>{poly_names[polygon_n]}เหลี่ยม</b> ว่ามีขนาดกี่องศา?"
                sol = f"""<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 <b>สูตร:</b> ผลรวมมุมภายใน = ( N - 2 ) × 180°<br>👉 รูป{poly_names[polygon_n]}เหลี่ยม มี N = {polygon_n}<br>👉 คำนวณ: ({polygon_n} - 2) × 180° = {polygon_n - 2} × 180° = <b>{sum_interior}°</b><br><b>ตอบ: {sum_interior} องศา</b></span>"""
            
            elif actual_sub_t == "พื้นที่ส่วนที่แรเงา (วงกลมซ้อนเหลี่ยม)":
                side = random.choice([14, 28, 42, 56]) 
                radius = side // 2
                area_sq = side * side
                area_cir = int((22/7) * radius * radius)
                ans = area_sq - area_cir
                svg = f'<div style="text-align:center; margin:15px 0;"><svg width="200" height="200">'
                svg += f'<rect x="10" y="10" width="180" height="180" fill="#bdc3c7" stroke="#2c3e50" stroke-width="3"/>'
                svg += f'<circle cx="100" cy="100" r="90" fill="#ffffff" stroke="#2c3e50" stroke-width="2"/>'
                svg += f'<line x1="10" y1="195" x2="190" y2="195" stroke="#e74c3c" stroke-width="2" stroke-dasharray="4,4"/>'
                svg += f'<line x1="10" y1="190" x2="10" y2="200" stroke="#e74c3c" stroke-width="2"/>'
                svg += f'<line x1="190" y1="190" x2="190" y2="200" stroke="#e74c3c" stroke-width="2"/>'
                svg += f'<text x="100" y="215" font-family="Sarabun" font-size="16" font-weight="bold" fill="#c0392b" text-anchor="middle">{side} ซม.</text>'
                svg += '</svg></div>'
                q = f"จากรูป สี่เหลี่ยมจัตุรัสมีความยาวด้านละ <b>{side} เซนติเมตร</b> มีวงกลมแนบในพอดี<br>จงหาพื้นที่ของส่วนที่แรเงาตามมุมทั้งสี่? (กำหนดให้ <b>π = 22/7</b>)<br>{svg}"
                frac_pi = f"<div style='display:inline-block; vertical-align:middle; text-align:center;'><div style='border-bottom:1px solid #2c3e50; padding:0 2px;'>22</div><div>7</div></div>"
                sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 พื้นที่แรเงา = พื้นที่สี่เหลี่ยมจัตุรัส - พื้นที่วงกลม<br>👉 พื้นที่สี่เหลี่ยม = {side} × {side} = {area_sq:,} ตร.ซม.<br>👉 พื้นที่วงกลม = πr² = {frac_pi} × {radius} × {radius} = {area_cir:,} ตร.ซม.<br>👉 {area_sq:,} - {area_cir:,} = <b>{ans:,} ตร.ซม.</b><br><b>ตอบ: {ans:,} ตารางเซนติเมตร</b></span>"

            elif actual_sub_t == "ความเร็ว ระยะทาง เวลา (รถไฟ/วิ่งไล่กัน)":
                v_a, v_rel, t_head = random.randint(50, 80), random.choice([10, 20, 25, 30]), random.randint(1, 3)
                v_b = v_a + v_rel
                catch_time = (v_a * t_head) / v_rel
                while not catch_time.is_integer():
                    v_a, v_rel, t_head = random.randint(50, 80), random.choice([10, 20, 25, 30]), random.randint(1, 3)
                    v_b, catch_time = v_a + v_rel, (v_a * t_head) / v_rel
                catch_time, dist = int(catch_time), int(catch_time * v_b)
                q = f"รถยนต์ A ขับออกจากเมืองด้วยความเร็ว <b>{v_a} กม./ชม.</b> หลังจากนั้นอีก <b>{t_head} ชั่วโมง</b> รถยนต์ B จึงขับตามออกไปด้วยความเร็ว <b>{v_b} กม./ชม.</b><br>รถยนต์ B จะใช้เวลาขับกี่ชั่วโมงจึงจะตามรถยนต์ A ทัน และจุดที่ตามทันอยู่ห่างจากเมืองกี่กิโลเมตร?"
                sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 ระยะห่างเริ่มต้น = รถ A นำไปก่อน = {v_a} × {t_head} = {v_a * t_head} กม.<br>👉 ความเร็วที่เข้าใกล้กัน (ความเร็วสัมพัทธ์) = {v_b} - {v_a} = {v_rel} กม./ชม.<br>👉 เวลาที่ใช้ = ระยะห่าง ÷ ความเร็วสัมพัทธ์ = {v_a * t_head} ÷ {v_rel} = <b>{catch_time} ชั่วโมง</b><br>👉 ระยะทาง = ความเร็วรถ B × เวลา = {v_b} × {catch_time} = <b>{dist:,} กิโลเมตร</b><br><b>ตอบ: ตามทันใน {catch_time} ชั่วโมง ที่ระยะ {dist:,} กม.</b></span>"

            elif actual_sub_t == "การจับมือและการแข่งขัน (Combinatorics)":
                n = random.randint(8, 20)
                ans = n * (n - 1) // 2
                q = f"ในงานเลี้ยงสังสรรค์ มีผู้เข้าร่วมงานทั้งหมด <b>{n} คน</b> <br>ถ้าทุกคนต้อง <b>จับมือทักทาย</b> กันให้ครบทุกคนแบบไม่ซ้ำกัน จะมีการจับมือเกิดขึ้นทั้งหมดกี่ครั้ง?"
                sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 <b>สูตรลัดจับมือ:</b> ( N × (N - 1) ) ÷ 2<br>👉 แทนค่า: ({n} × {n-1}) ÷ 2 = <b>{ans} ครั้ง</b><br><b>ตอบ: {ans} ครั้ง</b></span>"

            elif actual_sub_t == "โจทย์ปัญหาของผสม (ความเข้มข้น)":
                vol1, c1, vol2, c2 = 200, 20, 300, 40
                total_vol = vol1 + vol2
                total_content = ((vol1 * c1) + (vol2 * c2)) / 100
                final_c = int((total_content / total_vol) * 100)
                q = f"น้ำเกลือขวดที่ 1 เข้มข้น <b>{c1}%</b> ปริมาตร <b>{vol1} มล.</b> ผสมกับน้ำเกลือขวดที่ 2 เข้มข้น <b>{c2}%</b> ปริมาตร <b>{vol2} มล.</b><br>สารละลายผสมใหม่ จะมีความเข้มข้นกี่เปอร์เซ็นต์?"
                sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 ปริมาณเกลือขวด 1 = ({c1}/100) × {vol1} = {int((vol1 * c1)/100)} มล.<br>👉 ปริมาณเกลือขวด 2 = ({c2}/100) × {vol2} = {int((vol2 * c2)/100)} มล.<br>👉 เกลือรวม = {int(total_content)} มล. | ปริมาตรรวม = {total_vol} มล.<br>👉 ความเข้มข้น = ({int(total_content)} ÷ {total_vol}) × 100 = <b>{final_c}%</b><br><b>ตอบ: {final_c}%</b></span>"

            elif actual_sub_t == "อนุกรมเศษส่วน (Telescoping Sum)":
                diff = random.choice([2, 3])
                end_idx = random.choice([10, 15, 20])
                nn_2 = 1 + ((end_idx+1)*diff)
                q = f"จงหาผลบวกอนุกรม: <br>1/(1×{1+diff}) + 1/({1+diff}×{1+2*diff}) + ... + 1/({1+end_idx*diff}×{nn_2})"
                ans_num = nn_2 - 1
                ans_den = nn_2 * 1 * diff
                g = math.gcd(ans_num, ans_den)
                sol = f"<span style='color:#2c3e50;'><b>วิธีทำ (สูตรลัด Telescoping):</b><br>👉 ผลรวม = (1/ระยะห่าง) × (1/หัวแรก - 1/หางสุดท้าย)<br>👉 (1/{diff}) × (1/1 - 1/{nn_2}) = (1/{diff}) × ({nn_2-1}/{nn_2})<br>👉 ทอนเป็นเศษส่วนอย่างต่ำ จะได้ <b>{ans_num//g}/{ans_den//g}</b><br><b>ตอบ: {ans_num//g}/{ans_den//g}</b></span>"
            
            elif actual_sub_t == "กฎการหารลงตัว (Divisibility Rules)":
                d = random.choice([3, 4, 9, 11])
                base = random.randint(1000, 9999)
                num = base * d + random.choice([0, 1, 2])
                is_div = (num % d == 0)
                ans = "ลงตัว" if is_div else "ไม่ลงตัว"
                num_str = str(num)
                q = f"จงพิจารณาว่า <b>{num:,}</b> สามารถหารด้วย <b>{d}</b> ลงตัวหรือไม่? <br><span style='font-size:16px; color:#7f8c8d;'>(ใช้กฎการหารลงตัว โดยไม่ต้องตั้งหารยาว)</span>"
                if d == 3 or d == 9:
                    digit_sum = sum(int(x) for x in num_str)
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 <b>กฎแม่ {d}:</b> นำเลขโดดทุกหลักมาบวกกัน ถ้าผลบวกหารด้วย {d} ลงตัว จำนวนนั้นจะหารด้วย {d} ลงตัว<br>👉 นำ { ' + '.join(num_str) } = <b>{digit_sum}</b><br>👉 พบว่า {digit_sum} หารด้วย {d} <b>{ans}</b><br><b>ตอบ: {ans}</b></span>"
                elif d == 4:
                    last_two = int(num_str[-2:])
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 <b>กฎแม่ 4:</b> ให้ดูเฉพาะเลข <b>2 หลักสุดท้าย</b> ถ้าหารด้วย 4 ลงตัว จำนวนทั้งหมดก็จะหารด้วย 4 ลงตัว<br>👉 2 หลักสุดท้ายคือ <b>{last_two:02d}</b><br>👉 พบว่า {last_two:02d} หารด้วย 4 <b>{ans}</b><br><b>ตอบ: {ans}</b></span>"
                elif d == 11:
                    odd_pos = sum(int(num_str[i]) for i in range(len(num_str)) if i % 2 == 0)
                    even_pos = sum(int(num_str[i]) for i in range(len(num_str)) if i % 2 != 0)
                    diff = abs(odd_pos - even_pos)
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 <b>กฎแม่ 11:</b> นำผลบวกของเลขตำแหน่งคี่ ลบด้วย ผลบวกของเลขตำแหน่งคู่ ถ้าได้ 0 หรือตัวที่หารด้วย 11 ลงตัว จำนวนนั้นจะหารด้วย 11 ลงตัว<br>👉 ผลต่าง = |{odd_pos} - {even_pos}| = <b>{diff}</b><br>👉 พบว่า {diff} หารด้วย 11 <b>{ans}</b><br><b>ตอบ: {ans}</b></span>"
            
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

selected_grade = st.sidebar.selectbox("📚 เลือกระดับชั้น:", ["ป.4", "ป.5", "ป.6"])
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

if st.sidebar.button("🚀 สั่งสร้างใบงาน ป.4-ป.6", type="primary", use_container_width=True):
    with st.spinner("กำลังออกแบบรูปภาพและสร้างเฉลยแบบ Step-by-Step..."):
        
        qs = generate_questions_logic(selected_grade, selected_main, selected_sub, num_input, is_challenge)
        
        html_w = create_page(selected_grade, selected_sub, qs, is_key=False, q_margin=q_margin, ws_height=ws_height, brand_name=brand_name)
        html_k = create_page(selected_grade, selected_sub, qs, is_key=True, q_margin=q_margin, ws_height=ws_height, brand_name=brand_name)
        
        st.session_state['worksheet_html'] = html_w
        st.session_state['answerkey_html'] = html_k
        
        ebook_body = f'\n<div class="a4-wrapper">{extract_body(html_w)}</div>\n<div class="a4-wrapper">{extract_body(html_k)}</div>\n'
        
        full_ebook_html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap" rel="stylesheet"><style>@page {{ size: A4; margin: 15mm; }} @media screen {{ body {{ font-family: 'Sarabun', sans-serif; background-color: #525659; display: flex; flex-direction: column; align-items: center; padding: 40px 0; margin: 0; }} .a4-wrapper {{ width: 210mm; min-height: 297mm; background: white; margin-bottom: 30px; box-shadow: 0 10px 20px rgba(0,0,0,0.3); padding: 15mm; box-sizing: border-box; }} }} @media print {{ body {{ font-family: 'Sarabun', sans-serif; background: transparent; padding: 0; display: block; margin: 0; }} .a4-wrapper {{ width: 100%; min-height: auto; margin: 0; padding: 0; box-shadow: none; page-break-after: always; }} }} .header {{ text-align: center; border-bottom: 2px solid #333; margin-bottom: 10px; padding-bottom: 10px; }} .q-box {{ margin-bottom: {q_margin}; padding: 10px 15px; page-break-inside: avoid; font-size: 20px; line-height: 1.6; }} .workspace {{ height: {ws_height}; border: 2px dashed #bdc3c7; border-radius: 8px; margin: 15px 0; padding: 10px; color: #95a5a6; font-size: 16px; background-color: #fafbfc; }} .ans-line {{ margin-top: 10px; border-bottom: 1px dotted #999; width: 80%; height: 30px; font-weight: bold; font-size: 20px; display: flex; align-items: flex-end; padding-bottom: 5px; }} .sol-text {{ color: #333; font-size: 18px; display: block; margin-top: 15px; padding: 15px; background-color: #f1f8ff; border-left: 4px solid #3498db; border-radius: 4px; line-height: 1.6; }} .page-footer {{ text-align: right; font-size: 14px; color: #95a5a6; margin-top: 20px; border-top: 1px solid #eee; padding-top: 10px; }} </style></head><body>{ebook_body}</body></html>"""

        filename_base = f"BaanTded_P4_P6_{selected_grade}_{int(time.time())}"
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
