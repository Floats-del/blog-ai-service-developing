import logging
from pathlib import Path

def setup_logging():

    # create logs folder automatically
    Path("logs").mkdir(exist_ok=True)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(event)s | %(function)s | %(request_id)s | %(exception_type)s | %(exception)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # -------- Terminal --------
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # -------- File --------
    file_handler = logging.FileHandler(
        "logs/app.log",
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    logger = logging.getLogger("ai_saas")
    logger.setLevel(logging.INFO)

    logger.handlers.clear()      # avoid duplicate handlers

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.propagate = False


#so far our logs are like:
#1) routes: 2026-07-31 11:09:26 | INFO | AI_RESERVATION_CREATED | consume_ai_quota | 8fc44530-390e-4d3c-8b7f-7bddf8803f48 | None | None
#2) service: 2026-07-31 11:09:27 | INFO | AI_PROVIDER_IN_PROCESSING | generate_titles | None | None | None 
#see the service dont track the request_id in future change that!