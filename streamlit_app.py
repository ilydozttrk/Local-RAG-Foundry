import streamlit as st


APP_TITLE = "Local RAG AI Assistant"
APP_ICON = "🤖"

THEMES = {
    "Dark": {
        "background": "#0B1120",
        "surface": "#111827",
        "surface_alt": "#1E293B",
        "primary": "#38BDF8",
        "primary_hover": "#0EA5E9",
        "text": "#F8FAFC",
        "muted_text": "#94A3B8",
        "border": "#334155",
        "user_message": "#172554",
        "assistant_message": "#111827",
        "input_background": "#1E293B",
        "shadow": "rgba(0, 0, 0, 0.30)",
        "success": "#22C55E",
    },
    "Light": {
        "background": "#F1F5F9",
        "surface": "#FFFFFF",
        "surface_alt": "#E2E8F0",
        "primary": "#2563EB",
        "primary_hover": "#1D4ED8",
        "text": "#0F172A",
        "muted_text": "#475569",
        "border": "#CBD5E1",
        "user_message": "#DBEAFE",
        "assistant_message": "#FFFFFF",
        "input_background": "#FFFFFF",
        "shadow": "rgba(15, 23, 42, 0.10)",
        "success": "#16A34A",
    },
}


def configure_page() -> None:
    """Configure the Streamlit application page."""

    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        layout="wide",
        initial_sidebar_state="expanded",
    )


def initialize_session_state() -> None:
    """Initialize values stored in the Streamlit session."""

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "theme" not in st.session_state:
        st.session_state.theme = "Dark"


def apply_custom_theme() -> None:
    """Apply the selected custom theme."""

    theme = THEMES[st.session_state.theme]

    css = f"""
    <style>
        :root {{
            --app-background: {theme["background"]};
            --app-surface: {theme["surface"]};
            --app-surface-alt: {theme["surface_alt"]};
            --app-primary: {theme["primary"]};
            --app-primary-hover: {theme["primary_hover"]};
            --app-text: {theme["text"]};
            --app-muted-text: {theme["muted_text"]};
            --app-border: {theme["border"]};
            --app-user-message: {theme["user_message"]};
            --app-assistant-message: {theme["assistant_message"]};
            --app-input-background: {theme["input_background"]};
            --app-shadow: {theme["shadow"]};
            --app-success: {theme["success"]};
        }}

        html,
        body,
        [data-testid="stApp"],
        [data-testid="stAppViewContainer"] {{
            background-color: var(--app-background);
            color: var(--app-text);
        }}

        [data-testid="stHeader"] {{
            background-color: transparent;
        }}

        [data-testid="stMain"] {{
            background-color: var(--app-background);
        }}

        [data-testid="stMainBlockContainer"] {{
            max-width: 1320px;
            padding-top: 3.5rem;
            padding-bottom: 6rem;
        }}

        [data-testid="stSidebar"] {{
            background-color: var(--app-surface);
            border-right: 1px solid var(--app-border);
        }}

        [data-testid="stSidebarContent"] {{
            background-color: var(--app-surface);
        }}

        [data-testid="stSidebarContent"] > div {{
            padding-top: 1.4rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }}

        h1,
        h2,
        h3,
        h4,
        h5,
        h6,
        p,
        label,
        span {{
            color: var(--app-text);
        }}

        [data-testid="stCaptionContainer"] {{
            color: var(--app-muted-text);
        }}

        hr {{
            border-color: var(--app-border);
            margin-top: 1.3rem;
            margin-bottom: 1.3rem;
        }}

        [data-testid="stAlert"] {{
            background-color: var(--app-surface-alt);
            color: var(--app-text);
            border: 1px solid var(--app-border);
            border-radius: 14px;
        }}

        [data-testid="stChatMessage"] {{
            background-color: var(--app-assistant-message);
            border: 1px solid var(--app-border);
            border-radius: 16px;
            padding: 0.75rem 1rem;
            margin-bottom: 0.8rem;
            box-shadow: 0 6px 18px var(--app-shadow);
        }}

        [data-testid="stChatMessage"]:has(
            [data-testid="chatAvatarIcon-user"]
        ) {{
            background-color: var(--app-user-message);
        }}

        [data-testid="stBottomBlockContainer"] {{
            background-color: var(--app-background);
        }}

        [data-testid="stChatInput"] {{
            background-color: var(--app-input-background);
            border: 1px solid var(--app-border);
            border-radius: 14px;
            box-shadow: 0 8px 24px var(--app-shadow);
        }}

        [data-testid="stChatInput"] textarea {{
            color: var(--app-text);
            caret-color: var(--app-primary);
        }}

        [data-testid="stChatInput"] textarea::placeholder {{
            color: var(--app-muted-text);
        }}

        .stButton > button {{
            width: 100%;
            background-color: var(--app-surface-alt);
            color: var(--app-text);
            border: 1px solid var(--app-border);
            border-radius: 10px;
            padding: 0.58rem 1rem;
            font-weight: 600;
            transition:
                background-color 0.2s ease,
                border-color 0.2s ease,
                transform 0.2s ease;
        }}

        .stButton > button:hover {{
            background-color: var(--app-surface);
            color: var(--app-text);
            border-color: var(--app-primary);
            transform: translateY(-1px);
        }}

        [data-testid="stToggle"] {{
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0;
            padding: 0;
        }}

        [data-testid="stToggle"] > label {{
            display: flex;
            align-items: center;
            justify-content: center;
            width: 100%;
            margin: 0;
        }}

        [data-testid="stToggle"] div[role="switch"] {{
            transform: scale(1.14);
        }}

        [data-testid="stToggle"]
        div[role="switch"][aria-checked="true"] {{
            background-color: var(--app-primary);
        }}

        [data-testid="stSidebarCollapseButton"] button,
        [data-testid="stSidebarCollapsedControl"] button {{
            color: var(--app-text);
        }}

        .sidebar-brand {{
            display: flex;
            align-items: center;
            gap: 0.7rem;
            padding: 0.25rem 0 0.8rem 0;
        }}

        .sidebar-brand-icon {{
            display: flex;
            align-items: center;
            justify-content: center;
            width: 2.25rem;
            height: 2.25rem;
            background-color: var(--app-surface-alt);
            border: 1px solid var(--app-border);
            border-radius: 10px;
            font-size: 1.05rem;
        }}

        .sidebar-brand-title {{
            color: var(--app-text);
            font-size: 1.05rem;
            font-weight: 750;
            line-height: 1.2;
        }}

        .sidebar-brand-subtitle {{
            color: var(--app-muted-text);
            font-size: 0.72rem;
            line-height: 1.2;
            margin-top: 0.15rem;
        }}

        .theme-card {{
            padding: 0.8rem 0.75rem 0.65rem 0.75rem;
            background-color: var(--app-surface-alt);
            border: 1px solid var(--app-border);
            border-radius: 13px;
        }}

        .theme-label {{
            color: var(--app-muted-text);
            font-size: 0.82rem;
            font-weight: 650;
            line-height: 2rem;
            white-space: nowrap;
        }}

        .theme-label-left {{
            text-align: right;
        }}

        .theme-label-right {{
            text-align: left;
        }}

        .sidebar-section-title {{
            color: var(--app-text);
            font-size: 0.92rem;
            font-weight: 700;
            margin: 0 0 0.7rem 0;
        }}

        .system-list {{
            display: flex;
            flex-direction: column;
            gap: 0.72rem;
        }}

        .system-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.8rem;
        }}

        .system-label {{
            display: flex;
            align-items: center;
            color: var(--app-muted-text);
            font-size: 0.87rem;
        }}

        .system-value {{
            color: var(--app-text);
            font-size: 0.87rem;
            font-weight: 650;
        }}

        .system-dot {{
            display: inline-block;
            width: 0.48rem;
            height: 0.48rem;
            margin-right: 0.5rem;
            background-color: var(--app-success);
            border-radius: 50%;
            box-shadow: 0 0 8px var(--app-success);
        }}

        .upload-placeholder {{
            padding: 1.15rem 0.9rem;
            background-color: var(--app-surface-alt);
            border: 1px dashed var(--app-border);
            border-radius: 13px;
            text-align: center;
        }}

        .upload-placeholder-icon {{
            color: var(--app-primary);
            font-size: 1.35rem;
            margin-bottom: 0.4rem;
        }}

        .upload-placeholder-title {{
            color: var(--app-text);
            font-size: 0.88rem;
            font-weight: 650;
        }}

        .upload-placeholder-text {{
            color: var(--app-muted-text);
            font-size: 0.76rem;
            line-height: 1.45;
            margin-top: 0.25rem;
        }}

        .app-hero {{
            padding: 1.3rem 1.55rem;
            background:
                linear-gradient(
                    135deg,
                    var(--app-surface),
                    var(--app-surface-alt)
                );
            border: 1px solid var(--app-border);
            border-radius: 18px;
            box-shadow: 0 10px 30px var(--app-shadow);
            margin-bottom: 1.5rem;
        }}

        .app-hero-title {{
            color: var(--app-text);
            font-size: 2.15rem;
            font-weight: 750;
            line-height: 1.2;
            margin: 0;
        }}

        .app-hero-subtitle {{
            color: var(--app-muted-text);
            font-size: 1rem;
            line-height: 1.6;
            margin: 0.5rem 0 0 0;
        }}
    </style>
    """

    st.markdown(css, unsafe_allow_html=True)


def update_theme(theme_name: str) -> None:
    """Update the active theme."""

    if st.session_state.theme == theme_name:
        return

    st.session_state.theme = theme_name
    st.rerun()


def clear_chat() -> None:
    """Clear messages from the active chat session."""

    st.session_state.messages = []
    st.rerun()


def render_sidebar_brand() -> None:
    """Render the compact sidebar application identity."""

    brand_html = (
        '<div class="sidebar-brand">'
        '<div class="sidebar-brand-icon">🤖</div>'
        '<div>'
        '<div class="sidebar-brand-title">Local RAG</div>'
        '<div class="sidebar-brand-subtitle">Private document assistant</div>'
        '</div>'
        '</div>'
    )

    st.markdown(
        brand_html,
        unsafe_allow_html=True,
    )


def render_theme_control() -> None:
    """Render the theme switch inside a compact card."""

    st.markdown(
        '<div class="theme-card">',
        unsafe_allow_html=True,
    )

    dark_column, toggle_column, light_column = st.columns(
        [1.15, 0.7, 1.15],
        vertical_alignment="center",
        gap="small",
    )

    with dark_column:
        st.markdown(
            '<div class="theme-label theme-label-left">🌙 Dark</div>',
            unsafe_allow_html=True,
        )

    with toggle_column:
        light_mode_enabled = st.toggle(
            "Theme",
            value=st.session_state.theme == "Light",
            key="theme_switch",
            label_visibility="collapsed",
        )

    with light_column:
        st.markdown(
            '<div class="theme-label theme-label-right">Light ☀️</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )

    selected_theme = "Light" if light_mode_enabled else "Dark"

    if selected_theme != st.session_state.theme:
        update_theme(selected_theme)


def render_system_status() -> None:
    """Render application status information."""

    st.markdown(
        '<p class="sidebar-section-title">System</p>',
        unsafe_allow_html=True,
    )

    status_html = (
        '<div class="system-list">'
        '<div class="system-row">'
        '<span class="system-label">'
        '<span class="system-dot"></span>'
        'Application'
        '</span>'
        '<span class="system-value">Ready</span>'
        '</div>'
        '<div class="system-row">'
        '<span class="system-label">'
        '<span class="system-dot"></span>'
        'Database'
        '</span>'
        '<span class="system-value">Connected</span>'
        '</div>'
        '<div class="system-row">'
        '<span class="system-label">📄 Documents</span>'
        '<span class="system-value">0</span>'
        '</div>'
        '</div>'
    )

    st.markdown(
        status_html,
        unsafe_allow_html=True,
    )


def render_knowledge_base() -> None:
    """Render the knowledge base placeholder."""

    st.markdown(
        '<p class="sidebar-section-title">Knowledge Base</p>',
        unsafe_allow_html=True,
    )

    upload_html = (
        '<div class="upload-placeholder">'
        '<div class="upload-placeholder-icon">＋</div>'
        '<div class="upload-placeholder-title">Upload documents</div>'
        '<div class="upload-placeholder-text">'
        'PDF upload and document management will appear here.'
        '</div>'
        '</div>'
    )

    st.markdown(
        upload_html,
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    """Render the application sidebar."""

    with st.sidebar:
        render_sidebar_brand()
        render_theme_control()

        st.divider()

        render_system_status()

        st.divider()

        render_knowledge_base()

        st.divider()

        if st.button(
            "🗑 Clear Chat",
            key="clear_chat_button",
            use_container_width=True,
        ):
            clear_chat()


def render_header() -> None:
    """Render the main application header."""

    hero_html = (
        '<div class="app-hero">'
        f'<p class="app-hero-title">{APP_TITLE}</p>'
        '<p class="app-hero-subtitle">'
        'Your private AI assistant for intelligent document search '
        'and grounded question answering.'
        '</p>'
        '</div>'
    )

    st.markdown(
        hero_html,
        unsafe_allow_html=True,
    )


def render_chat_history() -> None:
    """Render chat messages from the current session."""

    if not st.session_state.messages:
        st.info(
            "Upload one or more documents to get started."
        )
        return

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def handle_chat_input() -> None:
    """Process user input from the chat field."""

    prompt = st.chat_input(
        "Ask anything about your documents..."
    )

    if not prompt:
        return

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    placeholder_response = (
        "The RAG pipeline will be connected in the next step."
    )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": placeholder_response,
        }
    )

    with st.chat_message("assistant"):
        st.markdown(placeholder_response)


def main() -> None:
    """Run the Streamlit application."""

    configure_page()
    initialize_session_state()
    apply_custom_theme()

    render_sidebar()
    render_header()
    render_chat_history()
    handle_chat_input()


if __name__ == "__main__":
    main()