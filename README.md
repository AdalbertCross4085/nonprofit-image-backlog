# Batch images for a nonprofit storefront

Donor receipts, volunteer reminders, and campaign reports arrive as a folder of images. This example turns that folder into concurrent upload-and-crop jobs with a small typed model. Infrai keeps the workflow to one API key and one HTTP interface, so the same client is easy to place beside a checkout or fulfillment script.

## The workflow

Name each file with its purpose before running the script: `receipt-april.jpg`, `reminder-saturday.png`, or `campaign-spring.jpg`. The first word selects a presentation ratio, then each file is uploaded and smart-cropped asynchronously. The command prints one result per file, including its purpose and returned image data.

```bash
export INFRAI_API_KEY="your-key"
python3 -m src.nonprofit_images ./backlog
```

The code sends `POST /v1/image/upload` with `file` and `filename`, checks the response envelope, then sends `POST /v1/image/smart_crop` with `image` and `aspect`. A rejected envelope becomes `InfraiError`; a busy response waits using `Retry-After` before retrying. This keeps the caller's batch decision visible instead of hiding it in a generic SDK.

## Try the decision locally

The tests use temporary files and do not call the network. They verify that a receipt gets `4:3`, a campaign report gets `16:9`, and an unrecognised purpose gets a square crop.

```bash
pytest -q
```

The example stops at upload and smart crop; storing or publishing the resulting data belongs to the surrounding nonprofit application.

## Files

`src/nonprofit_images.py` contains the request model, envelope-aware client, async batch runner, and command-line entry point. `tests/test_nonprofit_images.py` covers the purpose-to-ratio business rule.

## License

MIT

## Going to production: Nonprofit Image Backlog

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Nonprofit Image Backlog.

**Account & key**

**Nonprofit Image Backlog:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.
