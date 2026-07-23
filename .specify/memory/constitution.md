<!--
Sync Impact Report
==================
Version change: (template, unratified) → 1.0.0
Modified principles: N/A (initial adoption)
Added principles:
  - I. Language and Localization Standards
  - II. Code Quality
  - III. Testing Standards
  - IV. User Experience Consistency
  - V. Performance Requirements
  - VI. Code Review Standards
  - VII. Documentation Requirements
  - VIII. Security Standards
Added sections:
  - Tooling and Automation
  - Governance (Enforcement, Amendment Process, Versioning Policy, Exceptions)
Removed sections: none (all template placeholders replaced)
Templates requiring updates:
  - .specify/templates/spec-template.md ✅ updated (zh-TW language requirement noted)
  - .specify/templates/plan-template.md ✅ updated (zh-TW language requirement noted)
  - .specify/templates/tasks-template.md ✅ updated (zh-TW language requirement noted)
  - .specify/templates/checklist-template.md ⚠ pending (no language-specific mandate added; review if checklists are treated as user-facing docs)
  - .github/prompts/*.prompt.md ⚠ pending (no agent-specific or language-blocking references found; no changes required)
Follow-up TODOs:
  - RATIFICATION_DATE assumed as the date of this initial adoption (2026-07-23) since no prior ratified version existed; confirm if an earlier adoption date should be recorded instead.
-->

# fastapi_speckit Constitution

## Core Principles

### I. Language and Localization Standards

All feature specifications, project plans, and user-facing documentation MUST be written in
Traditional Chinese (zh-TW). User interface text, content, error messages, tooltips, and help
text MUST be in Traditional Chinese (zh-TW). Code comments MAY be written in English or
Traditional Chinese; variable and function names SHOULD use English for international
compatibility. Commit messages MAY be in English or Traditional Chinese, and internal API
documentation MAY be bilingual. Traditional Chinese content MUST use proper Taiwan terminology
(台灣用語) with a consistent translation glossary, MUST NOT rely on unreviewed machine
translation, and MUST be culturally appropriate.

**Rationale**: Specs, plans, and shipped UI copy target Traditional-Chinese-speaking
stakeholders and users; enforcing one documentation language prevents ambiguity while English
identifiers keep the codebase internationally maintainable.

### II. Code Quality

Code MUST prioritize clarity over cleverness, with names that reveal intent. Functions MUST
stay under 50 lines (target under 20) and do one thing well. Formatting MUST be automated
(e.g., Prettier, Black, gofmt) and applied consistently; any deviation from an established
style guide MUST be documented with justification. Code MUST be self-documenting — comments
explain "why", not "what". Duplication MUST be eliminated (DRY) through refactoring, and
dependencies MUST be kept minimal and current. Static typing MUST be used where the language
supports it; input MUST be validated at system boundaries; invalid states MUST be made
unrepresentable; compile-time errors are preferred over runtime failures.

**Rationale**: Consistent, typed, simple code reduces defects and onboarding cost, and keeps
the codebase changeable as requirements evolve.

### III. Testing Standards

Production code MUST maintain a minimum of 80% coverage; critical paths (authentication,
payments, data integrity) MUST reach 100% coverage. New features MUST ship with tests before
merge; bug fixes MUST include a regression test. The suite MUST approximate a 70% unit / 20%
integration / 10% end-to-end distribution, with end-to-end tests reserved for critical user
journeys. Tests MUST be deterministic (no tolerated flakiness), verify exactly one behavior,
use descriptive names (e.g., `test_user_cannot_access_unauthorized_resource`), follow
Arrange-Act-Assert, and mock external dependencies. All tests MUST run automatically and pass
on every commit before merge; performance and security scanning MUST be integrated into the
same pipeline.

**Rationale**: A disciplined test pyramid with enforced coverage thresholds catches
regressions early and keeps CI fast and trustworthy.

### IV. User Experience Consistency

All UI components MUST use the established design system; custom colors, fonts, or spacing
outside the system are NOT permitted, and design tokens MUST stay consistent across platforms
with regular audits. Navigation, keyboard shortcuts, accessibility controls, error handling,
and loading states MUST be consistent and predictable. Interfaces MUST meet WCAG 2.1 Level AA
at minimum: semantic HTML, proper ARIA labels, full keyboard navigation, compliant color
contrast, and screen-reader testing for critical flows. Development MUST be mobile-first with
touch targets of at least 44x44 pixels, graceful degradation across breakpoints, and
performance optimization for mobile networks. Voice, tone, terminology (per glossary), and
microcopy MUST be unified; error messages MUST guide users toward resolution.

**Rationale**: Consistent, accessible experiences build user trust and reduce support burden
across platforms.

### V. Performance Requirements

Core Web Vitals MUST meet: LCP < 2.5s, FID < 100ms, CLS < 0.1, TTFB < 600ms. API responses
MUST meet p95 < 200ms and p99 < 500ms; common database queries MUST complete in < 100ms; page
load MUST be < 3s on 3G; Time to Interactive MUST be < 5s. The initial JS bundle MUST stay
under 200KB gzipped; images MUST be optimized and lazy-loaded; the critical CSS path MUST be
optimized; render-blocking resources MUST be minimized; static assets MUST be served via CDN.
Systems MUST be designed for horizontal scaling from day one, with proper caching (Redis,
CDN), indexed database queries, rate limiting on public endpoints, and load testing before
major releases. Production MUST have Real User Monitoring, Application Performance Monitoring,
error tracking/alerting within 5 minutes, enforced performance budgets in CI/CD, and weekly
performance reviews.

**Rationale**: Explicit, measurable performance budgets prevent silent regressions and keep
the product usable at scale.

### VI. Code Review Standards

Every change MUST be reviewed by at least one peer; critical changes MUST have two reviewers.
Authors MUST NOT approve their own PRs. Reviews MUST complete within 24 hours, and approval
requires all automated checks to pass. Reviews MUST evaluate: requirement fulfillment, adequate
test coverage, adherence to the code quality principles, performance implications, UX
consistency, security concerns, and documentation updates.

**Rationale**: Structured, timely peer review is the last line of defense for quality,
security, and consistency before code ships.

### VII. Documentation Requirements

Public APIs MUST be fully documented; complex algorithms MUST be explained; setup instructions
MUST live in the README; significant architectural choices MUST be captured as Architecture
Decision Records (ADRs). Feature documentation MUST ship with the feature; API documentation
MUST be auto-generated and versioned; a changelog MUST be maintained for all releases; breaking
changes MUST include migration guides.

**Rationale**: Documentation that ships with the code keeps users and future maintainers
unblocked.

### VIII. Security Standards

All input MUST be validated and sanitized; output MUST be encoded to prevent XSS; queries MUST
be parameterized to prevent SQL injection; access MUST follow least privilege; security headers
MUST be properly configured. Sensitive data MUST be encrypted at rest; data in transit MUST use
TLS 1.3; credentials MUST NOT be stored in code; dependencies MUST be audited regularly for
known vulnerabilities; PII handling MUST comply with applicable regulations (e.g., GDPR, CCPA).

**Rationale**: Security is non-negotiable; these controls address the most common and
highest-impact vulnerability classes.

## Tooling and Automation

Recommended tooling MUST be adopted unless an equivalent is documented as an approved
substitute:

- **Linting**: ESLint, Pylint, RuboCop
- **Formatting**: Prettier, Black, gofmt
- **Testing**: Jest, pytest, RSpec
- **Performance**: Lighthouse CI, WebPageTest
- **Security**: Snyk, OWASP ZAP
- **Monitoring**: Sentry, DataDog, New Relic, Grafana, Prometheus, Loki, Tempo

## Governance

This constitution supersedes all other development practices and guidelines. All PRs and
reviews MUST verify compliance with the principles above; any complexity or deviation MUST be
explicitly justified in the PR description or an ADR.

**Enforcement**: Compliance is enforced via automated checks in CI/CD, regular code quality
audits, performance monitoring dashboards, and a quarterly constitution review.

**Amendment Process**: Amendments require a written proposal and team discussion, and MUST be
approved by a 2/3 team consensus before merge. Breaking changes to established practices MUST
include an implementation grace period. Version history MUST be maintained in this repository.

**Versioning Policy**: This constitution follows semantic versioning:
- **MAJOR**: Backward-incompatible governance or principle removals/redefinitions.
- **MINOR**: New principle or materially expanded guidance added.
- **PATCH**: Clarifications, wording, or non-semantic refinements.

**Exceptions**: Any exception requires written justification, approval from the tech lead, a
documented resolution timeline, and tracking as technical debt.

**Version**: 1.0.0 | **Ratified**: 2026-07-23 | **Last Amended**: 2026-07-23
