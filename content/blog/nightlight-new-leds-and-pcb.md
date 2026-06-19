---
title: "Swapping LEDs and PCB in a Dimmable Nightlight"
date: 2020-05-11
categories: ["Circuits", "DIY", "LED/Lighting", "tech"]
tags: ["1800K", "", "", "", "", ""]

cover:
  image: "/wp-content/uploads/2020/05/nightlight-01-1024x685.jpg"
  relative: false
  hidden: false
---
I've looked and been unsuccessful in finding household nightlights that meet my criteria:

  * auto on/off
  * dimmable
  * 1800K CCT
  * decent CRI
  * uniform illumination
  * no flickering
  * power efficient



The closest I found was [this nightlight](<https://www.amazon.com/gp/product/B078NH96RT/>).  I like everything about it except the 3000K CCT.  I believe it's a bit too cool for a nightlight.

![](/wp-content/uploads/2020/05/nightlight-01-1024x685.jpg)

I ended up swapping the 3000K LEDs for 2200K LEDs. I would have preferred 1800K, but was unable to source them on Digikey.

![](/wp-content/uploads/2020/05/nightlight-04-1024x685.jpg)

On the left is the original nightlight.  It has 4x 3V 3000K LEDs.  They are connected in series to a 12VDC power supply.

Overall, the nightlight and power supply are good quality.

However, the original LED PCB is very cheap. It was easier to build a new PCB that to desolder and resolder on the existing board. Anyways, I had to break the original PCB to remove it.

![](/wp-content/uploads/2020/05/nightlight-03-1024x685.jpg)

You can find my new PCB [here on OSHPark](<https://oshpark.com/shared_projects/cPf28g08>).  I bought [these LEDs](<https://www.digikey.com/product-detail/en/lumileds/L130-2280001400001/1416-2063-1-ND/10070628>) from Digikey and reflowed with hot air.

The original nightlight is shown on the left and the new nightlight on the right.

![](/wp-content/uploads/2020/05/nightlight-02-1024x685.jpg)

I'm quite happy with the results, especially with the minimal time required.
