# T0.10: Review note

**Verdict:** ✅ Approved · **Branch:** `feature/tickets`

## What changed

- `detect_changes.py` prints a sixth output, `images`: every changed `services/<x>` or `frontends/<x>` folder that holds a Dockerfile. `.github/workflows/images.yml`, `compose.e2e.yaml` and `.dockerignore` count as shared files and select everything.
- A new reusable `images.yml` runs once every step 2 check passes, in this order: OSV-Scanner on the three lock files, then a multi-stage build from the repository root with the gha cache under a run tag, then Trivy (fails on fixable HIGH or CRITICAL), the CycloneDX SBOM, the push, keyless cosign sign and attest, and a verify by digest.
- Playwright runs through `compose.e2e.yaml` against the pulled run-tag images, never a build or a dev server. `@swarm/e2e` refuses a `webServer` and requires `SWARM_IMAGE_TAG`. The HTML report is uploaded on failure.
- The commit SHA tag is added to the same signed digest only on pushes to `develop` or `master`, then verified.
- The dev cell refuses unsigned Swarm images in three places: the Sigstore policy-controller with an enforcing ClusterImagePolicy, the cell namespace's `policy.sigstore.dev/include` label, and a server-side dry-run probe at the end of `dev-cell.sh up`.

## Acceptance criteria

| Criterion | Evidence | Result |
| --- | --- | --- |
| 1. Given an unsigned image, when the dev cell is asked to run it, then the dev cell refuses it | `tests/deploy/environments/test_image_admission.py`, `test_up_fails_when_the_cell_accepts_an_unsigned_image` and `test_up_ends_with_a_server_side_probe_of_an_unsigned_image` in `tests/deploy/scripts/test_dev_cell_script.py`, `tests-evidences/terraform-test-deploy-terraform-modules-self-hosted-cell.txt`, `tests-evidences/pytest.txt` | ✅ Pass (static; no live cell was run) |
| 2. Given the real images started by `compose.e2e.yaml`, when Playwright runs against them, then it tests those images and not a development server | `tests/ci/e2e/test_compose_e2e.py`, `refuses a development server` in `packages/ts/e2e/test/define-e2e-config.test.ts` (`tests-evidences/test.txt`), `test_e2e_starts_the_compose_stack_with_the_image_tag` | ✅ Pass |
| 3. Given a Playwright test that fails, when the run ends, then its HTML report is uploaded | `test_e2e_uploads_the_report_on_failure` in `tests/ci/images/test_images_workflow.py`; the html reporter is checked in `define-e2e-config.test.ts` | ✅ Pass |
| 4. Given a commit on a branch other than `develop` or `master`, when the pipeline runs, then no image is published tagged with the commit SHA | `test_images_are_published_from_develop_and_master_pushes_only` (`tests/ci/workflows/test_ci_workflow.py`), `test_no_image_step_tags_with_the_commit_sha`, `test_publishing_depends_on_the_publish_input` | ✅ Pass |

## Look at first

- **Shared files before you approve the push:** `AGENT.md` and `pnpm-lock.yaml` are whole files in this ticket's diff, but they hold other running tickets' work: the REST contract, the simulator, synthetic Drones, swarm-storage and swarm-rest, the PostgreSQL fixtures, and the front-end and UI importers. Only the K18 hunks of AGENT.md (local image build, Playwright run, the images.yml step list, Docker images and Front-end tests bullets, the test locations) belong to T0.10.
- **Signing identity:** `.github/workflows/images.yml` (sign, attest and verify steps) and `deploy/environments/dev/platform/cluster-image-policy.yaml`. The Fulcio subject of a reusable workflow is `images.yml@refs/...`, which is what both the verify step and the policy expect.
- **Publish gate:** `.github/workflows/ci.yml` (the `images` job, `publish:` expression) and the `publish` job of `images.yml`. Every run pushes `run-<id>-<attempt>`, and only develop and master pushes add the SHA tag.
- **Admission probe:** `deploy/scripts/dev-cell.sh` `check_unsigned_image_refused`. The probe passes on any kubectl error, and its default image does not exist (see the follow-ups).
- **Gateway image:** `services/gateway/Dockerfile`. Two stages, pinned bases, runs as uid 10001 and not root, starts with `ENTRYPOINT swarm-gateway`.
- Operator isolation, Simulator isolation and identity: no service code is touched. No secret is in the code: GHCR uses `GITHUB_TOKEN` and signing is keyless OIDC.

## Assumptions accepted

- No FS, UC or BR named: accepted, the four technical sections settle the scope.
- Sprint anchor `#s02` as the ticket link: accepted, the rest of P0 does the same.
- No budget touched: accepted, there is no hot path.
- Admission by Sigstore policy-controller, enforced on `ghcr.io/gpbcom/swarm/**`, warn elsewhere: accepted as the conservative reading of 06-security#supply-chain for Swarm's own images.
- No screen touched: accepted, develop has no front end.

## Follow-ups

- Keep only T0.10's hunks of AGENT.md and the right lock file in the T0.10 commit. Hunk-level ownership of shared files is a harness gap.
- `test_every_service_has_a_dockerfile` will fail when missions, fleet or simulator merge without a Dockerfile: their tickets need one each.
- The dev-cell probe should use a real unsigned image and match the policy webhook in stderr.
- policy-controller needs pull credentials for the private GHCR signatures before the cell runs Swarm images.
- `test_images_workflow.py` has nested functions and raw strings, and `test_service_images.py` repeats the root path and the encoding.
- The Dockerfile's hand-listed workspace pyprojects must follow the gateway's dependencies.
- Move the Playwright specs to `frontends/<frontend>/e2e/` with the first front-end image.
