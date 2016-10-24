import os
import sys
from unittest import TestCase


from boltons import ioutils

# Python2/3 compat
if sys.version_info[0] == 3:
    text_type = str
    binary_type = bytes
else:
    text_type = unicode
    binary_type = str


class AssertionsMixin(object):

    def assertIsNone(self, item, msg=None):
        self.assertTrue(item is None, msg)


class BaseTestMixin(object):
    """
    A set of tests that work the same for SpooledBtyesIO and SpooledStringIO
    """

    def test_getvalue_norollover(self):
        """Make sure getvalue function works with in-memory flo"""
        self.spooled_flo.write(self.test_str)
        self.assertEqual(self.spooled_flo.getvalue(), self.test_str)

    def test_getvalue_rollover(self):
        """Make sure getvalue function works with on-disk flo"""
        self.spooled_flo.write(self.test_str)
        self.assertFalse(self.spooled_flo._rolled)
        self.spooled_flo.rollover()
        self.assertEqual(self.spooled_flo.getvalue(), self.test_str)
        self.assertTrue(self.spooled_flo._rolled)

    def test_truncate_noargs_norollover(self):
        """Test truncating with no args with in-memory flo"""
        self.spooled_flo.write(self.test_str)
        self.spooled_flo.seek(10)
        self.spooled_flo.truncate()
        self.assertEqual(self.spooled_flo.getvalue(), self.test_str[:10])

    def test_truncate_noargs_rollover(self):
        """Test truncating with no args with on-disk flo"""
        self.spooled_flo.write(self.test_str)
        self.spooled_flo.seek(10)
        self.spooled_flo.rollover()
        self.spooled_flo.truncate()
        self.assertEqual(self.spooled_flo.getvalue(), self.test_str[:10])

    def test_truncate_with_args_norollover(self):
        """Test truncating to a value with in-memory flo"""
        self.spooled_flo.write(self.test_str)
        self.spooled_flo.seek(5)
        self.spooled_flo.truncate(10)
        self.assertEqual(self.spooled_flo.getvalue(), self.test_str[:10])
        self.assertEqual(self.spooled_flo.tell(), 5)

    def test_truncate_with_args_rollover(self):
        """Test truncating to a value with on-disk flo"""
        self.spooled_flo.write(self.test_str)
        self.spooled_flo.seek(5)
        self.spooled_flo.rollover()
        self.spooled_flo.truncate(10)
        self.assertEqual(self.spooled_flo.getvalue(), self.test_str[:10])
        self.assertEqual(self.spooled_flo.tell(), 5)

    def test_type_error_too_many_args(self):
        """Make sure TypeError raised if too many args passed to truncate"""
        self.spooled_flo.write(self.test_str)
        self.assertRaises(TypeError, self.spooled_flo.truncate, 0, 10)

    def test_io_error_negative_truncate(self):
        """Make sure IOError raised trying to truncate with negative value"""
        self.spooled_flo.write(self.test_str)
        self.assertRaises(IOError, self.spooled_flo.truncate, -1)

    def test_compare_different_instances(self):
        """Make sure two different instance types are not considered equal"""
        a = ioutils.SpooledBytesIO()
        a.write(binary_type(b"I am equal!"))
        b = ioutils.SpooledStringIO()
        b.write(text_type("I am equal!"))
        self.assertNotEqual(a, b)

    def test_compare_unequal_instances(self):
        """Comparisons of non-SpooledIOBase classes should fail"""
        self.assertNotEqual("Bummer dude", self.spooled_flo)

    def test_set_softspace_attribute(self):
        """Ensure softspace attribute can be retrieved and set"""
        self.spooled_flo.softspace = True
        self.assertTrue(self.spooled_flo.softspace)

    def test_set_softspace_attribute_rolled(self):
        """Ensure softspace attribute can be retrieved and set if rolled"""
        self.spooled_flo.softspace = True
        self.assertTrue(self.spooled_flo.softspace)
        self.spooled_flo.rollover()
        self.spooled_flo.softspace = True
        self.assertTrue(self.spooled_flo.softspace)

    def test_iter(self):
        """Make sure iter works as expected"""
        self.spooled_flo.write(self.test_str)
        self.spooled_flo.seek(0)
        self.assertEqual([x for x in self.spooled_flo][0], self.test_str)
        self.assertEqual([x for x in self.spooled_flo][0], self.data_type())

    def test_buf_property(self):
        """'buf' property returns the same value as getvalue()"""
        self.assertEqual(self.spooled_flo.buf, self.spooled_flo.getvalue())

    def test_pos_property(self):
        """'pos' property returns the same value as tell()"""
        self.assertEqual(self.spooled_flo.pos, self.spooled_flo.tell())

    def test_closed_property(self):
        """'closed' property works as expected"""
        self.assertFalse(self.spooled_flo.closed)
        self.spooled_flo.close()
        self.assertTrue(self.spooled_flo.closed)

    def test_readline(self):
        """Make readline returns expected values"""
        self.spooled_flo.write(self.test_str_lines)
        self.spooled_flo.seek(0)
        self.assertEqual(self.spooled_flo.readline().rstrip(self.linesep),
                         self.test_str_lines.split(self.linesep)[0])

    def test_readlines(self):
        """Make sure readlines returns expected values"""
        self.spooled_flo.write(self.test_str_lines)
        self.spooled_flo.seek(0)
        self.assertEqual(
            [x.rstrip(self.linesep) for x in self.spooled_flo.readlines()],
            self.test_str_lines.split(self.linesep)
        )

    def test_next(self):
        """Make next returns expected values"""
        self.spooled_flo.write(self.test_str_lines)
        self.spooled_flo.seek(0)
        self.assertEqual(self.spooled_flo.next().rstrip(self.linesep),
                         self.test_str_lines.split(self.linesep)[0])

    def test_isatty(self):
        """Make sure we can check if the value is a tty"""
        # This should simply not fail
        self.assertTrue(self.spooled_flo.isatty() is True or
                        self.spooled_flo.isatty() is False)


class TestSpooledBytesIO(TestCase, BaseTestMixin, AssertionsMixin):
    linesep = os.linesep.encode('ascii')

    def setUp(self):
        self.spooled_flo = ioutils.SpooledBytesIO()
        self.test_str = b"Armado en los EE, UU. para S. P. Richards co.,"
        self.test_str_lines = (
            "Text with:{0}newlines!".format(os.linesep).encode('ascii')
        )
        self.data_type = binary_type

    def test_compare_not_equal_instances(self):
        """Make sure instances with different values fail == check."""
        a = ioutils.SpooledBytesIO()
        a.write(b"I am a!")
        b = ioutils.SpooledBytesIO()
        b.write(b"I am b!")
        self.assertNotEqual(a, b)

    def test_compare_two_equal_instances(self):
        """Make sure we can compare instances"""
        a = ioutils.SpooledBytesIO()
        a.write(b"I am equal!")
        b = ioutils.SpooledBytesIO()
        b.write(b"I am equal!")
        self.assertEqual(a, b)

    def test_auto_rollover(self):
        """Make sure file rolls over to disk after max_size reached"""
        tmp = ioutils.SpooledBytesIO(max_size=10)
        tmp.write(b"The quick brown fox jumped over the lazy dogs.")
        self.assertTrue(tmp._rolled)

    def test_use_as_context_mgr(self):
        """Make sure SpooledBytesIO can be used as a context manager"""
        test_str = b"Armado en los EE, UU. para S. P. Richards co.,"
        with ioutils.SpooledBytesIO() as f:
            f.write(test_str)
            self.assertEqual(f.getvalue(), test_str)

    def test_len_no_rollover(self):
        """Make sure len works with in-memory flo"""
        self.spooled_flo.write(self.test_str)
        self.assertEqual(self.spooled_flo.len, len(self.test_str))
        self.assertEqual(len(self.spooled_flo), len(self.test_str))

    def test_len_rollover(self):
        """Make sure len works with on-disk flo"""
        self.spooled_flo.write(self.test_str)
        self.spooled_flo.rollover()
        self.assertEqual(self.spooled_flo.len, len(self.test_str))
        self.assertEqual(len(self.spooled_flo), len(self.test_str))

    def test_invalid_type(self):
        """Ensure TypeError raised when writing unicode to SpooledBytesIO"""
        self.assertRaises(TypeError, self.spooled_flo.write, u"hi")

    def test_flush_after_rollover(self):
        """Make sure we can flush before and after rolling to a real file"""
        self.spooled_flo.write(self.test_str)
        self.assertIsNone(self.spooled_flo.flush())
        self.spooled_flo.rollover()
        self.assertIsNone(self.spooled_flo.flush())


class TestSpooledStringIO(TestCase, BaseTestMixin, AssertionsMixin):
    linesep = os.linesep

    def setUp(self):
        self.spooled_flo = ioutils.SpooledStringIO()
        self.test_str = u"Remember kids, always use an emdash: '\u2014'"
        self.test_str_lines = u"Text with\u2014{0}newlines!".format(os.linesep)
        self.data_type = text_type

    def test_compare_not_equal_instances(self):
        """Make sure instances with different values fail == check."""
        a = ioutils.SpooledStringIO()
        a.write(u"I am a!")
        b = ioutils.SpooledStringIO()
        b.write(u"I am b!")
        self.assertNotEqual(a, b)

    def test_compare_two_equal_instances(self):
        """Make sure we can compare instances"""
        a = ioutils.SpooledStringIO()
        a.write(u"I am equal!")
        b = ioutils.SpooledStringIO()
        b.write(u"I am equal!")
        self.assertEqual(a, b)

    def test_auto_rollover(self):
        """Make sure file rolls over to disk after max_size reached"""
        tmp = ioutils.SpooledStringIO(max_size=10)
        tmp.write(u"The quick brown fox jumped over the lazy dogs.")
        self.assertTrue(tmp._rolled)

    def test_use_as_context_mgr(self):
        """Make sure SpooledStringIO can be used as a context manager"""
        test_str = u"Armado en los EE, UU. para S. P. Richards co.,"
        with ioutils.SpooledStringIO() as f:
            f.write(test_str)
            self.assertEqual(f.getvalue(), test_str)

    def test_len_no_rollover(self):
        """Make sure len property works with in-memory flo"""
        self.spooled_flo.write(self.test_str)
        self.assertEqual(self.spooled_flo.len,
                         len(self.test_str.encode('utf-8')))

    def test_len_rollover(self):
        """Make sure len propery works with on-disk flo"""
        self.spooled_flo.write(self.test_str)
        self.spooled_flo.rollover()
        self.assertEqual(self.spooled_flo.len,
                         len(self.test_str.encode('utf-8')))

    def test_invalid_type(self):
        """Ensure TypeError raised when writing bytes to SpooledStringIO"""
        self.assertRaises(TypeError, self.spooled_flo.write, b"hi")
