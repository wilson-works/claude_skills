# shadcn/ui Theming & Customization

Theme configuration, CSS variables, dark mode, and component customization.

## Dark Mode Setup

### Next.js App Router

**1. Install next-themes:**
```bash
npm install next-themes
```

**2. Create theme provider:**
```tsx
// components/theme-provider.tsx
"use client"

import * as React from "react"
import { ThemeProvider as NextThemesProvider } from "next-themes"

export function ThemeProvider({
  children,
  ...props
}: React.ComponentProps<typeof NextThemesProvider>) {
  return <NextThemesProvider {...props}>{children}</NextThemesProvider>
}
```

**3. Wrap app:**
```tsx
// app/layout.tsx
import { ThemeProvider } from "@/components/theme-provider"

export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
}
```

**4. Theme toggle component:**
```tsx
import { Moon, Sun } from "lucide-react"
import { useTheme } from "next-themes"
import { Button } from "@/components/ui/button"

export function ThemeToggle() {
  const { setTheme, theme } = useTheme()

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={() => setTheme(theme === "light" ? "dark" : "light")}
    >
      <Sun className="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
      <Moon className="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
      <span className="sr-only">Toggle theme</span>
    </Button>
  )
}
```

### Vite / Other Frameworks

Use similar approach with next-themes or implement custom solution:

```javascript
// Store preference
function toggleDarkMode() {
  const isDark = document.documentElement.classList.toggle('dark')
  localStorage.setItem('theme', isDark ? 'dark' : 'light')
}

// Initialize on load
if (localStorage.theme === 'dark' ||
    (!('theme' in localStorage) &&
     window.matchMedia('(prefers-color-scheme: dark)').matches)) {
  document.documentElement.classList.add('dark')
}
```

## CSS Variable System

shadcn/ui themes with CSS variables in your global stylesheet (`globals.css` / `index.css`). In Tailwind v4 each variable holds a complete colour, OKLCH by default, and `@theme inline` maps it to a utility (next section). Pattern after shadcn-ui/ui (MIT): the values below are its `neutral` base, trimmed; the full set adds `--chart-1` to `--chart-5` and the `--sidebar-*` tokens.

```css
@import "tailwindcss";

@custom-variant dark (&:is(.dark *));

:root {
  --radius: 0.625rem;
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0 0);
  --card: oklch(1 0 0);
  --card-foreground: oklch(0.145 0 0);
  --popover: oklch(1 0 0);
  --popover-foreground: oklch(0.145 0 0);
  --primary: oklch(0.205 0 0);
  --primary-foreground: oklch(0.985 0 0);
  --secondary: oklch(0.97 0 0);
  --secondary-foreground: oklch(0.205 0 0);
  --muted: oklch(0.97 0 0);
  --muted-foreground: oklch(0.556 0 0);
  --accent: oklch(0.97 0 0);
  --accent-foreground: oklch(0.205 0 0);
  --destructive: oklch(0.577 0.245 27.325);
  --border: oklch(0.922 0 0);
  --input: oklch(0.922 0 0);
  --ring: oklch(0.708 0 0);
}

.dark {
  --background: oklch(0.145 0 0);
  --foreground: oklch(0.985 0 0);
  --card: oklch(0.205 0 0);
  --card-foreground: oklch(0.985 0 0);
  --popover: oklch(0.205 0 0);
  --popover-foreground: oklch(0.985 0 0);
  --primary: oklch(0.922 0 0);
  --primary-foreground: oklch(0.205 0 0);
  --secondary: oklch(0.269 0 0);
  --secondary-foreground: oklch(0.985 0 0);
  --muted: oklch(0.269 0 0);
  --muted-foreground: oklch(0.708 0 0);
  --accent: oklch(0.269 0 0);
  --accent-foreground: oklch(0.985 0 0);
  --destructive: oklch(0.704 0.191 22.216);
  --border: oklch(1 0 0 / 10%);
  --input: oklch(1 0 0 / 15%);
  --ring: oklch(0.556 0 0);
}
```

`@custom-variant dark` makes `dark:` utilities follow a `.dark` class on an ancestor (the `attribute="class"` setup above). Without it, `dark:` follows the operating-system setting.

### Color Format

Each variable holds a full colour, so utilities read it directly and opacity modifiers work: `bg-primary`, `bg-primary/50`, `border-border`. OKLCH is `oklch(lightness chroma hue)`: lightness 0–1, chroma 0 for grey and up for colour, hue in degrees. Lightness steps look even to the eye, which makes a scale or a dark variant easier to tune than HSL.

A Tailwind v3 project stores bare HSL channels (`--primary: 222.2 47.4% 11.2%`) and wraps them as `hsl(var(--primary))` in `tailwind.config`. Keep one model per project; the upgrade path is shadcn's Tailwind v4 guide (ui.shadcn.com/docs/tailwind-v4).

## Tailwind Mapping (`@theme inline`)

Tailwind v4 needs no `tailwind.config` theme (leave `tailwind.config` blank in `components.json`). Map the variables in CSS:

```css
@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-card: var(--card);
  --color-card-foreground: var(--card-foreground);
  --color-popover: var(--popover);
  --color-popover-foreground: var(--popover-foreground);
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
  --color-secondary: var(--secondary);
  --color-secondary-foreground: var(--secondary-foreground);
  --color-muted: var(--muted);
  --color-muted-foreground: var(--muted-foreground);
  --color-accent: var(--accent);
  --color-accent-foreground: var(--accent-foreground);
  --color-destructive: var(--destructive);
  --color-border: var(--border);
  --color-input: var(--input);
  --color-ring: var(--ring);
  --radius-sm: calc(var(--radius) * 0.6);
  --radius-md: calc(var(--radius) * 0.8);
  --radius-lg: var(--radius);
  --radius-xl: calc(var(--radius) * 1.4);
}
```

`inline` puts `var(--primary)` itself into each utility, so a `.dark` or `[data-theme]` override on any element switches every utility inside it.

## Color Customization

### Method 1: Edit the Variables

Change `:root` and `.dark` together; a dark value is designed, not inverted:

```css
:root {
  --primary: oklch(0.45 0.11 160);   /* deep green */
  --primary-foreground: oklch(0.985 0 0);
}

.dark {
  --primary: oklch(0.72 0.12 160);   /* lighter on a dark background */
  --primary-foreground: oklch(0.205 0 0);
}
```

Then re-check each role pair's contrast in both themes.

### Method 2: Generate a Theme

- **shadcn Create** (ui.shadcn.com/create): pick base colour, radius, fonts and style, then `npx shadcn@latest apply --preset <code> --only theme`.
- **tweakcn** (tweakcn.com, Apache-2.0, free editor): export the Tailwind v4 variables and paste them over yours. Its `shadcn add <url>` command installs a third-party registry item: run `npx shadcn@latest view <url>` first.

### Method 3: Multiple Themes

Scope overrides with a data attribute:

```css
[data-theme="forest"] {
  --primary: oklch(0.45 0.11 160);
  --primary-foreground: oklch(0.985 0 0);
}

[data-theme="ember"] {
  --primary: oklch(0.7 0.16 50);
  --primary-foreground: oklch(0.205 0 0);
}
```

Apply theme:
```tsx
<div data-theme="forest">
  <Button>Forest theme</Button>
</div>
```

### Adding a Color

Define it in `:root` and `.dark`, then expose it in `@theme inline`:

```css
:root {
  --warning: oklch(0.84 0.16 84);
  --warning-foreground: oklch(0.205 0 0);
}

.dark {
  --warning: oklch(0.41 0.11 46);
  --warning-foreground: oklch(0.985 0 0);
}

@theme inline {
  --color-warning: var(--warning);
  --color-warning-foreground: var(--warning-foreground);
}
```

`bg-warning text-warning-foreground` now works.

## Component Customization

Components live in your codebase - modify directly.

### Customize Variants

```tsx
// components/ui/button.tsx
const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 rounded-md text-sm font-medium transition-colors",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive: "bg-destructive text-white hover:bg-destructive/90",
        outline: "border bg-background hover:bg-accent hover:text-accent-foreground",
        // Add a variant from a token you defined (see Adding a Color)
        warning: "bg-warning text-warning-foreground hover:bg-warning/90",
      },
      size: {
        default: "h-9 px-4 py-2",
        sm: "h-8 rounded-md px-3",
        lg: "h-10 rounded-md px-6",
        // Add custom size
        xl: "h-12 rounded-md px-8 text-base",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)
```

Usage:
```tsx
<Button variant="warning" size="xl">Review 3 items</Button>
```

### Customize Styles

Current components are plain functions (no `forwardRef`) that carry a `data-slot` attribute. Edit the class list:

```tsx
// components/ui/card.tsx
function Card({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="card"
      className={cn("rounded-xl border bg-card text-card-foreground shadow-sm", className)}
      {...props}
    />
  )
}
```

### Override with className

Pass classes for a one-off, using tokens rather than raw colours:

```tsx
<Card className="bg-muted/50 shadow-none">
  Quiet card
</Card>
```

## Base Color Presets

`npx shadcn@latest init` asks for a base colour: Neutral, Stone, Zinc, Mauve, Olive, Mist or Taupe (`tailwind.baseColor` in `components.json`). It can't be changed after init; edit the variables or apply a preset instead.

## Style

`new-york` is the style; the older `default` style is deprecated. Set at `init` in `components.json` (it can't be changed afterwards):

```json
{
  "style": "new-york",
  "tailwind": {
    "config": "",
    "css": "app/globals.css",
    "baseColor": "neutral",
    "cssVariables": true
  }
}
```

## Radius Customization

One variable drives the scale; `@theme inline` derives `rounded-sm` to `rounded-xl` (and up) from it:

```css
:root {
  --radius: 0.625rem;  /* default */
  /* --radius: 0rem;   sharp corners */
  /* --radius: 1rem;   rounded */
}
```

## Best Practices

1. **Use CSS Variables**: Enables runtime theme switching
2. **Pair Every Fill with Its Foreground**: `primary` / `primary-foreground`, and so on
3. **Design Dark Mode**: Set `.dark` values on purpose, then test both themes
4. **Semantic Naming**: Use `destructive` not `red`, `muted` not `gray`
5. **Accessibility**: Check contrast per role pair, in both themes (WCAG AA minimum)
6. **Component Overrides**: Use `className` prop for one-off customization
7. **Extract Patterns**: Create custom variants for repeated customizations
8. **Not Default**: Change base colour, radius, fonts and shadows before shipping (Method 2)
