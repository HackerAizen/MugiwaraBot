from string import ascii_uppercase as UPPERCASE_LETTERS

flag_emoji_dict = {
"🇺🇸": "en",
"🇩🇪": "de",
"🇫🇷": "fr",
"🇪🇸": "es",
"🇮🇹": "it",
"🇵🇹": "pt",
"🇷🇺": "ru",
"🇦🇱": "sq",
"🇸🇦": "ar",
"🇧🇦": "bs",
"🇧🇬": "bg",
"🇨🇳": "zh-CN",
"🇭🇷": "hr",
"🇨🇿": "cs",
"🇩🇰": "da",
"🇪🇪": "et",
"🇫🇮": "fi",
"🇬🇷": "el",
"🇭🇺": "hu",
"🇮🇩": "id",
"🇮🇳": "hi",
"🇮🇪": "ga",
"🇮🇸": "is",
"🇮🇱": "he",
"🇯🇵": "ja",
"🇰🇷": "ko",
"🇱🇻": "lv",
"🇱🇹": "lt",
"🇲🇹": "mt",
"🇲🇪": "sr",
"🇳🇱": "nl",
"🇳🇴": "no",
"🇵🇰": "ur",
"🇵🇱": "pl",
"🇵🇹": "pt",
"🇷🇴": "ro",
"🇷🇸": "sr",
"🇸🇦": "ar",
"🇸🇰": "sk",
"🇸🇮": "sl",
"🇸🇬": "sv",
"🇹🇭": "th",
"🇹🇷": "tr",
"🇹🇼": "zh-TW",
"🇺🇦": "uk",
"🇻🇦": "la"
}

CHANNEL_WEBHOOK_URL = "https://discord.com/api/webhooks/1204387205276241991/APbVL0pCUGkvQlGRJxBwOW6Ti4SKnoLX8pC6h0Dd_xY8mK4PHbsLvqBd_PaY9FWysZrX"

HOST_ROLE = "Shanks"

BADWORDS =  ["лох", "дурак", "porn", "порн", "fuck", "hoe", "прон", "slave", "penis", "relig", "slave", "war ", "blood", 
            "traum", "violence", "weapon", "kill", "dynamite", "bomb", "dead", "terror", "destroy", "drug",
            "dirty old man", "down s", "dwarf", "duffer", "hussy", "pussy", "ass", "stupid", "motherf", "dick", "pron", "sex",
            "раб", "религ", "оруж", "кров", "убит", "динамит", "бомб", "смерт", "терро", "мамонт", "мать жива", "войн", "разруш",
            "нарко", "пизд", "уеб", "жоп", "даун", "идиот", "pidor", "пидор", "дур", "секс", "трах", "пенис", "член", "конч"]
LINKS = [".org", ".net", ".ru", ".shop", ".xyz", ".ру", ".рф"]

API_KEY = ""
TOKEN = ''
PREFIX = '!'
GUILD_ID = 1185210111724113940
WELCOME_CHANNEL = 1185210112302923919

QUESTION_EMBED_COLOR = 0x5c81f0
ANSWER_EMBED_COLOR = 0x1DF183
LEADERBOARD_EMBED_COLOR = 0xE6F31B

MIN_OPTIONS = 2
MAX_OPTIONS = len(UPPERCASE_LETTERS)