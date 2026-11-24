# Lab 04 — Rubric Evidence Pack (10 คะแนน)

ภาพทั้งหมดถ่ายจากแอปที่รันจริง `http://127.0.0.1:5000/` ด้วย **OpenCode Browser**
วันที่ 2026-11-24 · Engine **ngspice 47** · Model **QNPN generic teaching model**
(ไม่มี Starter Kit ของอาจารย์ในรีโป)

> **Playwright MCP: NOT RUN** — ไม่ถูก expose ในเซสชันนี้ จึงใช้ OpenCode Browser
> (navigate → snapshot → fill → submit → read values → screenshot) ตามที่ใบงานอนุญาต

## แมปกับ Rubric

| # | Rubric (คะแนน) | เกณฑ์หลักฐาน | ภาพที่ส่ง | สถานะ |
|---|---|---|---|---|
| 1 | ความต่อเนื่องจาก Lab 3 (1) | DC Bias 3 แบบยังทำงาน + Regression | `r1-lab3-fixed.png`, `r1-lab3-emitter.png`, `r1-lab3-divider.png`, `r5-b1-regression.png` | PASS |
| 2 | การเชื่อม ngspice (3) | `.op` สำเร็จ, adapter/error handling, อ่านผลจริงพร้อมแหล่งที่มา | `r2-dc-result.png`, `r2-dc-netlist-log.png`, `r2-invalid-re.png` | PASS |
| 3 | AC + Transient (2) | Bode + Waveform ข้อมูลจริง แกน/หน่วยถูก, ปรับ Source แล้วผลเปลี่ยน | `r3-ac-bode.png`, `r3-tran-default.png`, `r3-tran-source-changed.png` | PASS |
| 4 | UI และ Impeccable (2) | ใช้ Skill ตรวจ/ปรับ มีหลักฐานก่อน/หลัง ไม่กระทบผลคำนวณ | `r4-before-desktop.png`, `r4-after-desktop.png`, `r4-before-mobile.png`, `r4-after-mobile.png` + [critique](../lab04-impeccable-critique.md) | PASS |
| 5 | Browser Acceptance (1) | บันทึก B1–B8 จากผลรันจริง หรือระบุ NOT RUN ตรงไปตรงมา | `r5-b1-b8-summary.png` + `r5-b1…r5-b8` | PASS |
| 6 | GitHub + Reproducibility (1) | Commit, README, Steps to Run, หลักฐาน Validation | `r6-github-commit.png`, `r6-reproducibility.png` | PASS |

## ภาพด่วนที่แนะนำให้ส่ง

ถ้าส่งได้ไม่กี่ภาพ ให้ใช้ชุดนี้:

1. `r5-b1-b8-summary.png` — สรุป B1–B8 ทั้ง 8 ข้อ (อ่านจบในภาพเดียว)
2. `r2-dc-result.png` + `r2-dc-netlist-log.png` — DC `.op` และ log จริง
3. `r3-ac-bode.png` + `r3-tran-source-changed.png` — Bode และ waveform ที่เปลี่ยนตาม source
4. `r4-before-desktop.png` + `r4-after-desktop.png` — หลักฐาน Impeccable ก่อน/หลัง
5. `r6-github-commit.png` + `r6-reproducibility.png` — commit และ reproducibility

## ค่าสำคัญที่ใช้ตรวจ (คัดจากหน้าจริง)

| Case | ค่าที่เห็น |
|---|---|
| B1 Fixed | `VB 0.70 · VE 0.00 · VC 9.51 · VCE 9.51 V · IC 1.13 mA` |
| B1 Emitter | `VB 1.74 · VE 1.04 · VC 9.74 · VCE 8.71 V · IC 1.03 mA` |
| B1 Divider | `VB 1.94 · VE 1.24 · VC 9.29 · VCE 8.05 V · IC 1.23 mA` |
| B2 DC | `VB 1.95 · VE 1.29 · VC 9.19 · VCE 7.90 V · IC 1.28 mA` |
| B2 log | `0 1.949127e+00 1.289352e+00 9.189633e+00` |
| B3 RE=2k | DC `IC 695.83 µA`; AC `peak gain −1.14 dB` |
| B4 AC | `peak gain 4.86 dB (1.75×)`; phase `−3.14159 rad` ที่ความถี่สูง |
| B5 Tran | `508 samples · Vin pp 0.020 V · Vout pp 0.035 V · inverted` |
| B6 Source | `Vin pp 0.040 V · Vout pp 0.070 V`; `SIN(0 0.02 2000)` |
| B7 Invalid | `must be greater than zero`; `status: error`; 0 polyline |

## หมายเหตุความถูกต้อง

- ภาพไม่ได้แก้ย้อนหลังหรือวาดกราฟใหม่ — ทุกกราฟเป็น SVG ที่ parse จาก `run.log` ของ ngspice รันนั้น
- `r2-dc-netlist-log.png` แสดง netlist และ log `.op` จริงที่ตรงกับตารางบนหน้า
- `r4-before-*` คือก่อนแก้ P0 (ฟอร์มว่าง) และ `r4-after-*` คือหลังแก้ (มีค่าเริ่มต้น)
- ไม่มี image manipulation; มีเพียงการเลื่อน scroll ภายใน `<pre>` ของ log เพื่อให้เห็นบรรทัด `.op`
- ตารางเต็ม/ข้อจำกัด: [`docs/validation.md`](../../validation.md#lab-04--bjt-amplifier-simulator-v1-b1b8)
