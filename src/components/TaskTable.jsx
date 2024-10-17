import { useState, useEffect } from "react";
import { Box, Button, ButtonGroup, Icon, Text } from "@chakra-ui/react";
import {
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table";
import DATA from "../data";
import EditableCell from "./EditableCell";
//import StatusCell from "./StatusCell";
//import DateCell from "./DateCell";
import Filters from "./Filters";
import SortIcon from "./icons/SortIcon";
///////////////////////////////////////////////////////////
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
    //coluna "Nome_Municipio"
    accessorKey: "Nome_Municipio",
    header: "Nome Municipio",
    size: 180,
    cell: EditableCell,
  },
  {
    //Coordenada_X
    accessorKey: "Coordenada_X",
    header: "Coordenada X (m)",
    size: 180,
    cell: (props) => <p>{props.getValue()}</p>,
  },
  {
     //Coordenada_Y
    accessorKey: "Coordenada_Y",
    header: "Coordenada Y (m)",
    size: 180,
    cell: (props) => <p>{props.getValue()}</p>,
  },
  {
    //Ano_Inicio
    accessorKey: "Ano_Inicio",
    header: "Ano de Inicio",
    size: 160,
    cell: EditableCell,
  },
  {
     //Ano_Fim
    accessorKey: "Ano_Fim",
    header: "Ano de Fim",
    size: 160,
    cell: EditableCell,
  },
  {
     //Mes_Inicio
    accessorKey: "Mes_Inicio",
    header: "Mês de Inicio",
    size: 140,
    cell: EditableCell,
  },
  {
    //Mes_Fim
    accessorKey: "Mes_Fim",
    header: "Mês de Fim",
    size: 130,
    cell: EditableCell,
  },
  //Dados diarios meteriolologicos
   {
    //Total_dias_intervalo
    accessorKey: "Total_dias_intervalo",
    header: "Total de dias do intervalo",
    size: 225,
    cell: EditableCell,
  },
  {
    //Dias_dados_medidos
    accessorKey: "Dias_dados_medidos",
    header: "Número de dias com dados medidos",
    size: 225,
    cell: EditableCell,
  },
  {
    //Dias_falhos
    accessorKey: "Dias_falhos",
    header: "Número de dias com falhas",
    size: 225,
    cell: EditableCell,
  },
  {
    //Percentual_dias_falhos
    accessorKey: "Percentual_dias_falhos",
    header: "Percentual de dias com falhas (%)",
    size: 225,
    cell: EditableCell,
  },
  //Dados mensais meteriolologicos
  {
    //Total de meses do intervalo
    accessorKey: "Total_meses_intervalo",
    header: "Total de meses do intervalo",
    size: 225,
    cell: EditableCell,
  },
  {
    ///Nº de meses completos
    accessorKey: "Numero_meses_completos",
    header: "Nº de meses completos",
    size: 225,
    cell: EditableCell,
  },
  {
    //Nº de meses com falhas
    accessorKey: "Numero_meses_falha",
    header: "Nº de meses com falhas",
    size: 225,
    cell: EditableCell,
  },
  {
    //Percentual de meses com falhas (%)
    accessorKey: "Percentual_meses_falha",
    header: "Percentual de meses com falhas (%)",
    size: 225,
    cell: EditableCell,
  },
//Dados Anuais meteriolologicos
{
  //Total de anos do intervalo
  accessorKey: "Total_anos_intervalo",
  header: "Total de anos do intervalo",
  size: 225,
  cell: EditableCell,
},
{
  ///Nº de anos completos
  accessorKey: "Numero_anos_completos",
  header: "Nº de anos completos",
  size: 225,
  cell: EditableCell,
},
{
  //Nº de anos com falhas
  accessorKey: "Numero_anos_falha",
  header: "Nº de anos com falhas",
  size: 225,
  cell: EditableCell,
},
{
  //Percentual de anos com falhas (%)
  accessorKey: "Percentual_anos_falha",
  header: "Percentual de anos com falhas (%)",
  size: 225,
  cell: EditableCell,
},
//precipitação media anual
{
  //Precipitação média anual (mm)
  accessorKey: "Precipitacao_media_anual",
  header: "Precipitação média anual (mm)",
  size: 225,
  cell: EditableCell,
},

{
  //coluna "Precipitação em Janeiro"
  accessorKey: "Jan_chuva",
  header: "Jan (mm)",
  size: 200,
  cell: (props) => <p>{props.getValue()}</p>,
  enableColumnFilter: true,
  filterFn: "includesString",

},
{
  //coluna "Precipitação em Fervereiro"
  accessorKey: "Fev_chuva",
  header: "Feb (mm)",
  size: 200,
  cell: (props) => <p>{props.getValue()}</p>,
  enableColumnFilter: true,
  filterFn: "includesString",

},
{
  //coluna "Precipitação em Fervereiro"
  accessorKey: "Mar_chuva",
  header: "Mar (mm)",
  size: 200,
  cell: (props) => <p>{props.getValue()}</p>,
  enableColumnFilter: true,
  filterFn: "includesString",

},
{
  //coluna "Precipitação em Fervereiro"
  accessorKey: "Apr_chuva",
  header: "Apr (mm)",
  size: 200,
  cell: (props) => <p>{props.getValue()}</p>,
  enableColumnFilter: true,
  filterFn: "includesString",

},
{
  //coluna "Precipitação em Fervereiro"
  accessorKey: "Apr_chuva",
  header: "Apr (mm)",
  size: 200,
  cell: (props) => <p>{props.getValue()}</p>,
  enableColumnFilter: true,
  filterFn: "includesString",

},
{
  //coluna "Precipitação em Fervereiro"
  accessorKey: "May_chuva",
  header: "May (mm)",
  size: 200,
  cell: (props) => <p>{props.getValue()}</p>,
  enableColumnFilter: true,
  filterFn: "includesString",

},
{
  //coluna "Precipitação em Fervereiro"
  accessorKey: "Jun_chuva",
  header: "Jun (mm)",
  size: 200,
  cell: (props) => <p>{props.getValue()}</p>,
  enableColumnFilter: true,
  filterFn: "includesString",

},
{
  //coluna "Precipitação em Fervereiro"
  accessorKey: "Jul_chuva",
  header: "Jul (mm)",
  size: 200,
  cell: (props) => <p>{props.getValue()}</p>,
  enableColumnFilter: true,
  filterFn: "includesString",

},
{
  //coluna "Precipitação em Fervereiro"
  accessorKey: "Aug_chuva",
  header: "Aug (mm)",
  size: 200,
  cell: (props) => <p>{props.getValue()}</p>,
  enableColumnFilter: true,
  filterFn: "includesString",

},
{
  //coluna "Precipitação em Fervereiro"
  accessorKey: "Sep_chuva",
  header: "Sep (mm)",
  size: 200,
  cell: (props) => <p>{props.getValue()}</p>,
  enableColumnFilter: true,
  filterFn: "includesString",

},
{
  //coluna "Precipitação em Fervereiro"
  accessorKey: "Oct_chuva",
  header: "Oct (mm)",
  size: 200,
  cell: (props) => <p>{props.getValue()}</p>,
  enableColumnFilter: true,
  filterFn: "includesString",

},
{
  //coluna "Precipitação em Fervereiro"
  accessorKey: "Nov_chuva",
  header: "Nov (mm)",
  size: 200,
  cell: (props) => <p>{props.getValue()}</p>,
  enableColumnFilter: true,
  filterFn: "includesString",

},
{
  //coluna "Precipitação em Fervereiro"
  accessorKey: "Dec_chuva",
  header: "Dec (mm)",
  size: 200,
  cell: (props) => <p>{props.getValue()}</p>,
  enableColumnFilter: true,
  filterFn: "includesString",

},

];
const TaskTable = () => {
  
  const [data, setData] = useState(DATA);

  const [columnFilters, setColumnFilters] = useState([]);

  const table = useReactTable({
    data,
    columns,
    state: {
      columnFilters,
    },
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    columnResizeMode: "onChange",
    meta: {
      updateData: (rowIndex, columnId, value) =>
        setData((prev) =>
          prev.map((row, index) =>
            index === rowIndex
              ? {
                  ...prev[rowIndex],
                  [columnId]: value,
                }
              : row
          )
        ),
    },
  });

  return (
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
                {
                  {
                    asc: " 🔼",
                    desc: " 🔽",
                  }[header.column.getIsSorted()]
                }
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
      <br />
      {/*Legenda dos Botoes de paginação*/}
      <Text mb={2}>
      Página {table.getState().pagination.pageIndex + 1} de{" "}
        {table.getPageCount()}
      </Text>
      <ButtonGroup size="sm" isAttached variant="outline">
        <Button
         color="black"
          onClick={() => table.previousPage()}
          isDisabled={!table.getCanPreviousPage()}
        >
          {"<"}
        </Button>
        <Button
          color="black"
          onClick={() => table.nextPage()}
          isDisabled={!table.getCanNextPage()}
        >
          {">"}
        </Button>
      </ButtonGroup>
    </Box>
  );
};
export default TaskTable;