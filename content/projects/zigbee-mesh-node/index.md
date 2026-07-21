---
title: "ZigBee Mesh Node"
date: 2016-09-12
cover:
  image: "zigbee-mesh-node-01.jpg"
  relative: true
---

{{< figure-gallery images="zigbee-mesh-node-01.jpg,zigbee-mesh-node-02.jpg,zigbee-mesh-node-03.jpg" >}}

This board is for a node within a mesh of ZigBee hubs, ideally for an Internet of Things application.

I used the Atmel [ATmega256RFR2](http://www.atmel.com/devices/atmega256rfr2.aspx), an ATmega with a RF front-end
designed for 2.4GHz communication. The main module is the Dresden Elektronik
[deRFmega256](https://www.dresden-elektronik.de/funktechnik/products/radio-modules/overview/?L=1). I chose this module
because of its low cost, antenna diversity, power amp, and FCC certification. The design is based on the Dresden
Elektronik FCC Compliant reference design.
