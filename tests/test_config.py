import tempfile
import unittest
from datetime import datetime
from pathlib import Path

import config
from classes import Squad, SquadMember, SquadMemberStatus, UserInfo


class ConfigPersistenceTests(unittest.TestCase):
    def test_save_and_load_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            base = Path(tmp_dir)
            config.BASE_DIR = base
            config.USERS_LOCATION = base / 'users.json'
            config.SQUADS_LOCATION = base / 'squads.json'
            config.EVENTS_DATA_LOCATION = base / 'events_data.json'

            users = {
                100: UserInfo(bug_counts=7, squad_uuid='abc12345', screen_count=2),
                200: UserInfo(bug_counts=3, screen_count=1),
            }
            status = SquadMemberStatus(can_rename=True, can_kick=True, can_answer_to_join_requests=True)
            squads = {
                'abc12345': Squad('Test Squad', 100, [SquadMember(100, status), SquadMember(999, status)])
            }
            events_data = {'invasion': datetime(2026, 1, 1, 10, 0, 0)}

            ok = config.save(config.Data(users=users, squads=squads, events_data=events_data))
            self.assertTrue(ok)

            loaded = config.load()
            self.assertIn(100, loaded.users)
            self.assertEqual(loaded.users[100].bug_counts, 7)
            self.assertEqual(len(loaded.squads['abc12345'].members), 1)
            self.assertIn('invasion', loaded.events_data)


if __name__ == '__main__':
    unittest.main()
