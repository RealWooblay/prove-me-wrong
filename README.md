# Prove Me Wrong

An AI-assisted prediction-market prototype that turns verifiable claims into
short-lived markets, displays them through a browser extension, and settles
results on-chain.

The project was built as a fast end-to-end systems experiment: prompt
validation, market generation, evidence-based resolution, browser injection,
wallet interaction, and Solidity contracts all live in one repository.

## Architecture

```text
Web content
  -> browser extension detects a claim
  -> generator validates and creates a market
  -> users take YES / NO positions
  -> resolver gathers evidence after close
  -> contract records the outcome and settlement
```

| Area | Purpose | Stack |
| --- | --- | --- |
| [`frontend/`](frontend/) | Web application and packaged extension download | Next.js, TypeScript |
| [`pred-overlay/`](pred-overlay/) | Browser overlay, wallet interaction, and market UI | React, Vite, viem |
| [`ai/`](ai/) | Market generation, coordination, evidence collection, and resolution | Python, FastAPI, SQLAlchemy |
| [`contracts/`](contracts/) | Market, pool, and token contracts | Solidity, Hardhat |

## Engineering highlights

- Separates deterministic market state from AI-generated validation and
  resolution explanations.
- Supports local SQLite development and PostgreSQL-backed deployment.
- Uses a browser extension to place the product directly in the context where
  a claim appears.
- Keeps privileged signing material on the server side; browser code contains
  no administrator private key.
- Includes explicit `YES`, `NO`, and `INSUFFICIENT_EVIDENCE` resolution states.

## Running locally

Each component has its own setup guide:

- [`ai/README.md`](ai/README.md) for the generator and resolver services.
- [`pred-overlay/README.md`](pred-overlay/README.md) for the browser extension.
- [`contracts/README.md`](contracts/README.md) for contract development.

The services read credentials and deployment settings from environment
variables. Do not place private keys or API credentials in browser code or
tracked configuration.

## Project status

This is a hackathon-era engineering prototype, not a production financial
product. The useful artifact is the system design and integration work; a real
deployment would still require contract review, authenticated administrative
routes, operational hardening, and legal/compliance work.
