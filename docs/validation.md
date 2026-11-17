# Lab 03 — Browser Acceptance (A1–A5)

**วิธีตรวจ:** OpenCode Browser (Browser tool ใน OpenCode Desktop) — ไม่ได้ใช้ Playwright MCP
**วันที่ตรวจ:** 2026-11-17
**เครื่อง:** Windows, Flask dev server ที่ `http://127.0.0.1:5000/`

ใช้ค่าร่วมทุกกรณี: `VCC = 12 V`, `RC = 2.2 kΩ`, `β = 100`, `VBE = 0.70 V`
เกณฑ์: `IC` คลาดเคลื่อนไม่เกิน ±0.01 mA และ `VCE` ไม่เกิน ±0.02 V เทียบกับค่าอ้างอิงที่คำนวณมือ (ก่อนปัดเศษ)

ค่าอ้างอิงคำนวณจากสมการในใบงานด้วยเครื่องคิดเลข (ไม่ใช่ค่าจากโปรแกรม):

- A1 Divider: IB = 12.2986 µA → IC = 1.2299 mA, VCE = 8.0522 V
- A2 Fixed: IB = 11.3000 µA → IC = 1.1300 mA, VCE = 9.5140 V
- A3 Emitter (RE = 1 kΩ): IB = 10.2634 µA → IC = 1.0263 mA, VCE = 8.7054 V
- A4 Emitter (RE = 2 kΩ): IB = 9.4010 µA → IC = 0.9401 mA, VCE = 8.0328 V

| กรณี | วิธีตรวจ | อินพุตที่กรอก | คาดหมายก่อนรัน | ผลที่เห็นจริง | สถานะ | หลักฐาน |
|---|---|---|---|---|---|---|
| A1 · โหมดเดิม | OpenCode Browser | Divider · R1 = 100 kΩ, R2 = 22 kΩ, RE = 1 kΩ (ค่าเริ่มต้น) | IC = 1.2299 mA · VCE = 8.0522 V | VB 1.94 V, VE 1.24 V, VC 9.29 V, **VCE 8.05 V**, IB 12.3 µA, **IC 1.23 mA**, IE 1.24 mA · ACTIVE | PASS | ข้อความบนหน้า + ค่าตรงกับ Lab 02 เดิม |
| A2 · Fixed | OpenCode Browser | Fixed · RB = 1 MΩ (ไม่กรอก RE/R1/R2) | IC = 1.1300 mA · VCE = 9.5140 V | VB 0.70 V, VE 0.00 V, VC 9.51 V, **VCE 9.51 V**, IB 11.3 µA, **IC 1.13 mA**, IE 1.14 mA · ACTIVE | PASS | `docs/evidence/lab03-a2-fixed.jpeg` |
| A3 · Emitter | OpenCode Browser | Emitter · RB = 1 MΩ, RE = 1 kΩ | IC = 1.0263 mA · VCE = 8.7054 V | VB 1.74 V, VE 1.04 V, VC 9.74 V, **VCE 8.71 V**, IB 10.26 µA, **IC 1.03 mA**, IE 1.04 mA · ACTIVE | PASS | `docs/evidence/lab03-a3-emitter.jpeg` |
| A4 · เปลี่ยนค่าเดียว | OpenCode Browser | Emitter · เหมือน A3 แต่ RE = 2 kΩ | ทำนาย: IC ลดลงเพราะ RE ใหญ่ขึ้นลด IB · IC = 0.9401 mA · VCE = 8.0328 V | VB 2.60 V, VE 1.90 V, VC 9.93 V, **VCE 8.03 V**, IB 9.4 µA, **IC 940.1 µA (0.9401 mA)**, IE 949.5 µA · ACTIVE | PASS | ข้อความบนหน้า (IC ลดจาก A3) |
| A5 · อินพุตผิด | OpenCode Browser | Fixed · RB = 0 | ต้องมีข้อความให้แก้ RB, เว็บไม่ล่ม, ไม่แสดงผลเดิม | ขึ้น `must be greater than zero` ใต้ช่อง RB, ค่า 0 ยังคงอยู่, ไม่มีตารางผลลัพธ์, หน้าโหมด Fixed ยังใช้งานได้ | PASS | ข้อความบนหน้า |

## ตรวจเพิ่มเติม

| สิ่งที่ตรวจ | ผล |
|---|---|
| โหมดที่ไม่รู้จัก (`/calculate` ด้วย `mode=bogus`) | แสดง `Unknown bias mode: bogus (showing Voltage Divider Bias)` ไม่คำนวณและไม่แสดงผลลัพธ์ |
| หน่วยที่ไม่รู้จัก (`r1_unit=banana`) | แสดง `invalid unit` และไม่แสดงผล (เดิมเงียบ ๆ ใช้ตัวคูณ 1.0) |
| ผลตรวจไขว้ (Closed-form vs Independent) | ทั้งสามโหมดขึ้น `Matches within tolerance` |
| ฟอร์มโหมด Fixed | ไม่มีช่อง R1/R2/RE และไม่บังคับกรอก |
| ฟอร์มโหมด Emitter | มี RB, RE, RC และใช้ค่า RE จริง (A3 → A4 เปลี่ยนผล) |

## หมายเหตุ

- โปรแกรมแสดง V เป็นทศนิยม 2 ตำแหน่ง และกระแสเลือกหน่วยอัตโนมัติ (A/mA/µA) จึงเทียบกับค่าอ้างอิงที่ยังไม่ปัดเศษตามเกณฑ์ด้านบน
- ตารางนี้กรอกจากผลที่เห็นบนหน้าเว็บจริง ไม่ได้อ่านจากซอร์สโค้ดหรือเรียก HTTP ตรง
