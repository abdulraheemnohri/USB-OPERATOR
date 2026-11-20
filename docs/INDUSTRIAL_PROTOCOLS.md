# Industrial protocol foundations (read-only)

This milestone adds standalone, testable protocol primitives; it does not connect them to automatic discovery or the live command API.

## Modbus TCP
Only function codes 03 (read holding registers) and 04 (read input registers) are exposed. Unit ID, port, address and count are range-checked; count is capped at 125. MBAP transaction ID, protocol ID, length, unit ID, function code and byte count are verified. Malformed and exception responses fail closed.

## Modbus RTU
Helpers construct only FC03/FC04 requests and verify CRC16, unit ID, function code and byte count. A physical serial bus driver, arbitration, termination/biasing configuration and tested timeout/retry policy are still required before field integration.

## SCPI
The serial helper accepts only an explicit allowlist of measurement/identity queries. Arbitrary SCPI strings, writes, reset, output enable and remote configuration commands are rejected.

## Commissioning requirements
Verify device register maps, scaling, signedness, byte/word order, isolation, RS-485 bias/termination, grounding and manufacturer limits. Test against simulators and isolated bench equipment first. Do not use these primitives in safety-critical control loops. Hardware-in-the-loop tests and independent protective relays/interlocks remain mandatory.
