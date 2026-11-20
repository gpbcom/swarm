# T0.10: Implementation choices

**Ticket:** [TICKET.md](TICKET.md) · **How it works:** [EXPLAIN.md](EXPLAIN.md) · **Review:** [REVIEW.md](REVIEW.md)

## 🎯 Constraints

- An unsigned image is refused by the dev cell, Playwright tests the real images and not a development server, its failure report is uploaded, and no SHA tag is published off `develop` and `master` ([TICKET.md](TICKET.md)).
- Images are built from the repository root, one per service or front end ([`AGENT.md`](../../../AGENT.md)).
- Steps 1 and 2 of the pipeline are earlier work: images build only once those checks pass ([`.github/workflows/ci.yml:88-98`](../../../.github/workflows/ci.yml#L88-L98)).
- No secret in code: GHCR uses `GITHUB_TOKEN` and signing is keyless.
- The roadmap gives no admission mechanism (assumption accepted below).

## ⚖️ Choices at a glance

| # | Decision | Chosen | Main alternative | Trade-off accepted |
| --- | --- | --- | --- | --- |
| [D1](#d1) | How the dev cell refuses unsigned images | Sigstore policy-controller, enforce mode, scoped to Swarm images and opted-in namespaces | Not recorded by the workers (open point) | Private GHCR signatures are not yet readable by the controller |
| [D2](#d2) | When to add the SHA tag | Same signed digest, only on `develop` and `master` pushes | Not recorded (open point) | One extra job and verify |
| [D3](#d3) | Where the images workflow lives | A reusable `images.yml` called by `ci.yml` | Not recorded (open point) | Fulcio subject names `images.yml`, not `ci.yml` |
| [D4](#d4) | How Playwright refuses a dev server | `defineE2eConfig` throws on `webServer` and requires `SWARM_IMAGE_TAG` | Convention only | A shared package holds the smoke spec for now |

## <a id="d1"></a>D1: How the dev cell refuses unsigned images

**Chosen:** Sigstore policy-controller with a ClusterImagePolicy in enforce mode on `ghcr.io/gpbcom/swarm/**`, keyless identities from `images.yml` only, the `policy.sigstore.dev/include` namespace label, and a server-side dry-run probe · **Where:** [`deploy/environments/dev/platform/cluster-image-policy.yaml:9-17`](../../../deploy/environments/dev/platform/cluster-image-policy.yaml#L9-L17), [`deploy/terraform/modules/self-hosted/cell/main.tf:8`](../../../deploy/terraform/modules/self-hosted/cell/main.tf#L8), [`deploy/scripts/dev-cell.sh:106`](../../../deploy/scripts/dev-cell.sh#L106) · **Source:** PLAN.md assumption, read from the diff

| Option | For | Against |
| --- | --- | --- |
| ✅ Enforce for Swarm images, warn elsewhere | The security page asks that admission accepts only signed images, and this applies it to Swarm's own images without breaking third-party platform charts | Third-party images are not checked |
| Enforce on every image | Stricter | Not recorded as considered; the reviewer called the chosen scope the conservative reading |

**Trade-off:** the probe passes on any kubectl error and its default image does not exist, and policy-controller cannot yet read private signatures (follow-ups).

**Revisit when:** the cell first deploys a Swarm image, or when platform charts are signed.

## <a id="d2"></a>D2: When to add the SHA tag

**Chosen:** every run pushes `run-<id>-<attempt>`; the `publish` job adds the commit SHA tag to the same digest only on `develop` or `master` pushes, then verifies it · **Where:** [`.github/workflows/ci.yml:98`](../../../.github/workflows/ci.yml#L98), [`.github/workflows/images.yml:178`](../../../.github/workflows/images.yml#L178) · **Source:** read from the diff

| Option | For | Against |
| --- | --- | --- |
| ✅ Run tag first, SHA tag later | Playwright can pull images from any branch while acceptance criterion 4 holds | An extra job |
| Not recorded | Open point: the workers recorded no alternative | |

**Trade-off:** run tags exist for branches too, and are not retained by any policy recorded here.

**Revisit when:** a retention policy for GHCR is set (open point).

## <a id="d3"></a>D3: Where the images workflow lives

**Chosen:** a reusable workflow, started after every step 2 check · **Where:** [`.github/workflows/images.yml`](../../../.github/workflows/images.yml), [`.github/workflows/ci.yml:88`](../../../.github/workflows/ci.yml#L88) · **Source:** read from the diff

| Option | For | Against |
| --- | --- | --- |
| ✅ Reusable workflow | Matches `python.yml`, `rust.yml`, `typescript.yml` and `specs.yml` | The signing subject is `images.yml@refs/...`, which the policy and verify step must match |
| Steps inside `ci.yml` | Not recorded | Open point |

**Trade-off:** the identity in [`deploy/environments/dev/platform/cluster-image-policy.yaml:17`](../../../deploy/environments/dev/platform/cluster-image-policy.yaml#L17) must change if the workflow is renamed.

**Revisit when:** the workflow is renamed or split.

## <a id="d4"></a>D4: How Playwright refuses a development server

**Chosen:** `defineE2eConfig` throws on a `webServer` and requires `SWARM_IMAGE_TAG` · **Where:** [`packages/ts/e2e/src/define-e2e-config.ts:22`](../../../packages/ts/e2e/src/define-e2e-config.ts#L22) · **Source:** read from the diff

| Option | For | Against |
| --- | --- | --- |
| ✅ A shared config that refuses it | The AGENT.md rule "never a development server" is enforced in code and tested | The smoke spec sits in the shared package until a front end exists ([`packages/ts/e2e/e2e/images.spec.ts:1`](../../../packages/ts/e2e/e2e/images.spec.ts#L1)) |
| Convention in AGENT.md only | Less code | Unenforced; not recorded as considered |

**Trade-off:** specs must later move to each front end.

**Revisit when:** the first front end image lands.

## 📝 Assumptions behind the choices

- The admission mechanism, which the row does not give, is Sigstore policy-controller in enforce mode for Swarm images with warn elsewhere: supports [D1](#d1).
- The roadmap row names no feature, use case or business rule: supports [D3](#d3), as the technical sections settle the scope.
