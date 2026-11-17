import _paths
import unittest

from audit_references import identity_key, literal_matches, literal_score, traits_from_column


class ReferenceAuditTests(unittest.TestCase):
    def test_duplicate_words_first_astro_match_and_record_denominator(self):
        keywords = [{"word": "art", "weight": 4}, {"word": "ART", "weight": 8},
                    {"word": " art", "weight": 2}, {"word": "other", "weight": 10}]
        self.assertEqual(literal_matches(["ART", "art", " art", "missing"], keywords), [4, 4, 2, 0])
        self.assertEqual(literal_score(["ART", "art", " art", "missing"], keywords), 2.5)

    def test_keywords_keep_accents_and_no_identity_normalization(self):
        self.assertEqual(literal_matches(["SŒUR", "soeur", "ÉMOTIVITÉ", "emotivite"],
                                        [{"word": "sœur", "weight": 2}, {"word": "émotivité", "weight": 3}]),
                         [2, 0, 3, 0])

    def test_keyword_source_whitespace_preserved_summary_number_excluded(self):
        self.assertEqual(traits_from_column([["header"], [" trait "], [""], [" "], [None], [3]], 0, 2),
                         [{"row": 2, "word": " trait "}, {"row": 4, "word": " "}])

    def test_explicit_name_alias_and_unicode_variation_are_only_for_joins(self):
        self.assertEqual(identity_key("Assange, Julian"), identity_key("Assange, Julien "))
        self.assertEqual(identity_key("Wałęsa, Lech"), identity_key("Walesa, Lech"))
        self.assertNotEqual(identity_key("Nascimento, Milton"), identity_key("Nascimento, Edson"))

    def test_empty_chart_is_unavailable(self):
        with self.assertRaises(ValueError):
            literal_score(["art"], [])


if __name__ == "__main__":
    unittest.main()
