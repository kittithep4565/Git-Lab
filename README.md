# Git-Lab
ใช้สำหรับเรียน Lab compro ไฟฟ้า

- GitHub: https://github.com/kittithep4565/Git-Lab.git
- Lab 3 commits:
  [`a93ecb5`](https://github.com/kittithep4565/Git-Lab/commit/a93ecb5) (โค้ดสามโหมด) ·
  [`c5c1993`](https://github.com/kittithep4565/Git-Lab/commit/c5c1993) (ตาราง A1–A5 + หลักฐาน) ·
  [`8fc8c49`](https://github.com/kittithep4565/Git-Lab/commit/8fc8c49) (ลิงก์เอกสาร) ·
  [`6bca9f5`](https://github.com/kittithep4565/Git-Lab/commit/6bca9f5) (วิธีรันใน README)
- Commit ล่าสุดของสายงาน: https://github.com/kittithep4565/Git-Lab/commits/main
- หลักฐานการตรวจ A1–A5: [docs/validation.md](docs/validation.md)
- ค่าอ้างอิงอิสระ + สมการ: [docs/validation.md — ค่าอ้างอิงอิสระ](docs/validation.md#ค่าอ้างอิงอิสระ-คำนวณมือจากสมการใบงาน-ไม่ใช่ค่าจากโปรแกรม)

## BJT DC Bias Web App (ENG29 2121)

แอป Flask สำหรับคำนวณจุดทำงาน DC ของ NPN Common-Emitter amplifier เลือกได้สามโหมด:

| โหมด | อินพุตเฉพาะโหมด | สมการกระแสฐาน |
|---|---|---|
| Fixed Bias | `RB` | `IB = (VCC − VBE) / RB` |
| Emitter Bias | `RB`, `RE` | `IB = (VCC − VBE) / [RB + (β+1)RE]` |
| Voltage Divider Bias | `R1`, `R2`, `RE` | `IB = (VTH − VBE) / [RTH + (β+1)RE]` |

ทุกโหมดใช้ `VCC`, `RC`, `β`, `VBE` ร่วมกัน แล้วคำนวณ `IC = βIB`, `IE = (β+1)IB`,
`VE = IE·RE`, `VB = VE + VBE`, `VC = VCC − IC·RC`, `VCE = VC − VE`

## Lab 04 — BJT Amplifier Simulator v1 (ต่อจาก Lab 03)

เพิ่มจำลองจริงด้วย **ngspice** บนวงจร Common-Emitter voltage-divider **หนึ่งวงจร**
(`VCC 12 V`, `R1 100 kΩ`, `R2 22 kΩ`, `RC 2.2 kΩ`, `RE 1 kΩ`, `RL 10 kΩ`,
`Cin = Cout = 10 µF`, ไม่มี bypass capacitor) โดยยังคง `/calculate` และ
`fixed / emitter / divider` เดิมของ Lab 03 ไว้ทุกประการ

| Analysis | คำสั่ง SPICE จริง | ผลที่แสดง |
|---|---|---|
| DC | `.op` | `VB`, `VE`, `VC`, `VCE`, `IC` (derive จาก `VC` และ `RC`) |
| AC | `.ac` | Bode gain magnitude + phase เทียบ `Vin` ที่ node `in` ก่อน `Cin` (1 Hz–100 MHz) |
| Transient | `.tran` | `Vin` / `Vout` vs ms, ตรวจ inversion จาก correlation ติดลบ |

- ฟอร์ม `/simulate` มีค่าเริ่มต้นครบแล้ว (แก้บั๊ก Jinja `sim_form.values` → `sim_form['values']`)
- `β`, `VBE` เป็น **analytical reference เท่านั้น** ไม่ส่งเข้า ngspice — SPICE ใช้ `.model` ของจริง
- ผลลัพธ์มี provenance: เวอร์ชัน engine, ชื่อ/แหล่ง BJT model, isolated `run_dir`, netlist และ log
  ใน `<details>`; ไม่มีค่า plot hard-code และไม่แสดง `status: success` หากรันล้มเหลว

หลักฐานและตารางรับเลย B1–B8: [docs/validation.md — Lab 04](docs/validation.md#lab-04--bjt-amplifier-simulator-v1-b1b8)

## AI ช่วยส่วนไหน / นักศึกษาตรวจอะไร

| ส่วน | AI ช่วยทำ | นักศึกษาตรวจ |
|---|---|---|
| `bjt/engineering.py` — `analyze_fixed` (198), `analyze_emitter` (218), `analyze_mode` (239), `parse_mode_inputs` (100) | เขียนโค้ด ตั้งชื่อฟังก์ชัน และใส่สูตรจากใบงาน | เทียบสูตรทีละบรรทัดกับใบงาน + คำนวณมือ A2/A3/A4 แล้วเทียบกับผลบนหน้าเว็บ |
| `bjt/independent.py` — bisection ต่อโหมด | เขียนตัวแก้สมการอิสระและ `compare_results` | ตรวจว่าใช้วิธีต่างจากสูตร closed-form (bisection บน KCL) และผลขึ้น `Matches within tolerance` |
| `bjt/routes.py` | เขียน dispatch ตามโหมด, แปลงหน่วย, ตรวจอินพุตเฉพาะโหมด | กดฟอร์มทั้งสามโหมด, ลอง `mode=bogus`, `r1_unit=banana`, `RB = 0` และดูว่าไม่คำนวณต่อ |
| `bjt/templates/index.html`, `bjt/static/style.css` | เขียนแท็บโหมด, ฟอร์มเฉพาะโหมด, แผนวงจร, สไตล์ | เปิดทั้งสาม URL แล้วดูว่าแท็บ/ช่องกรอก/ผลลัพธ์ตรงโหมด |
| `docs/validation.md`, `docs/evidence/` | ร่างตาราง A1–A5 และเก็บภาพหน้าจอ | รันซ้ำในเบราว์เซอร์ (หัวข้อ [ทวนสอบซ้ำ](docs/validation.md#ทวนสอบซ้ำ-re-check)) แล้วยืนยันตัวเลข |
| `tests/` (20 tests เดิม) | ไม่ได้แก้ | รัน `python -m unittest discover -s tests` ให้ผ่านก่อน commit |
| `bjt/spice_engine.py` (Lab 04) | เขียน netlist, เรียก `subprocess.run([...], timeout=25, cwd=run_dir)` แบบไม่ใช้ `shell=True`, แปะ parse `.op`/`.ac`/`.tran` | เปิดดู netlist/log ที่แสดงบนหน้า, ตรวจว่าค่าในตาราง/กราฟมาจาก `.print` จริง, ลองปิด engine ดู error |
| `bjt/sim_params.py` (Lab 04) | เขียนตรวจหน่วย SI, ตาราง `REQUIRED_BY_ANALYSIS`, โหลด `.model` จาก file | ลอง `RE = 0`, หน่วย `banana`, `f = 5 Hz` แล้วดู error; ดูว่า β/VBE ไม่เข้า netlist |
| `bjt/plots.py` (Lab 04) | เขียน SVG polyline จาก array ของ ngspice โดยไม่เพิ่ม dependency | เปลี่ยน RE/amplitude/frequency แล้วดูว่ากราฟขยับ (ไม่ใช่ของ hard-code) |
| `bjt/routes.py` `/simulate` | เขียน route แยกจาก `/calculate`, จัดการ error/status/provenance | กด DC/AC/Transient แล้วดู `status`, เวอร์ชัน, model, `run_dir` |
| `tests/test_lab4.py` (11 tests ใหม่) | เขียนทดสอบ parser, error path, default form, Lab 03 regression | รันชุดรวมต้องได้ **31 tests OK** |
| Impeccable critique (dual-agent) | วิเคราะห์ UI, ชี้บั๊ก `sim_form.values` (P0) | นักศึกษากดฟอร์มใหม่ต้องเห็นค่าเริ่มต้น และตรวจ screenshot ก่อน/หลัง |

## จุดที่โค้ดเลือกฟังก์ชันและแปลงหน่วย

| งาน | ที่อยู่ | รายละเอียด |
|---|---|---|
| อ่านโหมดจาก URL (`?mode=`) | `bjt/routes.py:151` | `request.args.get("mode", "divider")` |
| อ่านโหมดจากฟอร์ม | `bjt/routes.py:164` | `request.form.get("mode", "divider")` — ฟอร์มเก่าที่ไม่มี `mode` ยังใช้ Divider ได้ |
| โหมดไม่รู้จัก | `bjt/routes.py:154-156`, `167-170` | ใส่ error และ **ไม่คำนวณ** (ไม่เดาเป็น Divider เงียบ ๆ) |
| เลือกเฉพาะช่องของโหมด | `bjt/routes.py:172-175` + `bjt/engineering.py:14-18` (`MODE_FIELDS`) | Fixed ไม่บังคับ R1/R2/RE, Emitter ใช้ RB/RE/RC |
| ตารางหน่วย | `bjt/routes.py:18-27` (`UNITS`) | V/mV, Ω/kΩ/MΩ, β ไม่มีหน่วย |
| แปลงหน่วยเป็น SI | `bjt/routes.py:81-84` (`_scale_for`), `97-116` (`_to_base_units`), เรียกที่ `177` | คูณครั้งเดียวก่อนเข้า engineering core; หน่วยไม่รู้จัก → `invalid unit` |
| ข้อความ → ตัวเลข + ตรวจสอบ | `bjt/routes.py:178` → `bjt/engineering.py:100` (`parse_mode_inputs`) → `_parse_fields` (78), `_validate_values` (48) | ตรวจเฉพาะ field ของโหมด |
| **เลือกฟังก์ชันคำนวณตามโหมด** | `bjt/routes.py:187` → `bjt/engineering.py:239-247` (`analyze_mode`) | `divider` → `analyze_bias` (242), `fixed` → `analyze_fixed` (244), `emitter` → `analyze_emitter` (246), โหมดอื่น raise `ValueError` |
| ตัวตรวจไขว้ | `bjt/routes.py:188` → `bjt/independent.py` (`solve_independent`) | bisection คนละสูตรกับ closed-form |
| แสดงผล | `bjt/routes.py:129-146` + `bjt/templates/index.html` | ส่ง `result` เป็น dict (`ib, ic, ie, vb, ve, vc, vce, region, warnings`) |

## ผลการตรวจ (Validation)

- ตาราง A1–A5 พร้อมอินพุต ค่าคาดหมาย ผลจริง หน่วย วิธีตรวจ และสถานะ: [docs/validation.md](docs/validation.md)
- ตาราง B1–B8 (ngspice `.op/.ac/.tran`, เปลี่ยนค่า, error path, UI desktop/mobile):
  [docs/validation.md — Lab 04](docs/validation.md#lab-04--bjt-amplifier-simulator-v1-b1b8)
- ค่าอ้างอิงอิสระของโหมดใหม่ (Fixed, Emitter) พร้อมสมการและหน่วย: [docs/validation.md — ค่าอ้างอิงอิสระ](docs/validation.md#ค่าอ้างอิงอิสระ-คำนวณมือจากสมการใบงาน-ไม่ใช่ค่าจากโปรแกรม)
- หลักฐานภาพหน้าจอ: [A2](docs/evidence/lab03-a2-fixed.jpeg) · [A3](docs/evidence/lab03-a3-emitter.jpeg) · [A4 (RE = 2 kΩ)](docs/evidence/lab03-a4-emitter-re2.jpeg)
- วิธีตรวจ: **OpenCode Browser** (ไม่ใช้ Playwright MCP เพราะต้องรีสตาร์ทแอปเพื่อโหลด config) — เหตุผลและบทบาทของ MCP อยู่ใน [docs/validation.md](docs/validation.md#ทำไมเปลี่ยนเครื่องมือจาก-playwright-mcp)
- ตรวจเส้นทางของค่า (ฟอร์ม → หลังแปลงหน่วย → argument ของฟังก์ชัน): [docs/validation.md — ตรวจเส้นทางของค่า RE](docs/validation.md#ตรวจเส้นทางของค่า-re-ตอบคำถามปิด-lab)

## คำถามปิด Lab

> ถ้าตัวเลขคำนวณมือถูก แต่เปลี่ยน RE แล้วผลบนหน้าเว็บไม่เปลี่ยน จะตรวจค่าที่ส่งจากฟอร์มและค่าที่เข้าไปในฟังก์ชันอย่างไร?

ตอบ: ตรวจ 3 ชั้น ถ้าชั้นไหนขาด ให้แก้ที่ชั้นนั้น

1. **ค่าที่ส่งจากฟอร์ม** — เปิด DevTools → Network ดู `POST /calculate` ต้องมี `re=2&re_unit=kΩ`
   ถ้าไม่มี แปลว่าช่องนั้นไม่ถูกส่ง (name ผิด, ถูก `disabled`, หรือค่าถูกเขียนทับด้วยค่าเริ่มต้น)
2. **ค่าหลังแปลงหน่วย** — ตรวจ `_to_base_units` (`bjt/routes.py:97`) ว่า kΩ ถูกคูณ 1000 เป็น `2000.0`
   และไม่ตกไปที่ branch `invalid unit`
3. **ค่าที่เข้าไปในฟังก์ชัน** — ตรวจ `bjt/routes.py:187` ส่งเข้า `analyze_mode` แล้ว dispatcher
   (`bjt/engineering.py:239`) เรียก `analyze_emitter` และฟังก์ชัน (`bjt/engineering.py:218`) ใช้ `re`
   ในสูตร `IB = (VCC − VBE) / (RB + (β+1)RE)` จริง — ถ้าค่าเข้าไปถูกแต่ผลเท่าเดิม ให้สงสัยว่าหน้าเว็บ
   แสดงผลเก่าค้าง หรือ `result` ไม่ได้ถูกส่งกลับไปที่ template

หลักฐานจริงของกรณีนี้ (RE 1 kΩ → 2 kΩ): [docs/validation.md — ตรวจเส้นทางของค่า RE](docs/validation.md#ตรวจเส้นทางของค่า-re-ตอบคำถามปิด-lab)

## ก่อน commit (ขั้นตอนที่ใช้จริง)

```bash
git status --short          # ดูไฟล์ที่เปลี่ยน
git diff                    # ตรวจเนื้อหาที่แก้
git add <ไฟล์ที่ต้องการ>
git diff --staged           # ตรวจรายการที่จะ commit จริง
git commit -m "feat: ..."
git push origin main
```

`.gitignore` กัน `__pycache__/`, `*.pyc`, `.venv/`, `.env`, `.opencode/` ไว้แล้ว
(`.opencode/` คือ skill ที่ติดตั้งสำหรับ Impeccable ไม่ใช่โค้ดแอป) — ในรีโปนี้ไม่มี
`.venv`, `.env` หรือ credentials ถูก commit; หลักฐาน critique เก็บใน
[docs/evidence/lab04-impeccable-critique.md](docs/evidence/lab04-impeccable-critique.md)


## วิธีรัน (Getting Started)

### สิ่งที่ต้องมี

- Python 3.10 ขึ้นไป (ทดสอบบน 3.12)
- ไม่ต้องติดตั้งฐานข้อมูลหรือ Node.js — ใช้ Flask ตัวเดียว
- พอร์ต 5000 ว่าง (ถ้าไม่ว่างดูหัวข้อ "แก้ปัญหา" ด้านล่าง)
- **ngspice** (ทดสอบบน 47) — จำเป็นเฉพาะ Lab 04 `/simulate`; Lab 03 `/calculate` ใช้ได้โดยไม่มีก็ได้

### ติดตั้ง ngspice (Lab 04)

ดาวน์โหลด executable จาก [ngspice Downloads](https://sourceforge.net/projects/ngspice/files/)
แล้วใส่โฟลเดอร์ `bin` ลง `PATH` หรือบอก path ตรง ๆ ผ่าน environment variable:

```powershell
$env:NGSPICE_EXE = 'C:\Users\คุณ\ngspice-47\Spice64\bin\ngspice.exe'
```

ตรวจสอบ (ถ้า `ngspice --version` ไม่พิมพ์อะไรใน PowerShell ให้ดูที่ path ของไฟล์
หรือเปิด `ngspice` แบบ interactive แล้วดู banner):

```bash
ngspice --version        # หรือ ngspice -v
```

แอปจะหา engine ตามลำดับ: `NGSPICE_EXE` → `PATH` → `~/ngspice-47/Spice64/bin/ngspice.exe`
(Windows) → `/usr/bin/ngspice` (Unix) ถ้าไม่เจอ จะเห็นป้าย `ngspice not found` และ
`status: error` แทนการคำนวณปลอม

### BJT model (Lab 04)

ไม่พบ Starter Kit ที่อาจารย์ตรวจแล้วในรีโปนี้ จึงใช้ fallback ที่ระบุชัดบนหน้าเว็บ:

```
.model QNPN NPN(IS=1e-14 BF=100 VAF=100 RB=10 RC=1)
```

และแสดงข้อความ `generic teaching model (no starter file found)` ทุกครั้ง ถ้ามี model
ของอาจารย์ ให้วางไฟล์ไว้ที่ `bjt/spice_model.lib` หรือตั้ง:

```powershell
$env:LAB04_MODEL_FILE = 'C:\path\to\instructor-model.lib'
```

แอปจะอ่าน `.model` ตัวแรกจากไฟล์และเปลี่ยนป้ายเป็น `starter file: <ชื่อไฟล์>` แทน

### เก็บหลักฐานการรัน (Lab 04)

ตามค่าเริ่มต้น ngspice จะรันใน isolated temp dir แล้วลบทิ้ง ถ้าต้องการเก็บ `circuit.cir`
และ `run.log` ไว้ตรวจภายหลัง ให้ตั้งก่อนรันเซิร์ฟเวอร์:

```powershell
$env:LAB04_KEEP_RUNS = '1'
python run.py
```

`run_dir` จะแสดงบนหน้า `Simulation & Plots`; **ไม่ใช้ค่าเก่าจากรันก่อนหน้า** — ทุกการกด
Run สร้าง directory ใหม่เสมอ

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

สำหรับ Lab 04 ให้เลื่อนลงไปที่ฟอร์ม **BJT CE Amplifier Simulator v1** เลือก
`DC · .op` / `AC · .ac` / `Transient · .tran` แล้วกด **Run Simulation**
(fresh GET จะเห็นค่าตัวเลขครบอยู่แล้ว ไม่ต้องเดาค่า) ผลที่ได้:

- `status: success` พร้อม `ngspice <version>`, analysis, model และ model source
- DC: ตาราง `VB/VE/VC/VCE/IC` + ตารางเทียบ analytical vs SPICE
- AC: กราฟ gain (dB) และ phase (°) แกนความถี่ log scale 1 Hz–100 MHz
- Transient: กราฟ `Vin`/`Vout` vs ms พร้อมข้อความ `inverted (negative correlation)`
- `Netlist & ngspice run log (evidence)` — กด `<details>` เพื่อดู `circuit.cir` และ `run.log`

ถ้าไม่มี ngspice ให้ขึ้น `ngspice not found` / `status: error` และ **ไม่มีกราฟ** —
ไม่มีการปลอมผลลัพธ์ ส่วนค่าที่ผิด (เช่น `RE = 0`) จะแสดง error ใต้ช่องนั้นทันที

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

ต้องได้ **31 tests** ผ่านทั้งหมด (20 เดิมของ Lab 03 + 11 ใหม่ของ Lab 04)
ใช้เป็นตัวตรวจว่าแก้โค้ดแล้วไม่พังของเดิม

```text
Ran 31 tests in 0.232s
OK
```

### Units

Voltages accept `V` or `mV`. Resistances accept `Ω`, `kΩ`, or `MΩ`. Beta is
dimensionless. Values are converted to SI units before calculation.

### โครงสร้าง

- `bjt/engineering.py` — สมการของแต่ละโหมด (`analyze_fixed`, `analyze_emitter`,
  `analyze_bias` สำหรับ Divider) และตัวเลือกฟังก์ชัน `analyze_mode` (Lab 03 — ไม่แตะ)
- `bjt/independent.py` — ตัวแก้สมการอิสระ (bisection) ต่อโหมด และ `compare_results`
- `bjt/routes.py` — `/calculate` (Lab 03) และ `/simulate` (Lab 04) แยกกัน,
  อ่านฟอร์ม, แปลงหน่วยครั้งเดียว, ตรวจอินพุต, status/provenance
- `bjt/spice_engine.py` — สร้าง netlist, รัน ngspice ด้วย `subprocess.run`, parse `.op/.ac/.tran`
- `bjt/sim_params.py` — validate/หน่วย/default ของ Lab 04, โหลด BJT `.model`
- `bjt/plots.py` — SVG gain/phase/waveform จากข้อมูลจริง (ไม่ใช้ chart library)
- `bjt/templates/index.html`, `bjt/static/style.css` — ฟอร์มทั้งสองชุด, กราฟ, evidence drawer
- `tests/test_lab4.py` — 11 tests ของ Lab 04 (parser/error/route/default/regression)
- `docs/validation.md` — ตารางตรวจ A1–A5 (Lab 03) และ B1–B8 (Lab 04) พร้อมหลักฐาน
- `docs/evidence/` — ภาพก่อน/หลัง Impeccable และภาพรับเลย B1–B7, B8 desktop/mobile
