---
title: "Octopart API Pricing Scheme"
date: 2019-06-06
categories: ["Circuits", "tech"]
tags: ["api", "automatic", "bom"]

cover:
  image: "octopart-api-pricing-thumbnail.jpg"
  relative: true
---
Octopart, the search engine for electronic and industrial parts, doesn't post the pricing for their [API](<https://octopart.com/api/home>) on their website. There's a bit of irony, since Octopart scrapes pricing from sites like Digikey, who also tries to [hide their pricing](<https://news.ycombinator.com/item?id=168735>).

The Octopart API is a great resource for pricing BOMs. [KiCost](<https://github.com/xesscorp/KiCost>) is a great example of tool that uses the Octopart API (although KiCost has [moved away from Octopart](<https://github.com/xesscorp/KiCost/issues/357#issuecomment-495579269>) due to the paywall).

As of June 2019, the Octopart API is as follows:

  * $25/month - up to 1,000 HTTP requests per month  

  * $50/month - up to 5,000 HTTP requests per month
  * $100/month - up to 12,000 HTTP requests per month
  * $200/month - up to 25,000 HTTP requests per month



$25/month is the minimum - you can't pay less. Octopart will happily sell you a custom plan if you need more than 25,000 requests per month.

Students (with a .edu email) can get 500 HTTP requests per month for free.
