---
title: "2\u00d715\u2033 Home Subwoofers, Car Amp, & Server Power Supply"
date: 2014-10-23
categories: ["Audio", "DIY"]
tags: ["amp", "audio", "box", "brutus", "car amp", "car subwoofer", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]

cover:
  image: "/wp-content/uploads/2014/10/hifonics03.jpg"
  relative: false
  hidden: false
---
After half a semester of college, I learned that my 8″, 40W woofer wasn't enough. I wanted something bigger, but didn't want to have to upgrade again in the future. So I decided on something reasonable for any 10'x15′ dorm room - two 15″ subwoofers powered by a 1000W car amp. My goals: keep it under $400, design it so one of the two subs can be placed in a car and be powered from a 12V source (like a car battery), and build them to be as durable as possible.

I chose the best subwoofers for the price I could find, Hifonic Brutus 15″s. They are terrific budget subs at $70/speaker. Once you know the environment and the speakers, you have everything begin designing the boxes.

 

 

[![hifonics03](/wp-content/uploads/2014/10/hifonics03.jpg)](</wp-content/uploads/2014/10/hifonics03.jpg>)

[![hifonics01](/wp-content/uploads/2014/10/hifonics01-1024x539.jpg)](</wp-content/uploads/2014/10/hifonics01.jpg>)




As with all home powered subwoofers, the power supply and amp should be integrated with the box. In an enclosure on the back of the box, I placed the amp. On the back of the other sub, I placed the power supplies. The design was not overly difficult. Most of the time was focused on structural integrity (1000W generates plenty of air pressure and vibrations), and placement of parts, such as connectors, voltage panels, and current panels.

[![](/wp-content/uploads/2015/07/hifonics02-1024x616.jpg)](</wp-content/uploads/2015/07/hifonics02.jpg>)

 

 

I bought two 3/4″ sheets of MDF, which is an excellent material for subwoofer boxes; MDF is incredibly uniform, airtight, and rigid. The front of the box is beefy. It has two layers of MDF, which is 1.5″ of solid wood.

 

[![](/wp-content/uploads/2015/07/hifonics04-1024x683.jpg)](</wp-content/uploads/2015/07/hifonics04.jpg>)

 

 

Each part of the box is wood glued and screwed together, then the edges are caulked. Two 14″ sections of 4″ diameter PVC are placed for ports. The inner edges on each end of the tubes are sanded, to prevent port chuffing.

[![](/wp-content/uploads/2015/07/hifonics05-1024x683.jpg)](</wp-content/uploads/2015/07/hifonics05.jpg>)

 

 

For a finished look, I covered the boxes in carpet and added corner covers. I meant to buy grey carpet, but I accidently bought black carpet.

Originally, I had 3 server PSUs to power the subwoofer. I was under the impression that these power supplies could run in parallel. Each power supply outputs 28 amps at 12V, which is 3 x 342W or 1026W. Unfortunately, they do not run in parallel gracefully. If one of the units is putting out 11.9V while another is outputting 12.1V, then large amounts of current will flow from the 12.1V source to the 11.9V source, which can damage many components, including the voltage correction circuitry. Two of the supplies failed after a few hours of use. I was down to 342W, which was enough for dormies to hear a floor above and below, but wasn't enough for me.

[![](/wp-content/uploads/2015/07/hifonics06-1024x683.jpg)](</wp-content/uploads/2015/07/hifonics06.jpg>)

 

 

There exists a power supply for large servers that only outputs 12V. They usually come in redundant pairs, and the one I found on eBay, supplies 106A. This 1300W device is a little bigger than a standard ATX PSU, and can be bought used for $15-$20. They are very popular in the RC community for their ability to charge numerous Lithium batteries quickly.

[![hifonics08](/wp-content/uploads/2015/07/hifonics08-1024x683.jpg)](</wp-content/uploads/2015/07/hifonics08.jpg>)

 

There is a downside to taking advantage of the inexpensive amplifiers and speakers from the car audio market, getting 12V to your amp. Any large power supply will probably be from a server, where noise is secondary to reliability. Therefore, the fans on this baby are loud as possible. You could use this thing as a leafblower. Or attach wings to it and it may take flight.

You have two options here:

-Slow down the fan (slightly) with a high power resistor and tolerate the noise. I did this for a year and a half.

-Make a circuit that measures the temperature and controls the fan speed at reasonable volumes

[![hifonics09](/wp-content/uploads/2015/07/hifonics09-1024x683.jpg)](</wp-content/uploads/2015/07/hifonics09.jpg>)

 

 

 

The second option is more technical. Again, you have 2 options:

-Drive the fan with PWM using a 555 timer. The duty time is determined by the temperature sensor and discrete components.

-Drive the fan with PWM using a microcontroller. The duty time is determined by the temperature sensor and your code.

 

I chose the second option for a few reasons. First, I can adjust the behavior of the fan easily; I can change the minimum temperature for the fan starting and how the fan speed scales with temperature. Second, I can generate a second output. If I control the internal fans with my circuit, the PSU doesn't get the right feedback signal from the fans, shutting off the PSU. I created a faux fan feedback signal (a 2kHz square wave) and feed it back to the PSU.

In summary, I use a microcontroller to control the fans to my liking. And I trick the PSU into thinking it controls the fans. Everybody wins.

 

[![hifonics11](/wp-content/uploads/2015/07/hifonics11-1024x683.jpg)](</wp-content/uploads/2015/07/hifonics11.jpg>)

 

 

This is a TMA 1000.1 mono subwoofer car amp. As far as non-name brand amplifiers go, this one is terrific. It's output (1000W RMS) isn't exaggerated, and it doesn't noticeably distort at high volumes, near the maximum of my power supply.

 

[![hifonics10](/wp-content/uploads/2015/07/hifonics10-1024x683.jpg)](</wp-content/uploads/2015/07/hifonics10.jpg>)

 

Fully assembled, this is what the subwoofers look like. Each box is 22″x25″x18″ and require two people to move. It cost under $400 for both. To buy something like this new, I would easily have spend over $1500. They are loud, probably unnecessarily loud. But that's not the point, they are a result of my favorite process: imagining and implementing. Plus they're fun to use.

[![hifonics07](/wp-content/uploads/2015/07/hifonics07-1024x683.jpg)](</wp-content/uploads/2015/07/hifonics07.jpg>)

 
