import { Box, Heading } from "@chakra-ui/react";
import TaskTable from "./components/TaskTable";
import Logo from "./components/img/Logo_Infracosteira.jpeg";
function App() {
  return (
    <Box maxW={2000} mx="auto" px={6} pt={24} fontSize="sm"  display="inline-block">
      <img src={Logo} alt="Logo_Infracosteira" width="50" height ="50" align="left"/>
      <Heading mb={10}>&nbsp;Infracosteira</Heading>
      <TaskTable />
    </Box>
  );
}
export default App;
