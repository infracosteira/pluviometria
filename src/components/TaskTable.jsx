import React, { useState, useEffect, useMemo } from "react";
import {
  Box,
  Button,
  ButtonGroup,
  Flex,
  Grid,
  GridItem,
  Heading,
  HStack,
  Icon,
  IconButton,
  Input,
  InputGroup,
  InputLeftElement,
  InputRightElement,
  Progress,
  Select,
  SimpleGrid,
  Stat,
  StatHelpText,
  StatLabel,
  StatNumber,
  Tag,
  Text,
  Tooltip,
  useToast,
  useColorMode,
  useColorModeValue,
} from "@chakra-ui/react";
import {
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table";
import {
  Search,
  X,
  Download,
  MapPin,
  ExternalLink,
  ChevronDown,
  ChevronRight,
  ChevronLeft,
  ChevronsLeft,
  ChevronsRight,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  Calendar,
  Layers,
  CheckCircle2,
  AlertTriangle,
  FileArchive,
  BarChart3,
  Droplets,
  Building2,
} from "lucide-react";
import axios from "axios";
import localJsonData from "./../../data/dados_formatados_resumo.json";

// Download seguro com suporte a axios blob e fallback para link direto
async function downloadFile(fileUrl, fileName) {
  try {
    const response = await axios.get(fileUrl, {
      responseType: "blob",
      headers: {
        "Content-Type": "text/csv",
      },
    });

    if (response.status === 200) {
      const blob = response.data;
      const link = document.createElement("a");
      link.href = window.URL.createObjectURL(blob);
      link.download = fileName || fileUrl.split("/").pop();
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(link.href);
      return;
    }
  } catch (error) {
    console.warn("Axios falhou, abrindo via download direto:", error);
  }

  // Fallback caso ocorra CORS ou erro de requisição direta
  const link = document.createElement("a");
  link.href = fileUrl;
  link.download = fileName || fileUrl.split("/").pop();
  link.target = "_blank";
  link.rel = "noopener noreferrer";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

const TaskTable = () => {
  const { colorMode } = useColorMode();
  const isDark = colorMode === "dark";

  const [data, setData] = useState(localJsonData || []);
  const [searchQuery, setSearchQuery] = useState("");
  const [expandedRows, setExpandedRows] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const toast = useToast();

  const [pagination, setPagination] = useState({
    pageIndex: 0,
    pageSize: 15,
  });

  // Tokens de cores dinâmicos para modo claro / escuro
  const cardBg = useColorModeValue("white", "#131f37");
  const cardBorder = useColorModeValue("#e2e8f0", "#1e293b");
  const cardShadow = useColorModeValue(
    "0 2px 10px rgba(0,0,0,0.03)",
    "0 2px 10px rgba(0,0,0,0.3)"
  );
  const cardHoverShadow = useColorModeValue(
    "0 6px 16px rgba(0,0,0,0.06)",
    "0 6px 16px rgba(0,0,0,0.45)"
  );

  const textPrimary = useColorModeValue("#0f172a", "#f1f5f9");
  const textSecondary = useColorModeValue("#334155", "#cbd5e1");
  const textMuted = useColorModeValue("#64748b", "#94a3b8");

  const inputBg = useColorModeValue("#f8fafc", "#0b1322");
  const inputHoverBg = useColorModeValue("#f1f5f9", "#152238");
  const inputFocusBg = useColorModeValue("#ffffff", "#0f172a");

  const tableRowExpandedBg = useColorModeValue("#f0f9ff", "#162540");
  const detailBoxBg = useColorModeValue("#f8fafc", "#0b1322");

  // Tenta buscar dados mais recentes do GitHub, mantendo o fallback local garantido
  useEffect(() => {
    async function loadData() {
      try {
        setIsLoading(true);
        const response = await fetch(
          "https://raw.githubusercontent.com/infracosteira/pluviometria/refs/heads/main/data/dados_formatados_resumo.json"
        );
        if (response.ok) {
          const remoteJson = await response.json();
          if (Array.isArray(remoteJson) && remoteJson.length > 0) {
            setData(remoteJson);
          }
        }
      } catch (err) {
        console.warn("Utilizando base de dados embutida:", err);
      } finally {
        setIsLoading(false);
      }
    }
    loadData();
  }, []);

  // Filtragem flexível por Município ou Nome do Posto
  const filteredData = useMemo(() => {
    if (!searchQuery.trim()) return data;
    const query = searchQuery.toLowerCase().trim();
    return data.filter((item) => {
      const mun = (item.Nome_Municipio || "").toLowerCase();
      const posto = (item.Nome_Posto || "").toLowerCase();
      const id = String(item.ID || "").toLowerCase();
      return mun.includes(query) || posto.includes(query) || id === query;
    });
  }, [data, searchQuery]);

  // Colunas principais da tabela
  const columns = useMemo(
    () => [
      {
        id: "expander",
        header: () => <Box textAlign="center" w="36px">#</Box>,
        size: 50,
        enableSorting: false,
        cell: ({ row }) => {
          const isExpanded = !!expandedRows[row.index];
          return (
            <IconButton
              size="xs"
              variant="ghost"
              colorScheme="cyan"
              aria-label={isExpanded ? "Recolher detalhes" : "Expandir detalhes"}
              icon={
                isExpanded ? (
                  <ChevronDown size={18} color="#0284c7" />
                ) : (
                  <ChevronRight size={18} color={isDark ? "#94a3b8" : "#64748b"} />
                )
              }
              onClick={(e) => {
                e.stopPropagation();
                toggleRowExpansion(row.index);
              }}
            />
          );
        },
      },
      {
        accessorKey: "ID",
        header: "ID",
        size: 70,
        cell: (props) => (
          <Tag size="sm" colorScheme="blue" variant="subtle" fontWeight="700">
            {props.getValue()}
          </Tag>
        ),
      },
      {
        accessorKey: "Nome_Posto",
        header: "Nome do Posto",
        size: 190,
        cell: (props) => (
          <Text fontWeight="600" color={textPrimary} fontSize="sm">
            {props.getValue()}
          </Text>
        ),
      },
      {
        accessorKey: "Nome_Municipio",
        header: "Município",
        size: 180,
        cell: (props) => (
          <HStack spacing={1.5}>
            <Building2 size={14} color="#0284c7" />
            <Text color={textSecondary} fontWeight="500">
              {props.getValue()}
            </Text>
          </HStack>
        ),
      },
      {
        id: "periodo",
        header: "Série Histórica",
        size: 160,
        enableSorting: true,
        accessorFn: (row) => `${row.Ano_Inicio} - ${row.Ano_Fim}`,
        cell: ({ row }) => (
          <Tag size="sm" variant="outline" colorScheme="teal" borderRadius="full">
            <HStack spacing={1}>
              <Calendar size={12} />
              <Text>
                {row.original.Ano_Inicio} – {row.original.Ano_Fim}
              </Text>
            </HStack>
          </Tag>
        ),
      },
      {
        accessorKey: "Numero_anos_completos",
        header: "Anos Completos",
        size: 150,
        cell: (props) => {
          const val = Number(props.getValue()) || 0;
          return (
            <Tag
              size="sm"
              colorScheme={val >= 40 ? "green" : val >= 25 ? "blue" : "orange"}
              variant="subtle"
              fontWeight="600"
              borderRadius="full"
            >
              {val} anos
            </Tag>
          );
        },
      },
      {
        id: "download",
        header: "Download",
        size: 110,
        enableSorting: false,
        cell: ({ row }) => (
          <Tooltip label={`Baixar dados de ${row.original.Nome_Posto} (.csv)`} hasArrow placement="top">
            <Button
              size="xs"
              colorScheme="blue"
              variant="outline"
              leftIcon={<Download size={13} />}
              onClick={() => {
                const name = `${row.original.ID}_${row.original.Nome_Posto}.csv`;
                downloadFile(row.original.link_csv, name);
                toast({
                  title: "Iniciando download",
                  description: `Baixando ${name}...`,
                  status: "info",
                  duration: 2500,
                  isClosable: true,
                });
              }}
            >
              CSV
            </Button>
          </Tooltip>
        ),
      },
      {
        id: "mapa",
        header: "Mapa",
        size: 90,
        enableSorting: false,
        cell: ({ row }) => {
          const lat = row.original.Coordenada_Y;
          const lng = row.original.Coordenada_X;
          return (
            <Tooltip label={`Abrir coordenadas (${lat}, ${lng}) no Google Maps`} hasArrow placement="top">
              <Button
                as="a"
                href={`https://maps.google.com/?q=${lat},${lng}`}
                target="_blank"
                rel="noopener noreferrer"
                size="xs"
                colorScheme="teal"
                variant="ghost"
                leftIcon={<MapPin size={14} color="#0d9488" />}
              >
                Ver
              </Button>
            </Tooltip>
          );
        },
      },
    ],
    [expandedRows, toast, textPrimary, textSecondary, isDark]
  );

  const table = useReactTable({
    data: filteredData,
    columns,
    state: {
      pagination,
    },
    onPaginationChange: setPagination,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    columnResizeMode: "onChange",
  });

  const toggleRowExpansion = (rowIndex) => {
    setExpandedRows((prev) => ({
      ...prev,
      [rowIndex]: !prev[rowIndex],
    }));
  };

  // Resumo dos dados para cards do topo
  const stats = useMemo(() => {
    const totalPostos = data.length;
    const municipiosUnicos = new Set(data.map((d) => d.Nome_Municipio)).size;
    let minAno = 9999;
    let maxAno = 0;
    data.forEach((d) => {
      const ini = Number(d.Ano_Inicio);
      const fim = Number(d.Ano_Fim);
      if (ini && ini < minAno) minAno = ini;
      if (fim && fim > maxAno) maxAno = fim;
    });
    return {
      totalPostos: totalPostos || 204,
      municipiosUnicos: municipiosUnicos || 184,
      periodo: minAno && maxAno ? `${minAno} – ${maxAno}` : "1973 – 2024",
    };
  }, [data]);

  return (
    <Box w="100%">
      {/* Cards de Resumo Científico */}
      <SimpleGrid columns={{ base: 1, sm: 2, md: 4 }} gap={4} mb={6}>
        <Box
          bg={cardBg}
          p={4}
          borderRadius="14px"
          border="1px solid"
          borderColor={cardBorder}
          boxShadow={cardShadow}
          transition="transform 0.2s, box-shadow 0.2s, background-color 0.2s, border-color 0.2s"
          _hover={{ transform: "translateY(-2px)", boxShadow: cardHoverShadow }}
        >
          <HStack spacing={3}>
            <Box
              p={2.5}
              borderRadius="10px"
              bg={useColorModeValue("#e0f2fe", "rgba(56, 189, 248, 0.16)")}
              color={useColorModeValue("#0369a1", "#38bdf8")}
            >
              <Droplets size={22} />
            </Box>
            <Stat>
              <StatLabel fontSize="xs" fontWeight="600" color={textMuted} textTransform="uppercase">
                Postos de Coleta
              </StatLabel>
              <StatNumber fontSize="2xl" fontWeight="800" color={textPrimary}>
                {stats.totalPostos}
              </StatNumber>
              <StatHelpText m={0} fontSize="xs" color={useColorModeValue("#059669", "#34d399")}>
                Estações catalogadas
              </StatHelpText>
            </Stat>
          </HStack>
        </Box>

        <Box
          bg={cardBg}
          p={4}
          borderRadius="14px"
          border="1px solid"
          borderColor={cardBorder}
          boxShadow={cardShadow}
          transition="transform 0.2s, box-shadow 0.2s, background-color 0.2s, border-color 0.2s"
          _hover={{ transform: "translateY(-2px)", boxShadow: cardHoverShadow }}
        >
          <HStack spacing={3}>
            <Box
              p={2.5}
              borderRadius="10px"
              bg={useColorModeValue("#ccfbf1", "rgba(45, 212, 191, 0.16)")}
              color={useColorModeValue("#0f766e", "#2dd4bf")}
            >
              <MapPin size={22} />
            </Box>
            <Stat>
              <StatLabel fontSize="xs" fontWeight="600" color={textMuted} textTransform="uppercase">
                Municípios Cobertos
              </StatLabel>
              <StatNumber fontSize="2xl" fontWeight="800" color={textPrimary}>
                {stats.municipiosUnicos}
              </StatNumber>
              <StatHelpText m={0} fontSize="xs" color={useColorModeValue("#0284c7", "#38bdf8")}>
                Cobertura no Ceará
              </StatHelpText>
            </Stat>
          </HStack>
        </Box>

        <Box
          bg={cardBg}
          p={4}
          borderRadius="14px"
          border="1px solid"
          borderColor={cardBorder}
          boxShadow={cardShadow}
          transition="transform 0.2s, box-shadow 0.2s, background-color 0.2s, border-color 0.2s"
          _hover={{ transform: "translateY(-2px)", boxShadow: cardHoverShadow }}
        >
          <HStack spacing={3}>
            <Box
              p={2.5}
              borderRadius="10px"
              bg={useColorModeValue("#fef3c7", "rgba(251, 191, 36, 0.16)")}
              color={useColorModeValue("#b45309", "#fbbf24")}
            >
              <Calendar size={22} />
            </Box>
            <Stat>
              <StatLabel fontSize="xs" fontWeight="600" color={textMuted} textTransform="uppercase">
                Série Temporal
              </StatLabel>
              <StatNumber fontSize="2xl" fontWeight="800" color={textPrimary}>
                {stats.periodo}
              </StatNumber>
              <StatHelpText m={0} fontSize="xs" color={textMuted}>
                ~51 anos históricos
              </StatHelpText>
            </Stat>
          </HStack>
        </Box>

        <Box
          bg={cardBg}
          p={4}
          borderRadius="14px"
          border="1px solid"
          borderColor={cardBorder}
          boxShadow={cardShadow}
          transition="transform 0.2s, box-shadow 0.2s, background-color 0.2s, border-color 0.2s"
          _hover={{ transform: "translateY(-2px)", boxShadow: cardHoverShadow }}
        >
          <HStack spacing={3}>
            <Box
              p={2.5}
              borderRadius="10px"
              bg={useColorModeValue("#ecfdf5", "rgba(16, 185, 129, 0.16)")}
              color={useColorModeValue("#047857", "#34d399")}
            >
              <FileArchive size={22} />
            </Box>
            <Stat>
              <StatLabel fontSize="xs" fontWeight="600" color={textMuted} textTransform="uppercase">
                Download Completo
              </StatLabel>
              <StatNumber fontSize="md" fontWeight="700" color={textPrimary} pt={1}>
                Base Integral
              </StatNumber>
              <StatHelpText m={0} fontSize="xs" color={useColorModeValue("#047857", "#34d399")}>
                Arquivo .RAR de todos os postos
              </StatHelpText>
            </Stat>
          </HStack>
        </Box>
      </SimpleGrid>

      {/* Barra de Ações: Busca, Contador e Botão de Download Integral */}
      <Flex
        direction={{ base: "column", md: "row" }}
        justify="space-between"
        align={{ base: "stretch", md: "center" }}
        gap={4}
        mb={4}
        bg={cardBg}
        p={4}
        borderRadius="14px"
        border="1px solid"
        borderColor={cardBorder}
        boxShadow={cardShadow}
        transition="background-color 0.2s, border-color 0.2s"
      >
        <HStack spacing={3} flex={1} maxW={{ base: "100%", md: "460px" }}>
          <InputGroup size="md">
            <InputLeftElement pointerEvents="none">
              <Search size={18} color={isDark ? "#94a3b8" : "#64748b"} />
            </InputLeftElement>
            <Input
              type="text"
              variant="filled"
              bg={inputBg}
              color={textPrimary}
              border="1px solid"
              borderColor={useColorModeValue("#e2e8f0", "#334155")}
              _hover={{ bg: inputHoverBg }}
              _focus={{ bg: inputFocusBg, borderColor: "#0284c7" }}
              _placeholder={{ color: textMuted }}
              placeholder="Buscar por município ou posto..."
              borderRadius="10px"
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setPagination((prev) => ({ ...prev, pageIndex: 0 }));
              }}
            />
            {searchQuery && (
              <InputRightElement>
                <IconButton
                  size="xs"
                  variant="ghost"
                  aria-label="Limpar busca"
                  icon={<X size={14} />}
                  onClick={() => setSearchQuery("")}
                />
              </InputRightElement>
            )}
          </InputGroup>
        </HStack>

        <HStack spacing={3} justify={{ base: "space-between", md: "flex-end" }} flexWrap="wrap">
          <Text fontSize="sm" color={textMuted} fontWeight="500">
            Exibindo{" "}
            <Text as="span" fontWeight="700" color={textPrimary}>
              {filteredData.length}
            </Text>{" "}
            de {data.length} postos
          </Text>

          <Button
            leftIcon={<Download size={16} />}
            colorScheme="teal"
            size="md"
            borderRadius="10px"
            fontWeight="600"
            boxShadow="0 2px 8px rgba(13, 148, 136, 0.25)"
            _hover={{ transform: "translateY(-1px)", boxShadow: "0 4px 12px rgba(13, 148, 136, 0.35)" }}
            onClick={() => {
              const fileUrl =
                "https://github.com/infracosteira/pluviometria/raw/main/data/todos_os_postos.rar";
              const link = document.createElement("a");
              link.href = fileUrl;
              link.download = "todos_os_postos.rar";
              link.click();
              toast({
                title: "Download iniciado",
                description: "Baixando pacote com todos os postos (todos_os_postos.rar)...",
                status: "success",
                duration: 4000,
                isClosable: true,
              });
            }}
          >
            Baixar todos os postos (.rar)
          </Button>
        </HStack>
      </Flex>

      {/* Contêiner da Tabela */}
      <Box className="table-container">
        <Box overflowX="auto">
          <Box className="table">
            {/* Cabeçalho */}
            {table.getHeaderGroups().map((headerGroup) => (
              <Box className="tr" key={headerGroup.id}>
                {headerGroup.headers.map((header) => {
                  const canSort = header.column.getCanSort();
                  const isSorted = header.column.getIsSorted();
                  return (
                    <Box
                      className="th"
                      w={header.getSize()}
                      key={header.id}
                      onClick={canSort ? header.column.getToggleSortingHandler() : undefined}
                      cursor={canSort ? "pointer" : "default"}
                    >
                      <HStack spacing={1.5} align="center">
                        <Text>{flexRender(header.column.columnDef.header, header.getContext())}</Text>
                        {canSort && (
                          <Box color={isSorted ? "#0284c7" : (isDark ? "#64748b" : "#94a3b8")}>
                            {isSorted === "asc" ? (
                              <ArrowUp size={14} />
                            ) : isSorted === "desc" ? (
                              <ArrowDown size={14} />
                            ) : (
                              <ArrowUpDown size={13} opacity={0.6} />
                            )}
                          </Box>
                        )}
                      </HStack>
                      <Box
                        onMouseDown={header.getResizeHandler()}
                        onTouchStart={header.getResizeHandler()}
                        className={`resizer ${
                          header.column.getIsResizing() ? "isResizing" : ""
                        }`}
                        onClick={(e) => e.stopPropagation()}
                      />
                    </Box>
                  );
                })}
              </Box>
            ))}

            {/* Linhas de Dados */}
            {table.getRowModel().rows.length === 0 ? (
              <Box p={10} textAlign="center" color={textMuted}>
                <AlertTriangle size={32} style={{ margin: "0 auto 12px", color: "#f59e0b" }} />
                <Text fontWeight="600" fontSize="md" color={textPrimary}>
                  Nenhum posto encontrado
                </Text>
                <Text fontSize="sm" color={textMuted}>Tente buscar por outro município ou limpe o filtro.</Text>
              </Box>
            ) : (
              table.getRowModel().rows.map((row) => {
                const isExpanded = !!expandedRows[row.index];
                const r = row.original;
                return (
                  <React.Fragment key={row.id}>
                    <Box
                      className="tr"
                      bg={isExpanded ? tableRowExpandedBg : "transparent"}
                      cursor="pointer"
                      onClick={() => toggleRowExpansion(row.index)}
                    >
                      {row.getVisibleCells().map((cell) => (
                        <Box className="td" w={cell.column.getSize()} key={cell.id}>
                          {flexRender(cell.column.columnDef.cell, cell.getContext())}
                        </Box>
                      ))}
                    </Box>

                    {/* Detalhes Científicos Expandidos */}
                    {isExpanded && (
                      <Box
                        p={5}
                        bg={detailBoxBg}
                        borderBottom="2px solid"
                        borderBottomColor={cardBorder}
                        borderLeft="4px solid #0284c7"
                        animation="fadeIn 0.2s ease"
                      >
                        <Flex
                          direction={{ base: "column", lg: "row" }}
                          gap={6}
                          justify="space-between"
                        >
                          {/* Coluna 1: Metadados Geográficos e Temporais */}
                          <Box flex="1" bg={cardBg} p={4} borderRadius="12px" border="1px solid" borderColor={cardBorder} boxShadow={cardShadow}>
                            <Heading size="xs" color={useColorModeValue("#0369a1", "#38bdf8")} textTransform="uppercase" mb={3} display="flex" alignItems="center" gap={2}>
                              <Layers size={16} /> Metadados da Estação
                            </Heading>
                            <Grid templateColumns="repeat(2, 1fr)" gap={3} fontSize="sm">
                              <Box>
                                <Text color={textMuted} fontSize="xs">Latitude (Y):</Text>
                                <Text fontWeight="600" color={textPrimary}>{r.Coordenada_Y || "—"}</Text>
                              </Box>
                              <Box>
                                <Text color={textMuted} fontSize="xs">Longitude (X):</Text>
                                <Text fontWeight="600" color={textPrimary}>{r.Coordenada_X || "—"}</Text>
                              </Box>
                              <Box>
                                <Text color={textMuted} fontSize="xs">Início da Série:</Text>
                                <Text fontWeight="600" color={textPrimary}>Mês {r.Mes_Inicio || "1"} / {r.Ano_Inicio}</Text>
                              </Box>
                              <Box>
                                <Text color={textMuted} fontSize="xs">Fim da Série:</Text>
                                <Text fontWeight="600" color={textPrimary}>Mês {r.Mes_Fim || "12"} / {r.Ano_Fim}</Text>
                              </Box>
                              <Box>
                                <Text color={textMuted} fontSize="xs">Total de Dias do Período:</Text>
                                <Text fontWeight="600" color={textPrimary}>{r.Total_dias_intervalo || "—"} dias</Text>
                              </Box>
                              <Box>
                                <Text color={textMuted} fontSize="xs">Total de Meses:</Text>
                                <Text fontWeight="600" color={textPrimary}>{r.Total_meses_intervalo || "—"} meses</Text>
                              </Box>
                            </Grid>
                            <Box mt={3} pt={2} borderTop="1px dashed" borderColor={useColorModeValue("#e2e8f0", "#334155")}>
                              <Button
                                as="a"
                                href={`https://maps.google.com/?q=${r.Coordenada_Y},${r.Coordenada_X}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                size="xs"
                                colorScheme="cyan"
                                variant="outline"
                                leftIcon={<ExternalLink size={12} />}
                              >
                                Visualizar Localização no Google Maps
                              </Button>
                            </Box>
                          </Box>

                          {/* Coluna 2: Qualidade e Confiabilidade dos Dados */}
                          <Box flex="1" bg={cardBg} p={4} borderRadius="12px" border="1px solid" borderColor={cardBorder} boxShadow={cardShadow}>
                            <Heading size="xs" color={useColorModeValue("#0f766e", "#2dd4bf")} textTransform="uppercase" mb={3} display="flex" alignItems="center" gap={2}>
                              <CheckCircle2 size={16} /> Indicadores de Qualidade da Série
                            </Heading>
                            <Box mb={3}>
                              <Flex justify="space-between" fontSize="xs" mb={1}>
                                <Text color={textMuted}>Integridade dos Dados Diários:</Text>
                                <Text fontWeight="700" color={Number(r.Percentual_dias_falhos) < 5 ? (isDark ? "#4ade80" : "#16a34a") : (isDark ? "#fb923c" : "#ea580c")}>
                                  {(100 - (Number(r.Percentual_dias_falhos) || 0)).toFixed(1)}% medido
                                </Text>
                              </Flex>
                              <Progress
                                value={100 - (Number(r.Percentual_dias_falhos) || 0)}
                                size="sm"
                                borderRadius="full"
                                colorScheme={Number(r.Percentual_dias_falhos) < 5 ? "green" : "orange"}
                              />
                            </Box>

                            <Grid templateColumns="repeat(2, 1fr)" gap={3} fontSize="sm">
                              <Box>
                                <Text color={textMuted} fontSize="xs">Dias com dados medidos:</Text>
                                <Text fontWeight="600" color={isDark ? "#4ade80" : "#16a34a"}>{r.Dias_dados_medidos || "—"}</Text>
                              </Box>
                              <Box>
                                <Text color={textMuted} fontSize="xs">Dias com falha:</Text>
                                <Text fontWeight="600" color={isDark ? "#f87171" : "#dc2626"}>{r.Dias_falhos || "0"} ({r.Percentual_dias_falhos || "0"}%)</Text>
                              </Box>
                              <Box>
                                <Text color={textMuted} fontSize="xs">Meses completos:</Text>
                                <Text fontWeight="600" color={isDark ? "#4ade80" : "#16a34a"}>{r.Numero_meses_completos || "—"}</Text>
                              </Box>
                              <Box>
                                <Text color={textMuted} fontSize="xs">Meses com falha:</Text>
                                <Text fontWeight="600" color={isDark ? "#f87171" : "#dc2626"}>{r.Numero_meses_falha || "0"} ({r.Percentual_meses_falha || "0"}%)</Text>
                              </Box>
                              <Box>
                                <Text color={textMuted} fontSize="xs">Anos completos:</Text>
                                <Text fontWeight="600" color={isDark ? "#4ade80" : "#16a34a"}>{r.Numero_anos_completos || "—"}</Text>
                              </Box>
                              <Box>
                                <Text color={textMuted} fontSize="xs">Anos com falha:</Text>
                                <Text fontWeight="600" color={isDark ? "#f87171" : "#dc2626"}>{r.Numero_anos_falha || "0"} ({r.Percentual_anos_falha || "0"}%)</Text>
                              </Box>
                            </Grid>
                          </Box>
                        </Flex>

                        {/* Linha 2: Médias Mensais de Precipitação (Regime Pluviométrico) */}
                        <Box mt={4} bg={cardBg} p={4} borderRadius="12px" border="1px solid" borderColor={cardBorder} boxShadow={cardShadow}>
                          <Flex justify="space-between" align="center" mb={3} flexWrap="wrap" gap={2}>
                            <Heading size="xs" color={useColorModeValue("#0369a1", "#38bdf8")} textTransform="uppercase" display="flex" alignItems="center" gap={2}>
                              <BarChart3 size={16} /> Precipitação Média Mensal (mm) • Quadra Chuvosa e Estiagem
                            </Heading>
                            <Tag size="md" colorScheme="blue" variant="solid" borderRadius="full">
                              Média Anual: {r.Precipitacao_media_anual ? `${r.Precipitacao_media_anual} mm` : "—"}
                            </Tag>
                          </Flex>

                          <SimpleGrid columns={{ base: 4, sm: 6, md: 12 }} gap={2}>
                            {[
                              { label: "Jan", val: r.Mes_Jan, quadra: false },
                              { label: "Fev", val: r.Mes_Fev, quadra: true },
                              { label: "Mar", val: r.Mes_Mar, quadra: true },
                              { label: "Abr", val: r.Mes_Apr, quadra: true },
                              { label: "Mai", val: r.Mes_May, quadra: true },
                              { label: "Jun", val: r.Mes_Jun, quadra: false },
                              { label: "Jul", val: r.Mes_Jul, quadra: false },
                              { label: "Ago", val: r.Mes_Aug, quadra: false },
                              { label: "Set", val: r.Mes_Sep, quadra: false },
                              { label: "Out", val: r.Mes_Oct, quadra: false },
                              { label: "Nov", val: r.Mes_Nov, quadra: false },
                              { label: "Dez", val: r.Mes_Dec, quadra: false },
                            ].map((m) => {
                              const num = parseFloat(m.val) || 0;
                              return (
                                <Box
                                  key={m.label}
                                  p={2}
                                  textAlign="center"
                                  borderRadius="8px"
                                  bg={m.quadra ? useColorModeValue("#e0f2fe", "rgba(56, 189, 248, 0.16)") : useColorModeValue("#f8fafc", "#0b1322")}
                                  border={m.quadra ? (isDark ? "1px solid #0284c7" : "1px solid #7dd3fc") : (isDark ? "1px solid #1e293b" : "1px solid #e2e8f0")}
                                >
                                  <Text fontSize="2xs" fontWeight="700" color={m.quadra ? (isDark ? "#38bdf8" : "#0369a1") : textMuted}>
                                    {m.label}
                                  </Text>
                                  <Text fontSize="xs" fontWeight="800" color={m.quadra ? (isDark ? "#e0f2fe" : "#0c4a6e") : textSecondary}>
                                    {num.toFixed(1)}
                                  </Text>
                                  <Text fontSize="3xs" color={textMuted}>mm</Text>
                                </Box>
                              );
                            })}
                          </SimpleGrid>
                          <Text fontSize="2xs" color={textMuted} mt={2} fontStyle="italic">
                            * Meses destacados em azul (Fev – Mai) correspondem à quadra chuvosa tradicional do Estado do Ceará.
                          </Text>
                        </Box>
                      </Box>
                    )}
                  </React.Fragment>
                );
              })
            )}
          </Box>
        </Box>
      </Box>

      {/* Controles de Paginação Modernos */}
      <Flex
        mt={4}
        p={4}
        bg={cardBg}
        borderRadius="14px"
        border="1px solid"
        borderColor={cardBorder}
        boxShadow={cardShadow}
        direction={{ base: "column", sm: "row" }}
        justify="space-between"
        align="center"
        gap={4}
        transition="background-color 0.2s, border-color 0.2s"
      >
        <HStack spacing={2}>
          <Text fontSize="sm" color={textMuted}>
            Linhas por página:
          </Text>
          <Select
            size="sm"
            width="85px"
            borderRadius="8px"
            bg={useColorModeValue("white", "#0b1322")}
            borderColor={useColorModeValue("#e2e8f0", "#334155")}
            color={textPrimary}
            value={pagination.pageSize}
            onChange={(e) => {
              const newSize = Number(e.target.value);
              setPagination((prev) => ({ ...prev, pageSize: newSize, pageIndex: 0 }));
            }}
          >
            {[10, 15, 25, 50, 100].map((size) => (
              <option
                key={size}
                value={size}
                style={{
                  backgroundColor: isDark ? "#0f172a" : "#ffffff",
                  color: isDark ? "#f1f5f9" : "#0f172a",
                }}
              >
                {size}
              </option>
            ))}
          </Select>
        </HStack>

        <Text fontSize="sm" color={textMuted} fontWeight="500">
          Página{" "}
          <Text as="span" fontWeight="700" color={textPrimary}>
            {table.getState().pagination.pageIndex + 1}
          </Text>{" "}
          de{" "}
          <Text as="span" fontWeight="700" color={textPrimary}>
            {Math.max(table.getPageCount(), 1)}
          </Text>
        </Text>

        <ButtonGroup size="sm" isAttached variant="outline">
          <IconButton
            icon={<ChevronsLeft size={16} />}
            aria-label="Primeira página"
            borderColor={useColorModeValue("#e2e8f0", "#334155")}
            color={textPrimary}
            _hover={{ bg: useColorModeValue("#f1f5f9", "#1e293b") }}
            onClick={() => setPagination((prev) => ({ ...prev, pageIndex: 0 }))}
            isDisabled={pagination.pageIndex === 0}
          />
          <IconButton
            icon={<ChevronLeft size={16} />}
            aria-label="Página anterior"
            borderColor={useColorModeValue("#e2e8f0", "#334155")}
            color={textPrimary}
            _hover={{ bg: useColorModeValue("#f1f5f9", "#1e293b") }}
            onClick={() =>
              setPagination((prev) => ({
                ...prev,
                pageIndex: Math.max(prev.pageIndex - 1, 0),
              }))
            }
            isDisabled={pagination.pageIndex === 0}
          />
          <IconButton
            icon={<ChevronRight size={16} />}
            aria-label="Próxima página"
            borderColor={useColorModeValue("#e2e8f0", "#334155")}
            color={textPrimary}
            _hover={{ bg: useColorModeValue("#f1f5f9", "#1e293b") }}
            onClick={() =>
              setPagination((prev) => ({
                ...prev,
                pageIndex: Math.min(prev.pageIndex + 1, table.getPageCount() - 1),
              }))
            }
            isDisabled={pagination.pageIndex >= table.getPageCount() - 1}
          />
          <IconButton
            icon={<ChevronsRight size={16} />}
            aria-label="Última página"
            borderColor={useColorModeValue("#e2e8f0", "#334155")}
            color={textPrimary}
            _hover={{ bg: useColorModeValue("#f1f5f9", "#1e293b") }}
            onClick={() =>
              setPagination((prev) => ({
                ...prev,
                pageIndex: Math.max(table.getPageCount() - 1, 0),
              }))
            }
            isDisabled={pagination.pageIndex >= table.getPageCount() - 1}
          />
        </ButtonGroup>
      </Flex>
    </Box>
  );
};

export default TaskTable;
