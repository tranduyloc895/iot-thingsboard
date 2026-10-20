"""Isolated demo fleet; reuse provisioning only, never run the 50-station loop."""
import argparse
import json
import math
import os
import random
import signal
import threading
import time

os.environ['NODE_INDEX'] = '0'  # Required to import existing provisioning helpers.
import single_device_simulator as provision
import paho.mqtt.client as mqtt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--devices', type=int, default=150)
    parser.add_argument('--cycles', type=int, default=600, help='Number of cycles (0 for continuous)')
    parser.add_argument('--interval', type=float, default=1.0, help='Interval in seconds (default: 1.0)')
    args = parser.parse_args()
    if not 1 <= args.devices <= 300 or args.cycles < 0 or args.interval < 0.1:
        parser.error('devices=1..300, cycles>=0, interval>=0.1 seconds')
    if str(provision.STATE_DIR) != '/demo-state':
        parser.error('STATE_DIR must be /demo-state (dedicated demo volume)')
    clients = []
    latencies = []
    errors = []
    gate = threading.Barrier(args.devices + 1, timeout=30)
    stop = threading.Event()

    def halt(*_):
        stop.set()
        gate.abort()

    signal.signal(signal.SIGTERM, halt)
    signal.signal(signal.SIGINT, halt)

    def connect(name, token):
        client = mqtt.Client(client_id=name)
        client.username_pw_set(token)
        ready = threading.Event()
        result = []

        def on_connect(c, u, flags, rc):
            result.append(rc)
            ready.set()

        client.on_connect = on_connect
        client.connect_async(provision.THINGSBOARD_HOST, provision.PORT, 60)
        client.loop_start()
        if not ready.wait(15) or result[-1] != 0:
            client.disconnect()
            client.loop_stop()
            raise RuntimeError(f'{name}: no successful CONNACK; verify endpoint/token')
        return client

    try:
        for index in range(1, args.devices + 1):
            if stop.is_set():
                return 130
            name = f'DEMO-SURGE-{index:03d}'
            provision.DEVICE_NAME = name
            provision.TOKEN_FILE = provision.STATE_DIR / (name + '.json')
            token = provision.load_token()
            if not token and args.prepare:
                if not provision.PROVISION_KEY or not provision.PROVISION_SECRET:
                    raise RuntimeError('Missing provisioning credentials')
                token = provision.provision_device()
                if token:
                    provision.save_token(token)
            if not token:
                raise RuntimeError(f'{name}: run --prepare first; inspect provisioning logs')
            client = connect(name, token)
            if args.prepare:
                client.disconnect()
                client.loop_stop()
                print(f'PREPARED {name}: CONNACK OK', flush=True)
            else:
                clients.append((name, client, index))
        if args.prepare:
            return 0
        print(f'READY {len(clients)} clients; all CONNACK OK', flush=True)

        is_infinite = (args.cycles == 0)

        def worker(name, client, dev_idx):
            try:
                # Tọa độ phân bổ đều trên toàn địa bàn TP.HCM (Quận 1..12, Gò Vấp, Bình Thạnh, Tân Bình, Thủ Đức, Bình Tân, Nhà Bè...)
                lat = round(10.725 + ((dev_idx * 37) % 150) * (0.130 / 150) + random.uniform(-0.0003, 0.0003), 5)
                lon = round(106.615 + ((dev_idx * 59) % 150) * (0.160 / 150) + random.uniform(-0.0003, 0.0003), 5)
                base = 15.0 + (dev_idx % 4) * 15.0  # 15, 30, 45, 60 cm

                cycle = 0
                while not stop.is_set():
                    if not is_infinite and cycle >= args.cycles:
                        break
                    gate.wait()
                    # Mực nước dao động ngẫu nhiên vượt các ngưỡng màu:
                    # SAFE (<20cm - Cyan), ALERT (20-35cm - Vàng), WARNING (35-50cm - Cam), CRITICAL (>=50cm - Đỏ)
                    wave = 18.0 * math.sin(cycle * 0.9 + dev_idx)
                    jitter = (random.random() - 0.5) * 8.0
                    water_level = round(max(5.0, base + wave + jitter), 1)

                    if water_level >= 50.0:
                        status = "CRITICAL"
                    elif water_level >= 35.0:
                        status = "WARNING"
                    elif water_level >= 20.0:
                        status = "ALERT"
                    else:
                        status = "SAFE"

                    payload = {
                        'ts': int(time.time() * 1000),
                        'values': {
                            'source': 'simulator',
                            'device_id': name,
                            'device_name': f'Trạm di động #{dev_idx:03d} (TP.HCM)',
                            'demo_device': name,
                            'demo_seq': cycle,
                            'demo_value': cycle % 100,
                            'water_level_cm': water_level,
                            'rainfall_mm': round(15.0 + (cycle % 7) * 4.5 + random.uniform(0, 4), 1),
                            'temperature_c': round(29.0 + random.uniform(-1.0, 2.0), 1),
                            'latitude': lat,
                            'longitude': lon,
                            'status': status
                        }
                    }
                    started = time.monotonic()
                    info = client.publish('v1/devices/me/telemetry', json.dumps(payload), qos=1)
                    if info.rc != mqtt.MQTT_ERR_SUCCESS:
                        raise RuntimeError(f'publish rc={info.rc}')
                    info.wait_for_publish(timeout=10)
                    if not info.is_published():
                        raise TimeoutError('PUBACK timeout')
                    latencies.append((time.monotonic() - started) * 1000)
                    gate.wait()
                    cycle += 1
            except threading.BrokenBarrierError:
                pass
            except Exception as exc:
                errors.append(f'{name}: {exc}')
                halt()

        threads = [threading.Thread(target=worker, args=item) for item in clients]
        for thread in threads:
            thread.start()
        try:
            cycle = 0
            while not stop.is_set():
                if not is_infinite and cycle >= args.cycles:
                    break
                started = time.monotonic()
                gate.wait()  # Release every client for this wave.
                gate.wait()  # All PUBACKs before the next wave.
                if (cycle + 1) % 10 == 0 or cycle < 5:
                    print(f'WAVE {cycle + 1}: PUBACK cumulative={len(latencies)}', flush=True)
                cycle += 1
                if stop.wait(max(0, args.interval - (time.monotonic() - started))):
                    break
        except threading.BrokenBarrierError:
            halt()
        finally:
            for thread in threads:
                thread.join()
        expected = args.devices * (args.cycles if not is_infinite else cycle)
        latencies.sort()
        print(f'Planned={expected} PUBACK={len(latencies)} '
              f'unconfirmed_or_unsent={expected - len(latencies)}', flush=True)
        if latencies:
            print(' '.join(f'p{p}={latencies[math.ceil(len(latencies)*p/100)-1]:.1f}ms'
                           for p in (50, 95, 99)), flush=True)
        for error in errors:
            print(error, flush=True)
        return 0 if not stop.is_set() or len(latencies) > 0 else 1
    finally:
        for item in clients:
            client = item[1]
            client.disconnect()
            client.loop_stop()


if __name__ == '__main__':
    raise SystemExit(main())
