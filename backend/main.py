import os

import uvicorn

from app.logging_config import setup_logging


if __name__ == "__main__":
    setup_logging()
    uvicorn.run(
        "app.api.server:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=False,
    )
