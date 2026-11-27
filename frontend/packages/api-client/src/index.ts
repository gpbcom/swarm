import createClient, { type Client, type ClientOptions } from "openapi-fetch";

import type { paths as FleetPaths } from "./generated/fleet.ts";
import type { components as GatewayComponents, paths as GatewayPaths } from "./generated/gateway.ts";
import type { paths as MissionsPaths } from "./generated/missions.ts";
import type { paths as SimulatorPaths } from "./generated/simulator.ts";

export type { FleetPaths, GatewayComponents, GatewayPaths, MissionsPaths, SimulatorPaths };
export type Problem = GatewayComponents["schemas"]["Problem"];
export type Operator = GatewayComponents["schemas"]["Operator"];
export type OperatorEntry = GatewayComponents["schemas"]["OperatorEntry"];
export type OperatorDirectoryEntry = GatewayComponents["schemas"]["OperatorDirectoryEntry"];
export type OperatorCreated = GatewayComponents["schemas"]["OperatorCreated"];
export type CellAssignment = GatewayComponents["schemas"]["CellAssignment"];
export type Person = GatewayComponents["schemas"]["Person"];

export function createGatewayClient(options?: ClientOptions): Client<GatewayPaths> {
  return createClient<GatewayPaths>(options);
}

export function createMissionsClient(options?: ClientOptions): Client<MissionsPaths> {
  return createClient<MissionsPaths>(options);
}

export function createFleetClient(options?: ClientOptions): Client<FleetPaths> {
  return createClient<FleetPaths>(options);
}

export function createSimulatorClient(options?: ClientOptions): Client<SimulatorPaths> {
  return createClient<SimulatorPaths>(options);
}
