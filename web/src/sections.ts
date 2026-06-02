// SCORES.md domain section names, for grouping the score picker.
export const SECTION_NAMES: Record<number, string> = {
  1: "General ICU severity / mortality",
  2: "Early warning / track-and-trigger",
  3: "Sepsis-specific",
  4: "Neurologic / neurocritical care",
  5: "Respiratory / ARDS / ventilation",
  6: "Cardiovascular / shock",
  7: "Hepatic / liver failure",
  8: "Renal / acute kidney injury",
  9: "Coagulation / hematology",
  10: "Trauma",
  11: "Burns",
  12: "Sedation / pain / delirium",
  13: "Withdrawal syndromes",
  14: "Nutrition",
  15: "Frailty / functional status",
  16: "Pressure injury risk",
  17: "GI: pancreatitis & bleeding",
  18: "Obstetric critical care",
  19: "Airway / difficult intubation",
  20: "Pediatric & neonatal",
  21: "Cardiac arrest & post-arrest",
  22: "ECMO / mechanical support",
  23: "Toxicology",
  24: "Long-term / QoL outcomes",
};

export function sectionName(n: number): string {
  return SECTION_NAMES[n] ?? `Section ${n}`;
}
