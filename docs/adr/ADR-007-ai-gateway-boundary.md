# ADR-007: AI gateway as an external platform boundary

- Status: Proposed
- Date: 2026-08-24

## Context

The enterprise product direction requires model access to evolve independently from business-domain capabilities.

A production deployment may need multiple model providers, provider failover, quota-aware routing, cost and usage telemetry, API-key isolation, compatibility translation, rate controls, and model policy enforcement. Reimplementing all of those concerns inside the Knowledge or Agent domains would increase scope and couple business logic to model-provider infrastructure.

OmniRoute is an MIT-licensed AI gateway that exposes OpenAI-compatible endpoints and already implements capabilities such as provider translation, model/provider fallback, quota-aware routing, usage and cost tracking, correlation identifiers, circuit breakers, MCP/A2A support, audit logging, and provider connection management.

The platform should be able to use such a gateway without making the product depend on one gateway implementation.

## Decision

AI Knowledge Platform will treat model routing as an external boundary called the **AI Gateway**.

Domain code must depend on platform-owned model contracts rather than on OmniRoute, OpenAI, Anthropic, or another vendor SDK.

The default deployment path may support an OpenAI-compatible gateway adapter. OmniRoute is a reference integration candidate for that adapter because it can consolidate provider routing and operational concerns behind one endpoint.

The architecture remains valid when:

- a deployment connects directly to one model provider;
- a deployment uses OmniRoute;
- a customer uses another OpenAI-compatible enterprise gateway;
- a future managed gateway is introduced.

## Responsibilities

### AI Knowledge Platform owns

- tenant and organization identity;
- application authorization and RBAC;
- knowledge-source permissions;
- document ingestion, versioning, retrieval, and provenance;
- agent definitions and agent/tool authorization;
- business connectors and tool contracts;
- agent execution policy;
- platform model/provider policy;
- platform audit records linking users, agents, tools, evidence, and model calls;
- evaluation and product-level usage records.

### AI Gateway owns or may own

- provider authentication and connection management;
- model/provider routing within platform-approved policy;
- compatibility translation;
- provider/model fallback within an approved set;
- provider quotas and rate behavior;
- model-side retry and circuit breaking;
- provider-level token/cost telemetry;
- normalized model API surface.

The platform must not delegate tenant authorization, business data authorization, or final provider eligibility to the AI gateway.

## Integration contract

The first gateway adapter should target an OpenAI-compatible interface where practical.

At minimum, the adapter must support:

- chat or response generation;
- request correlation identifiers;
- model selection through a platform policy;
- timeout and cancellation behavior;
- normalized provider errors;
- usage metadata when available.

Embeddings may use the same gateway or a separate embedding provider boundary depending on evaluation and deployment requirements.

## Licensing and provider terms

OmniRoute's MIT license permits commercial use, modification, distribution, sublicensing, and sale provided the copyright and permission notice are retained in copies or substantial portions of the software.

That permission applies to OmniRoute itself. It does not override the Terms of Service, API agreements, data-processing terms, or commercial restrictions of upstream model providers.

Therefore:

- commercial/self-hosted distributions that include OmniRoute or a modified build must retain the OmniRoute license notice and applicable third-party notices;
- the project must maintain a third-party software inventory and scan transitive dependencies before commercial distribution;
- enabled upstream providers must be independently approved for the intended commercial workload;
- the platform must use an explicit provider/model allowlist rather than inheriting OmniRoute's complete provider catalog;
- official commercial APIs and customer-owned or dedicated credentials are preferred for enterprise workloads.

## Security constraints

- Gateway credentials are infrastructure secrets and are never exposed to business users or agent prompts.
- An agent cannot select arbitrary providers or models unless platform policy explicitly permits it.
- Gateway fallback must not bypass data residency, model allowlists, sensitivity restrictions, or customer policy.
- Prompt content sent to a gateway is still subject to the platform's data-access rules.
- Provider/gateway telemetry must avoid logging sensitive business content by default.
- OmniRoute should run as an isolated internal service, not as part of the domain process.
- production deployments must pin a tested gateway version or immutable image digest rather than consume a floating release.
- unused privileged or consumer-client compatibility capabilities should be disabled or excluded from the deployed artifact.
- production integrations must not depend on MITM interception, consumer browser sessions, unofficial web endpoints, or stealth/fingerprint imitation without a separate explicit review.

The detailed deployment posture is defined in [OmniRoute Enterprise Integration Profile](../security/omniroute-enterprise-profile.md).

## Consequences

### Positive

- avoids rebuilding a large provider-routing subsystem inside the platform;
- preserves provider and gateway portability;
- allows the team to focus on enterprise knowledge, agents, governance, and integrations;
- enables mature fallback, quota, and telemetry capabilities earlier when a gateway is deployed;
- supports self-hosted and dedicated enterprise deployments;
- separates open-source gateway licensing from provider-specific commercial eligibility.

### Negative

- adds another runtime component in gateway-backed deployments;
- requires clear observability across platform and gateway correlation IDs;
- gateway capabilities differ between deployments, so the platform must define a minimum contract;
- third-party gateway upgrades and security posture must be managed operationally;
- provider terms and data-processing constraints require ongoing review rather than a one-time technical integration.

## Non-decision

This ADR does not make OmniRoute a mandatory dependency and does not vendor or copy OmniRoute source into the platform.

A production integration should be evaluated, pinned, secured, supply-chain scanned, and tested independently before it becomes a supported deployment profile.
