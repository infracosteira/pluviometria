import { Box, Heading } from "@chakra-ui/react";
import TaskTable from "./components/TaskTable";
import Logo from "./components/img/Logo_Infracosteira.jpeg";

function App() {
  return (
    <Box maxW="1400px" mx="auto" px={6} pt={24} fontSize="sm">
      <Box
        display="flex"
        alignItems="center"
        flexWrap="wrap"
        flexDirection={{ base: "column", sm: "row" }} // Responsividade: coluna em telas < 400px
      >
        {/* Imagens alinhadas à direita, responsivas */}
        <Box
          display="flex"
          justifyContent="center"
          flexWrap="wrap"
          gap={4}
          pb={4}
          mb={6} // Margem inferior entre a linha e a logo
          borderBottom="1px solid #ccc"
        >
          <Box>
            <img
              src="https://logodownload.org/wp-content/uploads/2016/09/ufc-logo-universidade.png"
              alt="UFC logo"
              style={{ height: "40px" }}
            />
          </Box>
          <Box>
            <img
              src="https://www.unilab.edu.br/wp-content/uploads/2014/02/Logo-Unilab-vertical-para-fundo-claro.jpg"
              alt="Unilab logo"
              style={{ height: "40px" }}
            />
          </Box>
          <Box>
            <img
              src="https://files.passeidireto.com/d02ca57a-be06-46fe-8761-acba8bcf27fb/d02ca57a-be06-46fe-8761-acba8bcf27fb.png"
              alt="IFCE logo"
              style={{ height: "40px" }}
            />
          </Box>
          <Box>
            <img
              src="https://www.uece.br/wp-content/uploads/2019/11/logouececentcolor.png"
              alt="UECE logo"
              style={{ height: "40px" }}
            />
          </Box>
          <Box>
            <img
              src="https://www.funcap.ce.gov.br/wp-content/uploads/sites/52/2018/08/Logomarca-Cientista-Chefe-CMYK.png"
              alt="Cientista logo"
              style={{ height: "40px" }}
            />
          </Box>
          <Box>
            <img
              src="https://www.funcap.ce.gov.br/wp-content/uploads/sites/52/2015/07/funcap.png"
              alt="Funcap Logo"
              style={{ height: "40px" }}
            />
          </Box>
          <Box>
            <img
              src="https://www.seduc.ce.gov.br/wp-content/uploads/sites/37/2021/04/001_marca_vertical_color.png"
              alt="SEDUC logo"
              style={{ height: "40px" }}
            />
          </Box>
        </Box>
        <Box
          display="flex"
          justifyContent={{ base: "center", sm: "flex-start" }} // Centraliza para telas pequenas, ajusta para grandes
          alignItems="center"
          gap={5}
          ml={{ base: 0, sm: 130 }} // ml 130 em telas grandes, 0 em pequenas
          flexWrap="wrap"
        >
          <img
            src={Logo}
            alt="Logo Infracosteira"
            style={{ width: "50px", height: "50px" }}
          />
          <Heading size="md">Infracosteira</Heading>
        </Box>
      </Box>

      {/* Tabela */}
      <Box maxW="100%" overflowX="auto" textAlign="right" mt={8}>
        <TaskTable />
      </Box>
    </Box>
  );
}

export default App;
