# Economics and model assumptions

The initial economic model is an experiment in the incentives to verify delegated work. Its outputs are illustrative parameters for simulation. They are not prices for insurance, estimates of actual losses, or evidence that a contractual forfeiture would be enforceable. The project must measure demand and verification performance before using these calculations to set commercial terms.

## Audit and bond calibration

Let the agreed task payment be `P > 0`, the supplier's cost of honest performance be `c_H`, and its cost of shirking be `c_L`. Define the non-negative private gain from shirking as `D = c_H - c_L`. Let `B` be collateral, `p` the audit probability, and `A` the cost of one audit. Conditional on an audit, let `delta` be the probability of an adverse decision against a shirking supplier and `epsilon` the probability of an adverse decision against an honest supplier. These are probabilities after the review process relevant to payment, not merely an initial model's classification scores.

Assume that an adverse decision causes the supplier to lose both the payment and the whole bond, that the supplier is risk neutral, and that the same collateral carrying cost applies under either action. With annual capital rate `r` and a lock of `t` days, write `h = r*t/365`. Expected supplier payoffs are then:

```text
U_honest = P - c_H - p*epsilon*(P+B) - h*B
U_shirk  = P - c_L - p*delta*(P+B) - h*B
```

Honest performance is weakly preferred exactly when:

```text
p*(delta-epsilon)*(P+B) >= D
```

Thus false positives reduce the effective deterrence of a verifier. Replacing perfect detection by `delta` alone is justified only when false positives are zero. Define `d = delta-epsilon`. When `D > 0`, the mechanism requires `d > 0` and:

```text
p_min(B) = D / [d*(P+B)]
B_min    = max(0, D/d-P)
```

The second expression enforces `p <= 1`. If available collateral `B_max` is smaller than `B_min`, deterrence is infeasible under these assumptions. An implementation must report infeasibility; clipping an audit probability greater than one would silently remove the incentive guarantee.

For the narrow objective consisting of audit expenditure and collateral carrying cost,

```text
C(B)  = A*D / [d*(P+B)] + h*B
C'(B) = -A*D / [d*(P+B)^2] + h
```

For positive `A`, `D`, `h` and `d`, convexity gives:

```text
B_unconstrained = sqrt(A*D/(h*d)) - P
B_optimal       = min(B_max, max(B_min, B_unconstrained))
p_optimal       = D / [d*(P+B_optimal)]
```

This is a constrained minimum, conditional on feasible collateral. The boundary cases must be explicit:

| Inputs | Result |
| --- | --- |
| `D = 0` | Choose `B = 0`, `p = 0` for this objective. Independent quality controls may still be necessary. |
| `D > 0`, `d <= 0` | No feasible deterrence solution. |
| `B_min > B_max` | No feasible deterrence solution. |
| `A = 0`, `h > 0` | Choose `B_min`; free auditing makes additional collateral unnecessary. |
| `h = 0`, `A > 0`, finite `B_max` | Choose `B_max`. Without a finite cap, there is generally no finite minimum. |
| `A = h = 0` | All feasible choices have the same objective; choose `B_min` as a declared tie rule. |

Reject non-finite numbers, negative costs, invalid probability ranges and negative capital periods. Recalculate the required audit probability after rounding collateral to currency units. A rounded display value is not the enforcement parameter.

### Reproducing the original example

For `P = 40`, `D = 12`, `A = 6`, `r = 0.10`, `t = 7`, and sufficient collateral, the report's arithmetic is correct:

| Detection | False positives | Optimal bond | Audit probability | Audit and capital cost |
| --- | --- | --- | --- | --- |
| 100% | 0% | 153.7598 | 6.1932% | 0.6665 |
| 80% | 0% | 176.6300 | 6.9242% | 0.7542 |
| 80% | 2% | 179.3898 | 7.0125% | 0.7648 |

Amounts use the same hypothetical currency units as the task price. The third row extends the original example. These totals exclude disputes, customer support, rail charges, fraud, operating overhead, model errors and losses suffered by buyers.

### What the calculation cannot establish

Deterrence concerns a rational supplier's choice between two actions. It does not prevent honest mistakes, ambiguous specifications, compromise or correlated outages. Supplier participation also requires `U_honest` to meet the supplier's outside option. At the minimum audit rate, expected false-positive forfeiture is `epsilon*D/d`; this may deter honest participation even when the narrow cost calculation looks attractive.

The entire `B` is assumed to be recoverable on an adverse decision. Legal limits, appeal reversals and collection risk may invalidate that assumption. The amount held as security and the amount lawfully payable as compensation are different quantities. A pre-funded bond remains at risk even if its pseudonymous owner disappears; the original report's suggestion that disappearance necessarily leaves nothing to forfeit is incorrect. Any shared bond must be reserved against aggregate outstanding obligations and cannot be counted in full for every concurrent task.

## Reputation and correlated errors

With independent, identically distributed binary outcomes and a uniform prior, `s` successes and `f` failures give a `Beta(s+1,f+1)` posterior. Its fifth percentile is approximately `0.3684` for two successes and no failures, and `0.9686` for 900 successes and 20 failures. The report's rounded examples are correct. Geometrically discounted or fee-weighted counts are modelling choices, not automatically a calibrated posterior for independent observations. Scores should be specific to task class, evaluator and software version.

Charging fees can make wash transactions costly, but does not establish Sybil resistance. An attacker may recover fees through rebates or colluding verifiers, purchase a score to exploit several future buyers, or concentrate apparent activity among related operators. Require related-party detection, caps on credit from any buyer, meaningful independent verification, and exposure limits. The original Cheng and Friedman impossibility result has a defined graph model and definition of symmetry; it is not a theorem that every economically costly reputation system is secure. See Alice Cheng and Eric Friedman, ‘Sybilproof Reputation Mechanisms’, [ACM proceedings](https://doi.org/10.1145/1080192.1080202).

For `n` Bernoulli failures with common probability `theta` and common pairwise correlation `rho`, covariance expansion gives:

```text
Var(F) = n*theta*(1-theta)*[1+(n-1)*rho]
```

For `n = 100` and `rho = 0.3`, the variance multiplier is `30.7`. Mean and pairwise correlation do not identify the joint distribution or the probability of catastrophic loss. Model-family diversity is a useful hypothesis to test, not proof of independent verification. Measure common errors on held-out tasks and stress shared dependencies such as hosting, retrieval and tool providers.

## Clearing and commercial validation

The McAfee mechanism's truthfulness claim belongs to its single-unit homogeneous-good model. The report's at-most-one-lost-trade statement is compatible with that model, but implementation needs explicit boundary behaviour when a next losing bid or ask is absent. Arbitrary rebates can change incentives. A scoring rule for differentiated work needs enforceable quality attributes and an explicit payment rule; simply sorting a sealed batch does not make truthful bidding dominant. See R Preston McAfee, ‘A Dominant Strategy Double Auction’ (1992) 56 *Journal of Economic Theory* 434–450, [publisher record](https://doi.org/10.1016/0022-0531(92)90091-U).

Begin with posted-price, reproducibly testable work. Measure buyer losses, verification costs, support time, disputes, repeat purchases and supplier participation separately. Publish denominators and uncertainty intervals. Zero observed failures does not demonstrate a zero failure probability. Fees should cover measured costs and a disclosed margin; assumed audit savings do not establish willingness to pay. The initial project should test these propositions before adding auctions, tradeable reputation or underwriting.
