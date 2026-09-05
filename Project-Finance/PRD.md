Atue como Gerente de Produto e Analista de Sistemas sênior.

Seu objetivo é consolidar tudo o que foi discutido, alinhado, refinado e aprovado ao longo desta conversa e transformar em um Documento de Requisitos do Produto, também chamado de PRD.

O PRD deve ser puramente funcional.

Isso significa que ele deve explicar:

- o que o sistema deve fazer;
- qual problema ele resolve;
- quem usará o sistema;
- quais funcionalidades fazem parte da primeira versão;
- quais regras precisam ser respeitadas;
- quais informações o sistema precisa controlar;
- quais fluxos principais precisam existir;
- quais pontos ainda precisam ser esclarecidos antes da próxima etapa.

Não defina tecnologias, linguagens de programação, banco de dados, bibliotecas, frameworks, hospedagem, arquitetura de código, estrutura de pastas ou detalhes técnicos de implementação.

Essas decisões serão tomadas depois, no FSD.

Use linguagem clara, didática e acessível para pessoas que não sabem programar.

Explique termos técnicos quando eles aparecerem.

Analise minuciosamente todo o histórico desta conversa. Use apenas informações que tenham sido discutidas, aprovadas ou claramente confirmadas pelo usuário.

Não adicione funcionalidades novas apenas porque elas são comuns em sistemas parecidos.

Se identificar uma ideia interessante, mas que não foi aprovada, coloque-a como sugestão ou ponto pendente. Não coloque como parte confirmada da primeira versão.

Se encontrar dúvidas, lacunas, ambiguidades ou contradições, registre isso na seção "Pontos Pendentes Antes do FSD".

Organize o PRD nas seções abaixo.

---

# DOCUMENTO DE REQUISITOS DO PRODUTO (PRD)

## 1. Visão Geral do Produto

Explique, de forma simples, qual sistema será criado.

Inclua:

- nome provisório do sistema, se tiver sido definido;
- descrição resumida do sistema;
- público principal que usará o sistema;
- principal benefício esperado;
- contexto geral de uso.

Se o nome do sistema ainda não tiver sido definido, use um nome provisório coerente com a conversa e informe que ele pode ser alterado depois.

## 2. Problema que o Sistema Resolve

Descreva o cenário atual sem o sistema.

Explique quais dores, dificuldades, riscos, retrabalhos, perdas de tempo ou falhas de controle este sistema pretende reduzir.

Considere, quando fizer sentido para o tipo de sistema discutido:

- atividades feitas manualmente;
- informações espalhadas em vários lugares;
- dificuldade para acompanhar prazos, status, etapas ou responsáveis;
- risco de erros, esquecimentos ou retrabalho;
- falta de visão clara para tomada de decisão;
- dificuldade para encontrar registros, documentos ou históricos;
- falta de controle sobre quem fez alterações importantes.

Adapte a explicação ao sistema discutido nesta conversa.

Não use exemplos de outro tipo de sistema.

## 3. Objetivos do Sistema

Liste os objetivos principais do sistema.

Os objetivos devem explicar o que o sistema precisa alcançar para ser considerado útil.

Separe em:

### Objetivo principal

Explique o objetivo central do sistema em uma frase clara.

### Objetivos específicos

Liste objetivos menores que ajudam a alcançar o objetivo principal.

Cada objetivo específico deve estar ligado a uma necessidade real discutida na conversa.

## 4. Personas e Perfis de Usuário

Identifique os perfis de usuário que utilizarão o sistema.

Persona é um perfil de usuário que representa um tipo de pessoa que vai usar o sistema.

Para cada perfil, explique:

- quem é esse usuário;
- o que ele espera fazer no sistema;
- quais permissões básicas ele deve ter;
- quais ações ele não deve poder realizar, se isso já tiver sido definido.

Use uma tabela com as colunas:

| Perfil | Descrição simples | Principais ações no sistema | Permissões básicas |
| ------ | ----------------- | --------------------------- | ------------------ |

Inclua apenas perfis discutidos ou aprovados na conversa.

Se algum perfil parecer necessário, mas não tiver sido confirmado, registre isso em "Pontos Pendentes Antes do FSD".

## 5. Escopo da Primeira Versão

Liste todas as funcionalidades confirmadas para a primeira versão do sistema.

Escopo é o conjunto de funcionalidades que fará parte desta versão do projeto.

Use apenas funcionalidades que tenham sido discutidas, aprovadas ou claramente confirmadas pelo usuário.

Não adicione funcionalidades novas apenas porque são comuns em sistemas parecidos.

Agrupe as funcionalidades por áreas funcionais.

Área funcional é um grupo de funcionalidades relacionadas ao mesmo assunto ou parte do sistema.

Exemplos genéricos de áreas funcionais:

- cadastros principais;
- operação principal do sistema;
- acompanhamento e consultas;
- relatórios;
- administração do sistema;
- configurações;
- permissões de acesso;
- comunicação;
- integrações;
- arquivos e documentos;
- histórico e auditoria.

Crie os nomes das áreas conforme o tipo de sistema discutido na conversa.

Para cada funcionalidade, descreva brevemente:

- o que ela permite fazer;
- quem normalmente usará essa funcionalidade;
- qual problema ela ajuda a resolver;
- se existe alguma regra de negócio já definida para ela.

Se houver dúvida sobre uma funcionalidade estar ou não confirmada para a primeira versão, coloque essa dúvida na seção "Pontos Pendentes Antes do FSD" em vez de assumir.

## 6. Funcionalidades Fora de Escopo

Liste as funcionalidades, ideias ou melhorias que não farão parte da primeira versão.

Fora de escopo significa que o item não será desenvolvido agora.

Inclua nesta seção:

- funcionalidades discutidas, mas adiadas;
- ideias sugeridas pela IA, mas não aprovadas pelo usuário;
- recursos considerados avançados demais para a primeira versão;
- integrações, automações ou melhorias que dependem de uma etapa futura.

Explique brevemente por que cada item ficou fora da primeira versão, quando essa razão estiver clara na conversa.

Se não houver itens fora de escopo definidos, declare isso explicitamente.

## 7. Regras de Negócio

Liste as regras que definem como o sistema deve funcionar.

Regra de negócio é uma regra prática do funcionamento do sistema.

Exemplos genéricos de regras de negócio:

- quem pode realizar determinada ação;
- quando uma informação pode ou não ser alterada;
- quais dados são obrigatórios;
- quais situações exigem confirmação;
- quais registros devem ficar visíveis ou bloqueados;
- quais ações precisam gerar histórico;
- quais limites ou condições precisam ser respeitados.

Organize as regras por assunto, quando fizer sentido.

Use apenas regras discutidas, aprovadas ou claramente derivadas das decisões tomadas na conversa.

Se uma regra parecer necessária, mas não tiver sido confirmada, registre como ponto pendente.

## 8. Informações que o Sistema Precisa Controlar

Liste as principais informações que o sistema precisa armazenar, consultar ou controlar.

Não transforme esta seção em modelagem de banco de dados.

Neste momento, não crie tabelas, campos técnicos, tipos de dados ou relacionamentos de banco.

Explique de forma funcional.

Use uma tabela com as colunas:

| Informação | Para que serve no sistema | Observações importantes |
| ---------- | ------------------------- | ----------------------- |

Exemplos genéricos de informações que podem existir em sistemas:

- usuários;
- perfis de acesso;
- registros principais do negócio;
- categorias ou classificações;
- arquivos ou anexos;
- status;
- histórico de alterações;
- configurações;
- comentários ou observações;
- notificações;
- relatórios ou indicadores.

Adapte a lista conforme o sistema discutido nesta conversa.

Inclua apenas informações necessárias para as funcionalidades confirmadas.

## 9. Fluxos Principais de Uso

Descreva os principais fluxos de uso do sistema em linguagem simples.

Fluxo de uso é a sequência de passos que mostra como o usuário realiza uma tarefa dentro do sistema.

Inclua os fluxos mais importantes para a primeira versão.

Para cada fluxo, use este formato:

### Nome do fluxo

1. O usuário acessa a área correspondente.
2. O usuário executa a ação principal.
3. O sistema solicita ou exibe as informações necessárias.
4. O usuário confirma a ação.
5. O sistema valida as informações.
6. O sistema registra ou atualiza a informação.
7. O sistema exibe o resultado esperado.

Adapte os passos ao tipo de funcionalidade descrita.

Não invente telas, campos ou detalhes técnicos que não tenham sido definidos.

Se algum fluxo depender de uma decisão ainda não confirmada, registre isso em "Pontos Pendentes Antes do FSD".

## 10. Histórias de Usuário

Crie histórias de usuário para as funcionalidades principais da primeira versão.

História de usuário é uma frase simples que explica o que um perfil de usuário quer fazer e qual benefício espera obter.

Use o formato:

"Como [perfil de usuário], eu quero [funcionalidade] para [benefício]."

Crie pelo menos uma história de usuário para cada funcionalidade importante confirmada para a primeira versão.

Use apenas perfis e funcionalidades compatíveis com o que foi discutido nesta conversa.

## 11. Critérios de Aceitação

Crie critérios de aceitação para as funcionalidades mais importantes.

Critérios de aceitação são condições que ajudam a verificar se uma funcionalidade foi feita corretamente.

Use formato de checklist.

Para cada funcionalidade importante, inclua critérios objetivos como:

- [ ] O usuário consegue realizar a ação principal da funcionalidade.
- [ ] O sistema impede o salvamento quando informações obrigatórias não são preenchidas.
- [ ] O sistema exibe mensagens claras quando algo precisa ser corrigido.
- [ ] O sistema mostra o registro criado ou atualizado nas consultas correspondentes.
- [ ] O sistema respeita as permissões definidas para cada perfil de usuário.
- [ ] O sistema registra histórico quando essa regra tiver sido definida.

Adapte os critérios ao funcionamento do sistema discutido.

Não inclua critérios técnicos de programação, banco de dados, performance ou segurança técnica nesta etapa.

## 12. Consultas, Relatórios e Indicadores

Descreva quais informações o usuário precisa consultar, filtrar, acompanhar ou visualizar.

Use esta seção apenas se consultas, relatórios, painéis, indicadores ou listagens tiverem sido discutidos ou forem necessários para as funcionalidades confirmadas.

Não defina layout visual detalhado.

Explique apenas:

- quais informações precisam ser exibidas;
- quais filtros ou buscas são importantes;
- quais perfis devem acessar essas informações;
- quais decisões essas informações ajudam a tomar.

Se o sistema não precisar de relatórios ou indicadores na primeira versão, declare isso explicitamente.

## 13. Permissões e Segurança Funcional

Descreva as permissões básicas por perfil de usuário.

Segurança funcional significa definir o que cada perfil pode ou não pode fazer dentro do sistema.

Não entre em segurança técnica, criptografia, código, banco de dados, infraestrutura ou implementação.

Use uma tabela com as colunas:

| Perfil | Pode fazer | Não pode fazer | Observações |
| ------ | ---------- | -------------- | ----------- |

Considere ações como:

- visualizar;
- cadastrar;
- editar;
- excluir;
- aprovar;
- cancelar;
- configurar;
- gerenciar usuários;
- acessar relatórios;
- visualizar histórico;
- importar ou exportar informações.

Adapte as permissões ao sistema discutido nesta conversa.

Se alguma permissão não estiver clara, registre como ponto pendente.

## 14. Limitações da Primeira Versão

Explique as limitações assumidas para manter a primeira versão simples, viável e coerente com o que foi aprovado.

Limitação é algo que o sistema não fará agora ou fará de forma simplificada.

Inclua apenas limitações compatíveis com a conversa.

Exemplos genéricos de limitações:

- não haverá integração com sistemas externos;
- não haverá aplicativo mobile;
- não haverá automações avançadas;
- não haverá múltiplas unidades, empresas ou ambientes, salvo se isso tiver sido aprovado;
- não haverá personalizações avançadas;
- não haverá importação ou exportação de dados, salvo se isso tiver sido aprovado;
- não haverá fluxos de aprovação complexos, salvo se isso tiver sido aprovado.

Adapte esta seção ao sistema discutido.

## 15. Pontos Pendentes Antes do FSD

Liste dúvidas, ambiguidades, decisões abertas ou contradições que ainda precisam ser resolvidas antes da criação do FSD.

O FSD será o documento usado para orientar a IA codificadora, por isso não deve nascer com dúvidas importantes em aberto.

Inclua pontos pendentes quando houver dúvida sobre:

- regra de negócio;
- permissão de usuário;
- fluxo principal;
- funcionalidade da primeira versão;
- item fora de escopo;
- informação que o sistema precisa controlar;
- comportamento esperado em situações especiais.

Se não houver dúvidas pendentes, declare explicitamente:

"Não foram identificadas dúvidas funcionais pendentes para a criação do FSD."

## 16. Resumo Final do PRD

Finalize com um resumo curto explicando:

- o que será construído;
- quem usará;
- quais são as principais funcionalidades;
- o que ficará fora da primeira versão;
- quais pontos ainda precisam ser confirmados, se houver;
- se o projeto está pronto ou não para avançar para o FSD.

---

Gere o documento final em Markdown, com títulos claros, listas, tabelas e exemplos apenas quando eles ajudarem a explicar o próprio sistema discutido nesta conversa.

Não crie o FSD neste momento.

Não defina tecnologia neste momento.

Não invente requisitos.

Quando algo não estiver claro, registre como ponto pendente em vez de assumir.
