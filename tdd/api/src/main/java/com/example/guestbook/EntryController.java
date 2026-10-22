package com.example.guestbook;

import java.util.ArrayList;
import java.util.List;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/entries")
public class EntryController {

	// 방명록 글 한 개
	public record Entry(String name, String message) {}

	// 연습용이라 DB 대신 메모리에 담아요.
	private final List<Entry> entries = new ArrayList<>();

	@PostMapping
	public Entry add(@RequestBody Entry request) {
		// 저장하기 전에 개인정보를 가려요.
		Entry saved = new Entry(request.name(), PrivacyMasker.mask(request.message()));
		entries.add(saved);
		return saved;
	}

	@GetMapping
	public List<Entry> list() {
		return List.copyOf(entries);
	}
}
