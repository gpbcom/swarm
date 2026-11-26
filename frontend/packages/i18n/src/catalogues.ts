import de from "./messages/de.json";
import en from "./messages/en.json";
import es from "./messages/es.json";
import fr from "./messages/fr.json";
import type { Language } from "./languages.ts";

export type MessageId = keyof typeof en;

export const MESSAGES: Record<Language, Record<MessageId, string>> = { en, fr, de, es };
