try:
    from fastapi import FastAPI
    app = FastAPI()
    print("FastAPI init successful")
except Exception as e:
    import traceback
    traceback.print_exc()
