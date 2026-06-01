# Competition Rules

## Overview

The **Modeling the Invisible** workshop forecasting competition is a collaborative scientific exercise focused on predicting influenza-associated hospitalization dynamics.

## Team Structure

- Teams may contain between 1 and 4 participants.
- Participants may belong to only one team.
- Teams may use any software, programming language, modeling framework, or analysis workflow.

## Competition Structure

The competition consists of multiple sequential forecast rounds.

For each round:
1. Organizers release updated hospitalization data.
2. Teams submit forecasts through the release horizon.
3. Forecasts are scored automatically.

## Forecast Targets

Teams forecast:

- weekly influenza-associated hospitalizations per 100,000 population
- the effective reproduction number (`r0`)

## Time System

The competition uses a normalized 40-week influenza season.

- Week numbers are integers.
- Week 1 corresponds to the beginning of the season.
- No calendar dates are used in submission files.

## Submission Rules

Each team submits one CSV file per round.

Submission files must:

- follow the official repository format
- contain the full predicted trajectory through the release horizon
- be committed to the repository before the submission deadline

## Permitted Methods

Participants may use any of the following, including combinations thereof:

- mechanistic epidemic models
- statistical forecasting models
- machine learning methods
- Bayesian approaches
- agent-based simulations
- hybrid or ensemble methods
- manual parameter tuning
- external public datasets
- publicly available software libraries

## Prohibited Activities

The only explicitly forbidden activity is attempting to gain unauthorized access to the organizer's or another participant's computer systems.

The workshop operates on an honor system emphasizing scientific collaboration and professionalism.

## Scoring

Forecasts are evaluated automatically using held-out ground truth data.

Detailed scoring methodology is documented separately in:

```text
docs/scoring-rules.md
```

## Reproducibility

Participants are encouraged to:

- document modeling assumptions
- preserve reproducible workflows
- maintain version-controlled code
- describe uncertainty sources

## Data Usage

Released workshop datasets are intended solely for educational and research purposes within the workshop.

Participants should not redistribute unpublished organizer-generated datasets outside the workshop without permission.

## Workshop Conduct

Participants are expected to:

- engage respectfully with other teams
- share ideas constructively
- acknowledge uncertainty honestly
- contribute to a collaborative workshop atmosphere

## Organizer Authority

Workshop organizers reserve the right to:

- clarify rules
- resolve ambiguities
- correct data-release issues
- modify schedules if necessary
- remove submissions that violate the competition rules

Any major rule modifications will be documented publicly in the repository.
