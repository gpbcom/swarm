import createClient, { type Client, type ClientOptions } from "openapi-fetch";

import type { paths as FleetPaths } from "./generated/fleet.ts";
import type { components as GatewayComponents, paths as GatewayPaths } from "./generated/gateway.ts";
import type { paths as MissionsPaths } from "./generated/missions.ts";

export type { FleetPaths, GatewayComponents, GatewayPaths, MissionsPaths };
export type Problem = GatewayComponents["schemas"]["Problem"];

export function createGatewayClient(options?: ClientOptions): Client<GatewayPaths> {
  return createClient<GatewayPaths>(options);
}

export function createMissionsClient(options?: ClientOptions): Client<MissionsPaths> {
  return createClient<MissionsPaths>(options);
}

export function createFleetClient(options?: ClientOptions): Client<FleetPaths> {
  return createClient<FleetPaths>(options);
}
