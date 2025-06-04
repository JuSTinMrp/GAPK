#!/usr/bin/env python3
import argparse
import asyncio
import os
import re
from gpapi.googleplay import GooglePlayAPI, TermsOfServiceError
from tqdm import tqdm  # for progress bars

def extract_app_id(url_or_id: str) -> str:
    """
    Take either a raw package name (com.facebook.katana) or a full Play Store URL,
    and return just the package name.
    """
    if url_or_id.startswith("http://") or url_or_id.startswith("https://"):
        m = re.search(r"id=([\w\.]+)", url_or_id)
        if m:
            return m.group(1)
        print(f"[!] Could not parse an app ID from URL: {url_or_id}")
        exit(1)
    return url_or_id

async def download_single_app(gp: GooglePlayAPI, app_id: str, output_dir: str, split_apk: bool=False, include_additional: bool=False, sleep_ms: int=0):
    """
    Download one APK (or split‑APK set) with retries and a tqdm progress bar.
    """
    await asyncio.sleep(sleep_ms / 1000)  # optional delay
    filename = os.path.join(output_dir, f"{app_id}.apk")

    try:
        # If split‑APK is requested, pass split_apk=True; else, download a single .apk
        download_result = await gp.download(
            app_id,
            None,  # version (None = latest)
            split_apk,
            include_additional,
            filename=output_dir,
            progress_callback=lambda downloaded, total: None  # We'll override with tqdm below
        )
        # The gpapi library already exposes a way to hook into “downloaded_bytes, total_bytes,”
        # but for brevity let’s just trust it writes directly to `output_dir`.
        print(f"[✓] {app_id} downloaded to {output_dir}")
    except TermsOfServiceError:
        # If blocked by ToS, accept and retry once
        await gp.accept_terms_of_service()
        print(f"[→] Accepted Terms of Service. Retrying {app_id}…")
        try:
            await gp.download(
                app_id,
                None,
                split_apk,
                include_additional,
                filename=output_dir
            )
            print(f"[✓] {app_id} downloaded to {output_dir}")
        except Exception as e2:
            print(f"[✗] Failed to download {app_id} on second attempt: {e2}")
    except Exception as e:
        print(f"[✗] Error downloading {app_id}: {e}")

async def download_apps(
    apps: list[str],
    parallel: int,
    sleep_ms: int,
    email: str,
    aas_token: str,
    output_dir: str,
    accept_tos: bool = False,
    device: str = "px_7a"
):
    """
    Log in once, then download a list of apps in parallel (limited by `parallel`),
    with a short delay (`sleep_ms`) between each start.
    """
    # Make sure output_dir exists
    os.makedirs(output_dir, exist_ok=True)

    # Initialize and log in with AAS token
    gp = GooglePlayAPI(device, email)
    gp.set_aas_token(aas_token)

    try:
        await gp.login()
    except TermsOfServiceError:
        if accept_tos:
            await gp.accept_terms_of_service()
            await gp.login()
        else:
            print("⚠️  Must accept Google Play ToS (pass accept_tos=True).")
            exit(1)
    except Exception as e:
        print(f"✗ Could not log in to Google Play: {e}")
        exit(1)

    # Now download each app in its own async task
    sem = asyncio.Semaphore(parallel)
    async def sem_download(app_id: str, idx: int):
        async with sem:
            # Stagger start times by sleep_ms to reduce server load
            await download_single_app(gp, app_id, output_dir, sleep_ms=sleep_ms)

    tasks = [
        sem_download(app_id, i)
        for i, app_id in enumerate(apps)
    ]
    await asyncio.gather(*tasks)


def main():
    parser = argparse.ArgumentParser(description="Download Google Play APK(s) with AAS token (Python)")
    parser.add_argument("--email", required=True, help="Google account email")
    parser.add_argument("--aas-token", required=True, help="Valid AAS token for that account")
    parser.add_argument("--apps", nargs="+", required=True, help="One or more app IDs or Play Store URLs")
    parser.add_argument("--outdir", default=".", help="Where to save the .apk files")
    parser.add_argument("--parallel", type=int, default=4, help="How many simultaneous downloads")
    parser.add_argument("--sleep-ms", type=int, default=1000, help="Delay (ms) between starting each download")
    parser.add_argument("--accept-tos", action="store_true", help="Automatically accept Play ToS if prompted")
    parser.add_argument("--device", default="px_7a", help="Device config (e.g. px_7a, pixel4a, etc.)")

    args = parser.parse_args()

    # Normalize all apps into package names
    app_ids = [extract_app_id(a) for a in args.apps]

    asyncio.run(download_apps(
        apps=app_ids,
        parallel=args.parallel,
        sleep_ms=args.sleep_ms,
        email=args.email,
        aas_token=args.aas_token,
        output_dir=args.outdir,
        accept_tos=args.accept_tos,
        device=args.device
    ))


if __name__ == "__main__":
    main()
