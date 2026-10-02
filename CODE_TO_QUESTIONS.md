# How to explain the code in plain English

One Python file (`wc2026_analytics.py`) reads one Excel workbook (`fifa data.xlsx`) with three sheets:

- **matches** — 104 games (used for attendance)
- **teams** — 48 countries (used for squad value)
- **players** — 1,016 players who actually played (used for yellow cards and age)

The file then answers **four questions**. Each question has its own short piece of code. At the end it writes the HTML report you submitted.

If they ask you to walk through the program, say:

> First we clean the three tables. Then we answer four questions, one after another. For each question we pick a random sample, describe it, build a 95% confidence interval, and run a t-test. Alpha is 0.05 and the random seed is 42, so anyone who reruns the file gets the same sample.

Do not explain the regression part unless they ask. That is Objective 2.

---

## What happens before the four questions (cleaning)

The loading functions tidy the Excel sheets so the tests are fair.

- Country names are standardised. “United States” and “USA” become the same name, so a match row can join to a team row.
- Numbers are forced to be numbers (age, cards, attendance, market value).
- We only keep players who played at least once. Unused squad members are not in the study.
- Yellow cards per appearance is calculated as yellows divided by games played. That way a player who featured in seven matches is not compared unfairly with someone who played once.
- We check there really are 104 matches and 48 teams. If not, the script stops.

**Missing values, in one sentence:** the things we actually tested — cards, attendance, squad value, and age — had no gaps. Blank “group” on knockout matches and blank “penalty winner” when there were no penalties are normal blanks, not holes we filled in.

---

## Question 1 — yellow cards

**In English:** Do midfielders get booked more often, per game, than defenders?

**Null hypothesis:** on average, midfielders and defenders get the same number of yellows per appearance.  
**Alternative:** the two averages are different. (We allowed either side to be higher.)

**What the code does:**

1. Keep only midfielders and defenders.
2. Randomly pick 45 of each.
3. Compare their yellows-per-game.
4. First check whether the two groups are similarly spread out (Levene’s test). Then run a two-sample t-test.
5. Also give a 95% confidence interval for the midfielder average.
6. Draw two histograms.

**What you found:** midfielders 0.098, defenders 0.131. p-value about 0.45. We **do not reject** the null. The “midfielders get booked more” story is not in this sample. Most players have zero yellows, which is why the median is 0 — we are still testing the *average* rate.

**If they say “show me”:** the function is called `task1_discipline`.

---

## Question 2 — attendance

**In English:** Were knockout matches fuller than group-stage matches?

**Null hypothesis:** average crowd size is the same.  
**Alternative:** the averages are different.

**What the code does:**

1. Mark each match as group stage or knockout (Round of 32 through the Final).
2. There are only 32 knockout games, so we use **all of them**.
3. From the 72 group games we randomly pick 32, so both sides have the same sample size.
4. Compare attendance with a two-sample t-test (after Levene).
5. Give a 95% interval for overall mean attendance in that sample.
6. Draw a box plot.

**What you found:** about 65,700 (group) vs 67,700 (knockout). p-value about 0.38. We **do not reject** the null. Roughly two thousand extra fans is not a statistically clear gap.

**If they say “show me”:** the function is called `task2_attendance`.

---

## Question 3 — squad market value

**In English:** Are European (UEFA) squads worth more than the rest of the world?

**Null hypothesis:** average squad value is the same.  
**Alternative:** UEFA squads are **worth more** (only this direction — that is why this test is one-sided).

**What the code does:**

1. Split the 48 teams into UEFA (16) and everyone else (32).
2. Randomly pick 14 from each group.
3. Compare Transfermarkt squad values with a one-sided t-test.
4. Give a 95% interval for the UEFA average.
5. Draw a box plot.

**What you found:** about EUR 670 million vs 257 million. p-value about 0.004. We **reject** the null. UEFA squads were about two and a half times more valuable. This is also a *large* difference, not just a small p-value.

**If they say “why one-sided?”:** because the question we wrote was “higher”, not “different”. We decided that before looking at the sample. Even a two-sided test would still have been significant.

**If they say “show me”:** the function is called `task3_value`. Look for the line that says the test is “greater”.

---

## Question 4 — goalkeeper age

**In English:** Are goalkeepers who played at this World Cup older, on average, than 27?

**Null hypothesis:** mean goalkeeper age is 27.  
**Alternative:** it is not 27.

We also compared keepers with outfield players, as a check.

**What the code does:**

1. Separate goalkeepers from outfield players (defenders, midfielders, forwards).
2. Randomly pick 40 of each.
3. Run a one-sample t-test of keeper age against the number 27.
4. Run a second t-test of keepers versus outfield players. Their ages were not equally spread out, so we used the version of the t-test that does not assume equal spread (Welch).
5. Give a 95% interval for mean keeper age.
6. Draw a box plot with a dashed line at 27.

**What you found:** keepers averaged about 30.3 years. The interval is roughly 28.7 to 31.9, which does **not** include 27. p-value about 0.0001. We **reject** the null. They were also about 3.6 years older than outfield teammates.

**If they say “why 27?”:** it is a common “prime age” for outfield players, not an official FIFA number. That is why we also compared keepers with actual outfield players.

**If they say “show me”:** the function is called `task4_age`.

---

## Tiny glossary if they use the official words

| Their word | Your plain sentence |
|------------|---------------------|
| Null hypothesis | The boring default: “no real difference” (or “mean age is 27”). |
| Fail to reject | The sample is still compatible with that default. We did **not** prove the averages are equal. |
| Reject | The sample is too extreme for the default to be believable. |
| p-value | How often you would see a gap this big (or bigger) **if the null were true**. |
| 95% CI | A range for the unknown average. If we sampled many times, about 95% of such ranges would cover the true average. |
| t-test | The test we were asked to use to compare means when we do not know the population standard deviation. |
| Levene | A check: are the two groups similarly spread out? That chooses which flavour of t-test we use. |
| Seed 42 | The random draw is fixed so the marker can rerun it and get the same sample. |
| Alpha 0.05 | We are willing to be wrong 5% of the time if we reject a true null. |

---

## One-minute tour of the whole file

> The script loads three sheets and cleans names and types. Then four functions: yellow cards, attendance, UEFA value, keeper age. Each one samples, describes, builds a confidence interval, and runs a t-test. Two questions were not significant. UEFA value and keeper age were. Then it writes the HTML report.

If they open the code, start at `main` at the bottom. It calls the four task functions in that order.
