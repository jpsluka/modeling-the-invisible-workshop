# Competition Rules

## Overview

The workshop is a forecasting competition focused on influenza-associated hospitalizations.

The competition is organized as:

- two independent challenges, representing two independent years
- three rounds per challenge
- sequential data releases within each challenge
- team submissions identified as `Team-01`, `Team-02`, and so on

## Team structure

- Teams may contain between 1 and 4 participants.
- Each participant may belong to only one team.
- Teams may use any software, programming language, modeling framework, or analysis workflow.

## Forecast targets

Teams forecast:

- weekly influenza-associated hospitalizations per 100,000 population
- effective reproduction number (`r0`)

## Time system

- The competition uses a normalized 40-week influenza season.
- Week numbers are integers.
- Week 1 represents the start of the season.
- No calendar dates are used in submissions.

## Submission rules

- Each team submits one CSV file per challenge round.
- The submission must include the full predicted weekly trajectory from Week 1 through the forecast horizon.
- The forecast horizon is defined by the release metadata for that round.
- Submissions are automatically validated and scored.

## Allowed methods

Participants may use any of the following:

- mechanistic epidemic models
- statistical forecasting models
- machine learning methods
- Bayesian approaches
- agent-based simulations
- hybrid or ensemble methods
- external public data sources
- publicly available software libraries

## Only explicit prohibition

The only activity explicitly forbidden is:

- hacking into the organizer's or other workshop participants' computer systems

## Data use

Released workshop data are intended for workshop use only.

Participants should not redistribute unpublished organizer-generated data outside the workshop without permission.

## Conduct

Participants are expected to communicate respectfully, collaborate constructively, and document their assumptions clearly.

## Organizer authority

Workshop organizers may clarify rules, correct data-release issues, and resolve ambiguities as needed.
