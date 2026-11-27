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
import { useState } from "react";
import { useIntl } from "react-intl";
import type { ReactNode } from "react";

import {
  effectiveProvider,
  isValidEmail,
  type OperatorDraft,
} from "./entry-checks";

export interface PlannerDraft {
  name: string;
  email: string;
}

export interface FirstMissionPlannerStepProps {
  operator: OperatorDraft;
  planner: PlannerDraft;
  failed: boolean;
  /** The Identity provider already knows this e-mail address (409 with the name still free). */
  emailTaken: boolean;
  pending: boolean;
  onChange: (planner: PlannerDraft) => void;
  onBack: () => void;
  onSubmit: () => void;
}

/** A2 of UC-029: the first Mission planner, who is invited when the Operator is created. */
export function FirstMissionPlannerStep({
  operator,
  planner,
  failed,
  emailTaken,
  pending,
  onChange,
  onBack,
  onSubmit,
}: FirstMissionPlannerStepProps): ReactNode {
  const intl = useIntl();
  const text = (id: string, values?: Record<string, string>): string =>
    intl.formatMessage({ id }, values);
  const [emailChecked, setEmailChecked] = useState(false);
  const emailInvalid = emailChecked && !isValidEmail(planner.email);

  const submit = (): void => {
    setEmailChecked(true);
    if (isValidEmail(planner.email)) {
      onSubmit();
    }
  };

  const summary: [string, string][] = [
    ["name", operator.name.trim()],
    [
      "deployment",
      operator.deployment === null
        ? ""
        : text(`operators.create.deployment.${operator.deployment}`),
    ],
    [
      "jurisdictions",
      operator.jurisdictions
        .map((jurisdiction) =>
          text(`operators.create.jurisdiction.${jurisdiction}`),
        )
        .join(", "),
    ],
    [
      "llm_provider",
      text(`operators.create.llm_provider.${effectiveProvider(operator)}`),
    ],
    ["anchoring", text(`operators.create.anchoring.${operator.anchoring}`)],
  ];

  return (
    <>
      {failed || emailInvalid || emailTaken ? (
        <Banner kind="failure" icon={null}>
          {text("operators.create.error.banner")}
        </Banner>
      ) : null}
      <h1>
        {text("people.first_planner.title", { name: operator.name.trim() })}
      </h1>
      <Grid2>
        <Card>
          <Stack>
            <Field
              id="planner-name"
              label={text("people.first_planner.name")}
              value={planner.name}
              onChange={(event) => { onChange({ ...planner, name: event.target.value }); }
              }
            />
            <Field
              id="planner-email"
              label={text("people.first_planner.email")}
              type="email"
              value={planner.email}
              onChange={(event) => { onChange({ ...planner, email: event.target.value }); }
              }
              {...(emailInvalid
                ? { error: text("operators.create.error.email_required") }
                : emailTaken
                  ? {
                      error: text("operators.create.error.email_taken", {
                        email: planner.email.trim(),
                      }),
                    }
                  : {})}
            />
            <Field
              id="planner-role"
              label={text("people.first_planner.role")}
              value={text("people.first_planner.role.mission_planner")}
              hint={text("people.first_planner.role.hint")}
              readOnly
            />
          </Stack>
        </Card>
        <Card title={text("operators.create.summary.title")}>
          <Stack>
            {summary.map(([key, value]) => (
              <Row key={key}>
                {text(`operators.create.summary.${key}`)}
                <Spacer />
                <span>{value}</span>
              </Row>
            ))}
          </Stack>
        </Card>
      </Grid2>
      <Row>
        <Spacer />
        <Button variant="secondary" onClick={onBack}>
          {text("operators.create.back")}
        </Button>
        <Button variant="primary" onClick={submit} disabled={pending}>
          {text("operators.create.submit")}
        </Button>
      </Row>
    </>
  );
}
