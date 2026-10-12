# requirements.md: Módulo de Recomendação de Produtos

> Projeto principal: **Origem**.
> Os identificadores RF e RNF são os mesmos do Documento de Requisitos de Software do módulo.
> Convenções: "peça" é um produto artesanal cadastrado no Origem; "sistema principal" é o back-end do Origem, único consumidor da API do módulo.

## Requisitos Funcionais

### RF-01: Recomendações de Peças Similares

*História de usuário*

Como comprador que está vendo uma peça, quero receber recomendações de outras peças feitas com a mesma técnica artesanal, priorizando as do mesmo polo de origem, para descobrir peças relacionadas ao que me interessa.

*Critérios de aceitação (EARS)*

- QUANDO a requisição informar uma peça de referência com técnica artesanal cadastrada, O MÓDULO DE RECOMENDAÇÃO DEVERÁ posicionar as peças que compartilhem essa técnica antes das peças de técnica diferente. 

- QUANDO houver duas ou mais peças que compartilhem a técnica artesanal da peça de referência, O MÓDULO DE RECOMENDAÇÃO DEVERÁ priorizar, entre elas, as que também compartilhem o polo de origem. 

- O MÓDULO DE RECOMENDAÇÃO DEVERÁ excluir a própria peça de referência da lista retornada. 

- QUANDO a peça de referência não for informada, não existir no catálogo ou não possuir técnica artesanal cadastrada, O MÓDULO DE RECOMENDAÇÃO DEVERÁ gerar a recomendação sem o critério de similaridade. 



### RF-02: Recomendações de Peças por Popularidade 

*História de usuário*

Como comprador, quero ver entre as recomendações peças com maior indicador de popularidade (derivado de vendas e visualizações), para descobrir produtos já validados por outros compradores.

*Critérios de aceitação (EARS)*

- O MÓDULO DE RECOMENDAÇÃO DEVERÁ calcular, para cada peça, um indicador de popularidade derivado da quantidade de vendas e da quantidade de visualizações.

- O MÓDULO DE RECOMENDAÇÃO DEVERÁ considerar no indicador apenas vendas e visualizações ocorridas nos últimos 30 dias (valor inicial da janela, definido em configuração). 

- QUANDO uma peça não possuir vendas nem visualizações dentro da janela definida, O MÓDULO DE RECOMENDAÇÃO DEVERÁ atribuir a ela o menor valor do indicador de popularidade, sem excluí-la dos itens elegíveis.


### RF-03: Recomendação por histórico do comprador

*História de usuário*

Como comprador com histórico de visualização ou compra, quero receber recomendações baseadas nesse histórico, para ver peças alinhadas ao que já demonstrei interesse.

*Critérios de aceitação (EARS)*

- QUANDO o comprador possuir histórico válido, O MÓDULO DE RECOMENDAÇÃO DEVERÁ incluir na lista de recomendações peças cuja técnica artesanal ou polo de origem coincida com os das peças desse histórico.

- O MÓDULO DE RECOMENDAÇÃO DEVERÁ considerar como histórico válido a existência de pelo menos um evento de visualização ou de compra registrado para o comprador autenticado. 

- QUANDO um evento de visualização ou compra do comprador for registrado, O MÓDULO DE RECOMENDAÇÃO DEVERÁ considerá-lo na próxima recomendação solicitada para esse comprador. 



### RF-04: Estratégia de cold start

**História de usuário**
Como comprador sem histórico de visualização ou compra, quero receber recomendações relevantes mesmo na minha primeira visita, para começar a explorar o catálogo desde já.

**Critérios de aceitação (EARS)**

- QUANDO o comprador não possuir histórico válido (RF-03), O MÓDULO DE RECOMENDAÇÃO DEVERÁ gerar as recomendações pelo indicador de popularidade (RF-02) e, quando houver peça de referência, também pela similaridade (RF-01), identificando a resposta com a estratégia "cold start". 

- QUANDO o sistema principal solicitar N recomendações para um comprador sem histórico e houver pelo menos N peças elegíveis, O MÓDULO DE RECOMENDAÇÃO DEVERÁ retornar N itens elegíveis utilizando a estratégia de cold start. 

- QUANDO o comprador registrar seu primeiro evento de visualização ou compra, O MÓDULO DE RECOMENDAÇÃO DEVERÁ aplicar a estratégia personalizada (RF-03) nas recomendações seguintes.



### RF-05: Exclusão de peças indisponíveis

**História de usuário**
Como comprador, quero que peças esgotadas ou despublicadas nunca apareçam nas recomendações, para não me frustrar tentando comprar algo indisponível.

**Critérios de aceitação (EARS)**

- O MÓDULO DE RECOMENDAÇÃO DEVERÁ excluir das recomendações peças com estoque igual a zero ou despublicadas.

- O MÓDULO DE RECOMENDAÇÃO DEVERÁ verificar a disponibilidade das peças a cada requisição, de modo que peças esgotadas ou despublicadas não apareçam nas recomendações.

- QUANDO uma peça esgotada ou despublicada voltar a ter estoque ou for republicada, O MÓDULO DE RECOMENDAÇÃO DEVERÁ voltar a considerá-la elegível a partir da requisição seguinte.

- SE o catálogo estiver inacessível, ENTÃO O MÓDULO DE RECOMENDAÇÃO DEVERÁ responder com erro de indisponibilidade, sem retornar peças cuja disponibilidade não tenha sido verificada. 



### RF-06: Quantidade configurável de recomendações

**História de usuário**
Como sistema principal, quero solicitar uma quantidade configurável de itens recomendados, respeitando um limite máximo definido, para adaptar o número de peças exibidas a cada contexto da interface.

**Critérios de aceitação (EARS)**

- QUANDO o sistema principal solicitar recomendações informando a quantidade desejada (N), O MÓDULO DE RECOMENDAÇÃO DEVERÁ retornar até N itens elegíveis.

- SE o valor de N solicitado for maior que 50, ENTÃO O MÓDULO DE RECOMENDAÇÃO DEVERÁ retornar no máximo 50 itens, sem gerar erro. 

- SE o sistema principal não informar a quantidade N, ENTÃO O MÓDULO DE RECOMENDAÇÃO DEVERÁ utilizar o valor padrão de 10 itens. 

- SE o número de peças elegíveis for menor que a quantidade solicitada (N) ou que o valor padrão, ENTÃO O MÓDULO DE RECOMENDAÇÃO DEVERÁ retornar todas as peças elegíveis disponíveis, sem gerar erro.



### RF-07: Interface de integração

**História de usuário**
Como sistema principal, quero uma interface de API para solicitar recomendações, para integrar o módulo à aplicação Origem.

**Critérios de aceitação (EARS)**

- O MÓDULO DE RECOMENDAÇÃO DEVERÁ expor uma interface de API para que o sistema principal solicite recomendações.

- QUANDO a requisição for válida, O MÓDULO DE RECOMENDAÇÃO DEVERÁ retornar uma resposta contendo o identificador da recomendação, a estratégia utilizada e a lista ordenada de peças recomendadas, com a posição e os critérios que contribuíram para a seleção de cada uma. 

- SE a requisição estiver malformada (parâmetros obrigatórios ausentes ou com valor inválido), ENTÃO O MÓDULO DE RECOMENDAÇÃO DEVERÁ retornar um erro indicando o parâmetro inválido, sem gerar nem registrar recomendação.



### RF-08: Registro das recomendações geradas

**História de usuário**
Como equipe responsável pelo módulo, quero que as recomendações geradas sejam registradas, associadas ao comprador e ao contexto da requisição, para permitir avaliação posterior.

**Critérios de aceitação (EARS)**

- O MÓDULO DE RECOMENDAÇÃO DEVERÁ registrar cada recomendação gerada com, no mínimo: identificador da recomendação; identificador pseudonimizado do comprador (quando autenticado); identificador da sessão; contexto da requisição; peça de referência (quando houver); estratégia utilizada; itens retornados em ordem; e data e hora da geração.

- QUANDO uma recomendação for gerada a partir da lista de contingência (RNF-02), O MÓDULO DE RECOMENDAÇÃO DEVERÁ registrá-la com a estratégia "contingência", para diferenciá-la das recomendações personalizadas e de cold start.


### RF-09: Registro de interações do comprador

**História de usuário**
Como equipe responsável pelo módulo, quero registrar as interações do comprador com as recomendações, para permitir cálculo de métricas e retreinamento.

**Critérios de aceitação (EARS)**

- QUANDO o sistema principal enviar uma interação do comprador (clique em peça recomendada, adição ao carrinho ou compra), O MÓDULO DE RECOMENDAÇÃO DEVERÁ registrá-la associada à recomendação correspondente (RF-08).

- SE a interação referenciar uma recomendação não encontrada nos registros (ex.: identificador de recomendação inválido ou inexistente), ENTÃO O MÓDULO DE RECOMENDAÇÃO DEVERÁ registrar a interação sem vínculo com recomendação, sem retornar erro ao sistema principal. 

---



## Requisitos Não Funcionais

### RNF-01: Tempo de Resposta da API de Recomendações

**História de usuário**
Como equipe do Origem, quero que as recomendações sejam retornadas dentro de um tempo limite, para que as páginas do marketplace não fiquem aguardando o módulo.

**Critérios de aceitação (EARS)**

- O MÓDULO DE RECOMENDAÇÃO DEVERÁ retornar os resultados da API de recomendações em menos de 200 milissegundos para 95% das requisições.

- O MÓDULO DE RECOMENDAÇÃO DEVERÁ medir esse tempo dentro do próprio módulo, do recebimento da requisição até o envio da resposta, excluindo qualquer latência de rede. 



### RNF-02: Disponibilidade do Serviço

**História de usuário**
Como equipe do Origem, quero que o marketplace continue exibindo recomendações mesmo quando o módulo falhar, para que o comprador não veja erros nem blocos vazios.

**Critérios de aceitação (EARS)**

- O MÓDULO DE RECOMENDAÇÃO DEVERÁ manter disponível para consulta do sistema principal uma lista de contingência de "Mais Vendidos", com até 50 peças, recalculada a cada 60 minutos, para que o sistema principal mantenha cópia local e a utilize quando o módulo estiver inacessível. 

- SE ocorrer falha interna durante o cálculo de uma recomendação e o catálogo estiver acessível, ENTÃO O MÓDULO DE RECOMENDAÇÃO DEVERÁ responder com a lista de contingência, identificando a estratégia "contingência", em vez de retornar erro ao sistema principal. 

- ENQUANTO a falha interna persistir, O MÓDULO DE RECOMENDAÇÃO DEVERÁ responder a cada nova requisição com a lista de contingência.

- QUANDO a operação normal for restabelecida, O MÓDULO DE RECOMENDAÇÃO DEVERÁ voltar a gerar recomendações personalizadas ou de cold start, conforme aplicável a cada comprador.

- SE o catálogo estiver inacessível ou nenhuma lista de contingência tiver sido calculada, ENTÃO O MÓDULO DE RECOMENDAÇÃO DEVERÁ responder com erro de indisponibilidade, para que o sistema principal utilize sua cópia local. 



### RNF-03: Conformidade com Privacidade e Proteção de Dados (LGPD)

**História de usuário**
Como comprador, quero que meus dados de navegação e compra sejam protegidos e possam ser apagados, para usar o Origem com segurança e exercer meus direitos previstos na LGPD.

**Critérios de aceitação (EARS)**

- O MÓDULO DE RECOMENDAÇÃO DEVERÁ armazenar o histórico de navegação e compra associado apenas a identificadores pseudonimizados e identificadores de sessão recebidos do sistema principal, sem armazenar dados pessoais diretos (nome, e-mail, CPF, endereço ou dados de pagamento). 

- O MÓDULO DE RECOMENDAÇÃO DEVERÁ manter os indicadores de popularidade apenas de forma agregada por peça, sem vínculo com compradores.

- QUANDO o sistema principal encaminhar uma solicitação de exclusão de dados feita pelo comprador (conforme LGPD), O MÓDULO DE RECOMENDAÇÃO DEVERÁ excluir os eventos, recomendações registradas e interações associados aos identificadores informados, de modo que consultas posteriores não retornem esses registros.

- O MÓDULO DE RECOMENDAÇÃO DEVERÁ excluir automaticamente os eventos com mais de 90 dias. 



### RNF-04: Escalabilidade

**História de usuário**
Como equipe do Origem, quero que o módulo suporte picos de acesso (ex.: datas comemorativas), para que as recomendações continuem funcionando nos momentos de maior venda.

**Critérios de aceitação (EARS)**

- QUANDO o volume de requisições atingir até 3 vezes o volume de referência, O MÓDULO DE RECOMENDAÇÃO DEVERÁ manter o tempo de resposta dentro do limite definido em RNF-01 (menos de 200 ms para 95% das requisições).



### RNF-05: Segurança

**História de usuário**
Como equipe do Origem, quero que apenas clientes autenticados e autorizados pelo sistema principal consigam usar o módulo, para proteger os dados dos compradores e impedir o uso indevido da API.

**Critérios de aceitação (EARS)**

- O MÓDULO DE RECOMENDAÇÃO DEVERÁ aceitar apenas credenciais de serviço emitidas pelo sistema principal.

- SE uma requisição não apresentar credencial ou apresentar credencial inválida ou expirada, ENTÃO O MÓDULO DE RECOMENDAÇÃO DEVERÁ rejeitá-la com erro de autenticação, sem processar a operação nem registrar dados.

- SE uma requisição apresentar credencial válida sem permissão para a operação solicitada, ENTÃO O MÓDULO DE RECOMENDAÇÃO DEVERÁ rejeitá-la com erro de autorização, sem processar a operação nem registrar dados.

