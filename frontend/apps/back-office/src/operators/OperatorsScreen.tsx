import type { OperatorDirectoryEntry, OperatorEntry } from "@swarm/api-client";
import { Banner, Button, Row, Spacer, Toast, ToastProvider } from "@swarm/ui";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useIntl } from "react-intl";
import type { ReactNode } from "react";

import { useGateway } from "../api/GatewayProvider";
import {
  DEFAULT_DRAFT,
  checkEntry,
  effectiveProvider,
  sameName,
  hasErrors,
  type EntryErrors,
  type OperatorDraft,
} from "./entry-checks";
import {
  FirstMissionPlannerStep,
  type PlannerDraft,
} from "./FirstMissionPlannerStep";
import { OperatorEntryStep } from "./OperatorEntryStep";
import { OperatorsTable } from "./OperatorsTable";

export type OperatorsStep = "entry" | "planner" | "list";

export interface OperatorsScreenProps {
  onStepChange?: (step: OperatorsStep) => void;
}

const DIRECTORY_KEY = ["operators"];
const CONFLICT = 409;
interface CreateOutcome {
  status: number;
  nameListed: boolean;
}

const NO_PLANNER: PlannerDraft = { name: "", email: "" };

/** The directory of the Operators and the three steps that create one (UC-029). */
export function OperatorsScreen({
  onStepChange,
}: OperatorsScreenProps): ReactNode {
  const intl = useIntl();
  const client = useGateway();
  const queryClient = useQueryClient();
  const [step, setStep] = useState<OperatorsStep>("entry");
  const [draft, setDraft] = useState<OperatorDraft>(DEFAULT_DRAFT);
  const [planner, setPlanner] = useState<PlannerDraft>(NO_PLANNER);
  const [errors, setErrors] = useState<EntryErrors>({});
  const [failed, setFailed] = useState(false);
  const [emailTaken, setEmailTaken] = useState(false);
  const [createdName, setCreatedName] = useState<string | null>(null);
  const [invitedEmail, setInvitedEmail] = useState<string | null>(null);
  const [toastOpen, setToastOpen] = useState(false);

  const directory = useQuery({
    queryKey: DIRECTORY_KEY,
    queryFn: async (): Promise<OperatorDirectoryEntry[]> => {
      const { data } = await client.GET("/v1/operators");
      if (data === undefined) {
        throw new Error("The directory of the Operators could not be read.");
      }
      return data;
    },
  });
  const entries = directory.data ?? [];

  const goTo = (next: OperatorsStep): void => {
    setStep(next);
    onStepChange?.(next);
  };

  const create = useMutation({
    mutationFn: async (body: OperatorEntry): Promise<CreateOutcome> => {
      const { response } = await client.POST("/v1/operators", { body });
      if (response.status !== CONFLICT) {
        return { status: response.status, nameListed: false };
      }
      // A conflict is either the name or the planner's e-mail: the directory tells which.
      const { data } = await client.GET("/v1/operators");
      const listed = (data ?? []).some((entry) =>
        sameName(entry.operator.name, body.name ?? ""),
      );
      return { status: response.status, nameListed: listed };
    },
    onSuccess: async ({ status, nameListed }) => {
      if (status === CONFLICT && nameListed) {
        setErrors({ name: "name_taken" });
        setFailed(false);
        setEmailTaken(false);
        await queryClient.invalidateQueries({ queryKey: DIRECTORY_KEY });
        goTo("entry");
      } else if (status === CONFLICT) {
        setEmailTaken(true);
        setFailed(false);
        goTo("planner");
      } else if (status >= 200 && status < 300) {
        setCreatedName(draft.name.trim());
        setInvitedEmail(planner.email.trim());
        setToastOpen(true);
        setFailed(false);
        await queryClient.invalidateQueries({ queryKey: DIRECTORY_KEY });
        goTo("list");
      } else {
        setFailed(true);
      }
    },
    onError: () => { setFailed(true); },
  });

  const next = (): void => {
    const found = checkEntry(
      draft,
      entries.map((entry) => entry.operator.name),
    );
    setErrors(found);
    if (!hasErrors(found)) {
      goTo("planner");
    }
  };

  const submit = (): void => {
    setFailed(false);
    setEmailTaken(false);
    create.mutate({
      name: draft.name.trim(),
      deployment: draft.deployment,
      jurisdictions: [...draft.jurisdictions],
      llm_provider: effectiveProvider(draft),
      anchoring: draft.anchoring,
      first_mission_planner_name: planner.name.trim(),
      first_mission_planner_email: planner.email.trim(),
    });
  };

  const startAgain = (): void => {
    setDraft(DEFAULT_DRAFT);
    setPlanner(NO_PLANNER);
    setErrors({});
    setEmailTaken(false);
    setCreatedName(null);
    goTo("entry");
  };

  return (
    <ToastProvider>
      {step === "entry" ? (
        <OperatorEntryStep
          draft={draft}
          errors={errors}
          onChange={setDraft}
          onNext={next}
          onCancel={() => {
            setErrors({});
            goTo("list");
          }}
        />
      ) : null}
      {step === "planner" ? (
        <FirstMissionPlannerStep
          operator={draft}
          planner={planner}
          failed={failed}
          emailTaken={emailTaken}
          pending={create.isPending}
          onChange={setPlanner}
          onBack={() => { goTo("entry"); }}
          onSubmit={submit}
        />
      ) : null}
      {step === "list" ? (
        <>
          {createdName === null ? null : (
            <Banner kind="success" icon={null}>
              {intl.formatMessage(
                { id: "operators.list.created" },
                { name: createdName },
              )}
            </Banner>
          )}
          <h1>{intl.formatMessage({ id: "operators.list.title" })}</h1>
          <OperatorsTable entries={entries} />
          <Row>
            <Spacer />
            <Button variant="primary" onClick={startAgain}>
              {intl.formatMessage({ id: "operators.create.title" })}
            </Button>
          </Row>
        </>
      ) : null}
      {invitedEmail === null ? null : (
        <Toast
          kind="success"
          icon={null}
          message={intl.formatMessage(
            { id: "operators.list.invitation_sent" },
            { email: invitedEmail },
          )}
          open={toastOpen}
          onOpenChange={setToastOpen}
        />
      )}
    </ToastProvider>
  );
}
