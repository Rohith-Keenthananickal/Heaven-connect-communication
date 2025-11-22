try:
    from app.config import settings
    print("Config import successful")
    print(settings.APP_NAME)
except Exception as e:
    import traceback
    traceback.print_exc()
