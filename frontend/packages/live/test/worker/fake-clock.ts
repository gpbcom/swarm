interface Timer {
  id: number;
  at: number;
  callback: () => void;
}

export class FakeClock {
  now = 0;
  private nextId = 1;
  private timers: Timer[] = [];

  nowMs(): number {
    return this.now;
  }

  setTimer(callback: () => void, delayMs: number): number {
    const id: number = this.nextId++;
    this.timers.push({ id, at: this.now + delayMs, callback });
    return id;
  }

  clearTimer(id: number): void {
    this.timers = this.timers.filter((timer: Timer) => timer.id !== id);
  }

  pending(): number {
    return this.timers.length;
  }

  advance(ms: number): void {
    const target: number = this.now + ms;
    for (;;) {
      const due: Timer[] = this.timers.filter((timer: Timer) => timer.at <= target);
      due.sort((a: Timer, b: Timer) => a.at - b.at || a.id - b.id);
      const first: Timer | undefined = due[0];
      if (!first) break;
      this.timers = this.timers.filter((timer: Timer) => timer.id !== first.id);
      this.now = Math.max(this.now, first.at);
      first.callback();
    }
    this.now = target;
  }
}
