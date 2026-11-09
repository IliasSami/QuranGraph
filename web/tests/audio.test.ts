import { test } from "node:test";
import assert from "node:assert/strict";
import {
  formatAyahKey,
  getAyahAudioCandidates,
  getEnglishAudioCandidates,
  getBanglaAudioUrl,
  SafeAudioController,
  DEFAULT_RECITER,
  EVERYAYAH_PRIMARY_HOST,
  EVERYAYAH_MIRROR_HOST
} from "../src/lib/audio/cdn.ts";

test("Audio CDN: Ayah Key Formatting", () => {
  assert.equal(formatAyahKey(1, 1), "001001");
  assert.equal(formatAyahKey(2, 255), "002255");
  assert.equal(formatAyahKey(114, 6), "114006");
});

test("Audio CDN: Default Reciter Candidates", () => {
  const candidates = getAyahAudioCandidates(1, 1, DEFAULT_RECITER);
  assert.equal(candidates.length, 2);
  assert.equal(candidates[0], `${EVERYAYAH_PRIMARY_HOST}/data/Alafasy_64kbps/001001.mp3`);
  assert.equal(candidates[1], `${EVERYAYAH_MIRROR_HOST}/data/Alafasy_64kbps/001001.mp3`);
});

test("Audio CDN: Non-Default Reciter Fallback Cascade", () => {
  const candidates = getAyahAudioCandidates(2, 255, "Husary_128kbps");
  // Expected order:
  // 1. Husary Primary
  // 2. Husary Mirror
  // 3. Alafasy (Default) Primary
  // 4. Alafasy (Default) Mirror
  assert.equal(candidates.length, 4);
  assert.equal(candidates[0], `${EVERYAYAH_PRIMARY_HOST}/data/Husary_128kbps/002255.mp3`);
  assert.equal(candidates[1], `${EVERYAYAH_MIRROR_HOST}/data/Husary_128kbps/002255.mp3`);
  assert.equal(candidates[2], `${EVERYAYAH_PRIMARY_HOST}/data/Alafasy_64kbps/002255.mp3`);
  assert.equal(candidates[3], `${EVERYAYAH_MIRROR_HOST}/data/Alafasy_64kbps/002255.mp3`);
});

test("Audio CDN: English Audio Candidates", () => {
  const candidates = getEnglishAudioCandidates(36, 1);
  assert.equal(candidates.length, 2);
  assert.equal(candidates[0], `${EVERYAYAH_PRIMARY_HOST}/data/Ibrahim_Walk_192kbps/036001.mp3`);
  assert.equal(candidates[1], `${EVERYAYAH_MIRROR_HOST}/data/Ibrahim_Walk_192kbps/036001.mp3`);
});

test("Audio CDN: Bangla Neural Audio URL", () => {
  assert.equal(getBanglaAudioUrl(1), "/audio/bn/001.mp3");
  assert.equal(getBanglaAudioUrl(114), "/audio/bn/114.mp3");
});

test("SafeAudioController: Clean Play and Pause State Transition", async () => {
  const controller = new SafeAudioController();
  let paused = false;

  const mockAudio = {
    play: async () => {
      // Simulate microtask async
      await new Promise((r) => setTimeout(r, 5));
    },
    pause: () => {
      paused = true;
    }
  };

  const playPromise = controller.play(mockAudio);
  assert.equal(controller.isPending, true);
  assert.equal(controller.isPlaying, true);

  const played = await playPromise;
  assert.equal(played, true);
  assert.equal(controller.isPending, false);
  assert.equal(controller.isPlaying, true);

  controller.pause(mockAudio);
  assert.equal(controller.isPlaying, false);
  assert.equal(paused, true);
});

test("SafeAudioController: Rapid Interruption AbortError Suppression", async () => {
  const controller = new SafeAudioController();
  let paused = false;

  const mockAudio = {
    play: async () => {
      await new Promise((r) => setTimeout(r, 10));
      if (!controller.isPlaying) {
        const err = new Error("The play() request was interrupted by a call to pause().");
        err.name = "AbortError";
        throw err;
      }
    },
    pause: () => {
      paused = true;
    }
  };

  const playPromise = controller.play(mockAudio);
  assert.equal(controller.isPlaying, true);

  // User immediately pauses while play is pending
  controller.pause(mockAudio);
  assert.equal(controller.isPlaying, false);
  assert.equal(paused, true);

  // Promise should resolve false without throwing unhandled error
  const res = await playPromise;
  assert.equal(res, false);
  assert.equal(controller.isPending, false);
});
