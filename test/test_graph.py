"""Simple unit tests from the paper and slides that only look at the final result (sketches)
"""

import unittest

from retypd import (
    ConstraintSet,
    SchemaParser,
)

from retypd.schema import Variance
from retypd.graph import ConstraintGraph, Node

VERBOSE_TESTS = False


class ConstraintGraphTest(unittest.TestCase):
    def test_simple(self):
        """
        Check that the constraint graph from one constraint has the expected elements.
        A constraint graph from one constraint has two paths that allow us to reconstruct
        the constraint, one in covariant version and one in contravariant.
        """
        cs = ConstraintSet(
            [SchemaParser.parse_constraint("f.in_0 <= A.load.σ4@0")]
        )
        graph = ConstraintGraph(cs).graph
        f_co = Node(SchemaParser.parse_variable("f"), Variance.COVARIANT)
        fin0_co = Node(
            SchemaParser.parse_variable("f.in_0"), Variance.COVARIANT
        )

        a_load_0_co = Node(
            SchemaParser.parse_variable("A.load.σ4@0"), Variance.COVARIANT
        )
        a_load_co = Node(
            SchemaParser.parse_variable("A.load"), Variance.COVARIANT
        )
        a_co = Node(SchemaParser.parse_variable("A"), Variance.COVARIANT)

        f_cn = Node(SchemaParser.parse_variable("f"), Variance.CONTRAVARIANT)
        fin0_cn = Node(
            SchemaParser.parse_variable("f.in_0"), Variance.CONTRAVARIANT
        )

        a_load_0_cn = Node(
            SchemaParser.parse_variable("A.load.σ4@0"), Variance.CONTRAVARIANT
        )
        a_load_cn = Node(
            SchemaParser.parse_variable("A.load"), Variance.CONTRAVARIANT
        )
        a_cn = Node(SchemaParser.parse_variable("A"), Variance.CONTRAVARIANT)
        self.assertEqual(
            {
                f_co,
                fin0_co,
                a_load_0_co,
                a_load_co,
                a_co,
                f_cn,
                fin0_cn,
                a_load_0_cn,
                a_load_cn,
                a_cn,
            },
            set(graph.nodes),
        )

        edges = {
            # one path from "f" to "A"
            (f_cn, fin0_co),
            (fin0_co, a_load_0_co),
            (a_load_0_co, a_load_co),
            (a_load_co, a_co),
            # the second path from "A" to "f"
            (a_cn, a_load_cn),
            (a_load_cn, a_load_0_cn),
            (a_load_0_cn, fin0_cn),
            (fin0_cn, f_co),
        }
        self.assertEqual(edges, set(graph.edges()))

    def test_two_constraints(self):
        """
        A constraint graph from two related constraints has two paths
        (a covariant and contravariant version) that allow us to conclude
        that A.out <= C.
        """
        constraints = ["A <= B", "B.out <= C"]
        cs = ConstraintSet(map(SchemaParser.parse_constraint, constraints))
        graph = ConstraintGraph(cs).graph
        b_co = Node(SchemaParser.parse_variable("B"), Variance.COVARIANT)
        b_out_co = Node(
            SchemaParser.parse_variable("B.out"), Variance.COVARIANT
        )
        a_co = Node(SchemaParser.parse_variable("A"), Variance.COVARIANT)
        c_co = Node(SchemaParser.parse_variable("C"), Variance.COVARIANT)

        b_cn = Node(SchemaParser.parse_variable("B"), Variance.CONTRAVARIANT)
        b_out_cn = Node(
            SchemaParser.parse_variable("B.out"), Variance.CONTRAVARIANT
        )
        a_cn = Node(SchemaParser.parse_variable("A"), Variance.CONTRAVARIANT)
        c_cn = Node(SchemaParser.parse_variable("C"), Variance.CONTRAVARIANT)

        edges = {
            # path from A to C
            (a_co, b_co),
            (b_co, b_out_co),
            (b_out_co, c_co),
            # path from C to A
            (c_cn, b_out_cn),
            (b_out_cn, b_cn),
            (b_cn, a_cn),
        }
        self.assertEqual(edges, set(graph.edges()))