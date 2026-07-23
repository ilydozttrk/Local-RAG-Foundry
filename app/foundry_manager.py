from foundry_local_sdk import Configuration, FoundryLocalManager


APP_NAME = "local_rag_foundry"

_manager: FoundryLocalManager | None = None


def get_foundry_manager() -> FoundryLocalManager:
    """Initialize and return the shared Foundry Local manager."""

    global _manager

    if _manager is None:
        config = Configuration(app_name=APP_NAME)
        FoundryLocalManager.initialize(config)
        _manager = FoundryLocalManager.instance

    return _manager