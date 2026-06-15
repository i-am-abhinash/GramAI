from backend.services.sync_service import GovernmentSchemeSyncService

if __name__ == '__main__':
    svc = GovernmentSchemeSyncService()
    svc.run_sync()
    print("Sync triggered successfully.")
