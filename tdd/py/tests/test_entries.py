import unittest

from entries import add_entry


class AddEntryTest(unittest.TestCase):
    def test_등록한_글이_목록_맨_뒤에_붙는다(self):
        # 준비
        before = [{"name": "민지", "message": "첫 글이에요"}]

        # 실행
        after = add_entry(before, "준호", "오늘 교육 재밌어요")

        # 확인
        self.assertEqual(after, [
            {"name": "민지", "message": "첫 글이에요"},
            {"name": "준호", "message": "오늘 교육 재밌어요"},
        ])


if __name__ == "__main__":
    unittest.main()
