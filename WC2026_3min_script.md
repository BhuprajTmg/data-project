# World Cup 2026 — 2.5-minute speaking script

Read at a calm ~150 words per minute. **Total ≈ 2 minutes 30 seconds.**
The same words are in PowerPoint **Presenter View** (Notes).

| Slide | Clock | Title |
|------:|:------|:------|
| 1 | 0:00–0:22 | Title |
| 2 | 0:22–0:48 | Data & method |
| 3 | 0:48–1:18 | Two non-results |
| 4 | 1:18–1:48 | Two significant findings |
| 5 | 1:48–2:18 | Two regressions |
| 6 | 2:18–2:30 | Close |

## Slide 1 — Title (0:00–0:22, ~48 words)

This is HIT 140 Assignment 2: World Cup 2026 analytics. Spain won the first 48-team tournament, 1–0 after extra time over Argentina. We analysed 104 matches, 48 national teams, and 1,016 players who featured. There are four inferential tasks and two pre-match linear models, all at alpha 0.05.

## Slide 2 — Data & method (0:22–0:48, ~75 words)

The data sits in three tables: matches, teams, and players. Player goals plus own goals reconcile to the official 308-goal total, and 15 red cards match FIFA. Each Objective 1 task follows the same six skills: question, wrangle, sample, describe, a 95 percent CI, and a t-test. Objective 2 predicts outcomes using only information knowable before kickoff — ranking, squad value, age, titles, host, rest, confederation, and knockout. No shots, no possession, no in-match events.

## Slide 3 — Two non-results (0:48–1:18, ~61 words)

Two questions came back non-significant. First: do midfielders pick up more yellows per appearance than defenders? In samples of 45, the means were 0.098 versus 0.131. p equals 0.45, Cohen’s d is tiny. We fail to reject. Second: do knockout crowds beat group-stage crowds? About two thousand extra fans, but p is 0.38. The expanded format drew large, comparable crowds throughout.

## Slide 4 — Two significant findings (1:18–1:48, ~65 words)

Two questions were significant. UEFA squads averaged 670 million euros against 257 million for everyone else — about 2.6 times as valuable. The one-sided t-test gives p of 0.004 and a large effect, d of 1.08. We reject. Goalkeepers averaged 30.3 years — well above the outfield prime of 27. The one-sample p is 0.0001, and they were also 3.6 years older than outfield teammates.

## Slide 5 — Two regressions (1:48–2:18, ~79 words)

Objective 2. Model 2.1 predicts match goal difference. Training R-squared is 0.49; on the hold-out it is 0.31. Only FIFA ranking gap and squad-value gap are significant. A billion-euro value edge is about plus 1.7 net goals. Model 2.2 predicts a team’s own goals. Fit is weaker, as expected for a noisy count: test R-squared 0.22. Significant drivers are opponent rank and own squad value. Residuals are slightly skewed, so a Poisson model would be a natural next step.

## Slide 6 — Close (2:18–2:30, ~36 words)

So: the midfield-booking story and the knockout-crowd premium are not in this data. Europe’s market-value gap is large, and keepers really do last longer. Before kickoff, ranking and squad value are the robust predictors. Thank you.

**Total spoken words:** 364  ·  **Pace:** ~145 words/minute.

If you over-run, drop the Poisson sentence on slide 5 and the Ochoa aside on slide 6.
