import os
import tempfile
import unittest

from anki.collection import Collection

from addon.ankiops import collection as ops
from addon.ankiops import notetypes


class CollectionTestBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.col = Collection(os.path.join(self.tmp.name, "c.anki2"))
        self.addCleanup(self.tmp.cleanup)
        self.addCleanup(self.col.close)


class NotetypeTest(CollectionTestBase):
    def test_created_once(self):
        a = notetypes.ensure_notetype(self.col, "basic")
        b = notetypes.ensure_notetype(self.col, "basic")
        self.assertEqual(a, b)
        names = [n.name for n in self.col.models.all_names_and_ids()]
        self.assertEqual(names.count("AutoCards Basic"), 1)

    def test_reversed_has_two_templates(self):
        nt = self.col.models.get(notetypes.ensure_notetype(self.col, "reversed"))
        self.assertEqual(len(nt["tmpls"]), 2)

    def test_cloze_is_cloze_type(self):
        nt = self.col.models.get(notetypes.ensure_notetype(self.col, "cloze"))
        self.assertEqual(nt["type"], 1)
        self.assertEqual([f["name"] for f in nt["flds"]][:2], ["Text", "Back Extra"])


class OpsTest(CollectionTestBase):
    def test_html_escaped_and_newlines(self):
        self.assertEqual(ops.to_html("a <b> & c\nd"), "a &lt;b&gt; &amp; c<br>d")

    def test_cloze_preserved(self):
        self.assertEqual(ops.to_html("The {{c1::cat}} sat"), "The {{c1::cat}} sat")

    def test_add_basic_card_with_audio(self):
        name = ops.write_audio(self.col, b"ID3fake", "abc")
        nid = ops.add_card(self.col, "Lang::Daily", "basic",
                           {"front": "Hi <there>", "back": "Oi", "context": "greeting"},
                           name, "front", ["autocards"])
        note = self.col.get_note(nid)
        self.assertEqual(note["Front"], "Hi &lt;there&gt;")
        self.assertEqual(note["FrontAudio"], f"[sound:{name}]")
        self.assertEqual(note["BackAudio"], "")
        self.assertEqual(note["Context"], "greeting")
        self.assertIn("autocards", note.tags)
        self.assertEqual(self.col.decks.name(note.cards()[0].did), "Lang::Daily")
        self.assertTrue(os.path.exists(os.path.join(self.col.media.dir(), name)))

    def test_add_cloze_card(self):
        nid = ops.add_card(self.col, "C", "cloze", {"text": "The {{c1::cat}}", "back_extra": "x"},
                           None, "back", [])
        self.assertEqual(len(self.col.get_note(nid).cards()), 1)

    def test_reversed_creates_two_cards(self):
        nid = ops.add_card(self.col, "R", "reversed", {"front": "a", "back": "b"}, None, "front", [])
        self.assertEqual(len(self.col.get_note(nid).cards()), 2)

    def test_deleted_deck_is_recreated(self):
        did = self.col.decks.id("Gone")
        self.col.decks.remove([did])
        nid = ops.add_card(self.col, "Gone", "basic", {"front": "a", "back": "b"}, None, "front", [])
        self.assertEqual(self.col.decks.name(self.col.get_note(nid).cards()[0].did), "Gone")

    def test_overdue_zero_in_new_collection(self):
        ops.add_card(self.col, "D", "basic", {"front": "a", "back": "b"}, None, "front", [])
        self.assertEqual(ops.overdue_count(self.col, "D"), 0)

    def test_existing_fronts_include_other_notetypes_newest_first(self):
        basic = self.col.models.by_name("Basic")
        n = self.col.new_note(basic)
        n.fields[0] = "old basic"
        self.col.add_note(n, self.col.decks.id("E"))
        ops.add_card(self.col, "E", "basic", {"front": "new auto", "back": "b"}, None, "front", [])
        self.assertEqual(ops.existing_fronts(self.col, "E"), ["new auto", "old basic"])

    def test_existing_fronts_deck_with_special_chars(self):
        ops.add_card(self.col, "My_Deck*", "basic", {"front": "x", "back": "y"}, None, "front", [])
        ops.add_card(self.col, "MyXDeckZ", "basic", {"front": "other", "back": "y"}, None, "front", [])
        self.assertEqual(ops.existing_fronts(self.col, "My_Deck*"), ["x"])

    def test_existing_fronts_missing_deck(self):
        self.assertEqual(ops.existing_fronts(self.col, "Nope"), [])


if __name__ == "__main__":
    unittest.main()


class ApprovalQueueTest(CollectionTestBase):
    def add_pending(self, front="a"):
        return ops.add_card(self.col, "Q", "basic", {"front": front, "back": "b"}, None, "front", [], pending=True)

    def test_pending_is_suspended_and_queued(self):
        nid = self.add_pending()
        self.assertEqual(ops.pending_notes(self.col), [nid])
        self.assertTrue(all(c.queue == -1 for c in self.col.get_note(nid).cards()))

    def test_manually_unsuspended_stays_in_queue(self):
        nid = self.add_pending()
        self.col.sched.unsuspend_cards(self.col.get_note(nid).card_ids())
        self.assertEqual(ops.pending_notes(self.col), [nid])

    def test_accept_unsuspends_and_leaves_queue(self):
        nid = self.add_pending()
        original, final = ops.accept_note(self.col, nid, None)
        self.assertEqual(ops.pending_notes(self.col), [])
        self.assertTrue(all(c.queue != -1 for c in self.col.get_note(nid).cards()))
        self.assertEqual(original, final)

    def test_edit_and_accept(self):
        nid = self.add_pending()
        original, final = ops.accept_note(self.col, nid, {"Back": "edited"})
        self.assertEqual((original["Back"], final["Back"]), ("b", "edited"))
        self.assertEqual(self.col.get_note(nid)["Back"], "edited")

    def test_discard_removes_note(self):
        nid = self.add_pending()
        ops.discard_note(self.col, nid)
        self.assertEqual(ops.pending_notes(self.col), [])
        self.assertEqual(self.col.find_notes(f"nid:{nid}"), [])

    def test_note_deleted_elsewhere_leaves_queue(self):
        nid = self.add_pending()
        self.col.remove_notes([nid])
        self.assertEqual(ops.pending_notes(self.col), [])

    def test_queue_oldest_first(self):
        a, b = self.add_pending("a"), self.add_pending("b")
        self.assertEqual(ops.pending_notes(self.col), [a, b])
