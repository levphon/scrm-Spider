import unittest


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def get_list(self):
        print(1)

    def get_info(self):
        print(2)

    def save_excel(self):
        print(3)

    def save_database(self):
        print(4)


if __name__ == '__main__':
    unittest.main()
