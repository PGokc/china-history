#!/usr/bin/env python3
"""Prepare and synthesize the Ming/Qing narration release.

The API key is read only from VOLCENGINE_TTS_API_KEY. Audio files are build
artifacts and stay outside the app bundle; the iOS client downloads them from
TOS and caches only what the reader plays.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "App/Resources/history.json"
MANIFEST = ROOT / "App/Resources/narration_manifest.json"
DEFAULT_OUTPUT = ROOT / "NarrationBuild/v1"
BASE_URL = "https://shiji-history-assets.tos-cn-shanghai.volces.com/narration/v1/"
SUBMIT_URL = "https://openspeech.bytedance.com/api/v3/tts/submit"
QUERY_URL = "https://openspeech.bytedance.com/api/v3/tts/query"
DEFAULT_VOICE = "zh_male_gaolengchenwen_uranus_bigtts"


def spoken_text(title: str, text: str) -> str:
    source = f"{title}。{text}".replace("—", "至")
    digits = str.maketrans("0123456789", "零一二三四五六七八九")
    return re.sub(r"(?<!\d)(\d{4})(?=年)", lambda m: m.group(1).translate(digits), source)


def load_sections() -> list[dict]:
    content = json.loads(HISTORY.read_text())
    dynasties = {person["id"]: person.get("dynasty") for person in content["people"]}
    result = []
    for article in content["articles"]:
        dynasty = dynasties.get(article["person"])
        if dynasty not in {"ming", "qing"}:
            continue
        for section in article["sections"]:
            text = spoken_text(section["title"], section["text"])
            digest = hashlib.sha256(text.encode()).hexdigest()
            filename = f"{dynasty}-{article['person']}-{section['id']}-{digest[:12]}.mp3"
            result.append({
                "articleID": article["person"],
                "sectionID": section["id"],
                "dynasty": dynasty,
                "path": filename,
                "textHash": digest,
                "text": text,
            })
    return result


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_manifest(entries: list[dict], voice: str, published: bool, output: Path) -> None:
    public_entries = []
    for item in entries:
        entry = {key: item[key] for key in ("articleID", "sectionID", "path", "textHash")}
        if published:
            entry["audioHash"] = file_hash(output / item["path"])
        public_entries.append(entry)
    data = {
        "version": 1,
        "voiceName": voice,
        "published": published,
        "baseURL": BASE_URL,
        "entries": public_entries,
    }
    MANIFEST.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def api_request(url: str, api_key: str, payload: dict) -> dict:
    body = json.dumps(payload, ensure_ascii=False).encode()
    request = urllib.request.Request(url, body, method="POST", headers={
        "Content-Type": "application/json",
        "X-Api-Key": api_key,
        "X-Api-Resource-Id": "seed-tts-2.0",
        "X-Api-Request-Id": str(uuid.uuid4()),
    })
    for attempt in range(5):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                result = json.loads(response.read())
            break
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", "replace")
            if error.code not in {429, 500, 502, 503, 504} or "requested resource not granted" in detail or attempt == 4:
                raise RuntimeError(f"Volcengine HTTP {error.code}: {detail}") from error
        except (TimeoutError, urllib.error.URLError) as error:
            if attempt == 4:
                raise RuntimeError(f"Volcengine network request failed: {error}") from error
        time.sleep(2 ** attempt)
    if result.get("code") != 20000000:
        raise RuntimeError(f"Volcengine request failed: {result}")
    return result["data"]


def synthesize(item: dict, output: Path, api_key: str, voice: str) -> None:
    destination = output / item["path"]
    if destination.exists() and destination.stat().st_size > 1024:
        return
    task_id = str(uuid.uuid4())
    payload = {
        "user": {"uid": "shiji-narration"},
        "unique_id": task_id,
        "req_params": {
            "text": item["text"],
            "speaker": voice,
            "audio_params": {
                "format": "mp3",
                "sample_rate": 24000,
                "bit_rate": 32000,
                "speech_rate": -5,
                "enable_timestamp": False,
            },
            "additions": json.dumps({
                "disable_default_bit_rate": True,
                "silence_duration": 450,
            }),
        },
    }
    submitted = api_request(SUBMIT_URL, api_key, payload)
    task_id = submitted["task_id"]
    deadline = time.monotonic() + 60 * 30
    while time.monotonic() < deadline:
        status = api_request(QUERY_URL, api_key, {"task_id": task_id})
        if status.get("task_status") == 2:
            with urllib.request.urlopen(status["audio_url"], timeout=120) as response:
                audio = response.read()
            if len(audio) < 1024:
                raise RuntimeError(f"Downloaded audio is unexpectedly small for {item['path']}")
            temporary = destination.with_suffix(".download")
            temporary.write_bytes(audio)
            temporary.replace(destination)
            return
        if status.get("task_status") == 3:
            raise RuntimeError(f"Synthesis failed for {item['path']}: {status}")
        time.sleep(2)
    raise TimeoutError(f"Timed out synthesizing {item['path']}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--synthesize", action="store_true")
    parser.add_argument("--published", action="store_true", help="Mark manifest usable after every asset has been uploaded")
    parser.add_argument("--voice", default=DEFAULT_VOICE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--article")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    entries = load_sections()
    selected = [item for item in entries if not args.article or item["articleID"] == args.article]
    if args.limit is not None:
        selected = selected[: args.limit]
    args.output.mkdir(parents=True, exist_ok=True)

    if args.synthesize:
        api_key = os.environ.get("VOLCENGINE_TTS_API_KEY")
        if not api_key:
            raise SystemExit("Set VOLCENGINE_TTS_API_KEY before synthesis; never store the key in this repository.")
        if not 1 <= args.workers <= 8:
            raise SystemExit("--workers must be between 1 and 8")
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = {pool.submit(synthesize, item, args.output, api_key, args.voice): item for item in selected}
            for index, future in enumerate(concurrent.futures.as_completed(futures), 1):
                item = futures[future]
                future.result()
                print(f"[{index}/{len(selected)}] {item['articleID']} / {item['sectionID']}", flush=True)

    if args.published:
        missing = [
            item["path"] for item in entries
            if not (args.output / item["path"]).exists() or (args.output / item["path"]).stat().st_size <= 1_024
        ]
        if missing:
            raise SystemExit(f"Cannot publish: {len(missing)} audio files are missing")
    write_manifest(entries, args.voice, args.published, args.output)
    total = sum(len(item["text"]) for item in entries)
    print(f"Prepared {len(entries)} sections / {total} characters; published={args.published}")


if __name__ == "__main__":
    main()
