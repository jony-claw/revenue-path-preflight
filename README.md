# Revenue Path Preflight

A deterministic CLI and GitHub Action that checks whether a creator product has a declared payment path **before engineering starts**.

It separates four states that launch checklists often blur:

- `payment_path_ready`: listing and payout prerequisites are declared.
- `listing_only`: a product can be listed, but payout prerequisites are missing.
- `distribution_only`: public distribution exists but the channel has no built-in payment.
- `blocked`: even listing prerequisites are missing.

No credentials are read. No platform approval, demand, revenue or legal compliance is implied.

## Why

Autonomous agents and indie developers can spend hours building before discovering that payout needs KYC, a bank account, Stripe/PayPal, a tax interview, account review, or a minimum threshold. This tool makes those blockers explicit and source-backed.

The initial catalog is intentionally narrow: Portugal plus Apify, Polar, Gumroad, Ko-fi, itch.io and GitHub public releases. Facts are dated `2026-11-23`; contributions for other countries are welcome when backed by first-party sources.

## Demand test: request coverage

Need a platform/country pair checked before you build? [Open a structured coverage request](https://github.com/jony-claw/revenue-path-preflight/issues/new?template=platform-country-request.yml). Public requests are the signal used to prioritize catalog additions; a request is not a promise of implementation, platform approval, or revenue.

The initial demand hypothesis is specific: autonomous agents and small software teams will use a CI gate to avoid engineering products whose listing or payout path is blocked. Stars and page views are weak signals; external issues, forks, Action usage, and paid-platform adoption are stronger signals.

## Run

```bash
python3 preflight.py examples/overnight-portugal.json
```

Fail CI when no complete paid path is declared:

```bash
python3 preflight.py profile.json --fail-if-no-payment-path
```

Example profile:

```json
{
  "country": "PT",
  "capabilities": [
    "apify_account",
    "accept_store_terms",
    "tested_product",
    "government_id",
    "billing_details",
    "payout_method"
  ]
}
```

## GitHub Action

```yaml
- uses: jony-claw/revenue-path-preflight@v0.1.0
  with:
    profile: commerce-profile.json
    fail-if-no-payment-path: "true"
```

The Action writes a Markdown table to the job summary and returns exit code 2 when no paid path is complete.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## Data policy

Each platform record must include:

1. a concrete capability requirement;
2. a first-party source URL;
3. a `checked_on` date;
4. no claim that listing or KYC approval is guaranteed.

## Limitations

This is a preflight, not financial, tax or legal advice. Platform rules change. Verify the linked first-party sources before relying on a result. `payment_path_ready` means the declared prerequisites match the catalog; it does not mean a sale occurred.
