---
title: "Big Nugget v2 - 5V 4A Power Supply"
date: 2019-06-21
cover:
  image: "big-nugget-v2-01.jpg"
  relative: true
---

{{< figure-gallery images="big-nugget-v2-01.jpg,big-nugget-v2-02.jpg,big-nugget-v2-03.jpg" >}}

The Big Nugget is best for high current projects needing long runtime from a battery source. It's great for Raspberry
Pi, BeagleBone, Arduino, IoT, and more.

It can power a Raspberry Pi drawing 1A for about 7 hours. An optional header allows you to connect larger batteries for
extended runtime.

The input can provide power to the output and charge the battery simultaneously. When the input power is removed, the
battery supplies power to the output.

I2C is available for checking battery capacity and voltage. It can also be used for adjusting settings such as max
charge rate and input current limit.

The Big Nugget v2 is based on the Texas Instruments [BQ25703A](http://www.ti.com/lit/ds/symlink/bq25703a.pdf "Texas
Instruments BQ25703A Datasheet") power management IC and the AOS
[AOZ2261](http://www.aosmd.com/res/data_sheets/AOZ2261QI-15.pdf "AOZ2261 IC Buck Regulator Datasheet") buck regulator.

Specs:

- 5VDC Output
- 4A Max continuous output
- Adjustable battery charge rate (5A max)
- 9V - 20V input
- 60μA sleep current
- Custom 4 cell BMS and balancing
- Optional headers for connecting larger batteries

More details are available at [www.flashcandy.us/products/big-nugget-v2](https://flashcandy.us/products/big-nugget-v2)
