# Histórico e Registro de Erros — FinançasSimples

Este arquivo tem como objetivo registrar problemas técnicos, falhas de execução, bugs de integração ou comportamentos inesperados encontrados durante o ciclo de desenvolvimento do projeto, detalhando o diagnóstico e a solução adotada para prevenir reincidências.

---

## Modelo de Registro

Utilize o padrão abaixo para cadastrar novos incidentes:

```markdown
## AAAA-MM-DD - Título curto do erro

- **Sintoma:** Descrição clara do comportamento anômalo observado ou mensagem de erro retornada.
- **Causa:** Diagnóstico da raiz do problema (código, dependência, configuração ou banco de dados).
- **Solução aplicada:** Detalhamento do ajuste ou refatoração realizada no projeto.
- **Como evitar no futuro:** Medida preventiva, teste ou boa prática a ser seguida daqui em diante.
```

---

## Registros de Incidentes

## 2026-09-19 - Cache incorreto de `g.current_user = None` e ausência de verificação de contexto de requisição

- **Sintoma:** Endpoint `/api/auth/sessao` respondia `autenticado: False` após login bem-sucedido quando executado em contexto contínuo de aplicação (`app_context`), e a função `validar_posse` gerava `RuntimeError: Working outside of request context` quando acionada diretamente fora de requisições HTTP ativas.
- **Causa:** A checagem `if not hasattr(g, "current_user")` considerava `True` mesmo quando `g.current_user` havia sido atribuído como `None` em requisição prévia não autenticada, impedindo nova consulta a `session.get("usuario_id")`. Além disso, o acesso incondicional ao proxy `session` sem checar `has_request_context()` gerava exceção de runtime fora de endpoints.
- **Solução aplicada:** Refatoração de `obter_usuario_atual()` em `app/utils/auth.py` para verificar previamente `has_request_context()`, consultar `session.get("usuario_id")` diretamente a cada requisição e invalidar o cache de `g.current_user` quando o identificador de sessão mudar.
- **Como evitar no futuro:** Em utilitários e middlewares Flask, sempre utilizar `has_request_context()` antes de ler proxies de requisição/sessão e sincronizar caches locais de contexto (`g`) baseando-se no estado real do cookie de sessão.

## 2026-09-19 - AttributeError ao acessar `current_user.is_authenticated` em requisições de visitantes não autenticados

- **Sintoma:** Ao renderizar rotas públicas como `/login`, ocorria erro `AttributeError: 'NoneType' object has no attribute 'is_authenticated'`, provocando resposta HTTP 500.
- **Causa:** O utilitário `obter_usuario_atual()` retornava `None` quando não havia identificador de usuário na sessão. O `LocalProxy(current_user)` do Werkzeug ao ser acessado repassava a busca de atributo diretamente ao objeto embrulhado (`None`), gerando a exceção.
- **Solução aplicada:** Criação da classe `UsuarioAnonimo` em `app/utils/auth.py` com propriedades `is_authenticated = False` e `is_anonymous = True`. Quando a sessão não possui usuário autenticado, `obter_usuario_atual()` retorna uma instância de `UsuarioAnonimo()`, garantindo compatibilidade com expressões como `current_user.is_authenticated`.
- **Como evitar no futuro:** Em proxies de usuário atual, sempre utilizar um objeto anônimo padrão que implemente a interface de autenticação em vez de retornar o literal `None`.

## 2026-09-19 - Perda de CSRF Token em `session.clear()` e descompasso na resposta do usuário no login

- **Sintoma:** Ao clicar em "Entrar no FinançasSimples" no formulário de login, a URL mudava para `/dashboard` mas a tela não atualizava o painel; em um segundo clique subsequente, o sistema exibia "Token CSRF inválido ou ausente. Recarregue a página e tente novamente". Ao clicar no botão do Google, um JSON bruto era exibido.
- **Causa:** Dois fatores: (1) O endpoint `/api/auth/login` retornava o objeto do usuário encapsulado sob `dados.usuario`, enquanto o componente React esperava `res.usuario`, fazendo com que o estado do usuário continuasse `null` no React; (2) Ao autenticar com sucesso no backend, a instrução `session.clear()` apagava a chave `_csrf_token` da sessão anterior. Ao tentar clicar novamente, o token antigo da página já não conferia com a nova sessão. Já no caso do Google OAuth, a ausência de chaves de API retornava JSON 501 sem redirecionar de volta à interface.
- **Solução aplicada:** (1) Criação de `renovar_sessao_mantendo_csrf()` em `app/utils/csrf.py` para preservar o token CSRF durante a regeneração de sessão no login, cadastro e logout; (2) Inclusão do token e do usuário tanto na raiz quanto em `dados` nas respostas de login e cadastro; (3) Implementação de auto-sincronização e auto-retry transparente no `app/static/js/api.js`; (4) Atualização do componente React para extrair o usuário flexivelmente (`res.usuario || res.dados.usuario`); (5) Redirecionamento da rota do Google OAuth para `/login?aviso=google_nao_configurado` com alerta visual informativo caso as chaves não estejam preenchidas no `config/config.py`.
- **Como evitar no futuro:** Ao regenerar sessões (`session.clear()`), sempre preservar ou emitir e sincronizar tokens CSRF com o cliente, e padronizar o schema de payloads JSON entre frontend e backend.

## 2026-09-29 - Dimensionamento excessivamente reduzido da logomarca nas telas de autenticação e no dashboard

- **Sintoma:** O logotipo do FinançasSimples era renderizado em escala quase imperceptível (~4% a 5% da altura de visualização horizontal na tela de login e 36px na barra lateral do dashboard), prejudicando a identidade visual da aplicação.
- **Causa:** Regras CSS estáticas com restrições rígidas (`height: 48px; max-width: 240px;` em `.auth-logo` e `height: 36px;` em `.sidebar-logo`) que não aproveitavam o espaço visual da viewport nem a proporção quadrada (1:1) dos assets oficiais.
- **Solução aplicada:**
  1. Tela de Login/Autenticação: redefinido `.auth-logo` para `height: 26vh; min-height: 120px; max-width: 100%; object-fit: contain;`, ocupando entre 25% e 30% da viewheight padrão em telas horizontais.
  2. Barra Lateral / Dashboard: redefinido `.sidebar-logo` para `height: clamp(100px, 16vh, 150px); max-width: 160px; object-fit: contain; margin: 0 auto;`, mantendo a largura fixa da sidebar em 260px com respiro generoso em relação às bordas e ao fim da sidebar, além de adicionar `overflow-y: auto` no menu de navegação.
  3. Formalização da regra de identidade visual e dimensionamento de logotipos em `docs/DESIGN.md`.
- **Como evitar no futuro:** Sempre utilizar unidades relativas ao contexto visual (`vh`, `clamp`) para elementos de identidade visual chave e consultar a seção "Logotipo e Identidade Visual" de `docs/DESIGN.md` ao implementar novos fluxos ou telas.

## 2026-09-29 - Fechamento acidental do modal ao clicar no fundo e usabilidade do campo de teto orçamentário

- **Sintoma:** O modal de criação/edição de categorias era fechado inesperadamente ao clicar fora do container (no overlay de fundo), causando risco de perda de digitação; os seletores de incremento do valor variavam apenas 1 centavo; não havia prefixo visual "R$" fixo à esquerda; os centavos sumiam ao digitar números inteiros; e o ícone de etiqueta competia com o nome das categorias em tamanho reduzido.
- **Causa:** O componente genérico `Modal` possuía um ouvinte `handleOverlayClick` que disparava `onFechar()` no clique do overlay externo; o input nativo HTML utilizava `step="0.01"` sem máscara monetária fixa de centavos; e os cards utilizavam estilos padrão com tipografia de 15px e emoji genérico de etiqueta (`🏷️`).
- **Solução aplicada:**
  1. Remoção do fechamento por clique no overlay no componente `Modal`, garantindo que o fechamento ocorra apenas por ação explícita no botão "Cancelar" ou no ícone "✕".
  2. Implementação de máscara monetária contínua com duas casas decimais visíveis (`0,00`), container com prefixo visual `R$` fixo à esquerda e botões steppers dedicados (`▲` / `▼`) que incrementam e decrementam o valor exatamente de R$ 1,00 em R$ 1,00.
  3. Substituição do ícone de etiqueta pelo ícone de moeda `🪙` envolvido em container de alto contraste harmônico nos temas claro e escuro (`.category-icon-coin`).
  4. Ampliação do destaque tipográfico do nome da categoria (`.category-name`) para 18px (`1.125rem`), peso 700 e `letter-spacing: -0.02em`.
- **Como evitar no futuro:** Em telas modais contendo formulários com campos de preenchimento, nunca permitir o fechamento silencioso por clique fora sem confirmação, e padronizar campos monetários com prefixo explícito `R$` e formatação contínua de centavos.

## 2026-10-01 - Tratamento de string monetária na API e exigência de retorno explícito HTTP 403 em `validar_posse`

- **Sintoma:** Ao cadastrar ou atualizar lançamento recorrente com valor numérico em string (`"1500.00"`), a remoção incondicional do caractere ponto convertia o valor para `150000.00`. Além disso, chamadas a `validar_posse` não bloqueavam a execução imediatamente caso o chamador não verificasse o valor booleano retornado.
- **Causa:** O método de limpeza de string tratava ponto como separador de milhar brasileiro mesmo quando não havia vírgula decimal na string recebida via API JSON. Adicionalmente, a função utilitária `validar_posse` registra o evento de segurança e retorna `False`, cabendo ao Controller checar a resposta e emitir explicitamente a resposta HTTP 403 Forbidden.
- **Solução aplicada:**
  1. Criação do helper `converter_valor_decimal` que detecta a presença de vírgula e ponto, tratando corretamente tanto formatações brasileiras (`1.500,00`) quanto números decimais padrão em ponto flutuante (`1500.00` ou `1500`).
  2. Adição de verificação explícita `if not validar_posse(recurso, "tipo"): return jsonify({"sucesso": False, "erro": "Acesso não autorizado."}), 403` em todas as rotas e validações de chaves estrangeiras (`categoria_id`, `conta_id`, `id`) no `recorrentes_controller.py`.
- **Como evitar no futuro:** Em endpoints de API REST, padronizar conversores numéricos resilientes a múltiplos formatos e sempre validar explicitamente o booleano de retorno de salvaguardas de autorização (`if not validar_posse(...) return 403`).

## 2026-10-06 - Divergências de UI/UX e quebra de layout na tela e modais de Fixos Recorrentes

- **Sintoma:** (1) Bloco de resumo financeiro de fixos renderizado como texto puro desestruturado sem cartões horizontais de KPIs e com textos redundantes entre parênteses; (2) Badges de tipo nos cards da listagem com quebra de linha inadequada entre a seta direcional e a palavra ("Despesa"/"Receita"); (3) Textos prolixos no modal de cadastro ("Descrição do Fixo", "Dia de Vencimento Padrão no Mês (1 a 31)") e botões de stepper com rótulos redundantes ("▲ +1 dia" / "▼ -1 dia"); (4) Botão de exclusão com contraste desarmônico (letras vermelhas sob fundo violeta).
- **Causa:** Ausência de classes de grid e cards de KPI de fixos no `style.css`; reaproveitamento indevido da classe `.tipo-badge` (que possuía largura fixa rígida de 24px criada originalmente para ícones isolados de tabela); textos excessivamente extensos e poluídos em labels e botões de steppers; e aplicação concorrente da classe `.btn-danger` sobre `.btn-primary` sobrescrevendo a cor do texto com `color: var(--error) !important`.
- **Solução aplicada:**
  1. Criação do layout horizontal `.recorrentes-kpi-grid` e `.recorrentes-kpi-card` com indicadores destacados e semânticos: "📉 Despesas Mensais Fixas", "📈 Entradas Mensais Fixas" e "Balanço Fixo Projetado" (sem bordas coloridas desnecessárias), eliminando textos secundários e parênteses explicativos.
  2. Criação da classe `.recorrente-tipo-badge` com `display: inline-flex`, `white-space: nowrap` e padding proporcional, eliminando a quebra de linha nas badges dos cards.
  3. Simplificação dos labels do modal de cadastro para "Descrição" e "Dia de vencimento", e redução dos botões de ajuste de dia para os símbolos essenciais `+` e `−` via classe `.dia-stepper-btn`.
  4. Remoção da classe conflitante `.btn-danger` no botão primário do modal de exclusão e criação da classe `.btn-confirmar-exclusao` com texto branco e inclusão do emoji de alerta "⚠️ Confirmar Exclusão".
- **Como evitar no futuro:** Validar a aderência visual de novos componentes de resumo e badges com o design system antes de reutilizar classes criadas para outros contextos; priorizar objetividade e concisão em labels e botões de incremento; e evitar misturar classes utilitárias de cores de texto conflitantes em botões de ação destrutiva com estilo primário.

## 2026-10-06 - Inconsistências de cores semânticas nos KPIs e contraste invertido do botão de exclusão no tema escuro

- **Sintoma:** (1) O valor monetário do mostrador de despesas fixas mensais exibia a cor padrão do texto (branco) em vez de vermelho; e o mostrador do balanço fixo projetado não possuía distinção visual neutra para saldo zero; (2) O botão "⚠️ Confirmar Exclusão" utilizava cor de texto branca forçada (`#ffffff !important`) mesmo no tema escuro (Obsidian), quebrando o padrão de contraste do tema onde o botão primário lilás utiliza fonte escura condizente com a superfície.
- **Causa:** (1) Atribuição da classe `.despesa` apontando para `var(--text-primary)` em vez de `var(--error)` nos valores dos KPIs de recorrentes; ausência de classe de estado para balanço zero; (2) Uso de classe customizada com cor estática branca em vez do padrão nativo `.btn.btn-primary` (que utiliza `var(--primary)` e `var(--primary-contrast)`, respondendo de forma calibrada tanto no tema escuro quanto no claro, idêntico ao botão "+ Novo Fixo").
- **Solução aplicada:**
  1. Configurada a cor de `.recorrentes-kpi-value.despesa` para `var(--error)` (sempre vermelho) e mantida `.recorrentes-kpi-value.receita` com `var(--tertiary)` (sempre verde).
  2. Implementada lógica dinâmica no Balanço Fixo Projetado para aplicar classe verde (`saldo-positivo`) quando > 0, vermelha (`saldo-negativo`) quando < 0 e branca (`saldo-zero`) quando exatamente 0.
  3. Removida a sobreposição estática de cor branca e padronizado o botão de exclusão como `btn btn-primary` com o prefixo `⚠️ Confirmar Exclusão`, adotando o mesmo design e resposta dinâmica de contraste claro/escuro do botão "+ Novo Fixo".
- **Como evitar no futuro:** Sempre vincular botões de ação primária à classe canônica `.btn.btn-primary` sem impor regras com `!important` que burlem o chaveamento de `--primary-contrast` entre temas; e verificar que cores semânticas de despesas e receitas sempre usem `var(--error)` e `var(--tertiary)` respectivamente.

## 2026-10-06 - Invisibilidade do valor neutro (zero) do Balanço Fixo Projetado no tema claro

- **Sintoma:** Ao alternar para o tema claro, caso o Balanço Fixo Projetado resultasse em R$ 0,00, o texto monetário ficava completamente invisível por estar configurado com cor fixa branca (`#ffffff`), fundindo-se com o fundo claro da tela.
- **Causa:** Definição da classe `.recorrentes-kpi-value.saldo-zero` com valor estático `#ffffff` sem declarar a variação correspondente para o tema claro sob `[data-theme="light"]`.
- **Solução aplicada:** Adicionado seletor de tema claro `[data-theme="light"] .recorrentes-kpi-value.saldo-zero, body.light-theme .recorrentes-kpi-value.saldo-zero { color: #09090b; }`, garantindo texto preto no tema claro e preservando a cor branca no tema escuro.
- **Como evitar no futuro:** Sempre validar os dois modos de exibição (escuro e claro) ao aplicar cores literais em elementos tipográficos, assegurando a compatibilidade de contraste por meio das variáveis ou regras condicionais de tema.

## 2026-10-06 - Divergência de nomes de método e atributo em modelos (calcular_saldo vs calcular_saldo_atual e conta vs conta_origem) no Dashboard

- **Sintoma:** Endpoint `GET /api/dashboard/resumo` retornava erro HTTP 500 no carregamento de métricas e alertas.
- **Causa:** O controller acessava `c.calcular_saldo()` em vez de `c.calcular_saldo_atual()` no modelo `Conta`, e tentava acessar o relacionamento direto `item.conta` em vez de `item.conta_origem` no modelo `Lancamento`.
- **Solução aplicada:** Substituição da invocação por `c.calcular_saldo_atual()` e do relacionamento por `item.conta_origem.nome if item.conta_origem else "-"`.
- **Como evitar no futuro:** Sempre inspecionar a definição precisa dos métodos e relacionamentos mapeados nos arquivos em `app/models/` antes de chamá-los nos controllers.
