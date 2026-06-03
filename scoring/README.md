# Scoring Outputs

This folder is populated automatically by the workflow.

- `scoring/challenge-01/leaderboard.csv`
- `scoring/challenge-02/leaderboard.csv`
- `scoring/overall-leaderboard.csv`

# Scoring weights

Scores are caclated as the RMS error for the wekklys predictions and Rt (R0) speretted. The two are combined with

`round_score = 0.8 × hospitalization_nRMSE + 0.2 × R0_RMSE`
