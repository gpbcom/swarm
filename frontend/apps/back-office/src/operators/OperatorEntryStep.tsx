import {
  Banner,
  Button,
  Card,
  Field,
  Grid2,
  Row,
  Spacer,
  Stack,
} from "@swarm/ui";
import { useIntl } from "react-intl";
import type { ReactNode } from "react";

import {
  ANCHORINGS,
  DEPLOYMENTS,
  JURISDICTIONS,
  PROVIDERS,
  effectiveProvider,
  hasErrors,
  type Anchoring,
  type Deployment,
  type EntryErrors,
  type Jurisdiction,
  type LlmProvider,
  type OperatorDraft,
} from "./entry-checks";

export interface OperatorEntryStepProps {
  draft: OperatorDraft;
  errors: EntryErrors;
  onChange: (draft: OperatorDraft) => void;
  onNext: () => void;
  onCancel: () => void;
}

/** A1 of UC-029: the Operator's name, deployment, Jurisdictions, LLM provider and Anchoring. */
export function OperatorEntryStep({
  draft,
  errors,
  onChange,
  onNext,
  onCancel,
}: OperatorEntryStepProps): ReactNode {
  const intl = useIntl();
  const text = (id: string, values?: Record<string, string>): string =>
    intl.formatMessage({ id }, values);

  const nameError =
    errors.name === undefined
      ? undefined
      : text(`operators.create.error.${errors.name}`, {
          name: draft.name.trim(),
        });
  const toggle = (jurisdiction: Jurisdiction): void => {
    const next = draft.jurisdictions.includes(jurisdiction)
      ? draft.jurisdictions.filter((chosen) => chosen !== jurisdiction)
      : [...draft.jurisdictions, jurisdiction];
    onChange({ ...draft, jurisdictions: next });
  };

  return (
    <>
      {hasErrors(errors) ? (
        <Banner kind="failure" icon={null}>
          {text("operators.create.error.banner")}
        </Banner>
      ) : null}
      <h1>{text("operators.create.title")}</h1>
      <Grid2>
        <Card>
          <Stack>
            <Field
              id="operator-name"
              label={text("operators.create.name")}
              value={draft.name}
              onChange={(event) => { onChange({ ...draft, name: event.target.value }); }
              }
              {...(nameError === undefined ? {} : { error: nameError })}
            />
            <fieldset className="field">
              <legend>{text("operators.create.deployment")}</legend>
              <Row>
                {DEPLOYMENTS.map((deployment: Deployment) => (
                  <label key={deployment}>
                    <input
                      type="radio"
                      name="deployment"
                      checked={draft.deployment === deployment}
                      onChange={() => { onChange({ ...draft, deployment }); }}
                    />
                    {text(`operators.create.deployment.${deployment}`)}
                  </label>
                ))}
              </Row>
              {errors.deployment === undefined ? null : (
                <p className="error" role="alert">
                  {text(`operators.create.error.${errors.deployment}`)}
                </p>
              )}
            </fieldset>
            <fieldset className="field">
              <legend>{text("operators.create.jurisdictions")}</legend>
              <Row>
                {JURISDICTIONS.map((jurisdiction: Jurisdiction) => (
                  <label key={jurisdiction}>
                    <input
                      type="checkbox"
                      checked={draft.jurisdictions.includes(jurisdiction)}
                      onChange={() => { toggle(jurisdiction); }}
                    />
                    {text(`operators.create.jurisdiction.${jurisdiction}`)}
                  </label>
                ))}
              </Row>
              {errors.jurisdictions === undefined ? null : (
                <p className="error" role="alert">
                  {text(`operators.create.error.${errors.jurisdictions}`)}
                </p>
              )}
            </fieldset>
            <div className="field">
              <label htmlFor="operator-llm-provider">
                {text("operators.create.llm_provider")}
              </label>
              <select
                id="operator-llm-provider"
                className="input"
                value={effectiveProvider(draft)}
                aria-describedby="operator-llm-provider-hint"
                onChange={(event) => {
                  onChange({
                    ...draft,
                    llmProvider: event.target.value as LlmProvider,
                  });
                }}
              >
                {PROVIDERS.map((provider: LlmProvider) => (
                  <option key={provider} value={provider}>
                    {text(`operators.create.llm_provider.${provider}`)}
                  </option>
                ))}
              </select>
              <p id="operator-llm-provider-hint" className="hint">
                {text("operators.create.llm_provider.hint")}
              </p>
            </div>
          </Stack>
        </Card>
        <Card title={text("operators.create.anchoring")}>
          <Stack>
            {ANCHORINGS.map((anchoring: Anchoring) => (
              <Row key={anchoring}>
                <label>
                  <input
                    type="radio"
                    name="anchoring"
                    checked={draft.anchoring === anchoring}
                    onChange={() => { onChange({ ...draft, anchoring }); }}
                  />
                  {text(`operators.create.anchoring.${anchoring}`)}
                </label>
                <Spacer />
                {anchoring === "qualified_timestamping" ? (
                  <span className="muted">
                    {text("operators.create.anchoring.default")}
                  </span>
                ) : null}
              </Row>
            ))}
            <span className="hint">
              {text("operators.create.anchoring.hint")}
            </span>
          </Stack>
        </Card>
      </Grid2>
      <Row>
        <Spacer />
        <Button variant="secondary" onClick={onCancel}>
          {text("operators.create.cancel")}
        </Button>
        <Button variant="primary" onClick={onNext}>
          {text("operators.create.next")}
        </Button>
      </Row>
    </>
  );
}
