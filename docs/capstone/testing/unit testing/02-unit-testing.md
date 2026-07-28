# Unit Testing in This Project

## What is unit testing?

Unit testing is the practice of testing small, isolated pieces of code independently. A unit test checks whether one function, method, or module behaves correctly for a given input.

The goal is to verify that the smallest building blocks of the application work as expected before they are combined into larger features.

Typical examples of units include:

- A helper function that formats a value
- A validation function that checks input
- A service method that returns computed data
- A reducer or controller logic that handles a simple action

Unit tests are usually fast, reliable, and easy to run repeatedly.

---

## Why unit testing is important

Unit testing helps teams build software with more confidence. It gives developers a quick way to confirm that changes did not break existing behavior.

Benefits include:

- Catching bugs early
- Making refactoring safer
- Documenting expected behavior
- Reducing regression issues
- Improving confidence in code changes

When a test fails, it usually points to a very specific area of the code, which makes debugging easier.

---

## Why we use Jest

Jest is a popular JavaScript and TypeScript testing framework. It is widely used because it is simple to set up and provides powerful testing features out of the box.

In this project, Jest is used because it supports:

- Easy test creation with describe, it, and expect
- Fast execution for repeated checks
- TypeScript support through ts-jest
- Coverage reporting
- Mocking capabilities for isolated tests

The current Jest configuration is defined in [src/jest.config.js](../../../src/jest.config.js), and the test scripts are available in [src/package.json](../../../src/package.json).

---

## What Jest gives us

Jest helps us write tests in a readable and structured way.

Common Jest features include:

- describe(): groups related tests together
- it() or test(): defines a single test case
- expect(): checks the actual result against the expected result
- beforeEach(), afterEach(): prepares or cleans up shared state
- jest.fn() and jest.mock(): creates function spies or mocked dependencies

Example:

```ts
describe('calculator', () => {
  it('adds two numbers correctly', () => {
    expect(2 + 3).toBe(5);
  });
});
```

---

## How unit tests are organized in this project

Tests in this repository are typically placed under the test folders in the source tree. The Jest configuration is set to look for files matching the pattern:

```text
**/tests/**/*.test.ts
```

That means test files should follow a structure similar to:

```text
src/tests/backend/...
src/tests/frontend/...
```

A good unit test should usually:

1. Set up the smallest possible input
2. Call the function or module being tested
3. Assert the expected result
4. Keep the test focused on one behavior

---

## Example of a simple unit test

Here is a small TypeScript-style example:

```ts
function add(a: number, b: number): number {
  return a + b;
}

describe('add', () => {
  it('returns the sum of two numbers', () => {
    expect(add(2, 3)).toBe(5);
  });

  it('handles negative values', () => {
    expect(add(-1, 1)).toBe(0);
  });
});
```

This is a simple unit test because it checks one function in isolation.

---

## How to run unit tests

From the project source directory, run the test suite with:

```bash
cd src
npm test
```

This runs the main Jest test command defined in [src/package.json](../../../src/package.json).

Other useful commands include:

```bash
cd src
npm run test:integration
```

Runs integration-focused tests.

```bash
cd src
npm run test:all
```

Runs all configured tests.

If you want to run a specific test file, you can use:

```bash
cd src
npx jest path/to/file.test.ts
```

---

## Best practices for unit testing

Write tests that are clear, small, and meaningful.

Good practices include:

- Test one behavior per test
- Use descriptive test names
- Keep tests independent from one another
- Avoid testing implementation details when possible
- Prefer realistic input values
- Keep assertions simple and specific

A test should answer the question: “What behavior should this unit produce?”

---

## Common mistakes to avoid

Some common issues in unit testing are:

- Writing tests that depend on other tests
- Making tests too broad or too complicated
- Asserting on unrelated behavior
- Relying on brittle mocks
- Testing everything at once instead of one unit at a time

Good tests are stable and easy to understand.

---

## When to write unit tests

You should write unit tests when:

- You add a new function or module
- You change existing logic
- You fix a bug and want to prevent regressions
- You refactor code and want safety checks

In practice, unit tests are especially helpful when the code is reused or likely to be changed often.

---

## Summary

Unit testing is a core practice for building reliable software. It helps verify that small pieces of code work correctly and remain stable as the project grows.

In this project, Jest is the testing framework used to run unit tests efficiently. By writing tests regularly and running them often, the team can catch issues earlier and maintain higher software quality.

If you are new to testing, start with simple functions, write one clear expectation per test, and expand from there.
