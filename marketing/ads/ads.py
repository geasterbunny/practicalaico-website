"""Scripts for the five website-services ads. *word* = teal accent.

Claims here are limited to what practicalaico.ai/websites and the home page
already state (prices, the 18 -> 33 indexing fix, live 3D home page).
"""

def S(kind, dur, **kw):
    kw.update(kind=kind, dur=dur)
    return kw

ADS = [
    dict(id=1, slug="chatbot-11pm", bpm=100, scenes=[
        S("hook", 3.6, text="It's *11:47pm.*\nSomeone's on your website, ready to book.", size=96),
        S("hook", 2.6, text="And you're\n*asleep.*", size=150),
        S("statement", 5.0, eyebrow="WHAT HAPPENS NEXT", head="They ask a question.\n*Nobody answers.*",
          body="So they hit back and book whoever replies first."),
        S("statement", 4.6, eyebrow="THE REAL PROBLEM", head="Enquiries don't wait for *business hours.*",
          body="They land while you're on the tools, at dinner, or asleep."),
        S("chat", 11.0, title="Now, with a chatbot on your site:", name="Your Business", initial="Y", msgs=[
            ("user", "Hi, do you regrout showers in Parramatta?", 0.8),
            ("bot", "We do! Most regrouts are a half-day job. Want a fixed quote?", 2.6),
            ("user", "Yes please. Thursday arvo suits.", 5.0),
            ("bot", "Got it, Thursday arvo is requested. You'll get a confirmed time by 9am.", 6.8),
        ]),
        S("ticks", 8.4, eyebrow="WEBSITE CHATBOT", title="It actually knows *your* business.", items=[
            "Trained on your pages, prices and FAQs, not the internet",
            "Answers hours, pricing, stock and bookings, 24/7",
            "Captures the lead when it can't answer",
            "Anything that commits you waits for your tap",
        ]),
        S("statement", 4.8, eyebrow="PLUGS STRAIGHT IN", head="Add it to the site you *already have.*",
          body="Or to a new one we build. On your website or Facebook Messenger."),
        S("cta", 8.0, head="Stop losing the *11pm enquiry.*", price="WEBSITE CHATBOT · FROM A$790 SETUP",
          url="practicalaico.ai"),
    ]),
    dict(id=2, slug="store-payments", bpm=104, scenes=[
        S("hook", 3.8, text="Your Instagram gets *likes.*\nYour bank account *doesn't.*", size=98),
        S("statement", 5.0, eyebrow="SOUND FAMILIAR?", head="*\"DM for price\"*\nis costing you sales.",
          body="Every sale has to survive a back-and-forth. Most don't."),
        S("checkout", 11.0, title="Let them buy in *three taps.*", product="Hand-poured soy candle", price="A$34.00"),
        S("ticks", 8.6, eyebrow="ONLINE STORE + PAYMENTS", title="A proper store, *built for you.*", items=[
            "Shopify store designed around your brand",
            "Card, Apple Pay and Google Pay at checkout",
            "Shipping and GST set up properly",
            "Order alerts straight to your phone",
        ]),
        S("statement", 5.4, eyebrow="BIG CATALOGUE?", head="200 products?\n*Don't type them.*",
          body="Our Product Listing Engine writes the copy, tags and mockups, and checks every image before it goes live."),
        S("statement", 5.0, eyebrow="NO LOCK-IN", head="Your store. Your domain.\n*Your customers.*",
          body="Fixed price. You know the number before we start."),
        S("cta", 9.0, head="Turn followers into *orders.*", price="ONLINE STORES · FIXED-PRICE QUOTE",
          url="practicalaico.ai"),
    ]),
    dict(id=3, slug="3d-websites", bpm=96, scenes=[
        S("hook", 4.0, text="Your website gets\n*one glance.*", size=116),
        S("hook", 3.0, text="Make it one they\n*remember.*", size=116),
        S("cube", 11.0, head="Live 3D.\n*Right in the browser.*", sub="No app. No download. Works on phones."),
        S("statement", 5.2, eyebrow="NOT A GIMMICK", head="3D gives people a *reason to stay.*",
          body="Spin the product. Peel back the build. Turn a scroll into a story."),
        S("statement", 5.4, eyebrow="PROOF", head="Our own homepage runs *live 3D.*",
          body="And it's usable in about half a second. Fast and impressive aren't opposites."),
        S("ticks", 9.6, eyebrow="WHERE 3D EARNS ITS KEEP", title="Built for *real businesses.*", items=[
            "Products people can spin, zoom and inspect",
            "Trades and builders: show the job layer by layer",
            "Scroll-driven story pages that hold attention",
            "Still fast, and still set up to be found on Google",
        ]),
        S("cta", 9.0, head="Build a site people *actually scroll.*", price="3D & SCROLL-DRIVEN SITES · FIXED PRICE",
          url="practicalaico.ai"),
    ]),
    dict(id=4, slug="ai-search", bpm=100, scenes=[
        S("hook", 3.8, text="Your next customer might not *Google* you.", size=104),
        S("hook", 2.8, text="They'll\n*ask AI.*", size=160),
        S("aisearch", 11.5, title="Here's what they see:",
          query="Who's the best bathroom renovator in the Sutherland Shire?",
          reviews=["4.9 · 212 reviews", "4.8 · 148 reviews", "4.8 · 96 reviews"],
          caption="Are you *in the answer?*"),
        S("statement", 5.2, eyebrow="HOW IT WORKS", head="AI can only recommend what it can *read.*",
          body="Slow pages, vague copy and details buried in images make you invisible."),
        S("ticks", 9.0, eyebrow="AI SEARCH OPTIMISATION", title="We make your site *AI-readable.*", items=[
            "Structured data: who, where, what and how much",
            "Clear answers to what customers actually ask",
            "Google Business Profile, sitemap and Search Console",
            "Fast pages crawlers can read in full",
        ]),
        S("statement", 4.8, eyebrow="STRAIGHT TALK", head="Nobody can promise you the *#1 spot.*",
          body="Anyone who does is guessing. We fix what's fixable and show you the before and after."),
        S("stat", 4.6, eyebrow="OUR OWN SITE", before=18, after=33,
          label="pages in Google's view of our site. Fixed the same day."),
        S("cta", 8.0, head="Be the *answer.*", price="START WITH A SITE AUDIT · FROM A$490",
          url="practicalaico.ai"),
    ]),
    dict(id=5, slug="full-toolkit", bpm=104, scenes=[
        S("hook", 3.8, text="Most small business websites are *brochures.*", size=104),
        S("hook", 3.0, text="They just\n*sit there.*", size=150),
        S("statement", 5.6, eyebrow="YOURS SHOULD WORK", head="A website that *brings the work in.*",
          body="Answers, sells, takes payment and gets found, while you're on the tools."),
        S("ticks", 14.0, eyebrow="PLUG IN WHAT YOU NEED", title="One site. *Every tool.*", items=[
            ("CHAT", "AI chatbot", "answers at 11pm"),
            ("SHOP", "Online store", "sells while you sleep"),
            ("PAY", "Payments", "card, Apple Pay, Google Pay"),
            ("3D", "Live 3D", "stops the scroll"),
            ("AI", "AI search", "so ChatGPT can find you"),
            ("AUTO", "Auto follow-ups", "reply drafted, waits for your tap"),
        ]),
        S("statement", 5.6, eyebrow="FIXED PRICE", head="Built in *days,* not months.",
          body="Five-page site from A$1,490. Add only the tools you need. No monthly platform fee."),
        S("statement", 5.6, eyebrow="YOU'RE IN CONTROL", head="Nothing goes live *without your OK.*",
          body="Private preview link first. Domain and code in your name. Yours outright."),
        S("cta", 9.5, head="Build the site that *brings the work in.*", price="WEBSITES FROM A$1,490 · SYDNEY",
          url="practicalaico.ai"),
    ]),
]

for _ad in ADS:
    _d = sum(s["dur"] for s in _ad["scenes"])
    assert _d >= 45, (_ad["slug"], _d)

# Voiceover, one line per scene (same order as the scenes above). Written for
# the ear: numbers and "A.I." spelled the way they should be spoken.
SITE = "Practical A.I. Co dot A.I."
VO = {
    1: [
        "It's eleven forty-seven p.m. Someone's on your website, ready to book.",
        "And you're asleep.",
        "They ask a question. Nobody answers. So they book whoever replies first.",
        "Enquiries don't wait for business hours. They land while you're on the tools, at dinner, or asleep.",
        "Now picture a chatbot on your site. It answers the question, offers a fixed quote, and takes the booking request, all while you sleep.",
        "It's trained on your pages, prices and FAQs, not the internet. It captures the lead when it can't answer. And anything that commits you waits for your tap.",
        "Add it to the site you already have, or to a new one we build.",
        "Stop losing the eleven p.m. enquiry. Website chatbots from seven hundred and ninety dollars. " + SITE,
    ],
    2: [
        "Your Instagram gets likes. Your bank account doesn't.",
        "DM for price is costing you sales. Every sale has to survive a back-and-forth, and most don't.",
        "Give them a proper store instead. Add to cart, Apple Pay, done. The payment lands, and the order alert hits your phone.",
        "We build your Shopify store around your brand, with card, Apple Pay and Google Pay at checkout, and shipping and G.S.T. set up properly.",
        "Got two hundred products? Don't type them. Our listing engine writes the copy, tags and mockups for you.",
        "Your store, your domain, your customers. Fixed price, so you know the number before we start.",
        "Turn followers into orders. Get a fixed-price quote at " + SITE,
    ],
    3: [
        "Your website gets one glance.",
        "Make it one they remember.",
        "Live 3D, right in the browser. No app, no download, and it works on phones.",
        "It's not a gimmick. It's a reason to stay. Spin the product, peel back the build, turn a scroll into a story.",
        "Our own homepage runs live 3D, and it's usable in about half a second. Fast and impressive aren't opposites.",
        "Products people can spin and zoom. Trades showing the job layer by layer. Story pages that hold attention, and still set up to be found on Google.",
        "Build a site people actually scroll. Fixed price, at " + SITE,
    ],
    4: [
        "Your next customer might not Google you.",
        "They'll ask A.I.",
        "They type: who's the best bathroom renovator in the Sutherland Shire? The A.I. lists three businesses. Are you one of them?",
        "A.I. can only recommend what it can read. Slow pages, vague copy and details buried in images make you invisible.",
        "We make your site A.I. readable. Structured data, clear answers to real customer questions, your Google Business Profile, sitemap and Search Console, all on fast pages.",
        "Nobody can promise you the number one spot. Anyone who does is guessing.",
        "On our own site, Google's view went from eighteen pages to thirty-three, the same day.",
        "Be the answer. Start with a site audit from four hundred and ninety dollars, at " + SITE,
    ],
    5: [
        "Most small business websites are brochures.",
        "They just sit there.",
        "Yours should bring the work in. It should answer, sell, take payment and get found, while you're on the tools.",
        "Plug in what you need. An A.I. chatbot that answers at eleven p.m. An online store that sells while you sleep. Card, Apple Pay and Google Pay. Live 3D that stops the scroll. A.I. search, so ChatGPT can find you. And follow-ups drafted for your tap.",
        "Built in days, not months. Five-page sites from fourteen hundred and ninety dollars, with no monthly platform fee.",
        "Nothing goes live without your OK. Domain and code in your name. Yours outright.",
        "Build the site that brings the work in. " + SITE,
    ],
}
for _ad in ADS:
    assert len(VO[_ad["id"]]) == len(_ad["scenes"]), _ad["slug"]
