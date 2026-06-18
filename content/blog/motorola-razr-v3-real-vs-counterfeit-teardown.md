---
title: "Motorola Razr V3: Real vs Counterfeit Teardown"
date: 2019-03-31
categories: ["Circuits", "embedded systems", "tech"]
tags: ["cell phone", "chinese", "circuit", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]
---

{{< figure-gallery images="/wp-content/uploads/2019/03/razr-real-fake-teardown-01.jpg,/wp-content/uploads/2019/03/razr-real-fake-teardown-02.jpg,/wp-content/uploads/2019/03/razr-real-fake-teardown-03.jpg,/wp-content/uploads/2019/03/razr-real-fake-teardown-04.jpg,/wp-content/uploads/2019/03/razr-real-fake-teardown-05.jpg,/wp-content/uploads/2019/03/razr-real-fake-teardown-06.jpg,/wp-content/uploads/2019/03/razr-real-fake-teardown-07.jpg,/wp-content/uploads/2019/03/razr-real-fake-teardown-08.jpg,/wp-content/uploads/2019/03/razr-real-fake-teardown-09.jpg,/wp-content/uploads/2019/03/razr-real-fake-teardown-10.jpg,/wp-content/uploads/2019/03/razr-real-fake-teardown-11.jpg,/wp-content/uploads/2019/03/razr-real-fake-teardown-12.jpg,/wp-content/uploads/2019/03/razr-real-fake-teardown-13.jpg,/wp-content/uploads/2019/03/razr-real-fake-teardown-14.jpg,/wp-content/uploads/2019/03/razr-real-fake-teardown-15.jpg,/wp-content/uploads/2019/03/razr-real-fake-teardown-16.jpg,/wp-content/uploads/2019/03/razr-real-fake-teardown-17.jpg,/wp-content/uploads/2019/03/razr-real-fake-teardown-18.jpg,/wp-content/uploads/2019/03/razr-real-fake-teardown-19.jpg,/wp-content/uploads/2019/03/razr-real-fake-teardown-20.jpg,/wp-content/uploads/2019/03/razr-real-fake-teardown-21.jpg,/wp-content/uploads/2019/03/razr-real-fake-teardown-22.jpg,/wp-content/uploads/2019/03/razr-real-fake-teardown-23.jpg,/wp-content/uploads/2019/03/razr-real-fake-teardown-24.jpg,/wp-content/uploads/2019/03/razr-real-fake-teardown-25.jpg,/wp-content/uploads/2019/03/razr-real-fake-teardown-26.jpg,/wp-content/uploads/2019/03/razr-real-fake-teardown-27.jpg,/wp-content/uploads/2019/03/razr-real-fake-teardown-28.jpg,/wp-content/uploads/2019/03/razr-real-fake-teardown-29.jpg,/wp-content/uploads/2019/03/razr-real-fake-teardown-30.jpg,/wp-content/uploads/2019/03/razr-real-fake-teardown-31.jpg,/wp-content/uploads/2019/03/razr-real-fake-teardown-32.jpg,/wp-content/uploads/2019/03/razr-real-fake-teardown-33.jpg,/wp-content/uploads/2019/03/razr-real-fake-teardown-34.jpg,/wp-content/uploads/2019/03/razr-real-fake-teardown-36.jpg,/wp-content/uploads/2019/03/razr-real-fake-teardown-37.jpg,/wp-content/uploads/2019/03/razr-real-fake-teardown-38.jpg,/wp-content/uploads/2019/03/razr-real-fake-teardown-39.jpg,/wp-content/uploads/2019/03/razr-real-fake-teardown-40.jpg,/wp-content/uploads/2019/03/razr-real-fake-teardown-41.jpg" >}}

![](/wp-content/uploads/2019/03/razr-real-fake-teardown-01-1024x685.jpg)Left- Authentic Razr V3, Right - Counterfeit Razr V3

I recently bought a Razr V3 on eBay. The listing below shows that it is made by Motorola. The pictures are of an authentic Razr. However I received a counterfeit Razr. 

PS - I wrote a [quick guide on spotting counterfeit Motorola Razr V3](<https://pcbisolation.com/blog/how-to-spot-a-counterfeit-motorola-razr-v3/>)'s (without disassembly). 

![](/wp-content/uploads/2019/03/razr-real-fake-teardown-34-1024x799.jpg)

If the phone would have worked, I wouldn't have cared. But it wouldn't get a signal with my SIM, so I complained and got a refund.

I decided to purchase an authentic Razr V3 to for a comparison teardown.   
The authentic black Razr is on the left. The counterfeit silver Razr is on the right. 

The most obvious error on the fake phone - the keyboard is the wrong color! It should be reflective silver, not black.

The display and UI looks very similar between the phones. I couldn't tell a difference. The counterfeit phone was significantly quicker than the real phone (we'll find out why, shortly). It's fun to look at an older mobile UX. I noticed a few interesting things. The camera is buried underneath two submenus, image filenames are shown when opening each image, and each SMS text is separate (texts aren't organized into conversations).

The counterfeit phone looks new from the outside, but contains a dirty (used) motherboard. This is odd. In the picture above, you can see wear marks from a grounding clip that was never installed. **It seems the counterfeit phone has a used motherboard?**

![](/wp-content/uploads/2019/03/razr-real-fake-teardown-13-1024x685.jpg)The clear plastic pieces in the center are the antennas

On the back of the board, the counterfeit phone's EMI shielding is rusting. Hm…

On the front of the motherboard:

Authentic (left) | Counterfeit (right)  
---|---  
  
  * Freescale SC29332VKP Baseband Processor
  * Intel 4050L0YBQ0 256 Mbit Flash and 64 Mbit SRAM
  * Murata LBMA1U4AU which contains:  
Broadcom BCM2035KWB Bluetooth 1.1/1.2 Controller
  * Freescale MC13777F Front End RF IC
  * SAWTEK 890036 RF Filter

| 

  * Freescale SC29343VKP Baseband Processor  
(this is a newer model than the authentic processor, hence why this phone seems faster)
  * ST M36L0R806 128Mbit Flash and 32 Mbit SRAM
  * Unlabeled package containing:  
Broadcom BCM2035KWB Bluetooth 1.1/1.2 Controller
  * RF Micro Devices RF6027 Front End RF IC

  
  
Authentic (left) | Counterfeit (right)  
---|---  
  
  * Motorola 5185941F02 PMIC and Audio
  * Skyworks SKY77501-14 GSM PMIC and Tx

| 

  * Freescale SC13890P23A PMIC and Audio
  * RF Micro Devices RF3178 GSM PMIC and Tx

  
  
Moving on to the display, there aren't many differences between the two. 

I suspect the camera module is made by the same manufacturer. 

The flexible keypad circuit are quite similar. 

![](/wp-content/uploads/2019/03/razr-real-fake-teardown-32-1024x685.jpg)

However, the difference in keypad cover's quality is outstanding when held up to the light.

![](/wp-content/uploads/2019/03/razr-real-fake-teardown-28-1024x685.jpg)

The frame and hinge mechanism are almost identical, albeit the counterfeit is made of more fragile plastic.

![](/wp-content/uploads/2019/03/razr-real-fake-teardown-33-1024x695.jpg)

I don't have closure on this yet - I can't decide if the counterfeit phone has an authentic motherboard or not. 

First, there are significant differences between the two motherboards. This could be a difference between the Russian and English variants, but I doubt it. It could also be differences between two revisions. Nowdays, a phone isn't likely to receive such a major internal overhaul and still be sold as the exact same model, but I'm not sure if that was true in 2004. 

Second, the counterfeit phone's motherboard is used. It has wear markings that indicate it was likely from an authentic Razr. I think it's more believable that a working phone's motherboard was refurbished, not a counterfeit's motherboard.

Either way, it's a testament to the Razr's popularity that counterfeits versions are still being sold today (15 years later, as of 2019). 
