import asyncio
import os
import sys
import re

# Ensure proper encoding
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["MONGO_URI"] = "mongodb+srv://rti_admin:ZqWmmEI9MhpEYIGB@cluster0.2vomo9m.mongodb.net/?appName=Cluster0"
os.environ["MONGO_DB_NAME"] = "rti_db"

from tools.department_lookup import get_canonical_departments_for_registration
from mcp_clients.mongo_client import get_mongo_client

def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='replace').decode('ascii'))

async def verify():
    safe_print("=== Verification Start ===")
    
    # 1. Verify mapping function
    safe_print("[Test 1] Verifying department mapping for 'health'...")
    canon_depts = get_canonical_departments_for_registration("health")
    safe_print(f"Mapped canonical departments: {canon_depts}")
    assert "Ministry of Health and Family Welfare" in canon_depts, "Error: Ministry of Health and Family Welfare should be mapped!"
    assert "State Health Department" in canon_depts, "Error: State Health Department should be mapped!"
    safe_print("✅ Department mapping verification passed!")

    # 2. Connect to MongoDB
    safe_print("\n[Test 2] Connecting to MongoDB and validating query resolution...")
    mongo = await get_mongo_client()
    
    # Check if officer exists
    officer_email = "acash.brands746@gmail.com"
    officer = await mongo.db["users"].find_one({"email": officer_email})
    assert officer is not None, f"Error: Officer account {officer_email} not found in DB!"
    safe_print(f"Found Officer: {officer['name']} | Registered Department: {officer['department']}")
    
    # Map their department and build query regex pattern
    dept = officer['department']
    canon_depts = get_canonical_departments_for_registration(dept)
    regex_pattern = "^(" + "|".join([re.escape(d) for d in canon_depts]) + ")$"
    
    # Query matching RTI requests
    query = {"department": {"$regex": regex_pattern, "$options": "i"}}
    matched_rtis = await mongo.db["rti_requests"].find(query).to_list(length=100)
    
    safe_print(f"Found {len(matched_rtis)} matching RTIs for mapping regex: {regex_pattern}")
    for r in matched_rtis:
        safe_print(f"  - ID: {r['request_id']} | Tracking ID: {r.get('tracking_id')} | Classified Dept: {r['department']} | Status: {r['status']}")
        
    target_request_id = "a0d642a4-ab4b-4708-b1c9-620d7c9dc6a4"
    found_target = any(r['request_id'] == target_request_id for r in matched_rtis)
    assert found_target, f"Error: Target request ID {target_request_id} was not matched by query!"
    safe_print("✅ MongoDB regex mapping query resolution passed! The officer can now see this request!")

    # 3. Simulate responding to the RTI
    safe_print("\n[Test 3] Simulating response submission for target RTI...")
    test_response = "This is a verification official response provided by the Health Department officer under testing."
    
    # Read the original record to preserve it for cleanup
    original_doc = await mongo.db["rti_requests"].find_one({"request_id": target_request_id})
    assert original_doc is not None, "Error: original target document not found!"
    
    # Perform update mock
    from datetime import datetime, timezone
    update_data = {
        "status": "completed",
        "final_response": test_response,
        "officer_response": test_response,
        "responded_by": officer_email,
        "responded_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc),
    }
    
    update_res = await mongo.db["rti_requests"].update_one(
        {"request_id": target_request_id},
        {"$set": update_data}
    )
    assert update_res.modified_count > 0 or update_res.matched_count > 0, "Error: Update failed!"
    
    # Verify update in DB
    updated_doc = await mongo.db["rti_requests"].find_one({"request_id": target_request_id})
    safe_print(f"Updated document status: {updated_doc['status']}")
    safe_print(f"Updated document officer_response: {updated_doc.get('officer_response')}")
    assert updated_doc['status'] == "completed", "Error: Status was not updated to completed!"
    assert updated_doc['officer_response'] == test_response, "Error: Officer response was not recorded correctly!"
    
    # Clean up and revert to original state
    safe_print("\n[Cleanup] Reverting target RTI to original state...")
    revert_data = {
        "status": original_doc.get("status"),
        "final_response": original_doc.get("final_response"),
        "officer_response": original_doc.get("officer_response"),
        "responded_by": original_doc.get("responded_by"),
        "responded_at": original_doc.get("responded_at"),
        "updated_at": original_doc.get("updated_at"),
    }
    # Using raw Mongo to avoid custom validation triggers
    await mongo.db["rti_requests"].update_one(
        {"request_id": target_request_id},
        {"$set": revert_data}
    )
    safe_print("✅ Verification clean up completed successfully!")
    safe_print("\n=== Verification End: ALL TESTS PASSED! ===")

if __name__ == "__main__":
    asyncio.run(verify())
