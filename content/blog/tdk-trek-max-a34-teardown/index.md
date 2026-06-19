---
title: "TDK Trek Max A34 Teardown"
date: 2017-04-04
categories: ["Audio"]
tags: ["bluetooth", "broken", "charging", "connection"]

cover:
  image: "TDK_Trek_A34_1.jpg"
  relative: true
---
![](TDK_Trek_A34_1.jpg)

This is a great bluetooth speaker - loud, good sound quality, waterproof, and durable. Yet sometimes it has bluetooth problems, playback problems, and doesn't work when in motion (like in a backpack).

I opened this up to look for issues. I found none. Note that you are removing glued pieces and may lose some waterproofing. Mine still seems very water resistant, but I wouldn't dunk it in a lake.

 

 

![](TDK_Trek_A34_2.jpg)

Start by removing 11 screws from the bottom. 4 of those screws are hidden under the rubber feet. You can get to them by only partially lifting up the feet. The bottom battery cover pry up with a plastic tool.

 

 

![](TDK_Trek_A34_3.jpg)

The battery is revealed. It's a 7.2V 2300mAh Ni-MH. Remove the battery. If you are just replacing the battery, you're done here.

 

![](TDK_Trek_A34_4.jpg)

Remove the four screws underneath the battery.

 

 

![](TDK_Trek_A34_5.jpg)

Cut and pry away the glue sealing the hole for the connector. You can use hot glue during reassembly.

Now the entire bottom plastic can be removed. Pull from one side. It's glued down, but should remove without excessive force.

 

 

![](TDK_Trek_A34_6.jpg)

Use a flat edge or plastic tool to get under the edge of the rubber top.

 

 

![](TDK_Trek_A34_7.jpg)

Once you get under it, slowly peel it up. If you peel carefully, the glue will stay intact and is reusable for reassembly.

 

 

![](TDK_Trek_A34_8.jpg)

On the top of the speaker, there's 10 screws. Once the screws are out, pull up firmly on one side of the top plastic. It should remove similar to the bottom plastic. The above picture is after the top plastic is removed.

 

 

![](TDK_Trek_A34_10.jpg)

 

Using a small flathead, get under the outside edge of the rear speaker grills.

 

 

![](TDK_Trek_A34_9-1024x685.jpg)

Pull up and out. The grill will slip over a lip and be free. It has a small amount of glue, so wiggle it off. You may bend the edge of the grill, but it can be easily bent back into shape before reassembly.

 

 

![](TDK_Trek_A34_11.jpg)

Remove the 8 screws on the back.

 

 

![](TDK_Trek_A34_12.jpg)

The case should now split in half.

 

 

![](TDK_Trek_A34_13.jpg)

And we're in like Flynn! To get the board out, you'd have to remove a lot of glue. I didn't bother with this.

Interesting to note the 8-pin programming head hidden under the rubber foot in the upper left corner.

 

 

![](TDK_Trek_A34_14.jpg)

![](TDK_Trek_A34_15.jpg)

Notable components:

Main chip is a [STM32](<https://en.wikipedia.org/wiki/STM32>) microcontroller.

Power amp is Texas Instruments [TAS5711](<http://www.ti.com/lit/ds/symlink/tas5711.pdf>).

Bluetooth is a prebuilt FCC certified module - [CSR BC05](<https://www.bluetooth.org/tpg/RefNotes/RIN15.pdf>) from Taiwick Limited.

 

 

![](TDK_Trek_A34_17.jpg)

Upon reassembly, I added some extra adhesive to the top. It's the adhesive used for repairing phone screens.

 

 

![](TDK_Trek_A34_16.jpg)

 
