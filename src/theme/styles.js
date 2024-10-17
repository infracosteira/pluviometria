import { color } from "framer-motion";

const styles = {
  global: {
    "html, body": {
      backgroundColor: "white",
      color: "Black",
    },
    svg: {
      cursor: "pointer",
    },
    ".table": {
      border: "1px solid #424242",
      textAlign: "center",
    },
    ".tr": {
      display: "flex",
      width: "fit-content",
      textAlign: "center",
    },
    ".th, .td": { boxShadow: "inset 0 0 0 1px #424242" },
    ".th": {
      position: "relative",
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      color: "Black",
      padding: "0.5rem",
      fontWeight: "bold",
      fontSize: "xs",
      textTransform: "uppercase",
      textAlign: "center",
    },
    ".td > input": {
      m: "1",
      padding: "0.2rem",
      bg: "transparent",
      maxW: "100%",
      textAlign: "center",
    },
    ".date-wrapper": {
      display: "flex",
      alignItems: "center",
      w: "100%",
      h: "100%",
    },
    ".resizer": {
      position: "absolute",
      opacity: 0,
      top: 0,
      right: 0,
      h: "100%",
      w: "5px",
      bg: "#27bbff",
      cursor: "col-resize",
      userSelect: "none",
      touchAction: "none",
      borderRadius: "6px",
      textAlign: "center",
    },
    //cor usada para a rederização de linhas
    ".resizer.isResizing": {
      bg: "#E74C3C",
      opacity: 1,
    },
    "*:hover > .resizer": {
      opacity: 1,
    },
    "*:Nlinhas":{
      position: "relative",
      top: 1000,
    },
  },
};

export default styles;
