# Objective 1 theory drill

Yakub will not ask you to recite means. He will ask **what a p-value is**, **what a CI means**, **why a t-test is allowed when the histogram is skewed**, and **why you sampled**. Practise these out loud. After each answer, add one sentence that points at **your** task.

Do not study regressions.

---

## 0. The map (say this if he asks “what did Objective 1 actually do?”)

Inferential statistics: use a **sample statistic** to say something about a **population parameter**, with a stated error rate.

For each of four questions we estimated a mean (or a difference of means), built a **95% CI**, and ran a **t-test** at **α = 0.05**.

| | Population parameter | Sample statistic |
|--|----------------------|------------------|
| Task 1 | μ_MF − μ_DF (cards/app) | x̄_MF − x̄_DF |
| Task 2 | μ_KO − μ_group (attendance) | x̄_KO − x̄_group |
| Task 3 | μ_UEFA − μ_non (EUR m) | x̄_UEFA − x̄_non |
| Task 4 | μ_GK (years) | x̄_GK |

---

## 1. Descriptive vs inferential

**Q. What is the difference?**

Descriptive statistics **summarise the numbers you have** (mean, SD, median, charts). Inferential statistics **generalise to a population** and attach uncertainty (CI, p-value, decision at α).

*In our project:* the table of sample means is descriptive. “Fail to reject H₀ at α = 0.05” is inferential.

**Q. Why not just describe the full 104 matches / 48 teams / 1,016 players?**

That would be a **census** of the compiled tournament. The brief required **sampling**, a CI, and a t-test — those are inferential tools. A census has no sampling error, so a p-value against “the rest of this same tournament” would not mean the same thing.

---

## 2. Population, sample, parameter, statistic

**Q. Define population and sample.**

The **population** is the full set we want to talk about. The **sample** is the random subset we actually measure.

*Ours:* Task 1 population = 319 MF and 345 DF who appeared; sample n = 45 each. Task 3 population = 16 UEFA and 32 non-UEFA squads; sample n = 14 each.

**Q. Parameter vs statistic?**

A **parameter** is a number about the population (μ, σ). A **statistic** is a number about the sample (x̄, s). We use statistics because parameters are unknown.

**Q. What is sampling error?**

The natural gap between x̄ and μ because you did not see everyone. It is not a mistake. **SE = s / √n** estimates how large that wobble is.

**Q. What is bias?**

A systematic miss — the sample is unrepresentative (convenience sample, only star players, only sold-out venues). Random sampling is how we aim for **unbiasedness**. Seed 42 does not remove bias; it only makes the random draw **reproducible**.

---

## 3. Sampling methods

**Q. What sampling method did you use?**

**Simple random sampling without replacement**, seed 42, **equal allocation** in each group. Task 2 is **stratified** by stage: knockout vs group.

**Q. What does SRS mean?**

Every unit in that group has the same chance of being chosen. We used `DataFrame.sample(..., replace=False, random_state=42)`.

**Q. Why without replacement?**

With replacement the same player/match could appear twice, which wastes the sample and slightly changes the variance. The populations are finite and small; we do not want duplicates.

**Q. What is stratified sampling? Why Task 2 only?**

Split the population into **strata** (here: stage), then sample inside each stratum. Knockout has only 32 matches, so we took a **census of that stratum** and an SRS of 32 of 72 group matches. Equal n keeps the two-sample t balanced. Tasks 1, 3, 4 already had two groups, so we SRS’d **inside** each group rather than stratifying a mixed list.

**Q. Why not convenience / judgement sampling?**

Those are biased. “Biggest stadiums” would fake a knockout attendance effect.

**Q. Why equal n, not proportional to population size?**

Equal n is simpler for a two-sample t and matches the “balanced groups” requirement. Proportional allocation would have given Task 3 something like 11 UEFA / 21 non-UEFA for n = 32, or used all 16 UEFA. We chose equal allocation and n = 14, just under the UEFA census.

**Q. Finite population: should you have used a finite-population correction?**

FPC shrinks SE when n is a large fraction of N. We sampled 45/319, 32/72, 14/16, 40/66. For Task 3, n/N = 14/16 is huge; an FPC would make SEs **smaller** and p **even smaller**. Skipping it is **conservative** (harder to reject). Good sentence if he pushes.

---

## 4. Variable types (he may start here)

**Q. What type of variables did you test?**

All four outcomes are **quantitative**. Cards/app and attendance and value and age are numeric means — so **t-tests for means**, not chi-square (that is for counts in categories) and not a test of proportions.

- Task 1: cards/app — numeric, right-skewed, many zeros  
- Task 2: attendance — numeric, roughly continuous  
- Task 3: market value EUR m — numeric, right-skewed, large SD  
- Task 4: age in years — numeric, fairly symmetric  

The **grouping** variables are categorical: position, stage, confederation, GK vs outfield.

**Q. Is age discrete or continuous?**

Recorded as whole years, treated as continuous for a mean. Standard in this unit.

---

## 5. Mean, median, SD, skew — especially Task 1

**Q. Why test the mean if the median cards/app is 0?**

Because the **research question is about the average rate**, μ. Most players have zero yellows; a few have several. The mean is pulled above the median. That is a real feature of count-like data, not a bug. The t-test still targets μ, not the median.

**Q. When would you prefer the median?**

When you want a “typical player” and the distribution is skewed with outliers. For inference on the median you would use a different tool (bootstrap or Wilcoxon). The brief asked for a t-test, which is a test about **means**.

**Q. What is standard deviation?**

Typical distance of observations from the mean, in the same units as the data. We used **sample SD** with divisor n−1 (ddof=1).

**Q. SD vs standard error?**

- **SD (s):** spread of **individuals**  
- **SE (s/√n):** spread of the **sample mean** if you repeated the sample

CI and t-tests use SE, not SD. Bigger n → smaller SE → tighter CI, easier to detect a given gap.

**Q. Your Task 1 histograms are skewed. Is the t-test invalid?**

The t-test does **not** require the raw data to be normal. It requires that the **sampling distribution of the mean** is approximately normal. By the **Central Limit Theorem**, that happens when n is reasonably large even if X is skewed. n = 45 is enough for a moderate skew. n = 14 in Task 3 is the weaker case — that is why we also report the large Cohen’s d and treat Task 3 more carefully.

**Memorise this sentence.** It is the most likely “gotcha” on Task 1.

---

## 6. Central Limit Theorem and the t distribution

**Q. What is a sampling distribution?**

The distribution of a statistic (x̄) across all possible samples of size n. We never see it directly; CLT and the t-model describe it.

**Q. State the CLT.**

For iid draws with finite mean and variance, as n grows,  
x̄ ≈ Normal(μ, σ²/n).  
So z = (x̄ − μ) / (σ/√n) → N(0,1).

**Q. Why t instead of z?**

σ is **unknown**. We plug in s. The extra uncertainty is a t distribution with df = n−1 (one-sample) — heavier tails than z, so the critical value is a bit larger (for n=45, t* ≈ 2.01 vs 1.96).

**Q. When would z be acceptable?**

σ known (rare) or n very large so t ≈ z. We never know σ here, so t is the correct default.

**Q. What are degrees of freedom?**

How many independent pieces of information remain after estimating parameters. One-sample: n−1 because we already used the data to get s. Two-sample pooled: n₁+n₂−2. Welch: a formula that can be **72.1**, not an integer.

---

## 7. Confidence intervals (he will ask this)

**Formula (one mean):**  
x̄ ± t* × (s / √n)  
t* = t_{n−1, 0.975} for 95%.

**Q. What does 95% confidence mean? (give the correct version)**

> If we repeated the whole sampling procedure many times, about 95% of the intervals we built would contain the true μ. For **this** interval, μ is either inside or not — it is not a random quantity.

**Wrong answers (do not say):**

- “There is a 95% probability that μ is in (a, b).” Once the interval is computed, μ is fixed.  
- “95% of the data lie in the interval.” That is a different idea (a prediction interval / empirical range).  
- “We are 95% sure of the sample mean.” The sample mean is known exactly.

**Q. How does a CI relate to a two-sided t-test at 5%?**

They are two views of the same maths.

- Task 4: CI for GK age is **(28.74, 31.91)**. 27 is **outside**, so the two-sided test of H₀: μ = 27 **rejects**.  
- If a CI for a difference of means contains **0**, the two-sided test of H₀: μ₁ = μ₂ **fails to reject**.

This duality is for **two-sided** tests. Task 3 is **one-sided**, so do not quote the CI as a substitute for that p-value. The CI we reported is for the UEFA **mean**, not for the difference.

**Q. What is the margin of error?**

t* × SE. Wider if: you want 99% instead of 95%; s is large; n is small.

**Q. Why 95% not 99%?**

Convention in the unit, matching α = 0.05. 99% would be wider (harder to exclude a null value).

---

## 8. Hypothesis testing — the framework

**Always four pieces:** H₀, H₁, α, test statistic → p → decision.

**Q. What is a null hypothesis?**

The sceptical default, usually “no difference / no effect,” written about **parameters** (μ, not x̄).

**Q. Why is H₀ the “no effect” statement?**

Science tries to **disprove** a simple default. We ask whether the sample is too extreme for that default to be believable.

**Q. How do you write H₀ / H₁ for each task?**

| Task | H₀ | H₁ | Tail |
|------|----|----|------|
| 1 | μ_MF = μ_DF | μ_MF ≠ μ_DF | two |
| 2 | μ_KO = μ_group | μ_KO ≠ μ_group | two |
| 3 | μ_UEFA = μ_non | μ_UEFA > μ_non | **one** |
| 4 primary | μ_GK = 27 | μ_GK ≠ 27 | two |
| 4 support | μ_GK = μ_OF | μ_GK ≠ μ_OF | two |

**Q. Why never “accept H₀”?**

A non-significant result means the data are **compatible** with H₀, not that H₀ is proven. The true difference might be small and the test under-powered. Say **fail to reject**.

**Q. Walk through the decision rule.**

If p ≤ α, reject H₀. If p > α, fail to reject. We used α = 0.05 throughout (no peeking at p then changing α).

---

## 9. p-values (he will definitely ask)

**Say this, slowly:**

> The p-value is the probability of getting a test statistic at least as extreme as the one we observed, **calculated under the assumption that H₀ is true**.

**Q. Extreme in which direction?**

Two-sided: both tails. One-sided: only the tail named in H₁. Task 3 p = 0.0041 is one-sided; two-sided would be about 0.008.

**Q. What a p-value is NOT**

- Not P(H₀ is true | data)  
- Not P(we made an error)  
- Not the probability the result was due to chance in everyday English (too vague)  
- Not the size of the effect (that is Cohen’s d / the mean gap)

**Q. p = 0.45 in Task 1. What does that mean?**

If midfielders and defenders had the **same** mean card rate, a gap as big as 0.098 vs 0.131 (or bigger) would happen in about 45% of random samples. That is very compatible with H₀, so we do not reject.

**Q. p = 0.004 in Task 3. What does that mean?**

If UEFA and non-UEFA had the same mean value, seeing UEFA this much higher would be rare (about 4 in 1,000 under the one-sided null). We reject.

**Q. Is p = 0.06 “almost significant”?**

Do not move the goalposts. At α = 0.05, p = 0.06 fails to reject. You may say it is **borderline** and look at effect size and CI, but the pre-set decision is fail to reject.

---

## 10. Type I, Type II, power

| | H₀ true | H₀ false |
|--|---------|----------|
| Reject H₀ | **Type I** (false positive), probability α | Correct (power) |
| Fail to reject | Correct | **Type II** (false negative), probability β |

**Power** = 1 − β = P(reject H₀ | H₀ is false). Power rises with n, with true effect size, and with α.

**Q. What Type I rate did you choose?**

α = 0.05. In the long run, 1 in 20 true nulls would be rejected by chance.

**Q. You ran four tests. Multiple testing?**

Four tests at 5% each raise the chance of **at least one** false rejection (family-wise error). A Bonferroni correction would use α = 0.05/4 = 0.0125.

*Honest application to our results:*

- Task 3 p = 0.004 and Task 4 p = 0.0001 still beat 0.0125. Those rejections **survive** Bonferroni.  
- Tasks 1–2 would still be non-significant.  
- So our story does not depend on uncorrected fishing.

This is a high-level answer. If you never mention Bonferroni unless asked, that is fine. If asked, this is the answer.

**Q. Power in Tasks 1–2?**

We did not compute power. Cohen’s d was small (−0.16, 0.22). A small real difference could exist and we might have missed it (Type II). That is why we **fail to reject**, we do not “prove no difference.”

**Q. Power in Task 3 with n = 14?**

Small n usually means low power — but the effect was **large** (d = 1.08), and we still rejected. So power was adequate **for an effect of that size**.

---

## 11. One-sided vs two-sided

**Q. When is one-sided allowed?**

When the **research question is directional before you see the sample**, and the other tail would not be of interest. Task 3: “Do UEFA squads carry a **higher** value?”

**Q. Why were Tasks 1, 2, 4 two-sided?**

The opposite gap was scientifically plausible. In Task 1, defenders actually had the **higher** sample mean. A one-sided “MF > DF” test would have been the wrong tail.

**Q. Did you choose one-sided after seeing UEFA were richer?**

No. The **wording of the question** is one-sided. To defend it: two-sided p ≈ 0.008 still rejects at 5%.

**Q. Why is one-sided “easier” to reject?**

The 5% sits in **one** tail instead of 2.5% each. Same t = 2.87 gives a smaller p one-sided. That is why you must pre-specify.

---

## 12. t-test assumptions

For a two-sample t:

1. **Independence** within and between groups (SRS helps)  
2. The **mean** is approximately normal (CLT / not tiny n + wild skew)  
3. For **pooled** t only: equal population variances (we **test** this with Levene)

**Q. What does Levene test?**

H₀: the two groups have equal variances. If Levene p > 0.05, we do not reject equal variance → **pooled t**. If Levene p < 0.05 → **Welch t** (does not assume σ₁ = σ₂).

| Task | Levene p | Test used | df |
|------|----------|-----------|-----|
| 1 | 0.45 | pooled | 88 |
| 2 | 0.94 | pooled | 62 |
| 3 | 0.13 | pooled | 26 |
| 4 two-sample | **0.04** | **Welch** | **72.1** |

**Q. Why is Welch df = 72.1 not 78?**

Pooled df = 40+40−2 = 78. Welch down-weights df when SDs differ (4.95 vs 3.69). It is the safer test when Levene rejects.

**Q. Independence — are players independent?**

Not perfectly: two midfielders on the same squad share tactics and referees. Honest limitation. We still sampled at **player** grain because that is the question (cards per appearance by position). Matches in Task 2 are closer to independent units.

**Q. Why not a paired t-test?**

Paired t needs **matched pairs** (before/after, or husband/wife). MF and DF are two independent groups, not pairs. Knockout and group matches are different matches, not pairs. UEFA vs non-UEFA are different countries.

**Q. Why not ANOVA?**

ANOVA is for **3+** group means. We always compared **two** groups (or one group vs a number). If we had tested all six confederations’ mean values, that would be one-way ANOVA, then post-hoc tests. We dichotomised UEFA vs rest because that was the question.

**Q. Why not chi-square?**

Chi-square tests **association of categorical variables** (counts). Our outcomes are numeric means.

**Q. Why not Mann–Whitney / Wilcoxon?**

Non-parametric tests of stochastic dominance / medians, useful when n is tiny and skew is brutal. The brief asked for a t-test. With n = 45 the CLT is our justification. Task 3 (n = 14, skew) is the place a rank test could be a **robustness check** we did not run.

---

## 13. The test statistic (if he says “write the formula”)

**One-sample (Task 4):**

\[
t = \frac{\bar x - \mu_0}{s/\sqrt{n}} = \frac{30.33 - 27}{4.95/\sqrt{40}} \approx 4.25,\quad df = 39
\]

**Two-sample pooled (Tasks 1–3):**

\[
t = \frac{\bar x_1 - \bar x_2}{s_p \sqrt{\frac{1}{n_1}+\frac{1}{n_2}}},\quad df = n_1+n_2-2
\]

Welch uses a different SE (no pooled s) and Satterthwaite df.

You do not need to compute live. You need to **point at numerator = gap, denominator = SE**.

**Q. What does t = −0.76 mean in Task 1?**

The MF−DF gap is 0.76 standard errors below zero — less than one SE, so of course p is large.

**Q. What does t = 2.87 mean in Task 3?**

UEFA’s mean sits 2.87 SEs above the non-UEFA mean, in the direction of H₁ — unusual under H₀.

---

## 14. Effect size vs statistical significance

**Q. What is the difference?**

- **Statistical significance:** p < α. “Unlikely if H₀ were true.”  
- **Practical / scientific importance:** is the gap **big** in football terms? Cohen’s d and the raw difference answer that.

A huge sample can make a tiny, useless gap “significant.” A small sample can miss a big gap.

**Cohen’s d** = (x̄₁ − x̄₂) / s_pooled. Rough guide: 0.2 small, 0.5 medium, 0.8 large.

| Task | p | d | Read it |
|------|---|---|---------|
| 1 | 0.45 | −0.16 | not significant, **and** small |
| 2 | 0.38 | 0.22 | not significant, **and** small (~2,000 fans on ~66,000) |
| 3 | 0.004 | **1.08** | significant **and** large (2.6× value) |
| 4 vs 27 | 0.0001 | 0.67 | significant, medium–large (~3.3 years) |

**Never say “it is significant so it matters” without d or the raw gap.**

---

## 15. α vs confidence level

**Q. How are 0.05 and 95% related?**

Same tail probability: α = 0.05 ↔ 95% CI for a two-sided test. 99% CI ↔ α = 0.01 (stricter).

We did **not** mix them (no 95% CI then testing at 0.01).

---

## 16. Reproducibility and seed 42

**Q. Why a seed?**

A random sample is still random; the seed fixes **which** draw we got so a marker can rerun `wc2026_analytics.py` and see the same n, means, and p. It is not a magic number that improves the science.

**Q. Would a different seed change the conclusion?**

Possibly for Tasks 1–2 (effects are small, p near the middle of [0,1]). Unlikely for Tasks 3–4 (p is far below 0.05, d is large). That is a good limitation sentence.

---

## 17. Rapid-fire traps — one-line fixes

| If he says | You say |
|------------|---------|
| “So they are equal.” | We **failed to reject** equality. We did not prove it. |
| “p = 0.45 means 45% chance H₀ is true.” | No. It is 45% chance of data this extreme **if** H₀ were true. |
| “95% chance μ is in the CI.” | 95% of **repeated intervals** cover μ. This interval either does or does not. |
| “t-test needs normal data.” | It needs an approximately normal **sampling distribution of the mean**. CLT, n = 45. |
| “Why not z?” | σ unknown → t. |
| “Why sample?” | Required skill; balanced groups. |
| “One-sided is cheating.” | Question was directional; two-sided p still 0.008. |
| “Significant means important.” | Look at Cohen’s d and the raw gap. |
| “df = 72.1 is a bug.” | Welch / Satterthwaite when variances differ. |
| “You should have used all the data.” | Then it is a census, not the sampling skill. Sensitivity: Task 3 would still reject. |

---

## 18. A 10-minute speaking drill (do this tonight)

One person asks, the other answers **without notes**, then swap.

1. Population vs sample vs parameter vs statistic.  
2. What is a sampling distribution? What does CLT say?  
3. Why t not z? What is df?  
4. Exact definition of a p-value.  
5. Exact definition of a 95% CI.  
6. Fail to reject vs accept. Type I vs Type II.  
7. Assumptions of a two-sample t. What Levene decides.  
8. Why Task 1 t-test is still OK when most players have 0 cards.  
9. Why Task 3 is one-sided and the others are not.  
10. Statistical significance vs Cohen’s d, using Task 1 vs Task 3.  
11. Why not paired t, ANOVA, or chi-square.  
12. Multiple testing: would Bonferroni change your two rejections? (No.)

If you can do those twelve out loud, you are ready for a theory-heavy viva.
