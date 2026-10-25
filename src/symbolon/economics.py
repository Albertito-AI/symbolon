"""Illustrative deterrence model. Never a production bond or insurance quote.

Amounts are analysis units (for example USD), not ledger money. The model
assumes risk neutrality, enforceable forfeiture, calibrated error rates and
equal loss of payment plus bond after an adverse decision. Those assumptions
are not established by this software. See docs/economics.md.
"""

from dataclasses import asdict, dataclass
import math


@dataclass(frozen=True)
class DeterrencePlan:
    bond: float
    audit_probability: float
    audit_cost: float
    capital_cost: float
    objective_cost: float
    feasible_bond_floor: float
    effective_detection: float
    binding_constraint: str

    def to_dict(self):
        return asdict(self)


def _number(value, name, minimum=0):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite number")
    try:
        value = float(value)
    except OverflowError as exc:
        raise ValueError(f"{name} exceeds the numeric model range") from exc
    if not math.isfinite(value) or value < minimum:
        raise ValueError(f"{name} must be finite and at least {minimum}")
    return value


def plan_deterrence(*, price, saved_cost, audit_cost, annual_capital_rate,
                    lock_days, detection=1.0, false_positive=0.0, bond_cap=None):
    """Minimise audit cost + opportunity cost on a bounded feasible interval.

    p (detection - false_positive) (price + bond) >= saved_cost; 0 <= p <= 1.
    Raises ValueError when the desired incentive constraint is infeasible or
    when zero capital cost leaves only an unattained infinite-bond infimum.
    """
    p0 = _number(price, "price")
    dc = _number(saved_cost, "saved_cost")
    a = _number(audit_cost, "audit_cost")
    r = _number(annual_capital_rate, "annual_capital_rate")
    days = _number(lock_days, "lock_days")
    delta = _number(detection, "detection")
    epsilon = _number(false_positive, "false_positive")
    cap = None if bond_cap is None else _number(bond_cap, "bond_cap")
    if delta > 1 or epsilon > 1:
        raise ValueError("detection and false_positive must be in [0, 1]")
    d = delta - epsilon
    h = r * days / 365
    if not math.isfinite(h):
        raise ValueError("capital cost exceeds the numeric model range")
    if r > 0 and days > 0 and h == 0:
        raise ValueError("capital cost underflows the numeric model")
    if dc == 0:
        return DeterrencePlan(0, 0, 0, 0, 0, 0, d, "no_cost_saving")
    if d <= 0:
        raise ValueError("the verifier does not distinguish shirking from honest work")
    floor = max(0.0, dc / d - p0)
    if not math.isfinite(floor):
        raise ValueError("feasible bond exceeds the numeric model range")
    if cap is not None and cap < floor:
        raise ValueError("bond cap makes deterrence infeasible even at 100% audit")
    if a == 0:
        bond = floor
        constraint = "zero_audit_cost"
    elif h == 0:
        if cap is None:
            raise ValueError("zero capital cost requires a finite bond cap")
        bond = cap
        constraint = "bond_cap"
    else:
        try:
            squared = a * dc / (h * d)
        except ZeroDivisionError as exc:
            raise ValueError("rates underflow the numeric model") from exc
        if not math.isfinite(squared):
            raise ValueError("optimal bond exceeds the numeric model range")
        unconstrained = math.sqrt(squared) - p0
        bond = max(floor, unconstrained)
        constraint = "feasibility_floor" if bond == floor else "interior"
        if cap is not None and bond > cap:
            bond = cap
            constraint = "bond_cap"
    denominator = d * (p0 + bond)
    if not math.isfinite(denominator) or denominator <= 0:
        raise ValueError("incentive calculation exceeds the numeric model range")
    probability = dc / denominator
    if probability == 0 or probability * denominator < dc * (1 - 1e-12):
        raise ValueError("audit probability underflows the incentive constraint")
    if probability > 1 + 1e-12:
        raise ValueError("no feasible audit probability")
    probability = min(1.0, probability)
    ac = a * probability
    cc = h * bond
    if not all(math.isfinite(value) for value in (bond, probability, ac, cc, ac + cc)):
        raise ValueError("cost exceeds the numeric model range")
    return DeterrencePlan(bond, probability, ac, cc, ac + cc, floor, d, constraint)

