# Generator: writes the three static HTML pages (/, /it/, /fr/) from one template.
# Usage: python _build/build.py   (from anywhere; output goes to the repository root)
import html, json, math, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://ouija1733.github.io/"
NB = "\u202f"  # narrow no-break space for French punctuation

EMAIL = "menestrina.simone@gmail.com"
LINKEDIN = "https://www.linkedin.com/in/simone-menestrina/"
GITHUB = "https://github.com/Ouija1733"

LANGS = ["en", "it", "fr"]
PATH = {"en": "", "it": "it/", "fr": "fr/"}
LOCALE = {"en": "en_US", "it": "it_IT", "fr": "fr_FR"}
NAME = {"en": "English", "it": "Italiano", "fr": "Français"}

# ---------- Line icons (24x24, stroke = currentColor) ----------
ICONS = {
    "web": '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 9h18"/><path d="M6.5 6.5h.01M9 6.5h.01"/><path d="M7 13h6M7 16h10"/>',
    "ai": '<path d="M11 3.5l1.9 5 5 1.9-5 1.9-1.9 5-1.9-5-5-1.9 5-1.9z"/><path d="M18.5 15l.8 2 2 .8-2 .8-.8 2-.8-2-2-.8 2-.8z"/>',
    "devices": '<rect x="2.5" y="4" width="13" height="10" rx="1.5"/><path d="M6 18h6M9 14v4"/><rect x="17" y="8" width="4.5" height="12" rx="1.2"/><path d="M19.25 17.5h.01"/>',
    "upgrade": '<path d="M20 11a8 8 0 0 0-14.7-4.4L4 8"/><path d="M4 4v4h4"/><path d="M4 13a8 8 0 0 0 14.7 4.4L20 16"/><path d="M20 20v-4h-4"/>',
    "bag": '<path d="M5 8h14l-1.2 12H6.2z"/><path d="M9 10V7a3 3 0 0 1 6 0v3"/>',
    "package": '<path d="M3.5 7.5 12 3.5l8.5 4L12 11.5z"/><path d="M3.5 7.5v9L12 20.5l8.5-4v-9"/><path d="M12 11.5v9"/><path d="M7.75 5.5l8.5 4"/>',
    "key": '<circle cx="8" cy="15" r="4"/><path d="M11 12l8.5-8.5"/><path d="M16.5 6.5l2.5 2.5"/><path d="M14 9l2 2"/>',
    "clock": '<rect x="6" y="2.5" width="12" height="19" rx="2"/><circle cx="12" cy="12" r="3.5"/><path d="M12 10.5V12l1 .8"/><path d="M11 18.5h2"/>',
    "columns": '<path d="M3 9.5 12 4l9 5.5"/><path d="M5.5 10.5v7M10 10.5v7M14 10.5v7M18.5 10.5v7"/><path d="M3 20.5h18"/>',
    "code": '<path d="M8 7l-5 5 5 5"/><path d="M16 7l5 5-5 5"/><path d="M13.5 4.5l-3 15"/>',
    "braces": '<path d="M8 4H7a2 2 0 0 0-2 2v3.5a2.5 2.5 0 0 1-2 2.5 2.5 2.5 0 0 1 2 2.5V18a2 2 0 0 0 2 2h1"/><path d="M16 4h1a2 2 0 0 1 2 2v3.5a2.5 2.5 0 0 0 2 2.5 2.5 2.5 0 0 0-2 2.5V18a2 2 0 0 1-2 2h-1"/>',
    "hexagon": '<path d="M12 2.8l8 4.6v9.2l-8 4.6-8-4.6V7.4z"/><circle cx="12" cy="12" r="2.5"/>',
    "terminal": '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M7 9.5l3 2.5-3 2.5"/><path d="M12.5 15h4.5"/>',
    "layers": '<path d="M12 3.5l9 4.75-9 4.75-9-4.75z"/><path d="M3 12.5l9 4.75 9-4.75"/><path d="M3 16.5l9 4.75 9-4.75"/>',
    "database": '<ellipse cx="12" cy="5.5" rx="7.5" ry="2.75"/><path d="M4.5 5.5v13c0 1.5 3.4 2.75 7.5 2.75s7.5-1.25 7.5-2.75v-13"/><path d="M4.5 12c0 1.5 3.4 2.75 7.5 2.75s7.5-1.25 7.5-2.75"/>',
    "chip": '<rect x="6" y="6" width="12" height="12" rx="2"/><path d="M10 10h4v4h-4z"/><path d="M9.5 2.5V6M14.5 2.5V6M9.5 18v3.5M14.5 18v3.5M2.5 9.5H6M2.5 14.5H6M18 9.5h3.5M18 14.5h3.5"/>',
    "chat": '<path d="M4.5 4.5h15a1.5 1.5 0 0 1 1.5 1.5v9a1.5 1.5 0 0 1-1.5 1.5H12l-4.5 3.5v-3.5h-3A1.5 1.5 0 0 1 3 15V6a1.5 1.5 0 0 1 1.5-1.5z"/><path d="M8 10.5h.01M12 10.5h.01M16 10.5h.01"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3.5 7l8.5 6 8.5-6"/>',
    "profile": '<rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="9" cy="10" r="2.25"/><path d="M5.5 16.5a3.6 3.6 0 0 1 7 0"/><path d="M15 9.5h3M15 13h3"/>',
    "branch": '<circle cx="6.5" cy="5.5" r="2.25"/><circle cx="6.5" cy="18.5" r="2.25"/><circle cx="17.5" cy="7.5" r="2.25"/><path d="M6.5 7.75v8.5"/><path d="M17.5 9.75V11a4 4 0 0 1-4 4h-3a4 4 0 0 0-4 1"/>',
    "alert": '<circle cx="12" cy="12" r="9"/><path d="M12 7.5v5.5"/><path d="M12 16.5h.01"/>',
    "blocks": '<rect x="3.5" y="13" width="7.5" height="7.5" rx="1.25"/><rect x="13" y="13" width="7.5" height="7.5" rx="1.25"/><rect x="8.25" y="3.5" width="7.5" height="7.5" rx="1.25"/>',
    "check": '<circle cx="12" cy="12" r="9"/><path d="M8 12.5l2.75 2.75L16.5 9.5"/>',
    "external": '<path d="M7 17 17 7"/><path d="M8.5 7H17v8.5"/>',
}


def icon(name, cls="icon"):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{ICONS[name]}</svg>')


T = {}

T["en"] = dict(
    title="Simone Menestrina (Ouija) — Full Stack Developer and AI Integration Specialist",
    og_title="Simone Menestrina (Ouija) — Full Stack Developer",
    desc="Simone Menestrina, aka Ouija: full stack developer in Genova with about 6 years of experience building custom web platforms, management systems, desktop and mobile apps and AI integrations.",
    skip="Skip to content", menu="Menu", nav_label="Main", lang_label="Language",
    nav=["About", "What I do", "Lanterna", "Case studies", "Stack", "Experience", "Contact"],
    yes="YES", no="NO",
    kicker="Genova — about 6 years of experience",
    role="Full Stack Developer and AI Integration Specialist",
    bridge="I sign my work as <strong>Ouija</strong>. Like the board, I act as a bridge between people’s ideas and technology.",
    mascot_alt="Ouija, Simone’s mascot: a cartoon character with a dark beret, a white skull-like face, a long braid and fingerless gloves.",
    labels=["About", "What I do", "Personal project", "Case studies", "Stack", "Experience and education", "Contact"],
    about_title="Turning what clients need into software that works.",
    profile="<strong>I turn what clients need into software that works.</strong> For about 6 years I have built custom web platforms, management systems, desktop and mobile apps and AI integrations at a software house in Genova, handling projects end to end, from scoping to support after launch.",
    facts=[("Based in", "Genova, Italy"), ("Experience", "About 6 years"), ("Signature", "Ouija")],
    services_title="Software built end to end.",
    services=[
        ("Web apps and management systems", "Custom web platforms and management systems, handled end to end, from scoping to support after launch."),
        ("AI integrations", "Chatbots connected to product catalogues and order data, and AI-assisted OCR pipelines that extract data from invoices and ID documents."),
        ("Desktop and mobile apps", "Desktop apps with Electron and cross-platform mobile apps with Ionic, connected to Laravel backends via REST API."),
        ("Upgrades and maintenance", "Upgrading existing platforms, such as moving from Laravel 8 to Laravel 12, and support after launch."),
    ],
    lanterna_sub="Modular personal assistant",
    lanterna_status="In progress",
    lanterna=[
        ("What it is", "A modular personal assistant I’m building in Laravel, developed with AI-assisted tools (Claude Code)."),
        ("First module", "Job-search automation: generating tailored, ATS-friendly CVs and managing applications."),
        ("Next modules", "Freelance work, expenses and budget, diet and training."),
        ("Status", "Private repository, in active development."),
    ],
    cases_title="Selected work.",
    cases_note="Clients are kept anonymous.",
    case_labels=("Problem", "What I built", "Result"),
    cases=[
        ("Cremation services sector", "Large Laravel management platform",
         "The client ran on an old AS/400 system and a lot of paper. Communication with funeral homes was inefficient, every member notice went out as a letter, and there was no digital archive of cases.",
         ["A digital case archive and case management, with each cremation assigned to a furnace and a time slot",
          "Furnace emissions tracking, with reports to the authorities when limits are exceeded",
          "Niche management: who rests in each niche, who pays for it and who is behind on payments, membership fees and subscriptions included",
          "Smarter member communications: email to everyone who has one, letters only for the rest",
          "More effective communication with funeral homes",
          "Built modules from scratch and upgraded the platform from Laravel 8 to Laravel 12, with queue-based bulk PDF generation, bank invoice imports and a companion Electron desktop app"],
         "AS/400 and paper workflows were replaced by one platform: cases, furnaces, emissions, niches, payments and member communications are all managed digitally."),
        ("E-commerce", "AI customer support chatbot",
         "Customers kept asking the same questions about products and their orders.",
         "A chatbot connected to the product catalogue and the order database.",
         "Customers get answers on products and order status at any time, without waiting for staff."),
        ("Import/export company", "Automated invoice processing",
         "Supplier invoices were read and typed into the system by hand.",
         "An AI-assisted OCR pipeline on OpenAI models, tuned on the company’s own documents.",
         "Invoice data is extracted automatically; staff review it instead of typing it."),
        ("Short-term rental platform", "ID document verification",
         "Guest identity documents had to be checked one by one.",
         "The same OCR technology adapted to read ID documents, with a human approving each result.",
         "Faster check-ins, with a person always in control of sensitive data."),
        ("Custom business app", "Staff time-tracking mobile app",
         "Hours and expenses were collected on paper and spreadsheets.",
         "A cross-platform Ionic app connected to a Laravel backend via REST API.",
         "Staff log hours from their phone; admin reports are generated automatically."),
    ],
    stack_title="Tools I work with.",
    stack_kind={"lang": "Language", "fw": "Framework", "rt": "Runtime", "infra": "Containers", "db": "Database", "ai": "AI API"},
    exp_title="Experience and education.",
    exp_h="Experience", edu_h="Education", lang_h="Languages",
    job_title="Full Stack Developer", job_where="Software house, Genova", job_meta="About 6 years",
    job_desc="Custom web platforms, management systems, desktop and mobile apps and AI integrations, handling projects end to end, from scoping to support after launch.",
    other_h="Other experience",
    other=["About one year in Java on a point-of-sale and cash-management system for shops and restaurants.",
           "Client relationships, project scoping and B2B sales materials."],
    edu_title="High school diploma in computer science", edu_where="I.I.S. Gastaldi-Abba, Genova",
    langs=[("Italian", "Native"), ("English", "C1")],
    contact_title="Get in touch.",
    new_tab="(opens in a new tab)",
    goodbye="GOODBYE",
    og_image_alt="Simone Menestrina, Full Stack Developer and AI Integration Specialist, next to the Ouija mascot.",
    board_title="Ouija board with the alphabet, the numbers, YES, NO and GOODBYE",
)

T["it"] = dict(
    title="Simone Menestrina (Ouija) — Sviluppatore full stack e specialista in integrazioni IA",
    og_title="Simone Menestrina (Ouija) — Sviluppatore full stack",
    desc="Simone Menestrina, in arte Ouija: sviluppatore full stack a Genova con circa 6 anni di esperienza in piattaforme web su misura, gestionali, app desktop e mobile e integrazioni di intelligenza artificiale.",
    skip="Vai al contenuto", menu="Menu", nav_label="Principale", lang_label="Lingua",
    nav=["Profilo", "Cosa faccio", "Lanterna", "Casi studio", "Stack", "Esperienza", "Contatti"],
    yes="SÌ", no="NO",
    kicker="Genova — circa 6 anni di esperienza",
    role="Sviluppatore full stack e specialista in integrazioni IA",
    bridge="Firmo i miei lavori come <strong>Ouija</strong>. Come la tavola, faccio da ponte tra le idee delle persone e la tecnologia.",
    mascot_alt="Ouija, la mascotte di Simone: un personaggio a fumetti con un basco scuro, un volto bianco simile a un teschio, una lunga treccia e guanti senza dita.",
    labels=["Profilo", "Cosa faccio", "Progetto personale", "Casi studio", "Stack", "Esperienza e formazione", "Contatti"],
    about_title="Trasformare le esigenze dei clienti in software che funziona.",
    profile="<strong>Trasformo le esigenze dei clienti in software che funziona.</strong> Da circa 6 anni realizzo piattaforme web su misura, gestionali, app desktop e mobile e integrazioni di intelligenza artificiale presso una software house di Genova, seguendo i progetti dall’inizio alla fine: dall’analisi all’assistenza dopo il rilascio.",
    facts=[("Sede", "Genova, Italia"), ("Esperienza", "Circa 6 anni"), ("Firma", "Ouija")],
    services_title="Software seguito dall’inizio alla fine.",
    services=[
        ("Web app e gestionali", "Piattaforme web su misura e gestionali, seguiti dall’inizio alla fine: dall’analisi all’assistenza dopo il rilascio."),
        ("Integrazioni IA", "Chatbot collegati a cataloghi prodotti e dati degli ordini, e pipeline OCR assistite dall’IA che estraggono i dati da fatture e documenti d’identità."),
        ("App desktop e mobile", "App desktop con Electron e app mobile multipiattaforma con Ionic, collegate a backend Laravel tramite API REST."),
        ("Upgrade e manutenzione", "Aggiornamento di piattaforme esistenti, come il passaggio da Laravel 8 a Laravel 12, e assistenza dopo il rilascio."),
    ],
    lanterna_sub="Assistente personale modulare",
    lanterna_status="In corso",
    lanterna=[
        ("Cos’è", "Un assistente personale modulare che sto sviluppando in Laravel, con l’aiuto di strumenti basati sull’IA (Claude Code)."),
        ("Primo modulo", "Automazione della ricerca di lavoro: generazione di CV personalizzati e ottimizzati per gli ATS, e gestione delle candidature."),
        ("Prossimi moduli", "Lavoro freelance, spese e budget, alimentazione e allenamento."),
        ("Stato", "Repository privato, in sviluppo attivo."),
    ],
    cases_title="Progetti selezionati.",
    cases_note="I clienti restano anonimi.",
    case_labels=("Problema", "Cosa ho realizzato", "Risultato"),
    cases=[
        ("Settore dei servizi di cremazione", "Grande piattaforma gestionale in Laravel",
         "Il cliente lavorava con un vecchio sistema AS/400 e moltissima carta. La comunicazione con le agenzie funebri era poco efficace, ogni comunicazione ai soci partiva come lettera e non esisteva un archivio digitale delle pratiche.",
         ["Archivio digitale e gestione delle pratiche, con ogni cremazione assegnata a un forno e a una fascia oraria",
          "Monitoraggio delle emissioni dei forni, con segnalazioni alle autorità quando si superano i limiti",
          "Gestione dei loculi: chi vi riposa, chi li paga e chi è in ritardo con i pagamenti, comprese quote sociali e abbonamenti",
          "Comunicazioni ai soci più intelligenti: email a chi ce l’ha, lettere solo a chi non ha un indirizzo email",
          "Comunicazione più efficace con le agenzie funebri",
          "Moduli sviluppati da zero e aggiornamento della piattaforma da Laravel 8 a Laravel 12, con generazione massiva di PDF tramite code, importazione delle fatture bancarie e un’app desktop Electron collegata"],
         "AS/400 e flussi cartacei sono stati sostituiti da un’unica piattaforma: pratiche, forni, emissioni, loculi, pagamenti e comunicazioni ai soci sono tutti gestiti in digitale."),
        ("E-commerce", "Chatbot IA per l’assistenza clienti",
         "I clienti facevano continuamente le stesse domande sui prodotti e sui loro ordini.",
         "Un chatbot collegato al catalogo prodotti e al database degli ordini.",
         "I clienti ottengono risposte su prodotti e stato degli ordini in qualsiasi momento, senza attendere il personale."),
        ("Azienda di import/export", "Elaborazione automatica delle fatture",
         "Le fatture dei fornitori venivano lette e inserite a mano nel sistema.",
         "Una pipeline OCR assistita dall’IA basata sui modelli OpenAI, messa a punto sui documenti dell’azienda.",
         "I dati delle fatture vengono estratti automaticamente; il personale li verifica invece di digitarli."),
        ("Piattaforma di affitti brevi", "Verifica dei documenti d’identità",
         "I documenti d’identità degli ospiti dovevano essere controllati uno per uno.",
         "La stessa tecnologia OCR adattata alla lettura dei documenti d’identità, con una persona che approva ogni risultato.",
         "Check-in più rapidi, con una persona sempre in controllo dei dati sensibili."),
        ("App aziendale su misura", "App mobile per la rilevazione delle ore del personale",
         "Ore e spese venivano raccolte su carta e fogli di calcolo.",
         "Un’app multipiattaforma in Ionic collegata a un backend Laravel tramite API REST.",
         "Il personale registra le ore dal telefono; i report per l’amministrazione vengono generati automaticamente."),
    ],
    stack_title="Gli strumenti con cui lavoro.",
    stack_kind={"lang": "Linguaggio", "fw": "Framework", "rt": "Runtime", "infra": "Container", "db": "Database", "ai": "API IA"},
    exp_title="Esperienza e formazione.",
    exp_h="Esperienza", edu_h="Formazione", lang_h="Lingue",
    job_title="Sviluppatore full stack", job_where="Software house, Genova", job_meta="Circa 6 anni",
    job_desc="Piattaforme web su misura, gestionali, app desktop e mobile e integrazioni di intelligenza artificiale, seguendo i progetti dall’inizio alla fine: dall’analisi all’assistenza dopo il rilascio.",
    other_h="Altre esperienze",
    other=["Circa un anno in Java su un sistema di punto vendita e gestione cassa per negozi e ristoranti.",
           "Gestione dei rapporti con i clienti, analisi dei progetti e materiali commerciali B2B."],
    edu_title="Diploma di scuola superiore in informatica", edu_where="I.I.S. Gastaldi-Abba, Genova",
    langs=[("Italiano", "Madrelingua"), ("Inglese", "C1")],
    contact_title="Scrivimi.",
    new_tab="(si apre in una nuova scheda)",
    goodbye="ARRIVEDERCI",
    og_image_alt="Simone Menestrina, Full Stack Developer and AI Integration Specialist, accanto alla mascotte Ouija.",
    board_title="Tavola Ouija con l’alfabeto, i numeri, SÌ, NO e ARRIVEDERCI",
)

T["fr"] = dict(
    title="Simone Menestrina (Ouija) — Développeur full stack et spécialiste de l’intégration d’IA",
    og_title="Simone Menestrina (Ouija) — Développeur full stack",
    desc=f"Simone Menestrina, alias Ouija{NB}: développeur full stack à Gênes avec environ 6 ans d’expérience en plateformes web sur mesure, logiciels de gestion, applications desktop et mobiles et intégrations d’IA.",
    skip="Aller au contenu", menu="Menu", nav_label="Principale", lang_label="Langue",
    nav=["Profil", "Ce que je fais", "Lanterna", "Études de cas", "Stack", "Parcours", "Contact"],
    yes="OUI", no="NON",
    kicker="Gênes — environ 6 ans d’expérience",
    role="Développeur full stack et spécialiste de l’intégration d’IA",
    bridge="Je signe mon travail sous le nom d’<strong>Ouija</strong>. Comme la planche, je fais le lien entre les idées des gens et la technologie.",
    mascot_alt=f"Ouija, la mascotte de Simone{NB}: un personnage de bande dessinée avec un béret sombre, un visage blanc en forme de crâne, une longue tresse et des mitaines.",
    labels=["Profil", "Ce que je fais", "Projet personnel", "Études de cas", "Stack technique", "Expérience et formation", "Contact"],
    about_title="Transformer les besoins des clients en logiciels qui fonctionnent.",
    profile="<strong>Je transforme les besoins de mes clients en logiciels qui fonctionnent.</strong> Depuis environ 6 ans, je développe des plateformes web sur mesure, des logiciels de gestion, des applications desktop et mobiles et des intégrations d’IA au sein d’une société de développement logiciel à Gênes, en suivant les projets de bout en bout, du cadrage au support après la mise en production.",
    facts=[("Basé à", "Gênes, Italie"), ("Expérience", "Environ 6 ans"), ("Signature", "Ouija")],
    services_title="Des logiciels suivis de bout en bout.",
    services=[
        ("Applications web et logiciels de gestion", f"Plateformes web sur mesure et logiciels de gestion, suivis de bout en bout{NB}: du cadrage au support après la mise en production."),
        ("Intégrations d’IA", "Chatbots connectés aux catalogues produits et aux données de commandes, et pipelines OCR assistés par IA qui extraient les données des factures et des pièces d’identité."),
        ("Applications desktop et mobiles", "Applications desktop avec Electron et applications mobiles multiplateformes avec Ionic, connectées à des backends Laravel via API REST."),
        ("Mises à niveau et maintenance", "Mise à niveau de plateformes existantes, comme le passage de Laravel 8 à Laravel 12, et support après la mise en production."),
    ],
    lanterna_sub="Assistant personnel modulaire",
    lanterna_status="En cours",
    lanterna=[
        ("Ce que c’est", "Un assistant personnel modulaire que je développe en Laravel, avec l’aide d’outils basés sur l’IA (Claude Code)."),
        ("Premier module", f"Automatisation de la recherche d’emploi{NB}: génération de CV personnalisés et compatibles ATS, et gestion des candidatures."),
        ("Prochains modules", "Travail en freelance, dépenses et budget, alimentation et entraînement."),
        ("Statut", "Dépôt privé, en développement actif."),
    ],
    cases_title="Travaux choisis.",
    cases_note="Les clients restent anonymes.",
    case_labels=("Problème", "Ce que j’ai réalisé", "Résultat"),
    cases=[
        ("Secteur des services de crémation", "Grande plateforme de gestion Laravel",
         "Le client travaillait avec un ancien système AS/400 et énormément de papier. La communication avec les pompes funèbres était peu efficace, chaque courrier aux adhérents partait par la poste et il n’existait aucune archive numérique des dossiers.",
         ["Une archive numérique et la gestion des dossiers, chaque crémation étant attribuée à un four et à un créneau horaire",
          "Le suivi des émissions des fours, avec des signalements aux autorités en cas de dépassement des limites",
          f"La gestion des columbariums{NB}: qui y repose, qui paie et qui est en retard de paiement, cotisations et abonnements compris",
          f"Des communications plus intelligentes avec les adhérents{NB}: un e-mail à ceux qui en ont un, un courrier uniquement pour les autres",
          "Une communication plus efficace avec les pompes funèbres",
          "Des modules développés de zéro et la migration de la plateforme de Laravel 8 à Laravel 12, avec génération massive de PDF par files d’attente, import des factures bancaires et une application de bureau Electron associée"],
         f"L’AS/400 et les processus papier ont été remplacés par une plateforme unique{NB}: dossiers, fours, émissions, columbariums, paiements et communications avec les adhérents sont tous gérés numériquement."),
        ("E-commerce", "Chatbot IA de support client",
         "Les clients posaient sans cesse les mêmes questions sur les produits et leurs commandes.",
         "Un chatbot connecté au catalogue produits et à la base de données des commandes.",
         "Les clients obtiennent à tout moment des réponses sur les produits et l’état de leurs commandes, sans attendre le personnel."),
        ("Entreprise d’import-export", "Traitement automatisé des factures",
         "Les factures fournisseurs étaient lues et saisies à la main dans le système.",
         "Un pipeline OCR assisté par IA reposant sur les modèles OpenAI, ajusté sur les documents propres à l’entreprise.",
         f"Les données des factures sont extraites automatiquement{NB}; le personnel les vérifie au lieu de les saisir."),
        ("Plateforme de location courte durée", "Vérification des pièces d’identité",
         "Les pièces d’identité des voyageurs devaient être contrôlées une par une.",
         "La même technologie OCR adaptée à la lecture des pièces d’identité, avec une personne qui valide chaque résultat.",
         "Des check-ins plus rapides, avec toujours une personne aux commandes des données sensibles."),
        ("Application métier sur mesure", "Application mobile de suivi du temps du personnel",
         "Les heures et les dépenses étaient collectées sur papier et dans des tableurs.",
         "Une application multiplateforme Ionic connectée à un backend Laravel via une API REST.",
         f"Le personnel saisit ses heures depuis son téléphone{NB}; les rapports administratifs sont générés automatiquement."),
    ],
    stack_title="Les outils avec lesquels je travaille.",
    stack_kind={"lang": "Langage", "fw": "Framework", "rt": "Runtime", "infra": "Conteneurs", "db": "Base de données", "ai": "API d’IA"},
    exp_title="Expérience et formation.",
    exp_h="Expérience", edu_h="Formation", lang_h="Langues",
    job_title="Développeur full stack", job_where="Société de développement logiciel, Gênes", job_meta="Environ 6 ans",
    job_desc="Plateformes web sur mesure, logiciels de gestion, applications desktop et mobiles et intégrations d’IA, en suivant les projets de bout en bout, du cadrage au support après la mise en production.",
    other_h="Autres expériences",
    other=["Environ un an en Java sur un système de point de vente et de gestion de caisse pour commerces et restaurants.",
           "Relation client, cadrage de projets et supports commerciaux B2B."],
    edu_title="Diplôme d’études secondaires en informatique", edu_where="I.I.S. Gastaldi-Abba, Gênes",
    langs=[("Italien", "Langue maternelle"), ("Anglais", "C1")],
    contact_title="Me contacter.",
    new_tab="(s’ouvre dans un nouvel onglet)",
    goodbye="AU REVOIR",
    og_image_alt="Simone Menestrina, Full Stack Developer and AI Integration Specialist, à côté de la mascotte Ouija.",
    board_title="Planche Ouija avec l’alphabet, les chiffres, OUI, NON et AU REVOIR",
)

SERVICE_ICONS = ["web", "ai", "devices", "upgrade"]
CASE_ICONS = ["columns", "bag", "package", "key", "clock"]  # same order as T[*]["cases"]
STACK = [
    ("PHP / Laravel", "fw", "code"), ("JavaScript / TypeScript", "lang", "braces"), ("Node.js", "rt", "hexagon"),
    ("Python", "lang", "terminal"), ("Docker", "infra", "layers"), ("MySQL", "db", "database"),
    ("OpenAI API", "ai", "chip"), ("Claude API", "ai", "chat"),
]

# ---------- "Ask the board" FAQ: one editable file per language in _build/faq/ ----------
BOARD_CHARS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ")


def load_faq(lang):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "faq", f"{lang}.json")
    with open(path, encoding="utf-8") as f:
        faq = json.load(f)
    ids = {t["id"] for t in faq["topics"]}
    for item in faq["topics"] + [faq["fallback"]]:
        bad = set(item["word"]) - BOARD_CHARS
        if bad:
            raise SystemExit(f"{path}: word {item['word']!r} uses characters not on the board: {''.join(sorted(bad))}")
    for g in faq["guided"]:
        if g["topic"] not in ids:
            raise SystemExit(f"{path}: guided question points to unknown topic {g['topic']!r}")
    if lang == "fr":  # French spacing before : ; ? !
        def nb(x):
            return re.sub(r" ([:;?!])", NB + r"\1", x)
        for k in ("label", "prefix", "empty", "guided_label"):
            faq[k] = nb(faq[k])
        for item in faq["guided"]:
            item["question"] = nb(item["question"])
        for item in faq["topics"] + [faq["fallback"]]:
            item["text"] = nb(item["text"])
    return faq


# ---------- The Ouija board (one inline SVG, viewBox units) ----------
BOARD_W, BOARD_H = 760, 520
ARC_CX, ARC_CY = 380, 760          # shared centre of the two letter arcs
REST = (380, 352)                  # planchette rest point: centre of the board

# Planchette drawn around its window, which sits at (0, 0)
PLANCHETTE_PATH = "M0 -62C21 -44 48 -16 44 12C40 40 -40 40 -44 12C-48 -16 -21 -44 0 -62Z"


def board_svg(t):
    glyphs = []

    def glyph(key, label, x, y, size, rot=0.0, keep=False):
        tr = f' transform="rotate({rot:.2f} {x:.1f} {y:.1f})"' if abs(rot) > 0.01 else ""
        a = f'x="{x:.1f}" y="{y:.1f}"{tr}'
        cls = "glyph keep" if keep else "glyph"
        glyphs.append(
            f'<g class="{cls}" data-ch="{key}" data-x="{x:.1f}" data-y="{y:.1f}" style="font-size:{size}px">'
            f'<text class="g-base" {a}>{label}</text><text class="g-lit" {a} filter="url(#bd-glow)">{label}</text></g>'
        )

    def arc(chars, radius, half_width, size):
        right = math.degrees(math.acos(half_width / radius))
        step = (180 - 2 * right) / (len(chars) - 1)
        for i, c in enumerate(chars):
            th = 180 - right - i * step
            x = ARC_CX + radius * math.cos(math.radians(th))
            y = ARC_CY - radius * math.sin(math.radians(th))
            glyph(c, c, x, y, size, 90 - th, keep=c in "OUIJA")

    arc("ABCDEFGHIJKLM", 580, 292, 46)
    arc("NOPQRSTUVWXYZ", 488, 256, 42)
    for i, c in enumerate("1234567890"):
        glyph(c, c, 170 + i * (420 / 9), 412, 30)
    glyph("YES", t["yes"], 132, 64, 30)
    glyph("NO", t["no"], 628, 64, 30)
    glyph("GOODBYE", t["goodbye"], 380, 474, 22)

    rx, ry = REST
    # Rules either side of GOODBYE, sized to the translated word (~0.94em per letter with tracking)
    half = len(t["goodbye"]) * 22 * 0.94 / 2 + 14
    gl, gr = 380 - half, 380 + half
    trail = "".join(f'<circle r="{4 - i * 0.4:.1f}" cx="0" cy="0"/>' for i in range(7))
    rays = "".join(
        f'<path d="M{58 + 11 * math.cos(a):.1f} {64 + 11 * math.sin(a):.1f}L{58 + 16 * math.cos(a):.1f} {64 + 16 * math.sin(a):.1f}"/>'
        for a in [k * math.pi / 4 for k in range(8)]
    )

    return f'''<svg class="board-svg" viewBox="0 0 {BOARD_W} {BOARD_H}" role="img" aria-labelledby="board-title" data-rest-x="{rx}" data-rest-y="{ry}">
            <title id="board-title">{t["board_title"]}</title>
            <defs>
              <filter id="bd-glow" x="-60%" y="-60%" width="220%" height="220%">
                <feGaussianBlur in="SourceGraphic" stdDeviation="3.2" result="blur"/>
                <feComponentTransfer in="blur" result="soft"><feFuncA type="linear" slope="0.75"/></feComponentTransfer>
                <feMerge><feMergeNode in="soft"/><feMergeNode in="SourceGraphic"/></feMerge>
              </filter>
              <clipPath id="pl-window"><circle r="21" cx="0" cy="0"/></clipPath>
            </defs>
            <rect class="bd-face" x="6" y="6" width="{BOARD_W - 12}" height="{BOARD_H - 12}" rx="22"/>
            <rect class="bd-inner" x="18" y="18" width="{BOARD_W - 36}" height="{BOARD_H - 36}" rx="13"/>
            <g class="bd-ornament">
              <circle cx="58" cy="64" r="7"/>{rays}
              <path d="M716 51A12 12 0 1 0 716 73A13 13 0 0 1 716 51Z"/>
              <path d="M{gl - 60:.0f} 474H{gl:.0f}M{gr:.0f} 474H{gr + 60:.0f}"/>
              <circle cx="{gl - 68:.0f}" cy="474" r="1.6"/><circle cx="{gr + 68:.0f}" cy="474" r="1.6"/>
            </g>
            <g id="bd-glyphs" class="bd-glyphs">
              {"".join(glyphs)}
            </g>
            <g class="pl-trail" aria-hidden="true">{trail}</g>
            <g class="pl" transform="translate({rx} {ry})">
              <g class="pl-body">
                <path class="pl-shape" d="{PLANCHETTE_PATH}"/>
                <circle class="pl-tip" cx="0" cy="-42" r="2.2"/>
                <path class="pl-deco" d="M-26 22Q0 32 26 22"/>
              </g>
              <g clip-path="url(#pl-window)">
                <circle class="pl-glass" r="21"/>
                <g class="pl-lens" transform="scale(1.2) translate({-rx} {-ry})"><use href="#bd-glyphs"/></g>
              </g>
              <circle class="pl-ring" r="21"/>
            </g>
          </svg>'''


IDS = ["about", "services", "lanterna", "case-studies", "stack", "experience", "contact"]


def rv(i=0, step=70):
    """Reveal-on-scroll hook; --d staggers siblings."""
    return f'data-reveal style="--d: {i * step}ms"' if i else "data-reveal"


def page(lang):
    t = T[lang]
    up = "" if lang == "en" else "../"
    url = SITE + PATH[lang]

    def rel(target):
        if target == lang:
            return "./"
        return up + PATH[target] if PATH[target] else (up or "./")

    alt_links = "\n".join(
        f'  <link rel="alternate" hreflang="{l}" href="{SITE + PATH[l]}">' for l in LANGS
    ) + f'\n  <link rel="alternate" hreflang="x-default" href="{SITE}">'
    og_alt = "\n".join(
        f'  <meta property="og:locale:alternate" content="{LOCALE[l]}">' for l in LANGS if l != lang
    )

    lang_items = []
    for l in LANGS:
        cur = ' aria-current="page"' if l == lang else ""
        lang_items.append(
            f'<li><a href="{rel(l)}" hreflang="{l}" lang="{l}"{cur}>{l.upper()}<span class="sr-only"> – {NAME[l]}</span></a></li>'
        )

    nav_items = "\n".join(
        f'            <li><a href="#{i}">{n}</a></li>' for i, n in zip(IDS, t["nav"])
    )

    def head(n, title_html=""):
        lab = f'<p class="section-label mono" {rv()}>{n + 1:02d} / {t["labels"][n]}</p>'
        return lab + ("\n          " + title_html if title_html else "")


    faq = load_faq(lang)
    faq_data = {
        "topics": [{"id": x["id"], "word": x["word"], "text": x["text"], "keywords": x["keywords"]} for x in faq["topics"]],
        "fallback": faq["fallback"],
    }
    guided = "\n".join(
        f'                <li><button class="ask-chip" type="button" data-topic="{g["topic"]}">{html.escape(g["question"])}</button></li>'
        for g in faq["guided"]
    )

    facts = "\n".join(
        f'            <div><dt class="mono">{k}</dt><dd>{v}</dd></div>' for k, v in t["facts"]
    )

    services = "\n".join(
        f'''          <li class="service" {rv(i)}>
            <div class="service-top">{icon(SERVICE_ICONS[i], "icon icon-lg")}<span class="service-num mono" aria-hidden="true">{i + 1:02d}</span></div>
            <h3>{h}</h3>
            <p>{p}</p>
          </li>''' for i, (h, p) in enumerate(t["services"])
    )

    lanterna = "\n".join(
        f'            <div><dt class="mono">{k}</dt><dd>{v}</dd></div>' for k, v in t["lanterna"]
    )

    lp, lb, lr = t["case_labels"]
    cases = []
    for i, (sector, title, prob, built, res) in enumerate(t["cases"]):
        featured = i == 0
        if isinstance(built, list):
            built = "<ul>" + "".join(f"<li>{b}</li>" for b in built) + "</ul>"
        cls = "case case--featured" if featured else "case"
        cases.append(f'''          <li class="{cls}" {rv(0 if featured else (i - 1) % 2 + 1)}>
            <div class="case-head">
              <span class="case-icon">{icon(CASE_ICONS[i])}</span>
              <div>
                <p class="case-sector mono">{sector}</p>
                <h3>{title}</h3>
              </div>
            </div>
            <dl>
              <div class="f-problem"><dt class="mono">{icon("alert", "icon icon-xs")}{lp}</dt><dd>{prob}</dd></div>
              <div class="f-built"><dt class="mono">{icon("blocks", "icon icon-xs")}{lb}</dt><dd>{built}</dd></div>
              <div class="f-result"><dt class="mono">{icon("check", "icon icon-xs")}{lr}</dt><dd>{res}</dd></div>
            </dl>
          </li>''')
    cases = "\n".join(cases)

    stack = "\n".join(
        f'          <li {rv(i % 4, 60)}>{icon(ic)}<span class="stack-name">{name}</span><span class="mono">{t["stack_kind"][k]}</span></li>'
        for i, (name, k, ic) in enumerate(STACK)
    )

    other = "".join(f"<li>{o}</li>" for o in t["other"])
    langs = "\n".join(
        f'              <div><dt>{k}</dt><dd>{v}</dd></div>' for k, v in t["langs"]
    )

    nt = f'<span class="sr-only"> {t["new_tab"]}</span>'
    contacts = [
        ("mail", "Email", f"mailto:{EMAIL}", EMAIL, False),
        ("profile", "LinkedIn", LINKEDIN, "linkedin.com/in/simone-menestrina", True),
        ("branch", "GitHub", GITHUB, "github.com/Ouija1733", True),
    ]
    contact_items = "\n".join(
        f'          <li {rv(i)}><a href="{href}"'
        + (' target="_blank" rel="me noopener"' if ext else "")
        + f'><span class="contact-label mono">{icon(ic)}{lab}</span><span class="contact-value">{val}</span>'
        + (nt if ext else "")
        + f'{icon("external", "icon contact-arrow")}</a></li>'
        for i, (ic, lab, href, val, ext) in enumerate(contacts)
    )

    return f'''<!doctype html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{t["title"]}</title>
  <meta name="description" content="{html.escape(t["desc"])}">
  <meta name="author" content="Simone Menestrina">
  <meta name="theme-color" content="#1C2230">
  <link rel="canonical" href="{url}">
{alt_links}

  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Simone Menestrina — Ouija">
  <meta property="og:title" content="{html.escape(t["og_title"])}">
  <meta property="og:description" content="{html.escape(t["desc"])}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{SITE}assets/og-image.png">
  <meta property="og:image:type" content="image/png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="{html.escape(t["og_image_alt"])}">
  <meta property="og:locale" content="{LOCALE[lang]}">
{og_alt}
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:image:alt" content="{html.escape(t["og_image_alt"])}">

  <link rel="icon" href="{up}assets/favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="{up}assets/ouija.png">

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400..800&amp;family=IBM+Plex+Mono:wght@400;500&amp;display=swap">
  <link rel="stylesheet" href="{up}assets/css/style.css">
  <script>
    /* Motion is opt-in: only with JS, only without reduced motion, and undone if main.js never runs. */
    (function (d) {{
      d.classList.add("js");
      if (window.matchMedia && !matchMedia("(prefers-reduced-motion: reduce)").matches) {{
        d.classList.add("motion");
        setTimeout(function () {{ if (!window.ouijaReady) d.classList.remove("motion"); }}, 2500);
      }}
    }})(document.documentElement);
  </script>
  <script src="{up}assets/js/main.js" defer></script>
</head>
<body>
  <a class="skip-link" href="#main">{t["skip"]}</a>

  <header class="site-header">
    <div class="wrap header-inner">
      <a class="brand" href="#top"><span class="brand-mark" aria-hidden="true"></span>Ouija</a>

      <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">
        <span class="nav-toggle-icon" aria-hidden="true"></span>{t["menu"]}
      </button>

      <nav class="site-nav" id="site-nav" aria-label="{t["nav_label"]}">
        <ul>
{nav_items}
        </ul>
      </nav>

      <nav class="lang-switch" aria-label="{t["lang_label"]}">
        <ul>
          {"".join(lang_items)}
        </ul>
      </nav>
    </div>
  </header>

  <main id="main" tabindex="-1">
    <section class="hero" id="top" aria-labelledby="hero-name">
      <div class="wrap">
        <div class="hero-grid">
          <div>
            <p class="hero-kicker mono" {rv()}>{t["kicker"]}</p>
            <h1 class="hero-name" id="hero-name" {rv(1, 90)}>Simone<br>Menestrina</h1>
            <p class="hero-role" {rv(2, 90)}>{t["role"]}</p>
            <p class="hero-bridge" {rv(3, 90)}>{t["bridge"]}</p>
          </div>

          <figure class="mascot">
            <span class="mascot-float"><img src="{up}assets/ouija.png" width="377" height="543" alt="{html.escape(t["mascot_alt"])}" fetchpriority="high"></span>
            <figcaption class="mono">Ouija</figcaption>
          </figure>
        </div>

        <div class="board">
          {board_svg(t)}

          <p class="ask-answer" id="ask-answer" aria-live="polite"></p>

          <form class="ask" id="ask" autocomplete="off" data-faq="{html.escape(json.dumps(faq_data, ensure_ascii=False))}" data-prefix="{html.escape(faq["prefix"])}" data-empty="{html.escape(faq["empty"])}">
            <label class="ask-label mono" for="ask-q">{faq["label"]}</label>
            <div class="ask-row">
              <input class="ask-input" id="ask-q" name="q" type="text" maxlength="140" spellcheck="false">
              <button class="ask-button" type="submit">{faq["button"]}</button>
            </div>
            <div class="ask-guided" role="group" aria-labelledby="ask-guided-label">
              <p class="ask-guided-label mono" id="ask-guided-label">{faq["guided_label"]}</p>
              <ul>
{guided}
              </ul>
            </div>
          </form>
        </div>
      </div>
    </section>

    <section class="section" id="about" aria-labelledby="about-title">
      <div class="wrap">
        <div class="section-head">
          {head(0, f'<h2 class="section-title" id="about-title" {rv(1)}>{t["about_title"]}</h2>')}
        </div>
        <div class="about-grid">
          <p class="lead" {rv()}>{t["profile"]}</p>
          <dl class="facts" {rv(2)}>
{facts}
          </dl>
        </div>
      </div>
    </section>

    <section class="section" id="services" aria-labelledby="services-title">
      <div class="wrap">
        <div class="section-head">
          {head(1, f'<h2 class="section-title" id="services-title" {rv(1)}>{t["services_title"]}</h2>')}
        </div>
        <ul class="services">
{services}
        </ul>
      </div>
    </section>

    <section class="section" id="lanterna" aria-labelledby="lanterna-title">
      <div class="wrap">
        <div class="section-head">
          {head(2)}
        </div>
        <article class="feature" {rv(1)}>
          <div>
            <h2 class="feature-title" id="lanterna-title">Lanterna</h2>
            <p class="feature-sub">{t["lanterna_sub"]}</p>
            <p class="status mono">{t["lanterna_status"]}</p>
          </div>
          <dl class="feature-list">
{lanterna}
          </dl>
        </article>
      </div>
    </section>

    <section class="section" id="case-studies" aria-labelledby="cases-title">
      <div class="wrap">
        <div class="section-head">
          {head(3, f'<h2 class="section-title" id="cases-title" {rv(1)}>{t["cases_title"]}</h2>')}
          <p class="section-note mono" {rv(2)}>{t["cases_note"]}</p>
        </div>
        <ul class="cases">
{cases}
        </ul>
      </div>
    </section>

    <section class="section" id="stack" aria-labelledby="stack-title">
      <div class="wrap">
        <div class="section-head">
          {head(4, f'<h2 class="section-title" id="stack-title" {rv(1)}>{t["stack_title"]}</h2>')}
        </div>
        <ul class="stack">
{stack}
        </ul>
      </div>
    </section>

    <section class="section" id="experience" aria-labelledby="exp-title">
      <div class="wrap">
        <div class="section-head">
          {head(5, f'<h2 class="section-title" id="exp-title" {rv(1)}>{t["exp_title"]}</h2>')}
        </div>
        <div class="exp-grid">
          <div class="exp-col" {rv()}>
            <h3 class="mono">{t["exp_h"]}</h3>
            <div class="entry">
              <h4>{t["job_title"]}</h4>
              <p class="meta mono">{t["job_where"]} · {t["job_meta"]}</p>
              <p>{t["job_desc"]}</p>
            </div>
            <div class="entry">
              <h4>{t["other_h"]}</h4>
              <ul>{other}</ul>
            </div>
          </div>
          <div class="exp-col" {rv(2)}>
            <h3 class="mono">{t["edu_h"]}</h3>
            <div class="entry">
              <h4>{t["edu_title"]}</h4>
              <p class="meta mono">{t["edu_where"]} · 2021</p>
            </div>
            <h3 class="mono exp-sub">{t["lang_h"]}</h3>
            <dl class="langs">
{langs}
            </dl>
          </div>
        </div>
      </div>
    </section>

    <section class="section" id="contact" aria-labelledby="contact-title">
      <div class="wrap">
        <div class="section-head">
          {head(6, f'<h2 class="section-title" id="contact-title" {rv(1)}>{t["contact_title"]}</h2>')}
        </div>
        <ul class="contact-list">
{contact_items}
        </ul>
      </div>
    </section>
  </main>

  <footer class="site-footer">
    <div class="wrap footer-inner mono">
      <span>© Simone Menestrina · Ouija</span>
      <span class="goodbye" aria-hidden="true">{t["goodbye"]}</span>
    </div>
  </footer>
</body>
</html>
'''


for lang in LANGS:
    out = os.path.join(ROOT, PATH[lang].rstrip("/"), "index.html") if PATH[lang] else os.path.join(ROOT, "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(page(lang))
    print("wrote", out)
