---
title: TinyNF

description: |
  We present TinyNF, a new driver model for network cards aimed at non-TCP network functions, such as Ethernet bridges, load balancers, and IP routers. TinyNF allows network functions to process packets one by one, modifying each packet as needed before transmitting or dropping it. Unlike traditional drivers, as found in DPDK and other such frameworks, network functions cannot keep buffers around for later.

people:
  - solal-pirelli
  - george-candea

layout: project
last-updated: 2020-11-05
link: "https://dslab.epfl.ch/research/tinynf/"
# no-link: true
---

Network functions currently use network card drivers intended for general purpose use, even though many core network functions have a restricted model. General-purpose drivers are hard to verify, requiring tradeoffs between peformance and verifiability.

We present TinyNF, a new driver model for network cards aimed at non-TCP network functions, such as Ethernet bridges, load balancers, and IP routers. TinyNF allows network functions to process packets one by one, modifying each packet as needed before transmitting or dropping it. Unlike traditional drivers, as found in DPDK and other such frameworks, network functions cannot keep buffers around for later.

TinyNF not only improves the performance of network functions compared to a verified driver subset, with 160% more throughput on average, but also beats state-of-the-art drivers that are too complex to verify. In addition, network functions can be verified 8x faster with TinyNF compared to using a verified driver subset.
