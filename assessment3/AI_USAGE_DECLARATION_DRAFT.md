# Draft text for the signed AI Usage Declaration Form

Copy into the official CDU form. Every group member must sign. Do not submit this markdown file instead of the form.

## Acknowledgement of generative AI

We used Cursor (Grok) as a coding and drafting assistant while preparing HIT140 Assessment 3. The Excel dataset, the choice of two pre-kickoff OLS models, the eight predictors in each model, and the interpretation of rank and value coefficients are the group’s decisions. We can explain every Python step in assignment3_final_code.py.

Where applicable, conversation history: the Cursor cloud agent used for this project (World Cup 2026 analytics).

## Reflective account (paste into the form)

We used generative AI in three limited ways.

1. Python. AI helped write and tidy assignment3_final_code.py (loading Excel sheets, building rank/value differences, rest-day fill, OLS with an 80/20 split, VIF and Shapiro–Wilk, and the two predicted-versus-actual charts). We ran the file ourselves, checked that there are 104 matches and 48 teams, and confirmed the printed R² and p-values against the report tables.

2. Report outline and proofreading. AI suggested a four-page structure (questions, wrangling, Model 2.1, Model 2.2, diagnostics, limitations). We then wrote the findings in our own words: what rank_diff’s negative sign means, why Model 2.2 has a lower R², why we did not treat rest_days as a real fatigue effect, and why shots were banned. AI was used to shorten sentences so the file stayed inside four pages and to check spelling.

3. We did not ask AI to invent match results or missing values. Attendance, rankings and scores come from public tournament sources. First-match rest days are filled with the median rest of five days, which is documented in the code.

What we still had to understand without the tool: the difference between training R² and test R²; why VIF below 5 is acceptable; why a small p-value is not the same as a large effect; and why two rows per match in Model 2.2 are not independent.

If asked in an interview, any member should be able to open assignment3_final_code.py, point to FEATS_21 and FEATS_22, and explain the 80/20 split, seed 42, the four shared ideas, and the significant coefficients (rank_diff and value_diff in 2.1; team_rank and opp_appearances in 2.2).
