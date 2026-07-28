# End-to-End Testing with Cypress

## What is end-to-end testing?

End-to-end (E2E) testing verifies that a real user flow works from start to finish. Instead of testing isolated functions or modules, E2E tests simulate how a user interacts with the application in a browser.

This kind of testing is useful for checking that:

- The frontend loads correctly
- Pages render as expected
- Users can navigate between views
- Forms submit and validate properly
- Backend and frontend work together in a real workflow

E2E tests are especially valuable for validating the experience that matters most to users.

---

## Why E2E testing is important

Unit tests and integration tests check logic and component interaction, but E2E tests verify the full user journey. They help catch issues that may not appear in smaller tests, such as:

- Broken navigation
- UI rendering problems
- Incorrect form behavior
- Authentication or session issues
- Problems that only appear when the whole app is running

E2E testing gives confidence that the application works in a realistic environment.

---

## Why Cypress is used here

Cypress is a modern E2E testing framework for web applications. It is popular because it makes browser-based testing easy to write and understand.

In this project, Cypress is used because it supports:

- Running tests directly in the browser
- Easy interaction with UI elements
- Clear test structure and readable assertions
- Fast feedback during development
- Good support for real user workflows

The Cypress commands used in this project are defined in [src/package.json](../../../src/package.json).

---

## How E2E testing differs from unit and integration testing

Each testing level serves a different purpose:

- Unit testing checks small isolated pieces of logic.
- Integration testing checks that multiple parts work together.
- End-to-end testing checks that the full application works for a real user flow.

In practice, these three levels complement each other:

- Unit tests catch logic issues early.
- Integration tests catch failures between layers.
- E2E tests confirm that the complete experience works.

---

## What E2E tests usually cover

Typical Cypress E2E scenarios include:

- Opening the application in the browser
- Logging in or accessing protected pages
- Filling out forms and submitting them
- Navigating between routes/pages
- Checking that expected UI content appears
- Verifying that errors or success states are shown correctly

These tests simulate realistic actions rather than isolated code behavior.

---

## Example Cypress test

Here is a simple example of an E2E test structure:

```ts
describe('Example user flow', () => {
  it('loads the homepage', () => {
    cy.visit('/');
    cy.contains('Welcome').should('be.visible');
  });
});
```

This test opens the app and checks that a visible page element is present.

---

## How to run E2E tests

The project provides an E2E script in [src/package.json](../../../src/package.json).

To run the Cypress suite, use:

```bash
cd src
npm run e2e
```

This script starts the app and runs Cypress against the application.

To run Cypress directly, use:

```bash
cd src
npm run cypress:run
```

---

## Prerequisites

Before running E2E tests, make sure:

- The application can start locally
- The frontend and backend are accessible
- The browser environment is available
- Required dependencies are installed

If the app is not running, the E2E script may fail or time out.

---

## Best practices for E2E testing

Good E2E tests should:

- Focus on important user journeys
- Avoid unnecessary duplication
- Use clear and meaningful test names
- Keep tests resilient to minor UI changes where possible
- Prefer realistic scenarios over overly technical checks

A small number of strong E2E tests is often more valuable than a very large number of fragile ones.

---

## Common mistakes to avoid

Some common issues in E2E testing include:

- Writing tests that are too brittle
- Depending on implementation details instead of user-visible behavior
- Overly broad tests that are hard to debug
- Failing because of timing issues or missing app startup
- Testing every single page in a way that becomes hard to maintain

E2E tests should be durable enough to survive normal UI changes.

---

## When to use E2E testing

Use E2E testing when:

- You want to verify complete user workflows
- You are changing navigation, forms, or authentication flows
- You want confidence that the app works in a browser
- You need to catch issues that unit or integration tests may miss

E2E testing is especially useful before releases and for critical user journeys.

---

## Summary

End-to-end testing verifies that the application works for real users in a browser. Cypress is used in this project to automate important user flows and confirm that the frontend and backend behave correctly together.

Combined with unit and integration testing, E2E testing provides a stronger safety net for overall application quality.
