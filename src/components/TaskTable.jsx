import { useState, useEffect } from "react";
import { Input } from '@chakra-ui/react';
import { Box, Button, ButtonGroup, Icon, Text, Grid, GridItem } from "@chakra-ui/react";
import {
  flexRender,
  getCoreRowModel,
  getFilteredRowModel, 
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table";
import EditableCell from "./EditableCell";
import Filters from "./Filters";
import SortIcon from "./icons/SortIcon";
import axios from 'axios';
import JsonData from './../../data/dados_formatados_resumo.json';

async function downloadFile(fileUrl) {
  try {
    const response = await axios.get(fileUrl, {
      responseType: 'blob',
      headers: {
        'Content-Type': 'text/csv', 
      },
    });
    
    console.log("response:", response);
    
    if (response.status !== 200) {
      throw new Error(`Erro ${response.status}: ${response.statusText}`);
    }

    const blob = response.data;
    console.log("blob:", blob);
    
    const link = document.createElement('a');
    link.href = window.URL.createObjectURL(blob);
    link.download = fileUrl.split('/').pop();
    link.click();

    window.URL.revokeObjectURL(link.href);
  } catch (error) {
    console.error('Erro ao buscar ou processar o arquivo CSV:', error);
  }
}

const columns = [
  {
    accessorKey: "ID",
    header: "ID",
    size: 150,
    cell: (props) => <p>{props.getValue()}</p>,
    enableColumnFilter: true,
    filterFn: "includesString",
  },
  {
    accessorKey: "Nome_Posto",
    header: "Nome do Posto",
    size: 186,
    cell: (props) => <p>{props.getValue()}</p>,
    enableColumnFilter: true,
    filterFn: "includesString",
  },
  {
    accessorKey: "download",
    header: "Download",
    size: 150, 
    cell: (props) => {
      return (
        <button
          onClick={() => {
            downloadFile(props.row.original.link_csv);
          }}
        >
          ⬇️  
        </button>
      );
    },
  },
  {
    accessorKey: "Nome_Municipio",
    header: "Nome Municipio",
    size: 215,
    cell: EditableCell,
  },
  {
    accessorKey: "Numero_anos_completos",
    header: "Nº de anos completos",
    size: 200,
    cell: EditableCell,
  },
  {
    accessorKey: "Ano_Inicio",
    header: "Ano de Inicio",
    size: 150,
    cell: EditableCell,
  },
  {
    accessorKey: "Ano_Fim",
    header: "Ano de Fim",
    size: 150,
    cell: EditableCell,
  },
  {
    accessorKey: "Mapa",
    header: "Mapa",
    size: 101,
    cell: (props) => <a href={`https://maps.google.com/?q=${props.row.original.Coordenada_Y},${props.row.original.Coordenada_X}`} target='_blank'>🌎</a>,
  }
];

const expandedColumns = [
  {
    accessorKey: "Coordenada_X",
    header: "Coord_X",
    size: 130,
    cell: (props) => <p>{props.getValue()}</p>,
  },
  {
    accessorKey: "Coordenada_Y",
    header: "Coord_Y",
    size: 130,
    cell: (props) => <p>{props.getValue()}</p>,
  },
  {
    accessorKey: "Mes_Inicio",
    header: "Mês de inicio",
    size: 100,
    cell: EditableCell,
  },
  {
    accessorKey: "Mes_Fim",
    header: "Mês de fim",
    size: 100,
    cell: EditableCell,
  },
  {
    accessorKey: "Total_Dias_intervalo",
    header: "Nº total do intervalo",
    size: 150,
    cell: EditableCell,
  },
  {
    accessorKey: "Dias_dados_medidos",
    header: "Dias com dados medidos",
    size: 160,
    cell: EditableCell,
  },
  {
    accessorKey: "Dias_falhos",
    header: "Dias com falhas",
    size: 130,
    cell: EditableCell,
  },
  {
    accessorKey: "Percentual_dias_falhos",
    header: "Percentual de dias com falhas (%)",
    size: 190,
    cell: EditableCell,
  },
  {
    accessorKey: "Total_meses_intervalo",
    header: "Total de meses do intervalo",
    size: 150,
    cell: EditableCell,
  },
  {
    accessorKey: "Numero_meses_completos",
    header: "Nº de meses completos",
    size: 150,
    cell: EditableCell,
  },
  {
    accessorKey: "Numero_meses_falha",
    header: "Nº de meses com falhas",
    size: 150,
    cell: EditableCell,
  },
  {
    accessorKey: "Percentual_meses_falha",
    header: "Percentual de meses com falhas (%)",
    size: 190,
    cell: EditableCell,
  },
  {
    accessorKey: "Total_anos_intervalo",
    header: "Total de anos do intervalo",
    size: 150,
    cell: EditableCell,
  },
  {
    accessorKey: "Numero_anos_falha",
    header: "Nº de anos com falhas",
    size: 150,
    cell: EditableCell,
  },
  {
    accessorKey: "Percentual_anos_falha",
    header: "Percentual de anos com falhas (%)",
    size: 190,
    cell: EditableCell,
  },
  {
    accessorKey: "Precipitacao_media_anual",
    header: "Precipitação média anual (mm)",
    size: 175,
    cell: EditableCell,
  },
  {
    accessorKey: "Mes_Jan",
    header: "Jan (mm)",
    size: 115,
    cell: (props) => <p>{props.getValue()}</p>,
    enableColumnFilter: true,
    filterFn: "includesString",
  },
  {
    accessorKey: "Mes_Fev",
    header: "Feb (mm)",
    size: 115,
    cell: (props) => <p>{props.getValue()}</p>,
    enableColumnFilter: true,
    filterFn: "includesString",
  },
  {
    accessorKey: "Mes_Mar",
    header: "Mar (mm)",
    size: 115,
    cell: (props) => <p>{props.getValue()}</p>,
    enableColumnFilter: true,
    filterFn: "includesString",
  },
  {
    accessorKey: "Mes_Apr",
    header: "Apr (mm)",
    size: 115,
    cell: (props) => <p>{props.getValue()}</p>,
    enableColumnFilter: true,
    filterFn: "includesString",
  },
  {
    accessorKey: "Mes_May",
    header: "May (mm)",
    size: 115,
    cell: (props) => <p>{props.getValue()}</p>,
    enableColumnFilter: true,
    filterFn: "includesString",
  },
  {
    accessorKey: "Mes_Jun",
    header: "Jun (mm)",
    size: 115,
    cell: (props) => <p>{props.getValue()}</p>,
    enableColumnFilter: true,
    filterFn: "includesString",
  },
  {
    accessorKey: "Mes_Jul",
    header: "Jul (mm)",
    size: 115,
    cell: (props) => <p>{props.getValue()}</p>,
    enableColumnFilter: true,
    filterFn: "includesString",
  },
  {
    accessorKey: "Mes_Aug",
    header: "Aug (mm)",
    size: 115,
    cell: (props) => <p>{props.getValue()}</p>,
    enableColumnFilter: true,
    filterFn: "includesString",
  },
  {
    accessorKey: "Mes_Sep",
    header: "Sep (mm)",
    size: 115,
    cell: (props) => <p>{props.getValue()}</p>,
    enableColumnFilter: true,
    filterFn: "includesString",
  },
  {
    accessorKey: "Mes_Oct",
    header: "Oct (mm)",
    size: 115,
    cell: (props) => <p>{props.getValue()}</p>,
    enableColumnFilter: true,
    filterFn: "includesString",
  },
  {
    accessorKey: "Mes_Nov",
    header: "Nov (mm)",
    size: 115,
    cell: (props) => <p>{props.getValue()}</p>,
    enableColumnFilter: true,
    filterFn: "includesString",
  },
  {
    accessorKey: "Mes_Dec",
    header: "Dec (mm)",
    size: 115,
    cell: (props) => <p>{props.getValue()}</p>,
    enableColumnFilter: true,
    filterFn: "includesString",
  },
];

const TaskTable = () => {
  const [data, setData] = useState([]);
  const [columnFilters, setColumnFilters] = useState([]);
  const [pageSize, setPageSize] = useState(15);

  async function fetchDataFromGitHub() {
    try {
      const response = await fetch('https://raw.githubusercontent.com/infracosteira/pluviometria/refs/heads/main/data/dados_formatados_resumo.json');
      
      if (!response.ok) {
        throw new Error(`Erro ao buscar dados: ${response.statusText}`);
      }

      const jsonData = await response.json();
      setData(jsonData);
    } catch (error) {
      console.error('Erro ao carregar os dados:', error);
    }
  }

  useEffect(() => {
    fetchDataFromGitHub();
  }, []);

  const [pagination, setPagination] = useState({
    pageIndex: 0,
    pageSize: 15
  });
  
  const table = useReactTable({
    data,
    columns,
    state: {
      columnFilters,
      pagination
    },
    onPaginationChange: setPagination,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    columnResizeMode: "onChange",
  });

  const [expandedRows, setExpandedRows] = useState({});

  const toggleRowExpansion = (rowIndex) => {
    setExpandedRows((prev) => ({
      ...prev,
      [rowIndex]: !prev[rowIndex],
    }));
  };

  return (
    <Box>
      <Box>
        <Filters
          columnFilters={columnFilters}
          setColumnFilters={setColumnFilters}
        />
        <Box className="table">
          {table.getHeaderGroups().map((headerGroup) => (
            <Box className="tr" key={headerGroup.id}>
              <Box className="th" w={50}>
              </Box>
              {headerGroup.headers.map((header) => (
                <Box className="th" w={header.getSize()} key={header.id}>
                  {header.column.columnDef.header}
                  {header.column.getCanSort() && (
                    <Icon
                      as={SortIcon}
                      mx={3}
                      fontSize={14}
                      onClick={header.column.getToggleSortingHandler()}
                    />
                  )}
                  {{
                    asc: " 🔼",
                    desc: " 🔽",
                  }[header.column.getIsSorted()]}
                  <Box
                    onMouseDown={header.getResizeHandler()}
                    onTouchStart={header.getResizeHandler()}
                    className={`resizer ${
                      header.column.getIsResizing() ? "isResizing" : ""
                    }`}
                  />
                </Box>
              ))}
            </Box>
          ))}
          {table.getRowModel().rows.map((row) => (
            <Box key={row.id}>
              <Box className="tr">
                <Box className="td" w={50}>
                  <Button onClick={() => toggleRowExpansion(row.index)}>
                    {expandedRows[row.index] ? "🔽" : "▶️"}
                  </Button>
                </Box>
                {row.getVisibleCells().map((cell) => (
                  <Box className="td" w={cell.column.getSize()} key={cell.id}>
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </Box>
                ))}
              </Box>
              {expandedRows[row.index] && (
                <Grid templateColumns="repeat(4, 1fr)" gap={4} className="expanded-content">
                  {expandedColumns.map((col) => (
                    <GridItem key={col.accessorKey}>
                      <Text fontWeight="bold">{col.header}:</Text>
                      {flexRender(col.cell, {
                        getValue: () => row.original[col.accessorKey],
                      })}
                    </GridItem>
                  ))}
                </Grid>
              )}
            </Box>
          ))}
        </Box>
        <br />
        <Box>
          <Box alignItems="center" display="inline-block" width="720" heigh="540" mr={9}>
            <Text mb={2}>
              Página {table.getState().pagination.pageIndex + 1} de{" "}
              {table.getPageCount()}
            </Text>
            <ButtonGroup size="sm" isAttached variant="outline">
              <Button
                color="black"
                borderColor="black"
                onClick={() => {
                  setPagination((prev) => ({
                    ...prev,
                    pageIndex: Math.max(prev.pageIndex - 1, 0),
                  }));
                }}
                isDisabled={pagination.pageIndex === 0}
              >
                {"<"}
              </Button>

              <Button
                color="black"
                borderColor="black"
                onClick={() => {
                  setPagination((prev) => ({
                    ...prev,
                    pageIndex: Math.min(prev.pageIndex + 1, table.getPageCount() - 1),
                  }));
                }}
                isDisabled={pagination.pageIndex >= table.getPageCount() - 1}
              >
                {">"}
              </Button>
            </ButtonGroup>
          </Box>
          <Box
            spacing={3}
            alignItems="center"
            display="inline-block"
            width="720"
            heigh="540"
            left="50"
          >
            <Text mb={2}>Linhas por página:</Text>
            <Input
              type="number"
              alignItems="center"
              height="30px"
              width="70px"
              value={pageSize}
              onChange={(e) => {
                const value = e.target.value ? Number(e.target.value) : null;
                setPageSize(value);
                table.setPageSize(value);
              }}
              min={0}
              max={100}
            />
          </Box>
          <Box mt={4}>
            <Button
              colorScheme="green"
              onClick={() => {
                const fileUrl = "https://github.com/infracosteira/pluviometria/raw/main/data/todos_os_postos.rar";
                const link = document.createElement("a");
                link.href = fileUrl;
                link.download = "todos_os_postos.rar";
                link.click();
              }}
            >
              Baixar todos os postos
            </Button>
          </Box>
        </Box>
      </Box>
    </Box>
  );
};

export default TaskTable;
