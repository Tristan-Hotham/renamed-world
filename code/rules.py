"""Classification rules for the renamed-world study, kept in one place so that they can be read and checked.

1. TYPE_GROUP: what kind of thing each common Wikidata class (P31) is. Assigned by hand from a sample of item labels of each
   class (Wikidata class labels were not in the extract). Items of other classes are grouped from words in their English label.
2. LOCAL_LANG: the official and regional languages of each present-day country (ISO 3166 alpha-2), used to tell a change of
   the official name from a change of the name used in another language (an exonym).
3. ADMIN_WORDS: words for the status of a place (town, city, village, district, rural council and so on) that are removed
   before two names are compared, so that "X Town" becoming "X City" counts as a change of status, not a renaming.
4. RED_TOKENS: name parts that honour communist leaders, the revolution or the Soviet state.
5. The waves: COMMUNIST (countries and years of communist rule), INDEPENDENCE (year of independence of former colonies),
   WAR (places and years where borders moved after the World Wars), MERGER (countries and years of large municipal merger
   programmes), NATION (countries and years of nation-building and language policy).
Each rule is applied in the order set out in classify() in 01_events.py.
"""

# ---------------------------------------------------------------- 1. kinds of thing
_T = {
    "place": """Q484170 Q18663566 Q20541692 Q532 Q21672098 Q1059478 Q486972 Q34841063 Q494721 Q1549591 Q19730508 Q21869758
        Q7930989 Q28328984 Q27676428 Q515 Q659103 Q12397176 Q735428 Q12813115 Q14839548 Q2514025 Q192287 Q130212458 Q121366249
        Q12131624 Q2276925 Q28203007 Q1070990 Q5327369 Q424857 Q26211545 Q5084 Q666943 Q2590631 Q15630849 Q667509 Q3957 Q902814
        Q15921247 Q4224624 Q4100864 Q65661087 Q22674925 Q123705 Q253019 Q1137833 Q116457956 Q17376095 Q15303838 Q89487741
        Q42744322 Q106658 Q747074 Q5123999 Q20724701 Q1093829 Q15078955 Q21507948 Q2023000 Q24764 Q55558027 Q1145012 Q106389302
        Q828658 Q3558970 Q2983893 Q20019082 Q748149 Q2264924 Q5153359 Q15978299 Q7841907 Q7819319 Q8452914 Q85482556 Q41501164
        Q6784672 Q3199141 Q27676416 Q27676524 Q2074737 Q3055118 Q13526752 Q1802801 Q2989457 Q12357832
        Q5119 Q925381 Q200250 Q1637706 Q174844 Q965568 Q13218690 Q15127012""",
    "admin": """Q2198484 Q27002 Q4414033 Q1065118 Q19953632 Q634099 Q18524218 Q1289426 Q13626398 Q114072597 Q2643128 Q5283544
        Q3487904 Q1336099 Q13417250 Q43263 Q188604 Q3191695 Q4389115 Q141223669 Q2655841 Q118287888 Q1267632 Q7688 Q2577184
        Q525504 Q986065 Q18867465 Q56061 Q1115575 Q3700011 Q3024240""",
    "nature": """Q8502 Q207326 Q47521 Q124714 Q23397 Q18389975 Q23442 Q39594""",
    "street": """Q79007 Q1251403 Q174782 Q703941 Q207934 Q7543083 Q54114 Q907698 Q3558430 Q13634881 Q83620 Q2026833 Q22698
        Q22746 Q34442""",
    "station": """Q55488 Q4312270 Q85882206 Q123094976 Q4346602 Q122397434 Q332496 Q121844689 Q928830 Q22808403 Q2142091
        Q121844395 Q11670533 Q22808404 Q1147171 Q2175765 Q11606300 Q55678 Q105038730 Q953806 Q2451577 Q4663385 Q55485
        Q123025722 Q55491 Q106772341 Q7886778 Q1793804 Q123114662 Q11429081 Q27996460 Q1248784 Q94993988""",
}
TYPE_GROUP = {q: g for g, s in _T.items() for q in s.split()}
GROUP_ORDER = ["place", "admin", "nature", "street", "station", "institution", "other"]
GROUP_NAME = {"place": "Cities, towns and villages", "admin": "Districts, regions and other administrative areas",
              "nature": "Mountains, rivers, lakes and other natural features", "street": "Streets, squares and parks",
              "station": "Stations, stops and airports", "institution": "Universities, schools, museums, companies and other bodies",
              "other": "Other things"}
LABEL_WORDS = [  # (group, regular expression on the English label), first match wins
    ("station", r"\b(station|stop|halt|airport|bahnhof|metro)\b"),
    ("street", r"\b(street|lane|avenue|boulevard|square|road|alley|passage|embankment|prospekt|ulitsa|vulytsia|rue|allée|place|"
               r"quai|platz|straße|strasse|park|garden|bridge)\b|straße$"),
    ("institution", r"\b(university|college|school|academy|institute|museum|theatre|theater|hospital|library|arena|stadium|"
                    r"hotel|cinema|church|company|limited|ltd|inc|association|society|council of|ministry|department|"
                    r"centre|center|club|gallery|foundation|bank|factory|plant|corporation|gimnázium|gymnasium|sd negeri|lyceum)\b"),
    ("admin", r"\b(district|raion|rayon|county|oblast|province|prefecture|region|governorate|municipality|rural council|"
              r"rural settlement|urban okrug|canton|volost|uyezd|parish|subdistrict|regency|krai|republic)\b"),
    ("nature", r"\b(mountain|mount|peak|hill|butte|creek|river|lake|spring|bay|island|cove|valley|canyon|ridge|falls|glacier)\b"),
]
CORE = {"place", "admin"}          # the places in the headline counts

# ---------------------------------------------------------------- 2. languages
LOCAL_LANG = {
    "RU": "ru tt ba cv ce os sah kbd ady udm mhr kv myv mdf krc", "UA": "uk crh", "BY": "be be-tarask", "MD": "ro mo",
    "EE": "et", "LV": "lv", "LT": "lt", "GE": "ka", "AM": "hy", "AZ": "az", "KZ": "kk", "UZ": "uz", "TM": "tk", "KG": "ky",
    "TJ": "tg", "PL": "pl csb szl", "CZ": "cs", "SK": "sk", "HU": "hu", "RO": "ro", "BG": "bg", "DE": "de hsb dsb nds frr",
    "AT": "de", "CH": "de fr it rm gsw", "FR": "fr br oc co eu", "BE": "nl fr de", "NL": "nl fy", "LU": "lb fr de",
    "IT": "it de sc fur lld", "ES": "es gl ca eu ast an oc", "PT": "pt", "GB": "en cy gd ga kw sco", "IE": "ga en",
    "SE": "sv", "NO": "nb nn no se", "DK": "da", "FI": "fi sv se", "IS": "is", "GR": "el", "TR": "tr", "CY": "el tr",
    "RS": "sr sr-ec sr-el", "HR": "hr", "SI": "sl", "BA": "bs hr sr", "ME": "sr cnr", "MK": "mk", "AL": "sq", "XK": "sq sr",
    "JP": "ja", "CN": "zh zh-cn zh-hans zh-hant zh-tw zh-hk", "TW": "zh zh-tw zh-hant", "KR": "ko", "KP": "ko",
    "MN": "mn", "VN": "vi", "TH": "th", "ID": "id", "MY": "ms", "PH": "tl fil en", "IN": "hi en mr ta bn te kn ml gu pa or",
    "PK": "ur en", "BD": "bn", "LK": "si ta", "MM": "my", "IL": "he", "IR": "fa", "IQ": "ar ku", "SY": "ar", "EG": "ar",
    "DZ": "ar fr", "MA": "ar fr zgh", "TN": "ar fr", "US": "en es", "CA": "en fr", "AU": "en", "NZ": "en mi",
    "ZA": "en af zu xh", "MX": "es", "BR": "pt", "AR": "es", "CL": "es", "CD": "fr", "CG": "fr", "SN": "fr", "CI": "fr",
}
LOCAL_LANG = {k: set(v.split()) | {"mul"} for k, v in LOCAL_LANG.items()}
DISPLAY_PREF = ["en", "en-gb", "en-us", "mul"]

# ---------------------------------------------------------------- 3. status words
ADMIN_WORDS = r"""town|city|village|township|county|district|municipality|local municipality|district municipality|
    metropolitan municipality|borough|parish|raion|rayon|oblast|region|province|prefecture|rural council|rural settlement|
    urban okrug|urban-type settlement|selo|posyolok|stanitsa|khutor|commune|gemeinde|stadt|markt|kreis|landkreis|
    municipio|ayuntamiento|concello|comune|gmina|okres|járás|megye|silska rada|selyshchna rada|miska rada|hromada|
    autonomous county|subdistrict|county-level city|shi|machi|cho|chō|mura|son|gun|ku|
    город|село|деревня|посёлок|поселок|хутор|станица|аул|район|сельсовет|сельское поселение|городское поселение|
    городской округ|муниципальный район|рабочий посёлок|волость|смт|селище|місто|сільська рада|селищна рада|міська рада|
    громада|bezirksamt|kreis|okrug|aimak|аймак|округ|муниципальный округ|автономный район|автономная область|
    landgemeinde|stadtgemeinde|marktgemeinde|samtgemeinde|verbandsgemeinde|sous-préfecture|arrondissement|
    rajons|novads|pagasts|vald|vallasbuogas|kommun|kunta|kaupunki|herad|landskommun|köping|
    paroisse|village of|town of|city of|township of|kota besar|kota kecil|kota-besar|kota-kecil|kotapraja|kota|kabupaten|
    kecamatan|stadsgemeente|stadsgerneente|landschapsgemeente|landschapsgemente|муниципальное образование|сельское поселение|
    хошун|этрап|уезд|отдел|губерния|губернія|губернии|дистрикт|qəzası|qəza|uyezd|gubernia|governorate|сельский округ|сельский|vármegye|megye|etrap|nohiya|ноҳияи|tuman|kirkedistrikt|sogn|socken|församling|landskap|län|fylke|herred"""
ADMIN_WORDS = [w.strip() for w in ADMIN_WORDS.replace("\n", "").split("|") if w.strip()]
CJK_ADMIN = ["市", "町", "村", "区", "區", "郡", "县", "縣", "镇", "鎮", "乡", "鄉", "街道", "省", "州", "专区", "專區", "地区", "地區",
             "自治区", "自治州", "自治县", "工矿区", "特区", "新区", "林区", "盟", "旗", "大字", "字", "丁目", "面", "邑", "洞", "里", "군", "시", "읍", "면"]

# ---------------------------------------------------------------- 4. communist names
RED_TOKENS = """lenin stalin kirov sverdlov kalinin kuibyshev kuybyshev kujbyshev gorky gorkiy zhdanov voroshilov voroshylov molotov
    ordzhonikidze frunze dzerzhin dzerzhyn kotovsk chapaev chapaiev chapayev budyonn budenn budenov sovetsk radiansk radyansk
    oktyabr oktiabr zhovtn krasnoarm chervonoarm krasnogvard chervonohvard krasnoznamen proletar komsomolar
    pervomai pervomay pershotravn marks marx engels ilyich illich ulyanov ulianov krupsk shchors artemivsk artyomovsk artemovsk
    tolyatti togliatti telman thalmann dimitrov gottwald stalino titograd leninabad stalinabad kirovabad kalininabad
    ordzhonikidzeabad krasnodar karl-marx kolkhoz kolhosp radhosp sovkhoz chervonozavod chervonohrad chervonopartyzansk
    иленин ленин сталин киров свердлов калинин куйбышев горьк жданов ворошилов молотов орджоникидзе фрунзе дзержин котовск
    чапаев будённ буденн советск радянськ октябр жовтн красноарм червоноарм красногвард червоногвард краснознам пролетар
    комсомол коммун комун комунар первомай першотравн маркс энгельс енгельс ильич ілліч ульянов крупськ крупск щорс
    артемовск артемівськ артёмовск тольятти тельман димитров стаханов червоноград червонозавод колхоз колгосп радгосп совхоз
    имени імені лениакан ленинакан volodar володар чапаи червон жовтен перше_травня першого_травня 1_травня цюруп
    1_mai 23_august gheorghiu-dej petru_groza brezhnev брежнев andropov андропов shcherbakov щербаков torez торез
    tolbukhin толбухин zinov зинов manuil мануил днепропетровск дніпропетровськ dnipropetrovsk dnepropetrovsk
    լենին կալինին կիրով ստալին մարքս սովետ հոկտեմբեր կոմսոմոլ օրջոնիկիձե ժդանով կոմունար կարմիր
    ლენინ სტალინ კიროვ კალინინ ორჯონიკიძე მახარაძე წითელ
    frunz фрунз komintern коминтерн комінтерн revoliuts revolyuts революц uritsk урицк урицьк lunachar луначар
    menzhinsk менжинск менжинськ luxemburg люксембург куйбишев khalturin халтурин postyshev постишев kosior косиор косіор
    chubar чубар пионер піонер пятилетк п'ятирічк интернационал інтернаціонал ustinov устинов""".split()
RED_TOKENS = sorted(set(t.replace("_", " ") for t in RED_TOKENS if t not in ("иленин",)))

# ---------------------------------------------------------------- 5. waves
# settlement names of the form "settlement of state farm No. 4": a Soviet placeholder, not a communist name to be undone
FARM_TOKENS = "sovkhoz kolkhoz совхоз колхоз колгосп радгосп отделения переселенческий участок".split()
# words of a qualifier: a name that only gains or loses these is the same name, extended or trimmed
QUAL_WORDS = set("""sur sous en les lès lez le la de du des d aux au à a l y i dei del della di am an im in bei ob unter ober nieder
    nad pod u na nei upon on by near dolny gorny wielki maly nowy stary new old upper lower east west north south great little
    bad saint sainte st ste mont""".split())
JOIN_WORDS = {"et", "and", "und", "og", "och", "y", "e", "i"}
CRIMEA = (32.4, 36.65, 44.3, 46.0)      # counted with Ukraine (Natural Earth draws it with Russia)
FR_REVOLUTION = [(1790, 1799, "communist", "French Revolution"), (1800, 1815, "reversal", "after the French Revolution")]
USSR = "RU UA BY MD EE LV LT GE AM AZ KZ UZ TM KG TJ".split()
COMMUNIST = {c: (1917, 1991) for c in USSR}
COMMUNIST.update({c: (1945, 1989) for c in "PL CZ SK HU RO BG AL".split()})
COMMUNIST.update({c: (1945, 1991) for c in "RS HR SI BA ME MK XK".split()})
COMMUNIST.update({"MN": (1924, 1990), "CN": (1949, 2026), "VN": (1945, 2026), "KP": (1945, 2026), "LA": (1975, 2026),
                  "KH": (1975, 1989), "CU": (1959, 2026), "DE_EAST": (1945, 1990)})
for c in ("EE", "LV", "LT"):
    COMMUNIST[c] = (1940, 1991)
for c in ("MD",):
    COMMUNIST[c] = (1940, 1991)
# the rule "renamed under communist rule" (no communist word in the name) stops a year or two before the end, because the
# renamings of 1990 and 1991 were national rather than communist
COMMUNIST_RULE = {c: (a, min(b, 1989 if c in USSR else 1988)) if b < 2000 else (a, b) for c, (a, b) in COMMUNIST.items()}
for c in ("CN", "VN", "KP", "LA", "CU"):
    COMMUNIST_RULE[c] = (COMMUNIST[c][0], 1980)

INDEPENDENCE = {  # year of independence of former colonies (or end of colonial rule)
    "DZ": 1962, "AO": 1975, "BJ": 1960, "BW": 1966, "BF": 1960, "BI": 1962, "CM": 1960, "CV": 1975, "CF": 1960, "TD": 1960,
    "KM": 1975, "CD": 1960, "CG": 1960, "CI": 1960, "DJ": 1977, "GQ": 1968, "ER": 1993, "SZ": 1968, "GA": 1960, "GM": 1965,
    "GH": 1957, "GN": 1958, "GW": 1974, "KE": 1963, "LS": 1966, "LY": 1951, "MG": 1960, "MW": 1964, "ML": 1960, "MR": 1960,
    "MU": 1968, "MA": 1956, "MZ": 1975, "NA": 1990, "NE": 1960, "NG": 1960, "RW": 1962, "ST": 1975, "SN": 1960, "SC": 1976,
    "SL": 1961, "SO": 1960, "SS": 2011, "SD": 1956, "TZ": 1961, "TG": 1960, "TN": 1956, "UG": 1962, "ZM": 1964, "ZW": 1980,
    "IN": 1947, "PK": 1947, "BD": 1947, "LK": 1948, "MM": 1948, "MY": 1957, "SG": 1965, "ID": 1945, "PH": 1946, "VN": 1954,
    "LA": 1953, "KH": 1953, "KR": 1945, "KP": 1945, "TW": 1945, "CY": 1960, "IL": 1948, "JO": 1946, "LB": 1943, "SY": 1946,
    "IQ": 1932, "KW": 1961, "AE": 1971, "QA": 1971, "BH": 1971, "YE": 1967, "BN": 1984, "TL": 2002, "PG": 1975, "FJ": 1970,
    "VU": 1980, "WS": 1962, "SB": 1978, "KI": 1979, "TV": 1978, "NR": 1968, "JM": 1962, "TT": 1962, "BB": 1966, "BS": 1973,
    "GY": 1966, "SR": 1975, "BZ": 1981,
}
DECOL_WINDOW = (-3, 25)            # years before and after independence

WAR = [  # (country, first year, last year, (lon0, lon1, lat0, lat1) or None)
    ("PL", 1918, 1922, None), ("PL", 1945, 1950, None),
    ("CZ", 1945, 1950, None),
    ("RU", 1945, 1950, (19.5, 23.0, 54.2, 55.4)),        # Kaliningrad
    ("RU", 1940, 1950, (27.5, 33.0, 60.0, 62.5)),        # the Karelian Isthmus and north of Lake Ladoga
    ("RU", 1945, 1950, (141.0, 157.0, 45.5, 54.5)),      # southern Sakhalin and the Kurils
    ("LT", 1945, 1950, (20.9, 21.8, 55.2, 56.1)),        # Klaipeda
    ("IT", 1918, 1945, (10.3, 14.5, 45.5, 47.1)),        # South Tyrol, Trentino and the north east
    ("FR", 1918, 1920, (5.8, 8.3, 47.4, 49.6)), ("FR", 1940, 1946, (5.8, 8.3, 47.4, 49.6)),   # Alsace and Moselle
    ("SI", 1945, 1950, None), ("HR", 1945, 1950, (13.4, 15.0, 44.7, 45.6)),                  # Istria
    ("RO", 1918, 1925, None), ("DK", 1920, 1921, (8.5, 10.0, 54.8, 55.6)),                   # North Schleswig
]

MERGER = {  # (first year, last year) of large municipal merger programmes
    "JP": [(1888, 1890), (1953, 1961), (1999, 2010)],
    "FR": [(1971, 1977), (2015, 2026)],
    "BE": [(1976, 1977)], "DK": [(1970, 1970), (2007, 2007)], "SE": [(1952, 1952), (1971, 1974)],
    "DE": [(1968, 1978)], "NL": [(1980, 2026)], "CA": [(2000, 2003)], "GR": [(1997, 1999), (2010, 2011)],
}
MERGER_ADMIN = {"UA": [(2015, 2020)], "RU": [(2004, 2006)], "GE": [(2006, 2006)]}

NATION = {  # nation-building and language policy: (first year, last year)
    "IE": (1916, 2026), "IN": (1947, 2026), "PK": (1947, 2026), "BD": (1947, 2026), "LK": (1948, 2026), "MM": (1948, 2026),
    "TR": (1923, 2026), "GR": (1913, 2026), "IL": (1948, 2026), "ZA": (1994, 2026), "FI": (1917, 2026), "NO": (1905, 2026),
    "CZ": (1918, 1939), "SK": (1918, 1939), "EE": (1918, 2026), "LV": (1918, 2026), "LT": (1918, 2026), "IS": (1918, 2026),
    "ES_REG": (1975, 2026),
}
for c in USSR:
    NATION.setdefault(c, (1991, 2026))
for c in "PL CZ SK HU RO BG AL RS HR SI BA ME MK XK MN".split():
    NATION.setdefault(c + "_POST", (1989, 2026))

# Ukraine's decommunisation laws (2015): the renamings of settlements in 2015 to 2017 were made under them, whatever the
# old name (Petrovsky, Artem, Komintern, Kolarov, Panfilov...), so every Ukrainian renaming in these years is counted here
UA_DECOM = (2015, 2017)
# regions of present-day former Soviet states that came under Soviet (communist) rule later than the rest; before that year
# their renamings were made by Poland, Czechoslovakia, Hungary, Romania, Finland, Germany or Japan, not under communist rule.
# (country, Natural Earth admin-1 names or a box (lon0, lon1, lat0, lat1), first year of Soviet rule)
SOVIET_FROM = [
    ("UA", ["L'viv", "Ivano-Frankivs'k", "Ternopil'", "Volyn", "Rivne"], 1939),   # Polish 1919 to 1939
    ("UA", ["Chernivtsi"], 1940),                                                    # Romanian 1918 to 1940
    ("UA", ["Transcarpathia"], 1945),                                                # Czechoslovak, then Hungarian
    ("UA", (28.2, 30.2, 45.2, 46.65), 1940),                                         # southern Bessarabia (Budjak)
    ("BY", ["Brest", "Grodno"], 1939),                                               # Polish 1921 to 1939
    ("RU", (19.5, 23.0, 54.2, 55.4), 1945),                                          # Kaliningrad (East Prussia)
    ("RU", (27.5, 33.0, 60.0, 62.5), 1940),                                          # Karelian Isthmus and Ladoga Karelia (Finnish)
    ("RU", (141.0, 157.0, 45.5, 54.5), 1945),                                        # southern Sakhalin and the Kurils (Japanese)
]

WAVES = ["colonial", "communist", "reversal", "war", "nation", "merger", "other"]
WAVE_NAME = {"qualifier": "Qualifier added or dropped", "colonial": "Decolonisation", "communist": "Revolution and communism", "reversal": "Undoing revolutionary and communist names",
             "war": "War and new borders", "nation": "Nation-building and language policy",
             "merger": "Mergers and administrative reform", "other": "Other renamings",
             "spelling": "Spelling and transliteration", "status": "Change of status, same name"}
WAVE_COL = {"colonial": "#B8862B", "communist": "#A3261B", "reversal": "#E07A3C", "war": "#5B4A8B", "nation": "#2F6E5A",
            "merger": "#8A8274", "other": "#3D6E9E", "spelling": "#C9BFA6", "status": "#C9BFA6", "qualifier": "#C9BFA6"}
