class GovernmentSchemeSyncService:
    """Mock synchronization is retired. No sample data may be written."""

    def run_sync(self):
        return {
            "success": False,
            "error": "Automatic sync is paused until official-source adapters are verified. No records were changed.",
            "imported": 0,
            "updated": 0,
        }
