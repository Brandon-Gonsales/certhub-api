import sys
import os

# Add the project root to the python path
sys.path.append(os.getcwd())

try:
    print("Importing schemas...")
    from app.schemas.campaign_schema import CampaignCreate, CampaignDisplay, CampaignUpdate
    print("Schemas imported successfully.")

    print("Importing service...")
    # We might not be able to import service if it depends on DB connection at module level, 
    # but let's try. It imports models which import Beanie.
    from app.services import campaign_service
    print("Service imported successfully.")
    
    print("Verification passed!")

except Exception as e:
    print(f"Verification failed: {e}")
    sys.exit(1)
