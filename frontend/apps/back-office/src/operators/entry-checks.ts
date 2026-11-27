import type { GatewayComponents } from "@swarm/api-client";

type Schemas = GatewayComponents["schemas"];

export type Deployment = Schemas["Deployment"];
export type Jurisdiction = Schemas["Jurisdiction"];
export type LlmProvider = Schemas["LlmProvider"];
export type Anchoring = Schemas["Anchoring"];

export const DEPLOYMENTS: readonly Deployment[] = ["cloud", "on_premises"];
export const JURISDICTIONS: readonly Jurisdiction[] = ["eu_easa", "us_faa"];
export const PROVIDERS: readonly LlmProvider[] = ["claude", "open_weight"];
export const ANCHORINGS: readonly Anchoring[] = [
  "qualified_timestamping",
  "public_blockchain",
  "none",
];

export interface OperatorDraft {
  name: string;
  deployment: Deployment | null;
  jurisdictions: readonly Jurisdiction[];
  /** `null` until the Swarm administrator picks one: the deployment then decides. */
  llmProvider: LlmProvider | null;
  anchoring: Anchoring;
}

/** The LLM provider chosen, or the default of the deployment: open-weight on premises, Claude in the cloud. */
export function effectiveProvider(draft: OperatorDraft): LlmProvider {
  if (draft.llmProvider !== null) {
    return draft.llmProvider;
  }
  return draft.deployment === "on_premises" ? "open_weight" : "claude";
}

export type NameError = "name_required" | "name_taken";

export interface EntryErrors {
  name?: NameError;
  deployment?: "deployment_required";
  jurisdictions?: "jurisdiction_required";
}

export const DEFAULT_DRAFT: OperatorDraft = {
  name: "",
  deployment: "cloud",
  jurisdictions: [],
  llmProvider: null,
  anchoring: "qualified_timestamping",
};

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

/** The same name, whatever its case and its surrounding spaces. */
export function sameName(first: string, second: string): boolean {
  return first.trim().toLowerCase() === second.trim().toLowerCase();
}

/** The errors of step 3 of UC-029: the required fields, and a name the directory already holds. */
export function checkEntry(
  draft: OperatorDraft,
  directoryNames: readonly string[],
): EntryErrors {
  const errors: EntryErrors = {};
  if (draft.name.trim() === "") {
    errors.name = "name_required";
  } else if (directoryNames.some((listed) => sameName(listed, draft.name))) {
    errors.name = "name_taken";
  }
  if (draft.deployment === null) {
    errors.deployment = "deployment_required";
  }
  if (draft.jurisdictions.length === 0) {
    errors.jurisdictions = "jurisdiction_required";
  }
  return errors;
}

export function hasErrors(errors: EntryErrors): boolean {
  return Object.keys(errors).length > 0;
}

/** Whether the first Mission planner's e-mail address is present and has the shape of an address. */
export function isValidEmail(email: string): boolean {
  return EMAIL_PATTERN.test(email.trim());
}
