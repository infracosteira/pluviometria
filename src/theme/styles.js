import { mode } from "@chakra-ui/theme-tools";

const styles = {
  global: (props) => ({
    "html, body": {
      backgroundColor: mode("#f8fafc", "#0b1322")(props),
      color: mode("#1e293b", "#f1f5f9")(props),
      fontFamily:
        "'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
      WebkitFontSmoothing: "antialiased",
      MozOsxFontSmoothing: "grayscale",
      transitionProperty: "background-color, color, border-color",
      transitionDuration: "0.2s",
      minHeight: "100vh",
    },
    "*": {
      boxSizing: "border-box",
    },
    svg: {
      cursor: "pointer",
    },
    "::-webkit-scrollbar": {
      width: "8px",
      height: "8px",
    },
    "::-webkit-scrollbar-track": {
      background: mode("#f1f5f9", "#0b1322")(props),
      borderRadius: "4px",
    },
    "::-webkit-scrollbar-thumb": {
      background: mode("#cbd5e1", "#334155")(props),
      borderRadius: "4px",
      "&:hover": {
        background: mode("#94a3b8", "#475569")(props),
      },
    },
    ".table-container": {
      background: mode("#ffffff", "#131f37")(props),
      borderRadius: "16px",
      border: mode("1px solid #e2e8f0", "1px solid #1e293b")(props),
      boxShadow: mode(
        "0 4px 20px -2px rgba(15, 23, 42, 0.05)",
        "0 4px 20px -2px rgba(0, 0, 0, 0.4)"
      )(props),
      overflow: "hidden",
      transition: "background 0.2s, border 0.2s, box-shadow 0.2s",
    },
    ".table": {
      width: "100%",
      borderCollapse: "separate",
      borderSpacing: 0,
    },
    ".tr": {
      display: "flex",
      width: "fit-content",
      minWidth: "100%",
      borderBottom: mode("1px solid #edf2f7", "1px solid #1e293b")(props),
      transition: "background-color 0.15s ease",
      "&:hover": {
        backgroundColor: mode("#f8fafc", "#182640")(props),
      },
    },
    ".th": {
      position: "relative",
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      color: mode("#475569", "#94a3b8")(props),
      background: mode("#f8fafc", "#0f172a")(props),
      padding: "0.85rem 1rem",
      fontWeight: "700",
      fontSize: "xs",
      letterSpacing: "0.05em",
      textTransform: "uppercase",
      borderBottom: mode("2px solid #e2e8f0", "2px solid #1e293b")(props),
      userSelect: "none",
    },
    ".td": {
      display: "flex",
      alignItems: "center",
      padding: "0.75rem 1rem",
      fontSize: "0.875rem",
      color: mode("#334155", "#e2e8f0")(props),
      borderBottom: mode("1px solid #f1f5f9", "1px solid #1a273e")(props),
    },
    ".resizer": {
      position: "absolute",
      opacity: 0,
      top: 0,
      right: 0,
      height: "100%",
      width: "4px",
      background: "#0284c7",
      cursor: "col-resize",
      userSelect: "none",
      touchAction: "none",
      borderRadius: "2px",
      transition: "opacity 0.2s",
    },
    ".resizer.isResizing": {
      background: "#0284c7",
      opacity: 1,
      width: "6px",
    },
    "*:hover > .resizer": {
      opacity: 0.6,
    },
  }),
};

export default styles;
