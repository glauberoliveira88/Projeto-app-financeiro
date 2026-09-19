/**
 * FinançasSimples — Aplicação React Principal (docs/FSD.md e docs/DESIGN.md)
 * 
 * Shell base com autenticação, alternância de tema de alto contraste e roteamento client-side.
 */

const { useState, useEffect, createContext, useContext } = React;

// Contexto Global de Autenticação e Tema
const AppContext = createContext(null);

function AppProvider({ children }) {
  const [tema, setTema] = useState(() => {
    return localStorage.getItem('financas_tema') || 'dark';
  });

  const [usuario, setUsuario] = useState(null);
  const [carregando, setCarregando] = useState(true);
  const [rotaAtual, setRotaAtual] = useState(window.location.pathname);

  // Sincroniza tema visual com DOM
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', tema);
    if (tema === 'light') {
      document.body.classList.add('light-theme');
    } else {
      document.body.classList.remove('light-theme');
    }
    localStorage.setItem('financas_tema', tema);
  }, [tema]);

  const alternarTema = () => {
    setTema((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  // Caminho dinâmico do logotipo oficial conforme o tema
  const logoSrc = tema === 'light' 
    ? '/static/img/logo_tema_claro.png' 
    : '/static/img/logo_tema_escuro.png';

  // Verifica sessão ativa ao carregar
  const verificarSessao = async () => {
    try {
      const res = await window.api.get('/api/auth/sessao');
      if (res && res.sucesso && res.autenticado) {
        setUsuario(res.usuario);
        if (res.usuario.tema_preferido && !localStorage.getItem('financas_tema')) {
          setTema(res.usuario.tema_preferido);
        }
      } else {
        setUsuario(null);
      }
    } catch (err) {
      setUsuario(null);
    } finally {
      setCarregando(false);
    }
  };

  useEffect(() => {
    verificarSessao();

    // Escuta evento popstate para navegação do navegador
    const handlePopState = () => {
      setRotaAtual(window.location.pathname);
    };
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const navegar = (caminho) => {
    window.history.pushState({}, '', caminho);
    setRotaAtual(caminho);
  };

  const logout = async () => {
    try {
      await window.api.post('/api/auth/logout');
    } catch (e) {
      console.warn('Erro ao deslogar:', e);
    }
    setUsuario(null);
    navegar('/login');
  };

  return (
    <AppContext.Provider
      value={{
        tema,
        alternarTema,
        logoSrc,
        usuario,
        setUsuario,
        carregando,
        rotaAtual,
        navegar,
        logout,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

function useApp() {
  return useContext(AppContext);
}

// ==============================================================================
// Componentes Auxiliares
// ==============================================================================

function BotaoAlternarTema() {
  const { tema, alternarTema } = useApp();
  return (
    <button
      type="button"
      className="theme-toggle-btn"
      onClick={alternarTema}
      title={tema === 'dark' ? 'Mudar para Tema Claro' : 'Mudar para Tema Escuro'}
      aria-label="Alternar tema de cores"
    >
      {tema === 'dark' ? '☀️' : '🌙'}
    </button>
  );
}

// ==============================================================================
// Tela de Login
// ==============================================================================
function TelaLogin() {
  const { logoSrc, navegar, setUsuario } = useApp();
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [erro, setErro] = useState('');
  const [aviso, setAviso] = useState(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('aviso') === 'google_nao_configurado') {
      return 'A integração com Google OAuth 2.0 requer credenciais válidas configuradas no config/config.py (GOOGLE_CLIENT_ID e GOOGLE_CLIENT_SECRET). Utilize seu e-mail e senha para acessar.';
    }
    return '';
  });
  const [bloqueado, setBloqueado] = useState(false);
  const [enviando, setEnviando] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErro('');
    setEnviando(true);

    try {
      const res = await window.api.post('/api/auth/login', { email, senha });
      const usuarioLogado = res && (res.usuario || (res.dados && res.dados.usuario));
      if (res && res.sucesso && usuarioLogado) {
        setUsuario(usuarioLogado);
        navegar('/dashboard');
      } else {
        setErro((res && res.erro) || 'Não foi possível autenticar. Tente novamente.');
      }
    } catch (err) {
      if (err.status === 429) {
        setBloqueado(true);
      }
      setErro(err.message || 'Erro ao efetuar login. Verifique suas credenciais.');
    } finally {
      setEnviando(false);
    }
  };

  return (
    <div className="auth-wrapper">
      <div className="theme-toggle-floating">
        <BotaoAlternarTema />
      </div>

      <div className="auth-header">
        <img src={logoSrc} alt="FinançasSimples" className="auth-logo" />
        <h1 className="auth-title">Acesse sua conta</h1>
        <p className="auth-subtitle">Controle financeiro simples, rápido e visual.</p>
      </div>

      <div className="auth-card">
        {aviso && <div className="alert alert-warning">{aviso}</div>}
        {erro && <div className="alert alert-error">{erro}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label" htmlFor="login-email">E-mail</label>
            <input
              id="login-email"
              type="email"
              required
              disabled={enviando || bloqueado}
              className="form-input"
              placeholder="seu.email@exemplo.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div className="form-group">
            <div className="form-row" style={{ marginBottom: 0 }}>
              <label className="form-label" htmlFor="login-senha">Senha</label>
              <a
                href="/recuperar-senha"
                onClick={(e) => {
                  e.preventDefault();
                  navegar('/recuperar-senha');
                }}
              >
                Esqueceu a senha?
              </a>
            </div>
            <input
              id="login-senha"
              type="password"
              required
              disabled={enviando || bloqueado}
              className="form-input"
              placeholder="Sua senha secreta"
              value={senha}
              onChange={(e) => setSenha(e.target.value)}
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary btn-block"
            disabled={enviando || bloqueado}
          >
            {enviando ? 'Entrando...' : 'Entrar no FinançasSimples'}
          </button>
        </form>

        <div className="divider">OU</div>

        <a href="/api/auth/google" className="btn btn-google btn-block">
          <svg width="18" height="18" viewBox="0 0 24 24">
            <path
              fill="#4285F4"
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
            />
            <path
              fill="#34A853"
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
            />
            <path
              fill="#FBBC05"
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
            />
            <path
              fill="#EA4335"
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
            />
          </svg>
          Entrar com o Google
        </a>

        <div style={{ marginTop: '1.5rem', textAlign: 'center', fontSize: '0.875rem' }}>
          <span style={{ color: 'var(--text-secondary)' }}>Não tem uma conta? </span>
          <a
            href="/cadastro"
            onClick={(e) => {
              e.preventDefault();
              navegar('/cadastro');
            }}
          >
            Cadastre-se gratuitamente
          </a>
        </div>
      </div>
    </div>
  );
}

// ==============================================================================
// Tela de Cadastro
// ==============================================================================
function TelaCadastro() {
  const { logoSrc, navegar, setUsuario } = useApp();
  const [nome, setNome] = useState('');
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [confirmacao, setConfirmacao] = useState('');
  const [erro, setErro] = useState('');
  const [enviando, setEnviando] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErro('');

    if (senha.length < 8) {
      setErro('A senha deve conter no mínimo 8 caracteres.');
      return;
    }

    if (senha !== confirmacao) {
      setErro('A confirmação de senha não confere.');
      return;
    }

    setEnviando(true);
    try {
      const res = await window.api.post('/api/auth/cadastro', {
        nome,
        email,
        senha,
        confirmacao_senha: confirmacao,
      });

      if (res && res.sucesso) {
        const usuarioCadastrado = res.usuario || (res.dados && res.dados.usuario);
        setUsuario(usuarioCadastrado);
        navegar('/dashboard');
      }
    } catch (err) {
      setErro(err.message || 'Erro ao criar conta. Verifique os dados informados.');
    } finally {
      setEnviando(false);
    }
  };

  return (
    <div className="auth-wrapper">
      <div className="theme-toggle-floating">
        <BotaoAlternarTema />
      </div>

      <div className="auth-header">
        <img src={logoSrc} alt="FinançasSimples" className="auth-logo" />
        <h1 className="auth-title">Crie sua conta</h1>
        <p className="auth-subtitle">Comece a organizar seu dinheiro em minutos.</p>
      </div>

      <div className="auth-card">
        {erro && <div className="alert alert-error">{erro}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label" htmlFor="cad-nome">Nome completo</label>
            <input
              id="cad-nome"
              type="text"
              required
              disabled={enviando}
              className="form-input"
              placeholder="Ex: Glauber Oliveira"
              value={nome}
              onChange={(e) => setNome(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="cad-email">E-mail</label>
            <input
              id="cad-email"
              type="email"
              required
              disabled={enviando}
              className="form-input"
              placeholder="seu.email@exemplo.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="cad-senha">Senha</label>
            <input
              id="cad-senha"
              type="password"
              required
              disabled={enviando}
              className="form-input"
              placeholder="Mínimo de 8 caracteres"
              value={senha}
              onChange={(e) => setSenha(e.target.value)}
            />
            <span className="form-helper">Mínimo de 8 caracteres para proteção da sua conta.</span>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="cad-confirma">Confirmar senha</label>
            <input
              id="cad-confirma"
              type="password"
              required
              disabled={enviando}
              className="form-input"
              placeholder="Digite novamente a senha"
              value={confirmacao}
              onChange={(e) => setConfirmacao(e.target.value)}
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary btn-block"
            disabled={enviando}
          >
            {enviando ? 'Criando sua conta...' : 'Criar minha conta'}
          </button>
        </form>

        <div className="divider">OU</div>

        <a href="/api/auth/google" className="btn btn-google btn-block">
          <svg width="18" height="18" viewBox="0 0 24 24">
            <path
              fill="#4285F4"
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
            />
            <path
              fill="#34A853"
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
            />
            <path
              fill="#FBBC05"
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
            />
            <path
              fill="#EA4335"
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
            />
          </svg>
          Cadastrar com o Google
        </a>

        <div style={{ marginTop: '1.5rem', textAlign: 'center', fontSize: '0.875rem' }}>
          <span style={{ color: 'var(--text-secondary)' }}>Já possui uma conta? </span>
          <a
            href="/login"
            onClick={(e) => {
              e.preventDefault();
              navegar('/login');
            }}
          >
            Faça login
          </a>
        </div>
      </div>
    </div>
  );
}

// ==============================================================================
// Tela de Recuperação de Senha
// ==============================================================================
function TelaRecuperarSenha() {
  const { logoSrc, navegar } = useApp();
  const [email, setEmail] = useState('');
  const [erro, setErro] = useState('');
  const [sucesso, setSucesso] = useState('');
  const [enviando, setEnviando] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErro('');
    setSucesso('');
    setEnviando(true);

    try {
      const res = await window.api.post('/api/auth/recuperar-senha', { email });
      if (res && res.sucesso) {
        setSucesso(
          res.mensagem ||
            'Se o e-mail estiver cadastrado, as instruções para redefinição foram enviadas com sucesso.'
        );
      }
    } catch (err) {
      setErro(err.message || 'Erro ao processar a solicitação. Tente novamente.');
    } finally {
      setEnviando(false);
    }
  };

  return (
    <div className="auth-wrapper">
      <div className="theme-toggle-floating">
        <BotaoAlternarTema />
      </div>

      <div className="auth-header">
        <img src={logoSrc} alt="FinançasSimples" className="auth-logo" />
        <h1 className="auth-title">Recuperar senha</h1>
        <p className="auth-subtitle">
          Informe seu e-mail para receber o link de redefinição de acesso.
        </p>
      </div>

      <div className="auth-card">
        {erro && <div className="alert alert-error">{erro}</div>}
        {sucesso && <div className="alert alert-success">{sucesso}</div>}

        {!sucesso ? (
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label" htmlFor="rec-email">E-mail cadastrado</label>
              <input
                id="rec-email"
                type="email"
                required
                disabled={enviando}
                className="form-input"
                placeholder="seu.email@exemplo.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
              <span className="form-helper">
                Enviaremos um link temporário válido por 60 minutos.
              </span>
            </div>

            <button
              type="submit"
              className="btn btn-primary btn-block"
              disabled={enviando}
            >
              {enviando ? 'Enviando...' : 'Enviar instruções de recuperação'}
            </button>
          </form>
        ) : (
          <div style={{ textAlign: 'center', marginTop: '1rem' }}>
            <p style={{ fontSize: '0.875rem', marginBottom: '1.5rem' }}>
              Verifique sua caixa de entrada e spam. Em ambiente local, confira o terminal de execução.
            </p>
          </div>
        )}

        <div style={{ marginTop: '1.5rem', textAlign: 'center', fontSize: '0.875rem' }}>
          <a
            href="/login"
            onClick={(e) => {
              e.preventDefault();
              navegar('/login');
            }}
          >
            ← Voltar para o Login
          </a>
        </div>
      </div>
    </div>
  );
}

// ==============================================================================
// Tela de Redefinição de Senha (com Token)
// ==============================================================================
function TelaRedefinirSenha() {
  const { logoSrc, navegar } = useApp();
  const [senha, setSenha] = useState('');
  const [confirmacao, setConfirmacao] = useState('');
  const [erro, setErro] = useState('');
  const [sucesso, setSucesso] = useState('');
  const [enviando, setEnviando] = useState(false);

  // Extrai o token da URL (/redefinir-senha/<token>) ou do atributo do body/app
  const pathname = window.location.pathname;
  const tokenUrl = pathname.startsWith('/redefinir-senha/') 
    ? pathname.replace('/redefinir-senha/', '').trim() 
    : '';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErro('');

    if (senha.length < 8) {
      setErro('A nova senha deve ter no mínimo 8 caracteres.');
      return;
    }

    if (senha !== confirmacao) {
      setErro('A confirmação de senha não confere.');
      return;
    }

    setEnviando(true);
    try {
      const res = await window.api.post('/api/auth/redefinir-senha', {
        token: tokenUrl,
        nova_senha: senha,
        confirmacao_senha: confirmacao,
      });

      if (res && res.sucesso) {
        setSucesso('Senha redefinida com sucesso! Redirecionando para o login...');
        setTimeout(() => {
          navegar('/login');
        }, 2000);
      }
    } catch (err) {
      setErro(err.message || 'Token inválido ou expirado. Solicite uma nova recuperação.');
    } finally {
      setEnviando(false);
    }
  };

  return (
    <div className="auth-wrapper">
      <div className="theme-toggle-floating">
        <BotaoAlternarTema />
      </div>

      <div className="auth-header">
        <img src={logoSrc} alt="FinançasSimples" className="auth-logo" />
        <h1 className="auth-title">Redefinir sua senha</h1>
        <p className="auth-subtitle">Crie uma nova senha segura para o seu painel.</p>
      </div>

      <div className="auth-card">
        {erro && <div className="alert alert-error">{erro}</div>}
        {sucesso && <div className="alert alert-success">{sucesso}</div>}

        {!sucesso && (
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label" htmlFor="red-senha">Nova senha</label>
              <input
                id="red-senha"
                type="password"
                required
                disabled={enviando}
                className="form-input"
                placeholder="Mínimo de 8 caracteres"
                value={senha}
                onChange={(e) => setSenha(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="red-confirma">Confirmar nova senha</label>
              <input
                id="red-confirma"
                type="password"
                required
                disabled={enviando}
                className="form-input"
                placeholder="Repita a nova senha"
                value={confirmacao}
                onChange={(e) => setConfirmacao(e.target.value)}
              />
            </div>

            <button
              type="submit"
              className="btn btn-primary btn-block"
              disabled={enviando}
            >
              {enviando ? 'Salvando...' : 'Salvar nova senha'}
            </button>
          </form>
        )}

        <div style={{ marginTop: '1.5rem', textAlign: 'center', fontSize: '0.875rem' }}>
          <a
            href="/login"
            onClick={(e) => {
              e.preventDefault();
              navegar('/login');
            }}
          >
            ← Ir para o Login
          </a>
        </div>
      </div>
    </div>
  );
}

// ==============================================================================
// Shell Autenticado (Base para Fases 6 a 11)
// ==============================================================================
function ShellAutenticado() {
  const { usuario, logoSrc, logout, rotaAtual, navegar } = useApp();

  return (
    <div className="app-layout">
      {/* Barra Lateral / Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <img src={logoSrc} alt="FinançasSimples" className="sidebar-logo" />
        </div>

        <nav className="sidebar-nav">
          <a
            href="/dashboard"
            className={`nav-link ${rotaAtual === '/dashboard' || rotaAtual === '/' ? 'active' : ''}`}
            onClick={(e) => {
              e.preventDefault();
              navegar('/dashboard');
            }}
          >
            <span>📊</span> Painel Principal
          </a>
          <a
            href="/lancamentos"
            className={`nav-link ${rotaAtual === '/lancamentos' ? 'active' : ''}`}
            onClick={(e) => {
              e.preventDefault();
              navegar('/lancamentos');
            }}
          >
            <span>💳</span> Lançamentos
          </a>
          <a
            href="/contas"
            className={`nav-link ${rotaAtual === '/contas' ? 'active' : ''}`}
            onClick={(e) => {
              e.preventDefault();
              navegar('/contas');
            }}
          >
            <span>🏦</span> Contas & Carteiras
          </a>
          <a
            href="/categorias"
            className={`nav-link ${rotaAtual === '/categorias' ? 'active' : ''}`}
            onClick={(e) => {
              e.preventDefault();
              navegar('/categorias');
            }}
          >
            <span>🏷️</span> Categorias & Tetos
          </a>
          <a
            href="/recorrentes"
            className={`nav-link ${rotaAtual === '/recorrentes' ? 'active' : ''}`}
            onClick={(e) => {
              e.preventDefault();
              navegar('/recorrentes');
            }}
          >
            <span>🔁</span> Fixos Recorrentes
          </a>
          <a
            href="/configuracoes"
            className={`nav-link ${rotaAtual === '/configuracoes' ? 'active' : ''}`}
            onClick={(e) => {
              e.preventDefault();
              navegar('/configuracoes');
            }}
          >
            <span>⚙️</span> Configurações
          </a>
        </nav>

        <div className="sidebar-footer">
          <div style={{ fontSize: '0.8125rem', padding: '0.25rem 0.5rem' }}>
            <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{usuario.nome}</div>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', overflow: 'hidden', textOverflow: 'ellipsis' }}>
              {usuario.email}
            </div>
          </div>
          <button
            type="button"
            className="btn btn-secondary btn-block"
            onClick={logout}
            style={{ marginTop: '0.5rem' }}
          >
            Sair do sistema
          </button>
        </div>
      </aside>

      {/* Conteúdo Principal */}
      <main className="main-content">
        <header className="top-bar">
          <div>
            <h2 style={{ fontSize: '1.5rem', marginBottom: '0.25rem' }}>Painel Geral</h2>
            <p style={{ fontSize: '0.875rem' }}>
              Bem-vindo ao <strong>FinançasSimples</strong>, {usuario.nome.split(' ')[0]}!
            </p>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <BotaoAlternarTema />
          </div>
        </header>

        {/* Card de Boas-Vindas da Fase 5 */}
        <div
          style={{
            backgroundColor: 'var(--surface-base)',
            border: 'var(--border-width) solid var(--border-color)',
            borderRadius: 'var(--radius-lg)',
            padding: '2rem',
            marginBottom: '2rem',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
            <span style={{ fontSize: '1.5rem' }}>✨</span>
            <h3 style={{ fontSize: '1.25rem' }}>Ambiente Base Configurado com Sucesso (Fase 5)</h3>
          </div>
          <p style={{ marginBottom: '1rem', color: 'var(--text-secondary)' }}>
            A casca React e o Design System Obsidian de alto contraste estão ativos, operando com proteção CSRF
            transparente e isolamento estrito de dados por usuário.
          </p>
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.4rem 0.8rem',
              backgroundColor: 'var(--tertiary-bg)',
              color: 'var(--tertiary)',
              border: '1px solid var(--tertiary)',
              borderRadius: 'var(--radius-md)',
              fontSize: '0.8125rem',
              fontWeight: 600,
            }}
          >
            ✓ Sessão Ativa: {usuario.email}
          </div>
        </div>
      </main>
    </div>
  );
}

// ==============================================================================
// Roteador e Componente Principal (App)
// ==============================================================================
function App() {
  const { usuario, carregando, rotaAtual } = useApp();

  if (carregando) {
    return (
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          backgroundColor: 'var(--bg-app)',
          color: 'var(--text-secondary)',
          fontSize: '0.9375rem',
        }}
      >
        Carregando FinançasSimples...
      </div>
    );
  }

  // Se o usuário estiver autenticado, renderiza o Shell Autenticado
  if (usuario) {
    return <ShellAutenticado />;
  }

  // Roteamento para rotas públicas desautenticadas
  if (rotaAtual === '/cadastro') {
    return <TelaCadastro />;
  }
  if (rotaAtual === '/recuperar-senha') {
    return <TelaRecuperarSenha />;
  }
  if (rotaAtual.startsWith('/redefinir-senha')) {
    return <TelaRedefinirSenha />;
  }

  // Padrão para não logados: tela de Login
  return <TelaLogin />;
}

// Inicialização da aplicação React no elemento #root
const container = document.getElementById('root');
if (container) {
  const root = ReactDOM.createRoot(container);
  root.render(
    <AppProvider>
      <App />
    </AppProvider>
  );
}
