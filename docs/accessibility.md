# Accessibility

What the PropSense panel offers, and what was tested. The panel runs inside Home Assistant, so it uses Home Assistant's theme and form components.

## Offered

On the Settings tab, under Display. The choices apply to one browser and are remembered there.

| Option | Behaviour |
|---|---|
| Text size | Small, Default, Large or Largest (90%, 100%, 115%, 130%). |
| High contrast | Stronger borders and full-strength secondary text. |
| Reduce motion | Starts from the system setting until you change it. |

Light and dark follow your Home Assistant theme, which you choose in your profile. The panel has no theme switch of its own. It also does not read the system's contrast or forced-colours settings.

Other measures: a visible focus ring on every control, controls at least 44 pixels high on touch screens, a text label next to every status colour, and an alert role on error messages.

## Tested

Checked by hand in the browser built into the Claude desktop app (Chromium), against Home Assistant 2026.10 beta with demo entities. A script measured the panel's own elements.

- **Widths:** 320, 390, 640 by 400 and 768 by 900 pixels, and 1280 pixels, each with the Largest text size. The Rules tab, the rule editor (two rules, one with state conditions), Status, Explain and Settings had no element past the right edge and no sideways scrolling. The 640 pixel width stands in for 200% zoom on a 1280 pixel laptop and is also a short, landscape-shaped screen. Real browser zoom was not used.
- **Light and dark:** both Home Assistant themes were used across those widths, not every theme at every width.
- **Touch targets:** at 320, 390 and 640 pixels, with touch emulation, the panel's buttons, text inputs, selects and summaries were at least 44 pixels high. Checkboxes are 24 pixels inside a clickable label, and were not measured.
- **Display options:** Largest raises the panel's text from 14 to 18.2 pixels and is remembered after a reload. High contrast and Reduce motion set their styles, and the choices are saved.
- **Keyboard focus:** a focus ring showed while tabbing across the tabs.

These checks found three problems, now fixed. The text size option changed only the title. At 320 pixels the rule buttons and the editor ran past the edge. High contrast gave every tab the same underline, so only colour marked the current one.

## Not tested (VERIFY)

- Completing a whole task with the keyboard only.
- A screen reader, a physical phone, real browser zoom, and browsers other than Chromium.
- Contrast ratios. Colours come from Home Assistant's theme, and the category accents on rule cards are decorative and always paired with a text label.
- Home Assistant's own form fields and chips, which do not follow the text size option as far as the screenshots show. They were not measured.
- There is no automated viewport test.
