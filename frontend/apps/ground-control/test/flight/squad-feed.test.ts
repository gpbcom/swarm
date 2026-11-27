import { describe, expect, it } from 'vitest';

import { LatencyHistogram } from '@swarm/live';

import { SquadFeed } from '../../src/flight/squad-feed';
import { FakeLiveClient, MISSION_ID, aSnapshot } from './fakes';

const URL = 'ws://127.0.0.1:8080/v1/live';

interface AFeed {
  feed: SquadFeed;
  client: FakeLiveClient;
  droneToScreen: LatencyHistogram;
  frameToPixels: LatencyHistogram;
}

function aFeed(): AFeed {
  const client = new FakeLiveClient();
  const droneToScreen = new LatencyHistogram();
  const frameToPixels = new LatencyHistogram();
  const feed = new SquadFeed(client, { droneToScreen, frameToPixels });
  return { feed, client, droneToScreen, frameToPixels };
}

describe('squad feed', () => {
  it('has no snapshot and no Drone before the first frame', () => {
    const { feed } = aFeed();
    expect(feed.current()).toBeNull();
    expect(feed.count).toBe(0);
  });

  it('connects the client to the url and the Mission on start', () => {
    const { feed, client } = aFeed();
    feed.start(URL, MISSION_ID);
    expect(client.connects).toEqual([{ url: URL, missionId: MISSION_ID }]);
  });

  it('keeps the latest snapshot and its count', () => {
    const { feed, client } = aFeed();
    feed.start(URL, MISSION_ID);
    const snapshot = aSnapshot(10);
    client.pushSnapshot(snapshot);
    expect(feed.current()).toBe(snapshot);
    expect(feed.count).toBe(10);
  });

  it('notifies its listeners of each snapshot', () => {
    const { feed, client } = aFeed();
    feed.start(URL, MISSION_ID);
    let notified = 0;
    feed.subscribe(() => {
      notified += 1;
    });
    client.pushSnapshot(aSnapshot(3));
    client.pushSnapshot(aSnapshot(4, 2_000_000, 1100, 2));
    expect(notified).toBe(2);
  });

  it('stops notifying a listener that unsubscribed', () => {
    const { feed, client } = aFeed();
    feed.start(URL, MISSION_ID);
    let notified = 0;
    const unsubscribe = feed.subscribe(() => {
      notified += 1;
    });
    unsubscribe();
    client.pushSnapshot(aSnapshot(3));
    expect(notified).toBe(0);
  });

  it('records the drone to screen latency of the updated slots only', () => {
    const { feed, client, droneToScreen } = aFeed();
    feed.start(URL, MISSION_ID);
    const snapshot = aSnapshot(4, 1_000_000, 1000);
    snapshot.updated[1] = 0;
    snapshot.updated[3] = 0;
    client.pushSnapshot(snapshot);
    feed.drawn(snapshot, 1040);
    expect(droneToScreen.count).toBe(2);
    expect(droneToScreen.sum).toBeCloseTo(80);
    expect(droneToScreen.min).toBeCloseTo(40);
    expect(droneToScreen.max).toBeCloseTo(40);
  });

  it('records the frame to pixels latency once per draw', () => {
    const { feed, client, frameToPixels } = aFeed();
    feed.start(URL, MISSION_ID);
    const snapshot = aSnapshot(10, 1_000_000, 1020);
    client.pushSnapshot(snapshot);
    feed.drawn(snapshot, 1060);
    expect(frameToPixels.count).toBe(1);
    expect(frameToPixels.sum).toBeCloseTo(40);
    feed.drawn(snapshot, 1080);
    expect(frameToPixels.count).toBe(2);
  });

  it('closes the client on stop', () => {
    const { feed, client } = aFeed();
    feed.start(URL, MISSION_ID);
    feed.stop();
    expect(client.closes).toBe(1);
  });
});
