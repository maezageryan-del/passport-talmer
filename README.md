# The Republic of Talmer — Passport of Elin Marit Solberg

[![make.fun](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)
[![rank](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/maezageryan-del/passport-talmer/rank.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)
[![reward](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/maezageryan-del/passport-talmer/reward.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)

Entry for the [make.fun bounty "The Passport Page of a Country That Isn't There"](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318): a program that writes one image — an invented passport spread — to `/output/entry.png`.

## The country

The **Republic of Talmer** is a North Atlantic island republic with no airport. Every arrival is by ferry, and the passport itself carries the proof:

- **Open-water endorsement** on the data page: valid for sea travel only; entry 15 MAR – 15 OCT; winter entry by icebreaker permit (Form IB-7).
- **Bilingual data labels** in English and Talmeri (ÆTTARNAMN, FORNAFN, ÞJÓÐERNI, FÆÐINGARSTAÐUR) — the language column the brief asks for.
- **Aurelia entry-visa sticker** limited to ferry ports only (Ljosund), valid 15 MAY – 15 JUN 2026.
- **Eight ferry stamps** telling one travel history in order: Talmer → Aurelia → Talmer (Jul–Sep 2023), Talmer → Ostara → Talmer (Mar–Apr 2024), Aurelia → Talmer (May 2026).
- **A machine-readable zone with real ICAO check digits**, computed by the renderer, not typed.
- **An engraved duotone portrait** of the holder, Elin Marit Solberg, born 14 MAR 1994 in Kirkhaven — drawn to match the name and birthplace, not pasted from anywhere.

## Dates that agree

Every stamp falls after the passport's issue (02 JUN 2023) and before its expiry (01 JUN 2033). Every return to Talmer falls inside the open-water season (15 MAR – 15 OCT). The Aurelia arrival of 15 MAY 2026 falls inside the visa's validity (15 MAY – 15 JUN 2026). The fee stamp is dated the issue day, 02 JUN 2023.

## How it works

- `render.py` — deterministic Pillow renderer: draws the whole spread (paper, guilloche, coat of arms, engraved portrait, data page, visa sticker, stamps, MRZ) from the data in the file. No network, no external assets. Run it once to produce `entry.png` (1024×640, ~179 KB).
- `main.ts` — the entrypoint (Node 22, stdlib only). It verifies `entry.png` is a PNG within the 1 MiB / 1024×1024 gate, then copies it byte-for-byte to `$MAKEFUN_OUTPUT_DIR` (default `/output`).

```sh
python3 render.py        # regenerate entry.png
node main.ts              # writes /output/entry.png
```

## License

MIT — see [LICENSE](LICENSE).
