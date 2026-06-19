---
title: "Waterproof, Sound Proof Generator Enclosure"
date: 2021-08-14
categories: ["DIY", "embedded systems", "tech"]
tags: ["box", "", "", "", ""]

cover:
  image: "/wp-content/uploads/2021/08/generator-enclosure-14.jpg"
  relative: false
  hidden: false
---

{{< figure-gallery images="/wp-content/uploads/2021/08/generator-enclosure-01.jpg,/wp-content/uploads/2021/08/generator-enclosure-02.jpg,/wp-content/uploads/2021/08/generator-enclosure-03.jpg,/wp-content/uploads/2021/08/generator-enclosure-04.jpg,/wp-content/uploads/2021/08/generator-enclosure-05.jpg,/wp-content/uploads/2021/08/generator-enclosure-06.jpg,/wp-content/uploads/2021/08/generator-enclosure-07.jpg,/wp-content/uploads/2021/08/generator-enclosure-08.jpg,/wp-content/uploads/2021/08/generator-enclosure-09.jpg,/wp-content/uploads/2021/08/generator-enclosure-10.jpg,/wp-content/uploads/2021/08/generator-enclosure-11.jpg,/wp-content/uploads/2021/08/generator-enclosure-12.jpg,/wp-content/uploads/2021/08/generator-enclosure-13.jpg,/wp-content/uploads/2021/08/generator-enclosure-14.jpg,/wp-content/uploads/2021/08/generator-enclosure-15.jpg,/wp-content/uploads/2021/08/generator-enclosure-16.jpg,/wp-content/uploads/2021/08/generator-enclosure-17.jpg,/wp-content/uploads/2021/08/generator-enclosure-18.jpg,/wp-content/uploads/2021/08/generator-enclosure-19.jpg,/wp-content/uploads/2021/08/generator-enclosure-20.jpg" >}}

For RVs and vans, generators are very useful but very loud. I wanted an enclosure that is both waterproof and noise dampening. It's hard to find something like this, because it's not easy to encase an engine and keep it cool.

In the end, I failed to keep the generator cool enough to for more than 2 hours. 

I used a [Wen 56235i](<https://www.amazon.com/WEN-56235i-2350-Watt-Generator-Lightweight/dp/B085828BQ6>) generator. It is a cheaper variant of the Honda EU2200 series.

### Frame

The enclosure is made of a few layers:

  1. Frame of 1″ AL square tubing
  2. 1/16″ AL treadplate
  3. [Dynamat sound dampening](<https://www.amazon.com/gp/product/B0751CBXBT>)
  4. [Residential reflective insulation](<https://www.homedepot.com/p/Everbilt-48-in-x-25-ft-Double-Reflective-Insulation-48x25RI/315103268>)
  5. [Automotiv](<https://www.amazon.com/gp/product/B008NF84J8>)e sound dampening carpet liner



### Waterproofing

I used aluminum tread plate so the enclosure would be waterproof, lightweight, and not rust. 

[![](/wp-content/uploads/2021/08/generator-enclosure-14-1024x659.jpg)](</wp-content/uploads/2021/08/generator-enclosure-14.jpg>)_1 of the 3 baffles is cross-sectioned in the upper left_

The air inlet, air outlet, and exhaust outlet have a series of baffles to keep waterproof. They are covered with a screen to keep bugs out (not pictured)

### Extra Muffler

I added a 2″ tube to my generator's exhaust outlet, which originally had a 1/2″ outlet.

The generator's exhaust now connects to flexible steel tube, which then goes through my extra muffler. My extra muffler is a long, L-shaped tunnel surrounded in [SuperWool insulation](<https://www.lynnmfg.com/superwool/>) (like ceramic fiber insulation, but safer to breathe). I used spring wire to keep the insulation from caving in.

It significantly reduces the noise and didn't appear to restrict the exhaust flow.

### Secondary gas tank

[![](/wp-content/uploads/2021/08/generator-enclosure-01-1024x768.jpg)](</wp-content/uploads/2021/08/generator-enclosure-01.jpg>)

To get more runtime, I bought [this gas tank](<https://www.amazon.com/gp/product/B07TXBHK3D>). It is sold as a drop-in replacement for larger generators. It adds another 5 gallons in addition to the internal 0.75 gallon tank.

I ran the gas line into the generator's gas cap. It required some modification of the gas cap, but it works.

### Easy Access

[![](/wp-content/uploads/2021/08/generator-enclosure-02-1024x768.jpg)](</wp-content/uploads/2021/08/generator-enclosure-02.jpg>)

I used [this marine access](<https://www.amazon.com/gp/product/B00L4QMF2A>) panel for waterproof access to the inside. It is not supposed to be mounted vertically, so I added a small gutter above it. It is completely waterproof.

The top of the enclosure is secured by 4 latches. It is quick to remove.

### Roof-mountable

I added an additional mount to the bottom of the enclosure made of 5/8″ threaded rod and 1″ steel tubing. It bolts into my van's roof rack and is exceptionally strong.

### Exterior waterproof outlet

The outlet is a standard residential exterior waterproof outlet.

### Airflow

To get airflow inside the enclosure, I installed two [12V marine bilge fans](<https://www.amazon.com/gp/product/B0166S2PA2>). They are rated to move 270 CFM. One fan pulls air into the enclosure and the other fan pushes air out of the enclosure.

The inner lining of the ducts are lined in automotive carpet to dampen the noise of the fan.

I built a fan controller using a temperature based PID controller. This was done with an Arduino and a custom shield and OLED display. It worked great while testing, but there was too much EMI inside the enclosure while the generator was running. I improved it with some hardening of the circuit board, but I wasn't willing to put in anymore effort into the PID controller since the enclosure was overheating with the fans running at 100%.

### Performance

This enclosure was tremendously quiet. It measured about 50 dB from 6 feet away. Outside and 6 feet away, it was impossible to tell it was running (even at 100% output).

Furthermore, it was very waterproof and durable.

### Conclusion

Unfortunately, this enclosure was a total failure. Keeping the generator cool is tremendously difficult. Even with 2 fans, each helping push 270 CFM, the generator would get hot and get vapor lock, then die. Furthermore, the generator would occasionally shut off the 12V output powering the fans. I think that a resettable fuse was tripping.

I tried running with the lid cracked open, with the access panel cracked open, and with extra fans. It always overheated within 20 minutes to 2 hours of runtime, depending on ambient temperature and load.

Not adding an extra muffler may have helped. Using a higher quality (Honda) generator may have worked better than a cheaper (Wen) generator. 

Still, I would never try this again. It was expensive (a few hundred dollars) and I wasn't close to being able to maintain a reasonable temperature.
