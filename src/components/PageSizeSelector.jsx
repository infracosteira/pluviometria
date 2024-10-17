// PageSizeSelector.js
import React from 'react';
import { Box, Text, Input } from '@chakra-ui/react';

const PageSizeSelector = ({ pageSize, setPageSize }) => {
  return (
    <Box mt={4} display="flex" alignItems="center" float="right">
      <Text>Linhas por página:</Text>
      <Input
        type="number"
        value={pageSize}
        onChange={(e) => {
          const value = e.target.value ? Number(e.target.value) : 30; // Padrão para 30 se o valor for inválido
          setPageSize(value); // Atualiza o estado de pageSize
        }}
        min={1}  // Mínimo de 1 linha por página
        max={100}  // Máximo de 100 linhas por página (opcional)
        width="70px"
        bg="gray.50"
        placeholder="quantidade de linhas"
      />
    </Box>
  );
};

export default PageSizeSelector;
