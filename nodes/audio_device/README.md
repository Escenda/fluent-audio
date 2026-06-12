# Audio Device

CPAL-backed microphone and speaker hardware interaction belongs here.

The hardware callback side must own its queue or ring buffer. DORA is the
process boundary outside that low-level timing loop.
