import os

JWT_SECRET = os.getenv("JWT_SECRET", "CHANGE_ME")  # set in env in real usage
JWT_ALG = os.getenv("JWT_ALG", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
