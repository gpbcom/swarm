//! Benchmarks of the `MAVLink` 2 decoder and of the latest-frame store.

use std::hint::black_box;

use criterion::{criterion_group, criterion_main, Criterion};
use swarm_core_mavlink::{decode, LatestFrames};

const CRC_INIT: u16 = 0xFFFF;

fn crc16(bytes: &[u8]) -> u16 {
    let mut crc = CRC_INIT;
    for byte in bytes {
        let mut tmp = *byte ^ crc.to_le_bytes()[0];
        tmp ^= tmp << 4;
        let wide = u16::from(tmp);
        crc = (crc >> 8) ^ (wide << 8) ^ (wide << 3) ^ (wide >> 4);
    }
    crc
}

fn frame(sequence: u8, system_id: u8, message_id: u8, extra: u8, payload: &[u8]) -> Vec<u8> {
    let length = u8::try_from(payload.len()).expect("payload fits one byte");
    let mut bytes = vec![0xFD, length, 0, 0, sequence, system_id, 1, message_id, 0, 0];
    bytes.extend_from_slice(payload);
    let mut covered = bytes[1..].to_vec();
    covered.push(extra);
    bytes.extend_from_slice(&crc16(&covered).to_le_bytes());
    bytes
}

fn datagram(sequence: u8, system_id: u8) -> Vec<u8> {
    let mut bytes = frame(sequence, system_id, 0, 50, &[0, 0, 0, 0, 2, 3, 0x81, 4, 3]);
    let mut battery = vec![0_u8; 30];
    battery.push(80);
    bytes.extend(frame(sequence, system_id, 1, 124, &battery));
    let mut position = Vec::new();
    for value in [123_456_i32, 473_977_420, -85_455_940, 510_000, 12_500] {
        position.extend_from_slice(&value.to_le_bytes());
    }
    position.extend_from_slice(&[150, 0, 181, 255, 10, 0, 0x78, 0x69]);
    bytes.extend(frame(sequence, system_id, 33, 104, &position));
    bytes
}

fn bench(c: &mut Criterion) {
    let one = datagram(1, 1);
    c.bench_function("mavlink_decode_three_messages", |b| b.iter(|| decode(black_box(&one))));

    let mut sequence = 0_u8;
    let datagrams: Vec<Vec<u8>> = (0..500_u16)
        .map(|drone| {
            sequence = sequence.wrapping_add(1);
            datagram(
                sequence,
                u8::try_from(drone % 255 + 1).expect("system id fits one byte"),
            )
        })
        .collect();
    let mut store = LatestFrames::new();
    c.bench_function("mavlink_ingest_500_drones", |b| {
        b.iter(|| {
            for datagram in &datagrams {
                store.ingest(black_box(datagram), 1_000);
            }
        });
    });
}

criterion_group!(benches, bench);
criterion_main!(benches);
