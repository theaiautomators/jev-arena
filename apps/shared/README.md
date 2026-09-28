# The AI Automators micro-app shell

Jev Arena and Support Lab both use `AppShell.tsx`. New React micro-apps should use this component instead of creating another header or navigation layout. It includes the original logo, locally bundled Poppins fonts, design tokens, header, navigation, content container, footer and presenter control. It makes no API requests.

## Layout contract

- Desktop: 76px sticky header, 240px labelled sidebar, 40px content gutters. Header shows the app name, current destination, optional status and presenter button.
- Compact desktop: navigation can collapse to a 76px icon rail; every item retains an accessible name and tooltip. The preference is saved per origin, with a session-only fallback if storage is unavailable.
- At 1150px: sidebar becomes 220px and gutters become 28px.
- At 850px: navigation becomes a horizontally scrollable strip below the header. The active destination scrolls into view; every destination remains available.
- At 580px: 64px header, compact robot mark and 18px gutters.
- Presenter: hide navigation and footer, retain brand, page identity and an explicit exit button. Escape also exits.

Use the shared `.page-heading` structure for the title, short context and page actions. Keep task-specific tabs, forms, charts, panels and state within the app. The shared stylesheet owns header/nav dimensions, active and focus states, heading rhythm, the palette and reduced-motion behaviour. Add new shell features here so every app receives the change.

## Minimal integration

Import app-specific styles **before** `AppShell` so the shared layout is the final authority. Adjust the relative import for the app's location.

```tsx
import { useState } from 'react';
import { Activity, Settings2 } from 'lucide-react';
import './styles.css';
import { AppShell, type AppNavigationItem } from '../../shared/AppShell';

type Page = 'overview' | 'settings';
const navigation: AppNavigationItem<Page>[] = [
  { id: 'overview', label: 'Overview', icon: Activity },
  { id: 'settings', label: 'Settings', icon: Settings2 },
];

export default function App() {
  const [page, setPage] = useState<Page>('overview');
  const [presenter, setPresenter] = useState(false);
  return (
    <AppShell
      appName="Example Lab"
      description="A short workspace description"
      navigation={navigation}
      activePage={page}
      onNavigate={setPage}
      presenter={presenter}
      onPresenterChange={setPresenter}
      status="Local workspace"
      footerNote="Data saved locally"
    >
      <div className="page-heading">
        <div>
          <p className="eyebrow">OVERVIEW</p>
          <h1>Your workspace.</h1>
          <p>One sentence explaining this screen.</p>
        </div>
      </div>
      {/* Render the active page's working surface here. */}
    </AppShell>
  );
}
```

`statusTone="success"` adds a green status dot. `sidebarFooter` accepts app-specific context or reference links. `className` supports page-specific styling. Applications still own routing and presenter state so workflow actions can open a page directly in presenter mode.

The component is router-independent. The logo is imported inline so Arena's standalone exported HTML reports remain self-contained. Vite-based apps need the usual `vite/client` type reference to resolve the asset and CSS imports.

## Verification

Build both consumers with `npm run build` and `npm run lab:build`. Check navigation, collapsed mode, presenter entry/exit and narrow layouts in both apps. Avoid starting or stopping model runs while testing the shell.

When adapting this to another repository, copy the entire `apps/shared` directory and install the existing React, `lucide-react` and `@fontsource/poppins` dependencies. Within this repository, import the shared source directly to keep a single implementation.
