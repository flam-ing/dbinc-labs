package com.example.guestbook;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;

class EntryControllerTest {

	@Test
	void 등록한_글이_목록에_나온다() {
		// 준비
		EntryController controller = new EntryController();

		// 실행
		controller.add(new EntryController.Entry("민지", "오늘 교육 재밌어요"));

		// 확인
		assertThat(controller.list())
			.containsExactly(new EntryController.Entry("민지", "오늘 교육 재밌어요"));
	}
}
