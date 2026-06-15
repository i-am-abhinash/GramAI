# GramAI — AI Powered Rural Assistance System

A modern, dark-themed PyQt6 **desktop application** UI designed for public kiosks
in rural areas. Built for villagers, elderly users, and first-time technology
users — large touch targets, minimal navigation, Telugu-friendly labels.

## Features

**Kiosk side**
- Animated, glowing microphone button ("Press and Speak")
- Telugu support indicator
- 4 quick-access cards (Schemes / Pension / Ration / Scholarships)
- Recent questions list with voice replay
- Bottom status bar (AI / Internet / Mic / Health)
- Full screen flow: **Home → Listening → Processing → Response**
  - Circular voice-wave visualisation
  - AI "thinking" orbit spinner
  - Question/Answer cards with Replay, Ask Again, Return Home

**Admin side**
- Secure-styled admin login screen
- Dark dashboard with sidebar (Dashboard, Schemes, FAQ, Unanswered,
  Logs, Settings)
- Stat widgets, most-asked questions list
- Unanswered Questions data table with status chips + Add Response
- Government Schemes management — card grid + detail table + search

## Setup

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install PyQt6
python main.py
```

Tested with Python 3.10+ and PyQt6 ≥ 6.5.

## Demo flow

1. App opens to the **Home** kiosk screen.
2. Tap the big mic → **Listening** screen (auto-advances after ~2.4 s).
3. → **Processing** screen (~2 s).
4. → **Response** screen with sample answer.
5. Top-left 🔐 icon opens **Admin Login**. Click *Sign In* (no real auth —
   demo) to enter the **Admin Dashboard**. Use the sidebar to navigate.
6. *Logout* returns to the kiosk.

> Auto-advance timings live in `app_window.py::_start_listen` — replace them
> with your real speech-to-text + LLM calls when integrating a backend.

## File layout

```
gramai/
├── main.py                  # entry point
├── app_window.py            # QMainWindow + screen routing
├── theme.py                 # color tokens + global QSS
├── widgets/
│   ├── header.py            # top header bar (logo, title, time, admin)
│   └── components.py        # MicButton, VoiceWaveCircle, ThinkingSpinner,
│                            # QuickAccessCard, StatusPill
├── screens/
│   ├── home.py
│   ├── listening.py
│   ├── processing.py
│   ├── response.py
│   └── admin_login.py
└── admin/
    ├── shell.py             # sidebar + stacked admin pages
    ├── dashboard.py
    ├── unanswered.py
    ├── schemes.py
    └── simple_pages.py      # FAQ / Logs / Settings placeholders
```

## Design tokens (theme.py)

| Token       | Value     |
|-------------|-----------|
| Background  | `#121212` |
| Panel       | `#1E1E1E` |
| Accent      | `#3B82F6` |
| Success     | `#22C55E` |
| Warning     | `#F59E0B` |
| Radius      | 16 px     |

All styling flows through `theme.APP_QSS` so you can re-skin globally in one
place.
