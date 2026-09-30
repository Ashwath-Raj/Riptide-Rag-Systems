class RiptideError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class SecurityGateUnavailable(RiptideError):
    def __init__(self, message: str = "security_gate_unavailable") -> None:
        super().__init__("security_gate_unavailable", message)


class PrivacyGateUnavailable(RiptideError):
    def __init__(self, message: str = "privacy_gate_unavailable") -> None:
        super().__init__("privacy_gate_unavailable", message)


class RetrievalUnavailable(RiptideError):
    def __init__(self, message: str = "retrieval_unavailable") -> None:
        super().__init__("retrieval_unavailable", message)


class GenerationUnavailable(RiptideError):
    def __init__(self, message: str = "generation_unavailable") -> None:
        super().__init__("generation_unavailable", message)


class TranscriptionUnavailable(RiptideError):
    def __init__(self, message: str = "transcription_unavailable") -> None:
        super().__init__("transcription_unavailable", message)


class DatasetIncomplete(RiptideError):
    def __init__(self, message: str = "dataset_incomplete") -> None:
        super().__init__("dataset_incomplete", message)
