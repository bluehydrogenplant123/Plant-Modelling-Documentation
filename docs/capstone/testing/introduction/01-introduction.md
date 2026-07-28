# Testing and Quality Assurance Introduction

This document is the entry point for the project’s testing and quality assurance documentation. It explains the purpose of automated testing, the testing layers used in this repository, and how the CI pipeline supports quality checks for pull requests.

---

## Why we test

Testing is an essential part of software development because it helps reduce risk, improve reliability, and make changes safer over time.

A strong testing strategy helps the team:

- catch bugs early
- reduce regressions when code changes
- make refactoring safer
- document expected behavior in executable form
- improve confidence before merging new work

In practice, testing is not only about finding errors. It is also about making the system easier to maintain and evolve.

---

## Testing philosophy

The project uses a layered testing approach so that different types of issues are caught at the right stage.

- Unit tests verify small, isolated pieces of logic.
- Integration tests verify that separate components work correctly together.
- End-to-end tests verify complete user workflows in a browser.

This combination gives broad coverage without relying on a single testing method.

---

## Testing stack

The project uses the following tools:

- Jest for unit and integration testing
- Cypress for end-to-end browser testing
- GitHub Actions for automated CI validation on pull requests

These tools are used together to support both fast feedback during development and stronger validation before release.

---

## Testing pyramid

The project follows a practical testing pyramid:

```text
      /\
     /  \    E2E tests (Cypress)
    / E2E \  Full user journeys, slower but realistic
   /------\
  / Integr.\ Integration tests (Jest)
 /----------\ Communication between modules and services
/  Unit     \ Unit tests (Jest)
------------- Isolated logic and helpers
```

This structure keeps the test suite balanced: fast checks for small logic, broader checks for connected components, and realistic checks for important user flows.

---

## CI and pull request validation

Every pull request is validated through a CI workflow that runs the project’s automated tests. This ensures that new changes are checked in a consistent environment before they are merged.

The workflow executes:

- unit tests
- integration tests
- end-to-end tests

The corresponding documentation for these topics is available here:

- [Unit testing guide](../unit%20testing/02-unit-testing.md)
- [Integration testing guide](../integration%20testing/03-integration-testing)
- [E2E testing guide](../e2e%20testing/e2e.md)
- [CI pipeline guide](../pipeline-github-actions/pipeline.md)

---

## Summary

This documentation set provides a complete view of how testing is approached in this project. Together, these guides explain the purpose of testing, the tools used, the testing levels, and the automation that helps keep the application reliable.
