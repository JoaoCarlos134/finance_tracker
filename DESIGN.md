# DESIGN.md — Finance Tracker visual system

Source of truth for the UI. Imported from the Claude Design project
"Finance Dashboard System" and implemented as CSS custom properties in
`frontend/src/styles/theme.css` — tokens there and this document must stay
in sync. The app brands itself "Finance Tracker" (the design mockup's
placeholder name "Ledger" is not used).

## Principles

1. **Legibility over decoration.** Every figure must be scannable at a
   glance; contrast, alignment and tabular numerals do more work than color
   or ornament.
2. **Numeric integrity.** All amounts and dates render in Archivo with
   `font-variant-numeric: tabular-nums` so digits align column-to-column and
   never jitter on update.
3. **Calm confidence.** One dominant muted color plus a single sharp accent
   keeps the eye on the data, not on the interface.
4. **Honest states.** Loading, error and empty states get the same care as
   the happy path — and the UI never fabricates data (e.g. the
   month-over-month trend hides itself below two months of history).

## Color

### Core

| Token | Hex | Role |
|---|---|---|
| `--color-ink-900` | `#12202E` | Dominant — nav, summary card, primary buttons, headings |
| `--color-accent` | `#C9752F` | Copper accent — active nav underline, brand mark, highlights |
| `--color-accent-dark` | `#A85E22` | Accent hover state |
| `--color-bg` | `#F6F3EE` | Warm paper page background |
| `--color-surface` | `#FFFFFF` | Card surfaces |

### Semantic

| Token | Hex | Role |
|---|---|---|
| `--color-success` | `#2F6844` | Positive amounts (on light surfaces) |
| `--color-success-soft` | `#7FBF98` | Positive amounts on dark (summary card) |
| `--color-warning` | `#A8791A` | Warnings |
| `--color-error` | `#B23B3B` | Negative amounts, error text |
| `--color-error-soft` | `#E0958A` | Negative amounts on dark |
| `--color-error-bg` | `#FBEAE8` | Error icon/row backgrounds |

### Neutrals

| Token | Hex | Role |
|---|---|---|
| `--color-ink-700` | `#3E4A56` | Body text on light |
| `--color-warm-600` | `#6B6255` | Secondary text |
| `--color-warm-500` | `#8A8072` | Metadata, captions |
| `--color-warm-300` | `#B8AD9C` | Disabled/placeholder text |
| `--color-warm-100` | `#EEE9DF` | Dividers, skeleton base, icon chips |
| `--color-border` / `--color-border-soft` | `#F0EBE1` / `#F5F1E9` | Card header rules / row rules |
| `--color-hover-row` | `#FBF6EE` | Table row hover tint |

## Typography

| Token | Font | Use |
|---|---|---|
| `--font-display` | Space Grotesk (500–700) | Titles, section labels, card headings |
| `--font-body` | IBM Plex Sans (400–600) | Body text, labels, descriptions |
| `--font-numeric` | Archivo (400–600) | Every amount, date, and ID — always with `tabular-nums` |

Scale (from the design spec): Display 44px · H1 32px · H2 20px ·
Body 15px · Small 13px · Numeric 18px. Loaded via Google Fonts in
`frontend/index.html`.

## Spacing

8px base grid, exposed as `--space-1` (8px) through `--space-8` (64px):
1x=8 · 2x=16 · 3x=24 · 4x=32 · 6x=48 · 8x=64. Radii in use: 8px (buttons,
icon chips), 14px (cards), 20px (pills).

## Component states — transaction table

Implemented in `frontend/src/components/TransactionsCard.jsx`:

- **Default:** grid rows (`1.6fr 1fr 0.8fr 0.9fr`), 15px vertical padding,
  `--color-border-soft` rule between rows; amounts right-aligned, colored by
  sign (`--color-error` / `--color-success`).
- **Hover:** row tinted `--color-hover-row`.
- **Loading:** skeleton bars using the `.skeleton` class (shimmer keyframe,
  1.4s linear infinite).
- **Error:** centered circle-! icon on `--color-error-bg`, one-line
  explanation, ink-900 Retry button.
- **Empty:** centered placeholder chip with a short instruction — no
  fake sample rows.
