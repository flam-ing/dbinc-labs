import { describe, expect, test } from 'vitest'
import { addEntry } from './entries.js'

describe('addEntry', () => {
  test('등록한_글이_목록_맨_뒤에_붙는다', () => {
    // 준비
    const before = [{ name: '민지', message: '첫 글이에요' }]

    // 실행
    const after = addEntry(before, '준호', '오늘 교육 재밌어요')

    // 확인
    expect(after).toEqual([
      { name: '민지', message: '첫 글이에요' },
      { name: '준호', message: '오늘 교육 재밌어요' },
    ])
  })
})
