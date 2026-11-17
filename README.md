# Git-Lab
ใช้สำหรับเรียน Lab compro ไฟฟ้า

- GitHub: https://github.com/kittithep4565/Git-Lab.git
- Lab 03 implementation commit: [`a93ecb5`](https://github.com/kittithep4565/Git-Lab/commit/a93ecb5)
- หลักฐานการตรวจ A1–A5: [docs/validation.md](docs/validation.md)

## BJT DC Bias Web App (ENG29 2121)

แอป Flask สำหรับคำนวณจุดทำงาน DC ของ NPN Common-Emitter amplifier เลือกได้สามโหมด:

| โหมด | อินพุตเฉพาะโหมด | สมการกระแสฐาน |
|---|---|---|
| Fixed Bias | `RB` | `IB = (VCC − VBE) / RB` |
| Emitter Bias | `RB`, `RE` | `IB = (VCC − VBE) / [RB + (β+1)RE]` |
| Voltage Divider Bias | `R1`, `R2`, `RE` | `IB = (VTH − VBE) / [RTH + (β+1)RE]` |

ทุกโหมดใช้ `VCC`, `RC`, `β`, `VBE` ร่วมกัน แล้วคำนวณ `IC = βIB`, `IE = (β+1)IB`,
`VE = IE·RE`, `VB = VE + VBE`, `VC = VCC − IC·RC`, `VCE = VC − VE`

## วิธีรัน (Getting Started)

### สิ่งที่ต้องมี

- Python 3.10 ขึ้นไป (ทดสอบบน 3.12)
- ไม่ต้องติดตั้งฐานข้อมูลหรือ Node.js — ใช้ Flask ตัวเดียว
- พอร์ต 5000 ว่าง (ถ้าไม่ว่างดูหัวข้อ "แก้ปัญหา" ด้านล่าง)

ตรวจเวอร์ชัน Python ก่อน:

```bash
python --version
```

ถ้าคำสั่ง `python` ไม่ทำงาน ให้ใช้ `python3 --version` หรือ `py --version` แทน

### 1) ดาวน์โหลดโค้ด

```bash
git clone https://github.com/kittithep4565/Git-Lab.git
cd Git-Lab
```

ถ้ามีโฟลเดอร์นี้อยู่แล้ว ข้ามขั้นนี้และเปิด terminal ที่โฟลเดอร์ `Git-Lab`

### 2) สร้าง virtual environment (แนะนำ)

**Windows (PowerShell)**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

ถ้าขึ้น error เรื่อง `ExecutionPolicy` ให้เปิดสิทธิ์ครั้งเดียวแล้วสั่ง activate ใหม่:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

เมื่อ activate สำเร็จ จะเห็น `(.venv)` นำหน้าบรรทัดคำสั่ง ถ้าไม่อยากใช้ venv
ให้ข้ามข้อนี้แล้วติดตั้งแบบ global ได้เลย

### 3) ติดตั้ง dependencies

```bash
python -m pip install -r requirements.txt
```

ติดตั้งครั้งเดียวพอ (ต้องมี `Flask>=3.0,<4`)

### 4) รันเว็บแอป

```bash
python run.py
```

จะเห็นข้อความ:

```
* Running on http://127.0.0.1:5000
```

ห้ามปิด terminal นี้ระหว่างใช้งาน — ปิดเมื่อเลิกใช้ด้วย `Ctrl+C`

### 5) เปิดในเบราว์เซอร์

เปิด http://127.0.0.1:5000/ แล้วเลือกโหมดจากแท็บด้านบนฟอร์ม (สลับโหมดด้วย `?mode=fixed`,
`?mode=emitter` หรือ `?mode=divider` — ไม่ต้องใช้ JavaScript)

| โหมด | URL |
|---|---|
| Voltage Divider Bias | http://127.0.0.1:5000/?mode=divider |
| Fixed Bias | http://127.0.0.1:5000/?mode=fixed |
| Emitter Bias | http://127.0.0.1:5000/?mode=emitter |

กรอกค่าอุปกรณ์ (เลือกหน่วย `V`/`mV`, `Ω`/`kΩ`/`MΩ` ได้จาก dropdown) แล้วกด
**Calculate DC Bias** จะได้ `VB`, `VE`, `VC`, `VCE`, `IB`, `IC`, `IE`
พร้อมสถานะ active/cutoff/saturation และผลตรวจไขว้ (closed-form vs independent)

### 6) เลิกใช้งาน

กด `Ctrl+C` ใน terminal ที่รัน `run.py` แล้วปิด virtual environment ด้วย:

```bash
deactivate
```

### แก้ปัญหาเบื้องต้น

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `ModuleNotFoundError: No module named 'flask'` | ยังไม่ได้ติดตั้ง หรือ activate venv คนละอัน | `python -m pip install -r requirements.txt` แล้วรัน `python run.py` ใน terminal เดียวกัน |
| `OSError: [WinError 10048]` / `Address already in use` | พอร์ต 5000 ถูกใช้อยู่ (มักเป็น `python run.py` ตัวเก่า) | ปิดตัวเก่าด้วย `Ctrl+C` หรือหา PID แล้วปิด: `netstat -ano \| findstr :5000` แล้ว `taskkill /PID <pid> /F` |
| เปิดเว็บแล้วขึ้น connection refused | เซิร์ฟเวอร์ยังไม่ขึ้นหรือถูกปิดไปแล้ว | รัน `python run.py` ใหม่แล้วรอข้อความ `Running on http://127.0.0.1:5000` |
| `Activate.ps1 cannot be loaded because running scripts is disabled` | PowerShell block script | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| แก้โค้ดแล้วหน้าเว็บไม่เปลี่ยน | ยังไม่ได้ refresh หรือเซิร์ฟเวอร์ตายจาก syntax error | ดู error ใน terminal, แก้ให้ถูก แล้วกด refresh (โหมด debug จะ reload เอง) |
| ภาษาไทยในหน้าเว็บเป็นตัวขยะ | ไฟล์ถูกบันทึกผิด encoding | บันทึกเป็น UTF-8 (ห้ามใช้ PowerShell `Set-Content` แก้ไฟล์ `.md`/`.html` ที่มีภาษาไทย) |

### รันเทสต์

```bash
python -m unittest discover -s tests -v
```

ต้องได้ 20 tests ผ่านทั้งหมด (ใช้เป็นตัวตรวจว่าแก้โค้ดแล้วไม่พังของเดิม)

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
