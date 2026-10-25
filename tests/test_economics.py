import math
import unittest
from symbolon.economics import plan_deterrence


class EconomicsTests(unittest.TestCase):
    def plan(self, **changes):
        values = dict(price=40, saved_cost=12, audit_cost=6, annual_capital_rate=.1,
                      lock_days=7, detection=1, false_positive=0, bond_cap=1000)
        return plan_deterrence(**(values | changes))

    def test_report_example(self):
        p = self.plan()
        self.assertAlmostEqual(p.bond, 153.759792677, places=6)
        self.assertAlmostEqual(p.objective_cost, .666475917, places=7)
        self.assertAlmostEqual(p.audit_probability * (40 + p.bond), 12)

    def test_imperfect_detection(self):
        p = self.plan(detection=.8)
        self.assertAlmostEqual(p.bond, 176.63003385, places=6)

    def test_false_positives_raise_required_rate_for_fixed_bond(self):
        baseline = self.plan(bond_cap=100)
        noisy = self.plan(bond_cap=100, false_positive=.1)
        self.assertGreater(noisy.audit_probability, baseline.audit_probability)

    def test_feasibility_floor(self):
        p = self.plan(price=1, saved_cost=12, audit_cost=.001, bond_cap=20)
        self.assertAlmostEqual(p.bond, 11)
        self.assertAlmostEqual(p.audit_probability, 1)

    def test_infeasible_cap(self):
        with self.assertRaises(ValueError):
            self.plan(price=1, saved_cost=12, bond_cap=10)

    def test_indiscriminate_verifier(self):
        with self.assertRaises(ValueError):
            self.plan(detection=.2, false_positive=.2)

    def test_zero_temptation(self):
        p = self.plan(saved_cost=0, detection=0)
        self.assertEqual((p.bond, p.audit_probability, p.objective_cost), (0, 0, 0))

    def test_zero_capital_requires_finite_cap(self):
        with self.assertRaises(ValueError):
            self.plan(annual_capital_rate=0, bond_cap=None)
        self.assertEqual(self.plan(annual_capital_rate=0, bond_cap=200).bond, 200)

    def test_zero_audit_cost_chooses_floor(self):
        self.assertEqual(self.plan(audit_cost=0).bond, 0)

    def test_bounded_optimum_beats_nearby_feasible_values(self):
        p = self.plan()
        objective = lambda b: 6 * 12 / (40 + b) + .1 * 7 / 365 * b
        for b in (0, 50, 100, 150, 180, 200, 500):
            self.assertLessEqual(p.objective_cost, objective(b) + 1e-10)

    def test_bad_numeric_inputs(self):
        for bad in (True, -1, math.nan, math.inf, "40"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                self.plan(price=bad)
        with self.assertRaises(ValueError):
            self.plan(detection=1.1)

