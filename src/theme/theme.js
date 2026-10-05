import { extendTheme } from "@chakra-ui/react";
import styles from "./styles.js";

const config = {
  initialColorMode: "light",
  useSystemColorMode: false,
};

const colors = {
  brand: {
    50: "#f0f9ff",
    100: "#e0f2fe",
    200: "#bae6fd",
    300: "#7dd3fc",
    400: "#38bdf8",
    500: "#0284c7",
    600: "#0369a1",
    700: "#075985",
    800: "#0c4a6e",
    900: "#082f49",
  },
  ocean: {
    50: "#f0fdfa",
    100: "#ccfbf1",
    200: "#99f6e4",
    300: "#5eead4",
    400: "#2dd4bf",
    500: "#14b8a6",
    600: "#0d9488",
    700: "#0f766e",
    800: "#115e59",
    900: "#134e4a",
  },
};

const fonts = {
  heading: "'Plus Jakarta Sans', 'Inter', -apple-system, sans-serif",
  body: "'Plus Jakarta Sans', 'Inter', -apple-system, sans-serif",
};

const theme = extendTheme({
  config,
  styles,
  colors,
  fonts,
});

export default theme;
