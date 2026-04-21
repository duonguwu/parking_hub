```markdown
# Design System Strategy: The Technical Schematic
 
## 1. Overview & Creative North Star
This design system is built on the Creative North Star of **"The Technical Schematic."** Moving away from the cluttered, "bubble-gum" aesthetic common in consumer apps, this system treats car care coordination as a high-precision architectural task. 
 
The aesthetic is a **Pastel Blue Blueprint**: it combines the clinical precision of an engineering drawing with the soft, approachable nature of a premium concierge service. By utilizing high-contrast typography scales, intentional asymmetry, and a strict adherence to flat, bordered geometry, we create a "Blueprint" that feels both expertly organized and incredibly light. We eschew shadows and gradients entirely, relying on the structural integrity of 1px lines and expansive whitespace to define "premium."
 
## 2. Colors: The Blueprint Palette
The palette is rooted in technical clarity. The primary blue is not just a brand color; it is a structural signifier.
 
*   **Primary (`primary_container` - #93C5FD):** Use this for primary actions and "active" blueprint states. It represents the "ink" of the schematic.
*   **Background (`background` - #F8FAFC):** An off-white canvas that reduces eye strain and distinguishes the app from standard "web white."
*   **Surface (`surface_container_lowest` - #FFFFFF):** Reserved for the floating sheets/cards that contain actionable data.
*   **Accent (`tertiary_fixed` - #8CF5E4):** Used sparingly for "system healthy" states, success confirmations, or secondary technical highlights.
 
### The "Precision Line" Rule
In this system, 1px solid borders (`outline_variant` - #E2E8F0) are the primary tool for hierarchy. While standard modern UI often relies on shadows, we use the "Blueprint Line" to define space. 
*   **Nesting:** To create depth without shadows, nest `surface` containers. A white card on a slightly grey background, framed by a 1px border, creates a "layered paper" effect.
*   **Intentional Asymmetry:** Break the grid by allowing certain borders to extend to the edge of the viewport while others remain contained, mimicking a technical drawing that is still "in progress."
 
## 3. Typography: Technical Editorial
We use **Inter** for its neutral, high-legibility "Helvetica-style" bones. To achieve a high-end editorial feel, we utilize extreme scale contrast.
 
*   **Display-LG (3.5rem):** Used for "hero" metrics or vehicle names. Should feel architectural.
*   **Headline-SM (1.5rem):** For section headers. Always paired with generous 32px+ top padding.
*   **Label-SM (0.6875rem):** For technical data (e.g., VIN numbers, timestamps, part IDs). Use all-caps with increased letter-spacing (0.05em) to mimic blueprint annotations.
 
The hierarchy communicates authority through "The Technical Annotation" style—pairing a very large number (Display-LG) with a very small, precise label (Label-SM).
 
## 4. Elevation & Depth: Flat Structuralism
Since box-shadows and gradients are prohibited, depth is achieved through **Tonal Layering and Line Geometry.**
 
*   **The Layering Principle:** Treat the UI as a series of stacked vellum sheets. Use the `surface_container` tiers to create subtle shifts in the "floor" of the application.
*   **The "Ghost" Boundary:** For secondary information, use the `outline_variant` at 50% opacity. This creates a hierarchy of lines—some are "structural" (100% opacity) and some are "guides" (50% opacity).
*   **Radius Dynamics:** Use the `xl` (3rem/Pill) radius for primary interaction points (Buttons) and `lg` (2rem/24px) for informational containers (Cards). This differentiation tells the user: "Rounder means more interactive."
 
## 5. Components
 
### Buttons
*   **Primary:** Pill-shaped (`full` radius), `primary_container` background, 1px `outline` border. No shadow.
*   **Secondary:** Pill-shaped, `surface` background, 1px `outline` border, `primary` text.
*   **Interaction:** On hover, the 1px border should increase to 1.5px or shift to the `primary` color to provide feedback without depth effects.
 
### Cards & Containers
*   **Rules:** Always 1px solid border (`#E2E8F0`). Always `lg` (24px) border-radius.
*   **Spacing:** Interior padding must be a minimum of 24px, with 32px gaps between cards to maintain the "room to breathe."
*   **No Dividers:** Never use horizontal rules within a card. Use whitespace or a subtle background shift to `surface_container_low` to separate content blocks.
 
### Input Fields
*   **Style:** `surface_container_lowest` background with a 1px `outline` border. 
*   **Focus State:** The border transitions from `#E2E8F0` to the `primary` blue (#93C5FD). The radius should be `md` (1.5rem) to differentiate inputs from pill-shaped buttons.
 
### Schematic Timeline (Context Specific)
A custom component for car care coordination. A vertical 1px line connects `tertiary_fixed` dots, representing the service history. This reinforces the "Blueprint" aesthetic.
 
## 6. Do's and Don'ts
 
### Do:
*   **Do** use 32px, 48px, or even 64px gaps to create an "Editorial" sense of luxury.
*   **Do** use the 1px border as a design feature—let it define the character of the site.
*   **Do** align text-heavy technical data in a grid that mimics a spreadsheet or ledger.
 
### Don't:
*   **Don't** use a shadow, even a soft one. It breaks the "Schematic" metaphor.
*   **Don't** use gradients to "fix" a flat area. If an area feels empty, solve it with better typography or more whitespace.
*   **Don't** crowd the edges. Every element should feel like it has been "placed" with surgical intent on the canvas.
*   **Don't** use high-contrast black for text. Use `on_surface` (#191C1E) to keep the "Ink on Paper" feel soft.
 
***
 
**Director's Final Note:**
Remember, luxury in a digital product isn't about how many effects you can add; it’s about the confidence of your layout. By stripping away shadows and gradients, we are leaning into the "naked" beauty of the geometry. Keep the lines thin, the corners round, and the whitespace vast.```