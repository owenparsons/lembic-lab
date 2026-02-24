/**
 * Client-side cell name generation (for optimistic UI).
 * The backend is the source of truth for names.
 */

const ADJECTIVES = [
  "amber", "azure", "bold", "bright", "calm", "cedar", "clean", "clear",
  "cool", "coral", "crisp", "dark", "deep", "eager", "fair", "fast",
  "fine", "fresh", "frost", "glad", "gold", "grand", "green", "happy",
];

const NOUNS = [
  "arch", "atlas", "aura", "badge", "basin", "beam", "bloom", "bolt",
  "bower", "brick", "brook", "cairn", "cape", "chain", "charm", "chord",
  "cliff", "cloud", "coast", "coil", "coral", "craft", "crane", "creek",
];

export function generateCellName(): string {
  const adj = ADJECTIVES[Math.floor(Math.random() * ADJECTIVES.length)]!;
  const noun = NOUNS[Math.floor(Math.random() * NOUNS.length)]!;
  return `${adj}-${noun}`;
}
