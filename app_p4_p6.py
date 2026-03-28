elif actual_sub_t == "การบวกเศษส่วน":
                import math
                prob_style = random.choice([1, 2, 3])
                
                def draw_frac(n, d):
                    return f"<span style='display:inline-flex; flex-direction:column; vertical-align:middle; text-align:center; margin:0 4px; font-weight:bold; font-size:18px;'><span style='border-bottom:2px solid #2c3e50; padding:0 3px;'>{n}</span><span style='padding:0 3px;'>{d}</span></span>"
                
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
                        svg += f'<path d="M 40 40 L {x1} {y1} A 38 38 0 {la} 1 {x2} {y2} Z" fill="{fill}" stroke="#2c3e50" stroke-width="1.5"/>'
                    svg += '</svg>'
                    return svg

                def draw_svg_rect(n, d, color="#9b59b6"):
                    svg = f'<svg width="120" height="40" viewBox="0 0 120 40">'
                    w = 120 / d
                    for i in range(d):
                        fill = color if i < n else "#ecf0f1"
                        svg += f'<rect x="{i*w}" y="0" width="{w}" height="40" fill="{fill}" stroke="#2c3e50" stroke-width="1.5"/>'
                    svg += '</svg>'
                    return svg

                if prob_style == 1:
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
                import math
                prob_style = random.choice([1, 2, 3])
                
                def draw_frac(n, d):
                    return f"<span style='display:inline-flex; flex-direction:column; vertical-align:middle; text-align:center; margin:0 4px; font-weight:bold; font-size:18px;'><span style='border-bottom:2px solid #2c3e50; padding:0 3px;'>{n}</span><span style='padding:0 3px;'>{d}</span></span>"
                
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

                def draw_svg_rect(n, d, color="#f39c12"):
                    svg = f'<svg width="120" height="40" viewBox="0 0 120 40">'
                    w = 120 / d
                    for i in range(d):
                        fill = color if i < n else "#ecf0f1"
                        svg += f'<rect x="{i*w}" y="0" width="{w}" height="40" fill="{fill}" stroke="#2c3e50" stroke-width="1.5"/>'
                    svg += '</svg>'
                    return svg

                if prob_style == 1:
                    d = random.choice([4, 6, 8, 10, 12])
                    n1 = random.randint(2, d-1)
                    n2 = random.randint(1, n1-1) 
                    
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
                    d1 = random.choice([2, 3, 4])
                    n1 = random.randint(1, d1-1)
                    m = random.choice([2, 3, 4])
                    d2 = d1 * m
                    
                    n1_new = n1 * m 
                    n2 = random.randint(1, n1_new - 1) 
                    
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
                    d1 = random.choice([3, 4, 5])
                    n1 = random.randint(1, d1-1)
                    m = random.choice([2, 3, 4])
                    d2 = d1 * m
                    n1_new = n1 * m
                    n2 = random.randint(1, n1_new - 1) 
                    
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
                import math
                prob_style = random.choice([1, 2, 3])
                
                def draw_frac(n, d):
                    return f"<span style='display:inline-flex; flex-direction:column; vertical-align:middle; text-align:center; margin:0 4px; font-weight:bold; font-size:18px;'><span style='border-bottom:2px solid #2c3e50; padding:0 3px;'>{n}</span><span style='padding:0 3px;'>{d}</span></span>"
                
                def draw_svg_grid(n1, d1, n2, d2):
                    w, h = 120, 120
                    cw, ch = w/d1, h/d2
                    svg = f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
                    for row in range(d2):
                        for col in range(d1):
                            if col < n1 and row < n2:
                                fill = "#2ecc71" 
                            elif col < n1:
                                fill = "#a9dfbf" 
                            elif row < n2:
                                fill = "#f9e79f" 
                            else:
                                fill = "#ecf0f1" 
                            svg += f'<rect x="{col*cw}" y="{row*ch}" width="{cw}" height="{ch}" fill="{fill}" stroke="#2c3e50" stroke-width="1.5"/>'
                    svg += '</svg>'
                    return svg

                if prob_style == 1:
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
                import math
                prob_style = random.choice([1, 2, 3])
                
                def draw_frac(n, d):
                    return f"<span style='display:inline-flex; flex-direction:column; vertical-align:middle; text-align:center; margin:0 4px; font-weight:bold; font-size:18px;'><span style='border-bottom:2px solid #2c3e50; padding:0 3px;'>{n}</span><span style='padding:0 3px;'>{d}</span></span>"
                
                def draw_svg_div_rect(n, d, m):
                    w, h = 120, 120
                    cw, ch = w/d, h/m
                    svg = f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
                    for row in range(m):
                        for col in range(d):
                            if col < n and row == 0:
                                fill = "#2ecc71" 
                            elif col < n:
                                fill = "#a9dfbf" 
                            else:
                                fill = "#ecf0f1" 
                            svg += f'<rect x="{col*cw}" y="{row*ch}" width="{cw}" height="{ch}" fill="{fill}" stroke="#2c3e50" stroke-width="1.5"/>'
                    svg += '</svg>'
                    return svg

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
                    d1 = random.choice([3, 4, 5])
                    n1 = random.randint(1, d1-1)
                    m = random.choice([2, 3, 4]) 
                    
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
                    v1 = round(random.uniform(5.1, 25.9), 1)   
                    v2 = round(random.uniform(1.11, 9.99), 2)  
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
                    <b>ตอบ: คุณแม่ต้อง
else:
                    # แบบที่ 3: ป้ายราคา (ราคา x จำนวนชิ้น) [โจทย์การบวกทศนิยมที่ค้างอยู่]
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
