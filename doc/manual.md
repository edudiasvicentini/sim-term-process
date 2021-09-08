# Pré uso

Primeiramente, é necessário criar uma pasta no caminho C:
chamada `C:/iot_sim_proc` e uma subpasta nesse caminho, 
chamada `sim`. 
Na pasta `sim`, é necesário ser colocado os 6 arquivos da
simulação, sendo um o arquivo de referência e os  outros cinco 
arquivos com as adsortâncias 0.3, 0.5, 0.7, 0.8 e 0.9.

# Regras para a simulação

Os nomes dos comodos, que serão os cabeçalhos dos arquivos csv
utilizados como input, terão de seguir o formato 
**TORRE_PAVIMENTO_APARTAMENTO#_COMODO**, onde '#' é o número do ap.

Os comodos só serão reconhecidos no caso de comodo estar preenchido como
sala ou quarto, exatamente assim. Para o caso de kitnet, necessariamente, 
deverá vir no lugar de comodo a palavra studio.

O arquivo de referência será indentificado pela presença da palavra referencia 
no nome. As adissortâncias serão identificadas pela prensença do valor no nome,
de 0.1 a 0.9, com intervalo de 0.1.

Quando o pavimento for **cobertura** indicar por COB, para poder ser aplicado a 
regra de variação da temperatura máxima maior que a de outros pavimentos.


# Execução

Para executar, entre na pasta dist e execute o arquivo `main.exe`


# Pós

Após executar, os resultados ficaram no arquivo `results.csv`, na pasta root.
