import { useState, useEffect } from "react";
import { Input } from '@chakra-ui/react';
import { Box, Button, ButtonGroup, Icon, Text } from "@chakra-ui/react";
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
    
    // Verifique se a resposta foi bem-sucedida
    if (response.status !== 200) {
      throw new Error(`Erro ${response.status}: ${response.statusText}`);
    }

    const blob = response.data; // response.data já é um Blob
    console.log("blob:", blob);
    
    const link = document.createElement('a');
    link.href = window.URL.createObjectURL(blob);
    link.download = fileUrl.split('/').pop(); // Define o nome do arquivo a partir da URL
    link.click();

    // Limpa o objeto URL após o uso
    window.URL.revokeObjectURL(link.href);
  } catch (error) {
    console.error('Erro ao buscar ou processar o arquivo CSV:', error);
  }
}

const columns = [
  {
    //coluna "id"
    accessorKey: "Chave_ID",
    header: "ID",
    size: 70,
    cell: (props) => <p>{props.getValue()}</p>,
    enableColumnFilter: true,
    filterFn: "includesString",
  },
  {
    //coluna "Nome do posto"
    accessorKey: "Nome_Posto",
    header: "Nome do Posto",
    size: 200,
    cell: (props) => <p>{props.getValue()}</p>,
    enableColumnFilter: true,
    filterFn: "includesString",
    },

    {
      accessorKey: "download",
      header: "➥",
      size: 90, 
      cell: (props) => {
        return (
          <button
            onClick={() => {
              console.log(props.row.original.link_csv);
              downloadFile(props.row.original.link_csv); // Chama a função de download com o link CSV
            }}
          >
            Baixar
          </button>
        );
      },
    },

  {
    //coluna "Nome_Municipio"
    accessorKey: "Nome_Municipio",
    header: "Nome Municipio",
    size: 180,
    cell: EditableCell,
  },
  {
    //Coordenada_X
    accessorKey: "Coordenada_X",
    header: "Coord_X",
    size: 120,
    cell: (props) => <p>{props.getValue()}</p>,
  },
  {
     //Coordenada_Y
    accessorKey: "Coordenada_Y",
    header: "Coord_Y",
    size: 120,
    cell: (props) => <p>{props.getValue()}</p>,
  },
  {
    //Ano_Inicio
    accessorKey: "Ano_Inicio",
    header: "Ano de Inicio",
    size: 100,
    cell: EditableCell,
  },
  {
     //Ano_Fim
    accessorKey: "Ano_Fim",
    header: "Ano de Fim",
    size: 100,
    cell: EditableCell,
  },
  {
     //Mes_Inicio
    accessorKey: "Mes_Inicio",
    header: "Mês de Inicio",
    size: 100,
    cell: EditableCell,
  },
  {
    //Mes_Fim
    accessorKey: "Mes_Fim",
    header: "Mês de Fim",
    size: 100,
    cell: EditableCell,
  },
  //Dados diarios meteriolologicos
   {
    //Total_dias_intervalo
    accessorKey: "Total_dias_intervalo",
    header: "Nº total do intervalo",
    size: 150,
    cell: EditableCell,
  },
  {
    //Dias_dados_medidos
    accessorKey: "Dias_dados_medidos",
    header: "Dias com dados medidos",
    size: 160,
    cell: EditableCell,
  },
  {
    //Dias_falhos
    accessorKey: "Dias_falhos",
    header: "dias com falhas",
    size: 130,
    cell: EditableCell,
  },
  {
    //Percentual_dias_falhos
    accessorKey: "Percentual_dias_falhos",
    header: "Percentual de dias com falhas (%)",
    size: 190,
    cell: EditableCell,
  },
  //Dados mensais meteriolologicos
  {
    //Total de meses do intervalo
    accessorKey: "Total_meses_intervalo",
    header: "Total de meses do intervalo",
    size: 150,
    cell: EditableCell,
  },
  {
    ///Nº de meses completos
    accessorKey: "Numero_meses_completos",
    header: "Nº de meses completos",
    size: 150,
    cell: EditableCell,
  },
  {
    //Nº de meses com falhas
    accessorKey: "Numero_meses_falha",
    header: "Nº de meses com falhas",
    size: 150,
    cell: EditableCell,
  },
  {
    //Percentual de meses com falhas (%)
    accessorKey: "Percentual_meses_falha",
    header: "Percentual de meses com falhas (%)",
    size: 190,
    cell: EditableCell,
  },
//Dados Anuais meteriolologicos
{
  //Total de anos do intervalo
  accessorKey: "Total_anos_intervalo",
  header: "Total de anos do intervalo",
  size: 150,
  cell: EditableCell,
},
{
  ///Nº de anos completos
  accessorKey: "Numero_anos_completos",
  header: "Nº de anos completos",
  size: 150,
  cell: EditableCell,
},
{
  //Nº de anos com falhas
  accessorKey: "Numero_anos_falha",
  header: "Nº de anos com falhas",
  size: 150,
  cell: EditableCell,
},
{
  //Percentual de anos com falhas (%)
  accessorKey: "Percentual_anos_falha",
  header: "Percentual de anos com falhas (%)",
  size: 190,
  cell: EditableCell,
},
//precipitação media anual
{
  //Precipitação média anual (mm)
  accessorKey: "Precipitacao_media_anual",
  header: "Precipitação média anual (mm)",
  size: 175,
  cell: EditableCell,
},

{
  //coluna "Precipitação em Janeiro"
  accessorKey: "Mes_Jan",
  header: "Jan (mm)",
  size: 115,
  cell: (props) => <p>{props.getValue()}</p>,
  enableColumnFilter: true,
  filterFn: "includesString",

},
{
  //coluna "Precipitação em Fervereiro"
  accessorKey: "Mes_Fev",
  header: "Feb (mm)",
  size: 115,
  cell: (props) => <p>{props.getValue()}</p>,
  enableColumnFilter: true,
  filterFn: "includesString",

},
{
  //coluna "Precipitação em Fervereiro"
  accessorKey: "Mes_Mar",
  header: "Mar (mm)",
  size: 115,
  cell: (props) => <p>{props.getValue()}</p>,
  enableColumnFilter: true,
  filterFn: "includesString",

},
{
  //coluna "Precipitação em Fervereiro"
  accessorKey: "Mes_Apr",
  header: "Apr (mm)",
  size: 115,
  cell: (props) => <p>{props.getValue()}</p>,
  enableColumnFilter: true,
  filterFn: "includesString",

},
{
  //coluna "Precipitação em Fervereiro"
  accessorKey: "Mes_May",
  header: "May (mm)",
  size: 115,
  cell: (props) => <p>{props.getValue()}</p>,
  enableColumnFilter: true,
  filterFn: "includesString",

},
{
  //coluna "Precipitação em Fervereiro"
  accessorKey: "Mes_Jun",
  header: "jun (mm)",
  size: 115,
  cell: (props) => <p>{props.getValue()}</p>,
  enableColumnFilter: true,
  filterFn: "includesString",

},
{
  //coluna "Precipitação em Fervereiro"
  accessorKey: "Mes_Jul",
  header: "Jul (mm)",
  size: 115,
  cell: (props) => <p>{props.getValue()}</p>,
  enableColumnFilter: true,
  filterFn: "includesString",

},
{
  //coluna "Precipitação em Fervereiro"
  accessorKey: "Mes_Aug",
  header: "Aug (mm)",
  size: 115,
  cell: (props) => <p>{props.getValue()}</p>,
  enableColumnFilter: true,
  filterFn: "includesString",

},
{
  //coluna "Precipitação em Fervereiro"
  accessorKey: "Mes_Sep",
  header: "Sep (mm)",
  size: 115,
  cell: (props) => <p>{props.getValue()}</p>,
  enableColumnFilter: true,
  filterFn: "includesString",

},
{
  //coluna "Precipitação em Fervereiro"
  accessorKey: "Mes_Oct",
  header: "Oct (mm)",
  size: 115,
  cell: (props) => <p>{props.getValue()}</p>,
  enableColumnFilter: true,
  filterFn: "includesString",

},
{
  //coluna "Precipitação em Fervereiro"
  accessorKey: "Mes_Nov",
  header: "Nov (mm)",
  size: 115,
  cell: (props) => <p>{props.getValue()}</p>,
  enableColumnFilter: true,
  filterFn: "includesString",

},
{
  //coluna "Precipitação em Fervereiro"
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

  // Função para buscar os dados do GitHub
  
  async function fetchDataFromGitHub() {
    try {
      const response = await fetch('https://raw.githubusercontent.com/infracosteira/pluviometria/refs/heads/main/data/dados_formatados_resumo.json');
      
      if (!response.ok) {
        throw new Error(`Erro ao buscar dados: ${response.statusText}`);
      }

      const jsonData = await response.json(); // Parse do JSON
      setData(jsonData); // Atualiza o estado com os dados carregados
    } catch (error) {
      console.error('Erro ao carregar os dados:', error);
    }
  }

  // useEffect para buscar os dados quando o componente é montado
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
  
  

  return (
    <Box>
      <Box>
        <Filters
          columnFilters={columnFilters}
          setColumnFilters={setColumnFilters}
          
        />
        <Box className="table" w={table.getTotalSize()}>
          {table.getHeaderGroups().map((headerGroup) => (
            <Box className="tr" key={headerGroup.id}>
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
            <Box className="tr" key={row.id}>
              {row.getVisibleCells().map((cell) => (
                <Box className="td" w={cell.column.getSize()} key={cell.id}>
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </Box>
              ))}
            </Box>
          ))}
        </Box>
        <br/>
        <Box>
          {/* Paginacão */}
          <Box  
            alignItems="center" 
            display="inline-block"
            width="720"
            heigh="540"
            mr={9}
          >
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
              height='30px'
              width='70px'
              value={pageSize}
              onChange={(e) => {
                const value = e.target.value ? Number(e.target.value) : 10;
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
   {/* <Button
        onClick={() => {
          alert(`Legendas:
          TDD: Total de dias do intervalo
          NDM: Número de dias com dados medidos
          DF: Número de dias com falhas
          PDF: Percentual de dias com falhas
          TMI: Total de meses do intervalo
          NMC: Número de meses completos
          NMCF: Número de meses com falhas
          PMF: Percentual de meses com falhas
          TAI: Total de anos do intervalo
          NAC: Número de anos completos
          NAF: Número de anos com falhas
          PAF: Percentual de anos com falhas
          PMA: Precipitação média anual`);
        }}
      >
        ℹ️
      </Button> */}
      <br/>
    </Box>

        </Box>    
      </Box>
    </Box>
  );
};

export default TaskTable;
