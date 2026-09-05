<div align="center">

# 🌾 GramAI

### AI-Powered Rural Assistance System

<p>
A voice-first desktop kiosk interface designed to make essential government
information more accessible to rural communities, elderly users, and
first-time technology users.
</p>

<br>

<a href="https://github.com/i-am-abhinash/GramAI">
  <img src="https://img.shields.io/badge/GitHub-GramAI-181717?style=for-the-badge&logo=github" alt="GitHub">
</a>

<img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">

<img src="https://img.shields.io/badge/PyQt6-Desktop%20Application-41CD52?style=for-the-badge&logo=qt&logoColor=white" alt="PyQt6">

<img src="https://img.shields.io/badge/Status-Prototype-orange?style=for-the-badge" alt="Status">

<br><br>

<img src="https://img.shields.io/badge/Voice--First%20UX-Enabled-6366F1?style=flat-square" alt="Voice First UX">
<img src="https://img.shields.io/badge/Telugu-Friendly-Enabled-0EA5E9?style=flat-square" alt="Telugu Friendly">
<img src="https://img.shields.io/badge/Rural%20Accessibility-Focused-16A34A?style=flat-square" alt="Rural Accessibility">

</div>

---

## 🌍 Overview

**GramAI** is an AI-powered rural assistance system designed around a simple
idea:

> **Government information should be accessible to everyone, regardless of
> their technical experience.**

The project explores a **voice-first kiosk experience** for rural communities,
elderly users, and people who may be unfamiliar with conventional digital
interfaces.

The current implementation is a **PyQt6 desktop application prototype**
demonstrating the kiosk experience, interaction flow, and administration
interface.

---

## 🎯 The Problem

Accessing government information can be difficult when users face:

- Complex digital interfaces
- Limited technical experience
- Language barriers
- Difficulty navigating large websites
- Lack of familiarity with conventional search interfaces

For many users, typing a query and navigating through multiple pages is not
the most natural interaction model.

GramAI explores a different approach:

```text
User
 |
 |  Speaks / Interacts
 v
+----------------------+
|     GramAI Kiosk     |
+----------+-----------+
           |
           v
+----------------------+
| Understand Question  |
+----------+-----------+
           |
           v
+----------------------+
| Find Relevant        |
| Government           |
| Information          |
+----------+-----------+
           |
           v
+----------------------+
| Simple Response      |
+----------+-----------+
           |
           v
        User
```

---

## 💡 Project Vision

GramAI is designed around **simplicity, accessibility, and voice-first
interaction**.

The long-term vision is to provide a kiosk where a person can ask questions
about topics such as:

- 🏛️ Government schemes
- 👴 Pension
- 🍚 Ration
- 🎓 Scholarships
- 📋 Public services
- ❓ Frequently asked questions

The interface is intentionally designed to minimize navigation complexity and
make the primary interaction as simple as possible.

---

## ✨ Key Features

<table>
<tr>

<td width="50%" valign="top">

### 🎙️ Voice-First Interaction

A large central microphone interaction provides a simple starting point for
users who may find typing difficult or inconvenient.

</td>

<td width="50%" valign="top">

### 🌐 Telugu-Friendly Interface

The interface includes Telugu-friendly labels and visual indicators to support
more accessible interaction for regional users.

</td>

</tr>

<tr>

<td width="50%" valign="top">

### 👴 Accessibility Focus

Designed with:

- Large touch targets
- Minimal navigation
- Clear visual hierarchy
- Simple interaction flows

</td>

<td width="50%" valign="top">

### 🏛️ Government Information

The kiosk interface provides quick-access areas for:

- Schemes
- Pension
- Ration
- Scholarships

</td>

</tr>

<tr>

<td width="50%" valign="top">

### 📊 Admin Dashboard

Includes an administration interface with:

- Dashboard
- Schemes
- FAQ
- Unanswered questions
- Logs
- Settings

</td>

<td width="50%" valign="top">

### 🔄 Guided Interaction Flow

The kiosk demonstrates a clear progression:

**Home → Listening → Processing → Response**

</td>

</tr>
</table>

---

## 🎙️ Kiosk Experience

The primary user experience is designed to be extremely simple.

<div align="center">

```text
+-------------------+
|       HOME        |
|                   |
|   🎙️ SPEAK        |
|                   |
| Schemes           |
| Pension           |
| Ration            |
| Scholarships      |
+---------+---------+
          |
          v
+-------------------+
|     LISTENING     |
|                   |
|   Voice Wave      |
|                   |
|   Listening...    |
+---------+---------+
          |
          v
+-------------------+
|    PROCESSING     |
|                   |
|    AI Thinking    |
|                   |
|   Processing...   |
+---------+---------+
          |
          v
+-------------------+
|     RESPONSE      |
|                   |
|    Answer         |
|                   |
| Replay | Ask Again|
|        | Home     |
+-------------------+
```

</div>

---

## 🧑‍💼 Admin Experience

GramAI also includes an administration interface for managing and reviewing
the information presented through the kiosk.

### Admin Dashboard

The dashboard provides areas for:

| Section | Purpose |
| --- | --- |
| 📊 Dashboard | Overview and statistics |
| 🏛️ Schemes | Government scheme management |
| ❓ FAQ | Frequently asked questions |
| ⚠️ Unanswered | Questions requiring attention |
| 📋 Logs | Activity and interaction records |
| ⚙️ Settings | Application configuration |

The current authentication screen is **demo-only** and does not implement
production authentication. 

---

## 🧠 System Concept

The intended architecture separates the user interface from the future AI and
data-processing layers.

```text
                    USER
                      |
                      v
             +----------------+
             |  GramAI Kiosk  |
             |    PyQt6 UI    |
             +-------+--------+
                     |
                     v
             +----------------+
             | Speech-to-Text |
             +-------+--------+
                     |
                     v
             +----------------+
             | Question /     |
             | Intent Parsing |
             +-------+--------+
                     |
                     v
             +----------------+
             | Information    |
             | Retrieval      |
             +-------+--------+
                     |
                     v
             +----------------+
             | AI / LLM Layer |
             +-------+--------+
                     |
                     v
             +----------------+
             | Response       |
             | Generation     |
             +-------+--------+
                     |
                     v
             +----------------+
             | Kiosk Response |
             +----------------+
```

> The current repository primarily implements the **desktop UI and prototype
> interaction flow**. The speech-to-text and LLM integration shown above
> represent the intended backend direction rather than claiming those systems
> are already fully integrated. 

---

## 🏗️ Application Architecture

```text
+------------------------------------------------------+
|                    GRAMAI APPLICATION                |
+------------------------------------------------------+
|                                                      |
|                    PyQt6 Desktop UI                  |
|                                                      |
|  +-------------+  +-------------+  +-------------+   |
|  |    Kiosk    |  | Interaction |  |    Admin    |   |
|  |   Screens   |  |   Flow      |  |  Dashboard  |   |
|  +-------------+  +-------------+  +-------------+   |
|                                                      |
+------------------------------------------------------+
|                                                      |
|                  Future AI Services                  |
|                                                      |
| Speech Recognition | NLP | Retrieval | LLM | TTS     |
|                                                      |
+------------------------------------------------------+
```

---

## 🛠️ Technology Stack

<table>
<tr>
<th>Technology</th>
<th>Purpose</th>
</tr>

<tr>
<td><b>Python</b></td>
<td>Application development</td>
</tr>

<tr>
<td><b>PyQt6</b></td>
<td>Desktop graphical user interface</td>
</tr>

<tr>
<td><b>Qt Style Sheets</b></td>
<td>Global application styling</td>
</tr>

<tr>
<td><b>Modular Python Components</b></td>
<td>Screens, widgets, administration and application routing</td>
</tr>
</table>

---

## 🎨 Design System

The application's styling is centralized through the project theme system.

| Token | Value |
| --- | --- |
| Background | `#121212` |
| Panel | `#1E1E1E` |
| Accent | `#3B82F6` |
| Success | `#22C55E` |
| Warning | `#F59E0B` |
| Border Radius | `16px` |

Centralizing the visual tokens allows the application to be re-skinned from a
single theme definition. 

---

## 📂 Project Structure

```text
gramai/
│
├── main.py
│   └── Application entry point
│
├── app_window.py
│   └── Main window and screen routing
│
├── theme.py
│   └── Color tokens and global QSS
│
├── widgets/
│   ├── header.py
│   │   └── Header bar
│   │
│   └── components.py
│       ├── MicButton
│       ├── VoiceWaveCircle
│       ├── ThinkingSpinner
│       ├── QuickAccessCard
│       └── StatusPill
│
├── screens/
│   ├── home.py
│   ├── listening.py
│   ├── processing.py
│   ├── response.py
│   └── admin_login.py
│
└── admin/
    ├── shell.py
    ├── dashboard.py
    ├── unanswered.py
    ├── schemes.py
    └── simple_pages.py
```

The structure separates the kiosk screens, reusable widgets, administration
interface, and application-level routing. 

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or newer
- PyQt6

### 1. Clone the repository

```bash
git clone https://github.com/i-am-abhinash/GramAI.git
cd GramAI
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment

#### Windows

```bash
.venv\Scripts\activate
```

#### macOS / Linux

```bash
source .venv/bin/activate
```

### 4. Install PyQt6

```bash
pip install PyQt6
```

### 5. Run GramAI

```bash
python main.py
```

The current project README specifies Python 3.10+ and PyQt6 6.5 or newer. 

---

## 🧪 Current Demo Flow

The current prototype demonstrates the following flow:

```text
Home
  ↓
Listening
  ↓
Processing
  ↓
Response
```

The prototype automatically advances through the listening and processing
screens and displays a sample response.

The current demo timings are implemented in
`app_window.py::_start_listen`. 

---

## 🚧 Current Status

<div align="center">

### Prototype / Active Development

</div>

The current version focuses primarily on the **user experience and desktop
application architecture**.

### Implemented

- ✅ PyQt6 desktop application
- ✅ Kiosk home screen
- ✅ Large microphone interaction
- ✅ Listening screen
- ✅ Processing screen
- ✅ Response screen
- ✅ Voice-wave visualisation
- ✅ AI-thinking animation
- ✅ Quick-access categories
- ✅ Admin login interface
- ✅ Admin dashboard
- ✅ Government scheme management interface
- ✅ Unanswered-question interface
- ✅ Dark application theme

### Integration Direction

- 🔄 Speech-to-text
- 🔄 Real AI / LLM backend
- 🔄 Live government information
- 🔄 Production authentication
- 🔄 Production deployment

The current repository explicitly describes the speech-to-text and LLM calls as
future integration points, so these are intentionally marked as development
direction rather than completed features. 

---

## 🔮 Future Roadmap

### Phase 1 — AI Integration

- [ ] Speech-to-text integration
- [ ] Natural language understanding
- [ ] Intent classification
- [ ] Question processing pipeline

### Phase 2 — Knowledge Layer

- [ ] Government scheme database
- [ ] Search and retrieval
- [ ] FAQ knowledge base
- [ ] Regional information support

### Phase 3 — AI Responses

- [ ] LLM integration
- [ ] Context-aware responses
- [ ] Telugu response generation
- [ ] Text-to-speech

### Phase 4 — Production Kiosk

- [ ] Secure authentication
- [ ] Hardware microphone integration
- [ ] Offline / low-connectivity support
- [ ] Deployment-ready kiosk mode
- [ ] Usage analytics
- [ ] Monitoring and maintenance

---

## 🌱 Why GramAI?

GramAI explores a simple but important principle:

> **Technology should adapt to the user, not force the user to adapt to technology.**

For users who may not be comfortable with conventional applications, a
voice-first kiosk can provide a more natural interaction model.

The project therefore combines:

**Accessibility + Voice Interaction + AI + Public Information**

into a single application concept.

---

## 👨‍💻 Author

<div align="center">

### Gowri Abhinash

**AI/ML Engineering Student & Software Developer**

<br>

<a href="https://github.com/i-am-abhinash">
  <img src="https://img.shields.io/badge/GitHub-i--am--abhinash-181717?style=for-the-badge&logo=github" alt="GitHub">
</a>

<a href="https://www.linkedin.com/in/gowri-abhinash-modugumudi-a7a1aa2b">
  <img src="https://img.shields.io/badge/LinkedIn-Gowri%20Abhinash-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn">
</a>

</div>

---

<div align="center">

### 🌾 GramAI

**Making essential information more accessible through simple technology.**

<br>

⭐ Explore the repository and follow the project's development.

</div>
