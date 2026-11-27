import type { OperatorDirectoryEntry } from "@swarm/api-client";
import { Badge, Card, Table } from "@swarm/ui";
import { useIntl } from "react-intl";
import type { ReactNode } from "react";

export interface OperatorsTableProps {
  entries: readonly OperatorDirectoryEntry[];
}

const COLUMNS: readonly string[] = [
  "operator",
  "deployment",
  "jurisdictions",
  "anchoring",
  "cell",
  "state",
];

/** The directory of the Operators, one row each, with its cell. */
export function OperatorsTable({ entries }: OperatorsTableProps): ReactNode {
  const intl = useIntl();
  const text = (id: string): string => intl.formatMessage({ id });
  const rows = entries.map(({ operator, cell_assignment }) => [
    operator.name,
    text(`operators.create.deployment.${operator.deployment}`),
    operator.jurisdictions
      .map((jurisdiction) =>
        text(`operators.create.jurisdiction.${jurisdiction}`),
      )
      .join(", "),
    text(`operators.create.anchoring.${operator.anchoring}`),
    cell_assignment.cell,
    <Badge key="state" kind="success" icon="✅" label="" />,
  ]);
  return (
    <Card>
      <Table
        columns={COLUMNS.map((column) =>
          text(`operators.list.column.${column}`),
        )}
        rows={rows}
      />
    </Card>
  );
}
