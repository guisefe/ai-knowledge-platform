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
- platform audit records linking users, agents, tools, evidence, and model calls;
- evaluation and product-level usage records.

### AI Gateway owns or may own

- provider authentication and connection management;
- model/provider routing;
- compatibility translation;
- provider/model fallback;
- provider quotas and rate behavior;
- model-side retry and circuit breaking;
- provider-level token/cost telemetry;
- normalized model API surface.

The platform must not delegate tenant authorization or business data authorization to the AI gateway.

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

## Security constraints

- Gateway credentials are infrastructure secrets and are never exposed to business users or agent prompts.
- An agent cannot select arbitrary providers or models unless platform policy explicitly permits it.
- Gateway fallback must not bypass data residency, model allowlists, or customer policy.
- Prompt content sent to a gateway is still subject to the platform's data-access rules.
- Provider/gateway telemetry must avoid logging sensitive business content by default.

## Consequences

### Positive

- avoids rebuilding a large provider-routing subsystem inside the platform;
- preserves provider and gateway portability;
- allows the team to focus on enterprise knowledge, agents, governance, and integrations;
- enables mature fallback, quota, and telemetry capabilities earlier when a gateway is deployed;
- supports self-hosted and dedicated enterprise deployments.

### Negative

- adds another runtime component in gateway-backed deployments;
- requires clear observability across platform and gateway correlation IDs;
- gateway capabilities differ between deployments, so the platform must define a minimum contract;
- third-party gateway upgrades and security posture must be managed operationally.

## Non-decision

This ADR does not make OmniRoute a mandatory dependency and does not vendor or copy OmniRoute source into the platform.

A production integration should be evaluated, pinned, secured, and tested independently before it becomes a supported deployment profile.
