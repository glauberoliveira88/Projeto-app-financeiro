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


