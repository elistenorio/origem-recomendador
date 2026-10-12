# product.md: Módulo de Recomendação de Produtos

## Contexto do Projeto Principal

**Origem** é uma aplicação web full stack que conecta artesãos e produtores criativos a compradores. A plataforma inclui vitrine do comprador (busca, filtros, perfil do artesão, carrinho, avaliações), painel do artesão (catálogo, estoque, pedidos), painel administrativo e indicadores de venda.

O Módulo de Recomendação de Produtos é um componente com responsabilidade delimitada: sugerir peças (produtos artesanais cadastrados no Origem) nas páginas inicial e de produto. Ele é consumido exclusivamente pelo back-end do Origem, por meio de uma interface de API (RF-07); o front-end nunca acessa o módulo diretamente (ver design.md).

## Problema de Negócio / Necessidade do Usuário

Artesãos e produtores criativos têm pouca visibilidade digital, dependem de intermediários e enfrentam gestão precária de catálogo, pedidos e estoque. O Origem cria um canal direto entre essa produção e os compradores, destacando origem, técnica e o impacto de comprar de quem faz.

À medida que o catálogo cresce e se distribui entre muitos pequenos produtores, compradores têm dificuldade em descobrir peças relevantes, e artesãos com pouca exposição vendem menos. O módulo de recomendação existe para reduzir essa fricção de descoberta.

## Público-Alvo

- **Compradores:** buscam peças artesanais alinhadas ao seu gosto e à técnica e origem que valorizam. São os usuários finais das recomendações e os titulares dos dados de navegação e compra (RNF-03).
- **Artesãos e produtores:** dependem de visibilidade dentro do Origem para vender suas peças.
- **Equipe da plataforma:** precisa que o módulo funcione de forma confiável e mensurável (RF-08, RF-09, RNF-01, RNF-02).
- **Back-end do Origem:** consumidor técnico da API do módulo (RF-06, RF-07).
- **Responsável pela conformidade com a LGPD**: precisa garantir pseudonimização, minimização e atendimento ao direito de exclusão (RNF-03). 

## Objetivo do Módulo

Ajudar cada comprador a descobrir peças disponíveis e relevantes, combinando similaridade com a peça que está vendo (técnica artesanal e polo de origem, RF-01), popularidade recente (RF-02) e seu histórico de visualização e compra (RF-03), inclusive na primeira visita, por meio da estratégia de cold start (RF-04).

## Benefícios Esperados

- Redução da fricção de descoberta de peças, combinando múltiplos critérios de relevância (RF-01 a RF-04) e mostrando apenas peças disponíveis (RF-05).
- Continuidade do serviço diante de falhas: o módulo responde com a lista de Mais Vendidos quando há falha interna, e o Origem mantém uma cópia dessa lista para quando o módulo estiver inacessível (RNF-02).
- Registros de recomendações e interações (RF-08, RF-09) que permitem à equipe comparar a estratégia principal com a baseline e recalibrar os pesos ao longo do tempo.
- Integração simples com o sistema principal por meio de uma API com quatro operações, com quantidade de itens configurável pelo consumidor (RF-06, RF-07). 
- Visibilidade para artesãos recém-cadastrados, já que a recomendação por similaridade de técnica e polo de origem (RF-01) independe do histórico de vendas. 

## Limites do Produto

- Nesta versão, o módulo recomenda apenas **peças**; não recomenda artesãos, serviços ou anúncios.
- As recomendações são geradas para dois contextos: página inicial e página de produto.
- O módulo não armazena dados de identificação direta dos compradores, apenas identificadores pseudonimizados e identificadores de sessão gerados pelo Origem (RNF-03). 
- Não inclui a interface visual das recomendações (responsabilidade do front-end do Origem).
- Não inclui geração dos indicadores de venda do painel administrativo (módulo separado).
- Não inclui precificação dinâmica, detecção de fraude ou moderação de conteúdo.
- Visitantes não autenticados não formam histórico e recebem sempre recomendações de cold start (RF-04). 

