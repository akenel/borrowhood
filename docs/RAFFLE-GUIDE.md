# La Piazza Raffles -- The Complete Guide

**Raffle off anything. Support your community. No fees. No middlemen.**

A raffle on La Piazza works like a raffle at a school fair: someone puts up a prize, people buy tickets, and one lucky ticket wins. The only difference is that La Piazza handles the organization for you -- tickets, countdown, the draw, and notifying the winner. You handle the prize and the payment yourself, just like at the fair.

---

## How It Works (The 9-Step Version)

### If You're the Organizer

1. **List your prize.** Add photos, a description, and a story. What are you raffling? A painting? A basket of homemade jam? Old Lego sets?
2. **Set the ticket price.** How much per ticket? EUR 0.50? EUR 2? EUR 5? Keep it low -- the magic of a raffle is that everyone can afford to play.
3. **Set the rules.** How many tickets total? When does the draw happen? How many tickets can one person buy?
4. **Write payment instructions.** "Pay me EUR 2 cash at the bar" or "Send to my PayPal" or "Bring exact change to the garage sale." La Piazza doesn't touch your money.
5. **Publish.** Your raffle goes live. People can see it, share it, buy tickets.
6. **Confirm payments.** When someone pays you (cash, PayPal, bank transfer -- whatever you chose), you click "Confirm" next to their ticket. Now they're in the draw.
7. **Draw the winner.** When the time comes, click "Draw Winner." The system picks one ticket at random -- provably fair, verifiable by anyone.
8. **Deliver the prize.** Contact the winner, arrange pickup or shipping.
9. **Done.** Participants verify it was fair. You earn trust points. Next time, you can raffle something bigger.

### If You're Buying Tickets

1. **Find a raffle** you like on the Raffles page.
2. **Reserve tickets.** Pick how many (1, 2, 3...). You get 48 hours to pay.
3. **Pay the organizer** using their instructions (cash, PayPal, whatever they listed).
4. **Wait for confirmation.** The organizer marks your payment as received.
5. **Watch the countdown.** When the draw happens, you'll be notified.
6. **Win or lose gracefully.** If you win -- congratulations! If not -- you supported your community for the price of a coffee.
7. **Verify the raffle.** After the draw, tell everyone if it was fair. Your vote helps build trust.

---

## The Trust System

La Piazza doesn't let strangers raffle expensive things on day one. You earn the right to run bigger raffles by completing smaller ones honestly.

| Your Completed Raffles | Maximum Total Value |
|---|---|
| 0 (first time) | EUR 10 |
| 1 | EUR 20 |
| 2 | EUR 40 |
| 3 | EUR 80 |
| 4 | EUR 160 |
| 5+ | EUR 320 (hard ceiling) |

**"Completed" means:** you ran the raffle, drew the winner, delivered the prize, and your participants said it was fair. If people flag your raffle as unfair, it doesn't count toward your next tier.

**Why?** A scammer would have to run 5 honest raffles before they could even attempt anything worth stealing. The math doesn't work for them. It works for you.

---

## Points You Earn

Everyone who participates earns reputation points on the La Piazza leaderboard:

| Action | Points |
|---|---|
| Your ticket gets confirmed (buyer) | +3 |
| You win a raffle | +10 |
| You submit a verification (buyer) | +5 |
| You complete a raffle (organizer) | +25 |
| 80%+ of participants say "fair" (organizer bonus) | +15 |

---

## Community Verification

After every draw, every ticket holder gets asked:

> "Was this raffle fair? Did the winner receive the prize?"

You answer yes or no, and optionally leave a comment. This is how the community polices itself -- no moderator needed.

- **80%+ positive** = raffle counts as "completed cleanly" and the organizer earns a trust bonus
- **Below 80%** = raffle doesn't count toward the next trust tier
- **Multiple negative verifications** = organizer stays at their current tier until they rebuild trust

---

## Provably Fair Draw

When the organizer clicks "Draw Winner," the system does this:

1. Generates a random cryptographic seed (a long string of letters and numbers)
2. Lists every confirmed ticket in order
3. Combines the seed + the ticket list and runs it through SHA-256 (a math function that always gives the same answer for the same input)
4. The result determines the winning ticket number

**Why this matters:** After the draw, the seed is published. Anyone can take that seed, the ticket list, and run the same SHA-256 function. If they get the same winner, the draw was fair. If the organizer tried to cheat, the math wouldn't match. It's the same principle used in cryptocurrency and online poker.

---

## Frequently Asked Questions

### For Organizers

**Q: Does La Piazza take a cut of my raffle?**
A: No. Zero. Nothing. La Piazza doesn't touch your money at all. Payments happen directly between you and the ticket buyers.

**Q: What can I raffle?**
A: Anything legal. A painting, a cake, a weekend at your holiday house, old Lego sets, a guitar lesson, a basket of local wine. Be creative.

**Q: What if nobody buys tickets?**
A: You can cancel the raffle anytime before the draw. No tickets sold = nothing to refund.

**Q: What if someone buys a ticket but doesn't pay?**
A: Tickets are "reserved" for 48 hours. If you don't confirm their payment within that window, the ticket expires automatically and goes back into the pool.

**Q: What if I get sick and can't run the draw?**
A: If you don't take any action within 6 days after the draw date, the raffle auto-cancels and all ticket holders are notified. Nobody loses money because La Piazza never held it.

**Q: Can I set a minimum number of tickets before the draw?**
A: Not yet -- but you can always cancel if too few tickets sold. We're working on a minimum-threshold feature.

**Q: Do I need a license to run a raffle?**
A: That depends on your local laws. In Italy, raffles may fall under gaming regulations (ADM). In Switzerland, Canada, and the US, rules vary. La Piazza is a listing platform -- you are the organizer, and you are responsible for complying with your local laws. When you publish a raffle, you check a box confirming this.

### For Buyers

**Q: Is my money safe?**
A: La Piazza doesn't hold your money. You pay the organizer directly. If something goes wrong, contact the organizer. If they don't respond, flag the raffle and leave a negative verification.

**Q: What are my odds of winning?**
A: Simple math. If 50 tickets are sold and you bought 2, your odds are 2 in 50 (4%). The stats page shows exactly how many tickets are sold at all times.

**Q: Can the organizer rig the draw?**
A: No. The draw uses a provably fair system. After the draw, a cryptographic seed is published that anyone can use to verify the winner was chosen fairly. See "Provably Fair Draw" above.

**Q: What if I win but the organizer doesn't deliver?**
A: Leave a negative verification. This blocks the organizer from running bigger raffles in the future. Other community members will see the negative reviews before buying tickets from that organizer again.

**Q: Can I buy tickets for someone else?**
A: Not yet. Each ticket is tied to the account that reserved it.

### For Everyone

**Q: Is this gambling?**
A: La Piazza is a listing platform. We don't organize, operate, or profit from raffles. We provide the tools for community members to organize their own. Whether a specific raffle constitutes "gambling" depends on your local laws. Our maximum total value of EUR 320 keeps raffles at community scale -- a painting, a hamper, a weekend basket. Not cars. Not cash prizes.

**Q: What's the difference between a raffle and an auction?**
A: In an auction, the richest person wins. In a raffle, a EUR 2 ticket gives everyone the same chance. That's a completely different social dynamic -- more community-friendly, more democratic, more fun.

**Q: Why EUR 320 maximum?**
A: To keep raffles at community scale. A church raffle, a school fundraiser, a neighborhood garage sale prize. Not high-value items that attract fraud. As the platform grows and trust systems mature, this ceiling may increase.

**Q: What happens if I abandon a raffle?**
A: If you don't draw a winner within 6 days of the draw date, the raffle auto-cancels and all ticket holders are notified. You have 30 days to resolve the situation. After 30 days with no resolution, your badge tier drops (e.g., Trusted → Active) and you receive a profile warning. Two abandoned raffles with confirmed ticket holders = raffle privileges permanently suspended. This is serious. Don't start a raffle you can't finish.

---

## Examples

### Marco's Painting
Marco painted a watercolor of the Trapani salt flats. He raffles it off: 20 tickets at EUR 5 each (EUR 100 total). Sally buys 2 tickets, pays EUR 10 cash at the bar. Mike buys 3, sends EUR 15 via PayPal. On Saturday evening, Marco draws the winner. Sally's ticket #7 wins. She picks up the painting at Marco's workshop. Both verify: "Fair raffle, beautiful painting." Marco earns 40 points and unlocks the EUR 160 tier.

### Sofia's Cookie Box
Sofia bakes a box of 24 Christmas cookies. She's never run a raffle before, so her limit is EUR 10. She sets 10 tickets at EUR 1 each. Her school friends buy all 10 in one afternoon. She draws the winner in class. Everyone verifies. Sofia earns 25 points and can now raffle up to EUR 20 next time.

### Nicolò's Jiu-Jitsu Private Lesson
Nicolò offers a free 1-hour private BJJ lesson as the prize. Tickets are EUR 2 each, 25 tickets (EUR 50 total, well within his tier). The proceeds go to the local youth sports club. The winner gets trained by Nicolò. Everyone else got a EUR 2 donation receipt and a good story.

---

## Quick Reference

| | |
|---|---|
| **Minimum ticket price** | EUR 0.10 |
| **Maximum raffle value** | EUR 320 (scales with trust) |
| **Minimum duration** | 24 hours |
| **Maximum duration** | 30 days |
| **Ticket hold time** | 48 hours (configurable) |
| **Winner response time** | 72 hours |
| **Auto-cancel on inaction** | 6 days after draw date |
| **Verification threshold** | 80% positive = "clean" |
| **Platform fee** | EUR 0.00. Forever. |

---

*"Instead of buying lottery tickets and losing to a company, buy raffle tickets and support your community."*

*La Piazza -- Rent it. Learn it. Make it. Raffle it.*
