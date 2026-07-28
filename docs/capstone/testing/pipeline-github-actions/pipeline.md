# CI Pipeline for Pull Requests

## What this pipeline does

This project includes a GitHub Actions workflow that runs automatically for pull requests. Its purpose is to validate the application before changes are merged.

The workflow is defined in [.github/workflows/ci.yml](/.github/workflows/ci.yml).

It runs three main test stages:

1. Unit tests
2. Integration tests
3. End-to-end tests with Cypress

Each stage is executed in a separate job so failures are easier to identify and debug.

---

## Why the pipeline exists

A CI pipeline helps maintain software quality by automatically checking changes in a consistent environment.

Benefits include:

- Running tests on every pull request
- Preventing broken code from being merged
- Providing fast feedback to contributors
- Ensuring the project remains stable as it grows
- Validating both backend and frontend behavior

This is especially important in a project with multiple layers, such as APIs, services, databases, and a web interface.

---

## How the workflow is triggered

The workflow is configured to run on pull requests with the following trigger:

- Pull request opened
- Pull request synchronized
- Pull request reopened

It is limited to the branch pattern used by this repository for the current development line.

---

## Pipeline structure

The CI workflow contains three jobs:

### 1. Unit Tests

The unit-test job runs the basic Jest suite for isolated logic checks.

It performs the following steps:

- Checks out the repository
- Sets up Node.js
- Installs dependencies
- Generates Prisma clients
- Runs the unit test suite

### 2. Integration Tests

The integration-test job runs more realistic tests that exercise multiple components together.

It includes:

- Postgres and Redis services
- A MongoDB replica set container
- Prisma client generation
- Database migrations
- The integration test command

This job is important because it validates how the backend services and data layers behave together.

### 3. E2E Tests

The E2E job runs after the integration tests pass. It uses Cypress to test browser-based workflows.

It includes:

- Starting the application environment with Docker Compose
- Preparing the required services
- Installing frontend and backend dependencies
- Running the E2E suite
- Uploading screenshots and videos if a test fails

This stage ensures the application works for real user journeys.

---

## Test commands used by the workflow

The workflow uses the project scripts defined in [src/package.json](/src/package.json):

- Unit tests: npm test
- Integration tests: npm run test:integration
- E2E tests: npm run e2e

These scripts are executed inside the source directory of the application.

---

## Environment setup in CI

The pipeline configures several environment variables so the tests run correctly in GitHub Actions. These include:

- Node environment settings
- Secret values for authentication
- Database connection details
- Redis connection details
- Backend URL values for solver and external services

This helps create a controlled environment that is close to a real test setup.

---

## Artifact collection

If Cypress tests fail, the workflow stores screenshots and videos as artifacts. This makes debugging failures much easier.

Artifacts are uploaded for:

- Cypress screenshots
- Cypress videos

---

## Why this matters for contributors

For contributors, this pipeline acts as a quality gate. Before a pull request is merged, the project verifies that:

- the code still passes unit tests
- the integrated components still work together
- the main user workflows still function

That reduces the risk of regressions and improves trust in the codebase.

---

## Summary

The CI pipeline for this project automatically runs unit, integration, and E2E tests for pull requests. It provides a dependable way to validate new changes before they are merged.

Together, these checks help ensure that the application remains reliable, testable, and ready for continued development.
