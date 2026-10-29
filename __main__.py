import logging
import os

from web import WebManager

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    host = os.environ.get("HOST", "::")
    port = int(os.environ.get("PORT", "443"))
    web = WebManager()
    web.serve(host, port)
