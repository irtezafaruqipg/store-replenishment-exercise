# Development Notes

## Time spent

I spent approximately **1 hour 20 minutes** on the exercise with AI assistance.
The breakdown below is estimated.

| Task | Estimated time |
| --- | ---: |
| Inspect and load the four CSVs | 10 min |
| Set up the validation checks and review the cleaned data | 20 min |
| Write and check the replenishment query and runner | 20 min |
| Build the note interpreter and try the prompt | 15 min |
| Run tests, review outputs, and document the solution | 15 min |
| **Total** | **80 min** |

## AI disclosure

I used Microsoft Copilot to help draft some functions and fill in repetitive
code after I had written the first example of a pattern. I also used AI
assistance to review the solution and manually tried the note prompt in
Microsoft Copilot Chat.

I tried the custom prompt editor in Microsoft Copilot Studio, but the editor
showed that the feature was disabled in my environment. I used predefined
model replies in the submitted interpreter, as allowed by the brief, and
tested the prompt separately in Copilot Chat. The submitted code runs without
a live model connection or an API key.

## How I checked the work

I read the code line by line and compared the outputs with the rules I wanted
to apply. I reconciled the starting and cleaned row counts and checked that
the validation summary explained the rows removed.

I worked through `STORE01 / PG001` by hand. Demand of 25 units minus 10 in
stock gives a shortfall of 15. With 12 units per case, I expected two cases,
or 24 units. I also checked that missing stock gives a blank recommendation
and that sufficient stock gives a zero order.

The replenishment test runs the same SQL file as the report. The note tests
check the response validator separately, including that it rejects malformed
replies and unexpected fields such as `order_units`.