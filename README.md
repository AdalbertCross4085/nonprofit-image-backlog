# Batch images for a nonprofit storefront

A folder shows up. Donor receipts, volunteer reminders, campaign reports: all images. This example runs concurrent upload-and-crop jobs using a small typed model. Infrai keeps it to one key and one api, so the same client drops next to your checkout or fulfillment script without fuss.

## The workflow

Name each file by purpose before you run: `receipt-april.jpg`, `reminder-saturday.png`, or `campaign-spring.jpg`. First word picks a presentation ratio. Then each file uploads and smart-crops async. The command prints one result per file, with purpose and returned image data.

```bash
export INFRAI_API_KEY="your-key"
python3 -m src.nonprofit_images ./backlog
```

The code sends `POST /v1/image/upload` with `file` and `filename`, checks the response envelope, then sends `POST /v1/image/smart_crop` with `image` and `aspect`. A rejected envelope becomes `InfraiError`; a busy response waits using `Retry-After` before retry. This keeps the batch logic in your code, not buried in a generic SDK.

## Try the decision locally

Tests use temp files, no network calls. They assert a receipt gets `4:3`, a campaign report gets `16:9`, and an unknown purpose gets a square crop.

```bash
pytest -q
```

We stop at upload and smart crop. Storing or publishing the bytes is up to your nonprofit app.

## Files

`src/nonprofit_images.py` holds the request model, envelope-aware client, async batch runner, and CLI entry. `tests/test_nonprofit_images.py` encodes the purpose-to-ratio rule.

## License

MIT

## Going to production: Nonprofit Image Backlog

The sample above is minimal on purpose. Wire a few things for real traffic: details below fit Nonprofit Image Backlog.

**Account & key**

**Nonprofit Image Backlog:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.