from pathlib import Path

from src.nonprofit_images import ImageJob, InfraiClient, load_jobs


def test_purpose_selects_storefront_crop_ratio(tmp_path: Path):
    (tmp_path / "receipt-april.jpg").write_bytes(b"receipt")
    (tmp_path / "campaign-spring.jpg").write_bytes(b"campaign")
    jobs = load_jobs(tmp_path)
    assert [job.aspect for job in jobs] == ["16:9", "4:3"]


def test_unknown_purpose_uses_square_crop(tmp_path: Path):
    (tmp_path / "volunteer.jpg").write_bytes(b"image")
    assert load_jobs(tmp_path)[0].aspect == "1:1"


def test_upload_encodes_binary_image_as_base64(tmp_path: Path, monkeypatch):
    image = tmp_path / "receipt-april.png"
    image.write_bytes(b"\x00\xff\x80")
    client = InfraiClient(api_key="test")
    requests = []
    monkeypatch.setattr(client, "_post", lambda path, payload: requests.append((path, payload)) or {})

    client.upload(ImageJob(image, "receipt"))

    assert requests == [("/v1/image/upload", {"file": "AP+A", "filename": image.name})]
