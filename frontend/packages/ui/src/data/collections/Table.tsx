import type { ReactNode } from "react";

export interface TableProps {
  columns: readonly ReactNode[];
  rows: readonly (readonly ReactNode[])[];
}

export function Table({ columns, rows }: TableProps) {
  return (
    <table className="table">
      <thead>
        <tr>
          {columns.map((column, index) => (
            <th key={index} scope="col">
              {column}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rows.map((row, rowIndex) => (
          <tr key={rowIndex}>
            {row.map((cell, cellIndex) => (
              <td key={cellIndex}>{cell}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
