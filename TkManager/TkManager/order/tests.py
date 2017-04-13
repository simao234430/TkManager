from django.test import TestCase
from TkManager.order.generator import *

class GeneratorTest(TestCase):

    def setUp(self):
        self.gen = Generator()
        pass

    def tearDown(self):
        pass

    def test_1(self):
        #print self.gen.random_string(5)
        self.gen.generate_apply()
        print "test_1 test done"

    def testsum(self):
        self.assertEqual(1+1, 2, 'test sum success')

if __name__ =='__main__':
    unittest.main()
