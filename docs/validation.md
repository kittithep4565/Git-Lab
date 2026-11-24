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

---

# Lab 04 — BJT Amplifier Simulator v1 (B1–B8)

**วันที่ตรวจ:** 2026-11-24
**วิธีตรวจที่ใช้จริง:** **OpenCode Browser** (`browser.*`: navigate → snapshot → fill →
click → read values → evaluate DOM → screenshot) บน Flask dev server `http://127.0.0.1:5000/`

**Playwright MCP: NOT RUN** — เหตุผล: MCP server ของ Playwright ไม่ได้ถูก expose ในเซสชันนี้
(พยายามโหลด skill/เครื่องมือแล้วไม่พบ) และการเพิ่มเข้า `opencode.json` ต้องปิด–เปิดแอปใหม่
ซึ่งจะทำให้ dev server และหลักฐาน Lab 03 หายไป ใบงานอนุญาตให้ระบุเหตุผลและใช้ browser tool อื่น
ได้ (หัวข้อ 09) จึงใช้ OpenCode Browser ซึ่งขับ Chromium ตัวเดียวกัน ทุกค่าในตารางด้านล่าง
อ่านจากหน้าเว็บที่รันจริง **ไม่ใช่ค่าจากซอร์สโค้ดหรือ mock**

## สภาพแวดล้อมของการรันจริง

| รายการ | ค่าที่สังเกต |
|---|---|
| Simulation engine | `ngspice 47` — `C:\Users\B6827441\ngspice-47\Spice64\bin\ngspice.exe` |
| วิธีตรวจเวอร์ชัน | `ngspice -v` / `--version` ไม่พิมพ์ stdout ใน PowerShell จึงใช้ path fallback ใน `find_ngspice()`; ข้อความบนหน้าเป็น `ngspice 47` |
| BJT model | `QNPN` · `.model QNPN NPN(IS=1e-14 BF=100 VAF=100 RB=10 RC=1)` |
| Model source | `generic teaching model (no starter file found)` — ไม่พบ Starter Kit ของอาจารย์ในรีโป จึงไม่แอบอ้างว่าเป็นโมเดลที่อาจารย์ตรวจแล้ว |
| เรียก engine | `subprocess.run([exe, "-b", "-o", "run.log", "circuit.cir"], timeout=25, cwd=run_dir)` ไม่ใช้ `shell=True` |
| สถานะบนหน้า | `ngspice ready` (ก่อนรัน) · `status: success` หลังได้ `.print` ใช้ได้จริง · `status: error` เมื่อ fail |
| หลักฐานรัน | isolated `run_dir` ต่อการกด Run ทุกครั้ง; แสดง netlist + `run.log` ใน `<details>`; เก็บถาวรได้ด้วย `LAB04_KEEP_RUNS=1` |
| Fixture | `VCC 12 V`, `R1 100 kΩ`, `R2 22 kΩ`, `RC 2.2 kΩ`, `RE 1 kΩ`, `RL 10 kΩ`, `Cin=Cout=10 µF`, `Vin 10 mV peak / 1 kHz`, ไม่มี bypass capacitor |

## ตาราง B1–B8 (ผลที่เห็นจริงบนหน้าเว็บ)

| Case | การกระทำจริงใน Browser | ผลที่สังเกต / ค่าจริง | วิธีเทียบกับข้อมูลจริง | หลักฐาน | สถานะ |
|---|---|---|---|---|---|
| **B1 · Regression** | เปิด `/` แล้วกด **Calculate DC Bias** ในโหมด Fixed, Emitter, Divider | Fixed `VB 0.70 V, VE 0.00 V, VC 9.51 V, VCE 9.51 V, IB 11.3 µA, IC 1.13 mA, IE 1.14 mA` · Emitter `VB 1.74 V, VE 1.04 V, VC 9.74 V, VCE 8.71 V, IB 10.26 µA, IC 1.03 mA, IE 1.04 mA` · Divider `VB 1.94 V, VE 1.24 V, VC 9.29 V, VCE 8.05 V, IB 12.3 µA, IC 1.23 mA, IE 1.24 mA`; ทุกอัน `ACTIVE` และ `Matches within tolerance` | ตรงกับตาราง A1–A3 และค่าคำนวณมือด้านบน (IC ±0.01 mA, VCE ±0.02 V) | [ภาพ B1](evidence/lab04-b1-regression.png) | **PASS** |
| **B2 · DC SPICE** | เลือก `DC · .op` → **Run Simulation** ด้วย fixture ด้านบน | `status: success`, `ngspice 47`, `DC · .op`, model `QNPN`; `VB 1.95 V · VE 1.29 V · VC 9.19 V · VCE 7.90 V · IC 1.28 mA`; ตาราง analytical เทียบ `VB 1.942, VE 1.242, VC 9.294, VCE 8.052, IC 1.23 mA` | netlist มี `.op` + `.print op v(base) v(emitter) v(collector) v(in) v(out)`; log มีบรรทัด `0  1.949e+00  1.289e+00  9.190e+00 ...`; `IC = (12 − 9.190 V)/2.2 kΩ = 1.28 mA` ตรงตามที่หน้าแสดง และหน้าระบุชัดว่า derive ไม่ใช่ print device current | [ภาพ B2](evidence/lab04-b2-dc-spice.png) + netlist/log ในข้อถัดไป | **PASS** |
| **B3 · Change RE** | เปลี่ยน **RE** ในฟอร์ม simulator `1 → 2 kΩ` แล้วรัน DC, แล้วรัน AC ที่ RE เดิม/RE=2 kΩ | DC: `VB 1.95→2.05 V`, `VE 1.29→1.40 V`, `VC 9.19→10.47 V`, `VCE 7.90→9.06 V`, `IC 1.28 mA→695.83 µA`; AC peak gain `4.86 dB (1.75×) → −1.14 dB (0.88×)`; circuit recap เปลี่ยนเป็น `RE 2 kΩ` | netlist เปลี่ยน `RE emitter 0 1000 → RE emitter 0 2000`; log `.op` เปลี่ยนเป็น `2.048203e+00  1.404491e+00  1.046918e+01` — ไม่ใช่ค่าค้าง | [ภาพ DC](evidence/lab04-b3-change-re.png) · [ภาพ AC gain ที่ RE=2 kΩ](evidence/lab04-b3-ac-gain-re2.png) | **PASS** |
| **B4 · AC** | เลือก `AC · .ac` → **Run Simulation** | กราฟ 2 อัน: `Frequency (Hz, log scale) versus Gain (dB)` และ `Frequency (Hz, log scale) versus Phase (°)`; axis `1, 39.8, 1.58e+03, 6.31e+04, 2.51e+06, 1.00e+08`; ข้อความ `Vin reference: source node 'in' before Cin · peak gain 4.86 dB (1.75×) · not determined in sweep range (-3 dB point not bracketed)` | netlist `.ac dec 50 1 100000000` และ `.print ac vdb(in) vp(in) vdb(out) vp(out)`; log excerpt มี `Index frequency vdb(out) vp(out)` และแถว `345  7.943282e+06  4.858972e+00  -3.14159e+00` (gain ≈ 4.86 dB, phase ≈ −180° ที่ความถี่สูง) ตรงกับ peak gain ที่หน้าแสดง | [ภาพ B4](evidence/lab04-b4-ac.png) | **PASS** |
| **B5 · Transient** | เลือก `Transient · .tran` → **Run Simulation** ที่ `10 mV peak, 1 kHz` | `508 samples · Vin pp 0.020 V · Vout pp 0.035 V · inverted (negative correlation)`; axis `Time (ms) 0…5`; legend `Vin`, `Vout`; กราฟ `Time (ms) versus Voltage (V)` | netlist `VIN in 0 DC 0 AC 1 SIN(0 0.01 1000)` + `.tran 1e-05 0.005` + `.print tran v(in) v(out)`; log แถว `464  4.572800e-03  -4.41631e-03  7.779958e-03` → `v(in)` ติดลบขณะ `v(out)` บวก = inversion จริง ไม่ใช่ข้อความ hard-code | [ภาพ B5](evidence/lab04-b5-transient.png) | **PASS** |
| **B6 · Change Source** | เปลี่ยน `Vamp 10→20 mV` และ `fsrc 1→2 kHz` แล้วรัน `.tran` อีกครั้ง | `508 samples · Vin pp 0.040 V · Vout pp 0.070 V · inverted`; axis เปลี่ยนเป็น `0…2.5 ms`; circuit recap `AMP 20 mV`, `FREQ 2 kHz` | netlist เปลี่ยนเป็น `SIN(0 0.02 2000)`; pp ของ Vin เพิ่มเป็นสองเท่า (0.020 → 0.040 V) ตาม amplitude ที่กรอก และช่วงเวลาแสดงผลเหลือครึ่ง (5 → 2.5 ms) ตาม frequency — ไม่มีการเขียน special case | [ภาพ B6](evidence/lab04-b6-change-source.png) | **PASS** |
| **B7 · Invalid / Fail** | ตั้ง `RE = 0` แล้วกด Run Simulation | ใต้ช่อง RE ขึ้น `must be greater than zero`; output ขึ้น `status: error` + `check the highlighted input field(s)`; **ไม่มี** `status: success` และ **ไม่มี** `<polyline>` (0 กราฟ); ค่า `0` ยังอยู่ในช่อง | ตรวจ DOM หลัง submit: `hasSuccess: false`, `polylines: 0`; route ไม่เรียก ngspice เพราะ validation กันก่อน (หน่วย/positivity/range) | [ภาพ B7](evidence/lab04-b7-invalid.png) + `tests/test_lab4.py::test_invalid_re_shows_error_without_success_or_plot` | **PASS** |
| **B8 · UI** | เปิด `/` ที่ viewport `1280×800` และ `390×844` แล้วเทียบก่อน/หลัง polish | ฟอร์ม simulator เห็นค่าเริ่มต้นครบ (`VCC 12.0`, `R1 100`, `RE 1.0`, `Vamp 10`, `fsrc 1`, `β 100`, `VBE 0.70`) หลังแก้บั๊ก `sim_form.values`; ปุ่ม/แท็บ/ตาราง/กราฟอ่านได้ทั้งสองขนาด ไม่มี horizontal overflow ที่ 390px; screenshot เก็บทั้ง 2 ขนาด | ใช้ `impeccable shot` บันทึก full-page จริง แล้วเทียบ [ก่อน](evidence/lab04-before/1280x800-full.png) / [หลัง](evidence/lab04-after/1280x800-full.png) และ [ก่อนมือถือ](evidence/lab04-before/390x844-full.png) / [หลังมือถือ](evidence/lab04-after/390x844-full.png) | PASS |

## หลักฐาน netlist / ngspice log ที่ใช้เทียบ (คัดจากหน้าเว็บ)

DC (B2):

```spice
VCC vcc 0 DC 12
VIN in 0 DC 0 AC 1 SIN(0 0.01 1000)
R1 vcc base 100000
R2 base 0 22000
RC vcc collector 2200
RE emitter 0 1000
Q1 collector base emitter QNPN
CIN in base 1e-05
COUT collector out 1e-05
RL out 0 10000
.model QNPN NPN(IS=1e-14 BF=100 VAF=100 RB=10 RC=1)
.op
.print op v(base) v(emitter) v(collector) v(in) v(out)
.end
```

AC (B4): `.ac dec 50 1 100000000` และ `.print ac vdb(in) vp(in) vdb(out) vp(out)`
— parser รวมตารางที่ ngspice แบ่งเป็นหน้า (header `Index frequency vdb(out) vp(out)`
ซ้ำทุก ~60 แถว) ตาม frequency ก่อนสร้าง polyline

Transient (B5/B6): `.tran 1e-05 0.005`, `.print tran v(in) v(out)`,
`SIN(0 0.01 1000)` → `SIN(0 0.02 2000)` เมื่อเปลี่ยน amplitude/frequency

ไม่มีการ hard-code ค่ากราฟ: ทุก polyline ถูกสร้างจาก array ที่ parse ได้จาก `run.log`
ของรันนั้น ๆ ถ้า log ว่าง/parse ไม่ได้/timeout จะขึ้น `status: error` และไม่มีกราฟ

## Impeccable critique และการแก้จริง

ใช้ **dual-agent** (Design Review + CLI/browser audit) แล้วสังเคราะห์เป็น snapshot เดียว
([docs/evidence/lab04-impeccable-critique.md](evidence/lab04-impeccable-critique.md)
— สำเนาจาก `.impeccable/critique/2026-11-24T10-51-58Z__127-0-0-1.md`) คะแนน **20/40 — Acceptable**

| Priority | สิ่งที่เจอ | การจัดการ |
|---|---|---|
| **P0** | ฟอร์ม simulator โหลดมาด้วยค่าเดิมเป็นช่องว่าง เพราะ Jinja อ่าน `sim_form.values` เป็น method ของ dict ไม่ใช่ key | แก้เป็น `sim_form['values'][field]` / `sim_form['units'][field]` 4 จุด + เพิ่ม `test_sim_form_renders_documented_defaults` — ตรวจแล้ว fresh GET เห็น `value="12.0"`, `value="1.0"` จริง (นี่คือสาเหตุที่ B3 รอบแรกดูเหมือน RE ไม่เปลี่ยน) |
| P1 | สอง primary action / สองหัวข้อ, ป้ายสัญลักษณ์ล้วน | บันทึกเป็น known limitation; ไม่เปลี่ยนโครงสร้าง Lab 03 เพื่อรักษา regression B1 |
| P2 | provenance มาก่อนคำตอบ, Δ ไม่มี verdict, accessibility/touch target | บันทึกเป็น known limitation; เน้นความถูกต้องของ simulation ตาม rubric ก่อน |

detector แจ้ง `low-contrast` 4.3:1–4.49:1 (บางอันขาด 0.01), `ai-color-palette` บนปุ่ม teal,
`nested-cards` บน callout แบบเส้นประ — ตรวจแล้วบางส่วนเป็น borderline/over-report
(เช่น `flat-type-hierarchy` ใน source scan เป็น false positive เพราะแก้ `url_for()` ไม่ได้)
overlay ถูก inject ทดสอบในแท็บใหม่แล้วปิด live-server ทุกครั้ง ไม่มี script ค้างในแอป

## ข้อจำกัดที่ระบุอย่างตรงไปตรงมา

1. **ไม่มี instructor-verified Starter Kit** จึงใช้ generic teaching model และแสดงป้ายกำกับทุกครั้ง
   SPICE และ analytical ไม่ควรตรง digit-for-digit ค่า `IC` ถูก derive จาก `VC` ไม่ใช่ device current ที่ print
2. **Cutoff frequency ไม่ถูก determine** เพราะจุด −3 dB ไม่อยู่ในช่วง sweep ที่ใช้
   หน้าแสดง `not determined in sweep range` แทนการเดาค่า
3. **Playwright MCP NOT RUN** ใช้ OpenCode Browser แทนตามที่ใบงานอนุญาต (ดูเหตุผลด้านบน)
4. **ยังไม่มี** emitter bypass capacitor, animated overlay, หรือ React/Vite — อยู่นอก scope ของ v1 ตามใบงาน
5. `LAB04_KEEP_RUNS` ไม่ได้ตั้งระหว่าง acceptance จึงใช้ `run_dir` ชั่วคราวต่อรัน; เปิดได้ด้วย env var ถ้าต้องการเก็บไฟล์

## สรุปสถานะรับเลย

B1–B8 ผ่านทั้งหมด (**8 PASS**, 0 FAIL) โดยใช้ browser จริงและเทียบกับ netlist/log ของ ngspice 47;
Playwright MCP เองเป็น **NOT RUN** พร้อมเหตุผลด้านบน และชุดเทสต์รวมผ่าน **31 tests OK**
(20 เดิม + 11 ใหม่ของ Lab 04)
