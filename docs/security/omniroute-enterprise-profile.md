# OmniRoute Enterprise Integration Profile

## Purpose

This document defines the minimum security, licensing, and operational posture for using OmniRoute as an optional AI Gateway implementation behind AI Knowledge Platform.

OmniRoute is infrastructure, not an authorization boundary. Tenant isolation, business-data permissions, agent/tool authorization, and product audit semantics remain responsibilities of AI Knowledge Platform.

## Integration shape

The preferred deployment keeps OmniRoute as an independent internal service behind the platform-owned AI Gateway contract.

```text
AI Knowledge Platform
        |
        | platform-owned gateway adapter
        v
Internal AI Gateway endpoint
        |
        v
OmniRoute (optional implementation)
        |
        v
Approved upstream model providers
```

The platform must be able to replace OmniRoute with a direct provider or another compatible gateway without changing business-domain code.

## Licensing posture

OmniRoute is distributed under the MIT License. The license permits commercial use, modification, distribution, sublicensing, and sale, subject to retaining the copyright and permission notice in copies or substantial portions of the software.

For platform deployments:

- do not remove the OmniRoute copyright or MIT license notice;
- preserve OmniRoute `LICENSE` and applicable third-party notices when distributing OmniRoute or a modified build to customers;
- maintain a product-level third-party software inventory before any commercial distribution;
- scan transitive dependencies and generated artifacts independently of the top-level MIT license;
- record the exact OmniRoute version or commit used in every supported release.

The MIT license does not grant permission to violate an upstream model provider's Terms of Service. Provider eligibility must therefore be evaluated separately.

## Provider policy

Enterprise deployments must use an explicit allowlist. OmniRoute's full provider catalog must not automatically become the platform's provider catalog.

Default enterprise posture:

- prefer official provider APIs intended for application or commercial use;
- prefer customer-owned credentials (BYOK) or dedicated enterprise credentials;
- do not rely on consumer sessions, browser cookies, personal subscriptions, or unofficial web endpoints for production workloads;
- do not use a provider when its terms prohibit proxying, resale, third-party access, automation, or the intended customer workload;
- re-review provider terms before enabling a new provider in a commercial deployment;
- associate every allowed provider/model with data-residency, retention, sensitivity, and customer-policy metadata.

A fallback chain may contain only providers that are permitted for the same data classification and tenant policy as the original request.

## Features disabled for the enterprise profile

Production deployments must not depend on compatibility features intended to imitate official consumer clients or intercept their traffic.

Unless separately reviewed and explicitly approved, disable or physically exclude:

- MITM proxy capabilities and local root-certificate installation;
- TLS/browser fingerprint impersonation used to emulate consumer clients;
- CLI fingerprint/stealth compatibility modes;
- credential import from unrelated local applications;
- consumer-web session or cookie based provider integrations;
- free-tier routing whose provider terms are ambiguous or restrict proxy/third-party use;
- any route capable of privileged host execution that is unnecessary for the gateway service.

Prefer OmniRoute's reduced/minimal build profile or an equivalent internally reviewed build when it removes unused privileged modules from the artifact.

## Runtime isolation

OmniRoute should run as a separate container or service identity with least privilege.

Required controls:

- no public Internet ingress to the management surface;
- application-to-gateway authentication with a dedicated secret or workload identity;
- network policy allowing egress only to approved provider endpoints;
- non-root container execution where supported;
- read-only filesystem where practical;
- dedicated persistent volume only for required gateway state;
- credentials injected at runtime from a secret manager, never committed to the repository or image;
- encryption at rest for stored provider credentials;
- TLS between platform and gateway outside a trusted single-host development environment;
- management endpoints isolated from normal model-inference traffic.

## Version and supply-chain policy

Do not deploy floating `latest` tags in production.

Each supported deployment must:

- pin an OmniRoute semantic version and preferably an immutable image digest;
- maintain an SBOM for the deployed gateway artifact;
- run dependency, container, secret, and vulnerability scans;
- review OmniRoute release notes and security advisories before upgrades;
- test upgrades in staging against the platform gateway contract and evaluation suite;
- use canary or controlled rollout for production upgrades;
- maintain a rollback path to the previous known-good gateway image.

A high-severity unresolved vulnerability in the gateway or a required dependency must be able to block release promotion.

## Data protection

Before a prompt leaves AI Knowledge Platform, the platform must decide whether the selected provider is permitted to receive that data.

The gateway must not be trusted to make business authorization decisions.

Controls include:

- tenant and user authorization before generation;
- data classification before provider selection when required;
- provider/model allowlists per tenant;
- prompt minimization so only necessary context is sent upstream;
- configurable PII/secret redaction where the use case permits it;
- content logging disabled by default for sensitive workloads;
- retention limits for request metadata;
- correlation IDs instead of raw prompt text for routine operational tracing.

## Observability and audit

The platform and gateway must share a correlation identifier.

Platform audit records should capture, without requiring raw prompt storage:

- tenant and caller identity;
- agent and agent version;
- policy decision;
- requested model policy;
- gateway request identifier;
- resolved provider/model when available;
- tool/evidence references;
- token/cost metadata when available;
- outcome, latency, retries, and fallback events.

Gateway logs are operational evidence, not a substitute for product-level audit logs.

## Failure and fallback rules

Fallback is a policy decision, not only an availability feature.

The gateway adapter must fail closed when no provider satisfies the request policy. It must never fall back to a cheaper or available provider that violates:

- tenant provider allowlists;
- geographic or data-residency requirements;
- required model capabilities;
- sensitivity restrictions;
- contractual provider restrictions.

The platform should expose a gateway kill switch and a direct-provider fallback path for incident response where an approved alternative exists.

## Initial rollout

### Phase 1 — development integration

- run OmniRoute as a separate local/internal service;
- use the OpenAI-compatible API surface through one platform adapter;
- enable only one or two official API providers;
- propagate correlation IDs and normalized usage metadata;
- prove that the same application tests can run with the mock provider and gateway adapter.

### Phase 2 — hardened staging

- pin the gateway image/version;
- build the provider allowlist and model policy;
- use secret management and network isolation;
- generate an SBOM and run vulnerability scans;
- test provider outage, timeout, fallback, quota, and gateway-unavailable scenarios;
- verify that a fallback cannot escape tenant policy.

### Phase 3 — supported enterprise profile

- legal/commercial review of enabled provider terms;
- customer-level BYOK or dedicated credentials where appropriate;
- documented data-retention and residency behavior;
- operational SLOs, rollback procedure, and incident playbook;
- license and third-party notices bundled with any distributed/self-hosted product artifact.

## Acceptance gates

OmniRoute should not be described as a supported production integration until:

1. the platform has a real OpenAI-compatible gateway adapter behind its own interface;
2. tests prove that tenant authorization is enforced before gateway calls;
3. provider/model allowlists are enforced independently of OmniRoute;
4. fallback cannot bypass policy;
5. credentials and management endpoints are isolated;
6. the deployed version is pinned and supply-chain scanned;
7. production-enabled providers have been reviewed for the intended commercial use;
8. the integration can be disabled or replaced without changing domain code.
