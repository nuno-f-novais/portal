import os

class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"

    # Local registration toggle
    ALLOW_SELF_REGISTER = os.getenv("ALLOW_SELF_REGISTER", "true").lower() == "true"

    # OIDC
    OIDC_ENABLED = os.getenv("OIDC_ENABLED", "false").lower() == "true"
    OIDC_CLIENT_ID = os.getenv("OIDC_CLIENT_ID")
    OIDC_CLIENT_SECRET = os.getenv("OIDC_CLIENT_SECRET")
    OIDC_AUTHORITY = os.getenv("OIDC_AUTHORITY")
    OIDC_AUTHORIZATION_ENDPOINT = os.getenv("OIDC_AUTHORIZATION_ENDPOINT")
    OIDC_TOKEN_ENDPOINT = os.getenv("OIDC_TOKEN_ENDPOINT")
    OIDC_USERINFO_ENDPOINT = os.getenv("OIDC_USERINFO_ENDPOINT")
    OIDC_REDIRECT_URI = os.getenv("OIDC_REDIRECT_URI")
    OIDC_SCOPES = os.getenv("OIDC_SCOPES", "openid profile email").split()

    # SAML
    SAML_ENABLED = os.getenv("SAML_ENABLED", "false").lower() == "true"
    SAML_SP_ENTITY_ID = os.getenv("SAML_SP_ENTITY_ID")
    SAML_ASSERTION_CONSUMER_SERVICE_URL = os.getenv("SAML_ASSERTION_CONSUMER_SERVICE_URL")
    SAML_SINGLE_LOGOUT_SERVICE_URL = os.getenv("SAML_SINGLE_LOGOUT_SERVICE_URL")
    SAML_IDP_ENTITY_ID = os.getenv("SAML_IDP_ENTITY_ID")
    SAML_IDP_SSO_URL = os.getenv("SAML_IDP_SSO_URL")
    SAML_IDP_SLO_URL = os.getenv("SAML_IDP_SLO_URL")
    SAML_IDP_X509_CERT = os.getenv("SAML_IDP_X509_CERT")
