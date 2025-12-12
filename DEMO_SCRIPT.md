# Demo Script: Agentic Ad Optimizer V2

## 1. Introduction (10s)
*Showing Loop View (Step 1)*
'This is Agentic Ad Optimizer. We've built an autonomous loop that designs experiments, generates real creative assets using Bria FIBO, and optimizes based on performance data.'

## 2. Planning & Generation (45s)
*Action: Fill form with 'Math Wars' example -> Click 'Generate Plan'*
'I'll start by giving the agent a business snapshot. It analyzes this to design a split test.'
*Action: Plan appears -> Click 'Generate creatives'*
'Now the agent is calling the Bria API to generate variants. Unlike standard image models, these are constrained by JSON specs for consistent brand control.'

## 3. Controllability & Iteration (60s)
*Action: Wait for images -> Click 'Product Shot' preset on Variant A -> Regenerate*
'Here are the results. Notice the Bria LIVE badge—these are real generations. If I want to pivot the strategy, I don't need to guess prompts. I can apply a preset like 'Product Shot'...'
*Action: Show Before/After*
'In seconds, the agent updates the JSON spec and regenerates the asset. We can see the clear before-and-after difference here.'

## 4. Scoring & Optimization (30s)
*Action: Click 'Score Creatives' -> Fill results -> Submit*
'Finally, the agent scores the creatives against our rubric. We feed back performance data, and it recommends the next logical test to run, closing the loop.'

