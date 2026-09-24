# Oniesoft Auto-Pilot Specialist Agents

This plugin defines specialized subagents for test creation, failure diagnosis, UI element discovery, and defect logging.

## Tool scope

`create_defect` — only call after reading and following `skills/create-defect/SKILL.md` through Step 5, or from within the `defect-creator` subagent. Never call it inline when the user asks to create a defect or log a bug without completing assignee selection (`get_users_assigned_to_project`) and user confirmation first.

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
- **Role:** Specialist for resolving UI locators. Web: CSS, XPath, Playwright (Playwright MCP allowed). Mobile: Appium/Selenium xpath only. With no mobile recording or codebase, persist selector as the literal string `selector` — never Playwright JSON or Playwright MCP.
- **When to Use:** Delegate during Phase 2 of test generation when filling out element info tables and authoring autopilot test steps.
- **Tools:** `create_element`, `update_element`, `fetch_element_details_by_id`, `get_element_details_by_name_or_unique_key`
- **Definition:** [`agents/element-discoverer.md`](agents/element-discoverer.md)

### 4. `defect-creator`
- **Role:** Specialist for logging Oniesoft defects from test failures or manual triage.
- **When to Use:** Delegate when the user asks to create a defect, log a bug, or file an issue — including after test-run analysis when failures should become defects.
- **Tools:** `create_defect`, `get_users_assigned_to_project`, `get_user_details_by_id_or_email_or_unique_key`, `get_module_id_by_name_or_unique_key`, `get_feature_id_by_name_or_unique_key`
- **Definition:** [`agents/defect-creator.md`](agents/defect-creator.md)
- **Skill:** Follow [`skills/create-defect/SKILL.md`](skills/create-defect/SKILL.md) end-to-end before calling `create_defect`.
