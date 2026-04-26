"""Seasonal pulse (BL-115): surface season-relevant categories on the home page.

Trapani-flavored. The app should know local rhythms:
- May/June: tonnara (tuna season) -- boats, sea gear wake up
- July/August: peak summer + Ferragosto (Aug 15) -- festivals, beach
- September: vendemmia (grape harvest) -- food, kitchen
- October/November: olive harvest -- frantoio, food prep, winter prep
- December: Christmas markets, presepi, indoor crafts
- February: Carnevale Trapani (one of Sicily's most famous)
- March/April: spring cleaning, gardens waking up, Pasqua

Each month maps to a theme + the categories most relevant to it. The home
page queries up to 6 active listings whose item.category is in the
current month's category list. If nothing matches, the section hides.

Keep this file as a single map -- adding seasonality elsewhere risks
inconsistency (e.g. theme says "olive harvest" but query asks for
swimwear). One source of truth.
"""
from datetime import datetime, timezone

# Month (1-12) -> seasonal hint
# accent must be a Tailwind palette name -- the template branches on it
# for backgrounds and badge colors.
SEASONAL_MAP: dict[int, dict] = {
    1: {
        "theme_en": "New Year, new skills",
        "theme_it": "Anno nuovo, competenze nuove",
        "subtitle_en": "Pick up something to learn this month -- a Maker, a workshop, a teacher.",
        "subtitle_it": "Trova qualcosa da imparare questo mese -- un Maker, un workshop, un insegnante.",
        "categories": ["training_service", "education", "skill_exchange", "workshop_event"],
        "accent": "indigo",
    },
    2: {
        "theme_en": "Carnevale season",
        "theme_it": "Stagione del Carnevale",
        "subtitle_en": "Costumes, masks, music, sweets -- everything for one of Sicily's loudest months.",
        "subtitle_it": "Costumi, maschere, musica, dolci -- tutto per uno dei mesi più rumorosi della Sicilia.",
        "categories": ["sewing", "crafts", "art", "music", "food"],
        "accent": "purple",
    },
    3: {
        "theme_en": "Spring cleaning + gardens waking up",
        "theme_it": "Pulizie di primavera + giardini che si svegliano",
        "subtitle_en": "Borrow what you need to refresh the house and start the season's planting.",
        "subtitle_it": "Prendi in prestito cio di cui hai bisogno per rinfrescare casa e iniziare la semina.",
        "categories": ["cleaning", "garden", "tool_library", "home_improvement"],
        "accent": "emerald",
    },
    4: {
        "theme_en": "Pasqua + planting time",
        "theme_it": "Pasqua + tempo di seminare",
        "subtitle_en": "Easter feasts, garden plans, kitchen rentals -- spring's busy weeks.",
        "subtitle_it": "Feste di Pasqua, piani per il giardino, cucine in affitto -- le settimane intense della primavera.",
        "categories": ["garden", "kitchen", "food", "crafts", "workshop_event"],
        "accent": "amber",
    },
    5: {
        "theme_en": "Sea wakes up: boats, tonnara, beach gear",
        "theme_it": "Il mare si sveglia: barche, tonnara, attrezzatura da spiaggia",
        "subtitle_en": "Tonnara starts, the coast opens, water sports return -- gear up.",
        "subtitle_it": "Inizia la tonnara, la costa si apre, gli sport acquatici tornano -- preparati.",
        "categories": ["water_sports", "sports", "camping", "transport"],
        "accent": "cyan",
    },
    6: {
        "theme_en": "Tonnara + summer kickoff",
        "theme_it": "Tonnara + estate al via",
        "subtitle_en": "Peak fishing season, tourists arriving, festivals starting -- the loud months begin.",
        "subtitle_it": "Stagione di pesca al massimo, turisti in arrivo, festival in partenza -- iniziano i mesi rumorosi.",
        "categories": ["water_sports", "vacation_rental", "camping", "festival", "concert"],
        "accent": "blue",
    },
    7: {
        "theme_en": "Peak summer: festivals, beaches, granita",
        "theme_it": "Estate al massimo: festival, spiagge, granita",
        "subtitle_en": "Every weekend has a festival or a market. Borrow what you need to join in.",
        "subtitle_it": "Ogni weekend ha un festival o un mercato. Prendi in prestito cio che ti serve per partecipare.",
        "categories": ["festival", "concert", "market", "water_sports", "vacation_rental"],
        "accent": "rose",
    },
    8: {
        "theme_en": "Ferragosto + outdoor everything",
        "theme_it": "Ferragosto + tutto all'aperto",
        "subtitle_en": "August 15 is sacred -- beach, food, family, fireworks. The whole island is outside.",
        "subtitle_it": "Il 15 agosto e sacro -- spiaggia, cibo, famiglia, fuochi. Tutta l'isola e fuori.",
        "categories": ["festival", "concert", "water_sports", "camping", "vacation_rental", "food"],
        "accent": "amber",
    },
    9: {
        "theme_en": "Vendemmia: grape harvest + autumn pivot",
        "theme_it": "Vendemmia + svolta autunnale",
        "subtitle_en": "Wine country wakes up. Kitchens fill with grape and fig recipes.",
        "subtitle_it": "Le cantine si svegliano. Le cucine si riempiono di ricette d'uva e fichi.",
        "categories": ["food", "kitchen", "hand_tools", "garden"],
        "accent": "purple",
    },
    10: {
        "theme_en": "Olive harvest begins -- press and store",
        "theme_it": "Inizia la raccolta delle olive -- frantoio e conserva",
        "subtitle_en": "Frantoi open, jars get filled, wood gets stacked. The pivot to winter has started.",
        "subtitle_it": "I frantoi aprono, i barattoli si riempiono, la legna si accatasta. La svolta verso l'inverno e iniziata.",
        "categories": ["food", "kitchen", "hand_tools", "garden", "tool_library"],
        "accent": "emerald",
    },
    11: {
        "theme_en": "Olive harvest peak + winter prep",
        "theme_it": "Raccolta olive + preparazione invernale",
        "subtitle_en": "Last warm weeks. Workshops fire up, repairs queue up, sweaters come out.",
        "subtitle_it": "Ultime settimane tiepide. Le botteghe si accendono, le riparazioni si accumulano, i maglioni escono.",
        "categories": ["food", "kitchen", "home_improvement", "hand_tools", "repairs"],
        "accent": "stone",
    },
    12: {
        "theme_en": "Christmas markets + presepi + warm gatherings",
        "theme_it": "Mercatini di Natale + presepi + incontri al caldo",
        "subtitle_en": "Crafts, sweets, decorations, indoor workshops -- the year's warmest social weeks.",
        "subtitle_it": "Artigianato, dolci, decorazioni, workshop al chiuso -- le settimane piu calde dell'anno.",
        "categories": ["crafts", "art", "food", "market", "workshop_event", "music"],
        "accent": "rose",
    },
}


def get_current_seasonal_hint(now: datetime | None = None) -> dict:
    """Return the seasonal hint for the current month.

    Defaults to UTC; for Italy that's good enough (Rome is UTC+1/+2 so the
    month boundary is the same except for the very first/last hour).
    """
    if now is None:
        now = datetime.now(timezone.utc)
    return SEASONAL_MAP.get(now.month, SEASONAL_MAP[1])
