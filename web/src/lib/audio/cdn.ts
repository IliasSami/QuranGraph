/**
 * Audio CDN resilience and URL management for QuranGraph.
 * Provides primary and mirror EveryAyah endpoints, reciter fallbacks,
 * and audio candidate resolution.
 */

export interface ReciterInfo {
  id: string;
  name: string;
  bitrate: string;
  style?: string;
}

export const RECITERS: Record<string, ReciterInfo> = {
  "Alafasy_64kbps": { id: "Alafasy_64kbps", name: "Mishary Rashid Alafasy", bitrate: "64kbps" },
  "Husary_128kbps": { id: "Husary_128kbps", name: "Mahmoud Khalil Al-Husary", bitrate: "128kbps" },
  "Husary_Muallim_128kbps": { id: "Husary_Muallim_128kbps", name: "Al-Husary (Teacher)", bitrate: "128kbps" },
  "Minshawy_Murattal_128kbps": { id: "Minshawy_Murattal_128kbps", name: "Mohamed Siddiq El-Minshawi", bitrate: "128kbps" },
  "Abdurrahmaan_As-Sudais_192kbps": { id: "Abdurrahmaan_As-Sudais_192kbps", name: "Abdur-Rahman As-Sudais", bitrate: "192kbps" }
};

export const DEFAULT_RECITER = "Alafasy_64kbps";
export const ENGLISH_RECITER = "Ibrahim_Walk_192kbps";

export const EVERYAYAH_PRIMARY_HOST = "https://everyayah.com";
export const EVERYAYAH_MIRROR_HOST = "https://media.everyayah.com";

export function formatAyahKey(surah: number, ayah: number): string {
  const sStr = String(surah).padStart(3, "0");
  const aStr = String(ayah).padStart(3, "0");
  return `${sStr}${aStr}`;
}

/**
 * Returns prioritized array of audio stream URLs with mirror fallbacks.
 * Order:
 * 1. Primary host with selected reciter
 * 2. Mirror host with selected reciter
 * 3. Primary host with default reciter (if selected is different)
 * 4. Mirror host with default reciter (if selected is different)
 */
export function getAyahAudioCandidates(
  surah: number,
  ayah: number,
  reciter: string = DEFAULT_RECITER
): string[] {
  const key = formatAyahKey(surah, ayah);
  const candidates: string[] = [
    `${EVERYAYAH_PRIMARY_HOST}/data/${reciter}/${key}.mp3`,
    `${EVERYAYAH_MIRROR_HOST}/data/${reciter}/${key}.mp3`
  ];

  if (reciter !== DEFAULT_RECITER) {
    candidates.push(
      `${EVERYAYAH_PRIMARY_HOST}/data/${DEFAULT_RECITER}/${key}.mp3`,
      `${EVERYAYAH_MIRROR_HOST}/data/${DEFAULT_RECITER}/${key}.mp3`
    );
  }

  return candidates;
}

/**
 * Returns prioritized English recitation URLs with mirror fallback.
 */
export function getEnglishAudioCandidates(surah: number, ayah: number): string[] {
  const key = formatAyahKey(surah, ayah);
  return [
    `${EVERYAYAH_PRIMARY_HOST}/data/${ENGLISH_RECITER}/${key}.mp3`,
    `${EVERYAYAH_MIRROR_HOST}/data/${ENGLISH_RECITER}/${key}.mp3`
  ];
}

/**
 * Returns the Bangla neural audio path for a given surah.
 */
export function getBanglaAudioUrl(surah: number): string {
  const sStr = String(surah).padStart(3, "0");
  return `/audio/bn/${sStr}.mp3`;
}

/**
 * Controller pattern for safely managing HTML5 Audio play/pause state
 * and preventing race conditions or unhandled AbortError rejections.
 */
export class SafeAudioController {
  private isPlayPending = false;
  private desiredPlaying = false;

  get isPending(): boolean {
    return this.isPlayPending;
  }

  get isPlaying(): boolean {
    return this.desiredPlaying;
  }

  setDesiredState(playing: boolean): void {
    this.desiredPlaying = playing;
  }

  async play(audio: { play: () => Promise<void>; pause: () => void }): Promise<boolean> {
    this.desiredPlaying = true;
    this.isPlayPending = true;

    try {
      await audio.play();
      this.isPlayPending = false;
      if (!this.desiredPlaying) {
        audio.pause();
        return false;
      }
      return true;
    } catch (err: any) {
      this.isPlayPending = false;
      if (err && err.name === "AbortError") {
        return false;
      }
      throw err;
    }
  }

  pause(audio: { pause: () => void }): void {
    this.desiredPlaying = false;
    audio.pause();
  }
}
