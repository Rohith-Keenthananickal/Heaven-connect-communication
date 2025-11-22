import sys
import os

# Add the project root to the python path
sys.path.append(os.getcwd())

from fastapi.testclient import TestClient
from app.main import app
from app.models.player import DeviceType

client = TestClient(app)

def test_register_player():
    print("Testing Player Registration...")
    response = client.post(
        "/players/register",
        json={
            "user_id": "user-123",
            "device_type": "android",
            "push_token": "token-123",
            "device_model": "Samsung S21",
            "os_version": "12.0",
            "app_version": "1.0.0"
        }
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 201:
        print("✅ Registration Successful")
        return response.json()["player_id"]
    else:
        print("❌ Registration Failed")
        return None

def test_get_player(player_id):
    print(f"\nTesting Get Player {player_id}...")
    response = client.get(f"/players/{player_id}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("✅ Get Player Successful")
    else:
        print("❌ Get Player Failed")

def test_update_player(player_id):
    print(f"\nTesting Update Player {player_id}...")
    response = client.put(
        f"/players/{player_id}",
        json={
            "device_model": "Samsung S22",
            "app_version": "1.0.1"
        }
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200 and response.json()["device_model"] == "Samsung S22":
        print("✅ Update Player Successful")
    else:
        print("❌ Update Player Failed")

if __name__ == "__main__":
    try:
        player_id = test_register_player()
        if player_id:
            test_get_player(player_id)
            test_update_player(player_id)
    except Exception as e:
        print(f"An error occurred: {e}")
