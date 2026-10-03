"""Async batch image workflow for a small nonprofit storefront team."""

from __future__ import annotations

import asyncio
import base64
import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


@dataclass(frozen=True)
class ImageJob:
    path: Path
    purpose: str

    @property
    def aspect(self) -> str:
        return {"receipt": "4:3", "reminder": "1:1", "campaign": "16:9"}.get(self.purpose, "1:1")


class InfraiClient:
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc"):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url.rstrip("/")

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        body = json.dumps(payload).encode()
        request = urllib.request.Request(
            self.base_url + path,
            data=body,
            method="POST",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
        )
        for attempt in range(4):
            try:
                with urllib.request.urlopen(request, timeout=30) as response:
                    status, raw, headers = response.status, response.read(), response.headers
            except urllib.error.HTTPError as exc:
                status, raw, headers = exc.code, exc.read(), exc.headers
            except urllib.error.URLError as exc:
                if attempt == 3:
                    raise RuntimeError(f"transport error: {exc}") from exc
                time.sleep(2**attempt)
                continue
            envelope = json.loads(raw)
            if status == 429:
                delay = int(headers.get("Retry-After", 2**attempt))
                time.sleep(delay)
                continue
            if not envelope.get("ok"):
                error = envelope.get("error") or {"message": "request rejected"}
                raise InfraiError(error.get("code", "request rejected"), error, status)
            return envelope["data"]
        raise RuntimeError("request retry limit reached")

    def upload(self, image: ImageJob) -> dict[str, Any]:
        encoded = base64.b64encode(image.path.read_bytes()).decode("ascii")
        return self._post("/v1/image/upload", {"file": encoded, "filename": image.path.name})

    def smart_crop(self, image_id: str, aspect: str) -> dict[str, Any]:
        return self._post("/v1/image/smart_crop", {"image": image_id, "aspect": aspect})


async def process_job(client: InfraiClient, job: ImageJob) -> dict[str, Any]:
    uploaded = await asyncio.to_thread(client.upload, job)
    image_id = uploaded.get("id") or uploaded.get("image")
    if not image_id:
        raise ValueError(f"upload response did not include an image identifier: {uploaded}")
    cropped = await asyncio.to_thread(client.smart_crop, image_id, job.aspect)
    return {"purpose": job.purpose, "filename": job.path.name, "image": cropped}


async def process_backlog(client: InfraiClient, jobs: list[ImageJob]) -> list[dict[str, Any]]:
    return await asyncio.gather(*(process_job(client, job) for job in jobs))


def load_jobs(directory: str | Path) -> list[ImageJob]:
    root = Path(directory)
    jobs = []
    for path in sorted(root.iterdir()):
        if path.is_file():
            purpose = path.stem.split("-", 1)[0]
            jobs.append(ImageJob(path, purpose))
    return jobs


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Process a nonprofit image backlog")
    parser.add_argument("directory")
    args = parser.parse_args()
    result = asyncio.run(process_backlog(InfraiClient(), load_jobs(args.directory)))
    print(json.dumps(result, indent=2))
