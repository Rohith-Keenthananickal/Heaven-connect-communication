try:
    import pydantic
    print(f"Pydantic version: {pydantic.VERSION}")
    
    from app.models.player import PlayerBase, PlayerResponse, DeviceType, DeviceStatus
    from datetime import datetime

    print("Import successful")
    
    print("Testing PlayerBase...")
    base_data = {
        "user_id": "u1",
        "device_type": DeviceType.ANDROID,
        "push_token": "t1"
    }
    base = PlayerBase(**base_data)
    print("PlayerBase instantiation successful")

    print("Testing PlayerResponse...")
    data = {
        "user_id": "u1",
        "device_type": DeviceType.ANDROID,
        "push_token": "t1",
        "device_id": "d1",
        "last_login_at": datetime.now(),
        "status": DeviceStatus.ACTIVE,
        "updated_at": datetime.now()
    }

    model = PlayerResponse(**data)
    print("Model instantiation successful")
    print(model.model_dump())

except Exception as e:
    import traceback
    traceback.print_exc()
