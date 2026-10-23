"""카페 포인트 마감 테스트. 임시 폴더에서 cafe.py를 실제로 돌려서 결과 파일을 봐요.

실행: python -m unittest (Mac은 python3 -m unittest)
지금 있는 테스트는 모두 통과해요. 그래도 이슈 네 개의 버그는 그대로 있어요.
"""
import unittest

from tests.cafe_runner import run_cafe


class CafeTest(unittest.TestCase):
    def test_마감을_돌리면_보고서가_생긴다(self):
        result = run_cafe(["2026-10-17,M004,5500,0", "2026-10-17,,6500,0"])
        self.assertEqual(result.code, 0, result.output)
        self.assertIn("주문 수: 2건", result.report)

    def test_일반_회원은_결제_금액의_1퍼센트가_쌓인다(self):
        result = run_cafe(["2026-10-17,M004,5500,0"])
        self.assertEqual(result.members["M004"]["points"], "1555")

    def test_포인트는_1000점보다_적으면_못_쓴다(self):
        result = run_cafe(["2026-10-17,M004,5500,500"])
        self.assertIn("결제 금액: 5500 원", result.output)


if __name__ == "__main__":
    unittest.main()
