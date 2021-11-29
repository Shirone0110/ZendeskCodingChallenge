import unittest
from unittest.mock import patch
import viewTickets
from io import StringIO
import pandas as pd
from pandas.testing import assert_frame_equal

class Test(unittest.TestCase):
    program = viewTickets.TicketViewer()

    @patch("sys.stdin", StringIO("a\na\na"))
    def test_get_credentials(self):
        self.assertEqual(self.program.get_credentials(), False)
    
    @patch("sys.stdin", StringIO("1\n3"))
    def test_view_single(self):
        d = {'id': [1, 2], 'type': ['None', 'None'], 
             'subject': ['test1', 'test2'], 'status': ['open', 'closed'],
             'requester_id': [1000, 1200]}
        df = pd.DataFrame(data = d)
        df = df.set_index('id')
        error = "Sorry, there was no ticket with that id number\n"
        #assert viewTickets.view_single(df).equals(df.loc[[1]]) == True
        assert_frame_equal(self.program.view_single(df), df.loc[[1]])
        self.assertEqual(self.program.view_single(df), error)

    @patch("sys.stdin", StringIO("p\nn\n1\np\nn\n2\n3\n4\n1"))
    def test_valid_input(self):
        self.assertEqual(self.program.get_valid_input(0, 0), '1')
        self.assertEqual(self.program.get_valid_input(1, 0), 'p')
        self.assertEqual(self.program.get_valid_input(0, 1), 'n')
        self.assertEqual(self.program.get_valid_input(0, 1), '2')
        self.assertEqual(self.program.get_valid_input(1, 1), '3')
        self.assertEqual(self.program.get_valid_input(1, 0), '1')

    def test_create_df(self):
        dict = [{'id': 1, 'type': 'incident', 'subject': 'test',
                 'status': 'open', 'requester_id': 100},
                {'id': 2, 'type': 'None', 'subject': 'test2',
                 'status': 'closed', 'requester_id': 404}]
        d = {'id': [1, 2], 'type': ['incident', 'None'], 
             'subject': ['test', 'test2'], 'status': ['open', 'closed'],
             'requester_id': [100, 404]}
        df = pd.DataFrame(data = d)
        df = df.set_index('id')
        test_df = self.program.create_df(dict)
        assert_frame_equal(test_df, df)

if __name__ == "__main__":
    unittest.main()