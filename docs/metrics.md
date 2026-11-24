# Metrics

The **Ship numeric history** action sends the numeric states of the entities a rule selects to one URL, in the InfluxDB line protocol. A VictoriaMetrics `/write` endpoint is a typical target.

## Turning it on

Nothing is sent until you do two things in Settings: set the **Metrics URL**, and turn on **Allow sending data off this instance**. There is no default URL. You set your own, and the permission cannot be turned on without one.

The action uses no credentials, so point it at an endpoint that only accepts posts from your own network.

PropSense checks the endpoint's TLS certificate and never relaxes that check. With an HTTPS URL, the certificate must be trusted by the machine Home Assistant runs on, for example one issued by your own certificate authority. If it is not, sends fail with a TLS error, and PropSense treats that like any other failed send.

## What a point looks like

```
homeassistant,area=Kitchen,device_class=temperature,domain=sensor,entity_id=sensor.kitchen_temp,unit_of_measurement=°C value=21.5 <timestamp in ns>
```

The area, device class and unit tags are optional.

## Limits and costs

- PropSense listens only to the state changes of the entities selected, never to every event.
- Each entity sends at most one point per interval (60 seconds by default, and the latest value wins). Points are posted in batches every 30 seconds.
- A rule may select at most 200 entities by default, and you can raise that to 1000. A wider rule is refused and a Repairs issue is raised.
- Only numeric states are sent. `unknown`, `unavailable` and text are skipped. On and off states are sent as 1 and 0 only if you turn that on.
- Locks, alarm panels and cameras are blocked by default.

## When the endpoint is down

Points wait in an in-memory buffer of 5000 and are retried every 30 seconds. When the buffer is full, the oldest points are dropped. The buffer is not saved, so a restart loses what had not been sent yet, which is at most one 30 second window plus any outage.

A dry run, or withdrawing the permission, discards the waiting points and sends nothing. The Status tab shows the target, the points sent, waiting and dropped, and the last error.
