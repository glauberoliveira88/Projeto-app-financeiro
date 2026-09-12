# Inventário de Insumos do Projeto

Este documento registra todos os arquivos de apoio e especificação presentes na pasta docs/.

> **Atenção:** A pasta `docs/` é destinada a documentação e apoio. Nenhum arquivo desta pasta é servido diretamente como asset público em execução. Os arquivos de interface necessários em tempo de execução (como logos e ícones) deverão ser copiados futuramente para a pasta pública de assets definida pela arquitetura (`app/static/img/` ou equivalente), respeitando a etapa de codificação.

| Arquivo | O que é | Usado pelo sistema em execução? | Onde será usado | Observações |
|---|---|---|---|---|
| `docs/FSD.md` | Documento de Especificação Funcional e Técnica (FSD) | Não | Documentação técnica | Documento mestre de requisitos funcionais, regras de negócio, modelagem de banco de dados MySQL, endpoints de API e arquitetura MVC. |
| `docs/DESIGN.md` | Guia de Diretrizes Visuais (Design System Obsidian) | Não | Documentação visual | Define as cores (zinc, violeta `#a78bfa`, esmeralda `#34d399`), tipografia (Geist), espaçamentos e regras do tema de alto contraste. |
| `docs/EXEMPLO DO DESIGN DA INTERFACE.html` | Protótipo interativo / Mockup HTML da tela de Dashboard | Não | Referência visual e de componentes | Código HTML de referência estilizado com Tailwind, exibindo layout, cartões de métricas, gráficos e bloco de alertas para orientar os componentes React/CSS. |
| `docs/EXEMPLO DO DESIGN DA INTERFACE.png` | Imagem / Captura de tela do protótipo de Dashboard | Não | Referência visual | Imagem estática renderizada do protótipo de interface para conferência rápida de layout e contraste. |
| `docs/logo_tema_escuro.png` | Imagem da Logotipo oficial para fundo escuro | Sim (precisará ser copiado para `app/static/`) | Telas de Login, Cadastro e Cabeçalho do Painel (Tema Escuro) | Logo com traços e contraste otimizados para o tema padrão *High-Contrast Dark* (Obsidian). |
| `docs/logo_tema_claro.png` | Imagem da Logotipo oficial para fundo claro | Sim (precisará ser copiado para `app/static/`) | Telas de Login, Cadastro e Cabeçalho do Painel (Tema Claro) | Logo com contraste otimizado para a variação de tema claro. |
