try:
    from pydantic import BaseModel, Field
    from enum import Enum

    print("Import successful")

    class DeviceType(str, Enum):
        ANDROID = "android"

    class TestModel(BaseModel):
        device_type: DeviceType = Field(..., description="Device category")

    print("Class definition successful")
    
    m = TestModel(device_type=DeviceType.ANDROID)
    print(m)

except Exception as e:
    import traceback
    traceback.print_exc()
