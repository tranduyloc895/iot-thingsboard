"""Isolated demo fleet; reuse provisioning only, never run the 50-station loop."""
import argparse
import json
import math
import os
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
    parser.add_argument('--cycles', type=int, default=5)
    parser.add_argument('--interval', type=float, default=1)
    args = parser.parse_args()
    if not 1 <= args.devices <= 300 or args.cycles < 1 or args.interval < 0.1:
        parser.error('devices=1..300, cycles>=1, interval>=0.1 seconds')
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
                clients.append((name, client))
        if args.prepare:
            return 0
        print(f'READY {len(clients)} clients; all CONNACK OK', flush=True)

        def worker(name, client):
            try:
                for cycle in range(args.cycles):
                    gate.wait()
                    payload = {'ts': int(time.time() * 1000), 'values': {
                        'source': 'load-test', 'demo_device': name,
                        'demo_seq': cycle, 'demo_value': cycle % 100}}
                    started = time.monotonic()
                    info = client.publish('v1/devices/me/telemetry', json.dumps(payload), qos=1)
                    if info.rc != mqtt.MQTT_ERR_SUCCESS:
                        raise RuntimeError(f'publish rc={info.rc}')
                    info.wait_for_publish(timeout=10)
                    if not info.is_published():
                        raise TimeoutError('PUBACK timeout')
                    latencies.append((time.monotonic() - started) * 1000)
                    gate.wait()
            except threading.BrokenBarrierError:
                pass
            except Exception as exc:
                errors.append(f'{name}: {exc}')
                halt()

        threads = [threading.Thread(target=worker, args=item) for item in clients]
        for thread in threads:
            thread.start()
        try:
            for cycle in range(args.cycles):
                started = time.monotonic()
                gate.wait()  # Release every client for this wave.
                gate.wait()  # All PUBACKs before the next wave.
                print(f'WAVE {cycle + 1}: PUBACK cumulative={len(latencies)}', flush=True)
                if stop.wait(max(0, args.interval - (time.monotonic() - started))):
                    break
        except threading.BrokenBarrierError:
            halt()
        finally:
            for thread in threads:
                thread.join()
        expected = args.devices * args.cycles
        latencies.sort()
        print(f'Planned={expected} PUBACK={len(latencies)} '
              f'unconfirmed_or_unsent={expected - len(latencies)}', flush=True)
        if latencies:
            print(' '.join(f'p{p}={latencies[math.ceil(len(latencies)*p/100)-1]:.1f}ms'
                           for p in (50, 95, 99)), flush=True)
        for error in errors:
            print(error, flush=True)
        return 0 if len(latencies) == expected and not stop.is_set() else 1
    finally:
        for _, client in clients:
            client.disconnect()
            client.loop_stop()


if __name__ == '__main__':
    raise SystemExit(main())
