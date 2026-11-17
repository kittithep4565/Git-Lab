# Git-Lab
ใช้สำหรับเรียน Lab compro ไฟฟ้า

## BJT DC Bias Web App (ENG29 2121)

แอป Flask สำหรับคำนวณจุดทำงาน DC ของ NPN Common-Emitter amplifier เลือกได้สามโหมด:

| โหมด | อินพุตเฉพาะโหมด | สมการกระแสฐาน |
|---|---|---|
| Fixed Bias | `RB` | `IB = (VCC − VBE) / RB` |
| Emitter Bias | `RB`, `RE` | `IB = (VCC − VBE) / [RB + (β+1)RE]` |
| Voltage Divider Bias | `R1`, `R2`, `RE` | `IB = (VTH − VBE) / [RTH + (β+1)RE]` |

ทุกโหมดใช้ `VCC`, `RC`, `β`, `VBE` ร่วมกัน แล้วคำนวณ `IC = βIB`, `IE = (β+1)IB`,
`VE = IE·RE`, `VB = VE + VBE`, `VC = VCC − IC·RC`, `VCE = VC − VE`

### ติดตั้งและรัน

```bash
python -m pip install -r requirements.txt
python run.py
```

เปิด http://127.0.0.1:5000 แล้วเลือกโหมดจากแท็บด้านบนฟอร์ม (สลับโหมดด้วย `?mode=fixed`,
`?mode=emitter` หรือ `?mode=divider` — ไม่ต้องใช้ JavaScript)

### รันเทสต์

```bash
python -m unittest discover -s tests -v
```

### Units

Voltages accept `V` or `mV`. Resistances accept `Ω`, `kΩ`, or `MΩ`. Beta is
dimensionless. Values are converted to SI units before calculation.

### โครงสร้าง

- `bjt/engineering.py` — สมการของแต่ละโหมด (`analyze_fixed`, `analyze_emitter`,
  `analyze_bias` สำหรับ Divider) และตัวเลือกฟังก์ชัน `analyze_mode`
- `bjt/independent.py` — ตัวแก้สมการอิสระ (bisection) ต่อโหมด และ `compare_results`
- `bjt/routes.py` — อ่านฟอร์ม, แปลงหน่วยครั้งเดียว, เลือกโหมด, ตรวจอินพุตตามโหมด
- `bjt/templates/index.html` — แท็บเลือกโหมด ฟอร์มเฉพาะโหมด แผนวงจร และผลลัพธ์
- `docs/validation.md` — ตารางตรวจ A1–A5 พร้อมหลักฐานจากเบราว์เซอร์
