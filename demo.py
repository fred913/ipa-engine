import logging

from ipa_engine import IPAEngine

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create an instance of IPASession
# ipa_session = IPASession(languages=["zh_hans"])
logger.debug("Initializing IPA session...")
ipa_session = IPAEngine(languages=["fr_FR"])
logger.debug("IPA session initialized.")

# Translate a sentence
sentence = "Ça va bien?"
ipa_result = ipa_session.translate_ipa(sentence)
logger.debug(
    "IPA translation: %s",
    "".join(ipa_result))  # Output will be a list of IPA transcriptions
