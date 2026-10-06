import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { ApprovalCard, ArtifactView } from "./components";
import Office from "./Office";
import type { Agent, Approval } from "./types";

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});
describe("governed UI controls", () => {
  it("renders only active gate decisions and sends the approval revision", async () => {
    const fetch = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue({ ok: true, json: async () => ({}) } as Response);
    const done = vi.fn();
    const approval: Approval = {
      id: "gate-1",
      run_id: "run-1",
      revision: 7,
      action: "production_approval",
      kind: "approval",
      allowed_decisions: ["approve", "cancel"],
      context: { specification: { movement: "NH35" } },
      status: "pending",
      created_at: new Date().toISOString(),
    };
    render(<ApprovalCard approval={approval} onDone={done} />);
    expect(
      screen.queryByRole("button", { name: "Pausieren" }),
    ).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Freigeben" }));
    await waitFor(() => expect(done).toHaveBeenCalledOnce());
    const body = JSON.parse(String(fetch.mock.calls[0][1]?.body));
    expect(body.revision).toBe(7);
    expect(body.decision).toBe("approve");
  });
  it("keeps the office keyboard list usable and founder selection only opens the launcher", () => {
    const launch = vi.fn();
    const agent = {
      id: "elena",
      name: "Elena Laurent",
      activity: { state: "idle" },
    } as Agent;
    render(<Office agents={[agent]} onLaunch={launch} stale />);
    expect(screen.getByRole("link", { name: /Elena/ })).toHaveAttribute(
      "href",
      "#/agents/elena",
    );
    fireEvent.click(
      screen.getByRole("button", { name: /Prozess mit Amancio starten/ }),
    );
    expect(launch).toHaveBeenCalledOnce();
    expect(screen.getByText("Unbekannt")).toBeInTheDocument();
  });
  it("renders model text as text instead of HTML", () => {
    const { container } = render(
      <ArtifactView value={{ result: "<script>alert(1)</script>" }} />,
    );
    expect(container.querySelector("script")).toBeNull();
    expect(screen.getByText("<script>alert(1)</script>")).toBeInTheDocument();
  });
});
