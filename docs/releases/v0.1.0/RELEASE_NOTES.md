# 🚀 Swarm v0.1.0

**Released:** 2026-11-20 · **Commit:** `bfa5c8296dabcbec185aaa070e67b8e2a518e802` · **Since:** `8d6b9f0d5cd0082b065c61371dd6c4cb3ab00c6b`

> [!NOTE]
> 9 ticket(s) delivered, 197 change(s), tests: ✅ 2351 passed, ❌ 0 failed, ⏭️ 0 skipped.

## 🎫 Tickets delivered

| Ticket | Title | Features, use cases and business rules |
| --- | --- | --- |
| [T0.01](../../tickets/T0.01/EXPLAIN.md) | Mono-repo layout and Terraform base | ➖ |
| [T0.02](../../tickets/T0.02/EXPLAIN.md) | Claude Code ticket harness | ➖ |
| [T0.03](../../tickets/T0.03/EXPLAIN.md) | Convention tests and linters | ➖ |
| [T0.04](../../tickets/T0.04/EXPLAIN.md) | CI checks for every language | ➖ |
| [T0.05](../../tickets/T0.05/EXPLAIN.md) | Lifecycle and logging packages | ➖ |
| [T0.06](../../tickets/T0.06/EXPLAIN.md) | Shared models and generated types | ➖ |
| [T0.07](../../tickets/T0.07/EXPLAIN.md) | Rust core and benchmark gate | ➖ |
| [T0.08](../../tickets/T0.08/EXPLAIN.md) | Dev cell on k3s | ➖ |
| [T0.09](../../tickets/T0.09/EXPLAIN.md) | NATS JetStream and Operator accounts | 📏 BR-008: Operator isolation<br>📏 BR-014: Simulation isolation |

## 🧪 Tests

[🧪 Full test report](TEST_REPORT.md)

| Suite | ✅ Passed | ❌ Failed | ⏭️ Skipped | ⏱️ Time | Report |
| --- | --- | --- | --- | --- | --- |
| ✅ python-packages/packages | 1164 | 0 | 0 | 11.3 s | [packages.xml](tests/test-report-python-packages/packages.xml) |
| ✅ python-repository/repository | 1138 | 0 | 0 | 116.3 s | [repository.xml](tests/test-report-python-repository/repository.xml) |
| ✅ python-service-gateway/conventions-gateway | 7 | 0 | 0 | 0.3 s | [conventions-gateway.xml](tests/test-report-python-service-gateway/conventions-gateway.xml) |
| ✅ python-service-gateway/service-gateway | 11 | 0 | 0 | 0.6 s | [service-gateway.xml](tests/test-report-python-service-gateway/service-gateway.xml) |
| ✅ rust/rust-cargo-test | 30 | 0 | 0 | 0.0 s | [rust-cargo-test.log](tests/test-report-rust/rust-cargo-test.log) |
| ✅ specs/specs-check (specs.py check printed nothing) | 1 | 0 | 0 | 0.0 s | [specs-check.log](tests/test-report-specs/specs-check.log) |
| ✅ ts-packages-ts-config/packages-ts-config | 0 | 0 | 0 | 0.0 s | [packages-ts-config.log](tests/test-report-ts-packages-ts-config/packages-ts-config.log) |
| ✅ ts-packages-ts-live/packages-ts-live | 0 | 0 | 0 | 0.0 s | [packages-ts-live.log](tests/test-report-ts-packages-ts-live/packages-ts-live.log) |

## 📜 Changes

The [changelog](../../../CHANGELOG.md) lists every commit. By kind:

- 🎫 Tickets: 164
- 🧰 Harness: 17
- 📐 Specifications: 2
- 🚦 CI/CD and fixes: 7
- 📦 Other changes: 7
