// @vitest-environment jsdom
// End-to-end UI test: render the real App, drive a calculator's inputs, and
// assert the computed score + band render. Proves the form -> compute ->
// ResultCard wiring, not just the engine in isolation.
import { describe, expect, it } from "vitest";
import { render, screen, fireEvent, within } from "@testing-library/react";
import { App } from "./App";

describe("App end-to-end", () => {
  it("computes qSOFA from user input and shows the band", async () => {
    render(<App />);

    // qSOFA is the first score (section 3); select it from the picker.
    fireEvent.click(screen.getByRole("button", { name: "qSOFA" }));

    // Fill the three inputs: RR 28, SBP 88, altered mentation on -> score 3.
    fireEvent.change(screen.getByLabelText(/Respiratory rate/i), { target: { value: "28" } });
    fireEvent.change(screen.getByLabelText(/Systolic blood pressure/i), { target: { value: "88" } });
    fireEvent.click(screen.getByLabelText(/Altered mentation/i));

    const result = await screen.findByRole("status");
    expect(within(result).getByText("3")).toBeTruthy();
    expect(within(result).getByText("Higher risk")).toBeTruthy();
  });

  it("shows the safety disclaimer", () => {
    render(<App />);
    expect(screen.getByText(/clinical decision support only/i)).toBeTruthy();
  });

  it("displays the full reference with a DOI/URL link for the selected score", () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: "qSOFA" }));

    // Scope to the R7 reference list item to avoid matching the disclaimer text.
    const refItem = screen.getByText("R7").closest("li")!;
    expect(refItem.id).toBe("ref-R7");
    expect(within(refItem).getByText(/Surviving Sepsis Campaign/i)).toBeTruthy();

    // ...with a clickable link to the source URL.
    const link = within(refItem).getByRole("link");
    expect(link.getAttribute("href")).toContain("sccm.org");
  });
});
