class AIService:
    def __init__(
        self,
        extract_chain,
        classifier_chain,
        conversation_chain,
    ):
        self.extract_chain = extract_chain
        self.classifier_chain = classifier_chain
        self.conversation_chain = conversation_chain
