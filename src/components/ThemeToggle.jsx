import React from "react";
import {
  IconButton,
  Button,
  Tooltip,
  useColorMode,
  useColorModeValue,
  HStack,
  Text,
} from "@chakra-ui/react";
import { Sun, Moon } from "lucide-react";

/**
 * Componente moderno para alternar entre Modo Claro e Modo Escuro
 * Suporta variantes: "icon" (botão circular compacto) ou "pill" (com rótulo descritivo)
 */
export const ThemeToggle = ({ variant = "pill", size = "sm" }) => {
  const { colorMode, toggleColorMode } = useColorMode();
  const isDark = colorMode === "dark";

  const label = isDark ? "Alternar para Modo Claro" : "Alternar para Modo Escuro";
  const textLabel = isDark ? "Modo Claro" : "Modo Escuro";

  const buttonBg = useColorModeValue("#f1f5f9", "#1e293b");
  const buttonHoverBg = useColorModeValue("#e2e8f0", "#283b58");
  const buttonBorder = useColorModeValue("#cbd5e1", "#334155");
  const textColor = useColorModeValue("#334155", "#e2e8f0");
  const iconColor = isDark ? "#fbbf24" : "#0284c7";

  if (variant === "pill") {
    return (
      <Tooltip label={label} hasArrow placement="bottom">
        <Button
          size={size}
          onClick={toggleColorMode}
          variant="outline"
          aria-label={label}
          bg={buttonBg}
          borderColor={buttonBorder}
          color={textColor}
          fontWeight="600"
          fontSize="xs"
          borderRadius="full"
          px={3}
          h="34px"
          leftIcon={
            isDark ? (
              <Sun size={15} color={iconColor} style={{ transition: "transform 0.3s ease" }} />
            ) : (
              <Moon size={15} color={iconColor} style={{ transition: "transform 0.3s ease" }} />
            )
          }
          _hover={{
            bg: buttonHoverBg,
            borderColor: isDark ? "#64748b" : "#94a3b8",
            transform: "translateY(-1px)",
            boxShadow: isDark
              ? "0 2px 10px rgba(251, 191, 36, 0.2)"
              : "0 2px 10px rgba(2, 132, 199, 0.2)",
          }}
          _active={{
            transform: "scale(0.97)",
          }}
          transition="all 0.2s cubic-bezier(0.4, 0, 0.2, 1)"
        >
          {textLabel}
        </Button>
      </Tooltip>
    );
  }

  return (
    <Tooltip label={label} hasArrow placement="bottom">
      <IconButton
        size={size}
        onClick={toggleColorMode}
        variant="outline"
        aria-label={label}
        bg={buttonBg}
        borderColor={buttonBorder}
        borderRadius="full"
        w="34px"
        h="34px"
        icon={
          isDark ? (
            <Sun size={17} color={iconColor} />
          ) : (
            <Moon size={17} color={iconColor} />
          )
        }
        _hover={{
          bg: buttonHoverBg,
          borderColor: isDark ? "#64748b" : "#94a3b8",
          transform: "scale(1.08)",
          boxShadow: isDark
            ? "0 2px 10px rgba(251, 191, 36, 0.25)"
            : "0 2px 10px rgba(2, 132, 199, 0.25)",
        }}
        _active={{
          transform: "scale(0.95)",
        }}
        transition="all 0.2s cubic-bezier(0.4, 0, 0.2, 1)"
      />
    </Tooltip>
  );
};

export default ThemeToggle;
