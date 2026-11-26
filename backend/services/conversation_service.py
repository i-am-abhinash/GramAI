"""In-memory citizen session; never treat a partial eligibility check as approval."""
import json
import re
from pathlib import Path
from backend.services.retrieval_service import normalized

_BUNDLE = Path(__file__).resolve().parents[1] / "knowledge" / "official_drafts.json"
_STOP = {"stop", "end conversation", "cancel", "thank you", "thanks", "ఆపు", "చాలు", "వద్దు", "ధన్యవాదాలు", "aapu", "chalu", "vaddu"}
_YES = {"yes", "yes i do", "yes i have", "i agree", "అవును", "ఉంది", "ఉన్నాయి", "ఉన్నది", "అంగీకరిస్తాను", "avunu", "undi", "unnayi"}
_NO = {"no", "no i do not", "no i don t", "i don t have", "లేదు", "లేవు", "కాదు", "ledu", "levu", "kaadu"}
_FOLLOWUPS = {
    "eligibility": ("eligibility", "who can apply", "am i eligible", "age limit", "అర్హతలు", "అర్హతలు ఏమిటి", "ఎవరికి వస్తుంది", "నేను అర్హుడినా", "arhatalu", "arhatha"),
    "required_documents": ("documents", "what documents", "what documents are required", "required documents", "పత్రాలు", "ఏం కావాలి", "ఏమేమి కావాలి", "ఏ పత్రాలు కావాలి", "డాక్యుమెంట్స్", "em em kavali", "em kavali"),
    "benefits": ("benefits", "how much", "how much money", "amount", "ఎంత", "ఎంత వస్తుంది", "ఎంత డబ్బు వస్తుంది", "డబ్బులు ఎంత", "entha", "entha vastundi"),
    "application_process": ("apply", "how to apply", "where to apply", "where", "ఎలా అప్లై చేయాలి", "ఎక్కడ అప్లై చేయాలి", "ఎక్కడ", "అప్లై చేయాలి", "ela apply cheyyali", "ekkada apply cheyyali"),
    "scheme_information": ("tell me more", "more details", "ఇంకా చెప్పు", "వివరాలు", "inka cheppu"),
}

def parse_age(text):
    q = normalized(text)
    m = re.fullmatch(r"(?:i am |my age is |నా వయసు )?(\d{1,3})(?: years old| years| year| ఏళ్లు| సంవత్సరాలు| years age)?", q)
    if m:
        age = int(m.group(1))
        return age if 0 < age <= 120 else None
    units = dict(zip("one two three four five six seven eight nine".split(), range(1, 10)))
    tens = dict(zip("twenty thirty forty fifty sixty seventy eighty ninety".split(), range(20, 100, 10)))
    words = q.split()
    if len(words) == 1:
        return {"eighteen": 18, "nineteen": 19, **tens}.get(q)
    if len(words) == 2 and words[0] in tens and words[1] in units:
        return tens[words[0]] + units[words[1]]
    return None

def verified_pilot(scheme):
    """Enable the pilot only when both reviewed eligibility texts still match its rules."""
    try:
        item = next(x for x in json.loads(_BUNDLE.read_text(encoding="utf-8"))["schemes"] if x["key"] == "pmjjby")
        return (scheme.get("name") == item["en"]["name"] and scheme.get("source_url") == item["source_url"]
                and all(scheme.get(prefix + "eligibility") == item[lang]["eligibility"] + "\n" + item[lang]["exclusions"]
                        for prefix, lang in (("", "en"), ("te_", "te"))))
    except (OSError, ValueError, KeyError, StopIteration):
        return False

class ConversationSession:
    def __init__(self):
        self.scheme_id = None
        self.pending_intent = None
        self.options = {}
        self.options_display = []
        self.awaiting = None
        self.age = None

    def reset(self):
        self.__init__()

    def _message(self, en, te, language, source=None):
        return {"type": "ANSWER", "text": en if language == "en" else te, "source": source or {}}

    def _prompt(self, gov, scheme, language, en, te):
        return self._message(en, te, language, gov.answer_scheme("eligibility", scheme, language)["source"])

    def _guided(self, gov, scheme, q, language):
        if not verified_pilot(scheme):
            self.awaiting = None
            self.age = None
            return self._message("The reviewed eligibility rules have changed. Please ask about the scheme again.", "పథకం అర్హత నిబంధనలు మారాయి. దయచేసి మళ్లీ అడగండి.", language)
        if self.awaiting == "age":
            age = parse_age(q)
            if age is None:
                return self._prompt(gov, scheme, language, "Please tell me your age in years, for example 35.", "మీ వయసు ఎన్ని సంవత్సరాలో చెప్పండి. ఉదాహరణకు 35.")
            self.age = age
            if not 18 <= age <= 50:
                self.awaiting = None
                self.age = None
                return self._prompt(gov, scheme, language, "For new enrolment, the reviewed age range is 18 to 50. Existing members have separate renewal rules. Please check with your bank or post office.", "కొత్తగా చేరాలంటే వయసు 18 నుంచి 50 ఏళ్ల మధ్య ఉండాలి. ఇప్పటికే చేరిన వారికి రెన్యువల్ నిబంధనలు వేరు. బ్యాంకు లేదా పోస్టాఫీసులో అడగండి.")
            self.awaiting = "account"
            return self._prompt(gov, scheme, language, "Your age is within the new-enrolment range. Do you have an individual account at a participating bank or post office?", "వయసు పరంగా సరిపోతుంది. ఈ పథకంలో పాల్గొనే బ్యాంకు లేదా పోస్టాఫీసులో మీకు వ్యక్తిగత ఖాతా ఉందా?")
        if q not in _YES | _NO:
            return self._prompt(gov, scheme, language, "Please answer yes or no, or ask another named scheme.", "అవును లేదా లేదు అని చెప్పండి. లేదా వేరే పథకం పేరు చెప్పండి.")
        if q in _NO:
            self.awaiting = None
            self.age = None
            return self._prompt(gov, scheme, language, "That requirement is not met based on your answer. Ask a participating bank or post office about your options.", "మీరు చెప్పిన వివరాల ప్రకారం ఈ నిబంధన సరిపోవడం లేదు. బ్యాంకు లేదా పోస్టాఫీసులో అడగండి.")
        if self.awaiting == "account":
            self.awaiting = "consent"
            return self._prompt(gov, scheme, language, "Are you willing to have the insurance premium automatically deducted from your account?", "బీమా ప్రీమియం మీ ఖాతా నుంచి ఆటోమేటిక్‌గా కట్ కావడానికి అంగీకరిస్తారా?")
        self.awaiting = None
        self.age = None
        docs = gov.answer_scheme("required_documents", scheme, language)
        application = gov.answer_scheme("application_process", scheme, language)
        prefix = ("Your answers match these preliminary checks. This is not final approval. " if language == "en" else "మీరు చెప్పిన వివరాలు ఈ ప్రాథమిక నిబంధనలకు సరిపోతున్నాయి. ఇది తుది అర్హత నిర్ధారణ కాదు. ")
        return {"type": "ANSWER", "text": prefix + docs["text"] + " " + application["text"], "source": docs["source"]}

    def process(self, gov, text, language="te"):
        q = normalized(text)
        if q in _STOP:
            self.reset()
            return {"type": "END"}
        # Re-read the verified view on every turn, even for a one-word reply.
        rows = gov.retrieval.scheme_repo.get_all_schemes()
        current = next((s for s in rows if s["id"] == self.scheme_id), None)
        matches = [s for s in rows if any(normalized(a) and " " + normalized(a) + " " in " " + q + " "
                   for a in [s["name"], s.get("te_name", ""), *s.get("aliases", [])])]
        follow = next((intent for intent, phrases in _FOLLOWUPS.items() if q in phrases), None)
        if self.options and not matches and q not in self.options:
            return {"type": "CLARIFICATION", "options": list(self.options_display)}
        if self.options and q in self.options:
            selected = self.options[q]
            matches = [s for s in rows if s["id"] == selected]
            intent = self.pending_intent
            self.reset()
            if not matches:
                return self._message("That scheme is no longer verified.", "ఆ పథకం సమాచారం ఇప్పుడు నిర్ధారించబడలేదు.", language)
        else:
            intent = follow or gov.nlp.detect_intent(text)
        if len(matches) > 1:
            self.reset()
            self.pending_intent = intent
            names = [s.get("te_name", s["name"]) if language == "te" else s["name"] for s in matches[:3]]
            self.options = {normalized(name): s["id"] for name, s in zip(names, matches)}
            self.options.update({str(i): s["id"] for i, s in enumerate(matches[:3], 1)})
            self.options_display = names
            return {"type": "CLARIFICATION", "options": names}
        if matches:
            self.reset()
            scheme = matches[0]
            self.scheme_id = scheme["id"]
            if intent in ("application_process", "eligibility") and verified_pilot(scheme):
                self.awaiting = "age"
                return self._prompt(gov, scheme, language, "For new enrolment in PMJJBY, let me check a few requirements. How old are you?", "జీవన్ జ్యోతి బీమాలో కొత్తగా చేరడానికి కొన్ని అర్హతలు చూద్దాం. మీ వయసు ఎంత?")
            result = gov.answer_scheme(intent, scheme, language)
            gov.record_public_answer(intent, scheme, result)
            return result
        if current is not None and follow:
            self.awaiting = None
            self.age = None
            if follow in ("application_process", "eligibility") and verified_pilot(current):
                self.awaiting = "age"
                return self._prompt(gov, current, language, "How old are you?", "మీ వయసు ఎంత?")
            result = gov.answer_scheme(follow, current, language)
            gov.record_public_answer(follow, current, result)
            return result
        if current is not None and self.awaiting:
            if gov.nlp.detect_entity(text) == "welfare":
                return self._guided(gov, current, q, language)
            self.reset()
            return self._message("Please name the other scheme. I cannot verify eligibility without its current rules.", "వేరే పథకం పేరు చెప్పండి. నిర్ధారించిన నిబంధనలు లేకుండా అర్హత చెప్పలేను.", language)
        if self.scheme_id is not None and current is None and (follow or self.awaiting):
            self.reset()
            return self._message("This scheme is no longer available as verified information. Please check the official office.", "ఈ పథకం నిర్ధారించిన సమాచారం ఇప్పుడు అందుబాటులో లేదు. సంబంధిత కార్యాలయంలో అడగండి.", language)
        self.reset()
        # Preserve the existing unanswered queue for general questions only.
        # Guided replies and contextual answers above never enter query logs.
        return gov.process_query(text, language=language)
