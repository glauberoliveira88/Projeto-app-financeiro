/**
 * FinançasSimples — Cliente HTTP Padronizado (docs/FSD.md - Seções 5 e 19.3)
 * 
 * Gerencia requisições assíncronas à API Flask, anexando automaticamente
 * o cabeçalho X-CSRFToken a partir da meta tag injetada no index.html.
 */

(function () {
  'use strict';

  function obterCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
  }

  function atualizarCsrfToken(novoToken) {
    if (!novoToken) return;
    let meta = document.querySelector('meta[name="csrf-token"]');
    if (!meta) {
      meta = document.createElement('meta');
      meta.name = 'csrf-token';
      document.head.appendChild(meta);
    }
    meta.setAttribute('content', novoToken);
  }

  async function apiFetch(endpoint, options = {}) {
    const config = {
      method: options.method || 'GET',
      headers: {
        'Accept': 'application/json',
        ...(options.headers || {}),
      },
      credentials: 'same-origin',
      ...options,
    };

    const metodoUpper = config.method.toUpperCase();
    const metodosMutadores = ['POST', 'PUT', 'PATCH', 'DELETE'];

    // Anexa cabeçalho X-CSRFToken transparente para operações mutadoras
    if (metodosMutadores.includes(metodoUpper)) {
      const token = obterCsrfToken();
      if (token && !config.headers['X-CSRFToken'] && !config.headers['X-CSRF-Token']) {
        config.headers['X-CSRFToken'] = token;
      }
    }

    // Serializa corpo para JSON se for um objeto literal
    if (config.body && typeof config.body === 'object' && !(config.body instanceof FormData)) {
      config.headers['Content-Type'] = 'application/json';
      config.body = JSON.stringify(config.body);
    }

    try {
      const response = await fetch(endpoint, config);
      const contentType = response.headers.get('content-type') || '';
      let dados = null;

      if (contentType.includes('application/json')) {
        dados = await response.json();
      } else {
        const texto = await response.text();
        dados = { sucesso: response.ok, mensagem: texto };
      }

      // Se a resposta fornecer um novo CSRF token, sincroniza na meta tag
      if (dados && dados.csrf_token) {
        atualizarCsrfToken(dados.csrf_token);
      }

      // Se falhou por token CSRF inválido ou ausente e não for retry, busca novo token e tenta de novo
      if (!response.ok && response.status === 400 && dados && dados.codigo === 'CSRF_INVALIDO' && !options._isRetry) {
        try {
          const csrfRes = await fetch('/api/auth/csrf', { credentials: 'same-origin' });
          if (csrfRes.ok) {
            const csrfJson = await csrfRes.json();
            if (csrfJson && csrfJson.csrf_token) {
              atualizarCsrfToken(csrfJson.csrf_token);
              const headersAtualizados = { ...(options.headers || {}), 'X-CSRFToken': csrfJson.csrf_token };
              return await apiFetch(endpoint, { ...options, headers: headersAtualizados, _isRetry: true });
            }
          }
        } catch (e) {
          console.warn('[CSRF Retry Falhou]', e);
        }
      }

      if (!response.ok) {
        const mensagemErro = (dados && dados.erro) || `Erro HTTP ${response.status}: ${response.statusText}`;
        const erro = new Error(mensagemErro);
        erro.status = response.status;
        erro.dados = dados;
        throw erro;
      }

      return dados;
    } catch (err) {
      console.error('[API Fetch Error]', err);
      throw err;
    }
  }

  // Métodos utilitários de conveniência
  const api = {
    get: (endpoint, options = {}) => apiFetch(endpoint, { ...options, method: 'GET' }),
    post: (endpoint, body, options = {}) => apiFetch(endpoint, { ...options, method: 'POST', body }),
    put: (endpoint, body, options = {}) => apiFetch(endpoint, { ...options, method: 'PUT', body }),
    patch: (endpoint, body, options = {}) => apiFetch(endpoint, { ...options, method: 'PATCH', body }),
    delete: (endpoint, options = {}) => apiFetch(endpoint, { ...options, method: 'DELETE' }),
    obterCsrfToken,
  };

  window.api = api;
})();
