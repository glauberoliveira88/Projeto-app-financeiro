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
// Utilitários de Formatação
// ==============================================================================
function formatarMoeda(valor) {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(valor || 0);
}

// ==============================================================================
// Componente: Modal Genérico
// ==============================================================================
function Modal({ titulo, onFechar, children }) {
  // Modal não fecha ao clicar no overlay de fundo para evitar perda acidental de dados
  return (
    <div className="modal-overlay">
      <div className="modal-container" role="dialog" aria-modal="true">
        <div className="modal-header">
          <h3 className="modal-titulo">{titulo}</h3>
          <button type="button" className="modal-fechar" onClick={onFechar} aria-label="Fechar modal">✕</button>
        </div>
        <div className="modal-body">{children}</div>
      </div>
    </div>
  );
}

// ==============================================================================
// Componente: Tela de Contas e Carteiras
// ==============================================================================
function TelaContas() {
  const [contas, setContas] = React.useState([]);
  const [saldoTotal, setSaldoTotal] = React.useState(0);
  const [carregando, setCarregando] = React.useState(true);
  const [erro, setErro] = React.useState('');
  const [modalAberto, setModalAberto] = React.useState(false);
  const [contaEmEdicao, setContaEmEdicao] = React.useState(null);
  const [formNome, setFormNome] = React.useState('');
  const [formSaldo, setFormSaldo] = React.useState('0');
  const [salvando, setSalvando] = React.useState(false);
  const [mensagemSucesso, setMensagemSucesso] = React.useState('');
  const [erroModal, setErroModal] = React.useState('');

  const carregarContas = async () => {
    setCarregando(true);
    setErro('');
    try {
      const res = await window.api.get('/api/contas');
      if (res && res.sucesso) {
        setContas(res.dados.contas);
        setSaldoTotal(res.dados.saldo_total_ativo);
      }
    } catch (err) {
      setErro(err.message || 'Erro ao carregar contas. Tente novamente.');
    } finally {
      setCarregando(false);
    }
  };

  React.useEffect(() => {
    carregarContas();
  }, []);

  const abrirModalNova = () => {
    setContaEmEdicao(null);
    setFormNome('');
    setFormSaldo('0');
    setErroModal('');
    setModalAberto(true);
  };

  const abrirModalEditar = (conta) => {
    setContaEmEdicao(conta);
    setFormNome(conta.nome);
    setFormSaldo('');
    setErroModal('');
    setModalAberto(true);
  };

  const fecharModal = () => {
    setModalAberto(false);
    setContaEmEdicao(null);
    setErroModal('');
  };

  const exibirSucesso = (msg) => {
    setMensagemSucesso(msg);
    setTimeout(() => setMensagemSucesso(''), 3500);
  };

  const handleSalvar = async (e) => {
    e.preventDefault();
    setErroModal('');
    const nome = formNome.trim();
    if (!nome) { setErroModal('O nome da conta é obrigatório.'); return; }

    setSalvando(true);
    try {
      if (contaEmEdicao) {
        // Edição: altera apenas o nome
        const res = await window.api.put(`/api/contas/${contaEmEdicao.id}`, { nome });
        if (res && res.sucesso) {
          exibirSucesso(res.mensagem || 'Conta atualizada com sucesso.');
          fecharModal();
          carregarContas();
        } else {
          setErroModal((res && res.erro) || 'Erro ao atualizar conta.');
        }
      } else {
        // Criação
        const saldoNum = parseFloat(formSaldo.replace(',', '.')) || 0;
        const res = await window.api.post('/api/contas', { nome, saldo_inicial: saldoNum });
        if (res && res.sucesso) {
          exibirSucesso(res.mensagem || 'Conta criada com sucesso.');
          fecharModal();
          carregarContas();
        } else {
          setErroModal((res && res.erro) || 'Erro ao criar conta.');
        }
      }
    } catch (err) {
      setErroModal(err.message || 'Erro inesperado. Tente novamente.');
    } finally {
      setSalvando(false);
    }
  };

  const handleArquivar = async (conta) => {
    if (!window.confirm(`Deseja arquivar a conta "${conta.nome}"? Ela ficará inativa para novos lançamentos, mas o histórico será preservado.`)) return;
    try {
      const res = await window.api.patch(`/api/contas/${conta.id}/arquivar`);
      if (res && res.sucesso) {
        exibirSucesso(res.mensagem || 'Conta arquivada.');
        carregarContas();
      } else {
        setErro((res && res.erro) || 'Erro ao arquivar conta.');
      }
    } catch (err) {
      setErro(err.message || 'Erro ao arquivar conta.');
    }
  };

  const handleReativar = async (conta) => {
    try {
      const res = await window.api.patch(`/api/contas/${conta.id}/reativar`);
      if (res && res.sucesso) {
        exibirSucesso(res.mensagem || 'Conta reativada.');
        carregarContas();
      } else {
        setErro((res && res.erro) || 'Erro ao reativar conta.');
      }
    } catch (err) {
      setErro(err.message || 'Erro ao reativar conta.');
    }
  };

  const handleExcluir = async (conta) => {
    if (!window.confirm(`Tem certeza que deseja excluir permanentemente a conta "${conta.nome}"? Esta ação não pode ser desfeita.`)) return;
    try {
      const res = await window.api.delete(`/api/contas/${conta.id}`);
      if (res && res.sucesso) {
        exibirSucesso(res.mensagem || 'Conta excluída.');
        carregarContas();
      } else {
        // Se tiver histórico, orienta o usuário a arquivar
        setErro((res && res.erro) || 'Não foi possível excluir a conta.');
      }
    } catch (err) {
      setErro(err.message || 'Erro ao excluir conta.');
    }
  };

  const contasAtivas = contas.filter(c => c.status === 'ativo');
  const contasArquivadas = contas.filter(c => c.status === 'arquivado');

  return (
    <div className="module-container">
      {/* Cabeçalho do módulo */}
      <div className="module-header">
        <div>
          <h2 className="module-title">Contas &amp; Carteiras</h2>
          <p className="module-subtitle">Gerencie onde seu dinheiro está custodiado.</p>
        </div>
        <button type="button" className="btn btn-primary" onClick={abrirModalNova}>
          + Nova Conta
        </button>
      </div>

      {/* Alertas */}
      {mensagemSucesso && <div className="alert alert-success">{mensagemSucesso}</div>}
      {erro && <div className="alert alert-error">{erro}<button className="alert-fechar" onClick={() => setErro('')}>✕</button></div>}

      {/* Card de saldo consolidado */}
      <div className="summary-card">
        <div className="summary-label">Saldo Total (Contas Ativas)</div>
        <div className={`summary-value ${saldoTotal >= 0 ? 'valor-positivo' : 'valor-negativo'}`}>
          {formatarMoeda(saldoTotal)}
        </div>
        <div className="summary-meta">{contasAtivas.length} conta{contasAtivas.length !== 1 ? 's' : ''} ativa{contasAtivas.length !== 1 ? 's' : ''}</div>
      </div>

      {carregando ? (
        <div className="skeleton-list">
          {[1, 2, 3].map(i => <div key={i} className="skeleton-card" />)}
        </div>
      ) : (
        <>
          {/* Grade de Contas Ativas */}
          {contasAtivas.length > 0 ? (
            <div className="section-block">
              <h3 className="section-title">Contas Ativas</h3>
              <div className="cards-grid">
                {contasAtivas.map(conta => (
                  <div key={conta.id} className="account-card">
                    <div className="account-card-header">
                      <span className="account-name">{conta.nome}</span>
                      <span className="badge badge-active">Ativa</span>
                    </div>
                    <div className={`account-balance ${conta.saldo_atual >= 0 ? 'valor-positivo' : 'valor-negativo'}`}>
                      {formatarMoeda(conta.saldo_atual)}
                    </div>
                    <div className="account-meta">Saldo inicial: {formatarMoeda(conta.saldo_inicial)}</div>
                    <div className="account-actions">
                      <button
                        type="button"
                        className="btn btn-ghost btn-sm"
                        onClick={() => abrirModalEditar(conta)}
                        title="Editar nome"
                      >
                        ✏️ Editar
                      </button>
                      <button
                        type="button"
                        className="btn btn-ghost btn-sm"
                        onClick={() => handleArquivar(conta)}
                        title="Arquivar conta"
                      >
                        📦 Arquivar
                      </button>
                      <button
                        type="button"
                        className="btn btn-ghost btn-sm btn-danger"
                        onClick={() => handleExcluir(conta)}
                        title="Excluir conta"
                      >
                        🗑️ Excluir
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="empty-state">
              <div className="empty-icon">🏦</div>
              <p className="empty-title">Nenhuma conta ativa</p>
              <p className="empty-subtitle">Crie sua primeira conta para começar a registrar lançamentos.</p>
              <button type="button" className="btn btn-primary" onClick={abrirModalNova}>
                + Criar Primeira Conta
              </button>
            </div>
          )}

          {/* Seção de Contas Arquivadas */}
          {contasArquivadas.length > 0 && (
            <div className="section-block section-archived">
              <h3 className="section-title">Contas Arquivadas</h3>
              <div className="cards-grid">
                {contasArquivadas.map(conta => (
                  <div key={conta.id} className="account-card account-card-archived">
                    <div className="account-card-header">
                      <span className="account-name">{conta.nome}</span>
                      <span className="badge badge-archived">Arquivada</span>
                    </div>
                    <div className="account-balance" style={{ color: 'var(--text-muted)' }}>
                      {formatarMoeda(conta.saldo_atual)}
                    </div>
                    <div className="account-actions">
                      <button
                        type="button"
                        className="btn btn-ghost btn-sm"
                        onClick={() => handleReativar(conta)}
                        title="Reativar conta"
                      >
                        ♻️ Reativar
                      </button>
                      <button
                        type="button"
                        className="btn btn-ghost btn-sm btn-danger"
                        onClick={() => handleExcluir(conta)}
                        title="Excluir conta permanentemente"
                      >
                        🗑️ Excluir
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {/* Modal de Criação / Edição */}
      {modalAberto && (
        <Modal
          titulo={contaEmEdicao ? `Editar: ${contaEmEdicao.nome}` : 'Nova Conta'}
          onFechar={fecharModal}
        >
          <form onSubmit={handleSalvar}>
            {erroModal && <div className="alert alert-error">{erroModal}</div>}

            <div className="form-group">
              <label className="form-label" htmlFor="conta-nome">Nome da Conta</label>
              <input
                id="conta-nome"
                type="text"
                required
                maxLength={100}
                className="form-input"
                placeholder="Ex: Nubank, Carteira, Poupança..."
                value={formNome}
                onChange={(e) => setFormNome(e.target.value)}
                disabled={salvando}
                autoFocus
              />
            </div>

            {!contaEmEdicao && (
              <div className="form-group">
                <label className="form-label" htmlFor="conta-saldo">Saldo Inicial (R$)</label>
                <input
                  id="conta-saldo"
                  type="number"
                  step="0.01"
                  min="0"
                  className="form-input"
                  placeholder="0,00"
                  value={formSaldo}
                  onChange={(e) => setFormSaldo(e.target.value)}
                  disabled={salvando}
                />
                <span className="form-helper">Informe quanto você possui nesta conta agora.</span>
              </div>
            )}

            <div className="modal-footer">
              <button type="button" className="btn btn-secondary" onClick={fecharModal} disabled={salvando}>
                Cancelar
              </button>
              <button type="submit" className="btn btn-primary" disabled={salvando}>
                {salvando ? 'Salvando...' : (contaEmEdicao ? 'Salvar Alterações' : 'Criar Conta')}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}

// ==============================================================================
// ==============================================================================
// Componente: Tela de Dashboard / Painel Principal (Fase 10)
// ==============================================================================
function TelaDashboard() {
  const dataHoje = new Date();
  const [mes, setMes] = React.useState(dataHoje.getMonth() + 1);
  const [ano, setAno] = React.useState(dataHoje.getFullYear());

  const [dados, setDados] = React.useState(null);
  const [carregando, setCarregando] = React.useState(true);
  const [erro, setErro] = React.useState('');
  const [mensagemSucesso, setMensagemSucesso] = React.useState('');
  const [quitandoId, setQuitandoId] = React.useState(null);

  // Estados para o Modal de Novo Lançamento Rápido no Dashboard
  const [modalAberto, setModalAberto] = React.useState(false);
  const [abaModal, setAbaModal] = React.useState('despesa'); // 'despesa', 'receita', 'transferencia'
  const [formValor, setFormValor] = React.useState('0,00');
  const [formDataCompetencia, setFormDataCompetencia] = React.useState('');
  const [formDataVencimento, setFormDataVencimento] = React.useState('');
  const [formDescricao, setFormDescricao] = React.useState('');
  const [formCategoriaId, setFormCategoriaId] = React.useState('');
  const [formContaId, setFormContaId] = React.useState('');
  const [formContaDestinoId, setFormContaDestinoId] = React.useState('');
  const [formFormaPagamento, setFormFormaPagamento] = React.useState('PIX');
  const [formStatus, setFormStatus] = React.useState('pago');
  const [formObservacao, setFormObservacao] = React.useState('');
  const [salvando, setSalvando] = React.useState(false);
  const [erroModal, setErroModal] = React.useState('');
  const [avisoSaldoInsuficiente, setAvisoSaldoInsuficiente] = React.useState('');

  const [contas, setContas] = React.useState([]);
  const [categorias, setCategorias] = React.useState([]);

  const nomesMeses = [
    'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
  ];

  const exibirSucesso = (msg) => {
    setMensagemSucesso(msg);
    setTimeout(() => setMensagemSucesso(''), 4000);
  };

  // Carrega os dados consolidados do dashboard
  const carregarDashboard = async () => {
    setCarregando(true);
    setErro('');
    try {
      const res = await window.api.get(`/api/dashboard/resumo?mes=${mes}&ano=${ano}`);
      if (res && res.sucesso && res.dados) {
        setDados(res.dados);
      } else {
        setErro((res && res.erro) || 'Não foi possível carregar os dados do painel.');
      }
    } catch (err) {
      setErro(err.message || 'Erro de comunicação ao carregar o painel.');
    } finally {
      setCarregando(false);
    }
  };

  // Carrega contas e categorias para o modal de novo lançamento
  const carregarMetadados = async () => {
    try {
      const [resContas, resCategorias] = await Promise.all([
        window.api.get('/api/contas'),
        window.api.get('/api/categorias'),
      ]);
      if (resContas && resContas.sucesso) {
        setContas(resContas.dados.contas || []);
      }
      if (resCategorias && resCategorias.sucesso) {
        setCategorias(resCategorias.dados.categorias || []);
      }
    } catch {
      // Metadados auxiliares opcionais
    }
  };

  React.useEffect(() => {
    carregarDashboard();
  }, [mes, ano]);

  React.useEffect(() => {
    carregarMetadados();
  }, []);

  // Navegação entre meses
  const mesAnterior = () => {
    if (mes === 1) {
      setMes(12);
      setAno(ano - 1);
    } else {
      setMes(mes - 1);
    }
  };

  const mesSeguinte = () => {
    if (mes === 12) {
      setMes(1);
      setAno(ano + 1);
    } else {
      setMes(mes + 1);
    }
  };

  const mesAtual = () => {
    const agora = new Date();
    setMes(agora.getMonth() + 1);
    setAno(agora.getFullYear());
  };

  // Quitação rápida de alerta pendente
  const marcarComoPago = async (alerta) => {
    setQuitandoId(alerta.id);
    try {
      const res = await window.api.patch(`/api/lancamentos/${alerta.id}/pagar`);
      if (res && res.sucesso) {
        exibirSucesso(`"${alerta.descricao}" marcada como paga com sucesso!`);
        carregarDashboard();
      } else {
        setErro((res && res.erro) || 'Não foi possível atualizar o status do lançamento.');
      }
    } catch (err) {
      setErro(err.message || 'Erro ao processar quitação rápida.');
    } finally {
      setQuitandoId(null);
    }
  };

  // Abertura do modal de novo lançamento
  const abrirNovoLancamento = (tipo = 'despesa') => {
    const hojeStr = new Date().toISOString().split('T')[0];
    setAbaModal(tipo);
    setFormValor('0,00');
    setFormDataCompetencia(hojeStr);
    setFormDataVencimento(hojeStr);
    setFormDescricao('');
    setFormFormaPagamento('PIX');
    setFormStatus('pago');
    setFormObservacao('');
    setErroModal('');
    setAvisoSaldoInsuficiente('');

    // Preenche conta padrão
    const contaAtiva = contas.find(c => c.status === 'ativo');
    if (contaAtiva) {
      setFormContaId(contaAtiva.id.toString());
    } else {
      setFormContaId('');
    }

    // Preenche categoria padrão para o tipo
    if (tipo !== 'transferencia') {
      const catValida = categorias.find(c => c.tipo === tipo && c.status === 'ativo');
      setFormCategoriaId(catValida ? catValida.id.toString() : '');
    } else {
      setFormCategoriaId('');
    }

    setModalAberto(true);
  };

  const fecharModal = () => {
    setModalAberto(false);
    setErroModal('');
    setAvisoSaldoInsuficiente('');
  };

  const mudarAbaModal = (novaAba) => {
    setAbaModal(novaAba);
    setErroModal('');
    setAvisoSaldoInsuficiente('');
    if (novaAba !== 'transferencia') {
      const catValida = categorias.find(c => c.tipo === novaAba && c.status === 'ativo');
      setFormCategoriaId(catValida ? catValida.id.toString() : '');
    } else {
      setFormCategoriaId('');
    }
  };

  // Manipulação de valor com stepper de R$ 1,00
  const parseValorNumerico = (vStr) => {
    if (!vStr) return 0;
    const limpo = vStr.toString().replace(/\./g, '').replace(',', '.');
    const num = parseFloat(limpo);
    return isNaN(num) ? 0 : num;
  };

  const formatarValorString = (num) => {
    return num.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  };

  const incrementarValor = (delta) => {
    const atual = parseValorNumerico(formValor);
    const novo = Math.max(0, atual + delta);
    setFormValor(formatarValorString(novo));
  };

  const handleValorChange = (e) => {
    const digitos = e.target.value.replace(/\D/g, '');
    if (!digitos) {
      setFormValor('0,00');
      return;
    }
    const centavos = parseInt(digitos, 10);
    const reais = (centavos / 100).toFixed(2);
    setFormValor(formatarValorString(parseFloat(reais)));
  };

  // Submissão do formulário de novo lançamento
  const handleSalvar = async (e, forcarTransferencia = false) => {
    if (e) e.preventDefault();
    setErroModal('');
    setSalvando(true);

    const valorNumerico = parseValorNumerico(formValor);
    if (valorNumerico <= 0) {
      setErroModal('O valor deve ser maior que zero (R$ 0,00).');
      setSalvando(false);
      return;
    }

    if (!formDataCompetencia) {
      setErroModal('Informe a data contábil (competência).');
      setSalvando(false);
      return;
    }

    try {
      if (abaModal === 'transferencia') {
        if (!formContaId || !formContaDestinoId) {
          setErroModal('Selecione as contas de origem e de destino.');
          setSalvando(false);
          return;
        }
        if (formContaId === formContaDestinoId) {
          setErroModal('A conta de destino deve ser diferente da conta de origem.');
          setSalvando(false);
          return;
        }

        const payload = {
          valor: valorNumerico,
          data_competencia: formDataCompetencia,
          conta_id: Number(formContaId),
          conta_destino_id: Number(formContaDestinoId),
          descricao: formDescricao.trim() || undefined,
          forma_pagamento: formFormaPagamento,
          observacao: formObservacao.trim() || undefined,
          confirmar_saldo_negativo: forcarTransferencia,
        };

        const res = await window.api.post('/api/lancamentos/transferencia', payload);
        if (res && res.sucesso) {
          exibirSucesso(res.mensagem || 'Transferência realizada com sucesso.');
          fecharModal();
          carregarDashboard();
        } else if (res && res.requer_confirmacao) {
          setAvisoSaldoInsuficiente(res.erro);
        } else {
          setErroModal((res && res.erro) || 'Erro ao processar transferência.');
        }
      } else {
        if (!formDescricao.trim()) {
          setErroModal('Informe a descrição do lançamento.');
          setSalvando(false);
          return;
        }
        if (!formCategoriaId) {
          setErroModal('Selecione uma categoria.');
          setSalvando(false);
          return;
        }
        if (!formContaId) {
          setErroModal('Selecione uma conta bancária ou carteira.');
          setSalvando(false);
          return;
        }

        const payload = {
          tipo: abaModal,
          valor: valorNumerico,
          data_competencia: formDataCompetencia,
          data_vencimento: formDataVencimento || formDataCompetencia,
          descricao: formDescricao.trim(),
          categoria_id: Number(formCategoriaId),
          conta_id: Number(formContaId),
          forma_pagamento: formFormaPagamento,
          status: formStatus,
          observacao: formObservacao.trim() || undefined,
        };

        const res = await window.api.post('/api/lancamentos', payload);
        if (res && res.sucesso) {
          exibirSucesso('Lançamento cadastrado com sucesso!');
          fecharModal();
          carregarDashboard();
        } else {
          setErroModal((res && res.erro) || 'Erro ao cadastrar lançamento.');
        }
      }
    } catch (err) {
      setErroModal(err.message || 'Erro inesperado ao salvar lançamento.');
    } finally {
      setSalvando(false);
    }
  };

  const metricas = dados?.metricas || {
    saldo_mes: 0,
    total_receitas: 0,
    total_receitas_pagas: 0,
    total_despesas: 0,
    total_despesas_pagas: 0,
    saldo_total_contas: 0,
  };

  const graficoCategorias = dados?.grafico_despesas_categoria || [];
  const alertasVencidos = dados?.alertas?.vencidos || [];
  const alertasAVencer = dados?.alertas?.a_vencer || [];
  const totalAlertas = (dados?.alertas?.total_alertas) || 0;

  const saldoMesClasse = metricas.saldo_mes > 0 ? 'positivo' : metricas.saldo_mes < 0 ? 'negativo' : 'neutro';

  return (
    <div className="module-container">
      {/* Alertas globais de feedback */}
      {mensagemSucesso && <div className="alert alert-success">{mensagemSucesso}</div>}
      {erro && <div className="alert alert-error">{erro}</div>}

      {/* Barra de Navegação de Períodos e Ação Rápida */}
      <div className="dashboard-periodo-bar">
        <div className="dashboard-periodo-controls">
          <button
            type="button"
            className="dashboard-periodo-btn"
            onClick={mesAnterior}
            title="Mês Anterior"
          >
            ◀
          </button>
          <span className="dashboard-periodo-titulo">
            {nomesMeses[mes - 1]} de {ano}
          </span>
          <button
            type="button"
            className="dashboard-periodo-btn"
            onClick={mesSeguinte}
            title="Próximo Mês"
          >
            ▶
          </button>
          <button
            type="button"
            className="dashboard-periodo-btn"
            onClick={mesAtual}
            title="Ir para o Mês Atual"
            style={{ marginLeft: '0.25rem' }}
          >
            Hoje
          </button>
        </div>

        <button
          type="button"
          className="btn-novo-lancamento-destaque"
          onClick={() => abrirNovoLancamento('despesa')}
        >
          <span>＋</span> Novo Lançamento
        </button>
      </div>

      {carregando ? (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Carregando indicadores do painel...</p>
        </div>
      ) : (
        <>
          {/* Grade de Indicadores Principais (KPIs) */}
          <div className="dashboard-kpi-grid">
            {/* Saldo Líquido do Mês */}
            <div className="dashboard-kpi-card">
              <div className="dashboard-kpi-header">
                <span className="dashboard-kpi-label">
                  ⚖️ Saldo Líquido do Mês
                </span>
                <div className="dashboard-kpi-icon">💰</div>
              </div>
              <div className={`dashboard-kpi-value ${saldoMesClasse}`}>
                {formatarMoeda(metricas.saldo_mes)}
              </div>
              <span className="dashboard-kpi-sub">
                Receitas Pagas − Despesas Pagas
              </span>
            </div>

            {/* Total de Receitas */}
            <div className="dashboard-kpi-card">
              <div className="dashboard-kpi-header">
                <span className="dashboard-kpi-label">
                  📈 Receitas do Mês
                </span>
                <div className="dashboard-kpi-icon" style={{ color: 'var(--tertiary)' }}>↑</div>
              </div>
              <div className="dashboard-kpi-value positivo">
                {formatarMoeda(metricas.total_receitas)}
              </div>
              <span className="dashboard-kpi-sub">
                Pagas: {formatarMoeda(metricas.total_receitas_pagas)}
              </span>
            </div>

            {/* Total de Despesas */}
            <div className="dashboard-kpi-card">
              <div className="dashboard-kpi-header">
                <span className="dashboard-kpi-label">
                  📉 Despesas do Mês
                </span>
                <div className="dashboard-kpi-icon" style={{ color: 'var(--error)' }}>↓</div>
              </div>
              <div className="dashboard-kpi-value negativo">
                {formatarMoeda(metricas.total_despesas)}
              </div>
              <span className="dashboard-kpi-sub">
                Pagas: {formatarMoeda(metricas.total_despesas_pagas)}
              </span>
            </div>

            {/* Saldo Consolidado em Carteiras */}
            <div className="dashboard-kpi-card">
              <div className="dashboard-kpi-header">
                <span className="dashboard-kpi-label">
                  🏦 Saldo Total em Contas
                </span>
                <div className="dashboard-kpi-icon">🏛️</div>
              </div>
              <div className="dashboard-kpi-value neutro">
                {formatarMoeda(metricas.saldo_total_contas)}
              </div>
              <span className="dashboard-kpi-sub">
                Consolidado de carteiras ativas
              </span>
            </div>
          </div>

          {/* Seção Principal: Gráfico Monocromático e Bloco de Alertas */}
          <div className="dashboard-main-grid">
            {/* Gráfico Monocromático de Despesas por Categoria */}
            <div className="dashboard-panel-card">
              <div className="dashboard-panel-header">
                <h3 className="dashboard-panel-title">
                  <span>📊</span> Despesas por Categoria
                </h3>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  {nomesMeses[mes - 1]}/{ano}
                </span>
              </div>

              {graficoCategorias.length === 0 ? (
                <div className="empty-state" style={{ padding: '2.5rem 1rem' }}>
                  <div className="empty-icon">🏷️</div>
                  <p className="empty-title">Nenhuma despesa no período</p>
                  <p className="empty-subtitle">
                    Quando você registrar gastos em {nomesMeses[mes - 1]}, a distribuição por categoria será exibida aqui.
                  </p>
                </div>
              ) : (
                <div className="grafico-barras-lista">
                  {graficoCategorias.map((item) => (
                    <div key={item.categoria_id || item.nome} className="grafico-barra-item">
                      <div className="grafico-barra-info">
                        <span className="grafico-barra-nome">
                          <span>•</span> {item.nome}
                        </span>
                        <div className="grafico-barra-valores">
                          <span className="grafico-barra-montante">
                            {formatarMoeda(item.total)}
                          </span>
                          <span className="grafico-barra-percentual">
                            {item.porcentagem}%
                          </span>
                        </div>
                      </div>
                      <div className="grafico-barra-track">
                        <div
                          className="grafico-barra-fill"
                          style={{ width: `${Math.min(100, Math.max(2, item.porcentagem))}%` }}
                          title={`${item.nome}: ${formatarMoeda(item.total)} (${item.porcentagem}%)`}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Bloco de Alertas de Vencimento com Ação Rápida */}
            <div className="dashboard-panel-card">
              <div className="dashboard-panel-header">
                <h3 className="dashboard-panel-title">
                  <span>🔔</span> Alertas de Vencimento
                </h3>
                {totalAlertas > 0 && (
                  <span
                    style={{
                      background: 'rgba(239, 68, 68, 0.15)',
                      color: 'var(--error)',
                      fontSize: '0.75rem',
                      fontWeight: 700,
                      padding: '0.2rem 0.5rem',
                      borderRadius: 'var(--radius-sm)',
                    }}
                  >
                    {totalAlertas} {totalAlertas === 1 ? 'pendência' : 'pendências'}
                  </span>
                )}
              </div>

              {totalAlertas === 0 ? (
                <div className="empty-state" style={{ padding: '2.5rem 1rem' }}>
                  <div className="empty-icon" style={{ color: 'var(--tertiary)' }}>✓</div>
                  <p className="empty-title">Tudo em dia!</p>
                  <p className="empty-subtitle">
                    Você não possui contas vencidas ou a vencer nos próximos 5 dias.
                  </p>
                </div>
              ) : (
                <div className="alertas-container">
                  {/* Vencidos (em atraso) */}
                  {alertasVencidos.map((alerta) => (
                    <div key={alerta.id} className="alerta-card-item vencido">
                      <div className="alerta-info">
                        <span className="alerta-descricao">{alerta.descricao}</span>
                        <span className="alerta-detalhe">
                          <span className="alerta-tag-vencido">⚠️ Vencida há {Math.abs(alerta.dias_diferenca)} dia(s)</span>
                          <span>•</span>
                          <span>{alerta.categoria}</span>
                        </span>
                      </div>
                      <div className="alerta-acoes">
                        <span className="alerta-valor">{formatarMoeda(alerta.valor)}</span>
                        <button
                          type="button"
                          className="alerta-btn-pagar"
                          onClick={() => marcarComoPago(alerta)}
                          disabled={quitandoId === alerta.id}
                          title="Marcar conta como paga agora"
                        >
                          {quitandoId === alerta.id ? '...' : '✓ Pagar'}
                        </button>
                      </div>
                    </div>
                  ))}

                  {/* A Vencer nos próximos 5 dias */}
                  {alertasAVencer.map((alerta) => (
                    <div key={alerta.id} className="alerta-card-item a_vencer">
                      <div className="alerta-info">
                        <span className="alerta-descricao">{alerta.descricao}</span>
                        <span className="alerta-detalhe">
                          <span className="alerta-tag-a-vencer">
                            🕒 {alerta.dias_diferenca === 0 ? 'Vence hoje!' : `Vence em ${alerta.dias_diferenca} dia(s)`}
                          </span>
                          <span>•</span>
                          <span>{alerta.categoria}</span>
                        </span>
                      </div>
                      <div className="alerta-acoes">
                        <span className="alerta-valor">{formatarMoeda(alerta.valor)}</span>
                        <button
                          type="button"
                          className="alerta-btn-pagar"
                          onClick={() => marcarComoPago(alerta)}
                          disabled={quitandoId === alerta.id}
                          title="Marcar conta como paga agora"
                        >
                          {quitandoId === alerta.id ? '...' : '✓ Pagar'}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </>
      )}

      {/* Modal de Novo Lançamento Rápido no Dashboard */}
      {modalAberto && (
        <Modal titulo="Novo Lançamento" onFechar={fecharModal}>
          <div className="modal-tabs">
            <button
              type="button"
              className={`modal-tab-btn tab-despesa ${abaModal === 'despesa' ? 'active' : ''}`}
              onClick={() => mudarAbaModal('despesa')}
            >
              ↑ Despesa
            </button>
            <button
              type="button"
              className={`modal-tab-btn tab-receita ${abaModal === 'receita' ? 'active' : ''}`}
              onClick={() => mudarAbaModal('receita')}
            >
              ↓ Receita
            </button>
            <button
              type="button"
              className={`modal-tab-btn tab-transferencia ${abaModal === 'transferencia' ? 'active' : ''}`}
              onClick={() => mudarAbaModal('transferencia')}
            >
              ⇄ Transferência
            </button>
          </div>

          <form onSubmit={handleSalvar}>
            {erroModal && <div className="alert alert-error">{erroModal}</div>}

            {avisoSaldoInsuficiente && (
              <div className="modal-warning-box">
                <div className="modal-warning-title">⚠️ Saldo Insuficiente na Origem</div>
                <p style={{ margin: '0 0 0.75rem 0' }}>{avisoSaldoInsuficiente}</p>
                <button
                  type="button"
                  className="btn btn-primary btn-sm btn-danger"
                  onClick={() => handleSalvar(null, true)}
                  disabled={salvando}
                >
                  Confirmar e Transferir Mesmo Assim
                </button>
              </div>
            )}

            {/* Campo Monetário com Stepper de R$ 1,00 */}
            <div className="form-group">
              <label className="form-label" htmlFor="dash-form-valor">Valor</label>
              <div className="currency-input-wrapper">
                <span className="currency-prefix">R$</span>
                <input
                  id="dash-form-valor"
                  type="text"
                  inputMode="numeric"
                  className="form-input currency-input-field"
                  value={formValor}
                  onChange={handleValorChange}
                  disabled={salvando}
                  placeholder="0,00"
                  required
                />
                <div className="stepper-buttons-container">
                  <button
                    type="button"
                    className="stepper-btn stepper-up"
                    onClick={() => incrementarValor(1)}
                    disabled={salvando}
                    title="Aumentar R$ 1,00"
                  >
                    ▲
                  </button>
                  <button
                    type="button"
                    className="stepper-btn stepper-down"
                    onClick={() => incrementarValor(-1)}
                    disabled={salvando}
                    title="Diminuir R$ 1,00"
                  >
                    ▼
                  </button>
                </div>
              </div>
            </div>

            {/* Descrição (Apenas para Receita e Despesa) */}
            {abaModal !== 'transferencia' && (
              <div className="form-group">
                <label className="form-label" htmlFor="dash-form-desc">Descrição</label>
                <input
                  id="dash-form-desc"
                  type="text"
                  className="form-input"
                  placeholder="Ex: Supermercado, Salário, Internet"
                  value={formDescricao}
                  onChange={(e) => setFormDescricao(e.target.value)}
                  disabled={salvando}
                  maxLength={200}
                  required
                />
              </div>
            )}

            {/* Datas */}
            <div className="form-row-2">
              <div className="form-group">
                <label className="form-label" htmlFor="dash-form-comp">
                  {abaModal === 'transferencia' ? 'Data da Transferência' : 'Data Contábil'}
                </label>
                <input
                  id="dash-form-comp"
                  type="date"
                  className="form-input"
                  value={formDataCompetencia}
                  onChange={(e) => setFormDataCompetencia(e.target.value)}
                  disabled={salvando}
                  required
                />
              </div>

              {abaModal !== 'transferencia' && (
                <div className="form-group">
                  <label className="form-label" htmlFor="dash-form-venc">Data de Vencimento</label>
                  <input
                    id="dash-form-venc"
                    type="date"
                    className="form-input"
                    value={formDataVencimento}
                    onChange={(e) => setFormDataVencimento(e.target.value)}
                    disabled={salvando}
                    required
                  />
                </div>
              )}
            </div>

            {/* Seleção de Categoria e Conta para Receita/Despesa */}
            {abaModal !== 'transferencia' ? (
              <div className="form-row-2">
                <div className="form-group">
                  <label className="form-label" htmlFor="dash-form-cat">Categoria</label>
                  <select
                    id="dash-form-cat"
                    className="form-select"
                    value={formCategoriaId}
                    onChange={(e) => setFormCategoriaId(e.target.value)}
                    disabled={salvando}
                    required
                  >
                    <option value="">Selecione uma categoria...</option>
                    {categorias
                      .filter((c) => c.tipo === abaModal && c.status === 'ativo')
                      .map((c) => (
                        <option key={c.id} value={c.id}>{c.nome}</option>
                      ))}
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label" htmlFor="dash-form-conta">Conta / Carteira</label>
                  <select
                    id="dash-form-conta"
                    className="form-select"
                    value={formContaId}
                    onChange={(e) => setFormContaId(e.target.value)}
                    disabled={salvando}
                    required
                  >
                    <option value="">Selecione a conta...</option>
                    {contas
                      .filter((c) => c.status === 'ativo')
                      .map((c) => (
                        <option key={c.id} value={c.id}>{c.nome}</option>
                      ))}
                  </select>
                </div>
              </div>
            ) : (
              /* Seleção de Contas para Transferência */
              <div className="form-row-2">
                <div className="form-group">
                  <label className="form-label" htmlFor="dash-transf-origem">Conta de Origem (Sai)</label>
                  <select
                    id="dash-transf-origem"
                    className="form-select"
                    value={formContaId}
                    onChange={(e) => setFormContaId(e.target.value)}
                    disabled={salvando}
                    required
                  >
                    <option value="">Selecione a origem...</option>
                    {contas
                      .filter((c) => c.status === 'ativo')
                      .map((c) => (
                        <option key={c.id} value={c.id}>{c.nome}</option>
                      ))}
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label" htmlFor="dash-transf-destino">Conta de Destino (Entra)</label>
                  <select
                    id="dash-transf-destino"
                    className="form-select"
                    value={formContaDestinoId}
                    onChange={(e) => setFormContaDestinoId(e.target.value)}
                    disabled={salvando}
                    required
                  >
                    <option value="">Selecione o destino...</option>
                    {contas
                      .filter((c) => c.status === 'ativo' && c.id.toString() !== formContaId)
                      .map((c) => (
                        <option key={c.id} value={c.id}>{c.nome}</option>
                      ))}
                  </select>
                </div>
              </div>
            )}

            {/* Forma de Pagamento e Status */}
            <div className="form-row-2">
              <div className="form-group">
                <label className="form-label" htmlFor="dash-form-fp">Forma de Pagamento</label>
                <select
                  id="dash-form-fp"
                  className="form-select"
                  value={formFormaPagamento}
                  onChange={(e) => setFormFormaPagamento(e.target.value)}
                  disabled={salvando}
                >
                  <option value="Dinheiro">Dinheiro</option>
                  <option value="PIX">PIX</option>
                  <option value="Cartão de Débito">Cartão de Débito</option>
                  <option value="Cartão de Crédito">Cartão de Crédito</option>
                  <option value="Boleto">Boleto</option>
                  <option value="Transferência">Transferência</option>
                </select>
              </div>

              {abaModal !== 'transferencia' && (
                <div className="form-group">
                  <label className="form-label" htmlFor="dash-form-status">Status de Pagamento</label>
                  <select
                    id="dash-form-status"
                    className="form-select"
                    value={formStatus}
                    onChange={(e) => setFormStatus(e.target.value)}
                    disabled={salvando}
                  >
                    <option value="pago">Já liquidado / Pago</option>
                    <option value="pendente">Pendente / Em aberto</option>
                  </select>
                </div>
              )}
            </div>

            {/* Observações */}
            <div className="form-group">
              <label className="form-label" htmlFor="dash-form-obs">Observações (opcional)</label>
              <textarea
                id="dash-form-obs"
                className="form-input"
                rows="2"
                placeholder="Anotações adicionais sobre este lançamento..."
                value={formObservacao}
                onChange={(e) => setFormObservacao(e.target.value)}
                disabled={salvando}
              />
            </div>

            <div className="modal-footer">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={fecharModal}
                disabled={salvando}
              >
                Cancelar
              </button>
              <button
                type="submit"
                className="btn btn-primary"
                disabled={salvando}
              >
                {salvando ? 'Salvando...' : 'Salvar Lançamento'}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}

// ==============================================================================
// Componente: Tela de Lançamentos (Fase 8)
// ==============================================================================
function TelaLancamentos() {
  const dataHoje = new Date();
  const [mes, setMes] = React.useState(dataHoje.getMonth() + 1);
  const [ano, setAno] = React.useState(dataHoje.getFullYear());
  const [filtroTipo, setFiltroTipo] = React.useState('todos');
  const [filtroStatus, setFiltroStatus] = React.useState('todos');
  const [filtroConta, setFiltroConta] = React.useState('');
  const [filtroCategoria, setFiltroCategoria] = React.useState('');
  const [termoBusca, setTermoBusca] = React.useState('');

  const [lancamentos, setLancamentos] = React.useState([]);
  const [resumo, setResumo] = React.useState({
    total_receitas: 0,
    total_despesas: 0,
    total_transferencias: 0,
    saldo_periodo: 0,
    total_itens: 0,
    total_pendentes: 0,
    total_vencidos: 0,
  });

  const [contas, setContas] = React.useState([]);
  const [categorias, setCategorias] = React.useState([]);
  const [carregando, setCarregando] = React.useState(true);
  const [erro, setErro] = React.useState('');
  const [mensagemSucesso, setMensagemSucesso] = React.useState('');

  // Estados dos Modais
  const [modalAberto, setModalAberto] = React.useState(false);
  const [lancamentoEmEdicao, setLancamentoEmEdicao] = React.useState(null);
  const [abaModal, setAbaModal] = React.useState('despesa'); // 'despesa', 'receita', 'transferencia'

  // Campos do Formulário
  const [formValor, setFormValor] = React.useState('0,00');
  const [formDataCompetencia, setFormDataCompetencia] = React.useState('');
  const [formDataVencimento, setFormDataVencimento] = React.useState('');
  const [formDescricao, setFormDescricao] = React.useState('');
  const [formCategoriaId, setFormCategoriaId] = React.useState('');
  const [formContaId, setFormContaId] = React.useState('');
  const [formContaDestinoId, setFormContaDestinoId] = React.useState('');
  const [formFormaPagamento, setFormFormaPagamento] = React.useState('PIX');
  const [formStatus, setFormStatus] = React.useState('pago');
  const [formObservacao, setFormObservacao] = React.useState('');
  const [salvando, setSalvando] = React.useState(false);
  const [erroModal, setErroModal] = React.useState('');
  const [avisoSaldoInsuficiente, setAvisoSaldoInsuficiente] = React.useState('');

  // Modal de Exclusão
  const [modalExcluirAberto, setModalExcluirAberto] = React.useState(false);
  const [lancamentoParaExcluir, setLancamentoParaExcluir] = React.useState(null);
  const [excluindo, setExcluindo] = React.useState(false);

  const nomesMeses = [
    'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
  ];

  const exibirSucesso = (msg) => {
    setMensagemSucesso(msg);
    setTimeout(() => setMensagemSucesso(''), 4000);
  };

  // Carrega opções de contas e categorias auxiliares
  const carregarMetadados = async () => {
    try {
      const [resContas, resCategorias] = await Promise.all([
        window.api.get('/api/contas'),
        window.api.get('/api/categorias'),
      ]);
      if (resContas && resContas.sucesso) {
        setContas(resContas.dados.contas || []);
      }
      if (resCategorias && resCategorias.sucesso) {
        setCategorias(resCategorias.dados.categorias || []);
      }
    } catch (e) {
      console.warn('Erro ao carregar contas/categorias:', e);
    }
  };

  // Carrega os lançamentos com base nos filtros
  const carregarLancamentos = async () => {
    setCarregando(true);
    setErro('');
    try {
      const params = new URLSearchParams();
      if (mes) params.append('mes', mes);
      if (ano) params.append('ano', ano);
      if (filtroTipo !== 'todos') params.append('tipo', filtroTipo);
      if (filtroStatus !== 'todos') params.append('status', filtroStatus);
      if (filtroConta) params.append('conta_id', filtroConta);
      if (filtroCategoria) params.append('categoria_id', filtroCategoria);
      if (termoBusca) params.append('busca', termoBusca);

      const res = await window.api.get(`/api/lancamentos?${params.toString()}`);
      if (res && res.sucesso) {
        setLancamentos(res.dados.lancamentos || []);
        if (res.dados.resumo) {
          setResumo(res.dados.resumo);
        }
      } else {
        setErro((res && res.erro) || 'Erro ao carregar movimentações financeiras.');
      }
    } catch (err) {
      setErro(err.message || 'Erro ao carregar movimentações financeiras.');
    } finally {
      setCarregando(false);
    }
  };

  useEffect(() => {
    carregarMetadados();
  }, []);

  useEffect(() => {
    carregarLancamentos();
  }, [mes, ano, filtroTipo, filtroStatus, filtroConta, filtroCategoria, termoBusca]);

  // Navegação de Período
  const navegarPeriodo = (direcao) => {
    if (direcao === -1) {
      if (mes === 1) {
        setMes(12);
        setAno(ano - 1);
      } else {
        setMes(mes - 1);
      }
    } else if (direcao === 1) {
      if (mes === 12) {
        setMes(1);
        setAno(ano + 1);
      } else {
        setMes(mes + 1);
      }
    } else {
      const hoje = new Date();
      setMes(hoje.getMonth() + 1);
      setAno(hoje.getFullYear());
    }
  };

  // Funções de formatação e steppers de moeda
  const parseValorNumerico = (texto) => {
    if (!texto) return 0;
    const limpo = String(texto).replace(/\./g, '').replace(',', '.');
    const n = parseFloat(limpo);
    return isNaN(n) ? 0 : n;
  };

  const formatarValorString = (num) => {
    return Number(num || 0).toLocaleString('pt-BR', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  };

  const handleValorChange = (e) => {
    let digits = e.target.value.replace(/\D/g, '');
    if (!digits) {
      setFormValor('0,00');
      return;
    }
    const num = parseInt(digits, 10) / 100;
    setFormValor(formatarValorString(num));
  };

  const ajustarValorStepper = (delta) => {
    const atual = parseValorNumerico(formValor);
    const novo = Math.max(0, atual + delta);
    setFormValor(formatarValorString(novo));
  };

  // Abertura do modal de criação
  const abrirModalCriacao = (tipoInicial = 'despesa') => {
    setLancamentoEmEdicao(null);
    setAbaModal(tipoInicial);
    setFormValor('0,00');

    // Data de hoje em YYYY-MM-DD
    const hojeStr = new Date().toISOString().split('T')[0];
    setFormDataCompetencia(hojeStr);
    setFormDataVencimento(hojeStr);
    setFormDescricao('');
    setFormObservacao('');
    setFormFormaPagamento('PIX');
    setFormStatus('pago');
    setErroModal('');
    setAvisoSaldoInsuficiente('');

    // Preenche primeira conta ativa
    const contasAtivas = contas.filter(c => c.status === 'ativo');
    if (contasAtivas.length > 0) {
      setFormContaId(contasAtivas[0].id);
      if (contasAtivas.length > 1) {
        setFormContaDestinoId(contasAtivas[1].id);
      } else {
        setFormContaDestinoId('');
      }
    } else {
      setFormContaId('');
      setFormContaDestinoId('');
    }

    // Preenche primeira categoria correspondente ao tipo
    const catsDoTipo = categorias.filter(c => c.tipo === tipoInicial && c.status === 'ativo');
    if (catsDoTipo.length > 0) {
      setFormCategoriaId(catsDoTipo[0].id);
    } else {
      setFormCategoriaId('');
    }

    setModalAberto(true);
  };

  // Alterna aba no modal de criação
  const mudarAbaModal = (novaAba) => {
    setAbaModal(novaAba);
    setErroModal('');
    setAvisoSaldoInsuficiente('');

    if (novaAba !== 'transferencia') {
      const cats = categorias.filter(c => c.tipo === novaAba && c.status === 'ativo');
      if (cats.length > 0 && (!formCategoriaId || !cats.some(c => c.id === Number(formCategoriaId)))) {
        setFormCategoriaId(cats[0].id);
      }
    }
  };

  // Abertura do modal de edição
  const abrirModalEdicao = (lancamento) => {
    setLancamentoEmEdicao(lancamento);
    setAbaModal(lancamento.tipo);
    setFormValor(formatarValorString(lancamento.valor));
    setFormDataCompetencia(lancamento.data_competencia || '');
    setFormDataVencimento(lancamento.data_vencimento || lancamento.data_competencia || '');
    setFormDescricao(lancamento.descricao || '');
    setFormCategoriaId(lancamento.categoria_id ? String(lancamento.categoria_id) : '');
    setFormContaId(lancamento.conta_id ? String(lancamento.conta_id) : '');
    setFormContaDestinoId(lancamento.conta_destino_id ? String(lancamento.conta_destino_id) : '');
    setFormFormaPagamento(lancamento.forma_pagamento || 'Dinheiro');
    setFormStatus(lancamento.status || 'pago');
    setFormObservacao(lancamento.observacao || '');
    setErroModal('');
    setAvisoSaldoInsuficiente('');
    setModalAberto(true);
  };

  const fecharModal = () => {
    setModalAberto(false);
    setLancamentoEmEdicao(null);
    setErroModal('');
    setAvisoSaldoInsuficiente('');
  };

  // Submissão do Formulário de Criação / Edição
  const handleSalvar = async (e, forcarTransferencia = false) => {
    if (e && e.preventDefault) e.preventDefault();
    setErroModal('');
    setSalvando(true);

    const valorNumerico = parseValorNumerico(formValor);
    if (valorNumerico <= 0) {
      setErroModal('O valor do lançamento deve ser maior que zero.');
      setSalvando(false);
      return;
    }

    if (!formDataCompetencia) {
      setErroModal('A data de competência é obrigatória.');
      setSalvando(false);
      return;
    }

    try {
      if (abaModal === 'transferencia') {
        // Fluxo de Transferência
        if (!formContaId || !formContaDestinoId) {
          setErroModal('Selecione a conta de origem e a conta de destino.');
          setSalvando(false);
          return;
        }

        if (Number(formContaId) === Number(formContaDestinoId)) {
          setErroModal('A conta de destino deve ser diferente da conta de origem.');
          setSalvando(false);
          return;
        }

        const payload = {
          valor: valorNumerico,
          data_competencia: formDataCompetencia,
          conta_id: Number(formContaId),
          conta_destino_id: Number(formContaDestinoId),
          descricao: formDescricao.trim() || undefined,
          forma_pagamento: formFormaPagamento,
          observacao: formObservacao.trim() || undefined,
          confirmar_saldo_negativo: forcarTransferencia,
        };

        let res;
        if (lancamentoEmEdicao) {
          res = await window.api.put(`/api/lancamentos/${lancamentoEmEdicao.id}`, payload);
        } else {
          res = await window.api.post('/api/lancamentos/transferencia', payload);
        }

        if (res && res.sucesso) {
          exibirSucesso(res.mensagem || 'Transferência realizada com sucesso.');
          fecharModal();
          carregarLancamentos();
          carregarMetadados();
        } else if (res && res.requer_confirmacao) {
          // Alerta preventivo de saldo insuficiente na origem (FSD Seção 14.2 item 6)
          setAvisoSaldoInsuficiente(res.erro);
        } else {
          setErroModal((res && res.erro) || 'Erro ao processar transferência.');
        }
      } else {
        // Fluxo de Receita ou Despesa
        if (!formDescricao.trim()) {
          setErroModal('Informe a descrição do lançamento.');
          setSalvando(false);
          return;
        }

        if (!formCategoriaId) {
          setErroModal('Selecione uma categoria para o lançamento.');
          setSalvando(false);
          return;
        }

        if (!formContaId) {
          setErroModal('Selecione uma conta bancária ou carteira.');
          setSalvando(false);
          return;
        }

        const payload = {
          tipo: abaModal,
          valor: valorNumerico,
          data_competencia: formDataCompetencia,
          data_vencimento: formDataVencimento || formDataCompetencia,
          descricao: formDescricao.trim(),
          categoria_id: Number(formCategoriaId),
          conta_id: Number(formContaId),
          forma_pagamento: formFormaPagamento,
          status: formStatus,
          observacao: formObservacao.trim() || undefined,
        };

        let res;
        if (lancamentoEmEdicao) {
          res = await window.api.put(`/api/lancamentos/${lancamentoEmEdicao.id}`, payload);
        } else {
          res = await window.api.post('/api/lancamentos', payload);
        }

        if (res && res.sucesso) {
          exibirSucesso(res.mensagem || 'Lançamento salvo com sucesso.');
          fecharModal();
          carregarLancamentos();
          carregarMetadados();
        } else {
          setErroModal((res && res.erro) || 'Não foi possível salvar o lançamento.');
        }
      }
    } catch (err) {
      setErroModal(err.message || 'Erro inesperado ao salvar.');
    } finally {
      setSalvando(false);
    }
  };

  // Alternância rápida de status (pago <-> pendente)
  const handleAlternarStatus = async (lancamento) => {
    try {
      const res = await window.api.patch(`/api/lancamentos/${lancamento.id}/pagar`);
      if (res && res.sucesso) {
        exibirSucesso(res.mensagem);
        // Atualiza item localmente para resposta instantânea
        setLancamentos(prev => prev.map(item => {
          if (item.id === lancamento.id) {
            return {
              ...item,
              status: res.dados.novo_status,
              vencido: res.dados.lancamento.vencido,
            };
          }
          return item;
        }));
        carregarMetadados();
      } else {
        setErro((res && res.erro) || 'Erro ao alternar status.');
      }
    } catch (err) {
      setErro(err.message || 'Erro ao alternar status do lançamento.');
    }
  };

  // Exclusão Lógica (Soft Delete)
  const handleConfirmarExcluir = (lancamento) => {
    setLancamentoParaExcluir(lancamento);
    setModalExcluirAberto(true);
  };

  const executarExclusao = async () => {
    if (!lancamentoParaExcluir) return;
    setExcluindo(true);
    try {
      const res = await window.api.delete(`/api/lancamentos/${lancamentoParaExcluir.id}`);
      if (res && res.sucesso) {
        exibirSucesso(res.mensagem || 'Lançamento excluído.');
        setModalExcluirAberto(false);
        setLancamentoParaExcluir(null);
        carregarLancamentos();
        carregarMetadados();
      } else {
        setErro((res && res.erro) || 'Erro ao excluir lançamento.');
      }
    } catch (err) {
      setErro(err.message || 'Erro ao excluir lançamento.');
    } finally {
      setExcluindo(false);
    }
  };

  // Formatação de datas
  const formatarData = (dataIso) => {
    if (!dataIso) return '-';
    const partes = dataIso.split('-');
    if (partes.length === 3) {
      return `${partes[2]}/${partes[1]}/${partes[0]}`;
    }
    return dataIso;
  };

  // Categorias válidas para a aba selecionada no modal
  const categoriasDoTipo = categorias.filter(c => c.tipo === abaModal && c.status === 'ativo');
  const contasAtivas = contas.filter(c => c.status === 'ativo');

  return (
    <div className="module-container">
      {/* Cabeçalho do Módulo */}
      <div className="module-header">
        <div>
          <h2 className="module-title">Lançamentos</h2>
          <p className="module-subtitle">Controle suas receitas, despesas e transferências com facilidade.</p>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          <button
            type="button"
            className="btn btn-primary"
            onClick={() => abrirModalCriacao('despesa')}
          >
            + Novo Lançamento
          </button>
        </div>
      </div>

      {mensagemSucesso && (
        <div className="alert alert-success" style={{ marginBottom: '1.25rem' }}>
          {mensagemSucesso}
        </div>
      )}

      {erro && (
        <div className="alert alert-error" style={{ marginBottom: '1.25rem' }}>
          {erro}
        </div>
      )}

      {/* Cartões de Resumo do Período */}
      <div className="lancamentos-summary-cards">
        <div className="lancamentos-summary-card">
          <span className="summary-card-label">Receitas</span>
          <span className="summary-card-value valor-receita">
            + {formatarMoeda(resumo.total_receitas)}
          </span>
          <span className="summary-card-meta">Entradas do mês</span>
        </div>

        <div className="lancamentos-summary-card">
          <span className="summary-card-label">Despesas</span>
          <span className="summary-card-value valor-despesa">
            - {formatarMoeda(resumo.total_despesas)}
          </span>
          <span className="summary-card-meta">Saídas do mês</span>
        </div>

        <div className="lancamentos-summary-card">
          <span className="summary-card-label">Saldo do Período</span>
          <span className={`summary-card-value ${resumo.saldo_periodo >= 0 ? 'valor-receita' : 'valor-despesa'}`}>
            {formatarMoeda(resumo.saldo_periodo)}
          </span>
          <span className="summary-card-meta">
            {resumo.saldo_periodo >= 0 ? 'Resultado positivo' : 'Atenção ao déficit'}
          </span>
        </div>

        <div className="lancamentos-summary-card">
          <span className="summary-card-label">Pendências</span>
          <span className="summary-card-value" style={{ color: resumo.total_vencidos > 0 ? 'var(--error)' : 'var(--text-primary)' }}>
            {resumo.total_pendentes} {resumo.total_pendentes === 1 ? 'conta' : 'contas'}
          </span>
          <span className="summary-card-meta">
            {resumo.total_vencidos > 0 ? (
              <strong style={{ color: 'var(--error)' }}>⚠️ {resumo.total_vencidos} em atraso</strong>
            ) : (
              'Em dia com os prazos'
            )}
          </span>
        </div>
      </div>

      {/* Barra de Filtros e Navegação de Mês */}
      <div className="lancamentos-toolbar">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem' }}>
          {/* Navegador de Período */}
          <div className="periodo-nav">
            <button
              type="button"
              className="periodo-btn"
              onClick={() => navegarPeriodo(-1)}
              title="Mês anterior"
            >
              ‹
            </button>
            <span className="periodo-texto">
              {nomesMeses[mes - 1]} de {ano}
            </span>
            <button
              type="button"
              className="periodo-btn"
              onClick={() => navegarPeriodo(1)}
              title="Próximo mês"
            >
              ›
            </button>
          </div>

          <button
            type="button"
            className="btn btn-ghost btn-sm"
            onClick={() => navegarPeriodo(0)}
          >
            📅 Ir para o mês atual
          </button>
        </div>

        {/* Linha de Filtros Dropdown e Busca */}
        <div className="lancamentos-filters-row">
          {/* Busca textual */}
          <div className="lancamentos-search-box">
            <span className="lancamentos-search-icon">🔍</span>
            <input
              type="text"
              className="form-input lancamentos-search-input"
              placeholder="Buscar pela descrição..."
              value={termoBusca}
              onChange={(e) => setTermoBusca(e.target.value)}
            />
          </div>

          {/* Filtro de Tipo */}
          <select
            className="form-select"
            value={filtroTipo}
            onChange={(e) => setFiltroTipo(e.target.value)}
          >
            <option value="todos">Todos os tipos</option>
            <option value="receita">Receitas</option>
            <option value="despesa">Despesas</option>
            <option value="transferencia">Transferências</option>
          </select>

          {/* Filtro de Status */}
          <select
            className="form-select"
            value={filtroStatus}
            onChange={(e) => setFiltroStatus(e.target.value)}
          >
            <option value="todos">Todos os status</option>
            <option value="pago">Apenas pagos</option>
            <option value="pendente">Apenas pendentes</option>
          </select>

          {/* Filtro de Conta */}
          <select
            className="form-select"
            value={filtroConta}
            onChange={(e) => setFiltroConta(e.target.value)}
          >
            <option value="">Todas as contas</option>
            {contas.map(c => (
              <option key={c.id} value={c.id}>
                {c.nome} {c.status === 'arquivado' ? '(Arquivada)' : ''}
              </option>
            ))}
          </select>

          {/* Filtro de Categoria */}
          <select
            className="form-select"
            value={filtroCategoria}
            onChange={(e) => setFiltroCategoria(e.target.value)}
          >
            <option value="">Todas as categorias</option>
            {categorias.map(c => (
              <option key={c.id} value={c.id}>
                {c.nome} ({c.tipo})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Listagem de Lançamentos */}
      {carregando ? (
        <div className="empty-state">
          <p className="empty-subtitle">Carregando movimentações financeiras...</p>
        </div>
      ) : lancamentos.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">💳</div>
          <p className="empty-title">Nenhum lançamento encontrado</p>
          <p className="empty-subtitle">
            {termoBusca || filtroTipo !== 'todos' || filtroStatus !== 'todos' || filtroConta || filtroCategoria
              ? 'Tente ajustar os filtros ou termo de busca aplicados.'
              : `Você não possui lançamentos registrados para ${nomesMeses[mes - 1]} de ${ano}.`}
          </p>
          <button
            type="button"
            className="btn btn-primary"
            style={{ marginTop: '1rem' }}
            onClick={() => abrirModalCriacao('despesa')}
          >
            + Adicionar Lançamento
          </button>
        </div>
      ) : (
        <div className="table-responsive">
          <table className="lancamentos-table">
            <thead>
              <tr>
                <th style={{ width: '100px' }}>Data</th>
                <th>Descrição</th>
                <th>Categoria</th>
                <th>Conta / Carteira</th>
                <th>Pagamento</th>
                <th style={{ textAlign: 'right' }}>Valor</th>
                <th style={{ textAlign: 'center', width: '110px' }}>Status</th>
                <th style={{ textAlign: 'center', width: '120px' }}>Ações</th>
              </tr>
            </thead>
            <tbody>
              {lancamentos.map((item) => {
                const isReceita = item.tipo === 'receita';
                const isDespesa = item.tipo === 'despesa';
                const isTransf = item.tipo === 'transferencia';

                return (
                  <tr key={item.id}>
                    <td data-label="Data">
                      <div style={{ fontWeight: 600 }}>{formatarData(item.data_competencia)}</div>
                      {item.data_vencimento && item.data_vencimento !== item.data_competencia && (
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                          Venc: {formatarData(item.data_vencimento)}
                        </div>
                      )}
                    </td>

                    <td data-label="Descrição">
                      <div style={{ display: 'flex', alignItems: 'center' }}>
                        <span className={`tipo-badge tipo-badge-${item.tipo}`} title={item.tipo}>
                          {isReceita && '↓'}
                          {isDespesa && '↑'}
                          {isTransf && '⇄'}
                        </span>
                        <div>
                          <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                            {item.descricao}
                          </span>
                          {item.observacao && (
                            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                              {item.observacao}
                            </div>
                          )}
                        </div>
                      </div>
                    </td>

                    <td data-label="Categoria">
                      {isTransf ? (
                        <span style={{ color: 'var(--text-muted)', fontSize: '0.8125rem' }}>
                          Transferência
                        </span>
                      ) : (
                        <span style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>
                          {item.categoria_nome || 'Sem categoria'}
                        </span>
                      )}
                    </td>

                    <td data-label="Conta">
                      <span style={{ fontSize: '0.8125rem', fontWeight: 500 }}>
                        {isTransf ? (
                          <>
                            {item.conta_nome} <span style={{ color: 'var(--primary)' }}>→</span> {item.conta_destino_nome}
                          </>
                        ) : (
                          item.conta_nome || '-'
                        )}
                      </span>
                    </td>

                    <td data-label="Pagamento">
                      <span style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>
                        {item.forma_pagamento || '-'}
                      </span>
                    </td>

                    <td data-label="Valor" style={{ textAlign: 'right' }}>
                      <span
                        className={
                          isReceita
                            ? 'valor-receita'
                            : isDespesa
                            ? 'valor-despesa'
                            : 'valor-transferencia'
                        }
                      >
                        {isReceita && '+ '}
                        {isDespesa && '- '}
                        {formatarMoeda(item.valor)}
                      </span>
                    </td>

                    <td data-label="Status" style={{ textAlign: 'center' }}>
                      {item.status === 'pago' ? (
                        <span
                          className="badge-status badge-status-pago"
                          onClick={() => handleAlternarStatus(item)}
                          title="Clique para reabrir como pendente"
                        >
                          ✓ Pago
                        </span>
                      ) : item.vencido ? (
                        <span
                          className="badge-status badge-status-vencido"
                          onClick={() => handleAlternarStatus(item)}
                          title="Conta em atraso! Clique para marcar como paga"
                        >
                          ⚠️ Vencida
                        </span>
                      ) : (
                        <span
                          className="badge-status badge-status-pendente"
                          onClick={() => handleAlternarStatus(item)}
                          title="Pendente. Clique para marcar como paga"
                        >
                          ⏳ Pendente
                        </span>
                      )}
                    </td>

                    <td data-label="Ações" style={{ textAlign: 'center' }}>
                      <div style={{ display: 'inline-flex', gap: '0.25rem' }}>
                        <button
                          type="button"
                          className="btn btn-ghost btn-sm"
                          onClick={() => abrirModalEdicao(item)}
                          title="Editar lançamento"
                        >
                          ✏️
                        </button>
                        <button
                          type="button"
                          className="btn btn-ghost btn-sm btn-danger"
                          onClick={() => handleConfirmarExcluir(item)}
                          title="Excluir lançamento"
                        >
                          🗑️
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Modal de Criação / Edição de Lançamento */}
      {modalAberto && (
        <Modal
          titulo={
            lancamentoEmEdicao
              ? `Editar Lançamento: ${lancamentoEmEdicao.descricao}`
              : 'Novo Lançamento'
          }
          onFechar={fecharModal}
        >
          {/* Abas no topo (apenas quando criando novo lançamento) */}
          {!lancamentoEmEdicao && (
            <div className="modal-tabs">
              <button
                type="button"
                className={`modal-tab-btn tab-despesa ${abaModal === 'despesa' ? 'active' : ''}`}
                onClick={() => mudarAbaModal('despesa')}
              >
                ↑ Despesa
              </button>
              <button
                type="button"
                className={`modal-tab-btn tab-receita ${abaModal === 'receita' ? 'active' : ''}`}
                onClick={() => mudarAbaModal('receita')}
              >
                ↓ Receita
              </button>
              <button
                type="button"
                className={`modal-tab-btn tab-transferencia ${abaModal === 'transferencia' ? 'active' : ''}`}
                onClick={() => mudarAbaModal('transferencia')}
              >
                ⇄ Transferência
              </button>
            </div>
          )}

          <form onSubmit={handleSalvar}>
            {erroModal && <div className="alert alert-error">{erroModal}</div>}

            {/* Aviso Preventivo de Saldo Insuficiente na Transferência */}
            {avisoSaldoInsuficiente && (
              <div className="modal-warning-box">
                <div className="modal-warning-title">
                  ⚠️ Saldo Insuficiente na Origem
                </div>
                <p style={{ margin: '0 0 0.75rem 0' }}>{avisoSaldoInsuficiente}</p>
                <button
                  type="button"
                  className="btn btn-primary btn-sm btn-danger"
                  onClick={() => handleSalvar(null, true)}
                  disabled={salvando}
                >
                  Confirmar e Transferir Mesmo Assim
                </button>
              </div>
            )}

            {/* Campo Monetário com Prefixo R$ e Steppers de R$ 1,00 */}
            <div className="form-group">
              <label className="form-label" htmlFor="lanc-valor">
                Valor (R$)
              </label>
              <div className="input-moeda-wrapper">
                <span className="input-moeda-prefixo">R$</span>
                <input
                  id="lanc-valor"
                  type="text"
                  required
                  inputMode="numeric"
                  className="form-input input-moeda-field"
                  placeholder="0,00"
                  value={formValor}
                  onChange={handleValorChange}
                  disabled={salvando}
                  autoFocus
                />
                <div className="input-moeda-steppers">
                  <button
                    type="button"
                    className="input-moeda-stepper-btn"
                    onClick={() => ajustarValorStepper(1)}
                    disabled={salvando}
                    title="Aumentar R$ 1,00"
                  >
                    ▲
                  </button>
                  <button
                    type="button"
                    className="input-moeda-stepper-btn"
                    onClick={() => ajustarValorStepper(-1)}
                    disabled={salvando}
                    title="Diminuir R$ 1,00"
                  >
                    ▼
                  </button>
                </div>
              </div>
            </div>

            {/* Campos Específicos para Transferência */}
            {abaModal === 'transferencia' ? (
              <>
                <div className="form-group">
                  <label className="form-label" htmlFor="transf-origem">
                    Conta de Origem (Debitar)
                  </label>
                  <select
                    id="transf-origem"
                    className="form-select"
                    value={formContaId}
                    onChange={(e) => setFormContaId(e.target.value)}
                    disabled={salvando}
                    required
                  >
                    <option value="">Selecione a conta de saída...</option>
                    {contasAtivas.map(c => (
                      <option key={c.id} value={c.id}>
                        {c.nome} (Saldo atual: {formatarMoeda(c.saldo_atual)})
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label" htmlFor="transf-destino">
                    Conta de Destino (Creditar)
                  </label>
                  <select
                    id="transf-destino"
                    className="form-select"
                    value={formContaDestinoId}
                    onChange={(e) => setFormContaDestinoId(e.target.value)}
                    disabled={salvando}
                    required
                  >
                    <option value="">Selecione a conta de entrada...</option>
                    {contasAtivas.map(c => (
                      <option key={c.id} value={c.id} disabled={Number(c.id) === Number(formContaId)}>
                        {c.nome} {Number(c.id) === Number(formContaId) ? '(Mesma conta)' : `(Saldo: ${formatarMoeda(c.saldo_atual)})`}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label" htmlFor="transf-data">
                    Data da Transferência
                  </label>
                  <input
                    id="transf-data"
                    type="date"
                    required
                    className="form-input"
                    value={formDataCompetencia}
                    onChange={(e) => setFormDataCompetencia(e.target.value)}
                    disabled={salvando}
                  />
                </div>

                <div className="form-group">
                  <label className="form-label" htmlFor="transf-desc">
                    Descrição (Opcional)
                  </label>
                  <input
                    id="transf-desc"
                    type="text"
                    maxLength={200}
                    className="form-input"
                    placeholder="Ex: Transferência para reserva"
                    value={formDescricao}
                    onChange={(e) => setFormDescricao(e.target.value)}
                    disabled={salvando}
                  />
                </div>
              </>
            ) : (
              /* Campos para Receita e Despesa */
              <>
                <div className="form-group">
                  <label className="form-label" htmlFor="lanc-descricao">
                    Descrição
                  </label>
                  <input
                    id="lanc-descricao"
                    type="text"
                    required
                    maxLength={200}
                    className="form-input"
                    placeholder={abaModal === 'despesa' ? 'Ex: Supermercado, Aluguel...' : 'Ex: Salário, Rendimentos...'}
                    value={formDescricao}
                    onChange={(e) => setFormDescricao(e.target.value)}
                    disabled={salvando}
                  />
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                  <div className="form-group">
                    <label className="form-label" htmlFor="lanc-comp">
                      Data Competência
                    </label>
                    <input
                      id="lanc-comp"
                      type="date"
                      required
                      className="form-input"
                      value={formDataCompetencia}
                      onChange={(e) => {
                        setFormDataCompetencia(e.target.value);
                        if (!formDataVencimento || formDataVencimento === formDataCompetencia) {
                          setFormDataVencimento(e.target.value);
                        }
                      }}
                      disabled={salvando}
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label" htmlFor="lanc-venc">
                      Data Vencimento
                    </label>
                    <input
                      id="lanc-venc"
                      type="date"
                      required
                      className="form-input"
                      value={formDataVencimento}
                      onChange={(e) => setFormDataVencimento(e.target.value)}
                      disabled={salvando}
                    />
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                  <div className="form-group">
                    <label className="form-label" htmlFor="lanc-categoria">
                      Categoria
                    </label>
                    <select
                      id="lanc-categoria"
                      className="form-select"
                      value={formCategoriaId}
                      onChange={(e) => setFormCategoriaId(e.target.value)}
                      disabled={salvando}
                      required
                    >
                      <option value="">Selecione...</option>
                      {categoriasDoTipo.map(c => (
                        <option key={c.id} value={c.id}>
                          {c.nome}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="form-group">
                    <label className="form-label" htmlFor="lanc-conta">
                      Conta / Carteira
                    </label>
                    <select
                      id="lanc-conta"
                      className="form-select"
                      value={formContaId}
                      onChange={(e) => setFormContaId(e.target.value)}
                      disabled={salvando}
                      required
                    >
                      <option value="">Selecione...</option>
                      {contasAtivas.map(c => (
                        <option key={c.id} value={c.id}>
                          {c.nome}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                  <div className="form-group">
                    <label className="form-label" htmlFor="lanc-forma">
                      Forma de Pagamento
                    </label>
                    <select
                      id="lanc-forma"
                      className="form-select"
                      value={formFormaPagamento}
                      onChange={(e) => setFormFormaPagamento(e.target.value)}
                      disabled={salvando}
                    >
                      <option value="Dinheiro">Dinheiro</option>
                      <option value="PIX">PIX</option>
                      <option value="Cartão de Débito">Cartão de Débito</option>
                      <option value="Cartão de Crédito">Cartão de Crédito</option>
                      <option value="Boleto">Boleto</option>
                      <option value="Transferência">Transferência</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label className="form-label" htmlFor="lanc-status">
                      Situação / Liquidação
                    </label>
                    <select
                      id="lanc-status"
                      className="form-select"
                      value={formStatus}
                      onChange={(e) => setFormStatus(e.target.value)}
                      disabled={salvando}
                    >
                      <option value="pago">✓ Já foi pago / liquidado</option>
                      <option value="pendente">⏳ Pendente (em aberto)</option>
                    </select>
                  </div>
                </div>
              </>
            )}

            <div className="form-group">
              <label className="form-label" htmlFor="lanc-obs">
                Observações (Opcional)
              </label>
              <textarea
                id="lanc-obs"
                className="form-input"
                rows={2}
                placeholder="Anotações adicionais sobre esta movimentação..."
                value={formObservacao}
                onChange={(e) => setFormObservacao(e.target.value)}
                disabled={salvando}
              />
            </div>

            <div className="modal-footer">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={fecharModal}
                disabled={salvando}
              >
                Cancelar
              </button>
              <button
                type="submit"
                className="btn btn-primary"
                disabled={salvando}
              >
                {salvando
                  ? 'Salvando...'
                  : lancamentoEmEdicao
                  ? 'Salvar Alterações'
                  : abaModal === 'transferencia'
                  ? 'Confirmar Transferência'
                  : 'Salvar Lançamento'}
              </button>
            </div>
          </form>
        </Modal>
      )}

      {/* Modal de Confirmação de Exclusão (Soft Delete) */}
      {modalExcluirAberto && lancamentoParaExcluir && (
        <Modal
          titulo="Confirmar Exclusão de Lançamento"
          onFechar={() => setModalExcluirAberto(false)}
        >
          <div className="modal-warning-box">
            <div className="modal-warning-title">
              ⚠️ Exclusão de Lançamento
            </div>
            <p style={{ margin: '0 0 0.5rem 0' }}>
              Tem certeza de que deseja excluir o lançamento{' '}
              <strong>"{lancamentoParaExcluir.descricao}"</strong> no valor de{' '}
              <strong style={{ color: 'var(--text-primary)' }}>
                {formatarMoeda(lancamentoParaExcluir.valor)}
              </strong>?
            </p>
            <p style={{ margin: 0, fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>
              O impacto financeiro será revertido imediatamente e o saldo das contas envolvidas será recalculado.
            </p>
          </div>

          <div className="modal-footer">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => setModalExcluirAberto(false)}
              disabled={excluindo}
            >
              Cancelar
            </button>
            <button
              type="button"
              className="btn btn-primary btn-danger"
              onClick={executarExclusao}
              disabled={excluindo}
            >
              {excluindo ? 'Excluindo...' : 'Sim, Excluir Lançamento'}
            </button>
          </div>
        </Modal>
      )}
    </div>
  );
}

// ==============================================================================
// Componente: Tela de Categorias e Orçamentos (Fase 7)
// ==============================================================================
function TelaCategorias() {
  const [categorias, setCategorias] = React.useState([]);
  const [abaAtiva, setAbaAtiva] = React.useState('despesa'); // 'despesa' ou 'receita'
  const [carregando, setCarregando] = React.useState(true);
  const [erro, setErro] = React.useState('');
  const [mensagemSucesso, setMensagemSucesso] = React.useState('');

  // Estados do Modal de Criação / Edição
  const [modalAberto, setModalAberto] = React.useState(false);
  const [categoriaEmEdicao, setCategoriaEmEdicao] = React.useState(null);
  const [formNome, setFormNome] = React.useState('');
  const [formTipo, setFormTipo] = React.useState('despesa');
  const [formTeto, setFormTeto] = React.useState('');
  const [salvando, setSalvando] = React.useState(false);
  const [erroModal, setErroModal] = React.useState('');

  // Estados do Modal de Reatribuição em Lote ao Excluir
  const [modalReatribuicaoAberto, setModalReatribuicaoAberto] = React.useState(false);
  const [categoriaParaExcluir, setCategoriaParaExcluir] = React.useState(null);
  const [infoReatribuicao, setInfoReatribuicao] = React.useState(null);
  const [novaCategoriaId, setNovaCategoriaId] = React.useState('');
  const [processandoReatribuicao, setProcessandoReatribuicao] = React.useState(false);
  const [erroReatribuicao, setErroReatribuicao] = React.useState('');

  const carregarCategorias = async () => {
    setCarregando(true);
    setErro('');
    try {
      const res = await window.api.get('/api/categorias');
      if (res && res.sucesso) {
        setCategorias(res.dados.categorias || []);
      } else {
        setErro((res && res.erro) || 'Erro ao carregar categorias.');
      }
    } catch (err) {
      setErro(err.message || 'Erro de comunicação ao carregar categorias.');
    } finally {
      setCarregando(false);
    }
  };

  React.useEffect(() => {
    carregarCategorias();
  }, []);

  const exibirSucesso = (msg) => {
    setMensagemSucesso(msg);
    setTimeout(() => setMensagemSucesso(''), 4000);
  };

  const formatarMoedaInput = (valorNumerico) => {
    if (valorNumerico === null || valorNumerico === undefined || isNaN(valorNumerico)) return '';
    return Number(valorNumerico).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  };

  const abrirModalNova = (tipoInicial) => {
    setCategoriaEmEdicao(null);
    setFormNome('');
    setFormTipo(tipoInicial || abaAtiva);
    setFormTeto('');
    setErroModal('');
    setModalAberto(true);
  };

  const abrirModalEditar = (cat) => {
    setCategoriaEmEdicao(cat);
    setFormNome(cat.nome);
    setFormTipo(cat.tipo);
    setFormTeto(cat.teto_orcamento !== null ? formatarMoedaInput(cat.teto_orcamento) : '');
    setErroModal('');
    setModalAberto(true);
  };

  const fecharModal = () => {
    setModalAberto(false);
    setCategoriaEmEdicao(null);
    setErroModal('');
  };

  const fecharModalReatribuicao = () => {
    setModalReatribuicaoAberto(false);
    setCategoriaParaExcluir(null);
    setInfoReatribuicao(null);
    setNovaCategoriaId('');
    setErroReatribuicao('');
  };

  const handleTetoChange = (e) => {
    const digits = e.target.value.replace(/\D/g, '');
    if (!digits) {
      setFormTeto('');
      return;
    }
    const centavos = parseInt(digits, 10);
    const reais = centavos / 100;
    setFormTeto(formatarMoedaInput(reais));
  };

  const handleStepTeto = (deltaReais) => {
    let valorAtual = 0;
    if (formTeto) {
      const limpo = formTeto.replace(/\./g, '').replace(',', '.');
      valorAtual = parseFloat(limpo) || 0;
    }
    const novoValor = Math.max(0, valorAtual + deltaReais);
    setFormTeto(formatarMoedaInput(novoValor));
  };

  const handleSalvar = async (e) => {
    e.preventDefault();
    setErroModal('');
    const nome = formNome.trim();
    if (!nome) {
      setErroModal('O nome da categoria é obrigatório.');
      return;
    }

    let tetoNum = null;
    if (formTipo === 'despesa' && formTeto) {
      const limpo = formTeto.replace(/\./g, '').replace(',', '.');
      tetoNum = parseFloat(limpo);
      if (isNaN(tetoNum) || tetoNum < 0) {
        setErroModal('O teto orçamentário deve ser um número válido e maior ou igual a zero.');
        return;
      }
    }

    setSalvando(true);
    try {
      if (categoriaEmEdicao) {
        const payload = { nome };
        if (formTipo === 'despesa') {
          payload.teto_orcamento = tetoNum;
        }
        const res = await window.api.put(`/api/categorias/${categoriaEmEdicao.id}`, payload);
        if (res && res.sucesso) {
          exibirSucesso(res.mensagem || 'Categoria atualizada com sucesso.');
          fecharModal();
          carregarCategorias();
        } else {
          setErroModal((res && res.erro) || 'Erro ao salvar alterações.');
        }
      } else {
        const payload = {
          nome,
          tipo: formTipo,
          teto_orcamento: tetoNum,
        };
        const res = await window.api.post('/api/categorias', payload);
        if (res && res.sucesso) {
          exibirSucesso(res.mensagem || 'Categoria criada com sucesso.');
          fecharModal();
          carregarCategorias();
        } else {
          setErroModal((res && res.erro) || 'Erro ao criar categoria.');
        }
      }
    } catch (err) {
      setErroModal(err.message || 'Erro inesperado ao salvar.');
    } finally {
      setSalvando(false);
    }
  };

  const handleArquivar = async (cat) => {
    if (!window.confirm(`Deseja arquivar a categoria "${cat.nome}"? Ela não aparecerá para novas seleções, mas o histórico existente continuará intacto.`)) return;
    try {
      const res = await window.api.patch(`/api/categorias/${cat.id}/arquivar`);
      if (res && res.sucesso) {
        exibirSucesso(res.mensagem || 'Categoria arquivada com sucesso.');
        carregarCategorias();
      } else {
        setErro((res && res.erro) || 'Erro ao arquivar categoria.');
      }
    } catch (err) {
      setErro(err.message || 'Erro de comunicação ao arquivar.');
    }
  };

  const handleReativar = async (cat) => {
    try {
      const res = await window.api.patch(`/api/categorias/${cat.id}/reativar`);
      if (res && res.sucesso) {
        exibirSucesso(res.mensagem || 'Categoria reativada com sucesso.');
        carregarCategorias();
      } else {
        setErro((res && res.erro) || 'Erro ao reativar categoria.');
      }
    } catch (err) {
      setErro(err.message || 'Erro de comunicação ao reativar.');
    }
  };

  const handleExcluir = async (cat) => {
    if (!window.confirm(`Tem certeza que deseja excluir a categoria "${cat.nome}"?`)) return;

    try {
      const res = await window.api.delete(`/api/categorias/${cat.id}`);
      if (res && res.sucesso) {
        exibirSucesso(res.mensagem || 'Categoria excluída com sucesso.');
        carregarCategorias();
      } else if (res && res.requer_reatribuicao) {
        setCategoriaParaExcluir(cat);
        setInfoReatribuicao(res);
        const candidatas = categorias.filter(c => c.id !== cat.id && c.tipo === cat.tipo && c.status === 'ativo');
        setNovaCategoriaId(candidatas.length > 0 ? String(candidatas[0].id) : '');
        setErroReatribuicao('');
        setModalReatribuicaoAberto(true);
      } else {
        setErro((res && res.erro) || 'Não foi possível excluir a categoria.');
      }
    } catch (err) {
      setErro(err.message || 'Erro de comunicação ao excluir.');
    }
  };

  const handleConfirmarReatribuicao = async (e) => {
    e.preventDefault();
    if (!novaCategoriaId) {
      setErroReatribuicao('Selecione uma categoria de destino válida.');
      return;
    }

    setProcessandoReatribuicao(true);
    setErroReatribuicao('');
    try {
      const res = await window.api.post(`/api/categorias/${categoriaParaExcluir.id}/reatribuir-excluir`, {
        nova_categoria_id: parseInt(novaCategoriaId, 10),
      });

      if (res && res.sucesso) {
        exibirSucesso(res.mensagem || 'Histórico transferido e categoria excluída com sucesso.');
        fecharModalReatribuicao();
        carregarCategorias();
      } else {
        setErroReatribuicao((res && res.erro) || 'Erro na reatribuição.');
      }
    } catch (err) {
      setErroReatribuicao(err.message || 'Erro de comunicação durante a reatribuição.');
    } finally {
      setProcessandoReatribuicao(false);
    }
  };

  // Filtra as categorias conforme a aba ativa
  const categoriasExibidas = categorias.filter(c => c.tipo === abaAtiva);
  const ativas = categoriasExibidas.filter(c => c.status === 'ativo');
  const arquivadas = categoriasExibidas.filter(c => c.status === 'arquivado');

  // Contagens para badges das abas
  const totalDespesas = categorias.filter(c => c.tipo === 'despesa').length;
  const totalReceitas = categorias.filter(c => c.tipo === 'receita').length;

  // Categorias válidas de destino para reatribuição
  const categoriasDestinoValidas = categoriaParaExcluir
    ? categorias.filter(c => c.id !== categoriaParaExcluir.id && c.tipo === categoriaParaExcluir.tipo && c.status === 'ativo')
    : [];

  return (
    <div className="module-container">
      {/* Cabeçalho do módulo */}
      <div className="module-header">
        <div>
          <h2 className="module-title">Categorias &amp; Tetos de Orçamento</h2>
          <p className="module-subtitle">Classifique suas receitas e despesas e monitore limites de gastos mensais.</p>
        </div>
        <button
          type="button"
          className="btn btn-primary"
          onClick={() => abrirModalNova(abaAtiva)}
        >
          + Nova Categoria
        </button>
      </div>

      {/* Alertas */}
      {mensagemSucesso && <div className="alert alert-success">{mensagemSucesso}</div>}
      {erro && (
        <div className="alert alert-error">
          {erro}
          <button className="alert-fechar" onClick={() => setErro('')}>✕</button>
        </div>
      )}

      {/* Navegação por Abas (Despesas / Receitas) */}
      <div className="tabs-nav">
        <button
          type="button"
          className={`tab-btn ${abaAtiva === 'despesa' ? 'active' : ''}`}
          onClick={() => setAbaAtiva('despesa')}
        >
          <span>📉 Despesas</span>
          <span className="tab-count">{totalDespesas}</span>
        </button>
        <button
          type="button"
          className={`tab-btn ${abaAtiva === 'receita' ? 'active' : ''}`}
          onClick={() => setAbaAtiva('receita')}
        >
          <span>📈 Receitas</span>
          <span className="tab-count">{totalReceitas}</span>
        </button>
      </div>

      {carregando ? (
        <div className="skeleton-list">
          {[1, 2, 3, 4].map(i => <div key={i} className="skeleton-card" />)}
        </div>
      ) : (
        <>
          {/* Seção de Categorias Ativas */}
          {ativas.length > 0 ? (
            <div className="section-block">
              <h3 className="section-title">Categorias Ativas ({ativas.length})</h3>
              <div className="cards-grid">
                {ativas.map(cat => {
                  const temTeto = cat.tipo === 'despesa' && cat.teto_orcamento !== null && cat.teto_orcamento > 0;
                  const porcentagem = cat.porcentagem_consumo || 0;
                  const tetoExcedido = cat.teto_excedido || porcentagem > 100;

                  let progressClass = 'progress-safe';
                  if (tetoExcedido) {
                    progressClass = 'progress-exceeded';
                  } else if (porcentagem >= 80) {
                    progressClass = 'progress-warning';
                  }

                  return (
                    <div key={cat.id} className="category-card">
                      <div>
                        <div className="category-card-header">
                          <div className="category-name-group">
                            <span className="category-icon-coin" title={cat.tipo === 'despesa' ? 'Categoria de Despesa' : 'Categoria de Receita'}>🪙</span>
                            <span className="category-name" title={cat.nome}>{cat.nome}</span>
                          </div>
                          <div style={{ display: 'flex', gap: '0.25rem', alignItems: 'center' }}>
                            {tetoExcedido && <span className="badge badge-exceeded">Teto Excedido</span>}
                            <span className="badge badge-active">Ativa</span>
                          </div>
                        </div>

                        {/* Bloco de Orçamento para Despesas */}
                        {cat.tipo === 'despesa' && (
                          temTeto ? (
                            <div className="budget-block">
                              <div className="budget-header">
                                <span className="budget-amounts">
                                  <strong>{formatarMoeda(cat.consumo_mes)}</strong>
                                  <span className="budget-meta"> de {formatarMoeda(cat.teto_orcamento)}</span>
                                </span>
                                <span
                                  className="budget-percent"
                                  style={{ color: tetoExcedido ? 'var(--error)' : 'var(--text-primary)' }}
                                >
                                  {porcentagem}%
                                </span>
                              </div>
                              <div className="progress-bar-bg" title={`${porcentagem}% do orçamento consumido este mês`}>
                                <div
                                  className={`progress-bar-fill ${progressClass}`}
                                  style={{ width: `${Math.min(porcentagem, 100)}%` }}
                                />
                              </div>
                            </div>
                          ) : (
                            <div className="no-budget-meta">Sem teto de gastos definido</div>
                          )
                        )}
                      </div>

                      <div className="account-actions" style={{ marginTop: '0.75rem' }}>
                        <button
                          type="button"
                          className="btn btn-ghost btn-sm"
                          onClick={() => abrirModalEditar(cat)}
                          title="Editar categoria ou teto"
                        >
                          ✏️ Editar
                        </button>
                        <button
                          type="button"
                          className="btn btn-ghost btn-sm"
                          onClick={() => handleArquivar(cat)}
                          title="Arquivar categoria"
                        >
                          📦 Arquivar
                        </button>
                        <button
                          type="button"
                          className="btn btn-ghost btn-sm btn-danger"
                          onClick={() => handleExcluir(cat)}
                          title="Excluir categoria"
                        >
                          🗑️ Excluir
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ) : (
            <div className="empty-state">
              <div className="empty-icon">🪙</div>
              <p className="empty-title">Nenhuma categoria de {abaAtiva} ativa</p>
              <p className="empty-subtitle">Cadastre uma categoria para organizar suas movimentações.</p>
              <button
                type="button"
                className="btn btn-primary"
                onClick={() => abrirModalNova(abaAtiva)}
              >
                + Criar Primeira Categoria de {abaAtiva === 'despesa' ? 'Despesa' : 'Receita'}
              </button>
            </div>
          )}

          {/* Seção de Categorias Arquivadas */}
          {arquivadas.length > 0 && (
            <div className="section-block section-archived">
              <h3 className="section-title">Categorias Arquivadas ({arquivadas.length})</h3>
              <div className="cards-grid">
                {arquivadas.map(cat => (
                  <div key={cat.id} className="category-card category-card-archived">
                    <div className="category-card-header">
                      <div className="category-name-group">
                        <span className="category-icon-coin" style={{ opacity: 0.6 }} title="Categoria Arquivada">🪙</span>
                        <span className="category-name" title={cat.nome}>{cat.nome}</span>
                      </div>
                      <span className="badge badge-archived">Arquivada</span>
                    </div>

                    <div className="account-actions">
                      <button
                        type="button"
                        className="btn btn-ghost btn-sm"
                        onClick={() => handleReativar(cat)}
                        title="Reativar categoria"
                      >
                        ♻️ Reativar
                      </button>
                      <button
                        type="button"
                        className="btn btn-ghost btn-sm btn-danger"
                        onClick={() => handleExcluir(cat)}
                        title="Excluir permanentemente"
                      >
                        🗑️ Excluir
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {/* Modal de Criação / Edição de Categoria */}
      {modalAberto && (
        <Modal
          titulo={categoriaEmEdicao ? `Editar Categoria: ${categoriaEmEdicao.nome}` : `Nova Categoria de ${formTipo === 'despesa' ? 'Despesa' : 'Receita'}`}
          onFechar={fecharModal}
        >
          <form onSubmit={handleSalvar}>
            {erroModal && <div className="alert alert-error">{erroModal}</div>}

            <div className="form-group">
              <label className="form-label" htmlFor="cat-nome">Nome da Categoria</label>
              <input
                id="cat-nome"
                type="text"
                required
                maxLength={100}
                className="form-input"
                placeholder="Ex: Alimentação, Lazer, Salário..."
                value={formNome}
                onChange={(e) => setFormNome(e.target.value)}
                disabled={salvando}
                autoFocus
              />
            </div>

            {!categoriaEmEdicao && (
              <div className="form-group">
                <label className="form-label" htmlFor="cat-tipo">Tipo</label>
                <select
                  id="cat-tipo"
                  className="form-select"
                  value={formTipo}
                  onChange={(e) => setFormTipo(e.target.value)}
                  disabled={salvando}
                >
                  <option value="despesa">Despesa (Saída)</option>
                  <option value="receita">Receita (Entrada)</option>
                </select>
              </div>
            )}

            {formTipo === 'despesa' && (
              <div className="form-group">
                <label className="form-label" htmlFor="cat-teto">Teto de Gastos Mensal — Opcional</label>
                <div className="input-moeda-wrapper">
                  <span className="input-moeda-prefixo">R$</span>
                  <input
                    id="cat-teto"
                    type="text"
                    inputMode="numeric"
                    className="form-input input-moeda-field"
                    placeholder="0,00"
                    value={formTeto}
                    onChange={handleTetoChange}
                    disabled={salvando}
                  />
                  <div className="input-moeda-steppers">
                    <button
                      type="button"
                      className="input-moeda-stepper-btn"
                      onClick={() => handleStepTeto(1)}
                      title="Aumentar R$ 1,00"
                      disabled={salvando}
                    >
                      ▲
                    </button>
                    <button
                      type="button"
                      className="input-moeda-stepper-btn"
                      onClick={() => handleStepTeto(-1)}
                      title="Diminuir R$ 1,00"
                      disabled={salvando}
                    >
                      ▼
                    </button>
                  </div>
                </div>
                <span className="form-helper">Defina um limite de gastos para receber alertas visuais no painel caso ultrapasse.</span>
              </div>
            )}

            <div className="modal-footer">
              <button type="button" className="btn btn-secondary" onClick={fecharModal} disabled={salvando}>
                Cancelar
              </button>
              <button type="submit" className="btn btn-primary" disabled={salvando}>
                {salvando ? 'Salvando...' : (categoriaEmEdicao ? 'Salvar Alterações' : 'Criar Categoria')}
              </button>
            </div>
          </form>
        </Modal>
      )}

      {/* Modal de Reatribuição em Lote ao Excluir com Histórico */}
      {modalReatribuicaoAberto && categoriaParaExcluir && (
        <Modal
          titulo={`Excluir Categoria: ${categoriaParaExcluir.nome}`}
          onFechar={fecharModalReatribuicao}
        >
          <form onSubmit={handleConfirmarReatribuicao}>
            {erroReatribuicao && <div className="alert alert-error">{erroReatribuicao}</div>}

            <div className="modal-warning-box">
              <div className="modal-warning-title">
                ⚠️ Categoria em uso no histórico
              </div>
              <p style={{ margin: '0 0 0.5rem 0' }}>
                A categoria <strong>"{categoriaParaExcluir.nome}"</strong> possui{' '}
                <strong>{infoReatribuicao?.total_lancamentos || 0} lançamento(s)</strong> e{' '}
                <strong>{infoReatribuicao?.total_recorrentes || 0} fixo(s)</strong> vinculados.
              </p>
              <p style={{ margin: 0 }}>
                Para evitar a quebra do seu histórico contábil, você pode transferir todo o histórico para outra categoria antes de excluí-la, ou simplesmente optar por arquivá-la.
              </p>
            </div>

            {categoriasDestinoValidas.length > 0 ? (
              <div className="form-group">
                <label className="form-label" htmlFor="cat-destino">
                  Transferir histórico para qual categoria de {categoriaParaExcluir.tipo}?
                </label>
                <select
                  id="cat-destino"
                  className="form-select"
                  value={novaCategoriaId}
                  onChange={(e) => setNovaCategoriaId(e.target.value)}
                  disabled={processandoReatribuicao}
                  required
                >
                  {categoriasDestinoValidas.map(c => (
                    <option key={c.id} value={c.id}>{c.nome}</option>
                  ))}
                </select>
                <span className="form-helper">
                  Todos os lançamentos passados e modelos recorrentes serão migrados para a categoria selecionada de forma atômica.
                </span>
              </div>
            ) : (
              <div className="alert alert-error">
                Você não possui outra categoria de {categoriaParaExcluir.tipo} ativa para onde transferir os lançamentos. Crie uma nova categoria ou utilize o arquivamento.
              </div>
            )}

            <div className="modal-footer">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => {
                  fecharModalReatribuicao();
                  handleArquivar(categoriaParaExcluir);
                }}
                disabled={processandoReatribuicao}
              >
                📦 Apenas Arquivar
              </button>
              {categoriasDestinoValidas.length > 0 && (
                <button
                  type="submit"
                  className="btn btn-primary btn-danger"
                  disabled={processandoReatribuicao || !novaCategoriaId}
                >
                  {processandoReatribuicao ? 'Transferindo e Excluindo...' : 'Reatribuir e Excluir'}
                </button>
              )}
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}

// ==============================================================================
// Componente: Tela de Lançamentos Recorrentes (Fase 9 - Fixos)
// ==============================================================================
function TelaRecorrentes() {
  const [recorrentes, setRecorrentes] = React.useState([]);
  const [contas, setContas] = React.useState([]);
  const [categorias, setCategorias] = React.useState([]);
  const [carregando, setCarregando] = React.useState(true);
  const [erro, setErro] = React.useState('');
  const [mensagemSucesso, setMensagemSucesso] = React.useState('');
  const [filtroTipo, setFiltroTipo] = React.useState('todos');
  const [filtroStatus, setFiltroStatus] = React.useState('todos');
  const [busca, setBusca] = React.useState('');

  // Estados do Modal de Criação / Edição
  const [modalAberto, setModalAberto] = React.useState(false);
  const [recorrenteEmEdicao, setRecorrenteEmEdicao] = React.useState(null);
  const [abaModal, setAbaModal] = React.useState('despesa'); // 'despesa' | 'receita'
  const [formDescricao, setFormDescricao] = React.useState('');
  const [formValor, setFormValor] = React.useState('0,00');
  const [formDiaVencimento, setFormDiaVencimento] = React.useState(10);
  const [formCategoriaId, setFormCategoriaId] = React.useState('');
  const [formContaId, setFormContaId] = React.useState('');
  const [formFormaPagamento, setFormFormaPagamento] = React.useState('PIX');
  const [formAtivo, setFormAtivo] = React.useState(true);
  const [salvando, setSalvando] = React.useState(false);
  const [erroModal, setErroModal] = React.useState('');

  // Modal de Exclusão
  const [modalExcluirAberto, setModalExcluirAberto] = React.useState(false);
  const [recorrenteParaExcluir, setRecorrenteParaExcluir] = React.useState(null);
  const [excluindo, setExcluindo] = React.useState(false);

  // Sincronização manual
  const [sincronizando, setSincronizando] = React.useState(false);

  const exibirSucesso = (msg) => {
    setMensagemSucesso(msg);
    setTimeout(() => setMensagemSucesso(''), 4000);
  };

  // Carrega dados iniciais
  const carregarDados = async () => {
    setCarregando(true);
    setErro('');
    try {
      const [resRecorrentes, resContas, resCategorias] = await Promise.all([
        window.api.get('/api/recorrentes'),
        window.api.get('/api/contas'),
        window.api.get('/api/categorias'),
      ]);

      if (resRecorrentes && resRecorrentes.sucesso) {
        setRecorrentes(resRecorrentes.dados.recorrentes);
      }
      if (resContas && resContas.sucesso) {
        setContas(resContas.dados.contas || []);
      }
      if (resCategorias && resCategorias.sucesso) {
        setCategorias(resCategorias.dados.categorias || []);
      }
    } catch (err) {
      setErro(err.message || 'Erro ao carregar dados dos lançamentos fixos.');
    } finally {
      setCarregando(false);
    }
  };

  React.useEffect(() => {
    carregarDados();
  }, []);

  // Formatação e steppers monetários
  const parseValorNumerico = (texto) => {
    if (!texto) return 0;
    const limpo = String(texto).replace(/\./g, '').replace(',', '.');
    const n = parseFloat(limpo);
    return isNaN(n) ? 0 : n;
  };

  const formatarValorString = (num) => {
    return Number(num || 0).toLocaleString('pt-BR', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  };

  const handleValorChange = (e) => {
    let digits = e.target.value.replace(/\D/g, '');
    if (!digits) {
      setFormValor('0,00');
      return;
    }
    const num = parseInt(digits, 10) / 100;
    setFormValor(formatarValorString(num));
  };

  const ajustarValorStepper = (delta) => {
    const atual = parseValorNumerico(formValor);
    const novo = Math.max(0, atual + delta);
    setFormValor(formatarValorString(novo));
  };

  const ajustarDiaStepper = (delta) => {
    setFormDiaVencimento((prev) => {
      const n = Number(prev) || 1;
      const novo = n + delta;
      if (novo < 1) return 1;
      if (novo > 31) return 31;
      return novo;
    });
  };

  // Abertura do modal de criação
  const abrirModalCriacao = (tipoInicial = 'despesa') => {
    setRecorrenteEmEdicao(null);
    setAbaModal(tipoInicial);
    setFormDescricao('');
    setFormValor('0,00');
    setFormDiaVencimento(10);
    setFormFormaPagamento('PIX');
    setFormAtivo(true);
    setErroModal('');

    const contasAtivas = contas.filter(c => c.status === 'ativo');
    if (contasAtivas.length > 0) {
      setFormContaId(contasAtivas[0].id);
    } else {
      setFormContaId('');
    }

    const catsDoTipo = categorias.filter(c => c.tipo === tipoInicial && c.status === 'ativo');
    if (catsDoTipo.length > 0) {
      setFormCategoriaId(catsDoTipo[0].id);
    } else {
      setFormCategoriaId('');
    }

    setModalAberto(true);
  };

  // Alterna aba no modal
  const mudarAbaModal = (novaAba) => {
    setAbaModal(novaAba);
    setErroModal('');
    const cats = categorias.filter(c => c.tipo === novaAba && c.status === 'ativo');
    if (cats.length > 0 && (!formCategoriaId || !cats.some(c => c.id === Number(formCategoriaId)))) {
      setFormCategoriaId(cats[0].id);
    }
  };

  // Abertura do modal de edição
  const abrirModalEdicao = (modelo) => {
    setRecorrenteEmEdicao(modelo);
    setAbaModal(modelo.tipo);
    setFormDescricao(modelo.descricao || '');
    setFormValor(formatarValorString(modelo.valor));
    setFormDiaVencimento(modelo.dia_vencimento || 10);
    setFormCategoriaId(modelo.categoria_id ? String(modelo.categoria_id) : '');
    setFormContaId(modelo.conta_id ? String(modelo.conta_id) : '');
    setFormFormaPagamento(modelo.forma_pagamento || 'PIX');
    setFormAtivo(modelo.ativo);
    setErroModal('');
    setModalAberto(true);
  };

  const fecharModal = () => {
    setModalAberto(false);
    setRecorrenteEmEdicao(null);
    setErroModal('');
  };

  // Salvar criação ou edição
  const handleSalvar = async (e) => {
    if (e && e.preventDefault) e.preventDefault();
    setErroModal('');
    setSalvando(true);

    const valorNumerico = parseValorNumerico(formValor);
    if (valorNumerico <= 0) {
      setErroModal('O valor deve ser estritamente maior que zero.');
      setSalvando(false);
      return;
    }

    if (!formDescricao.trim() || formDescricao.trim().length < 2) {
      setErroModal('A descrição deve ter entre 2 e 150 caracteres.');
      setSalvando(false);
      return;
    }

    const diaNum = Number(formDiaVencimento);
    if (isNaN(diaNum) || diaNum < 1 || diaNum > 31) {
      setErroModal('O dia de vencimento deve estar entre 1 e 31.');
      setSalvando(false);
      return;
    }

    if (!formCategoriaId) {
      setErroModal('Selecione uma categoria compatível.');
      setSalvando(false);
      return;
    }

    if (!formContaId) {
      setErroModal('Selecione a conta/carteira preferencial.');
      setSalvando(false);
      return;
    }

    const payload = {
      tipo: abaModal,
      descricao: formDescricao.trim(),
      valor: valorNumerico,
      dia_vencimento: diaNum,
      categoria_id: Number(formCategoriaId),
      conta_id: Number(formContaId),
      forma_pagamento: formFormaPagamento,
      ativo: Boolean(formAtivo),
    };

    try {
      let res;
      if (recorrenteEmEdicao) {
        res = await window.api.put(`/api/recorrentes/${recorrenteEmEdicao.id}`, payload);
      } else {
        res = await window.api.post('/api/recorrentes', payload);
      }

      if (res && res.sucesso) {
        exibirSucesso(res.mensagem || 'Lançamento recorrente salvo com sucesso.');
        fecharModal();
        carregarDados();
      } else {
        setErroModal((res && res.erro) || 'Não foi possível salvar o fixo recorrente.');
      }
    } catch (err) {
      setErroModal(err.message || 'Erro inesperado ao salvar.');
    } finally {
      setSalvando(false);
    }
  };

  // Alternar rapidamente status Ativo <-> Pausado
  const handleAlternarStatus = async (modelo) => {
    try {
      const res = await window.api.patch(`/api/recorrentes/${modelo.id}/toggle`);
      if (res && res.sucesso) {
        exibirSucesso(res.mensagem);
        setRecorrentes((prev) =>
          prev.map((item) =>
            item.id === modelo.id ? { ...item, ativo: res.dados.recorrente.ativo } : item
          )
        );
      } else {
        setErro((res && res.erro) || 'Erro ao alternar status do lançamento recorrente.');
      }
    } catch (err) {
      setErro(err.message || 'Erro ao alternar status.');
    }
  };

  // Abertura do modal de confirmação de exclusão
  const handleConfirmarExcluir = (modelo) => {
    setRecorrenteParaExcluir(modelo);
    setModalExcluirAberto(true);
  };

  const handleExcluir = async () => {
    if (!recorrenteParaExcluir) return;
    setExcluindo(true);
    try {
      const res = await window.api.delete(`/api/recorrentes/${recorrenteParaExcluir.id}`);
      if (res && res.sucesso) {
        exibirSucesso(res.mensagem || 'Lançamento recorrente excluído.');
        setModalExcluirAberto(false);
        setRecorrenteParaExcluir(null);
        carregarDados();
      } else {
        setErro((res && res.erro) || 'Erro ao excluir.');
      }
    } catch (err) {
      setErro(err.message || 'Erro ao excluir lançamento recorrente.');
    } finally {
      setExcluindo(false);
    }
  };

  // Sincronização manual transparente
  const handleSincronizarManual = async () => {
    setSincronizando(true);
    setErro('');
    try {
      const res = await window.api.post('/api/recorrentes/sincronizar');
      if (res && res.sucesso) {
        const total = res.dados.gerados_total;
        if (total > 0) {
          exibirSucesso(`Sincronização concluída: ${total} novo(s) lançamento(s) gerado(s) para este mês!`);
        } else {
          exibirSucesso('Todos os fixos ativos já estavam sincronizados para o ciclo vigente.');
        }
      }
    } catch (err) {
      setErro(err.message || 'Erro ao sincronizar fixos recorrentes.');
    } finally {
      setSincronizando(false);
    }
  };

  // Cálculos de resumo
  const totalDespesasFixas = recorrentes
    .filter((r) => r.ativo && r.tipo === 'despesa')
    .reduce((acc, r) => acc + (Number(r.valor) || 0), 0);

  const totalReceitasFixas = recorrentes
    .filter((r) => r.ativo && r.tipo === 'receita')
    .reduce((acc, r) => acc + (Number(r.valor) || 0), 0);

  const saldoProjetado = totalReceitasFixas - totalDespesasFixas;

  // Filtragem da lista
  const itensFiltrados = recorrentes.filter((item) => {
    if (filtroTipo !== 'todos' && item.tipo !== filtroTipo) return false;
    if (filtroStatus === 'ativos' && !item.ativo) return false;
    if (filtroStatus === 'pausados' && item.ativo) return false;
    if (busca.trim()) {
      const termo = busca.toLowerCase();
      const bateDesc = (item.descricao || '').toLowerCase().includes(termo);
      const bateCat = (item.categoria_nome || '').toLowerCase().includes(termo);
      const bateConta = (item.conta_nome || '').toLowerCase().includes(termo);
      if (!bateDesc && !bateCat && !bateConta) return false;
    }
    return true;
  });

  const categoriasDoTipo = categorias.filter(
    (c) => c.tipo === abaModal && c.status === 'ativo'
  );
  const contasAtivas = contas.filter((c) => c.status === 'ativo');

  return (
    <div className="module-container">
      {/* Cabeçalho do Módulo */}
      <div className="module-header">
        <div>
          <h2 className="module-title">Fixos Recorrentes</h2>
          <p className="module-subtitle">
            Automatize suas despesas e receitas mensais. Na virada do ciclo, lançamentos são gerados com status pendente.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={handleSincronizarManual}
            disabled={sincronizando || carregando}
            title="Verifica e gera lançamentos pendentes no mês atual"
          >
            {sincronizando ? 'Sincronizando...' : '🔁 Sincronizar Agora'}
          </button>
          <button
            type="button"
            className="btn btn-primary"
            onClick={() => abrirModalCriacao('despesa')}
          >
            + Novo Fixo
          </button>
        </div>
      </div>

      {mensagemSucesso && (
        <div className="alert alert-success" style={{ marginBottom: '1.25rem' }}>
          {mensagemSucesso}
        </div>
      )}

      {erro && (
        <div className="alert alert-error" style={{ marginBottom: '1.25rem' }}>
          {erro}
        </div>
      )}

      {/* Indicadores de Fixos Recorrentes */}
      <div className="recorrentes-kpi-grid">
        <div className="recorrentes-kpi-card">
          <span className="recorrentes-kpi-label">📉 Despesas Mensais Fixas</span>
          <span className="recorrentes-kpi-value despesa">
            {formatarMoeda(totalDespesasFixas)}
          </span>
        </div>

        <div className="recorrentes-kpi-card">
          <span className="recorrentes-kpi-label">📈 Entradas Mensais Fixas</span>
          <span className="recorrentes-kpi-value receita">
            {formatarMoeda(totalReceitasFixas)}
          </span>
        </div>

        <div className="recorrentes-kpi-card">
          <span className="recorrentes-kpi-label">Balanço Fixo Projetado</span>
          <span
            className={`recorrentes-kpi-value ${
              saldoProjetado > 0
                ? 'saldo-positivo'
                : saldoProjetado < 0
                ? 'saldo-negativo'
                : 'saldo-zero'
            }`}
          >
            {formatarMoeda(saldoProjetado)}
          </span>
        </div>
      </div>


      {/* Linha de Filtros e Busca */}
      <div className="lancamentos-filters-row" style={{ marginBottom: '1.25rem' }}>
        <div className="lancamentos-search-box">
          <span className="lancamentos-search-icon">🔍</span>
          <input
            type="text"
            className="form-input lancamentos-search-input"
            placeholder="Buscar por descrição, categoria ou conta..."
            value={busca}
            onChange={(e) => setBusca(e.target.value)}
          />
        </div>

        <select
          className="form-select"
          value={filtroTipo}
          onChange={(e) => setFiltroTipo(e.target.value)}
        >
          <option value="todos">Todos os tipos</option>
          <option value="despesa">Apenas Despesas</option>
          <option value="receita">Apenas Receitas</option>
        </select>

        <select
          className="form-select"
          value={filtroStatus}
          onChange={(e) => setFiltroStatus(e.target.value)}
        >
          <option value="todos">Todos os status</option>
          <option value="ativos">Apenas Ativos</option>
          <option value="pausados">Apenas Pausados</option>
        </select>
      </div>

      {/* Listagem em Cards de Fixos */}
      {carregando ? (
        <div className="empty-state">
          <p className="empty-title">Carregando fixos recorrentes...</p>
        </div>
      ) : itensFiltrados.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">🔁</div>
          <p className="empty-title">Nenhum lançamento fixo encontrado</p>
          <p className="empty-subtitle">
            Cadastre aluguel, luz, internet, assinaturas ou salários para automatizar a geração de lançamentos a cada mês.
          </p>
          <button
            type="button"
            className="btn btn-primary"
            style={{ marginTop: '1rem' }}
            onClick={() => abrirModalCriacao('despesa')}
          >
            + Criar Primeiro Fixo
          </button>
        </div>
      ) : (
        <div className="recorrentes-grid">
          {itensFiltrados.map((item) => {
            const isReceita = item.tipo === 'receita';
            return (
              <div
                key={item.id}
                className={`recorrente-card ${!item.ativo ? 'pausado' : ''}`}
              >
                <div>
                  <div className="recorrente-card-header">
                    <div>
                      <div className="recorrente-card-title">{item.descricao}</div>
                      <div className="recorrente-card-meta">
                        <span className={`recorrente-tipo-badge tipo-${item.tipo}`}>
                          {isReceita ? '↓ Receita' : '↑ Despesa'}
                        </span>
                        <span>•</span>
                        <span>{item.categoria_nome || 'Sem categoria'}</span>
                      </div>
                    </div>
                    <span className="recorrente-dia-badge">
                      📅 Dia {item.dia_vencimento}
                    </span>
                  </div>

                  <div style={{ marginTop: '0.85rem' }}>
                    <div className={`recorrente-card-valor ${item.tipo}`}>
                      {isReceita ? '+' : '-'} {formatarMoeda(item.valor)}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                      Conta: <strong>{item.conta_nome || '-'}</strong> • Via {item.forma_pagamento || 'PIX'}
                    </div>
                  </div>
                </div>

                <div className="recorrente-card-footer">
                  <button
                    type="button"
                    className={`toggle-switch-btn ${item.ativo ? 'ativo' : 'pausado'}`}
                    onClick={() => handleAlternarStatus(item)}
                    title={item.ativo ? 'Clique para pausar geração' : 'Clique para ativar geração'}
                  >
                    <span>{item.ativo ? '●' : '○'}</span>
                    <span>{item.ativo ? 'Ativo' : 'Pausado'}</span>
                  </button>

                  <div style={{ display: 'flex', gap: '0.25rem' }}>
                    <button
                      type="button"
                      className="btn btn-ghost btn-sm"
                      onClick={() => abrirModalEdicao(item)}
                      title="Editar parâmetros do fixo"
                    >
                      ✏️
                    </button>
                    <button
                      type="button"
                      className="btn btn-ghost btn-sm btn-danger"
                      onClick={() => handleConfirmarExcluir(item)}
                      title="Excluir fixo recorrente"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Modal de Criação / Edição de Fixo Recorrente */}
      {modalAberto && (
        <Modal
          titulo={
            recorrenteEmEdicao
              ? `Editar Fixo: ${recorrenteEmEdicao.descricao}`
              : 'Novo Lançamento Fixo (Recorrente)'
          }
          onFechar={fecharModal}
        >
          {/* Abas no topo (apenas ao criar novo) */}
          {!recorrenteEmEdicao && (
            <div className="modal-tabs">
              <button
                type="button"
                className={`modal-tab-btn tab-despesa ${abaModal === 'despesa' ? 'active' : ''}`}
                onClick={() => mudarAbaModal('despesa')}
              >
                ↑ Despesa Fixa
              </button>
              <button
                type="button"
                className={`modal-tab-btn tab-receita ${abaModal === 'receita' ? 'active' : ''}`}
                onClick={() => mudarAbaModal('receita')}
              >
                ↓ Receita Fixa
              </button>
            </div>
          )}

          <form onSubmit={handleSalvar}>
            {erroModal && <div className="alert alert-error">{erroModal}</div>}

            {/* Campo Monetário com Prefixo R$ e Steppers de R$ 1,00 */}
            <div className="form-group">
              <label className="form-label" htmlFor="rec-valor">
                Valor Previsto (R$)
              </label>
              <div className="input-moeda-wrapper">
                <span className="input-moeda-prefixo">R$</span>
                <input
                  id="rec-valor"
                  type="text"
                  required
                  inputMode="numeric"
                  className="form-input input-moeda-field"
                  placeholder="0,00"
                  value={formValor}
                  onChange={handleValorChange}
                  disabled={salvando}
                  autoFocus
                />
                <div className="input-moeda-steppers">
                  <button
                    type="button"
                    className="input-moeda-stepper-btn"
                    onClick={() => ajustarValorStepper(1)}
                    disabled={salvando}
                    title="Aumentar R$ 1,00"
                  >
                    ▲
                  </button>
                  <button
                    type="button"
                    className="input-moeda-stepper-btn"
                    onClick={() => ajustarValorStepper(-1)}
                    disabled={salvando}
                    title="Diminuir R$ 1,00"
                  >
                    ▼
                  </button>
                </div>
              </div>
            </div>

            {/* Descrição */}
            <div className="form-group">
              <label className="form-label" htmlFor="rec-descricao">
                Descrição
              </label>
              <input
                id="rec-descricao"
                type="text"
                required
                maxLength={150}
                className="form-input"
                placeholder={
                  abaModal === 'despesa'
                    ? 'Ex: Aluguel, Internet fibra, Academia...'
                    : 'Ex: Salário mensal, Rendimento fixo...'
                }
                value={formDescricao}
                onChange={(e) => setFormDescricao(e.target.value)}
                disabled={salvando}
              />
            </div>

            {/* Dia de Vencimento com Steppers */}
            <div className="form-group">
              <label className="form-label" htmlFor="rec-dia">
                Dia de vencimento
              </label>
              <div className="dia-stepper-container">
                <input
                  id="rec-dia"
                  type="number"
                  min="1"
                  max="31"
                  required
                  className="form-input dia-input"
                  value={formDiaVencimento}
                  onChange={(e) => {
                    const v = parseInt(e.target.value, 10);
                    if (!isNaN(v)) {
                      setFormDiaVencimento(Math.min(31, Math.max(1, v)));
                    } else {
                      setFormDiaVencimento('');
                    }
                  }}
                  disabled={salvando}
                />
                <div style={{ display: 'flex', gap: '0.25rem' }}>
                  <button
                    type="button"
                    className="btn btn-secondary btn-sm dia-stepper-btn"
                    onClick={() => ajustarDiaStepper(1)}
                    disabled={salvando || formDiaVencimento >= 31}
                    title="Aumentar dia"
                  >
                    +
                  </button>
                  <button
                    type="button"
                    className="btn btn-secondary btn-sm dia-stepper-btn"
                    onClick={() => ajustarDiaStepper(-1)}
                    disabled={salvando || formDiaVencimento <= 1}
                    title="Diminuir dia"
                  >
                    −
                  </button>
                </div>
              </div>
              <span className="form-helper">
                Em meses com menos dias (como fevereiro ou meses de 30 dias), o vencimento é ajustado automaticamente para o último dia válido.
              </span>
            </div>

            {/* Categoria e Conta */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
              <div className="form-group">
                <label className="form-label" htmlFor="rec-categoria">
                  Categoria
                </label>
                <select
                  id="rec-categoria"
                  className="form-select"
                  value={formCategoriaId}
                  onChange={(e) => setFormCategoriaId(e.target.value)}
                  disabled={salvando}
                  required
                >
                  <option value="">Selecione...</option>
                  {categoriasDoTipo.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.nome}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="rec-conta">
                  Conta / Carteira
                </label>
                <select
                  id="rec-conta"
                  className="form-select"
                  value={formContaId}
                  onChange={(e) => setFormContaId(e.target.value)}
                  disabled={salvando}
                  required
                >
                  <option value="">Selecione...</option>
                  {contasAtivas.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.nome}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Forma de Pagamento */}
            <div className="form-group">
              <label className="form-label" htmlFor="rec-pagamento">
                Forma de Pagamento Padrão
              </label>
              <select
                id="rec-pagamento"
                className="form-select"
                value={formFormaPagamento}
                onChange={(e) => setFormFormaPagamento(e.target.value)}
                disabled={salvando}
              >
                <option value="PIX">PIX</option>
                <option value="Boleto">Boleto</option>
                <option value="Cartão de Crédito">Cartão de Crédito</option>
                <option value="Cartão de Débito">Cartão de Débito</option>
                <option value="Dinheiro">Dinheiro</option>
                <option value="Transferência">Transferência</option>
              </select>
            </div>

            {/* Ativo Checkbox */}
            <div className="form-group" style={{ flexDirection: 'row', alignItems: 'center', gap: '0.5rem', margin: '0.75rem 0 1.25rem 0' }}>
              <input
                id="rec-ativo"
                type="checkbox"
                checked={formAtivo}
                onChange={(e) => setFormAtivo(e.target.checked)}
                disabled={salvando}
                style={{ width: '18px', height: '18px', cursor: 'pointer' }}
              />
              <label htmlFor="rec-ativo" style={{ fontSize: '0.875rem', fontWeight: 600, cursor: 'pointer' }}>
                Modelo ativo para geração automática de lançamentos mensais
              </label>
            </div>

            <div className="modal-footer">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={fecharModal}
                disabled={salvando}
              >
                Cancelar
              </button>
              <button type="submit" className="btn btn-primary" disabled={salvando}>
                {salvando
                  ? 'Salvando...'
                  : recorrenteEmEdicao
                  ? 'Salvar Alterações'
                  : 'Criar Lançamento Fixo'}
              </button>
            </div>
          </form>
        </Modal>
      )}

      {/* Modal de Confirmação de Exclusão */}
      {modalExcluirAberto && recorrenteParaExcluir && (
        <Modal
          titulo="Excluir Lançamento Fixo"
          onFechar={() => {
            if (!excluindo) {
              setModalExcluirAberto(false);
              setRecorrenteParaExcluir(null);
            }
          }}
        >
          <div className="modal-warning-box">
            <div className="modal-warning-title">⚠️ Atenção: Exclusão do Modelo</div>
            <p style={{ margin: '0 0 0.5rem 0' }}>
              Tem certeza de que deseja excluir o modelo de fixo{' '}
              <strong>"{recorrenteParaExcluir.descricao}"</strong> (
              {formatarMoeda(recorrenteParaExcluir.valor)})?
            </p>
            <p style={{ margin: 0 }}>
              Os lançamentos já gerados a partir dele em meses anteriores permanecerão intactos no seu histórico contábil. Apenas a geração automática para os próximos ciclos será interrompida.
            </p>
          </div>

          <div className="modal-footer" style={{ marginTop: '1.25rem' }}>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => {
                setModalExcluirAberto(false);
                setRecorrenteParaExcluir(null);
              }}
              disabled={excluindo}
            >
              Cancelar
            </button>
            <button
              type="button"
              className="btn btn-primary"
              onClick={handleExcluir}
              disabled={excluindo}
            >
              {excluindo ? 'Excluindo...' : '⚠️ Confirmar Exclusão'}
            </button>
          </div>
        </Modal>
      )}
    </div>
  );
}

function TelaConfiguracoes() {
  return (
    <div className="module-container">
      <div className="module-header">
        <div><h2 className="module-title">Configurações</h2></div>
      </div>
      <div className="empty-state">
        <div className="empty-icon">⚙️</div>
        <p className="empty-title">Módulo em construção</p>
        <p className="empty-subtitle">Será implementado na Fase 11.</p>
      </div>
    </div>
  );
}

// ==============================================================================
// Shell Autenticado (Base para Fases 6 a 11)
// ==============================================================================
function ShellAutenticado() {
  const { usuario, logoSrc, logout, rotaAtual, navegar, tema, alternarTema } = useApp();

  // Título e subtítulo da página conforme rota ativa
  const obterTituloPagina = () => {
    if (rotaAtual === '/contas') return { titulo: 'Contas & Carteiras', sub: 'Gerencie seus saldos e carteiras' };
    if (rotaAtual === '/lancamentos') return { titulo: 'Lançamentos', sub: 'Registre e controle suas movimentações' };
    if (rotaAtual === '/categorias') return { titulo: 'Categorias & Tetos', sub: 'Organize e controle seus gastos' };
    if (rotaAtual === '/recorrentes') return { titulo: 'Fixos Recorrentes', sub: 'Automatize suas despesas e receitas fixas' };
    if (rotaAtual === '/configuracoes') return { titulo: 'Configurações', sub: 'Preferências e dados do perfil' };
    return { titulo: 'Painel Principal', sub: `Bem-vindo, ${(usuario.nome || '').split(' ')[0]}!` };
  };

  const { titulo, sub } = obterTituloPagina();

  // Renderiza o módulo correspondente à rota
  const renderizarModulo = () => {
    if (rotaAtual === '/contas') return <TelaContas />;
    if (rotaAtual === '/lancamentos') return <TelaLancamentos />;
    if (rotaAtual === '/categorias') return <TelaCategorias />;
    if (rotaAtual === '/recorrentes') return <TelaRecorrentes />;
    if (rotaAtual === '/configuracoes') return <TelaConfiguracoes />;
    return <TelaDashboard />;
  };

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
            className={`nav-link ${(rotaAtual === '/dashboard' || rotaAtual === '/') ? 'active' : ''}`}
            onClick={(e) => { e.preventDefault(); navegar('/dashboard'); }}
          >
            <span>📊</span> Painel Principal
          </a>
          <a
            href="/lancamentos"
            className={`nav-link ${rotaAtual === '/lancamentos' ? 'active' : ''}`}
            onClick={(e) => { e.preventDefault(); navegar('/lancamentos'); }}
          >
            <span>💳</span> Lançamentos
          </a>
          <a
            href="/contas"
            className={`nav-link ${rotaAtual === '/contas' ? 'active' : ''}`}
            onClick={(e) => { e.preventDefault(); navegar('/contas'); }}
          >
            <span>🏦</span> Contas &amp; Carteiras
          </a>
          <a
            href="/categorias"
            className={`nav-link ${rotaAtual === '/categorias' ? 'active' : ''}`}
            onClick={(e) => { e.preventDefault(); navegar('/categorias'); }}
          >
            <span>🏷️</span> Categorias &amp; Tetos
          </a>
          <a
            href="/recorrentes"
            className={`nav-link ${rotaAtual === '/recorrentes' ? 'active' : ''}`}
            onClick={(e) => { e.preventDefault(); navegar('/recorrentes'); }}
          >
            <span>🔁</span> Fixos Recorrentes
          </a>
          <a
            href="/configuracoes"
            className={`nav-link ${rotaAtual === '/configuracoes' ? 'active' : ''}`}
            onClick={(e) => { e.preventDefault(); navegar('/configuracoes'); }}
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
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.125rem', letterSpacing: '-0.02em' }}>
              {titulo}
            </h2>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>{sub}</p>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <BotaoAlternarTema />
          </div>
        </header>

        {/* Módulo ativo */}
        {renderizarModulo()}
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
