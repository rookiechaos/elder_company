"""
Disclaimer texts for compliance (non-medical product).
Used by emergency guidance and RAG knowledge answers. Supports zh, ja, en.
"""

# Emergency guidance disclaimer: not diagnosis; call emergency when needed.
DISCLAIMER_EMERGENCY = {
    "zh": "本产品为照护陪伴与记录工具，非医疗设备。以上内容仅供参考与情境缓解，不构成诊断或治疗。紧急情况请立即拨打急救电话或联系医疗机构。",
    "ja": "本製品は介護・記録のためのツールであり、医療機器ではありません。上記は参考・状況緩和用であり、診断や治療を意図していません。緊急の場合は119番または医療機関に連絡してください。",
    "en": "This product is a care companion and recording tool, not a medical device. The above is for reference and situation support only, not diagnosis or treatment. In an emergency, call emergency services or contact a healthcare provider.",
}

# Knowledge base / RAG answer disclaimer: reference only, not medical advice; consult when urgent.
DISCLAIMER_KNOWLEDGE = {
    "zh": "以上信息仅供参考，不构成医疗诊断或建议。健康与医疗决策请咨询专业医护人员。紧急情况请联系医疗机构。",
    "ja": "この情報は参考用です。医療診断ではありません。健康・医療に関する判断は専門の医療従事者にご相談ください。緊急の場合は医療機関に連絡してください。",
    "en": "This information is for reference only and does not constitute medical diagnosis or advice. Please consult a healthcare professional for health and medical decisions. In an emergency, contact a healthcare provider.",
}

# Knowledge base empty result (no documents found).
DISCLAIMER_KNOWLEDGE_EMPTY = {
    "zh": "以上信息仅供参考，不构成医疗诊断或建议。",
    "ja": "この情報は参考用です。医療診断ではありません。",
    "en": "This information is for reference only and does not constitute medical diagnosis or advice.",
}

SUPPORTED_LANGUAGES = ("zh", "ja", "en")
DEFAULT_LANGUAGE = "ja"


def _normalize_language(lang: str) -> str:
    if not lang or not isinstance(lang, str):
        return DEFAULT_LANGUAGE
    lang = lang.strip().lower()[:2]
    return lang if lang in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE


def get_disclaimer_emergency(language: str) -> str:
    """Return emergency guidance disclaimer for the given language."""
    return DISCLAIMER_EMERGENCY.get(_normalize_language(language), DISCLAIMER_EMERGENCY[DEFAULT_LANGUAGE])


def get_disclaimer_knowledge(language: str) -> str:
    """Return knowledge/RAG answer disclaimer for the given language."""
    return DISCLAIMER_KNOWLEDGE.get(_normalize_language(language), DISCLAIMER_KNOWLEDGE[DEFAULT_LANGUAGE])


def get_disclaimer_knowledge_empty(language: str) -> str:
    """Return knowledge empty-result disclaimer for the given language."""
    return DISCLAIMER_KNOWLEDGE_EMPTY.get(_normalize_language(language), DISCLAIMER_KNOWLEDGE_EMPTY[DEFAULT_LANGUAGE])
