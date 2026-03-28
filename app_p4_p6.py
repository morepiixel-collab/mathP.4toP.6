import streamlit as st
import streamlit.components.v1 as components
import random
import math
import zipfile
import io
import time

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
st.set_page_config(page_title="Math Generator Pro - P.4 & P.5", page_icon="🚀", layout="wide")

st.markdown("""
<style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1200px; }
    div[data-testid="stSidebar"] div.stButton > button { background-color: #27ae60; color: white; border-radius: 8px; height: 3.5rem; font-size: 18px; font-weight: bold; transition: all 0.3s ease; border: none; box-shadow: 0 4px 6px rgba(39,174,96,0.3); }
    div[data-testid="stSidebar"] div.stButton > button:hover { background-color: #219653; box-shadow: 0 6px 12px rgba(39,174,96,0.4); transform: translateY(-2px); }
    div.stDownloadButton > button { border-radius: 8px; font-weight: bold; border: 1px solid #bdc3c7; transition: all 0.2s ease; }
    div.stDownloadButton > button:hover { border-color: #3498db; color: #3498db; }
    .main-header { background: linear-gradient(135deg, #2980b9, #2c3e50); padding: 2rem; border-radius: 15px; color: white; margin-bottom: 2rem; box-shadow: 0 10px 20px rgba(0,0,0,0.15); transition: all 0.3s ease; }
    .main-header h1 { margin: 0; font-size: 2.8rem; font-weight: 800; text-shadow: 2px 2px 4px rgba(0,0,0,0.2); }
    .main-header p { margin: 10px 0 0 0; font-size: 1.2rem; opacity: 0.9; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>🚀 Math Worksheet Pro <span style="font-size: 20px; background: #f39c12; color: #fff; padding: 5px 15px; border-radius: 20px; vertical-align: middle;">ป.4 - ป.5 Edition</span></h1>
    <p>ระบบสร้างสื่อการสอนคณิตศาสตร์ (ป.4 - ป.5) พร้อมระบบ Spacing ที่ยืดหยุ่น และเฉลยละเอียดยิบ</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 1. คลังคำศัพท์และฟังก์ชันตัวช่วย
# ==========================================
NAMES = ["อคิณ", "นาวิน", "ภูผา", "สายฟ้า", "เจ้านาย", "ข้าวหอม", "ใบบัว", "มะลิ", "น้ำใส", "ญาญ่า", "ปลื้ม", "พายุ", "ไออุ่น"]
ROOMS = ["ห้องนอน", "ห้องนั่งเล่น", "ห้องเรียน", "ห้องทำงาน", "ห้องประชุม", "ห้องเก็บของ"]
FURNITURE = ["ตู้เสื้อผ้า", "โต๊ะทำงาน", "เตียงนอน", "ชั้นวางหนังสือ", "โซฟา", "ตู้โชว์", "โต๊ะเรียน", "ตู้เก็บเอกสาร"]

def f_html(n, d, c="#2c3e50", b=True):
    w = "bold" if b else "normal"
    return f"<span style='display:inline-flex; flex-direction:column; vertical-align:middle; text-align:center; line-height:1.4; margin:0 4px;'><span style='border-bottom:2px solid {c}; padding:0 4px; font-weight:{w}; color:{c};'>{n}</span><span style='padding:0 4px; font-weight:{w}; color:{c};'>{d}</span></span>"

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
            <tr><td style='padding: 5px 10px 5px 0; border: none; border-bottom: 2px solid #000;'>{b_str}</td></tr>
            <tr>
                <td style='padding: 5px 10px 0 0; border: none; {border_ans} height: 35px;'>{ans_val}</td>
                <td style='border: none;'></td>
            </tr>
        </table>
    </div>
    """

def generate_mixed_number_html(whole, num, den):
    return f"<span style='font-size: 24px; vertical-align: middle;'>{whole}</span> {f_html(num, den)}"

def generate_short_division_html(a, b, mode="ห.ร.ม."):
    factors = []
    ca, cb = a, b
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
        if mode == "ห.ร.ม.": return f"<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>ไม่มีตัวเลขใดหารทั้ง {a} และ {b} ลงตัวพร้อมกัน<br><b>ดังนั้น ห.ร.ม. = 1</b></span>"
        else: return f"<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>ไม่มีตัวเลขใดหารลงตัวทั้งคู่<br><b>ดังนั้น ค.ร.น. = {a} × {b} = {a*b}</b></span>"
    steps_html += f"<tr><td></td><td style='padding: 5px 15px; text-align: center;'>{ca}</td><td style='padding: 5px 15px; text-align: center;'>{cb}</td></tr>"
    table = f"<table style='margin: 10px 0; font-size: 20px; border-collapse: collapse; color: #333;'>{steps_html}</table>"
    if mode == "ห.ร.ม.":
        ans = math.prod(factors)
        calc_str = " × ".join(map(str, factors))
        sol = f"<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด (การตั้งหารสั้น):</b><br>{table}<b>ดังนั้น ห.ร.ม. = {calc_str} = {ans}</b></span>"
    else:
        ans = math.prod(factors) * ca * cb
        calc_str = " × ".join(map(str, factors + [ca, cb]))
        sol = f"<span style='color: #2c3e50;'><b>วิธีทำอย่างละเอียด (การตั้งหารสั้น):</b><br>{table}<b>ดังนั้น ค.ร.น. = {calc_str} = {ans}</b></span>"
    return sol

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
            a_chars, b_chars = list(str_a), list(str_b)
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
            for _ in range(div_len + 1): empty_rows += f"<td style='width: 35px; height: 45px;'></td>"
            empty_rows += "</tr>"
        return f"{equation_html}<div style=\"display: block; margin-left: 60px; margin-top: 15px; margin-bottom: 15px;\"><div style=\"display: inline-block; font-family: 'Sarabun', sans-serif; line-height: 1.2;\"><table style=\"border-collapse: collapse;\"><tr><td style=\"border: none;\"></td>{''.join(ans_tds_list)}</tr><tr><td style=\"border: none; text-align: right; padding-right: 12px; vertical-align: bottom; font-size: 38px;\">{divisor}</td>{''.join(div_tds_list)}</tr>{empty_rows}</table></div></div>"
    
    steps = []
    current_val_str, ans_str, has_started = "", "", False
    
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
        cur_chars, m_chars = list(str(current_val)), list(str(mul_res).zfill(len(str(current_val))))
        c_dig, m_dig = [int(c) for c in cur_chars], [int(c) for c in m_chars]
        
        top_m, strik = [""] * len(c_dig), [False] * len(c_dig)
        for idx_b in range(len(c_dig) - 1, -1, -1):
            if c_dig[idx_b] < m_dig[idx_b]:
                for j in range(idx_b-1, -1, -1):
                    if c_dig[j] > 0:
                        strik[j], c_dig[j] = True, c_dig[j] - 1
                        top_m[j] = str(c_dig[j])
                        for k in range(j+1, idx_b): 
                            strik[k], c_dig[k] = True, 9
                            top_m[k] = "9"
                        strik[idx_b], c_dig[idx_b] = True, c_dig[idx_b] + 10
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
            mark, is_strik = s0['top_m'][t_idx], s0['strik'][t_idx]
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
            else: mul_tds += '<td style="width: 35px;"></td>'
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
                    mark, is_strik = next_step['top_m'][t_idx], next_step['strik'][t_idx]
                    if is_strik: td_content = f'<div style="position: relative;"><span style="position: absolute; top: -25px; left: 50%; transform: translateX(-50%); font-size: 20px; color: red; font-weight: bold;">{mark}</span><span style="text-decoration: line-through; text-decoration-color: red; text-decoration-thickness: 2px;">{char_val}</span></div>'
                    elif mark: td_content = f'<div style="position: relative;"><span style="position: absolute; top: -25px; left: 50%; transform: translateX(-50%); font-size: 20px; color: red; font-weight: bold;">{mark}</span><span>{char_val}</span></div>'
                border_b2 = "border-bottom: 6px double #000;" if is_last_step else ""
                rem_tds += f'<td style="width: 35px; height: 50px; vertical-align: bottom; text-align: center; font-size: 38px; {border_b2}">{td_content}</td>'
            else: rem_tds += '<td style="width: 35px;"></td>'
        html += f"<tr><td style='border: none;'></td>{rem_tds}</tr>"
    return html + "</table></div></div>"

def generate_thai_number_text(num_str):
    thai_nums = ["ศูนย์", "หนึ่ง", "สอง", "สาม", "สี่", "ห้า", "หก", "เจ็ด", "แปด", "เก้า"]
    positions = ["", "สิบ", "ร้อย", "พัน", "หมื่น", "แสน", "ล้าน"]
    parts = str(num_str).replace(",", "").split(".")
    int_part = parts[0]
    dec_part = parts[1] if len(parts) > 1 else ""
    
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
        
    int_text = read_int(int_part)
    dec_text = ("จุด" + "".join([thai_nums[int(d)] for d in dec_part])) if dec_part else ""
    return int_text + dec_text


# ==========================================
# 2. ฐานข้อมูลหลักสูตร (ป.4 - ป.5)
# ==========================================
curriculum_db = {
    "ป.4": {
        "จำนวนนับที่มากกว่า 100,000": ["การอ่านและการเขียนตัวเลข", "หลัก ค่าประจำหลัก และรูปกระจาย", "การเปรียบเทียบและเรียงลำดับ", "ค่าประมาณเป็นจำนวนเต็มสิบ เต็มร้อย เต็มพัน"],
        "การบวก ลบ คูณ หาร": ["การบวก (แบบตั้งหลัก)", "การลบ (แบบตั้งหลัก)", "การคูณ (แบบตั้งหลัก)", "การหารยาว"],
        "เศษส่วนและทศนิยม": ["แปลงเศษเกินเป็นจำนวนคละ", "การอ่านและการเขียนทศนิยม"],
        "เรขาคณิตและการวัด": ["การบอกชนิดของมุม", "การวัดขนาดของมุม (ไม้โปรแทรกเตอร์)", "การสร้างมุมตามขนาดที่กำหนด", "โจทย์ปัญหาเรื่องมุมจากเข็มนาฬิกา", "การหาความยาวรอบรูปสี่เหลี่ยมมุมฉาก", "การหาพื้นที่รูปสี่เหลี่ยมมุมฉาก"],
        "สมการ": ["การแก้สมการ (บวก/ลบ)", "สมการและตัวไม่ทราบค่าจากชีวิตประจำวัน", "สมการเชิงตรรกะและตาชั่งปริศนา", "โจทย์ปัญหาสมการ: ตาชั่งผลไม้", "โจทย์ปัญหาสมการ: ความสัมพันธ์ของ 2 สิ่ง"]
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
        "เตรียมสอบเข้า ม.1 (Gifted)": ["โจทย์ปัญหา ห.ร.ม. และ ค.ร.น.", "โจทย์ปัญหาคลาสสิก (สมการประยุกต์)", "แบบรูปและอนุกรม (Number Patterns)", "มาตราส่วนและทิศทาง", "เรขาคณิตประยุกต์ (หาพื้นที่แรเงา)"]
    }
}

# ==========================================
# 3. Logic & Dynamic Difficulty Scaling
# ==========================================
def generate_questions_logic(grade, main_t, sub_t, num_q, is_challenge=False):
    questions = []
    seen = set()
    
    for _ in range(num_q):
        q = ""
        sol = ""
        attempts = 0
        
        while attempts < 300:
            actual_sub_t = sub_t

            # ================= หมวด ป.5 =================
            if actual_sub_t == "การบวกและการลบทศนิยม":
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
                op = random.choice(["×", "÷"])
                if op == "×":
                    dp1, dp2 = random.choice([1, 2]), random.choice([1, 2])
                    if is_challenge:
                        a, b = round(random.uniform(10.0, 99.99), dp1), round(random.uniform(5.0, 50.99), dp2)
                    else:
                        a, b = round(random.uniform(1.0, 15.9), dp1), round(random.uniform(1.0, 9.9), dp2)
                        
                    ans = round(a * b, dp1 + dp2)
                    a_str, b_str, ans_str = f"{a:.{dp1}f}", f"{b:.{dp2}f}", f"{ans:.{dp1+dp2}f}"
                    a_int, b_int = int(a_str.replace(".", "")), int(b_str.replace(".", ""))
                    
                    q = f"จงหาผลคูณของ <b>{a_str} × {b_str}</b>"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 นับตำแหน่งทศนิยมรวม: {dp1} + {dp2} = {dp1+dp2} ตำแหน่ง<br>👉 นำตัวเลขคูณกัน: {a_int:,} × {b_int:,} = {a_int * b_int:,}<br>👉 ใส่จุดทศนิยมกลับเข้าไป {dp1+dp2} ตำแหน่ง จะได้ <b>{ans_str}</b><br><b>ตอบ: {ans_str}</b></span>"
                else:
                    dp_ans, dp_b = random.choice([1, 2]), random.choice([1, 2])
                    is_exact = random.choice([True, False])
                    if is_exact:
                        ans_val = round(random.uniform(5.0, 50.0) if is_challenge else random.uniform(1.0, 12.0), dp_ans)
                        b = round(random.uniform(2.0, 15.0) if is_challenge else random.choice([0.2, 0.5, 1.5, 2.5]), dp_b)
                        a = round(ans_val * b, dp_ans + dp_b)
                    else:
                        a = round(random.uniform(20.0, 99.0) if is_challenge else random.uniform(5.0, 25.0), 1)
                        b = round(random.choice([0.3, 0.7, 0.9]) if is_challenge else random.choice([0.3, 0.6, 1.5]), 1)
                        
                    a_str, b_str = f"{a:g}", f"{b:g}"
                    b_dp = len(b_str.split('.')[1]) if '.' in b_str else 0
                    mult_factor = 10 ** b_dp
                    a_shift_str = f"{round(a * mult_factor, 4):g}" 
                    b_shift = int(round(b * mult_factor))
                    
                    q = f"จงหาผลลัพธ์ของ <b>{a_str} ÷ {b_str}</b>"
                    ans_str = f"{a/b:.2f}" if not is_exact else f"{a/b:g}"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำอย่างละเอียด:</b><br>👉 เลื่อนจุดทศนิยมของตัวหารให้เป็นจำนวนเต็ม (คูณ {mult_factor:,})<br>👉 ตัวตั้ง: {a_str} × {mult_factor:,} = {a_shift_str}<br>👉 ตัวหาร: {b_str} × {mult_factor:,} = {b_shift:,}<br>👉 ตั้งหารยาว {a_shift_str} ÷ {b_shift:,} = <b>{ans_str}</b><br><b>ตอบ: {ans_str}</b></span>"

            elif actual_sub_t == "โจทย์ปัญหาบัญญัติไตรยางศ์":
                scenario = random.choice(["buy_change", "recipe_convert", "work_time"])
                if scenario == "buy_change":
                    unit_price = random.randint(7, 25)
                    A = random.randint(4, 12) * 5 
                    B = A * unit_price 
                    C_budget = (random.randint(15, 40) * 10 * unit_price) + random.randint(1, unit_price - 1)
                    max_items = C_budget // unit_price
                    rem_money = C_budget % unit_price
                    q = f"แม่ค้าขายขนม <b>{A} ชิ้น</b> ราคา <b>{B:,} บาท</b> <br>ถ้ามีเงิน <b>{C_budget:,} บาท</b> จะซื้อขนมได้มากที่สุดกี่ชิ้น และเหลือเงินทอนกี่บาท?"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b><br>👉 หาชิ้นละกี่บาท: {B:,} ÷ {A} = {unit_price:,} บาท<br>👉 นำเงินที่มีไปหาร: {C_budget:,} ÷ {unit_price:,} ได้ {max_items:,} เศษ {rem_money:,}<br><b>ตอบ: ซื้อได้ {max_items:,} ชิ้น เหลือเงินทอน {rem_money:,} บาท</b></span>"
                elif scenario == "recipe_convert":
                    pA, g_per = random.randint(4, 10), random.randint(120, 350)
                    totA = pA * g_per
                    pC = random.randint(25, 80)
                    totC = pC * g_per
                    q = f"อาหารสำหรับ <b>{pA} คน</b> ใช้เนื้อสัตว์ <b>{totA:,} กรัม</b><br>ถ้าทำอาหารเลี้ยง <b>{pC} คน</b> ต้องใช้เนื้อสัตว์กี่กิโลกรัม กี่กรัม?"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b><br>👉 หาปริมาณต่อคน: {totA:,} ÷ {pA} = {g_per:,} กรัม<br>👉 สำหรับ {pC} คน = {g_per:,} × {pC} = {totC:,} กรัม<br>👉 แปลงหน่วย: {totC//1000} กก. {totC%1000} กรัม<br><b>ตอบ: {totC//1000} กิโลกรัม {totC%1000} กรัม</b></span>"
                else:
                    tA, rate = random.randint(2, 10), random.randint(15, 60)
                    amtA = tA * rate
                    tC = random.randint(15, 45)
                    while tC == tA: tC = random.randint(15, 45)
                    ans = tC * rate
                    q = f"เครื่องจักรใช้เวลา <b>{tA} นาที</b> ผลิตสินค้าได้ <b>{amtA:,} ชิ้น</b><br>ถ้าเปิดเครื่องทำงาน <b>{tC} นาที</b> จะผลิตได้กี่ชิ้น?"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b><br>👉 หา 1 นาทีผลิตได้: {amtA:,} ÷ {tA} = {rate:,} ชิ้น<br>👉 สำหรับ {tC} นาที = {rate:,} × {tC} = {ans:,} ชิ้น<br><b>ตอบ: {ans:,} ชิ้น</b></span>"

            elif actual_sub_t == "การหาค่าเฉลี่ย (Average)":
                scenario = random.choice(["basic", "missing", "total_from_avg"])
                if scenario == "basic":
                    items = random.randint(4, 6)
                    target_avg = random.randint(20, 80)
                    total = target_avg * items
                    nums = [random.randint(target_avg - 10, target_avg + 10) for _ in range(items - 1)]
                    nums.append(total - sum(nums))
                    random.shuffle(nums)
                    q = f"น้ำหนักของนักเรียน <b>{items} คน</b> มีดังนี้: {', '.join(map(str, nums))} กิโลกรัม<br>จงหาน้ำหนัก <b>'เฉลี่ย'</b>?"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b><br>👉 ผลรวมทั้งหมด = {total} กิโลกรัม<br>👉 ค่าเฉลี่ย = {total} ÷ {items} = <b>{target_avg} กก.</b><br><b>ตอบ: {target_avg} กิโลกรัม</b></span>"
                elif scenario == "missing":
                    items, target_avg = random.randint(3, 5), random.randint(40, 90)
                    total = target_avg * items
                    nums = [random.randint(target_avg - 15, target_avg + 15) for _ in range(items - 1)]
                    missing_val = total - sum(nums)
                    q = f"นักเรียน <b>{items} คน</b> มีคะแนนเฉลี่ย <b>{target_avg} คะแนน</b><br>ถ้ารู้คะแนน {items-1} คน คือ {', '.join(map(str, nums))}<br>จงหาคะแนนของคนที่เหลือ?"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b><br>👉 คะแนนรวมทั้งหมด = {items} × {target_avg} = {total} คะแนน<br>👉 คะแนนคนที่มี = {sum(nums)} คะแนน<br>👉 คะแนนคนที่หายไป = {total} - {sum(nums)} = <b>{missing_val} คะแนน</b><br><b>ตอบ: {missing_val} คะแนน</b></span>"
                else:
                    items, avg = random.randint(5, 12), random.randint(25, 85)
                    total = items * avg
                    q = f"กระสอบข้าวสาร <b>{items} ใบ</b> มีน้ำหนัก <b>'เฉลี่ย'</b> ใบละ <b>{avg} กิโลกรัม</b><br>จงหาน้ำหนักรวมทั้งหมด?"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b><br>👉 ผลรวม = จำนวน × ค่าเฉลี่ย<br>👉 {items} × {avg} = <b>{total} กิโลกรัม</b><br><b>ตอบ: {total} กิโลกรัม</b></span>"

            elif actual_sub_t == "ความน่าจะเป็นเบื้องต้น (สุ่มหยิบของ)":
                num_colors = random.randint(3, 4)
                chosen_colors = random.sample(["สีแดง", "สีฟ้า", "สีเขียว", "สีเหลือง"], num_colors)
                color_counts = {c: random.randint(2, 6) for c in chosen_colors}
                total_marbles = sum(color_counts.values())
                target_color = random.choice(chosen_colors)
                target_count = color_counts[target_color]
                g = math.gcd(target_count, total_marbles)
                
                details = ", ".join([f"{k} {v} ลูก" for k, v in color_counts.items()])
                q = f"ในกล่องมีลูกแก้วดังนี้: <b>{details}</b><br>ถ้าสุ่มหยิบ 1 ลูก โอกาสที่จะได้ <b>ลูกแก้ว{target_color}</b> คิดเป็นเศษส่วนเท่าใด?"
                sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b><br>👉 ลูกแก้วทั้งหมด = {total_marbles} ลูก<br>👉 ลูกแก้ว{target_color} = {target_count} ลูก<br>👉 โอกาสคือ เศษ {target_count} ส่วน {total_marbles} (ทอนเป็นอย่างต่ำได้ <b>{target_count//g}/{total_marbles//g}</b>)<br><b>ตอบ: {target_count//g}/{total_marbles//g}</b></span>"

            elif actual_sub_t == "โจทย์ปัญหาพื้นที่และความยาวรอบรูป":
                is_square = random.choice([True, False])
                if is_square:
                    side = random.randint(12, 35)
                    area = side * side
                    perimeter = 4 * side
                    q = f"สนามหญ้ารูปสี่เหลี่ยมจัตุรัส มีพื้นที่ <b>{area:,} ตารางเมตร</b><br>ถ้าต้องการทำรั้วล้อมรอบ 1 รอบ จะต้องใช้รั้วยาวกี่เมตร?"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b><br>👉 พื้นที่ = ด้าน × ด้าน ➔ {side} × {side} = {area:,}<br>👉 ความยาวรอบรูป = 4 × {side} = <b>{perimeter:,} เมตร</b><br><b>ตอบ: {perimeter:,} เมตร</b></span>"
                else:
                    w, h = random.randint(8, 15), random.randint(16, 25)
                    area = w * h
                    rate = random.choice([250, 350, 450])
                    total_cost = area * rate
                    q = f"ห้องประชุมรูปสี่เหลี่ยมผืนผ้า กว้าง <b>{w} เมตร</b> ยาว <b>{h} เมตร</b><br>ช่างคิดค่าปูกระเบื้อง <b>ตารางเมตรละ {rate:,} บาท</b> จะต้องจ่ายเงินทั้งหมดกี่บาท?"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b><br>👉 พื้นที่ห้อง = {w} × {h} = {area:,} ตารางเมตร<br>👉 ค่าใช้จ่าย = {area:,} × {rate:,} = <b>{total_cost:,} บาท</b><br><b>ตอบ: {total_cost:,} บาท</b></span>"

            elif actual_sub_t == "การหาขนาดของมุมที่หายไป":
                a1 = random.randint(40, 75)
                a2 = random.randint(40, 75)
                ans = 180 - a1 - a2
                q = f"รูปสามเหลี่ยมมีมุมภายใน 3 มุม ถ้ารู้ขนาด 2 มุมคือ <b>{a1}°</b> และ <b>{a2}°</b><br>มุมที่เหลือมีขนาดกี่องศา?"
                sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b><br>👉 มุมภายในสามเหลี่ยมรวมกันได้ 180°<br>👉 มุมที่เหลือ = 180° - ({a1}° + {a2}°) = <b>{ans}°</b><br><b>ตอบ: {ans}°</b></span>"

            elif actual_sub_t == "เส้นขนานและมุมแย้ง":
                val = random.randint(40, 85)
                ans = val
                q = f"เส้นตรงสองเส้นขนานกัน มีเส้นตัดขวางทำให้เกิดมุมแย้ง<br>ถ้ามุมหนึ่งมีขนาด <b>{val}°</b> มุมแย้งของมุมนี้จะมีขนาดกี่องศา?"
                sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b><br>👉 มุมแย้งที่เกิดจากเส้นขนานจะมีขนาด <b>เท่ากันเสมอ</b><br>👉 ดังนั้น มุมแย้ง = <b>{ans}°</b><br><b>ตอบ: {ans}°</b></span>"

            elif actual_sub_t == "ปริมาตรและความจุทรงสี่เหลี่ยมมุมฉาก":
                w, l, h = random.randint(3, 10), random.randint(5, 15), random.randint(4, 12)
                vol = w * l * h
                q = f"กล่องทรงสี่เหลี่ยมมุมฉาก กว้าง <b>{w} ซม.</b> ยาว <b>{l} ซม.</b> และสูง <b>{h} ซม.</b><br>กล่องใบนี้มี<b>ปริมาตร</b>กี่ลูกบาศก์เซนติเมตร?"
                sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b><br>👉 ปริมาตร = กว้าง × ยาว × สูง<br>👉 {w} × {l} × {h} = <b>{vol:,} ลูกบาศก์เซนติเมตร</b><br><b>ตอบ: {vol:,} ลูกบาศก์เซนติเมตร</b></span>"

            elif actual_sub_t in ["การบวกเศษส่วน", "การลบเศษส่วน", "การคูณเศษส่วน", "การหารเศษส่วน"]:
                op_map = {"การบวกเศษส่วน": "+", "การลบเศษส่วน": "-", "การคูณเศษส่วน": "×", "การหารเศษส่วน": "÷"}
                op_sign = op_map[actual_sub_t]
                d1, d2 = random.randint(3, 12), random.randint(3, 12)
                while d1 == d2: d2 = random.randint(3, 12) 
                n1, n2 = random.randint(1, d1-1), random.randint(1, d2-1)
                if actual_sub_t in ["การลบเศษส่วน", "การหารเศษส่วน"]:
                    if n1*d2 <= n2*d1: n1, n2, d1, d2 = n2, n1, d2, d1
                        
                q = f"จงหาผลลัพธ์: <b>({n1}/{d1}) {op_sign} ({n2}/{d2}) = ?</b>"
                
                if actual_sub_t == "การบวกเศษส่วน":
                    lcm = (d1 * d2) // math.gcd(d1, d2)
                    new_n1, new_n2 = n1 * (lcm // d1), n2 * (lcm // d2)
                    res_n, res_d = new_n1 + new_n2, lcm
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b><br>👉 ทำส่วนให้เป็น ค.ร.น. คือ {lcm}<br>👉 ({new_n1}/{lcm}) + ({new_n2}/{lcm}) = <b>{res_n}/{res_d}</b></span>"
                elif actual_sub_t == "การลบเศษส่วน":
                    lcm = (d1 * d2) // math.gcd(d1, d2)
                    new_n1, new_n2 = n1 * (lcm // d1), n2 * (lcm // d2)
                    res_n, res_d = new_n1 - new_n2, lcm
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b><br>👉 ทำส่วนให้เป็น ค.ร.น. คือ {lcm}<br>👉 ({new_n1}/{lcm}) - ({new_n2}/{lcm}) = <b>{res_n}/{res_d}</b></span>"
                elif actual_sub_t == "การคูณเศษส่วน":
                    res_n, res_d = n1 * n2, d1 * d2
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b><br>👉 บนคูณบน ล่างคูณล่าง<br>👉 ({n1}×{n2}) / ({d1}×{d2}) = <b>{res_n}/{res_d}</b></span>"
                elif actual_sub_t == "การหารเศษส่วน":
                    res_n, res_d = n1 * d2, d1 * n2
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b><br>👉 เปลี่ยนหารเป็นคูณ กลับเศษเป็นส่วนตัวหลัง<br>👉 ({n1}/{d1}) × ({d2}/{n2}) = <b>{res_n}/{res_d}</b></span>"

            elif actual_sub_t == "การเขียนเศษส่วนในรูปร้อยละ":
                d = random.choice([2, 4, 5, 10, 20, 25, 50])
                n = random.randint(1, d-1)
                m = 100 // d
                ans = n * m
                q = f"จงเขียนเศษส่วน <b>{n}/{d}</b> ให้อยู่ในรูป <b>ร้อยละ (เปอร์เซ็นต์)</b>"
                sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b><br>👉 ทำส่วนให้เป็น 100 โดยคูณด้วย {m} ทั้งเศษและส่วน<br>👉 ({n}×{m}) / ({d}×{m}) = {ans}/100<br><b>ตอบ: ร้อยละ {ans} หรือ {ans}%</b></span>"

            elif actual_sub_t == "การแก้สมการ (คูณ/หาร)":
                var = random.choice(["x", "y", "a", "m"])
                scenario = random.choice(["mult", "div", "mult_add"])
                if scenario == "mult":
                    a, ans = random.randint(4, 15), random.randint(3, 12)
                    b = a * ans
                    q = f"จงแก้สมการเพื่อหาค่าของ <b>{var}</b> : <b>{a}{var} = {b}</b>"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b><br>👉 {var} = {b} ÷ {a} = <b>{ans}</b><br><b>ตอบ: {ans}</b></span>"
                elif scenario == "div":
                    a, ans = random.randint(3, 9), random.randint(5, 20)
                    c = a * ans
                    q = f"จงแก้สมการเพื่อหาค่าของ <b>{var}</b> : <b>{var}/{a} = {ans}</b>"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b><br>👉 {var} = {ans} × {a} = <b>{c}</b><br><b>ตอบ: {c}</b></span>"
                elif scenario == "mult_add":
                    a, ans, b = random.randint(2, 6), random.randint(3, 10), random.randint(1, 15)
                    c = (a * ans) + b
                    q = f"จงแก้สมการเพื่อหาค่าของ <b>{var}</b> : <b>{a}{var} + {b} = {c}</b>"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b><br>👉 {a}{var} = {c} - {b} = {c-b}<br>👉 {var} = {c-b} ÷ {a} = <b>{ans}</b><br><b>ตอบ: {ans}</b></span>"

            elif actual_sub_t == "โจทย์ปัญหา ห.ร.ม. และ ค.ร.น.":
                scenario = random.choice(["gcd", "lcm"])
                if scenario == "gcd":
                    g = random.choice([5, 6, 8, 10])
                    a, b, c = g * 3, g * 4, g * 5
                    q = f"มีผลไม้ 3 ชนิด จำนวน <b>{a} ผล, {b} ผล, {c} ผล</b> ต้องการแบ่งใส่ถุง ถุงละเท่าๆ กัน ให้ได้มากที่สุดโดยไม่เหลือเศษ<br>จะได้ถุงละกี่ผล?"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b><br>👉 หา ห.ร.ม. ของ {a}, {b}, {c}<br>👉 ห.ร.ม. คือ <b>{g}</b><br><b>ตอบ: {g} ผล</b></span>"
                else:
                    t1, t2, t3 = random.choice([(10, 15, 20), (12, 15, 20), (15, 20, 30)])
                    lcm_val = math.lcm(math.lcm(t1, t2), t3)
                    q = f"นาฬิกาปลุก 3 เรือน ปลุกทุกๆ <b>{t1} นาที, {t2} นาที, {t3} นาที</b><br>ถ้านาฬิกาปลุกพร้อมกันครั้งแรก อีกกี่นาทีจึงจะปลุกพร้อมกันอีกครั้ง?"
                    sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b><br>👉 หา ค.ร.น. ของ {t1}, {t2}, {t3}<br>👉 ค.ร.น. คือ <b>{lcm_val}</b><br><b>ตอบ: อีก {lcm_val} นาที</b></span>"

            elif actual_sub_t == "โจทย์ปัญหาคลาสสิก (สมการประยุกต์)":
                pigs, chickens = random.randint(5, 20), random.randint(10, 30)
                heads, legs = pigs + chickens, (pigs * 4) + (chickens * 2)
                q = f"ฟาร์มแห่งหนึ่งมี <b>หมู</b> และ <b>ไก่</b> รวมกัน <b>{heads} ตัว</b> ถ้านับขาสัตว์รวมกันได้ <b>{legs} ขา</b><br>ฟาร์มแห่งนี้มีหมูกี่ตัว?"
                sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b><br>👉 ให้หมู x ตัว, ไก่ ({heads}-x) ตัว<br>👉 4x + 2({heads}-x) = {legs}<br>👉 2x = {legs - heads*2}<br>👉 x = <b>{pigs}</b><br><b>ตอบ: หมู {pigs} ตัว</b></span>"

            elif actual_sub_t == "แบบรูปและอนุกรม (Number Patterns)":
                start_base = random.randint(1, 4)
                bases = [start_base + i for i in range(6)]
                seq = [b**2 for b in bases]
                ans = seq[-1]
                q = f"จากแบบรูป: <b>{', '.join(map(str, seq[:-1]))}, ...</b> จงหาจำนวนถัดไป?"
                sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b><br>👉 สังเกตว่าเป็นตัวเลขยกกำลังสอง (คูณตัวเอง)<br>👉 ตัวถัดไปคือ {bases[5]}² = <b>{ans}</b><br><b>ตอบ: {ans}</b></span>"

            elif actual_sub_t == "มาตราส่วนและทิศทาง":
                scale_km = random.choice([10, 20, 50])
                map_cm = random.randint(5, 15)
                ans = map_cm * scale_km
                q = f"แผนที่ใช้มาตราส่วน <b>1 ซม. : {scale_km} กม.</b> ถ้าวัดในแผนที่ได้ <b>{map_cm} เซนติเมตร</b> ระยะทางจริงคือกี่กิโลเมตร?"
                sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b><br>👉 {map_cm} × {scale_km} = <b>{ans} กิโลเมตร</b><br><b>ตอบ: {ans} กิโลเมตร</b></span>"

            elif actual_sub_t == "เรขาคณิตประยุกต์ (หาพื้นที่แรเงา)":
                W, H = random.randint(15, 30), random.randint(10, 20)
                border = random.randint(1, 3)
                area_out = W * H
                area_in = (W - 2*border) * (H - 2*border)
                ans = area_out - area_in
                q = f"กรอบรูปขนาด <b>{W}x{H} ซม.</b> มีขอบกว้าง <b>{border} ซม.</b> รอบด้าน<br>จงหาพื้นที่ของขอบกรอบรูปนี้?"
                sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b><br>👉 พื้นที่ขอบ = รูปใหญ่ - รูปเล็ก<br>👉 {area_out} - {area_in} = <b>{ans} ตร.ซม.</b><br><b>ตอบ: {ans} ตารางเซนติเมตร</b></span>"

            # ================= หมวด ป.4 (15 หัวข้อ) =================
            elif actual_sub_t == "การอ่านและการเขียนตัวเลข":
                num = random.randint(100000, 999999) if not is_challenge else random.randint(1000000, 99999999)
                thai_text = generate_thai_number_text(str(num))
                if random.choice([True, False]):
                    q = f"จงเขียนตัวเลข <b>{num:,}</b> เป็นตัวหนังสือภาษาไทย"
                    sol = f"<span style='color:#2c3e50;'><b>ตอบ: {thai_text}</b></span>"
                else:
                    q = f"จงเขียนคำอ่าน <b>\"{thai_text}\"</b> เป็นตัวเลขฮินดูอารบิก"
                    sol = f"<span style='color:#2c3e50;'><b>ตอบ: {num:,}</b></span>"

            elif actual_sub_t == "หลัก ค่าประจำหลัก และรูปกระจาย":
                num = random.randint(100000, 9999999)
                num_str = str(num)
                q = f"จงเขียนจำนวน <b>{num:,}</b> ให้อยู่ในรูปกระจาย"
                expanded = " + ".join([f"{int(d) * (10**(len(num_str)-i-1))}" for i, d in enumerate(num_str) if d != '0'])
                sol = f"<span style='color:#2c3e50;'><b>ตอบ: {expanded}</b></span>"

            elif actual_sub_t == "การเปรียบเทียบและเรียงลำดับ":
                base = random.randint(100000, 999999)
                nums = list(set([base + random.randint(-50000, 50000) for _ in range(4)]))
                while len(nums) < 4: nums.append(base + random.randint(-50000, 50000)); nums = list(set(nums))
                order = random.choice(["น้อยไปมาก", "มากไปน้อย"])
                nums_str = ", ".join([f"{n:,}" for n in nums])
                sorted_nums = sorted(nums) if order == "น้อยไปมาก" else sorted(nums, reverse=True)
                sorted_str = ", ".join([f"{n:,}" for n in sorted_nums])
                q = f"จงเรียงลำดับจำนวนจาก<b>{order}</b>: <b>{nums_str}</b>"
                sol = f"<span style='color:#2c3e50;'><b>ตอบ: {sorted_str}</b></span>"

            elif actual_sub_t == "สมการและตัวไม่ทราบค่าจากชีวิตประจำวัน":
                qty, price, total = random.randint(3, 8), random.randint(15, 40), 0
                extra = random.randint(20, 60)
                total = (price * qty) + extra
                q = f"ซื้อขนม <b>{qty} ห่อ</b> และน้ำ <b>{extra} บาท</b> จ่ายเงินไป <b>{total} บาท</b><br>ขนมราคาห่อละกี่บาท?"
                sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b><br>👉 ({qty} × ราคาขนม) + {extra} = {total}<br>👉 ราคาขนม = ({total} - {extra}) ÷ {qty} = <b>{price} บาท</b><br><b>ตอบ: {price} บาท</b></span>"

            elif actual_sub_t == "สมการเชิงตรรกะและตาชั่งปริศนา":
                val_a, val_b = random.randint(12, 25), random.randint(15, 40)
                w1 = val_a * 3
                w2 = (val_a * 2) + val_b
                q = f"ตาชั่ง 1: วงกลม 3 ชิ้น หนัก <b>{w1} กรัม</b><br>ตาชั่ง 2: วงกลม 2 ชิ้น + สี่เหลี่ยม 1 ชิ้น หนัก <b>{w2} กรัม</b><br>สี่เหลี่ยม 1 ชิ้น หนักกี่กรัม?"
                sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b><br>👉 วงกลม 1 ชิ้น = {w1} ÷ 3 = {val_a} กรัม<br>👉 สี่เหลี่ยม = {w2} - ({val_a} × 2) = <b>{val_b} กรัม</b><br><b>ตอบ: {val_b} กรัม</b></span>"

            elif actual_sub_t == "โจทย์ปัญหาสมการ: ตาชั่งผลไม้":
                val_m, val_l = random.randint(35, 80), random.randint(150, 300)
                w1 = val_m * 4
                w2 = (val_m * 2) + val_l
                q = f"เครื่องชั่ง 1: แอปเปิล 4 ผล หนัก <b>{w1} กรัม</b><br>เครื่องชั่ง 2: แอปเปิล 2 ผล + เมลอน 1 ผล หนัก <b>{w2} กรัม</b><br>เมลอน 1 ผล หนักกี่กรัม?"
                sol = f"<span style='color:#2c3e50;'><b>วิธีทำ:</b><br>👉 แอปเปิล 1 ผล = {w1} ÷ 4 = {val_m} กรัม<br>👉 เมลอน = {w2} - ({val_m} × 2) = <b>{val_l} กรัม</b><br><b>ตอบ: {val_l} กรัม</b></span>"

            elif actual_sub_t == "โจทย์ปัญหาสมการ: ความสัมพันธ์ของ 2 สิ่ง":
                val_A, val_B = random.randint(30, 80), random.randint(10, 20)
                sum_val = val_A + val_B
                diff_val = val_A - val_B
                q = f"สมุด 1 เล่ม กับ ปากกา 1 ด้าม ราคารวมกัน <b>{sum_val} บาท</b><br>ถ้าสมุดแพงกว่าปากกาอยู่ <b>{diff_val} บาท</b> สมุดราคากี่บาท?"
                sol = f"<span style='color:#2c3e50;'><b>วิธีทำ (สูตรลัด):</b><br>👉 ของที่แพงกว่า = (ผลรวม + ผลต่าง) ÷ 2<br>👉 ({sum_val} + {diff_val}) ÷ 2 = <b>{val_A} บาท</b><br><b>ตอบ: {val_A} บาท</b></span>"

            elif actual_sub_t == "ค่าประมาณเป็นจำนวนเต็มสิบ เต็มร้อย เต็มพัน":
                target = random.choice(["สิบ", "ร้อย", "พัน"])
                num = random.randint(1234, 99999)
                round_dict = {"สิบ": -1, "ร้อย": -2, "พัน": -3}
                ans = round(num, round_dict[target])
                q = f"จงหาค่าประมาณเป็น<b>จำนวนเต็ม{target}</b> ของ <b>{num:,}</b>"
                sol = f"<span style='color:#2c3e50;'><b>ตอบ: {ans:,}</b></span>"

            elif actual_sub_t == "การบวก (แบบตั้งหลัก)":
                a, b = random.randint(100000, 999999), random.randint(100000, 999999)
                q = f"จงหาผลบวกของ <b>{a:,} + {b:,}</b>"
                sol = f"<span style='color:#2c3e50;'><b>ตอบ: {a + b:,}</b></span>"

            elif actual_sub_t == "การลบ (แบบตั้งหลัก)":
                a = random.randint(100000, 999999)
                b = random.randint(50000, a - 1000)
                q = f"จงหาผลลบของ <b>{a:,} - {b:,}</b>"
                sol = f"<span style='color:#2c3e50;'><b>ตอบ: {a - b:,}</b></span>"

            elif actual_sub_t == "การคูณ (แบบตั้งหลัก)":
                a, b = random.randint(100, 9999), random.randint(12, 99)
                q = f"จงหาผลคูณของ <b>{a:,} × {b:,}</b>"
                sol = f"<span style='color:#2c3e50;'><b>ตอบ: {a * b:,}</b></span>"

            elif actual_sub_t == "การหารยาว":
                divisor = random.randint(2, 9)
                quotient = random.randint(1000, 9999)
                remainder = random.randint(0, divisor - 1)
                dividend = (divisor * quotient) + remainder
                q = f"จงหาผลหารของ <b>{dividend:,} ÷ {divisor}</b>"
                ans_txt = f"{quotient:,}" if remainder == 0 else f"{quotient:,} เศษ {remainder}"
                sol = f"<span style='color:#2c3e50;'><b>ตอบ: {ans_txt}</b></span>"

            elif actual_sub_t == "แปลงเศษเกินเป็นจำนวนคละ":
                den, whole = random.randint(3, 12), random.randint(2, 9)
                num_rem = random.randint(1, den - 1)
                num_total = (whole * den) + num_rem
                q = f"จงแปลงเศษเกิน <b>{num_total}/{den}</b> ให้เป็นจำนวนคละ"
                sol = f"<span style='color:#2c3e50;'><b>ตอบ: {whole} {num_rem}/{den}</b></span>"

            elif actual_sub_t == "การอ่านและการเขียนทศนิยม":
                whole, dec = random.randint(0, 99), random.randint(1, 99)
                num_str = f"{whole}.{dec:02d}"
                q = f"จงเขียนทศนิยม <b>{num_str}</b> เป็นคำอ่าน"
                sol = f"<span style='color:#2c3e50;'><b>ตอบ: (อ่านตัวเลขตามหลักภาษาไทย)</b></span>"

            elif actual_sub_t == "การบอกชนิดของมุม":
                angle = random.randint(10, 175)
                a_type = "มุมแหลม" if angle < 90 else "มุมฉาก" if angle == 90 else "มุมป้าน"
                q = f"มุมที่มีขนาด <b>{angle}°</b> คือมุมชนิดใด?"
                sol = f"<span style='color:#2c3e50;'><b>ตอบ: {a_type}</b></span>"

            elif actual_sub_t == "การวัดขนาดของมุม (ไม้โปรแทรกเตอร์)":
                base_deg, angle = random.choice([0, 10, 20]), random.randint(30, 120)
                q = f"แขนของมุมชี้ที่ <b>{base_deg}°</b> และ <b>{base_deg+angle}°</b> มุมนี้มีขนาดกี่องศา?"
                sol = f"<span style='color:#2c3e50;'><b>ตอบ: {angle} องศา</b></span>"

            elif actual_sub_t == "การสร้างมุมตามขนาดที่กำหนด":
                target_deg = random.choice([45, 60, 75, 120, 135, 150])
                q = f"จงสร้างมุมให้มีขนาด <b>{target_deg} องศา</b> พร้อมระบุชนิดของมุม"
                a_type = "มุมแหลม" if target_deg < 90 else "มุมฉาก" if target_deg == 90 else "มุมป้าน"
                sol = f"<span style='color:#2c3e50;'><b>ตอบ: วาดมุม {target_deg} องศา ({a_type})</b></span>"

            elif actual_sub_t == "โจทย์ปัญหาเรื่องมุมจากเข็มนาฬิกา":
                m1, m2 = random.sample(range(0, 60), 2)
                dist = abs(m1 - m2) if abs(m1 - m2) <= 30 else 60 - abs(m1 - m2)
                q = f"เข็มสั้นและเข็มยาวชี้ห่างกัน <b>{dist} ขีดนาที</b> มุมระหว่างเข็มกางกี่องศา?"
                sol = f"<span style='color:#2c3e50;'><b>ตอบ: {dist * 6} องศา</b></span>"

            elif actual_sub_t == "การหาความยาวรอบรูปสี่เหลี่ยมมุมฉาก":
                w, h = random.randint(4, 15), random.randint(16, 30)
                q = f"สี่เหลี่ยมผืนผ้า กว้าง <b>{w} ซม.</b> ยาว <b>{h} ซม.</b> มีความยาวรอบรูปกี่เซนติเมตร?"
                sol = f"<span style='color:#2c3e50;'><b>ตอบ: {2*(w+h)} เซนติเมตร</b></span>"

            elif actual_sub_t == "การหาพื้นที่รูปสี่เหลี่ยมมุมฉาก":
                w, h = random.randint(4, 15), random.randint(16, 30)
                q = f"สี่เหลี่ยมผืนผ้า กว้าง <b>{w} ซม.</b> ยาว <b>{h} ซม.</b> มีพื้นที่กี่ตารางเซนติเมตร?"
                sol = f"<span style='color:#2c3e50;'><b>ตอบ: {w*h} ตารางเซนติเมตร</b></span>"

            elif actual_sub_t == "การแก้สมการ (บวก/ลบ)":
                var = random.choice(["A", "x", "y"])
                a, ans = random.randint(100, 999), random.randint(1000, 9999)
                c = ans + a
                q = f"จงแก้สมการ: <b>{var} + {a} = {c}</b>"
                sol = f"<span style='color:#2c3e50;'><b>ตอบ: {var} = {ans}</b></span>"

            else:
                q = f"⚠️ [ระบบผิดพลาด] ไม่พบเงื่อนไขสำหรับหัวข้อ: <b>{actual_sub_t}</b>"
                sol = "Error"

            # ==================================================
            # ระบบเช็คโจทย์ซ้ำ
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
            html += f'{item["question"]}<div class="sol-text">{item["solution"]}</div>'
        else:
            html += f'{item["question"]}<div class="workspace">พื้นที่สำหรับแสดงวิธีทำ...</div><div class="ans-line">ตอบ: </div>'
        html += '</div>'
        
    if brand_name: 
        html += f'<div class="page-footer">&copy; 2026 {brand_name} | สงวนลิขสิทธิ์</div>'
        
    return html + "</body></html>"

# ==========================================
# 4. Streamlit UI
# ==========================================
st.sidebar.markdown("## ⚙️ พารามิเตอร์การสร้าง")

# 💡 แก้ไข: เหลือแค่ ป.4 และ ป.5
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

if st.sidebar.button("🚀 สั่งสร้างใบงานเดี๋ยวนี้", type="primary", use_container_width=True):
    with st.spinner("กำลังสร้าง..."):
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
    st.success(f"✅ ลิขสิทธิ์นี้เป็นของ บ้านทีเด็ด เท่านั้น ห้ามนำไปขาย หรือแจกจ่าย ก่อนได้รับอนุญาต จาก บ้านทีเด็ด")
    c1, c2 = st.columns(2)
    with c1:
        st.download_button("📄 โหลดเฉพาะโจทย์", data=st.session_state['worksheet_html'], file_name=f"{st.session_state['filename_base']}_Worksheet.html", mime="text/html", use_container_width=True)
        st.download_button("🔑 โหลดเฉพาะเฉลย", data=st.session_state['answerkey_html'], file_name=f"{st.session_state['filename_base']}_AnswerKey.html", mime="text/html", use_container_width=True)
    with c2:
        st.download_button("📚 โหลดรวมเล่ม E-Book", data=st.session_state['ebook_html'], file_name=f"{st.session_state['filename_base']}_Full_EBook.html", mime="text/html", use_container_width=True)
        st.download_button("🗂️ โหลดแพ็กเกจ (.zip)", data=st.session_state['zip_data'], file_name=f"{st.session_state['filename_base']}.zip", mime="application/zip", use_container_width=True)
    st.markdown("---")
    components.html(st.session_state['ebook_html'], height=800, scrolling=True)
