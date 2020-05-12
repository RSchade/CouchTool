import unittest
import couchtool.designbuilder as ddocbuilder

class Test_DesignBuilder(unittest.TestCase):

    def test_add_to_design_doc(self):
        testddoc = {}
        ddocbuilder.add_to_design_doc(testddoc, "testcategory", "name1", "content")
        self.assertEqual(list(testddoc.keys()), ["testcategory"])
        self.assertEqual(list(testddoc["testcategory"].keys()), ["name1"])
        self.assertEqual(testddoc["testcategory"]["name1"], "content")
        ddocbuilder.add_to_design_doc(testddoc, "testcategory", "name2", "content")
        self.assertEqual(testddoc["testcategory"]["name2"], "content")
        ddocbuilder.add_to_design_doc(testddoc, "testcategory2", "name2", "content")
        self.assertEqual(testddoc["testcategory2"]["name2"], "content")

if __name__ == "__main__":
    unittest.main()
