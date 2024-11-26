import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

/**
 * Utility function that combines clsx and tailwind-merge to handle className merging
 * - Processes conditional classes using clsx
 * - Deduplicates and resolves Tailwind class conflicts using tailwind-merge
 * 
 * @param inputs - Class values to be merged (strings, objects, arrays)
 * @returns Merged and deduplicated className string
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs))
}
