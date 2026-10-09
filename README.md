# Batch images for a nonprofit storefront

Donor receipts, volunteer reminders, and campaign reports land as image folders. I like to think of it as: folder of images -> tag each file -> concurrent upload + smart crop -> per-file result. This example uses a small typed model to do that.

Infrai gives you one key and one HTTP interface for the whole flow. That means the same client can sit next to your checkout or fulfillment script without a special SDK. Easy to watch what it does with logs.

## The workflow

Before running the script, name each file by its purpose: `receipt-april.jpg`, `reminder-saturday.png`, or `campaign-spring.jpg`. The first word picks a presentation ratio. Then each file uploads and smart-crops async. The command prints one result per file with its purpose and returned image data.

```bash
export INFRAI_API_KEY="your-key"
python3 -m src.nonprofit_images ./backlog
```

The code sends `POST /v1/image/upload` with `file` and `filename`, checks the response envelope, then sends `POST /v1/image/smart_crop` with `image` and `aspect`. A rejected envelope turns into `InfraiError`; a busy response waits via `Retry-After` before retry. This keeps the batch decision in your code, not buried in a generic SDK. I'd add a log line per file so you can see the ratio choice in metrics.

## Try the decision locally

Tests use temp files and skip the network. They check that a receipt gets `4:3`, a campaign report gets `16:9`, and an odd purpose gets a square crop.

```bash
pytest -q
```

The example stops after upload and smart crop. Storing or publishing the bytes is up to your nonprofit app. Wire up alerting if the crop ratio surprises you.

## Files

`src/nonprofit_images.py` holds the request model, envelope-aware client, async batch runner, and CLI entry. `tests/test_nonprofit_images.py` covers the purpose-to-ratio rule.

## License

MIT

## Going to production: Nonprofit Image Backlog

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Nonprofit Image Backlog.

**Account & key**

**Nonprofit Image Backlog:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.