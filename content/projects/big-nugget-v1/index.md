---
title: "Big Nugget v1 - 5V 3.5A Power Supply"
date: 2018-01-30
cover:
  image: "big-nugget-v1-01.jpg"
  relative: true
---

{{< figure-gallery images="big-nugget-v1-01.jpg,big-nugget-v1-02.jpg" >}}

This is the first version of the Big Nugget. Version 2 improves considerably on this design. Compared to version 2, this
has a single cell battery, 2 USB type A outputs, and a different set of power management ICs.

The microUSB input can negotiate from 100mA to 3.25A with USB MaxCharge and High Voltage Adapters.

The Big Nugget v1 is based on the Texas Instruments [BQ25895](http://www.ti.com/lit/ds/symlink/bq25895.pdf "Texas
Instruments BQ25895 Datasheet") power management IC and the Microchip
[MIC2876](http://ww1.microchip.com/downloads/en/DeviceDoc/20005572A.pdf "Microchip MIC2876 Datasheet") boost IC.

Specs:

- 5VDC Output
- 3.5A Max continuous output
- Adjustable battery charge rate (5A max)
- 9V - 20V input
- 50μA sleep current

The board and design files are available at
[www.flashcandy.us/products/big-nugget-v1](https://flashcandy.us/products/big-nugget-v1)
