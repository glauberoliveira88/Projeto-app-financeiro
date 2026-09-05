# DOCUMENTO DE REQUISITOS DO PRODUTO (PRD)

## 1. Visão Geral do Produto

* **Nome provisório do sistema:** FinançasSimples (sujeito a alteração posterior).
* **Descrição resumida do sistema:** Sistema web de gestão financeira pessoal focado em simplicidade, usabilidade e agilidade, funcionando como um painel unificado para o controle de receitas, despesas, carteiras e transferências.
* **Público principal que usará o sistema:** Pessoas físicas que desejam organizar sua vida financeira de forma prática, sem termos contábeis complexos.
* **Principal benefício esperado:** Proporcionar uma visão rápida, visual e organizada do orçamento, respondendo com facilidade a perguntas cotidianas sobre saldos, gastos e pendências.
* **Contexto geral de uso:** Uso diário e estritamente individual por painel, acessível tanto por computadores quanto por celulares de forma totalmente responsiva, com suporte a temas claro e escuro.

---

## 2. Problema que o Sistema Resolve

Sem o sistema, o controle financeiro pessoal costuma ser descentralizado, propenso a erros e cansativo. As principais dificuldades enfrentadas pelo usuário incluem:

* **Informações espalhadas:** Anotações em planilhas complexas, blocos de notas ou papel, dificultando a visão consolidada do dinheiro.
* **Falta de clareza no orçamento:** Dificuldade para identificar rapidamente se o mês fechará no positivo ou no negativo e quais categorias consomem mais recursos.
* **Risco de esquecimentos:** Falta de acompanhamento visual claro para contas pendentes ou próximas do vencimento, gerando atrasos.
* **Retrabalho operacional:** Necessidade de redigitar manualmente despesas fixas recorrentes todos os meses.
* **Complexidade excessiva:** Ferramentas de mercado carregadas de termos contábeis avançados que desmotivam o uso diário.

---

## 3. Objetivos do Sistema

### Objetivo principal

Ajudar a organizar a vida financeira do usuário de forma simples, visual e prática, permitindo o controle completo de entradas, saídas e saldos sem complicação.

### Objetivos específicos

* Permitir o registro ágil de receitas, despesas e transferências entre contas próprias.
* Organizar as movimentações por categorias personalizáveis e formas de pagamento básicas.
* Exibir um painel resumo (Dashboard) com saldos mensais claros e gráficos simples de despesas por categoria.
* Automatizar a geração de lançamentos recorrentes (fixos) ao virar o mês.
* Alertar visualmente o usuário sobre contas próximas do vencimento ou já vencidas.
* Monitorar tetos de gastos por categoria com alertas visuais de estouro de orçamento.
* Oferecer segurança e praticidade de acesso via login tradicional ou conta Google.

---

## 4. Personas e Perfil de Usuário

| Perfil | Descrição simples | Principais ações no sistema | Permissões básicas |
| --- | --- | --- | --- |
| **Usuário Pessoal** | Pessoa física que gerencia o próprio orçamento e deseja praticidade no controle de suas finanças diárias. | Cadastrar contas, gerenciar categorias, registrar receitas/despesas/transferências, acompanhar o painel e filtrar lançamentos. | Acesso total e exclusivo ao seu próprio painel de dados financeiros. |

---

## 5. Escopo da Primeira Versão

### Área Funcional: Autenticação e Acesso

* **Login e Cadastro:** Permite criar conta e acessar o sistema via e-mail e senha tradicionais (com recuperação de senha por e-mail) ou de forma automática integrada com a conta Google. A sessão permanece ativa até o logout manual.

### Área Funcional: Painel Principal (Dashboard)

* **Indicadores do Mês:** Exibição clara do saldo do mês, total de receitas e total de despesas.
* **Gráfico de Despesas:** Gráfico de barras simples e monocromático dividindo as despesas por categoria.
* **Alerta de Vencimentos:** Bloco de destaque visual para contas próximas do vencimento ou em atraso.

### Área Funcional: Gestão de Lançamentos

* **Cadastro de Movimentações:** Registro manual de receitas, despesas e transferências informando valor, data, descrição, categoria, forma de pagamento básica, status (pago/pendente) e observações textuais opcionais.
* **Edição e Exclusão:** Liberdade total para editar ou excluir qualquer lançamento a qualquer momento.
* **Busca e Filtros:** Barra de pesquisa por texto e filtros por período (navegação livre por meses passados e futuros), contas e status.

### Área Funcional: Lançamentos Recorrentes

* **Automação de Fixos:** Geração automática de despesas e receitas fixas pré-cadastradas pelo usuário ao virar o mês.

### Área Funcional: Gestão de Contas e Carteiras

* **Múltiplas Carteiras:** Cadastro de contas (ex: Conta Corrente, Dinheiro, Cartão) com definição de saldo inicial.
* **Arquivamento:** Opção de inativar (arquivar) contas que não são mais utilizadas, preservando o histórico.

### Área Funcional: Gestão de Categorias e Orçamento

* **Personalização:** Lista padrão inicial combinada com a liberdade de criar, editar, excluir ou arquivar categorias personalizadas.
* **Reatribuição de Histórico:** Ao tentar excluir uma categoria com lançamentos vinculados, o sistema bloqueia a exclusão e sugere o arquivamento ou a realocação em lote dos itens para outra categoria.
* **Limites de Gastos (Tetos):** Definição opcional de um limite de orçamento mensal por categoria, emitindo alerta visual caso o teto seja ultrapassado.

### Área Funcional: Configurações Visuais

* **Responsividade e Tema:** Interface totalmente adaptada para celulares e computadores, com botão de alternância manual entre tema claro e escuro.

---

## 6. Funcionalidades Fora de Escopo

* **Anexo de arquivos:** Envio de fotos de recibos, comprovantes ou notas fiscais em PDF (adiado para versões futuras).
* **Importação automática de extratos:** Conexão com bancos via arquivos OFX ou Open Finance.
* **Gestão de investimentos:** Acompanhamento de ativos de renda fixa, ações ou criptomoedas.
* **Divisão de contas em grupo:** Recurso para rachar despesas de viagens ou contas compartilhadas.
* **Exportação de dados:** Baixar relatórios em planilhas CSV/Excel ou arquivos PDF.
* **Múltiplas moedas:** Suporte a moedas internacionais (o sistema operará exclusivamente em Real brasileiro - R$).

---

## 7. Regras de Negócio

* **Isolamento de Transferências:** Transferências entre contas próprias alteram estritamente o saldo individual das carteiras envolvidas, sem impactar o somatório geral de receitas e despesas do período.
* **Integridade de Dados e Exclusão:** O sistema bloqueia a exclusão definitiva de contas ou categorias que possuem histórico de lançamentos vinculados, exigindo o arquivamento ou a realocação dos registros.
* **Geração de Recorrentes:** Despesas e receitas fixas configuradas pelo usuário são geradas de forma automática pelo sistema no início de cada novo ciclo mensal.
* **Monitoramento de Orçamento:** O sistema compara o total gasto em uma categoria com o teto de orçamento definido e exibe um alerta visual se o limite for ultrapassado.
* **Destaque de Atrasos:** Lançamentos com status pendente cuja data de vencimento já passou recebem destaque visual automático no painel.
* **Moeda Padrão:** Todos os valores monetários devem seguir obrigatoriamente a formatação padrão do Real brasileiro (R$).

---

## 8. Informações que o Sistema Precisa Controlar

| Informação | Para que serve no sistema | Observações importantes |
| --- | --- | --- |
| **Usuários** | Identificar o usuário no login e vincular os dados financeiros ao seu painel exclusivo. | Pode utilizar credenciais tradicionais (e-mail/senha) ou identificador da conta Google. |
| **Contas / Carteiras** | Controlar onde o dinheiro está armazenado (ex: Conta Corrente, Dinheiro, Cartão). | Armazena nome, saldo inicial e status (ativo ou arquivado). |
| **Categorias** | Classificar a natureza dos gastos e ganhos. | Armazena nome, tipo (receita/despesa), teto de orçamento mensal opcional e status (ativo/arquivado). |
| **Lançamentos** | Registrar todas as movimentações financeiras do usuário. | Armazena tipo, valor, data, descrição, categoria, conta de origem/destino, forma de pagamento, status (pago/pendente) e observações. |

---

## 9. Fluxos Principais de Uso

### Registrar Nova Movimentação (Receita ou Despesa)

1. O usuário acessa a área de lançamentos ou o painel principal.
2. O usuário clica em adicionar novo lançamento.
3. O sistema exibe o formulário de cadastro.
4. O usuário preenche os campos obrigatórios (tipo, valor, data, descrição, categoria, conta e status) e o campo opcional de observação.
5. O usuário confirma a ação.
6. O sistema valida o preenchimento dos campos obrigatórios.
7. O sistema registra a movimentação e atualiza o saldo da conta e os indicadores do painel.
8. O sistema exibe a movimentação atualizada na listagem.

### Realizar Transferência entre Contas

1. O usuário acessa a opção de transferências.
2. O usuário informa o valor, a data, a conta de origem e a conta de destino.
3. O usuário confirma a transferência.
4. O sistema valida se há saldo ou se a operação é permitida.
5. O sistema desconta o valor da conta de origem e adiciona na conta de destino, sem alterar o total de receitas e despesas do mês.
6. O sistema exibe o sucesso da operação e os novos saldos das contas.

### Navegar por Períodos (Meses)

1. O usuário visualiza o seletor de mês e ano na tela principal.
2. O usuário seleciona um mês passado ou futuro.
3. O sistema atualiza instantaneamente o painel e a lista de lançamentos exibindo os dados referentes ao período escolhido.

---

## 10. Histórias de Usuário

* Como usuário pessoal, eu quero fazer login com minha conta Google ou e-mail para acessar meu painel financeiro de forma segura.
* Como usuário pessoal, eu quero cadastrar receitas e despesas informando valor, categoria e forma de pagamento para saber exatamente para onde vai o meu dinheiro.
* Como usuário pessoal, eu quero que minhas despesas e receitas fixas sejam geradas automaticamente todo mês para evitar o trabalho de redigitação manual.
* Como usuário pessoal, eu quero definir um teto de gastos por categoria para receber alertas visuais caso ultrapasse o orçamento planejado.
* Como usuário pessoal, eu quero navegar livremente entre meses passados e futuros para consultar o histórico do meu orçamento.
* Como usuário pessoal, eu quero alternar entre o tema claro e o tema escuro para melhorar o meu conforto visual durante o uso.

---

## 11. Critérios de Aceitação

* [ ] O usuário consegue realizar o cadastro e o login utilizando e-mail/senha ou a conta Google.
* [ ] O sistema impede o salvamento de lançamentos e cadastros quando campos obrigatórios não são preenchidos.
* [ ] O sistema exibe mensagens claras quando dados precisam ser corrigidos nos formulários.
* [ ] O sistema mostra o registro criado ou atualizado imediatamente nas consultas e no painel correspondente.
* [ ] O sistema respeita o isolamento de dados garantindo acesso apenas ao painel do próprio usuário.
* [ ] O sistema altera o saldo das contas corretamente ao registrar movimentações e transferências internas.
* [ ] O sistema exibe alertas visuais automáticos para contas vencidas ou próximas do vencimento e para categorias que ultrapassaram o teto de orçamento.

---

## 12. Consultas, Relatórios e Indicadores

* **Painel Resumo (Dashboard):** Exibe o saldo líquido do mês, total de receitas e total de despesas calculados em tempo real.
* **Gráfico de Categorias:** Apresenta um gráfico de barras simples e monocromático com a distribuição das despesas por categoria no mês selecionado.
* **Alerta de Vencimentos:** Lista resumida de contas pendentes com prazos próximos ou expirados.
* **Listagem de Movimentações:** Tabela detalhada de lançamentos com suporte a barra de pesquisa textual e filtros por período (mês/ano), conta específica e status de pagamento.

---

## 13. Permissões e Segurança Funcional

| Perfil | Pode fazer | Não pode fazer | Observações |
| --- | --- | --- | --- |
| **Usuário Pessoal** | Cadastrar, visualizar, editar e excluir seus próprios lançamentos, contas, categorias e definir orçamentos. Acessar painel e filtros. | Acessar dados de outros usuários ou gerenciar configurações globais de sistema. | Cada painel é restrito e isolado para o seu respectivo usuário. |

---

## 14. Limitações da Primeira Versão

* Não haverá suporte para anexo de arquivos, fotos de recibos ou notas fiscais.
* Não haverá importação automática de extratos bancários (OFX ou Open Finance).
* Não haverá exportação de relatórios para arquivos externos (Excel, CSV ou PDF).
* Não haverá suporte a múltiplas moedas (apenas Real brasileiro - R$).
* Não haverá controle de investimentos ou divisão de contas em grupo.
* Não haverá perfis múltiplos ou contas compartilhadas no mesmo painel (uso estritamente individual).

---

## 15. Pontos Pendentes Antes do FSD

Não foram identificadas dúvidas funcionais pendentes para a criação do FSD.

---

## 16. Resumo Final do PRD

O projeto consiste na criação do **FinançasSimples**, um sistema web responsivo de gestão financeira pessoal voltado para usuários únicos que buscam praticidade e clareza no dia a dia. A primeira versão entregará painel resumo com indicadores, gráfico de despesas por categoria, alerta de vencimentos, gestão completa de lançamentos avulsos e recorrentes automáticos, controle de múltiplas contas, transferências internas, categorias personalizáveis com tetos de orçamento e opções flexíveis de login (e-mail/senha e Google), além de alternância entre temas claro e escuro. Recursos avançados como anexos, importação bancária e exportação de relatórios ficam formalmente fora do escopo inicial. O projeto encontra-se totalmente alinhado e pronto para avançar para a etapa de criação do FSD (Documento de Especificação Funcional).