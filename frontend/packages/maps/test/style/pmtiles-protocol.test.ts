import { beforeEach, describe, expect, it, vi } from "vitest";

interface Recorder {
  names: string[];
  addProtocol(name: string, loader: unknown): void;
}

function recorder(): Recorder {
  const names: string[] = [];
  return {
    names,
    addProtocol(name: string): void {
      names.push(name);
    },
  };
}

async function freshRegister(): Promise<(target: Recorder) => void> {
  vi.resetModules();
  const module = await import("../../src/style/pmtiles-protocol");
  return module.registerPmtilesProtocol;
}

describe("registerPmtilesProtocol", () => {
  beforeEach(() => {
    vi.resetModules();
  });

  it("registers the pmtiles protocol", async () => {
    const register = await freshRegister();
    const target = recorder();
    register(target);
    expect(target.names).toEqual(["pmtiles"]);
  });

  it("registers it once however many times it is called", async () => {
    const register = await freshRegister();
    const target = recorder();
    register(target);
    register(target);
    register(target);
    expect(target.names).toEqual(["pmtiles"]);
  });
});
