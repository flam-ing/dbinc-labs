'use strict';
/**
 * Outbox writer
 * 2022-02 Kim Doyun
 *
 * The send gateway reads outbox.json every minute and sends messages whose sendAt has passed.
 * Keep the order: sendAt, notice, channel, to.
 */
const fs = require('fs/promises');
const path = require('path');

const CHANNEL_ORDER = { messenger: 1, mail: 2, sms: 3 };

class OutboxWriter {
  constructor(dir) {
    this.dir = dir;
  }

  sort(messages) {
    return messages.slice().sort((a, b) => {
      if (a.sendAt !== b.sendAt) return a.sendAt < b.sendAt ? -1 : 1;
      if (a.notice !== b.notice) return a.notice < b.notice ? -1 : 1;
      if (a.channel !== b.channel) return CHANNEL_ORDER[a.channel] - CHANNEL_ORDER[b.channel];
      if (a.to !== b.to) return a.to < b.to ? -1 : 1;
      return 0;
    });
  }

  async write(messages) {
    const list = this.sort(messages);
    list.forEach((m, i) => {
      m.seq = i + 1;
    });
    await fs.mkdir(this.dir, { recursive: true });
    await fs.writeFile(path.join(this.dir, 'outbox.json'), JSON.stringify(list, null, 2) + '\n', 'utf8');
    return list.length;
  }
}

module.exports = OutboxWriter;
