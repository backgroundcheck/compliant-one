# compliant-one

Modern compliance and risk-intelligence platform.

## Features
- Sanctions & PEP screening
- KYC/CDD/EDD workflows
- OSINT intelligence & adverse media
- Beneficial ownership (UBO) analysis
- Breach intelligence
- Reporting & audit

## Quickstart (Docker)
- docker compose -f docker-compose.prod.yml up -d postgres redis breach-api
- Open http://localhost:8080/docs

## Environment
- DATABASE_URL (Postgres), or SQLite fallback
- REDIS_URL
- ALLOWED_ORIGINS

## API Highlights
- POST /api/v1/sanctions/screen
- POST /api/v1/kyc/verify
- POST /api/v1/osint/search
- POST /api/v1/beneficial-ownership/analyze
- POST /api/v1/breach-intel/check-credential

## License
See LICENSE.
