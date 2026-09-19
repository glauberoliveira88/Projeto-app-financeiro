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
