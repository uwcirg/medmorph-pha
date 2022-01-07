"""Default configuration

Use env var to override
"""
import os

SERVER_NAME = os.getenv("SERVER_NAME")
SECRET_KEY = os.getenv("SECRET_KEY")
# URL scheme to use outside of request context
PREFERRED_URL_SCHEME = os.getenv("PREFERRED_URL_SCHEME", "http")
DEBUG_DUMP_HEADERS = os.getenv("DEBUG_DUMP_HEADERS", "false").lower() == "true"
DEBUG_DUMP_REQUEST = os.getenv("DEBUG_DUMP_REQUEST", "false").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

BACKING_FHIR_URL = os.getenv("BACKING_FHIR_URL ", "http://fhir:8080/fhir")
