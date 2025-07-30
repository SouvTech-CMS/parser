from configs import settings

CREDENTIALS_ARG = dict(
    refresh_token=settings.SP_API_REFRESH_TOKEN,
    credentials=dict(
    lwa_app_id=settings.LWA_APP_ID,
    lwa_client_secret=settings.LWA_CLIENT_SECRET
    )
)
