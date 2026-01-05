"""
Bilingual copy for Murkaverse Gatekeeper Bot.
All texts are dictionaries with "en" and "ru" keys.
Theme: dreamy, playful, light — dreams, sparkles, moons, cat paws
"""

# --- Language Selection ---

LANGUAGE_SELECT = """🌐 *Choose your language*

Please select your preferred language:

🌐 *Выбери язык*

Пожалуйста, выбери предпочитаемый язык:"""

# --- Welcome & Rules ---

WELCOME_START = {
    "en": """🌙 *Hey there, dreamer!*

Welcome to Murkaverse ✨

Tap below to begin your journey.""",
    
    "ru": """🌙 *Привет, мечтатель!*

Добро пожаловать в Murkaverse ✨

Нажми ниже, чтобы начать путешествие."""
}

WELCOME_RULES = {
    "en": """🐾 *Almost there, dreamer!*

Just a few simple rules before you enter:

✨ Be kind to fellow dreamers
✨ No spam or self-promo
✨ Keep it cozy and stick to the theme of dreams or the Murkaverse project in general
✨ English in General, other topics include English and Russian language versions""",
    
    "ru": """🐾 *Почти все, мечтатель!*

Несколько простых правил:

✨ Будь добр к другим мечтателям
✨ Без спама и саморекламы
✨ Сохраняй уют и придерживайся темы снов или проекта Муркаверс в общем
✨ Английский в General, другие темы включают английскую и русскую версии"""
}

# --- Buttons ---

BTN_LANG_EN = "🇬🇧 English"
BTN_LANG_RU = "🇷🇺 Русский"

BTN_JOIN = {
    "en": "🌙 Enter Murkaverse",
    "ru": "🌙 Войти в Муркаверс"
}

BTN_AGREE = {
    "en": "🐾 I agree",
    "ru": "🐾 Согласен"
}

BTN_CANCEL = {
    "en": "✨ Later",
    "ru": "✨ Позже"
}

BTN_TRY_AGAIN = {
    "en": "🌙 Try again",
    "ru": "🌙 Ещё раз"
}

BTN_TRY_LATER = {
    "en": "✨ Try later",
    "ru": "✨ Попробовать позже"
}

# --- Captcha ---

CAPTCHA_INTRO = {
    "en": """🐾 *Quick Verification!*

Just making sure you're a real dreamer, not a bot ✨

{challenge}""",
    
    "ru": """🐾 *Быстрая проверка!*

Убедимся, что ты настоящий мечтатель ✨

{challenge}"""
}

# Challenge templates: (english_text, russian_text, correct_emoji)
CAPTCHA_CHALLENGES = [
    ("Tap the moon 🌙", "Нажми на луну 🌙", "🌙"),
    ("Tap the sparkle ✨", "Нажми на искорку ✨", "✨"),
    ("Tap the cat paw 🐾", "Нажми на лапку 🐾", "🐾"),
    ("Tap the star 🌟", "Нажми на звезду 🌟", "🌟"),
    ("Tap the dream cloud 💭", "Нажми на облако 💭", "💭"),
]

# Decoy emojis (used to fill wrong answers)
CAPTCHA_DECOYS = ["🌸", "🦋", "🍃", "☁️", "🫧", "🪷", "🌿", "🧸", "💫", "🌷", "🪻", "🐚"]

CAPTCHA_SUCCESS = {
    "en": """✨ *Welcome to Murkaverse, dreamer!*

You're all set to join 🌙

🐾 *Next steps:*
1. Tap the link below → "Request to Join"
2. You'll be approved in seconds
3. English in General, other topics include English and Russian language versions

{invite_link}""",
    
    "ru": """✨ *Добро пожаловать в Муркаверс, мечтатель!*

Присоединяйся к группе Муркаверс 🌙

🐾 *Что дальше:*
1. Нажми на ссылку, чтобы войти в группу!
2. Одобрим за секунды
3. Английский в General, другие темы включают английскую и русскую версии

{invite_link}"""
}

CAPTCHA_WRONG = {
    "en": """🌙 *Oops, wrong one!*

Try again, dreamer ✨
Attempts left: {remaining}""",
    
    "ru": """🌙 *Упс, не то!*

Попробуй ещё, мечтатель ✨
Осталось попыток: {remaining}"""
}

CAPTCHA_COOLDOWN = {
    "en": """💤 *Take a little nap...*

Too many tries! Wait {minutes} min and try again 🌙""",
    
    "ru": """💤 *Немного подремли...*

Слишком много попыток! Подожди {minutes} мин 🌙"""
}

# --- Cancelled ---

CANCELLED = {
    "en": """✨ *No worries, dreamer!*

Come back anytime — just tap /start""",
    
    "ru": """✨ *Без проблем, мечтатель!*

Возвращайся когда захочешь — нажми /start"""
}

# --- Join Request Approved ---

APPROVED = {
    "en": """🐾 *You're in, dreamer!*

Welcome to Murkaverse ✨

🌙 English in General
🌙 Other topics include English and Russian language versions

See you inside! 💫""",
    
    "ru": """🐾 *Ты внутри, мечтатель!*

Добро пожаловать в Муркаверс ✨

🌙 Английский в General
🌙 Другие темы включают английскую и русскую версии

До встречи! 💫"""
}

# --- Strict Mode Decline ---

DECLINED_VERIFY_FIRST = {
    "en": """🌙 *One moment, dreamer!*

Please complete the verification first ✨

Tap /start to begin.""",
    
    "ru": """🌙 *Секундочку, мечтатель!*

Сначала пройди проверку ✨

Нажми /start чтобы начать."""
}

# --- Admin Messages (English only) ---

ADMIN_LOCKDOWN_ON = "🔒 Lockdown ON. All join requests will be declined."
ADMIN_LOCKDOWN_OFF = "🔓 Lockdown OFF. Dreams flowing again."
ADMIN_MODE_STRICT = "🌙 Strict mode ON. Unverified requests declined."
ADMIN_MODE_SOFT = "✨ Soft mode ON. Unverified requests left pending."
ADMIN_NOT_AUTHORIZED = "🐾 Sorry, admin only."

ADMIN_STATUS = """🌙 *Gatekeeper Status*

**Mode:** {mode}
**Lockdown:** {lockdown}

**Stats (24h):**
✨ Verified: {verified_24h}
🐾 Total dreamers: {total_users}"""

ADMIN_HELP = """🐾 *Admin Commands*

/lockdown on|off — Emergency mode
/mode soft|strict — Verification mode
/status — Stats and status"""

# --- Errors ---

ERROR_GENERIC = {
    "en": "🌙 Something went wrong... Try again?",
    "ru": "🌙 Что-то пошло не так... Попробуй ещё раз?"
}


# --- Helper function ---

def get_text(text_dict: dict | str, lang: str) -> str:
    """Get text for specified language. Falls back to English if not found."""
    if isinstance(text_dict, str):
        return text_dict
    return text_dict.get(lang, text_dict.get("en", ""))
