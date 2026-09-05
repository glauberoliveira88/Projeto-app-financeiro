# DECISÕES TÉCNICAS DO PROJETO

## 1. Documentos recebidos

* O arquivo `PRD.md` foi anexado, lido e analisado integralmente, estabelecendo o escopo funcional do sistema **FinançasSimples**.


* O arquivo `DESIGN.md` foi anexado, lido e analisado, determinando o guia visual de alta contraste (*High-Contrast Dark*, paleta zinc com violeta primário `#a78bfa`, superfícies near-black `#09090b` e separação por bordas).



## 2. Identificação do sistema

* **Nome do sistema:** FinançasSimples.


* **Objetivo principal:** Proporcionar controle financeiro pessoal simplificado, visual e ágil para o acompanhamento de receitas, despesas, carteiras e transferências.


* **Público usuário:** Pessoas físicas com uso estritamente individual por painel.


* **Contexto de uso:** Aplicação web totalmente responsiva para computadores e dispositivos móveis, com suporte a temas claro e escuro.


* **Resumo funcional:** Painel de indicadores mensais, gráfico de despesas por categoria, alertas de vencimento e tetos de orçamento, gestão de lançamentos avulsos e recorrentes, múltiplas carteiras e transferências internas.



## 3. Decisões técnicas confirmadas

* **Stack tecnológica:** Python com Flask no backend, MySQL como banco de dados relacional, e HTML, CSS, JavaScript e React para a interface de usuário.


* **Ambientes de execução:** Desenvolvimento local utilizando ambiente virtual Python (`venv`), servidor Flask embutido e MySQL via XAMPP. Produção hospedada no **PythonAnywhere**.


* **Arquitetura estrutural:** Organização baseada em MVC (Model-View-Controller), assegurando a separação limpa entre persistência de dados (MySQL), regras de negócio (Flask) e camada de apresentação (React).


* **Autenticação:** Suporte híbrido a cadastro tradicional por e-mail/senha (com recuperação via link por e-mail) e login rápido integrado via conta Google (OAuth/OpenID Connect).


* **Controle de acesso e segurança:** Isolamento estrito de dados por painel de usuário único (RBAC simplificado), auditoria básica de registros (`created_at`, `updated_at`), log de erros do sistema e exclusão lógica (*soft delete*).



## 4. Decisões adotadas por padrão

* **Ambiente de testes/homologação:** Não haverá ambiente obrigatório de testes ou homologação nesta primeira versão; o sistema será validado localmente antes do deploy.


* **Recursos estruturais padrão:** Autenticação integrada, auditoria, log de erros e *soft delete* adotados conforme padrão especificado.


* **Orientação para a IA codificadora:** O FSD incluirá diretrizes de implementação divididas em etapas incrementais, progressivas e testáveis.

## 5. Stack e ambientes

* **Linguagem backend:** Python / Flask


* **Banco de dados:** MySQL


* **Tecnologias de frontend:** HTML, CSS, JavaScript, React e diretrizes visuais do `DESIGN.md`

* **Ambiente local:** `venv` do Python + servidor Flask + MySQL (XAMPP)


* **Ambiente de homologação:** Ausente (testes locais)


* **Ambiente de produção:** PythonAnywhere


* **Observações de deploy:** O processo de publicação no PythonAnywhere será abordado em etapa posterior do fluxo.

## 6. Arquitetura obrigatória

* A aplicação seguirá estritamente o padrão MVC adaptado à stack escolhida.


* O Model gerencia a comunicação com o banco MySQL; o Controller processa as rotas e regras de negócio no Flask; a View entrega a interface reativa em React em conformidade com o `DESIGN.md`.



## 7. Recursos estruturais definidos

* **Autenticação:** E-mail/senha e Google OAuth.


* **RBAC:** Isolamento estrito de dados por usuário.


* **Auditoria:** Rastreio básico de criação e atualização em registros principais.


* **Soft delete:** Exclusão lógica em cadastros e lançamentos para preservação de histórico.


* **Log de erros:** Registro centralizado de falhas na aplicação Flask.


* **Configurações globais:** Preferências de perfil e alternância de temas visuais.


* **Uploads e anexos:** Fora de escopo na primeira versão.


* **Exportações:** Apenas visualização estruturada em tela.


* **APIs e integrações externas:** Exclusivamente integração com a API de autenticação do Google.



## 8. Perfis e permissões em nível alto

* **Usuário Pessoal:** Acesso restrito e exclusivo ao seu próprio painel financeiro, com permissão total para gerenciar suas contas, categorias e lançamentos, sem privilégios administrativos globais ou acesso a dados de terceiros.



## 9. Entidades prováveis em nível alto

* **Usuários:** Dados cadastrais, credenciais e identificador vinculado ao Google.


* **Contas / Carteiras:** Nome, saldo inicial e status (ativo ou arquivado).


* **Categorias:** Nome, tipo (receita ou despesa), teto de orçamento mensal opcional e status (ativo ou arquivado).


* **Lançamentos:** Tipo, valor, data, descrição, categoria, contas envolvidas, forma de pagamento, status (pago/pendente), observações e recorrência.



## 10. Módulos, telas e fluxos esperados em nível alto

* **Módulo de Autenticação:** Telas de login tradicional, cadastro, recuperação de senha e integração com o Google.


* **Painel Principal (Dashboard):** Tela de indicadores mensais consolidados, gráfico de despesas por categoria e painel de alertas de vencimento.


* **Módulo de Lançamentos:** Tabela detalhada de movimentações com filtros por período e status, além de formulários para lançamentos avulsos e transferências entre contas.


* **Módulo de Contas/Carteiras:** Tela de listagem e gerenciamento de saldos de carteiras com opção de arquivamento.


* **Módulo de Categorias e Orçamentos:** Tela de personalização de categorias, configuração de tetos de gastos e tratamento de reatribuição em caso de arquivamento.


* **Configurações Visuais:** Alternância manual entre tema claro e escuro.



## 11. Alertas para relatórios, consultas, exportações e desempenho

* O FSD deverá prever a criação de índices no banco MySQL para otimizar consultas filtradas por período (mês/ano), ID de usuário, carteira e categoria, garantindo alta performance no dashboard e nas listagens.


* Relatórios e consultas limitados à visualização interativa em tela.



## 12. Alertas para uploads, anexos e arquivos

* O envio de arquivos, fotos de recibos, comprovantes ou notas fiscais está formalmente excluído do escopo da primeira versão.



## 13. Alertas para logs, auditoria e segurança

* O FSD especificará o armazenamento seguro de senhas por hash robusto no Flask, proteção rigorosa de rotas por sessão/token e isolamento absoluto de dados entre diferentes usuários.



## 14. Itens que não devem ser inventados

* APIs e integrações externas (exceto Google OAuth).


* Importação automática de extratos bancários (OFX ou Open Finance).


* Exportação de relatórios em arquivos PDF, Excel ou CSV.


* Envio de anexos ou comprovantes.


* Suporte a múltiplas moedas (exclusivo para Real brasileiro - R$).


* Gestão de investimentos ou divisão de despesas em grupo.



## 15. Pendências não bloqueantes

* Não foram identificadas pendências não bloqueantes para a criação do FSD.
