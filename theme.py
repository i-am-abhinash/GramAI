"""Central modern Deep Space / Aurora theme tokens + global QSS stylesheet for GramAI."""

# Color tokens
BG          = "#080E1D"
PANEL       = "#142039"
PANEL_HI    = "#223453"
BORDER      = "#344B6C"
ACCENT      = "#8CF3D0"
ACCENT_HI   = "#D0FFEC"
PURPLE_GLOW = "#A58CFF"

SUCCESS     = "#10B981"
WARNING     = "#F59E0B"
DANGER      = "#EF4444"
TEXT        = "#F8FAFC"
TEXT_MUTED  = "#94A3B8"
TEXT_DIM    = "#64748B"

RADIUS = 24

APP_QSS = f"""
* {{
    font-family: "Inter", "Segoe UI Variable", "Segoe UI", sans-serif;
    color: {TEXT};
    outline: none;
    border: none;
}}
QWidget {{
    background-color: {BG};
}}

/* Headings */
QLabel#H1     {{ font-size: 36px; font-weight: 800; letter-spacing: -0.5px; color: {TEXT}; }}
QLabel#H2     {{ font-size: 26px; font-weight: 700; color: {TEXT}; }}
QLabel#H3     {{ font-size: 18px; font-weight: 600; color: {TEXT}; }}
QLabel#Muted  {{ color: {TEXT_MUTED}; font-size: 15px; }}
QLabel#Dim    {{ color: {TEXT_DIM};   font-size: 13px; }}
QLabel#Brand  {{ font-size: 30px; font-weight: 900; color: {ACCENT}; letter-spacing: -1px; }}

/* Top header bar */
QFrame#HeaderBar {{
    background-color: rgba(18, 26, 47, 0.85);
    border-bottom: 1px solid rgba(0, 229, 255, 0.15);
}}

/* Panels / cards */
QFrame#Card {{
    background-color: rgba(25, 39, 65, 0.91);
    border: 1px solid rgba(184, 216, 250, 0.19);
    border-radius: {RADIUS}px;
}}
QFrame#CardHover:hover {{
    background-color: {PANEL_HI};
    border: 1px solid {ACCENT};
}}
QFrame#Glass {{
    background-color: rgba(38, 55, 83, 0.72);
    border: 1px solid rgba(225,242,255,0.20);
    border-radius: {RADIUS}px;
}}

/* Buttons */
QPushButton {{
    background-color: {PANEL_HI};
    border: 1px solid {BORDER};
    border-radius: 18px;
    padding: 13px 25px;
    font-size: 15px;
    font-weight: 600;
    color: {TEXT};

}}
QPushButton:hover  {{ 
    background-color: rgba(28, 39, 66, 0.9); 
    border: 1px solid {ACCENT}; 
    color: {ACCENT};
}}
QPushButton:pressed{{ background-color: {PANEL}; }}

QPushButton#Primary {{
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {ACCENT}, stop:1 #61D9C4);
    border: none;
    color: #0A2C2B;
    font-weight: 700;
}}
QPushButton#Primary:hover  {{ 
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {ACCENT_HI}, stop:1 {ACCENT}); 
    color: #000000;
}}
QPushButton#Primary:pressed{{ background-color: #00B4CC; }}

QPushButton#Ghost {{
    background-color: transparent;
    border: 1px solid {BORDER};
    color: {TEXT_MUTED};
}}
QPushButton#Ghost:hover {{
    border-color: {TEXT};
    color: {TEXT};
}}

QPushButton#Danger {{
    background-color: rgba(239, 68, 68, 0.15); 
    border: 1px solid rgba(239, 68, 68, 0.4);
    color: {DANGER};
}}
QPushButton#Danger:hover {{
    background-color: {DANGER};
    color: #FFFFFF;
}}

QPushButton#IconBtn {{
    background-color: transparent;
    border: 1px solid {BORDER};
    border-radius: 22px;
    min-width: 44px; min-height: 44px;
    font-size: 18px;
}}
QPushButton#IconBtn:hover {{ 
    background-color: rgba(0, 229, 255, 0.1);
    border-color: {ACCENT}; 
    color: {ACCENT}; 
}}

/* Inputs */
QLineEdit, QTextEdit, QPlainTextEdit, QComboBox {{
    background-color: rgba(10, 15, 28, 0.6);
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 12px 16px;
    font-size: 15px;
    color: {TEXT};
    selection-background-color: {ACCENT};
    selection-color: #000000;
}}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
    border: 1px solid {ACCENT};
    background-color: rgba(18, 26, 47, 0.8);
}}

/* Sidebar */
QFrame#Sidebar {{
    background-color: rgba(14, 25, 46, 0.96);
    border-right: 1px solid rgba(198,227,255,0.16);
}}
QPushButton#NavItem {{
    background-color: transparent;
    border: none;
    border-radius: 18px;
    text-align: left;
    padding: 16px 22px;
    font-size: 15px;
    font-weight: 600;
    color: {TEXT_MUTED};
}}
QPushButton#NavItem:hover  {{ background-color: {PANEL_HI}; color: {TEXT}; }}
QPushButton#NavItem:checked{{ 
    background-color: rgba(0, 229, 255, 0.15); 
    color: {ACCENT}; 
    border: 1px solid rgba(140,243,208,0.28);
    border-radius: 18px;
}}

/* Tables */
QTableWidget, QTableView {{
    background-color: transparent;
    gridline-color: rgba(255,255,255,0.05);
    border: none;
    font-size: 14px;
}}
QHeaderView::section {{
    background-color: transparent;
    color: {TEXT_MUTED};
    padding: 14px 10px;
    border: none;
    border-bottom: 2px solid {BORDER};
    font-weight: 700;
    font-size: 13px;
    text-transform: uppercase;
}}
QTableWidget::item {{ padding: 12px 10px; border-bottom: 1px solid rgba(255,255,255,0.02); }}
QTableWidget::item:selected {{ background-color: rgba(0, 229, 255, 0.1); color: {ACCENT}; }}

/* Scrollbars */
QScrollBar:vertical {{
    background: transparent; width: 8px; margin: 4px;
}}
QScrollBar::handle:vertical {{
    background: {BORDER}; border-radius: 4px; min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{ background: {ACCENT}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

/* Status pills */
QLabel#PillOk {{
    background-color: rgba(16, 185, 129, 0.15); color: {SUCCESS};
    border: 1px solid rgba(16, 185, 129, 0.3);
    border-radius: 12px; padding: 4px 12px; font-size: 12px; font-weight: 700;
}}
QLabel#PillWarn {{
    background-color: rgba(245, 158, 11, 0.15); color: {WARNING};
    border: 1px solid rgba(245, 158, 11, 0.3);
    border-radius: 12px; padding: 4px 12px; font-size: 12px; font-weight: 700;
}}
QLabel#PillErr {{
    background-color: rgba(239, 68, 68, 0.15); color: {DANGER};
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: 12px; padding: 4px 12px; font-size: 12px; font-weight: 700;
}}
"""

# iOS-inspired additional styles; applied without altering backend or signal wiring.
APP_QSS += f"""
QToolTip {{ background: #223453; color: {TEXT}; border: 1px solid {BORDER}; border-radius: 8px; padding: 8px; }}
QPushButton:disabled {{ color: #71849F; background: #1C2941; }}
QPushButton#Primary:disabled {{ color: #71849F; background: #1C2941; }}
QFrame#Glass QLabel {{ background: transparent; }}
QFrame#Sidebar QLabel {{ background: transparent; }}
"""
