# Oniesoft Auto-Pilot Specialist Agents

This plugin defines three specialized subagents for test creation, failure diagnosis, and UI element discovery.

## Available Agents

### 1. `test-author`
- **Role:** Specialist for authoring Oniesoft test cases across many features/endpoints.
- **When to Use:** Delegate when the user wants to generate a batch of web, API, or mobile test cases from requirements, an OpenAPI spec, or user stories.
- **Tools:** `create_test_cases`, `analyze_test_steps`, `save_claude_test_cases`
- **Definition:** [`agents/test-author.md`](agents/test-author.md)

### 2. `failure-analyst`
- **Role:** Specialist for post-run triage and root-cause analysis of test failures.
- **When to Use:** Delegate when the user wants to diagnose why a test run failed, compare multiple runs, or interpret stack traces.
- **Tools:** `fetch_test_run_results`, `fetch_test_run_failure_details`, `fetch_element_details_by_id`, `fetch_util_details`
- **Definition:** [`agents/failure-analyst.md`](agents/failure-analyst.md)

### 3. `element-discoverer`
- **Role:** Specialist for resolving UI element locators (CSS, XPath, Playwright) from codebases, recordings, or live browsers.
- **When to Use:** Delegate during Phase 2 of test generation when filling out element info tables and authoring autopilot test steps.
- **Tools:** `create_element`, `update_element`, `fetch_element_details_by_id`, `get_element_details_by_name_or_unique_key`
- **Definition:** [`agents/element-discoverer.md`](agents/element-discoverer.md)
