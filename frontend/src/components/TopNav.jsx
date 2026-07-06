export default function TopNav() {
  return (
    <div
      style={{
        background: "var(--color-ink-900)",
        padding: "18px 28px",
        display: "flex",
        alignItems: "center",
        gap: 14,
      }}
    >
      <div
        style={{
          width: 9,
          height: 9,
          background: "var(--color-accent)",
          borderRadius: 2,
          transform: "rotate(45deg)",
        }}
      />
      <span
        style={{
          fontFamily: "var(--font-display)",
          fontWeight: 600,
          fontSize: 16,
          color: "var(--color-bg)",
          letterSpacing: "0.01em",
        }}
      >
        Finance Tracker
      </span>
      <div style={{ marginLeft: "auto", display: "flex", gap: 22, fontSize: 13, color: "#9aaab8" }}>
        <span
          style={{
            color: "var(--color-bg)",
            borderBottom: "2px solid var(--color-accent)",
            paddingBottom: 4,
          }}
        >
          Overview
        </span>
        <span>Accounts</span>
        <span>Budgets</span>
      </div>
    </div>
  )
}
