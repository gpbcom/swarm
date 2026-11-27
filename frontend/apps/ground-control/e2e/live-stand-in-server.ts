import { randomUUID } from "node:crypto";
import type { AddressInfo } from "node:net";

import { decode, encode } from "@msgpack/msgpack";
import { WebSocketServer } from "ws";
import type { RawData, WebSocket } from "ws";

import { DRONE_COUNT, SPEED_M_S, squadPosition } from "./squad-route.js";

const HOST = "127.0.0.1";
const TICK_MS = 50;
const ALTITUDE_M = 40;
const OP_FIELD = "op";
const SUBSCRIBE = "subscribe";
const AIRBORNE = "airborne";

export const DRONE_IDS: string[] = Array.from({ length: DRONE_COUNT }, () => randomUUID());

/** A stand-in for the live socket: records what it receives and streams 10 moving Drones once subscribed. */
export class LiveStandInServer {
  readonly received: Record<string, unknown>[] = [];
  private readonly server: WebSocketServer;
  private readonly missionId: string;
  private readonly timers: NodeJS.Timeout[] = [];
  private seq = 0;

  private constructor(server: WebSocketServer, missionId: string) {
    this.server = server;
    this.missionId = missionId;
    server.on("connection", (socket) => {
      this.attach(socket);
    });
  }

  static async start(missionId: string): Promise<LiveStandInServer> {
    const server = new WebSocketServer({ host: HOST, port: 0 });
    await new Promise<void>((resolve) => server.once("listening", resolve));
    return new LiveStandInServer(server, missionId);
  }

  get port(): number {
    return (this.server.address() as AddressInfo).port;
  }

  async stop(): Promise<void> {
    this.timers.forEach((timer) => {
      clearInterval(timer);
    });
    this.server.clients.forEach((client) => {
      client.terminate();
    });
    await new Promise<void>((resolve) => {
      this.server.close(() => {
        resolve();
      });
    });
  }

  private attach(socket: WebSocket): void {
    socket.on("message", (data: RawData) => {
      const message = decode(data as Buffer) as Record<string, unknown>;
      this.received.push(message);
      if (message[OP_FIELD] === SUBSCRIBE) {
        this.stream(socket);
      }
    });
  }

  private stream(socket: WebSocket): void {
    const started = Date.now();
    const timer = setInterval(() => {
      if (socket.readyState !== socket.OPEN) {
        return;
      }
      this.seq += 1;
      const nowUs = Date.now() * 1000;
      const elapsedS = (Date.now() - started) / 1000;
      const frames = DRONE_IDS.map((droneId, index) => ({
        mission_id: this.missionId,
        drone_id: droneId,
        seq: this.seq,
        t_us: nowUs,
        ...squadPosition(index, elapsedS),
        altitude_m: ALTITUDE_M,
        speed_m_s: SPEED_M_S,
        battery_pct: 90,
        link_quality_pct: 95,
        state: AIRBORNE,
      }));
      socket.send(encode({ mission_id: this.missionId, t_us: nowUs, frames }));
    }, TICK_MS);
    this.timers.push(timer);
  }
}
