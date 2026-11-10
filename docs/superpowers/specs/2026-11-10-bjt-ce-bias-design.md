# BJT Common-Emitter DC Bias Web App — Design

- วันที่: 2026-11-10
- สถานะ: รออนุมัติ
- แล็บ: ENG29 2121
- ที่มา: ต้องการเว็บ Flask ขนาดเล็กที่คำนวณจุดทำงาน DC ของ NPN common-emitter แบบ voltage-divider bias พร้อมตรวจสอบอินพุต เตือน region และเทียบผลกับการคำนวณอิสระ

## 1. บริบทและเหตุผล

แล็บสั้นนี้ต้องส่งแอป Flask จริงที่แยก engineering logic, routes, templates, CSS และ tests ออกจากกัน ผลลัพธ์ต้องมีหน่วย มี validation และเตือนเมื่อทรานซิสเตอร์ไม่อยู่ใน active region การมีตัวคำนวณที่สองช่วยยืนยันผลและใช้เป็นหลักฐานในรายงานแล็บได้

## 2. เป้าหมาย

- รับอินพุต VCC, R1, R2, RC, RE, β, VBE
- คำนวณจุดทำงาน DC: IB, IC, IE, VB, VE, VC, VCE
- แสดงหน่วยและจัดรูปแบบตัวเลขให้อ่านง่าย
- ตรวจอินพุตและแสดง error รายฟิลด์
- จำแนก region: active, saturation, cutoff
- แสดงผลจากสมการ closed-form เทียบกับตัวคำนวณอิสระ พร้อม delta และ badge
- รันบน localhost ได้ และมีเทสต์อัตโนมัติ

## 3. Non-goals / Anti-goals

- ไม่มี AC, transient, frequency response
- ไม่มี circuit editor, netlist หรือ SPICE simulation
- ไม่รองรับ FET หรือ PNP (NPN เท่านั้น)
- ไม่แก้สมการใหม่สำหรับจุดอิ่มตัว — รายงานผล active-region พร้อมคำเตือน
- ไม่มีฐานข้อมูล, login, JS framework หรือ Docker
- ไม่แก้ `electrical.py` เดิม

Anti-goal: แอปที่ "รันได้" แต่ตัวเลขไม่ตรงกับสมการที่คำนวณมือ หรือไม่มีการตรวจอินพุต

## 4. ข้อจำกัด

- Python 3.10.11, Flask 3.x (ยังไม่ติดตั้งในเครื่อง)
- Windows, รันด้วย `python run.py`
- เทสต์ด้วย `unittest` (stdlib) ไม่เพิ่ม dependency
- ต้อง demo และ commit ขึ้น GitHub ภายในวันนี้

## 5. ทางเลือกที่พิจารณา

### แบบ 1 — แพ็กเกจ + ตัวตรวจแบบตัวเลข (เลือก)

```
run.py
requirements.txt
bjt/__init__.py        create_app()
bjt/engineering.py     closed-form + validation + region
bjt/independent.py     bisection บน KCL ที่ base node
bjt/routes.py          GET / , POST /calculate
bjt/templates/index.html
bjt/static/style.css
tests/test_engineering.py
tests/test_independent.py
tests/test_routes.py
```

- ตัวตรวจอิสระใช้วิธีตัวเลข (bisection) ไม่ได้ใช้พีชคณิตชุดเดียวกับผลหลัก
- Flask test client ทำงานสะอาด และเป็นโครงสร้างมาตรฐาน
- ต้นทุน: เพิ่ม `__init__.py` และ `run.py` ไม่กี่บรรทัด

### แบบ 2 — ไฟล์แบน + ตัวตรวจเชิงพีชคณิต

ไฟล์น้อยกว่า แต่ `app` ระดับโมดูลเทสต์แยกยากกว่า และตัวตรวจใช้พีชคณิตใกล้เคียงกับผลหลักเกินไป

### ทางเลือกที่ตัดทิ้ง

- Single-file app — ผิดข้อกำหนดเรื่องแยก engineering logic
- โมเดล Shockley แบบ nonlinear — ต้องเพิ่ม IS/n/VT ซึ่งไม่อยู่ในอินพุตที่กำหนด และเปลี่ยนฟิสิกส์จนการเทียบไม่มีความหมาย
- Blueprint — เกินจำเป็นสำหรับ 2 route

**เลือกแบบ 1** เพราะแยกส่วนชัด เทสต์ง่าย และการครอสเช็กมีความเป็นอิสระจริง

## 6. การออกแบบ

### 6.1 วงจร

NPN voltage-divider bias: R1 จาก VCC ไป base, R2 จาก base ไป ground, RC จาก VCC ไป collector, RE จาก emitter ไป ground ไม่มีโหลดและไม่คิดผลของ capacitor (DC เท่านั้น)

### 6.2 อินพุตและค่าเริ่มต้น

| ฟิลด์ | หน่วย | ค่าเริ่มต้น |
|---|---|---|
| VCC | V | 12 |
| R1 | Ω | 47000 |
| R2 | Ω | 10000 |
| RC | Ω | 2200 |
| RE | Ω | 1000 |
| β | - | 150 |
| VBE | V | 0.7 |

ค่าความต้านทานกรอกเป็นโอห์ม (ไม่รับ suffix เช่น 47k)

### 6.3 การตรวจสอบอินพุต

- ทุกฟิลด์ต้องมีค่า เป็นตัวเลข และเป็น finite (ไม่ใช่ NaN/Infinity)
- ปฏิเสธ `bool` แม้ใน Python จะนับเป็น int
- VCC > 0
- R1, R2, RC, RE > 0
- β > 0
- 0 ≤ VBE < VCC
- อินพุตผิด: เรนเดอร์ฟอร์มเดิมพร้อมค่าเก่าและข้อความ error รายฟิลด์ ไม่คำนวณ

### 6.4 สมการหลัก (closed-form)

```
RBB = R1 * R2 / (R1 + R2)
VBB = VCC * R2 / (R1 + R2)

IB = (VBB - VBE) / (RBB + (β + 1) * RE)
IC = β * IB
IE = (β + 1) * IB

VE = IE * RE
VB = VE + VBE
VC = VCC - IC * RC
VCE = VC - VE
```

### 6.5 การจำแนก region

| เงื่อนไข | Region | การแสดงผล |
|---|---|---|
| IB ≤ 0 | cutoff | IB = IC = IE = 0, VE = 0, VB = VBB, VC = VCC, VCE = VCC |
| VCE < 0.2 V | saturation | รายงานค่าที่คำนวณได้ + เตือนว่าสมการ active-region ใช้ไม่ได้ |
| VCE ≥ 0.2 V | active | ไม่มีคำเตือน |

`VCE_sat = 0.2 V` เป็นค่าคงที่ ไม่รับเป็นอินพุต

### 6.6 ตัวคำนวณอิสระ

แก้ KCL ที่ base node ด้วย bisection แทนการแทนสูตร:

```
VB(IB) = VBE + (β + 1) * IB * RE
f(IB) = (VCC - VB(IB)) / R1 - VB(IB) / R2 - IB
```

- ถ้า `f(0) ≤ 0` → cutoff (ใช้ค่าเดียวกับตาราง 6.5)
- ไม่งั้นหา IB ที่ทำให้ `f(IB) = 0` ด้วย bisection ช่วง `[0, VCC/R1]` (ขยายขอบเขตถ้าจำเป็น) สูงสุด 200 รอบ
- คำนวณ IC, IE, VE, VB, VC, VCE จาก IB ด้วยสมการฟิสิกส์เดียวกัน
- ใช้ `classify_region` ร่วมกับผลหลัก

### 6.7 การเทียบผล

- เทียบทีละปริมาณด้วย `math.isclose(rel_tol=1e-6, abs_tol=1e-9)`
- ตรงกันทุกค่า → badge "ตรงกันภายใน tolerance"
- ไม่ตรง → badge เตือน พร้อมค่า delta
- แสดงตาราง: Quantity | Closed-form | Independent | Delta

### 6.8 หน้าจอ

หน้าเดียว `/`:

```
+--------------------------------------------------+
| BJT CE DC Bias Calculator                        |
| [VCC] [R1] [R2] [RC] [RE] [β] [VBE]  [Calculate] |
|                                                  |
| Region badge: ACTIVE                             |
| Warnings: ...                                    |
| Quantity | Closed-form | Independent | Delta     |
| IB       | 8.82 µA     | 8.82 µA     | 0.00      |
| ...                                              |
| [Match badge]                                    |
+--------------------------------------------------+
```

- GET `/` แสดงฟอร์มพร้อมค่าเริ่มต้น
- POST `/calculate` ตรวจสอบ → คำนวณ → เรนเดอร์ผล
- ไม่ใช้ JavaScript; ฟอร์ม HTML ธรรมดา, label ครบ, CSS responsive เรียบง่าย
- หน่วยกระแสเลือกอัตโนมัติ µA/mA/A; แรงดันเป็น V ทศนิยม 3 ตำแหน่ง

### 6.9 เทสต์

- `test_engineering.py`
  - ค่าตัวอย่าง: VCC=12, R1=47k, R2=10k, RC=2.2k, RE=1k, β=150, VBE=0.7 → IB≈8.8245 µA, IC≈1.3237 mA, IE≈1.3325 mA, VB≈2.0325 V, VE≈1.3325 V, VC≈9.0879 V, VCE≈7.7554 V
  - cutoff, saturation
  - validation: ค่าเป็นศูนย์/ติดลบ, β ≤ 0, VBE ≥ VCC, ค่าไม่ใช่ตัวเลข, bool, NaN/Infinity
- `test_independent.py`
  - ตรงกับ closed-form ในเคส active, cutoff, saturation
  - bisection ลู่เข้า
  - validation ผิดแบบเดียวกับผลหลัก
- `test_routes.py`
  - GET 200 และมีฟอร์ม
  - POST ถูกต้องแสดงผลทั้งสองคอลัมน์และ badge
  - POST ผิดแสดง error และคงค่าเดิม

รัน: `python -m unittest discover -s tests -v`

### 6.10 วิธีรัน

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run.py
# เปิด http://127.0.0.1:5000
```

`requirements.txt` ระบุเฉพาะ Flask 3.x

## 7. สิ่งที่เหลือให้ผู้สร้างตัดสิน

- ถ้อยคำของคำเตือนและ label
- ค่า tolerance ที่แสดงผลและรูปแบบ delta
- รายละเอียดหน้าตา CSS
- ค่าเริ่มต้นในฟอร์ม (ปรับได้ตามอาจารย์ผู้สอน)

## 8. นิยามของเสร็จ

- เทสต์ทั้งหมดผ่าน
- `python run.py` แล้วใช้งานได้ที่ localhost:5000
- demo ด้วยค่าเริ่มต้นแสดงผลถูกต้องและ badge ตรงกัน
- มี `requirements.txt` และคำแนะนำการรันใน README
- commit บน branch `feature/bjt-bias-app` แล้ว merge เข้า `main` และ push ขึ้น GitHub
