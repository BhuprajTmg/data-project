# FIFA World Cup 2026 — 3-minute speaking script

Read this aloud. The same text is in PowerPoint **Presenter View** (notes under each slide).
About **522 words** — roughly **3 minutes** at a calm speaking pace (~150 words/minute).
Point at the chart when you say “on the right” or “the box plot”. If you overrun, skip the Ochoa sentence on slide 6.

---

## 0:00–0:20  ·  Slide 1 — Opening

Good morning. This is a three-minute briefing on World Cup 2026 — the first forty-eight-team tournament, won by Spain, one-nil after extra time against Argentina.

We asked four distinct statistical questions, each with a different focal point, and we built two linear models that try to predict the score using only information you could have known before kickoff.

## 0:20–0:40  ·  Slide 2 — Data and method

The data are real: one hundred and four matches, forty-eight teams, and one thousand and sixteen players who actually appeared.

Every Objective 1 task follows the same path: a question, a sample, descriptive statistics, a ninety-five percent confidence interval, and a t-test at alpha 0.05. Objective 2 then asks: if you only know ranking, squad value, age, host status and rest days before the match, how well can you predict the result?

## 0:40–1:05  ·  Slide 3 — Discipline

First: are midfielders booked more than defenders? People assume they are because they fight for the ball in midfield. We used yellow cards per appearance, so a seven-match finalist is not punished for playing more, and we sampled forty-five players from each position.

Look at the histogram — both groups pile up at zero. Means are 0.10 versus 0.13. p is 0.45, so we fail to reject the null. The “dirty midfield” story is not supported.

## 1:05–1:25  ·  Slide 4 — Attendance

Second: did knockouts draw bigger crowds? With forty-eight teams you might expect thin weekday group games. We compared all thirty-two knockout matches with a random sample of thirty-two group matches.

The box plots sit on top of each other: about sixty-eight thousand versus sixty-six thousand. p is 0.38. Not significant. This World Cup filled stadiums from match one.

## 1:25–1:45  ·  Slide 5 — Squad value

Third: money. Are UEFA squads worth more on Transfermarkt? Fourteen European teams against fourteen from the rest of the world.

The gap is large: six hundred and seventy million euros against two hundred and fifty-seven million — about two and a half times. p is 0.004, a large effect. Europe’s club market really does show up in national-team squads.

## 1:45–2:05  ·  Slide 6 — Goalkeeper age

Fourth: do goalkeepers last longer? We tested keepers who appeared against the usual outfield “prime” of twenty-seven, and against outfield teammates.

The dashed line on the chart is twenty-seven. The keeper box sits clearly above it, at 30.3 years. p is 0.0001. They are also about three and a half years older than outfield players. That longer shelf life is real.

## 2:05–2:45  ·  Slide 7 — Two regression models

Now the two models. Eight predictors each, all knowable before kickoff — no shots, no possession.

On the left, goal difference across one hundred and four matches. R-squared 0.49. Typical error about one and a half goals. What mattered: ranking gap and squad-value gap. Host, rest and age dropped out.

On the right, goals scored by a team, two hundred and eight rows. R-squared 0.29 — noisier, because one tally is harder than a difference. What mattered: opponent’s rank and own squad value. The scatter plots are the held-out tests: they follow the diagonal, with the noise you expect from football.

## 2:45–3:00  ·  Slide 8 — Close

Three takeaways. Crowds did not wait for knockouts. Europe’s money is a real gap. And before a match, rank and squad value — not rest days or host status — are what move the scoreline. Thank you.
