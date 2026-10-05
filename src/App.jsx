import {
  Box,
  Container,
  Flex,
  Heading,
  HStack,
  Text,
  Badge,
  Divider,
  Link,
  Tooltip,
  useColorMode,
  useColorModeValue,
} from "@chakra-ui/react";
import TaskTable from "./components/TaskTable";
import ThemeToggle from "./components/ThemeToggle";
import LogoInfracosteira from "./components/img/Logo_Infracosteira.jpeg";
import { GraduationCap, Award, ExternalLink, Code2, Waves, BookOpen } from "lucide-react";

const partners = [
  { name: "Universidade Federal do Ceará (UFC)", src: "/pluviometria/logos/ufc.png", category: "Universidade" },
  { name: "Universidade da Integração Internacional da Lusofonia Afro-Brasileira (UNILAB)", src: "/pluviometria/logos/unilab.png", category: "Universidade" },
  { name: "Instituto Federal do Ceará (IFCE)", src: "/pluviometria/logos/ifce.svg", category: "Instituto Federal" },
  { name: "Universidade Estadual do Ceará (UECE)", src: "/pluviometria/logos/uece.png", category: "Universidade" },
  { name: "Programa Cientista Chefe", src: "/pluviometria/logos/cientista_chefe.png", category: "Fomento / Governo" },
  { name: "Fundação Cearense de Apoio ao Desenvolvimento Científico e Tecnológico (FUNCAP)", src: "/pluviometria/logos/funcap.png", category: "Fomento" },
  { name: "Governo do Estado do Ceará / SEDUC", src: "/pluviometria/logos/ceara_gov.png", category: "Governo" },
];

function App() {
  const { colorMode } = useColorMode();
  const isDark = colorMode === "dark";

  const appBg = useColorModeValue("#f8fafc", "#0b1322");
  const topBarBg = useColorModeValue("#ffffff", "#0f172a");
  const topBarBorder = useColorModeValue("#e2e8f0", "#1e293b");
  const topBarTextColor = useColorModeValue("#475569", "#94a3b8");

  const heroBg = useColorModeValue(
    "linear-gradient(135deg, #091e2b 0%, #0e3d48 55%, #075985 100%)",
    "linear-gradient(135deg, #05141f 0%, #082631 55%, #033954 100%)"
  );
  const heroBorder = useColorModeValue("transparent", "#1e293b");
  const heroShadow = useColorModeValue(
    "0 4px 20px rgba(14, 61, 72, 0.15)",
    "0 4px 24px rgba(0, 0, 0, 0.45)"
  );

  const footerBg = useColorModeValue("#ffffff", "#0f172a");
  const footerBorder = useColorModeValue("#e2e8f0", "#1e293b");
  const footerTextColor = useColorModeValue("#64748b", "#94a3b8");
  const footerTitleColor = useColorModeValue("#1e293b", "#f1f5f9");
  const linkColor = useColorModeValue("#0284c7", "#38bdf8");

  return (
    <Box minH="100vh" bg={appBg} display="flex" flexDirection="column" transition="background-color 0.25s ease">
      {/* 1. Barra Institucional Superior */}
      <Box
        bg={topBarBg}
        borderBottom="1px solid"
        borderColor={topBarBorder}
        py={3}
        px={{ base: 4, md: 8 }}
        transition="background-color 0.25s ease, border-color 0.25s ease"
      >
        <Container maxW="1400px" px={0}>
          <Flex
            direction={{ base: "column", lg: "row" }}
            align={{ base: "center", lg: "center" }}
            justify="space-between"
            gap={3}
          >
            <HStack spacing={2} color={topBarTextColor} fontSize="xs" fontWeight="600" flexWrap="wrap">
              <GraduationCap size={16} color="#0284c7" />
              <Text>Rede Interinstitucional de Pesquisa e Desenvolvimento</Text>
              <Badge colorScheme="blue" variant="subtle" fontSize="2xs" borderRadius="full">
                Ceará • Brasil
              </Badge>
            </HStack>

            {/* Galeria de Logos das Instituições Parceiras e Fomento + Toggle Modo Escuro */}
            <HStack spacing={4} align="center" flexWrap="wrap" justify="center">
              <HStack
                spacing={{ base: 3, sm: 5 }}
                flexWrap="wrap"
                justify="center"
                align="center"
              >
                {partners.map((partner) => (
                  <Tooltip
                    key={partner.name}
                    label={`${partner.name} (${partner.category})`}
                    hasArrow
                    placement="bottom"
                  >
                    <Box
                      p={isDark ? "3px 6px" : 0}
                      bg={isDark ? "rgba(255, 255, 255, 0.95)" : "transparent"}
                      borderRadius="8px"
                      boxShadow={isDark ? "0 1px 4px rgba(0,0,0,0.3)" : "none"}
                      transition="all 0.2s"
                      display="inline-flex"
                      alignItems="center"
                      justifyContent="center"
                    >
                      <Box
                        as="img"
                        src={partner.src}
                        alt={partner.name}
                        h={{ base: "26px", sm: "32px" }}
                        maxW={{ base: "65px", sm: "85px" }}
                        objectFit="contain"
                        transition="transform 0.2s, opacity 0.2s"
                        opacity={isDark ? 0.95 : 0.9}
                        _hover={{ opacity: 1, transform: "scale(1.06)" }}
                      />
                    </Box>
                  </Tooltip>
                ))}
              </HStack>

              <Divider
                orientation="vertical"
                h="26px"
                borderColor={topBarBorder}
                display={{ base: "none", md: "block" }}
              />

              {/* Botão de Alternância de Tema */}
              <ThemeToggle variant="pill" size="sm" />
            </HStack>
          </Flex>
        </Container>
      </Box>

      {/* 2. Banner Principal / Hero Acadêmico */}
      <Box
        bg={heroBg}
        color="white"
        py={{ base: 8, md: 10 }}
        px={{ base: 4, md: 8 }}
        position="relative"
        overflow="hidden"
        borderBottom="1px solid"
        borderColor={heroBorder}
        boxShadow={heroShadow}
        transition="background 0.25s ease, border-color 0.25s ease"
      >
        <Container maxW="1400px" px={0}>
          <Flex
            direction={{ base: "column", md: "row" }}
            align="center"
            justify="space-between"
            gap={6}
          >
            {/* Logo do Laboratório e Título Principal */}
            <HStack spacing={5} align="center" flex={1}>
              <Box
                position="relative"
                p={1.5}
                bg={isDark ? "gray.900" : "white"}
                borderRadius="full"
                boxShadow="0 8px 24px rgba(0,0,0,0.35)"
                border="3px solid #38bdf8"
                flexShrink={0}
                transition="all 0.2s"
              >
                <Box
                  as="img"
                  src={LogoInfracosteira}
                  alt="Logo Infracosteira"
                  w={{ base: "64px", md: "78px" }}
                  h={{ base: "64px", md: "78px" }}
                  borderRadius="full"
                  objectFit="cover"
                />
              </Box>

              <Box>
                <HStack spacing={2} mb={1} flexWrap="wrap">
                  <Badge colorScheme="cyan" variant="solid" borderRadius="full" px={2.5} py={0.5} fontSize="2xs">
                    Infracosteira
                  </Badge>
                  <Badge bg="rgba(255,255,255,0.15)" color="white" borderRadius="full" px={2.5} py={0.5} fontSize="2xs">
                    Dados Pluviométricos
                  </Badge>
                  <Badge bg="#10b981" color="white" borderRadius="full" px={2.5} py={0.5} fontSize="2xs">
                    Série Histórica Aberta
                  </Badge>
                </HStack>

                <Heading as="h1" fontSize={{ base: "xl", md: "3xl" }} fontWeight="800" letterSpacing="-0.02em">
                  Monitoramento Pluviométrico do Ceará
                </Heading>
                <Text
                  color="#e0f2fe"
                  fontSize={{ base: "xs", md: "sm" }}
                  mt={1}
                  maxW="720px"
                  lineHeight="tall"
                  opacity={0.92}
                >
                  Plataforma de consulta, exploração estatística e download das séries temporais
                  de chuvas dos postos de monitoramento cearenses. Desenvolvido no âmbito de
                  projetos acadêmicos e bolsas de pesquisa científica e tecnológica.
                </Text>
              </Box>
            </HStack>

            {/* Selo de Bolsa / Projeto Científico */}
            <Box
              bg="rgba(255, 255, 255, 0.08)"
              backdropFilter="blur(12px)"
              p={4}
              borderRadius="16px"
              border="1px solid rgba(255, 255, 255, 0.18)"
              maxW={{ base: "100%", md: "320px" }}
            >
              <HStack spacing={2} color="#38bdf8" mb={1.5}>
                <Award size={18} />
                <Text fontSize="xs" fontWeight="700" textTransform="uppercase" letterSpacing="0.05em">
                  Projeto de Pesquisa & Bolsa
                </Text>
              </HStack>
              <Text fontSize="xs" color="#e2e8f0" lineHeight="short">
                Apoio e fomento do <strong>Programa Cientista Chefe</strong>, <strong>FUNCAP</strong> e{" "}
                <strong>SEDUC</strong> em parceria com a <strong>UFC</strong>, <strong>UNILAB</strong>,{" "}
                <strong>IFCE</strong> e <strong>UECE</strong>.
              </Text>
            </Box>
          </Flex>
        </Container>
      </Box>

      {/* 3. Corpo Principal com a Tabela e Filtros */}
      <Box flex="1" py={8} px={{ base: 4, md: 8 }}>
        <Container maxW="1400px" px={0}>
          <TaskTable />
        </Container>
      </Box>

      {/* 4. Rodapé Acadêmico */}
      <Box
        bg={footerBg}
        borderTop="1px solid"
        borderColor={footerBorder}
        py={6}
        px={{ base: 4, md: 8 }}
        mt="auto"
        transition="background-color 0.25s ease, border-color 0.25s ease"
      >
        <Container maxW="1400px" px={0}>
          <Flex
            direction={{ base: "column", md: "row" }}
            justify="space-between"
            align={{ base: "flex-start", md: "center" }}
            gap={4}
            fontSize="xs"
            color={footerTextColor}
          >
            <Box>
              <HStack spacing={2} mb={1}>
                <Waves size={15} color="#0284c7" />
                <Text fontWeight="700" color={footerTitleColor}>
                  Projeto Infracosteira • Gestão Costeira e Recursos Hídricos
                </Text>
              </HStack>
              <Text>
                Desenvolvido por bolsistas e pesquisadores em projetos de iniciação científica e tecnológica.
              </Text>
            </Box>

            <HStack spacing={4} flexWrap="wrap" align="center">
              <HStack spacing={1}>
                <BookOpen size={14} />
                <Text>Citação: Infracosteira / FUNCAP / Governo do Ceará</Text>
              </HStack>
              <Link
                href="https://github.com/infracosteira/pluviometria"
                isExternal
                display="flex"
                alignItems="center"
                gap={1}
                color={linkColor}
                fontWeight="600"
                _hover={{ textDecoration: "underline" }}
              >
                <Code2 size={14} />
                <span>Repositório GitHub</span>
                <ExternalLink size={12} />
              </Link>
              <ThemeToggle variant="icon" size="xs" />
            </HStack>
          </Flex>
        </Container>
      </Box>
    </Box>
  );
}

export default App;
