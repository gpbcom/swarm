import { BackOfficeFrame, SwarmAdministrationFrame } from "@swarm/ui";
import { LANGUAGE_NAMES, useLanguage } from "@swarm/i18n";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { useIntl } from "react-intl";
import type { ReactNode } from "react";

import { useGateway } from "./api/GatewayProvider";
import { useSession } from "./auth/SessionProvider";
import { isSwarmAdministrator } from "./auth/session";
import {
  OperatorsScreen,
  type OperatorsStep,
} from "./operators/OperatorsScreen";

const OPERATORS_ITEM = "operators";
const PEOPLE_ITEM = "people";

export function App(): ReactNode {
  const intl = useIntl();
  const { language } = useLanguage();
  const session = useSession();
  const client = useGateway();
  const [active, setActive] = useState(OPERATORS_ITEM);
  const administrator = isSwarmAdministrator(session);
  const operatorId = session.operatorId;

  const operator = useQuery({
    queryKey: ["operator", operatorId],
    enabled: !administrator && operatorId !== null,
    queryFn: async (): Promise<string> => {
      const { data } = await client.GET("/v1/operators/{operator_id}", {
        params: { path: { operator_id: operatorId ?? "" } },
      });
      if (data === undefined) {
        throw new Error("The Operator could not be read.");
      }
      return data.name;
    },
  });

  const statusItems = [
    intl.formatMessage(
      { id: "status.language" },
      { language: LANGUAGE_NAMES[language] },
    ),
  ];

  if (administrator) {
    const onStepChange = (step: OperatorsStep): void => {
      setActive(step === "planner" ? PEOPLE_ITEM : OPERATORS_ITEM);
    };
    return (
      <SwarmAdministrationFrame active={active} statusItems={statusItems}>
        <OperatorsScreen onStepChange={onStepChange} />
      </SwarmAdministrationFrame>
    );
  }
  return (
    <BackOfficeFrame
      statusItems={statusItems}
      {...(operator.data === undefined ? {} : { operatorName: operator.data })}
    />
  );
}
