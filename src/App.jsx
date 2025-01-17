import { Box, Heading } from "@chakra-ui/react";
import TaskTable from "./components/TaskTable";
import Logo from "./components/img/Logo_Infracosteira.jpeg";

function App() {
  return (
    <Box maxW="1400px" mx="auto" px={6} pt={24} fontSize="sm">
      <Box display="flex" alignItems="center" flexWrap="wrap">
        {/* Logo Infracosteira e Título */}
        <Box display="flex" alignItems="center" flex="1">
          <img
            src={Logo}
            alt="Logo_Infracosteira"
            width="50"
            height="50"
            style={{ marginRight: "10px" }}
          />
          <Heading>Infracosteira</Heading>
        </Box>

        {/* Imagens alinhadas à direita, responsivas */}
        <Box
          display="flex"
          alignItems="center"
          ml="auto"
          maxW="78%"
          flexWrap="wrap"
          justifyContent={{ base: "center", md: "flex-end" }} // Centralizado em telas pequenas
          gap={2} // Espaçamento entre os elementos
        >
          <Box>
            <img
              src="https://logodownload.org/wp-content/uploads/2016/09/ufc-logo-universidade.png"
              alt="UFC logo"
              style={{
                height: "40px", // Altura ajustada para telas pequenas
                margin: "5px",
              }}
            />
          </Box>
          <Box>
            <img
              src="https://www.unilab.edu.br/wp-content/uploads/2014/02/Logo-Unilab-vertical-para-fundo-claro.jpg"
              alt="Unilab logo"
              style={{
                height: "40px",
                margin: "5px",
              }}
            />
          </Box>
          <Box>
            <img
              src="https://files.passeidireto.com/d02ca57a-be06-46fe-8761-acba8bcf27fb/d02ca57a-be06-46fe-8761-acba8bcf27fb.png"
              alt="IFCE logo"
              style={{
                height: "40px",
                margin: "5px",
              }}
            />
          </Box>
          <Box>
            <img
              src="https://www.uece.br/wp-content/uploads/2019/11/logouececentcolor.png"
              alt="UECE logo"
              style={{
                height: "40px",
                margin: "5px",
              }}
            />
          </Box>
          <Box>
            <img
              src="https://www.funcap.ce.gov.br/wp-content/uploads/sites/52/2018/08/Logomarca-Cientista-Chefe-CMYK.png"
              alt="Cientista logo"
              style={{
                height: "40px",
                margin: "5px",
              }}
            />
          </Box>
          <Box>
            <img
              src="https://www.funcap.ce.gov.br/wp-content/uploads/sites/52/2015/07/funcap.png"
              alt="Funcap Logo"
              style={{
                height: "40px",
                margin: "5px",
              }}
            />
          </Box>
          <Box>
            <img
              src="https://www.seduc.ce.gov.br/wp-content/uploads/sites/37/2021/04/001_marca_vertical_color.png"
              alt="SEDUC logo"
              style={{
                height: "40px",
                margin: "5px",
              }}
            />
          </Box>
        </Box>
      </Box>

      {/* Tabela */}
      <Box maxW="100%" overflowX="center" textAlign="right" mt={8}>
        <TaskTable />
      </Box>
    </Box>
  );
}

export default App;
