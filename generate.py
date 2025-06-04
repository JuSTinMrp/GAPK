#!/usr/bin/env python3
import os
import argparse
import asyncio

# If your protobuf package is too new, force the pure-Python implementation
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

from gpapi.googleplay import GooglePlayAPI
import gpapi

async def request_aas_token(email: str, oauth_token: str, android_id: str = "px_7a"):
    """
    Log in to Google Play with an OAuth2 token and print a fresh AAS token.
    """

    # 1) Instantiate with exactly one positional argument: the Android device codename.
    gp = GooglePlayAPI(android_id)

    # 2) Explicitly set a locale and timezone (both are optional, but some accounts fail without them).
    try:
        gp.setLocale("en_US")
    except Exception:
        # If your gpapi version does not have setLocale or if "en_US" is invalid,
        # you can safely ignore this (though some accounts require a valid locale).
        pass

    try:
        gp.setTimezone("UTC")
    except Exception:
        # Same as above: if your gpapi does not support .setTimezone( ), ignore.
        pass

    # 3) We already have an OAuth2–based AAS token (passed in as `oauth_token`).
    #    Tell gpapi to reuse it:
    gp.set_aas_token(oauth_token)

    # 4) Attempt to log in using that AAS token
    try:
        await gp.login(oauth2_access_token=oauth_token)
    except Exception as err:
        # gpapi may raise a generic exception whose text contains "terms_of_service_required".
        if "terms_of_service_required" in str(err).lower():
            print("[→] Google Play Terms-of-Service not yet accepted. Accepting now…")
            await gp.accept_terms_of_service()
            await gp.login(oauth2_access_token=oauth_token)
        else:
            # Any other login error we re-raise so you can see it.
            raise

    # 5) If login succeeded, get the fresh AAS token and print it.
    fresh_aas = gp.get_aas_token()
    if fresh_aas:
        print("AAS Token:", fresh_aas)
    else:
        print("❌ Failed to retrieve AAS token from Google Play.")

def main():
    parser = argparse.ArgumentParser(
        description="Generate AAS token from OAuth2 token using pure-Python gpapi"
    )
    parser.add_argument(
        "--email", "-e", required=True, help="Google account email"
    )
    parser.add_argument(
        "--oauth-token", "-o", required=True,
        help="OAuth2 access token (e.g. from gplay login)"
    )
    parser.add_argument(
        "--device", "-d", default="px_7a",
        help="Android device codename (px_7a, hammerhead, bullhead, etc.)"
    )
    args = parser.parse_args()

    asyncio.run(request_aas_token(
        email=args.email,
        oauth_token=args.oauth_token,
        android_id=args.device
    ))

if __name__ == "__main__":
    main()
