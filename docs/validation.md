# Lab 03 — Browser Acceptance (A1–A5)

**วิธีตรวจ:** OpenCode Browser (เครื่องมือ `browser.*` ใน OpenCode Desktop)
**วันที่ตรวจ:** 2026-11-17
**เครื่อง:** Windows, Flask dev server ที่ `http://127.0.0.1:5000/`

## ทำไมเปลี่ยนเครื่องมือจาก Playwright MCP

ใบงานอนุญาตให้ใช้ browser tool อื่นได้ ถ้าระบุเหตุผลและวิธีที่ใช้แทน ในเซสชันนี้ใช้
**OpenCode Browser** แทน **Playwright MCP** เพราะ:

1. Playwright MCP ต้องเพิ่ม MCP server ใน `opencode.json` แล้ว **ปิด–เปิดแอปใหม่** เพื่อโหลด config
   ระหว่างนั้น dev server และ context ของงาน Lab 03 จะหายไป
2. OpenCode Browser ทำงานได้ทันทีในเซสชันเดิม และให้ความสามารถที่ต้องใช้ครบ:
   เปิดหน้า, อ่าน DOM, กรอกฟอร์ม, กด submit, อ่าน network request body, screenshot

**MCP (Model Context Protocol)** คือ protocol มาตรฐานที่ให้ agent เรียกเครื่องมือภายนอก
เช่น `playwright` MCP server ที่ห่อ Playwright API ไว้ ส่วน OpenCode Browser เป็นเครื่องมือ
browser ที่ฝังมากับ OpenCode (ไม่ได้ผ่าน MCP) แต่ขับ Chromium ตัวเดียวกัน จึงตรวจผลได้เท่ากัน
**ทุกวิธีให้คะแนนเท่ากัน** สิ่งที่ต้องมีคือระบุวิธีที่ใช้จริงและแนบหลักฐาน

## เกณฑ์ตัดสิน

ใช้ค่าร่วมทุกกรณี: `VCC = 12 V`, `RC = 2.2 kΩ`, `β = 100`, `VBE = 0.70 V`
เกณฑ์: `IC` คลาดเคลื่อนไม่เกิน ±0.01 mA และ `VCE` ไม่เกิน ±0.02 V เทียบกับค่าอ้างอิงที่คำนวณมือ (ก่อนปัดเศษ)

## ค่าอ้างอิงอิสระ (คำนวณมือจากสมการใบงาน ไม่ใช่ค่าจากโปรแกรม)

### A2 · Fixed Bias — RB = 1 MΩ, RC = 2.2 kΩ, β = 100, VBE = 0.70 V, VCC = 12 V

```
IB  = (VCC − VBE) / RB
    = (12 − 0.70) V / 1 000 000 Ω
    = 11.3000 µA

IC  = β · IB = 100 × 11.3000 µA        = 1.1300 mA
IE  = (β+1) · IB = 101 × 11.3000 µA    = 1.1413 mA
VE  = 0 V                              ( fixed bias ไม่มี RE )
VB  = VE + VBE = 0 + 0.70              = 0.7000 V
VC  = VCC − IC · RC = 12 − 1.1300 mA × 2.2 kΩ
    = 12 − 2.4860                      = 9.5140 V
VCE = VC − VE = 9.5140 − 0              = 9.5140 V
```

### A3 · Emitter Bias — RB = 1 MΩ, RE = 1 kΩ, RC = 2.2 kΩ, β = 100, VBE = 0.70 V, VCC = 12 V

```
IB  = (VCC − VBE) / [RB + (β+1)·RE]
    = 11.3 V / [1 000 000 + 101 × 1 000] Ω
    = 11.3 / 1 101 000 A                = 10.2634 µA

IC  = 100 × 10.2634 µA                 = 1.0263 mA
IE  = 101 × 10.2634 µA                 = 1.0366 mA
VE  = IE · RE = 1.0366 mA × 1 kΩ       = 1.0366 V
VB  = VE + VBE = 1.0366 + 0.70         = 1.7366 V
VC  = 12 − 1.0263 mA × 2.2 kΩ
    = 12 − 2.2579                      = 9.7421 V
VCE = 9.7421 − 1.0366                  = 8.7054 V
```

### A4 · Emitter Bias เปลี่ยนค่าเดียว — RE = 2 kΩ (ค่าอื่นเหมือน A3)

```
IB  = 11.3 / [1 000 000 + 101 × 2 000] = 11.3 / 1 202 000 A = 9.4010 µA
IC  = 100 × 9.4010 µA                  = 0.9401 mA
IE  = 101 × 9.4010 µA                  = 0.9495 mA
VE  = 0.9495 mA × 2 kΩ                 = 1.8990 V
VB  = 1.8990 + 0.70                    = 2.5990 V
VC  = 12 − 0.9401 mA × 2.2 kΩ          = 9.9318 V
VCE = 9.9318 − 1.8990                  = 8.0328 V
```

### A1 · Divider Bias (โหมดเดิม, ต้องไม่เสียจาก Lab 02) — R1 = 100 kΩ, R2 = 22 kΩ, RE = 1 kΩ

```
RTH = R1·R2/(R1+R2) = 100 k × 22 k / 122 k = 18.0328 kΩ
VTH = VCC·R2/(R1+R2) = 12 × 22 / 122        = 2.1639 V
IB  = (VTH − VBE) / [RTH + (β+1)·RE]
    = (2.1639 − 0.70) / (18 032.8 + 101 000) = 12.2983 µA
IC  = 1.2298 mA · IE = 1.2421 mA · VE = 1.2421 V
VB  = 1.9421 V · VC = 9.2944 V · VCE = 8.0523 V
```

**ผลตรวจไขว้:** โปรแกรมมีตัวแก้สมการอิสระอีกชุด (`bjt/independent.py` ใช้วิธี bisection บนสมการ KCL
ซึ่งต่างจากสูตร closed-form ใน `bjt/engineering.py`) ทั้งสามโหมดขึ้น `Matches within tolerance`

## ตาราง A1–A5 (ผลที่เห็นจริงบนหน้าเว็บ)

| กรณี | วิธีตรวจ | อินพุตที่กรอก | คาดหมายก่อนรัน (หน่วย SI) | ผลที่เห็นจริง (หน่วยตามที่หน้าเว็บแสดง) | สถานะ | หลักฐาน |
|---|---|---|---|---|---|---|
| A1 · โหมดเดิม | OpenCode Browser | Divider · R1 = 100 kΩ, R2 = 22 kΩ, RE = 1 kΩ (ค่าเริ่มต้น) | IC = 1.2298 mA · VCE = 8.0523 V | VB 1.94 V, VE 1.24 V, VC 9.29 V, **VCE 8.05 V**, IB 12.3 µA, **IC 1.23 mA**, IE 1.24 mA · ACTIVE | PASS | ข้อความที่คัดจากหน้า (ดูหัวข้อ "ทวนสอบซ้ำ") + ค่าตรงกับ Lab 02 เดิม |
| A2 · Fixed | OpenCode Browser | Fixed · RB = 1 MΩ (ไม่กรอก RE/R1/R2) | IC = 1.1300 mA · VCE = 9.5140 V | VB 0.70 V, VE 0.00 V, VC 9.51 V, **VCE 9.51 V**, IB 11.3 µA, **IC 1.13 mA**, IE 1.14 mA · ACTIVE | PASS | [ภาพหน้าจอ A2](evidence/lab03-a2-fixed.jpeg) |
| A3 · Emitter | OpenCode Browser | Emitter · RB = 1 MΩ, RE = 1 kΩ | IC = 1.0263 mA · VCE = 8.7054 V | VB 1.74 V, VE 1.04 V, VC 9.74 V, **VCE 8.71 V**, IB 10.26 µA, **IC 1.03 mA**, IE 1.04 mA · ACTIVE | PASS | [ภาพหน้าจอ A3](evidence/lab03-a3-emitter.jpeg) |
| A4 · เปลี่ยนค่าเดียว | OpenCode Browser | Emitter · เหมือน A3 แต่ RE = 2 kΩ | ทำนาย: RE ใหญ่ขึ้น → IB ลด → IC ลด · IC = 0.9401 mA · VCE = 8.0328 V | VB 2.60 V, VE 1.90 V, VC 9.93 V, **VCE 8.03 V**, IB 9.4 µA, **IC 940.1 µA (= 0.9401 mA)**, IE 949.5 µA · ACTIVE | PASS | [ภาพหน้าจอ A4](evidence/lab03-a4-emitter-re2.jpeg) + ค่าที่ส่งจากฟอร์ม (หัวข้อ "ตรวจเส้นทางของค่า RE") |
| A5 · อินพุตผิด | OpenCode Browser | Fixed · RB = 0 | ต้องขึ้นข้อความให้แก้ RB, เว็บไม่ล่ม, ไม่แสดงผลเดิม | ขึ้น `must be greater than zero` ใต้ช่อง RB, ค่า 0 ยังคงอยู่, ไม่มีตารางผลลัพธ์, หน้าโหมด Fixed ยังใช้งานได้ | PASS | ข้อความบนหน้า |

## ตรวจเส้นทางของค่า RE (ตอบคำถามปิด Lab)

กรณี A4: เปลี่ยนช่อง RE จาก `1.0` เป็น `2` โดยหน่วยเป็น kΩ แล้วกด Calculate
เก็บหลักฐาน 3 ชั้นจากเครื่องจริง:

**1. ค่าที่ส่งออกจากฟอร์ม** — อ่าน request body ของ `POST /calculate` จาก network log ของเบราว์เซอร์:

```
mode=emitter&vcc=12.0&vcc_unit=V&rb=1&rb_unit=M%CE%A9&re=2&re_unit=k%CE%A9
&rc=2.2&rc_unit=k%CE%A9&beta=100&vbe=0.70&vbe_unit=V
```

แกะ percent-encoding แล้วได้ `re=2`, `re_unit=kΩ` (ฟอร์มส่งค่าดิบพร้อมหน่วยที่เลือก ไม่ได้แปลงเอง)

**2. ค่าหลังแปลงหน่วย** — เรียกฟังก์ชันของ route ตรง ๆ ด้วย payload เดียวกัน:

```
typed in form : {'vcc': '12.0', 'rb': '1', 're': '2', 'rc': '2.2', 'beta': '100', 'vbe': '0.70'}
units chosen  : {'vcc': 'V', 'rb': 'MΩ', 're': 'kΩ', 'rc': 'kΩ', 'beta': '–', 'vbe': 'V'}
after scaling : {'vcc': '12.0', 'rb': '1000000.0', 're': '2000.0', 'rc': '2200.0', 'beta': '100.0', 'vbe': '0.7'}
```

**3. ค่าที่เข้าไปในฟังก์ชัน** — ครอบ `analyze_emitter` แล้วพิมพ์ค่าที่รับจริง:

```
function args : {'vcc': 12.0, 'rb': 1000000.0, 're': 2000.0, 'rc': 2200.0, 'beta': 100.0, 'vbe': 0.7}
  >> analyze_emitter received re = 2000.0 ohm
RE=2 kohm     IC = 0.9401 mA, VCE = 8.0328 V
RE=1 kohm     IC = 1.0263 mA, VCE = 8.7054 V
```

**ขั้นตอนตรวจซ้ำเมื่อผลไม่เปลี่ยนทั้งที่คำนวณมือถูก**

1. เปิด DevTools → Network (หรือใช้ network log ของ browser tool) ดู `POST /calculate`
   ต้องเห็น `re=2&re_unit=kΩ` — ถ้าไม่เห็น แปลว่าฟอร์มช่องนั้นไม่ถูกส่ง (name ผิด/ค่าถูกเขียนทับ)
2. ตรวจ `_to_base_units` (`bjt/routes.py:97`) ว่าคูณตัวคูณถูก: kΩ → ×1000 → `2000.0`
3. ตรวจว่า route ส่ง `re` เข้า `analyze_mode` (`bjt/routes.py:187`) และ dispatcher
   (`bjt/engineering.py:239`) เรียก `analyze_emitter` ไม่ใช่ฟังก์ชันของโหมดอื่น
4. ตรวจว่า `analyze_emitter` (`bjt/engineering.py:218`) ใช้ `re` ในสูตร
   `IB = (VCC − VBE) / (RB + (β+1)·RE)` จริง ไม่ได้ใช้ค่าคงที่หรือตัวแปรอื่น
5. เทียบผลที่ควรได้จากการคำนวณมือ (A3 กับ A4 ต้องต่างกัน) — ถ้าตัวเลขยังเท่าเดิม แปลว่าค่า
   ไม่ได้ถูกใช้ หรือหน้าเว็บแสดงผลจาก state เก่า (cache/ผลลัพธ์เดิมค้าง)

## ทวนสอบซ้ำ (re-check)

รันซ้ำด้วย OpenCode Browser เมื่อ 2026-11-17 หลังแก้เอกสารครั้งสุดท้าย เพื่อยืนยันว่าผลไม่ใช่ของเก่า:

| ขั้น | การกระทำ | ผลที่เห็น |
|---|---|---|
| 1 | เปิด `http://127.0.0.1:5000/?mode=divider` | ฟอร์ม Divider พร้อมค่าเริ่มต้น R1 = 100 kΩ, R2 = 22 kΩ |
| 2 | กด **Calculate DC Bias** | `DC Bias Results — Voltage Divider Bias` |
| 3 | อ่านค่า | VB 1.94 V · VE 1.24 V · VC 9.29 V · VCE 8.05 V · IB 12.3 µA · IC 1.23 mA · IE 1.24 mA |
| 4 | อ่านสถานะ | `Active region approximation OK` / `ACTIVE`, `VCE = 8.05 V > 0.2 V` |
| 5 | อ่านผลตรวจไขว้ | `Closed-form vs Independent — Matches within tolerance` |
| 6 | เทียบกับตาราง A1 | ตรงกับค่าคาดหมายภายในเกณฑ์ (IC ±0.01 mA, VCE ±0.02 V) |

นักศึกษาสามารถทำขั้นตอน 1–6 ซ้ำเองได้ใน 2 นาที (ไม่ต้องแก้โค้ด) — ถ้าค่าไม่ตรงให้จดค่าที่เห็น
แล้วเทียบกับหัวข้อ "ตรวจเส้นทางของค่า RE" ด้านบน

## ตรวจเพิ่มเติม

| สิ่งที่ตรวจ | ผล |
|---|---|
| โหมดที่ไม่รู้จัก (`/calculate` ด้วย `mode=bogus`) | แสดง `Unknown bias mode: bogus (showing Voltage Divider Bias)` ไม่คำนวณและไม่แสดงผลลัพธ์ |
| หน่วยที่ไม่รู้จัก (`r1_unit=banana`) | แสดง `invalid unit` และไม่แสดงผล (เดิมเงียบ ๆ ใช้ตัวคูณ 1.0) |
| ผลตรวจไขว้ (Closed-form vs Independent) | ทั้งสามโหมดขึ้น `Matches within tolerance` |
| ฟอร์มโหมด Fixed | ไม่มีช่อง R1/R2/RE และไม่บังคับกรอก |
| ฟอร์มโหมด Emitter | มี RB, RE, RC และใช้ค่า RE จริง (A3 → A4 เปลี่ยนผล) |
| รันเทสต์เดิม | `python -m unittest discover -s tests` → 20 tests OK (ไม่ได้เพิ่มไฟล์ unittest ใหม่) |

## หมายเหตุ

- โปรแกรมแสดง V เป็นทศนิยม 2 ตำแหน่ง และกระแสเลือกหน่วยอัตโนมัติ (A/mA/µA) จึงเทียบกับค่าอ้างอิงที่ยังไม่ปัดเศษตามเกณฑ์ด้านบน
- ตารางนี้กรอกจากผลที่เห็นบนหน้าเว็บจริง ไม่ได้อ่านจากซอร์สโค้ดหรือเรียก HTTP ตรง (ยกเว้นหัวข้อ
  "ตรวจเส้นทางของค่า RE" ที่เจตนาตรวจสามชั้น: ค่าจากฟอร์ม → ค่าหลังแปลงหน่วย → argument ของฟังก์ชัน)
